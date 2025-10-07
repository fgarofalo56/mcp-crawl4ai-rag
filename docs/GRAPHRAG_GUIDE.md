# GraphRAG Implementation Guide

## Table of Contents

1. [Overview](#overview)
2. [What is GraphRAG?](#what-is-graphrag)
3. [Architecture](#architecture)
4. [Setup and Configuration](#setup-and-configuration)
5. [Tools Reference](#tools-reference)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Performance Considerations](#performance-considerations)

## Overview

GraphRAG (Graph-Augmented Retrieval-Augmented Generation) extends traditional vector-based RAG with knowledge graph capabilities. This implementation combines:

- **Vector embeddings** in Supabase for semantic similarity search
- **Knowledge graph** in Neo4j for entity relationships and structured knowledge
- **LLM-based entity extraction** for automatic graph construction

**Result:** Richer context, better reasoning, and reduced hallucinations in RAG responses.

## What is GraphRAG?

### Traditional Vector RAG

```
User Query → Embedding → Vector Search → Top K Documents → LLM → Answer
```

**Strengths:**
- Fast similarity search
- Works well for factual questions
- Simple architecture

**Weaknesses:**
- No understanding of relationships
- Limited multi-hop reasoning
- Can't explain dependencies or connections

### GraphRAG (This Implementation)

```
User Query → [Vector Search + Graph Traversal] → Enriched Context → LLM → Answer
```

**How it works:**

1. **Ingestion Phase:**
   - Crawl web content → Store in Supabase with embeddings
   - Extract entities (FastAPI, OAuth2, Docker, etc.) → Store in Neo4j
   - Extract relationships (FastAPI USES Python, OAuth2 REQUIRES JWT) → Store in Neo4j
   - Link documents to entities

2. **Query Phase:**
   - User asks: "How do I configure OAuth2 in FastAPI?"
   - Vector search finds relevant documents
   - Graph traversal discovers:
     - OAuth2 requires python-jose library
     - OAuth2 uses JWT tokens
     - JWT needs SECRET_KEY configuration
     - FastAPI has SecurityHTTPBearer for OAuth2
   - Combine document chunks + graph relationships → LLM
   - Answer includes complete dependency chain

**Strengths:**
- Understands entity relationships
- Multi-hop reasoning (A requires B, B requires C)
- Explicit dependencies reduce hallucinations
- Better answers for "how do X and Y relate?" questions

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│  MCP Crawl4AI RAG Server (v1.2.0+)                      │
└─────────────────────────────────────────────────────────┘
           │                          │
           │                          │
    ┌──────▼────────┐        ┌───────▼────────┐
    │   Supabase    │        │     Neo4j      │
    │  (pgvector)   │        │  (Graph DB)    │
    │               │        │                │
    │ • Documents   │        │ • Entities     │
    │ • Embeddings  │        │ • Relationships│
    │ • Chunks      │        │ • Documents    │
    └───────────────┘        └────────────────┘
           │                          │
           │                          │
    Vector Search              Graph Traversal
           │                          │
           └──────────┬───────────────┘
                      │
              ┌───────▼────────┐
              │  Enriched      │
              │  Context       │
              └────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  OpenAI LLM   │
              └───────────────┘
```

### Database Schemas

#### Supabase (Vector Store)
```sql
-- Existing schema (unchanged)
crawled_pages (
  id,
  url,
  content,
  embedding vector(1536),
  source_id
)
```

#### Neo4j (Knowledge Graph)
```cypher
// New schema for GraphRAG

// Document nodes (linked to Supabase)
(:Document {
  id: string,           // MD5 hash of URL
  source_id: string,    // Domain
  url: string,
  title: string,
  updated_at: datetime
})

// Entity nodes
(:Concept {name: string, description: string, type: string})
(:Technology {name: string, description: string, category: string})
(:Configuration {name: string, description: string})
(:Person {name: string})
(:Organization {name: string})
(:Product {name: string, description: string})

// Relationships
(Document)-[:MENTIONS {count: int}]->(Entity)
(Document)-[:FROM_SOURCE]->(Source)
(Entity)-[:REQUIRES]->(Entity)
(Entity)-[:USES]->(Entity)
(Entity)-[:PART_OF]->(Entity)
(Entity)-[:ALTERNATIVE_TO]->(Entity)
// ... and more
```

## Setup and Configuration

### Prerequisites

1. **Neo4j Database** (same as code knowledge graph)
   - Neo4j 5.15+ for optimal performance
   - Can use Docker Compose (recommended) or cloud (AuraDB)

2. **OpenAI API** (for entity extraction)
   - Standard OpenAI or Azure OpenAI
   - Model: `gpt-4o-mini` recommended for cost efficiency

3. **Supabase** (existing requirement)
   - No changes needed

### Environment Variables

Add to your `.env` file:

```bash
# Enable GraphRAG
USE_GRAPHRAG=true

# Neo4j Configuration (same as knowledge graph)
NEO4J_URI=bolt://localhost:7687     # or bolt://neo4j:7687 in Docker
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# OpenAI for entity extraction
OPENAI_API_KEY=sk-your-key-here

# OR Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Docker Compose Setup

GraphRAG uses the same Neo4j instance as the code knowledge graph:

```bash
# Start services (Neo4j + MCP server)
docker-compose up -d

# Verify GraphRAG is initialized
docker-compose logs mcp-server | grep -i "graphrag"

# Expected output:
# Initializing GraphRAG components...
# ✓ Document graph validator initialized
# ✓ Document graph queries initialized
# ✓ Document entity extractor initialized (OpenAI)
```

### Standalone Setup

```bash
# 1. Install dependencies (if not already)
uv sync

# 2. Set environment variables in .env
USE_GRAPHRAG=true
# ... other vars

# 3. Start Neo4j (if not running)
# See DOCKER_SETUP.md for Neo4j setup

# 4. Run MCP server
uv run src/crawl4ai_mcp.py
```

## Tools Reference

GraphRAG adds 4 new MCP tools:

### 1. `crawl_with_graph_extraction`

**Purpose:** Crawl a URL and build both vector embeddings AND knowledge graph.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to crawl |
| `extract_entities` | boolean | true | Extract entities from content |
| `extract_relationships` | boolean | true | Extract relationships between entities |
| `chunk_size` | integer | 5000 | Text chunk size for processing |

**Returns:**
```json
{
  "success": true,
  "url": "https://fastapi.tiangolo.com/",
  "source_id": "fastapi.tiangolo.com",
  "crawl_results": {
    "documents_stored": 15,
    "total_words": 5432
  },
  "graph_extraction": {
    "entities_found": 23,
    "entities_stored": 23,
    "relationships_found": 18,
    "relationships_stored": 18,
    "extraction_time": "4.32s"
  },
  "document_id": "a3b2c1d4e5f6..."
}
```

**Example:**
```python
crawl_with_graph_extraction("https://fastapi.tiangolo.com/tutorial/")
```

---

### 2. `graphrag_query`

**Purpose:** Perform RAG query with optional graph enrichment.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `use_graph_enrichment` | boolean | true | Enable graph context |
| `max_entities` | integer | 15 | Max entities in enrichment |
| `source_filter` | string | null | Filter by source domain |

**When to use graph enrichment:**
- ✅ Complex "how do X and Y relate?" questions
- ✅ Dependency and prerequisite questions
- ✅ Multi-step procedures
- ❌ Simple factual lookups (disable for speed)

**Returns:**
```json
{
  "success": true,
  "query": "How do I configure OAuth2 in FastAPI?",
  "answer": "[Detailed answer with relationships and dependencies]",
  "graph_enrichment_used": true,
  "documents_found": 5,
  "sources": [
    {"url": "...", "relevance": 0.87}
  ]
}
```

**Example:**
```python
graphrag_query(
    "What are the dependencies for deploying FastAPI with Docker?",
    use_graph_enrichment=True
)
```

---

### 3. `query_document_graph`

**Purpose:** Execute custom Cypher queries on document graph (advanced).

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cypher_query` | string | required | Cypher query |

**Common Query Patterns:**

Find all technologies:
```cypher
MATCH (t:Technology)
RETURN t.name, t.description
LIMIT 20
```

Find dependencies:
```cypher
MATCH (a)-[r:REQUIRES]->(b)
RETURN a.name, b.name, r.description
```

Find most-mentioned entities:
```cypher
MATCH (d:Document)-[m:MENTIONS]->(e)
RETURN e.name, labels(e)[0] as type, sum(m.count) as total_mentions
ORDER BY total_mentions DESC
LIMIT 10
```

Find entities in specific source:
```cypher
MATCH (d:Document {source_id: 'fastapi.tiangolo.com'})-[:MENTIONS]->(e:Technology)
RETURN DISTINCT e.name, e.description
```

**Returns:**
```json
{
  "success": true,
  "record_count": 10,
  "records": [
    {"t.name": "FastAPI", "t.description": "Modern Python web framework"},
    ...
  ]
}
```

---

### 4. `get_entity_context`

**Purpose:** Get comprehensive context for a specific entity.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entity_name` | string | required | Entity to look up |
| `max_hops` | integer | 2 | Relationship hops |

**Returns:**
```json
{
  "success": true,
  "entity": {
    "name": "FastAPI",
    "type": "Technology",
    "description": "Modern Python web framework"
  },
  "related_entities": [
    {"name": "Python", "type": "Technology", "relationship": "USES"},
    {"name": "Pydantic", "type": "Technology", "relationship": "REQUIRES"},
    ...
  ],
  "relationships": [
    {"from": "FastAPI", "to": "Python", "type": "USES"},
    ...
  ],
  "documents": [
    {"id": "...", "url": "...", "title": "..."},
    ...
  ],
  "stats": {
    "related_entities_count": 8,
    "relationships_count": 12,
    "documents_count": 3
  }
}
```

**Example:**
```python
get_entity_context("FastAPI", max_hops=2)
```

## Usage Examples

### Example 1: Build Knowledge Graph from Documentation

```python
# Crawl FastAPI documentation with graph extraction
result = crawl_with_graph_extraction(
    url="https://fastapi.tiangolo.com/tutorial/",
    extract_entities=True,
    extract_relationships=True
)

# Result: Vector embeddings in Supabase + Entity graph in Neo4j
# Entities extracted: FastAPI, Pydantic, OAuth2, JWT, Python, etc.
# Relationships: FastAPI USES Python, OAuth2 REQUIRES python-jose, etc.
```

### Example 2: Graph-Enriched Question Answering

```python
# Traditional RAG (fast, simple)
answer = graphrag_query(
    "What is FastAPI?",
    use_graph_enrichment=False  # Disable graph for simple questions
)

# GraphRAG (slower, richer context)
answer = graphrag_query(
    "How do I implement OAuth2 authentication in FastAPI with all dependencies?",
    use_graph_enrichment=True  # Enable graph for complex questions
)

# GraphRAG answer will include:
# - OAuth2 concepts
# - Required libraries (python-jose, passlib)
# - Configuration requirements (SECRET_KEY)
# - Related concepts (JWT, hashing)
# - Complete dependency chain
```

### Example 3: Explore Entity Relationships

```python
# Find all related technologies
context = get_entity_context("FastAPI", max_hops=2)

# Returns:
# - Direct dependencies: Python, Pydantic, Starlette
# - Indirect dependencies: asyncio, typing
# - Alternative frameworks: Flask, Django
# - Documents mentioning FastAPI
```

### Example 4: Advanced Graph Queries

```python
# Find all configuration requirements
query = """
MATCH (c:Configuration)<-[:REQUIRES]-(t:Technology)
RETURN t.name as technology, c.name as config, c.description
ORDER BY technology
"""

result = query_document_graph(query)

# Returns all config requirements discovered in docs
# e.g., FastAPI needs SECRET_KEY, Database needs connection string, etc.
```

### Example 5: Build Cross-Document Knowledge

```python
# Crawl multiple related sources
urls = [
    "https://fastapi.tiangolo.com/tutorial/security/",
    "https://docs.python-jose.readthedocs.io/",
    "https://passlib.readthedocs.io/"
]

for url in urls:
    crawl_with_graph_extraction(url)

# Query with graph enrichment
answer = graphrag_query(
    "What's the complete setup for JWT authentication?",
    use_graph_enrichment=True
)

# GraphRAG will traverse across all crawled documents,
# finding connections between FastAPI, python-jose, and passlib
```

## Best Practices

### When to Use GraphRAG

✅ **Use GraphRAG for:**
- Technical documentation with many interconnected concepts
- Questions about dependencies, prerequisites, or relationships
- Multi-step procedures that require understanding connections
- "How do X and Y work together?" type questions
- Domain-specific knowledge bases

❌ **Don't use GraphRAG for:**
- Simple factual lookups ("What is X?")
- Time-sensitive queries (graph traversal adds latency)
- Very broad, general questions
- Small document sets (graph won't provide value)

### Entity Extraction Tips

1. **Chunk Size:** Default 5000 is optimal
   - Smaller chunks: More granular but higher API costs
   - Larger chunks: Better context but may miss entities

2. **Limit Chunks:** Only first 10 chunks are processed by default
   - Reduces API costs
   - Most important content is usually at the top
   - Adjust in code if needed: `chunks[:10]` → `chunks[:20]`

3. **Entity Types:** Focus on:
   - Technologies (FastAPI, Docker, PostgreSQL)
   - Concepts (OAuth2, JWT, Microservices)
   - Configurations (PORT, API_KEY, SECRET)
   - Products/Tools (GitHub, VS Code)

4. **Relationship Types:** Common patterns:
   - REQUIRES (A needs B to function)
   - USES (A uses B)
   - PART_OF (A is part of B)
   - ALTERNATIVE_TO (A can replace B)

### Performance Optimization

#### Crawling Phase
- **Batch Processing:** Crawl multiple URLs in sequence
- **Entity Extraction:** Limit to 10 chunks per document (default)
- **Concurrent Extraction:** Max 3 concurrent LLM calls (default)

#### Query Phase
- **Toggle Graph Enrichment:** Disable for simple questions
- **Cache Results:** Vector search results can be cached
- **Limit Entities:** Default max_entities=15 is good balance

### Cost Management

GraphRAG adds LLM costs for entity extraction:

| Component | Cost Driver | Optimization |
|-----------|-------------|--------------|
| Entity Extraction | LLM API calls | Limit chunks processed |
| Graph Storage | Neo4j (minimal) | Use Docker (free) |
| Vector Storage | Supabase (existing) | No change |
| Query Enrichment | Graph queries (free) | No additional cost |

**Example costs:**
- Crawl 1 page (5000 tokens): ~$0.001 with gpt-4o-mini
- Crawl 100 pages: ~$0.10
- Query with graph enrichment: No additional LLM cost (uses existing data)

## Troubleshooting

### GraphRAG Not Enabled

**Symptom:**
```json
{"error": "GraphRAG functionality is disabled"}
```

**Solution:**
```bash
# Check .env file
USE_GRAPHRAG=true  # Must be exactly 'true'

# Restart server
docker-compose restart mcp-server
# OR
uv run src/crawl4ai_mcp.py
```

### Entity Extraction Failing

**Symptom:**
```json
{"error": "Entity extraction failed: ..."}
```

**Common causes:**
1. **Missing OpenAI API key**
   ```bash
   # Check .env
   OPENAI_API_KEY=sk-...
   # OR for Azure
   AZURE_OPENAI_ENDPOINT=https://...
   AZURE_OPENAI_API_KEY=...
   ```

2. **Rate limiting**
   - Reduce concurrent extraction: Edit `max_concurrent=3` → `max_concurrent=1`

3. **Invalid JSON response from LLM**
   - Rare but possible with very short text
   - Try increasing chunk_size

### Neo4j Connection Issues

**Symptom:**
```json
{"error": "Document graph queries not available"}
```

**Solution:**
See [DOCKER_SETUP.md](DOCKER_SETUP.md#neo4j-connection-troubleshooting) for Neo4j troubleshooting.

Quick checks:
```bash
# Verify Neo4j is running
docker ps | grep neo4j

# Check Neo4j browser
curl http://localhost:7474

# Verify credentials
docker exec -it mcp-crawl4ai-server env | grep NEO4J
```

### Graph Query Syntax Errors

**Symptom:**
```json
{"error": "Query execution failed: Invalid Cypher syntax"}
```

**Solution:**
- Use Neo4j Browser (http://localhost:7474) to test queries
- Check Cypher syntax documentation
- Common mistakes:
  - Missing quotes: `name = FastAPI` → `name = "FastAPI"`
  - Wrong label: `(c:Configuration)` not `(c:Config)`
  - Invalid relationship direction

### No Entities Found

**Symptom:**
```json
{"entities_found": 0, "relationships_found": 0}
```

**Possible causes:**
1. **Content too short** - LLM needs substantial text
2. **Generic content** - No clear entities to extract
3. **API error** - Check logs for LLM errors

**Solution:**
```bash
# Check MCP server logs for LLM errors
docker-compose logs mcp-server | grep -i "entity\|error"

# Try with a technical documentation page
crawl_with_graph_extraction("https://fastapi.tiangolo.com/tutorial/")
```

## Performance Considerations

### Latency Comparison

| Operation | Vector RAG | GraphRAG | Difference |
|-----------|-----------|----------|------------|
| Simple query | 200ms | 350ms | +75% |
| Complex query | 200ms | 500ms | +150% |
| Crawl (new page) | 2s | 6s | +200% |

**GraphRAG is slower** but provides significantly better answers for complex questions.

### Scalability

#### Small Scale (< 100 pages)
- ✅ Graph provides value
- ✅ Entity extraction is affordable
- ✅ Query performance is fast

#### Medium Scale (100-1000 pages)
- ✅ Graph provides significant value
- ⚠️ Watch API costs for entity extraction
- ✅ Query performance still good

#### Large Scale (1000+ pages)
- ✅ Graph provides excellent value
- ⚠️ Consider batch extraction with caching
- ⚠️ May need Neo4j performance tuning

### Neo4j Performance Tuning

For large graphs (10,000+ entities):

```bash
# Increase heap size
NEO4J_server_memory_heap_max__size=4G

# Increase page cache
NEO4J_server_memory_pagecache_size=2G

# Monitor query performance
docker exec -it mcp-crawl4ai-neo4j cypher-shell
```

See [Neo4j Performance Tuning Documentation](https://neo4j.com/docs/operations-manual/current/performance/).

## Next Steps

1. **Try It Out:**
   ```bash
   # Enable GraphRAG
   echo "USE_GRAPHRAG=true" >> .env

   # Restart server
   docker-compose restart mcp-server

   # Crawl with graph extraction
   crawl_with_graph_extraction("https://fastapi.tiangolo.com/")

   # Query with graph enrichment
   graphrag_query("How does FastAPI handle authentication?", use_graph_enrichment=True)
   ```

2. **Explore the Graph:**
   ```bash
   # Open Neo4j Browser
   open http://localhost:7474

   # Run queries
   MATCH (t:Technology) RETURN t LIMIT 25
   ```

3. **Read More:**
   - [API Reference](../API_REFERENCE.md) - Full tool documentation
   - [Docker Setup](DOCKER_SETUP.md) - Neo4j configuration
   - [Architecture](ARCHITECTURE.md) - System design details

4. **Get Help:**
   - GitHub Issues: https://github.com/coleam00/mcp-crawl4ai-rag/issues
   - Include: Logs, .env configuration (without secrets), error messages

---

**Version:** 1.2.0
**Last Updated:** 2025-10-07
