# 🕸️ GraphRAG implementation guide

> **🏠 [Home](../README.md)** | **📖 [Documentation](README.md)** | **👤 GraphRAG guide**

---

## Table of contents

1. [What's new](#whats-new)
2. [Overview](#overview)
3. [What is GraphRAG?](#what-is-graphrag)
4. [Architecture](#architecture)
5. [Setup and configuration](#setup-and-configuration)
6. [Tools reference](#tools-reference)
7. [Usage examples](#usage-examples)
8. [Best practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Performance considerations](#performance-considerations)

## What's new

**GraphRAG is now PRODUCTION-READY with full graph enrichment!**

As of version 1.2.0 (October 2025), GraphRAG provides TRUE graph-enriched queries:

**Key improvements:**
- **Automatic document linking**: `crawl_with_graph_extraction` now stores `document_id` in Supabase metadata, creating a direct link between vector search results and Neo4j graph nodes
- **Real graph enrichment**: `graphrag_query` now extracts document IDs from search results and enriches them with entity contexts, relationships, and dependency chains from the knowledge graph
- **Comprehensive context**: Answers now include explicit entity relationships, related concepts, and dependency information
- **Full integration testing**: New test suite validates the complete GraphRAG workflow

**What this means:**
- Documents crawled with `crawl_with_graph_extraction` are automatically linked to the knowledge graph
- Queries with `use_graph_enrichment=True` now provide real entity contexts from Neo4j
- Answers explain relationships and dependencies, not just document content
- The system provides comprehensive, graph-augmented responses for complex questions

See [Usage Examples](#usage-examples) for demonstrations of the enhanced capabilities.

## Overview

GraphRAG (Graph-Augmented Retrieval-Augmented Generation) extends traditional vector-based RAG with knowledge graph capabilities. This implementation combines:

- **Vector embeddings** in Supabase for semantic similarity search
- **Knowledge graph** in Neo4j for entity relationships and structured knowledge
- **LLM-based entity extraction** for automatic graph construction
- **Document linking** to connect vector search results with graph nodes

**Result:** Richer context, better reasoning, explicit relationship explanations, and reduced hallucinations in RAG responses.

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

**Purpose:** Crawl a URL and build both vector embeddings AND knowledge graph with automatic linking.

**What it does:**
1. Crawls the URL and extracts content
2. Stores content chunks in Supabase with vector embeddings
3. **Stores `document_id` in Supabase metadata for GraphRAG linking**
4. Extracts entities and relationships using LLM
5. Stores entities and relationships in Neo4j knowledge graph
6. Creates document node in Neo4j linked to entities

**Key Feature:** The returned `document_id` is automatically stored in Supabase metadata, enabling `graphrag_query` to enrich results with knowledge graph data.

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

**Important:** The `document_id` is the key that links Supabase vector search results to Neo4j graph nodes. Documents crawled with this tool are fully GraphRAG-enabled.

**Example:**
```python
# Crawl with full GraphRAG capabilities
result = crawl_with_graph_extraction("https://fastapi.tiangolo.com/tutorial/")

# The returned document_id is now linked in both Supabase and Neo4j
# Future queries will automatically enrich results with graph data
```

---

### 2. `graphrag_query`

**Purpose:** Perform RAG query with optional graph enrichment for comprehensive, relationship-aware answers.

**How it works:**
1. Performs vector similarity search in Supabase (traditional RAG)
2. **Extracts `document_id` values from search result metadata**
3. **Queries Neo4j to get entity contexts, relationships, and dependencies for those documents**
4. Combines document content + graph enrichment into LLM context
5. Generates answer that explains relationships and dependencies

**Key Feature:** When `use_graph_enrichment=True`, the tool automatically retrieves and includes:
- Entity contexts (what entities are mentioned and their descriptions)
- Related concepts (other entities connected to the found entities)
- Dependency chains (A requires B, B requires C relationships)
- Relationship explanations (how entities connect to each other)

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
- ✅ Understanding technology stacks and architectures
- ❌ Simple factual lookups (disable for speed)

**Returns:**
```json
{
  "success": true,
  "query": "How do I configure OAuth2 in FastAPI?",
  "answer": "[Detailed answer with relationships and dependencies explained]",
  "graph_enrichment_used": true,
  "graph_enrichment": {
    "entities_found": 5,
    "concepts": ["FastAPI", "OAuth2", "JWT", "python-jose"],
    "dependencies": [
      {"from": "OAuth2", "to": "JWT"},
      {"from": "FastAPI", "to": "python-jose"}
    ]
  },
  "documents_found": 5,
  "sources": [
    {"url": "...", "relevance": 0.87}
  ]
}
```

**Example:**
```python
# Query with full graph enrichment
result = graphrag_query(
    "What are the dependencies for deploying FastAPI with Docker?",
    use_graph_enrichment=True
)

# Answer will include:
# - FastAPI requires Python
# - Docker configuration needs specific environment variables
# - Relationships between FastAPI, Docker, and dependencies
# - Explicit dependency chains
```

**Important:** Graph enrichment only works for documents crawled with `crawl_with_graph_extraction`. Documents crawled with standard tools will fall back to traditional RAG.

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

## Usage examples

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
# Returns: Simple factual answer from document content

# GraphRAG (comprehensive, relationship-aware)
answer = graphrag_query(
    "How do I implement OAuth2 authentication in FastAPI with all dependencies?",
    use_graph_enrichment=True  # Enable graph for complex questions
)

# GraphRAG answer now includes REAL enrichment data:
# {
#   "success": true,
#   "answer": "Detailed explanation with relationships...",
#   "graph_enrichment_used": true,
#   "graph_enrichment": {
#     "entities_found": 5,
#     "concepts": ["FastAPI", "OAuth2", "JWT", "python-jose", "passlib"],
#     "dependencies": [
#       {"from": "OAuth2", "to": "JWT"},
#       {"from": "FastAPI", "to": "python-jose"},
#       {"from": "Authentication", "to": "passlib"}
#     ]
#   }
# }
#
# The answer will explain:
# - OAuth2 concepts and their relationships
# - Required libraries (python-jose for JWT, passlib for hashing)
# - Configuration requirements (SECRET_KEY, ALGORITHM)
# - How FastAPI integrates with OAuth2 (SecurityHTTPBearer)
# - Complete dependency chain from FastAPI → OAuth2 → JWT → libraries
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
    result = crawl_with_graph_extraction(url)
    # Each crawl stores document_id in Supabase metadata
    # and creates linked nodes in Neo4j

# Query with graph enrichment
answer = graphrag_query(
    "What's the complete setup for JWT authentication?",
    use_graph_enrichment=True
)

# GraphRAG now:
# 1. Finds relevant documents via vector search
# 2. Extracts document_ids from search results
# 3. Queries Neo4j for entity contexts from those documents
# 4. Combines document content + graph relationships
# 5. Generates answer explaining the complete authentication stack
#
# Result includes:
# - FastAPI security features
# - python-jose JWT encoding/decoding
# - passlib password hashing
# - Relationships: FastAPI → OAuth2 → JWT → python-jose
# - Configuration requirements across all libraries
```

### Example 6: Production GraphRAG Workflow

```python
# Step 1: Crawl documentation with graph extraction
crawl_result = crawl_with_graph_extraction(
    "https://fastapi.tiangolo.com/tutorial/",
    extract_entities=True,
    extract_relationships=True
)

# Verify GraphRAG linking
print(f"Document ID: {crawl_result['document_id']}")
print(f"Entities extracted: {crawl_result['graph_extraction']['entities_found']}")
print(f"Relationships mapped: {crawl_result['graph_extraction']['relationships_found']}")

# Step 2: Query with graph enrichment
query_result = graphrag_query(
    "How do I deploy a FastAPI application with Docker?",
    use_graph_enrichment=True,
    max_entities=15
)

# Step 3: Verify graph enrichment was used
if query_result['graph_enrichment_used']:
    enrichment = query_result['graph_enrichment']
    print(f"✓ Graph enrichment active")
    print(f"  Entities found: {enrichment['entities_found']}")
    print(f"  Related concepts: {enrichment['concepts']}")
    print(f"  Dependencies: {len(enrichment['dependencies'])}")

    # Answer now includes:
    # - FastAPI deployment requirements
    # - Docker configuration needs
    # - Dependency relationships (FastAPI → Python → Docker image)
    # - Environment variables and configuration
    print(f"\nAnswer with graph context:\n{query_result['answer']}")
else:
    print("⚠ Graph enrichment not available - document may not be linked")
    print("  Re-crawl with crawl_with_graph_extraction to enable GraphRAG")
```

## Best practices

### When to Use GraphRAG

✅ **Use GraphRAG for:**
- Technical documentation with many interconnected concepts
- Questions about dependencies, prerequisites, or relationships
- Multi-step procedures that require understanding connections
- "How do X and Y work together?" type questions
- Technology stack questions (e.g., "What do I need to deploy X?")
- Configuration and setup questions with multiple dependencies
- Domain-specific knowledge bases with entity relationships

❌ **Don't use GraphRAG for:**
- Simple factual lookups ("What is X?") - traditional RAG is faster
- Time-sensitive queries (graph enrichment adds 150-300ms latency)
- Very broad, general questions without specific entities
- Small document sets (< 10 pages) where graph won't provide value

### Ensuring GraphRAG Compatibility

**For full GraphRAG capabilities, ALWAYS use `crawl_with_graph_extraction`:**

```python
# ✓ Correct - full GraphRAG support
crawl_with_graph_extraction("https://example.com/docs")

# ✗ Incorrect - no graph linking
smart_crawl_url("https://example.com/docs")  # Vector search only
```

**Documents crawled with standard tools won't have graph enrichment:**
- Missing `document_id` in Supabase metadata
- `graphrag_query` will fall back to traditional RAG
- No entity contexts or relationship data available

**To verify GraphRAG is active:**
```python
result = graphrag_query("your question", use_graph_enrichment=True)

if result['graph_enrichment_used']:
    print("✓ GraphRAG active with entity contexts")
else:
    print("⚠ Fallback to traditional RAG")
    print("  Re-crawl documents with crawl_with_graph_extraction")
```

### Batch Processing Best Practices

For processing multiple documents or large documentation sites:

#### 1. Optimal Batch Sizes

```python
# Small batch (2-5 pages): Fast, good for testing
for url in small_batch:
    crawl_with_graph_extraction(url)

# Medium batch (10-50 pages): Use sequential processing
urls = ["url1", "url2", ..., "url10"]
for url in urls:
    result = crawl_with_graph_extraction(url)
    # Process result before next URL

# Large batch (50+ pages): Consider breaking into smaller batches
def process_in_batches(urls, batch_size=10):
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        for url in batch:
            crawl_with_graph_extraction(url)
        # Pause between batches to avoid rate limits
        time.sleep(5)
```

#### 2. Rate Limiting Strategies

GraphRAG uses OpenAI API for entity extraction. To avoid rate limits:

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def crawl_with_retry(url):
    return crawl_with_graph_extraction(url)

# Process with delays
for url in urls:
    try:
        result = crawl_with_retry(url)
    except Exception as e:
        print(f"Failed after retries: {url}")
    time.sleep(2)  # 2 second delay between requests
```

#### 3. Progress Tracking

For long-running batch operations:

```python
from tqdm import tqdm

urls = [...]  # Your URL list
results = []

for url in tqdm(urls, desc="Crawling with GraphRAG"):
    try:
        result = crawl_with_graph_extraction(url)
        results.append({
            "url": url,
            "status": "success",
            "entities": result.get("graph_extraction", {}).get("entities_found", 0)
        })
    except Exception as e:
        results.append({
            "url": url,
            "status": "failed",
            "error": str(e)
        })

# Summary statistics
successful = sum(1 for r in results if r["status"] == "success")
total_entities = sum(r.get("entities", 0) for r in results if r["status"] == "success")
print(f"Processed: {successful}/{len(urls)} URLs")
print(f"Total entities extracted: {total_entities}")
```

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

### Graph Enrichment Not Being Used

**Symptom:**
```json
{
  "graph_enrichment_used": false,
  "graph_enrichment": null
}
```

**Possible causes:**
1. **Documents not crawled with GraphRAG** - Missing `document_id` in metadata
2. **GraphRAG disabled** - `USE_GRAPHRAG=false` in environment
3. **Neo4j not connected** - Graph queries unavailable

**Solution:**

```bash
# 1. Check if GraphRAG is enabled
echo $USE_GRAPHRAG  # Should be "true"

# 2. Verify Neo4j connection
docker exec -it mcp-crawl4ai-neo4j cypher-shell -u neo4j -p your_password
# Run: MATCH (d:Document) RETURN count(d);

# 3. Re-crawl documents with graph extraction
crawl_with_graph_extraction("https://your-url.com")

# 4. Verify document_id is stored in Supabase
# Check Supabase dashboard: crawled_pages table → metadata column
# Should contain: {"source_id": "...", "document_id": "..."}

# 5. Test with a known-good document
graphrag_query("your question", use_graph_enrichment=True)
```

**Check document compatibility:**
```python
# Query a document and inspect metadata
from src.utils import search_documents, get_supabase_client

client = get_supabase_client()
results = search_documents(client, "test query", match_count=1)

# Check if document_id exists
if results:
    metadata = results[0].get('metadata', {})
    if 'document_id' in metadata:
        print("✓ Document is GraphRAG-compatible")
    else:
        print("✗ Document missing document_id - re-crawl needed")
```

## Performance Considerations

### Latency Comparison

| Operation | Vector RAG | GraphRAG (with enrichment) | Difference |
|-----------|-----------|---------------------------|------------|
| Simple query | 200ms | 350-450ms | +75-125% |
| Complex query | 200ms | 500-700ms | +150-250% |
| Crawl (new page) | 2s | 6-8s | +200-300% |

**GraphRAG is slower** but provides significantly better answers for complex questions:

- **Graph enrichment adds:** 150-300ms for Neo4j queries per request
- **Entity extraction adds:** 3-5s per crawl (LLM API calls)
- **Trade-off:** Slower queries, but much richer context and better answers

**Performance breakdown:**
```
graphrag_query with enrichment:
├─ Vector search (Supabase): 100-150ms
├─ Extract document IDs: 1-5ms
├─ Graph enrichment (Neo4j): 150-300ms
│  ├─ Entity context queries: 50-100ms
│  ├─ Relationship queries: 50-100ms
│  └─ Dependency chain queries: 50-100ms
└─ LLM answer generation: 1-2s (OpenAI)
Total: ~1.5-2.5s for enriched query
```

### Memory Monitoring for Large-Scale GraphRAG

When crawling large documentation sites with GraphRAG:

```python
# Use memory monitoring wrapper
result = crawl_with_memory_monitoring(
    url="https://large-docs.com/sitemap.xml",
    memory_threshold_mb=400  # Adjust based on available memory
)

# Monitor memory statistics in response
print(f"Peak memory: {result['memory_stats']['peak_mb']}MB")
print(f"Memory delta: {result['memory_stats']['delta_mb']}MB")
```

### Concurrent Entity Extraction Limits

GraphRAG extracts entities using LLM calls. Control concurrency to manage:
- **API rate limits**: OpenAI tier limits (e.g., 3,500 RPM for Tier 1)
- **Memory usage**: Each concurrent extraction holds chunks in memory
- **Cost optimization**: Avoid duplicate extractions

**Default Settings** (in code):
```python
# Current default: 3 concurrent LLM calls
# This balances speed vs. rate limits
# For higher tiers, you can increase this in the code
```

**Recommendations by OpenAI Tier**:

| Tier | RPM Limit | Recommended Concurrent Extractions | Batch Size |
|------|-----------|-----------------------------------|------------|
| Free | 3 RPM | 1 | 5-10 pages |
| Tier 1 | 3,500 RPM | 3 (default) | 50 pages |
| Tier 2 | 5,000 RPM | 5 | 100 pages |
| Tier 3+ | 10,000+ RPM | 10 | 500+ pages |

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

### Quick Start: Try GraphRAG Now

1. **Enable and verify GraphRAG:**
   ```bash
   # Enable GraphRAG
   echo "USE_GRAPHRAG=true" >> .env

   # Restart server
   docker-compose restart mcp-server

   # Verify GraphRAG components initialized
   docker-compose logs mcp-server | grep -i "graphrag"
   # Expected: "✓ Document graph validator initialized"
   #           "✓ Document graph queries initialized"
   #           "✓ Document entity extractor initialized"
   ```

2. **Crawl with full GraphRAG support:**
   ```bash
   # Crawl and verify document linking
   result = crawl_with_graph_extraction("https://fastapi.tiangolo.com/tutorial/")

   # Verify document_id was created
   print(f"Document ID: {result['document_id']}")
   print(f"Entities: {result['graph_extraction']['entities_found']}")
   print(f"Relationships: {result['graph_extraction']['relationships_found']}")
   ```

3. **Query with graph enrichment:**
   ```bash
   # Query and verify enrichment is active
   result = graphrag_query(
       "How does FastAPI handle OAuth2 authentication?",
       use_graph_enrichment=True
   )

   # Verify graph enrichment was used
   if result['graph_enrichment_used']:
       print("✓ GraphRAG is working!")
       print(f"  Entities: {result['graph_enrichment']['entities_found']}")
       print(f"  Concepts: {result['graph_enrichment']['concepts']}")
       print(f"  Dependencies: {len(result['graph_enrichment']['dependencies'])}")
   else:
       print("⚠ Graph enrichment not active - check logs")
   ```

4. **Explore the knowledge graph:**
   ```bash
   # Open Neo4j Browser
   open http://localhost:7474

   # Verify documents and entities exist
   # Run in Neo4j Browser:
   MATCH (d:Document) RETURN d LIMIT 10
   MATCH (t:Technology) RETURN t LIMIT 25
   MATCH (d:Document)-[:MENTIONS]->(e) RETURN d, e LIMIT 50
   ```

### Production Deployment

For production use:

1. **Monitor graph enrichment usage:**
   - Track `graph_enrichment_used` in query responses
   - Monitor Neo4j query performance
   - Set up alerts for fallback to traditional RAG

2. **Optimize for scale:**
   - Use batch crawling for large documentation sites
   - Tune Neo4j memory settings for large graphs (10,000+ entities)
   - Consider caching frequent graph queries

3. **Maintain data quality:**
   - Regularly validate entity extraction quality
   - Review and clean up duplicate entities
   - Monitor relationship accuracy

### Learn More

- **[API Reference](API_REFERENCE.md)** - Full tool documentation
- **[Docker Setup](DOCKER_SETUP.md)** - Neo4j configuration and deployment
- **[Architecture](ARCHITECTURE.md)** - System design and implementation details
- **[Troubleshooting](guides/TROUBLESHOOTING.md)** - Common issues and solutions

### Get Help

Having issues with GraphRAG?

- **GitHub Issues**: https://github.com/coleam00/mcp-crawl4ai-rag/issues
- **Include in reports:**
  - MCP server logs (docker-compose logs mcp-server)
  - Neo4j connection status
  - Environment configuration (without secrets)
  - Sample query that's not working
  - Whether `graph_enrichment_used` is true/false

---

**Version:** 1.2.0 (Production-Ready GraphRAG)
**Status:** ✓ Full graph enrichment functional
**Last Updated:** 2025-10-28
