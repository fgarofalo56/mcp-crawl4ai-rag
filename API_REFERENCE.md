# API Reference - Crawl4AI RAG MCP Server

This document provides comprehensive documentation for all 16 tools available in the Crawl4AI RAG MCP Server v1.2.0.

## Table of Contents

- [Core Web Crawling Tools](#core-web-crawling-tools)
  - [crawl_single_page](#crawl_single_page)
  - [smart_crawl_url](#smart_crawl_url)
- [Advanced Crawling Tools (v1.1.0)](#advanced-crawling-tools-v110)
  - [crawl_with_stealth_mode](#crawl_with_stealth_mode)
  - [crawl_with_multi_url_config](#crawl_with_multi_url_config)
  - [crawl_with_memory_monitoring](#crawl_with_memory_monitoring)
- [RAG Search Tools](#rag-search-tools)
  - [get_available_sources](#get_available_sources)
  - [perform_rag_query](#perform_rag_query)
  - [search_code_examples](#search_code_examples)
- [Knowledge Graph Tools (Code Repositories)](#knowledge-graph-tools-code-repositories)
  - [parse_github_repository](#parse_github_repository)
  - [parse_github_repositories_batch](#parse_github_repositories_batch)
  - [check_ai_script_hallucinations](#check_ai_script_hallucinations)
  - [query_knowledge_graph](#query_knowledge_graph)
- [GraphRAG Tools (Document Knowledge Graph) 🆕 v1.2.0](#graphrag-tools-document-knowledge-graph--v120)
  - [crawl_with_graph_extraction](#crawl_with_graph_extraction) 🆕
  - [graphrag_query](#graphrag_query) 🆕
  - [query_document_graph](#query_document_graph) 🆕
  - [get_entity_context](#get_entity_context) 🆕

---

## Core Web Crawling Tools

### crawl_single_page

Quickly crawl a single web page and store its content in the vector database.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL of the web page to crawl |

#### Returns

JSON object with the following structure:
```json
{
  "success": true,
  "url": "https://example.com",
  "chunks_stored": 5,
  "code_examples_stored": 3,
  "content_length": 12345,
  "total_word_count": 2000,
  "source_id": "example.com",
  "links_count": {
    "internal": 10,
    "external": 5
  }
}
```

#### Example Usage

```python
result = await crawl_single_page(ctx, "https://docs.python.org/3/tutorial/index.html")
```

#### Error Handling

- Returns `{"success": false, "error": "..."}` if the page cannot be crawled
- Common errors: Network issues, invalid URLs, authentication required

#### Use Cases

- Quick content extraction from a single page
- Testing connectivity to a website
- Extracting specific documentation pages
- Rapid prototyping of RAG applications

---

### smart_crawl_url

Intelligently crawl a URL based on its type (sitemap, text file, or webpage with recursive crawling).

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to crawl (webpage, sitemap.xml, or .txt file) |
| `max_depth` | integer | No | 3 | Maximum recursion depth for webpage crawling |
| `max_concurrent` | integer | No | 10 | Maximum number of concurrent browser sessions |
| `chunk_size` | integer | No | 5000 | Maximum size of each content chunk in characters |

#### Returns

JSON object with crawl summary:
```json
{
  "success": true,
  "url": "https://example.com",
  "crawl_type": "sitemap|webpage|text_file",
  "pages_crawled": 25,
  "chunks_stored": 150,
  "code_examples_stored": 45,
  "sources_updated": 3,
  "urls_crawled": ["url1", "url2", "..."]
}
```

#### Example Usage

```python
# Crawl a sitemap
result = await smart_crawl_url(ctx, "https://docs.example.com/sitemap.xml")

# Crawl recursively with custom depth
result = await smart_crawl_url(ctx, "https://example.com", max_depth=5)

# Crawl with smaller chunks
result = await smart_crawl_url(ctx, "https://example.com", chunk_size=2000)
```

#### Crawl Type Detection

- **Sitemap**: URLs ending in `sitemap.xml` or containing "sitemap" in the path
- **Text file**: URLs ending in `.txt` (e.g., `llms.txt`)
- **Webpage**: All other URLs, crawled recursively following internal links

#### Performance Considerations

- Sitemap crawling is parallelized for efficiency
- Recursive crawling respects `max_depth` to prevent infinite loops
- Uses memory-adaptive dispatching to prevent OOM errors

---

## Advanced Crawling Tools (v1.1.0)

### crawl_with_stealth_mode

Crawl URLs using undetected browser mode to bypass bot protection systems.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to crawl |
| `max_depth` | integer | No | 3 | Maximum recursion depth |
| `max_concurrent` | integer | No | 10 | Maximum concurrent sessions |
| `chunk_size` | integer | No | 5000 | Chunk size in characters |
| `wait_for_selector` | string | No | "" | CSS selector to wait for |
| `extra_wait` | integer | No | 2 | Additional wait time in seconds |

#### Returns

```json
{
  "success": true,
  "crawl_type": "stealth_webpage",
  "url": "https://protected-site.com",
  "mode": "stealth (undetected browser)",
  "pages_crawled": 10,
  "total_chunks": 50
}
```

#### Example Usage

```python
# Bypass Cloudflare protection
result = await crawl_with_stealth_mode(
    ctx,
    "https://cloudflare-protected.com",
    wait_for_selector="div.main-content",
    extra_wait=3
)

# Crawl e-commerce site with dynamic content
result = await crawl_with_stealth_mode(
    ctx,
    "https://shop.example.com",
    wait_for_selector=".product-list",
    extra_wait=5
)
```

#### Stealth Features

- Uses `undetected-chromedriver` to avoid detection
- Overrides navigator properties to hide automation
- Simulates human-like behavior
- Bypasses common bot detection services:
  - Cloudflare
  - Akamai
  - PerimeterX
  - DataDome

#### Limitations

- 2-3x slower than regular crawling
- May not work on extremely sophisticated detection systems
- Requires undetected-chromedriver (auto-installed)

---

### crawl_with_multi_url_config

Crawl multiple URLs with automatic per-URL configuration based on content type.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `urls_json` | string | Yes | - | JSON array of URLs to crawl |
| `max_concurrent` | integer | No | 5 | Maximum concurrent sessions |
| `chunk_size` | integer | No | 5000 | Chunk size in characters |

#### Returns

```json
{
  "success": true,
  "urls_processed": 3,
  "total_chunks": 150,
  "results": [
    {
      "url": "https://docs.python.org",
      "content_type": "documentation",
      "success": true,
      "pages_crawled": 15,
      "chunks_stored": 75
    },
    {
      "url": "https://blog.example.com",
      "content_type": "article",
      "success": true,
      "pages_crawled": 5,
      "chunks_stored": 25
    }
  ]
}
```

#### Example Usage

```python
# Crawl multiple documentation sites
urls = '["https://docs.python.org", "https://fastapi.tiangolo.com", "https://docs.pytest.org"]'
result = await crawl_with_multi_url_config(ctx, urls)

# Mixed content types
urls = '["https://news.site.com", "https://docs.api.com", "https://blog.example.com"]'
result = await crawl_with_multi_url_config(ctx, urls, max_concurrent=3)
```

#### Content Type Detection

| URL Pattern | Content Type | Optimizations Applied |
|-------------|--------------|----------------------|
| Contains: `docs`, `documentation`, `api`, `reference` | Documentation | Lower word threshold, wait for code blocks, target technical selectors |
| Contains: `news`, `article`, `blog`, `post` | Article | Higher word threshold, focus on main content, article-specific selectors |
| All others | General | Standard balanced settings |

#### Best Practices

- Group similar content types for better performance
- Start with lower concurrency (3-5) for stability
- Monitor memory usage for large batches

---

### crawl_with_memory_monitoring

Crawl URLs with active memory monitoring and adaptive throttling.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to crawl |
| `max_depth` | integer | No | 3 | Maximum recursion depth |
| `max_concurrent` | integer | No | 10 | Initial concurrent sessions |
| `chunk_size` | integer | No | 5000 | Chunk size in characters |
| `memory_threshold_mb` | integer | No | 500 | Memory limit before throttling (MB) |

#### Returns

```json
{
  "success": true,
  "crawl_type": "memory_monitored_sitemap",
  "url": "https://large-docs.com/sitemap.xml",
  "pages_crawled": 500,
  "total_chunks": 2500,
  "memory_stats": {
    "start_mb": 150.5,
    "end_mb": 487.3,
    "peak_mb": 495.2,
    "delta_mb": 336.8,
    "avg_mb": 320.4,
    "threshold_mb": 500,
    "elapsed_seconds": 245.7
  }
}
```

#### Example Usage

```python
# Large-scale documentation crawl
result = await crawl_with_memory_monitoring(
    ctx,
    "https://massive-docs.com/sitemap.xml",
    memory_threshold_mb=400
)

# Crawl with conservative memory limit
result = await crawl_with_memory_monitoring(
    ctx,
    "https://docs.example.com",
    memory_threshold_mb=200,
    max_concurrent=5
)
```

#### Memory Management Features

- Real-time memory tracking with psutil
- Automatic concurrency reduction when threshold exceeded
- Batch processing for sitemaps with memory checks
- Comprehensive memory statistics reporting

#### When to Use

- Large-scale documentation sites (1000+ pages)
- Sites with heavy media content
- Long-running crawl operations
- Resource-constrained environments
- Production deployments requiring stability

---

## RAG Search Tools

### get_available_sources

Get all available sources (domains) from the database for filtering.

#### Parameters

No parameters required.

#### Returns

```json
{
  "success": true,
  "sources": [
    {
      "source_id": "docs.python.org",
      "summary": "Official Python documentation...",
      "total_words": 450000,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-20T15:45:00Z"
    }
  ],
  "count": 5
}
```

#### Example Usage

```python
# Get all available sources
sources = await get_available_sources(ctx)

# Use sources for filtered search
for source in sources["sources"]:
    results = await perform_rag_query(ctx, "async functions", source["source_id"])
```

#### Best Practices

- Always call this before using source-filtered searches
- Cache results if making multiple filtered queries
- Use source summaries to understand content scope

---

### perform_rag_query

Perform semantic search on stored content with optional source filtering.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `source` | string | No | None | Source domain to filter results |
| `match_count` | integer | No | 5 | Maximum number of results |

#### Returns

```json
{
  "success": true,
  "query": "async programming",
  "source_filter": "docs.python.org",
  "search_mode": "hybrid",
  "reranking_applied": true,
  "results": [
    {
      "url": "https://docs.python.org/3/library/asyncio.html",
      "content": "Content chunk...",
      "metadata": {
        "headers": "## Coroutines and Tasks",
        "chunk_index": 3
      },
      "similarity": 0.89,
      "rerank_score": 0.95
    }
  ],
  "count": 5
}
```

#### Example Usage

```python
# Basic semantic search
results = await perform_rag_query(ctx, "how to use async/await in Python")

# Filtered search
results = await perform_rag_query(
    ctx,
    "authentication",
    source="fastapi.tiangolo.com",
    match_count=10
)

# Complex technical query
results = await perform_rag_query(
    ctx,
    "difference between asyncio.create_task and asyncio.ensure_future",
    match_count=3
)
```

#### Search Modes

Depending on configuration:
- **Vector search**: Semantic similarity matching
- **Hybrid search**: Combines vector and keyword search (if `USE_HYBRID_SEARCH=true`)
- **Reranking**: Applied after initial retrieval (if `USE_RERANKING=true`)

---

### search_code_examples

Search for code examples and their summaries (requires `USE_AGENTIC_RAG=true`).

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query for code examples |
| `source_id` | string | No | None | Source to filter results |
| `match_count` | integer | No | 5 | Maximum number of results |

#### Returns

```json
{
  "success": true,
  "query": "FastAPI middleware",
  "source_filter": "fastapi.tiangolo.com",
  "search_mode": "hybrid",
  "reranking_applied": true,
  "results": [
    {
      "url": "https://fastapi.tiangolo.com/tutorial/middleware/",
      "code": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.middleware(\"http\")...",
      "summary": "Example of creating custom middleware in FastAPI...",
      "metadata": {
        "chunk_index": 0,
        "char_count": 450
      },
      "source_id": "fastapi.tiangolo.com",
      "similarity": 0.92,
      "rerank_score": 0.96
    }
  ],
  "count": 5
}
```

#### Example Usage

```python
# Search for specific code patterns
results = await search_code_examples(ctx, "decorator pattern in Python")

# Find framework-specific examples
results = await search_code_examples(
    ctx,
    "request validation",
    source_id="fastapi.tiangolo.com"
)
```

#### Prerequisites

- Must have `USE_AGENTIC_RAG=true` in configuration
- Code examples are extracted during crawling (slower indexing)
- Only code blocks ≥300 characters are indexed

---

## Knowledge Graph Tools

### parse_github_repository

Parse a GitHub repository into the Neo4j knowledge graph for hallucination detection.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_url` | string | Yes | GitHub repository URL (must end with .git or be a valid GitHub URL) |

#### Returns

```json
{
  "success": true,
  "repo_url": "https://github.com/pydantic/pydantic-ai.git",
  "repo_name": "pydantic-ai",
  "message": "Successfully parsed repository 'pydantic-ai' into knowledge graph",
  "statistics": {
    "repository": "pydantic-ai",
    "files_processed": 45,
    "classes_created": 78,
    "methods_created": 342,
    "functions_created": 156,
    "attributes_created": 234,
    "sample_modules": ["pydantic_ai.agent", "pydantic_ai.tools", "pydantic_ai.models"]
  },
  "ready_for_validation": true,
  "next_steps": [
    "Repository is now available for hallucination detection",
    "Use check_ai_script_hallucinations to validate scripts against pydantic-ai",
    "The knowledge graph contains classes, methods, and functions from this repository"
  ]
}
```

#### Example Usage

```python
# Parse a repository
result = await parse_github_repository(
    ctx,
    "https://github.com/langchain-ai/langchain.git"
)

# Parse specific framework
result = await parse_github_repository(
    ctx,
    "https://github.com/fastapi/fastapi.git"
)
```

#### Processing Steps

1. Clones repository to temporary location
2. Analyzes all Python files using AST
3. Extracts classes, methods, functions, and imports
4. Stores structure in Neo4j knowledge graph
5. Creates relationships between code elements

#### Prerequisites

- Requires `USE_KNOWLEDGE_GRAPH=true`
- Neo4j must be running and configured
- Only processes Python files currently

---

### parse_github_repositories_batch

🆕 **v1.1.1** - Parse multiple GitHub repositories in parallel with intelligent retry logic and progress tracking.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repo_urls_json` | string | Yes | - | JSON array of GitHub repository URLs |
| `max_concurrent` | integer | No | 3 | Maximum number of repositories to process simultaneously |
| `max_retries` | integer | No | 2 | Number of retry attempts for failed repositories |

#### Returns

```json
{
  "success": true,
  "summary": {
    "total_repositories": 5,
    "successful": 4,
    "failed": 1,
    "retried": 2,
    "validation_errors": 0,
    "elapsed_seconds": 187.42,
    "average_time_per_repo": 37.48
  },
  "results": [
    {
      "url": "https://github.com/openai/openai-python.git",
      "repository": "openai-python",
      "status": "success",
      "attempt": 1,
      "statistics": {
        "files_processed": 245,
        "classes_created": 67,
        "methods_created": 412,
        "functions_created": 89
      }
    }
  ],
  "aggregate_statistics": {
    "total_files_processed": 1203,
    "total_classes_created": 345,
    "total_methods_created": 2104,
    "total_functions_created": 567
  },
  "failed_repositories": [
    {
      "url": "https://github.com/user/problematic-repo.git",
      "repository": "problematic-repo",
      "error": "Connection timeout",
      "attempts": 3
    }
  ],
  "retry_urls": [
    "https://github.com/user/problematic-repo.git"
  ]
}
```

#### Example Usage

```python
# Basic batch processing
repos = '''[
  "https://github.com/openai/openai-python.git",
  "https://github.com/anthropics/anthropic-sdk-python.git",
  "https://github.com/langchain-ai/langchain.git"
]'''
result = await parse_github_repositories_batch(ctx, repos)

# High concurrency for faster processing
result = await parse_github_repositories_batch(
    ctx,
    repos,
    max_concurrent=10,
    max_retries=3
)

# Low resource mode
result = await parse_github_repositories_batch(
    ctx,
    repos,
    max_concurrent=1,  # Sequential
    max_retries=0      # No retries
)

# Retry failed repositories
failed_urls = result["retry_urls"]
retry_json = json.dumps(failed_urls)
result = await parse_github_repositories_batch(ctx, retry_json, max_retries=5)
```

#### Key Features

1. **Parallel Processing**: Process multiple repos simultaneously with configurable concurrency
2. **Automatic Retries**: Failed repos are automatically retried with exponential backoff
3. **Progress Tracking**: Real-time console output shows processing status
4. **Error Isolation**: One repo failure doesn't affect others
5. **Detailed Results**: Per-repo status tracking with statistics
6. **Easy Retry**: Failed URLs are collected for simple retry

#### Best Practices

| Batch Size | Recommended Settings |
|------------|---------------------|
| 2-5 repos | `max_concurrent=2, max_retries=2` |
| 6-15 repos | `max_concurrent=3, max_retries=2` (default) |
| 15+ repos | `max_concurrent=5, max_retries=3` |
| Low memory | `max_concurrent=1, max_retries=1` |

#### Prerequisites

- Requires `USE_KNOWLEDGE_GRAPH=true`
- Neo4j must be running and configured
- Sufficient memory for concurrent operations
- Stable network connection for multiple clones

---

### check_ai_script_hallucinations

Analyze AI-generated Python scripts for hallucinations by validating against the knowledge graph.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `script_path` | string | Yes | Absolute path to the Python script to analyze |

#### Returns

```json
{
  "success": true,
  "script_path": "/path/to/script.py",
  "overall_confidence": 0.78,
  "validation_summary": {
    "total_validations": 25,
    "valid_count": 18,
    "invalid_count": 4,
    "uncertain_count": 2,
    "not_found_count": 1,
    "hallucination_rate": 0.28
  },
  "hallucinations_detected": [
    {
      "type": "method",
      "item": "Agent.run_async",
      "issue": "Method 'run_async' does not exist on class 'Agent'",
      "confidence": 0.95,
      "suggestion": "Did you mean 'run_stream'?"
    },
    {
      "type": "parameter",
      "item": "Tool.__init__",
      "issue": "Unexpected parameter 'timeout' in Tool constructor",
      "confidence": 0.88
    }
  ],
  "recommendations": [
    "Review method calls on Agent class",
    "Check Tool initialization parameters",
    "Consider using 'run_stream' instead of 'run_async'"
  ],
  "analysis_metadata": {
    "total_imports": 5,
    "total_classes": 3,
    "total_methods": 12,
    "total_attributes": 8,
    "total_functions": 7
  },
  "libraries_analyzed": ["pydantic_ai", "langchain"]
}
```

#### Example Usage

```python
# Validate an AI-generated script
result = await check_ai_script_hallucinations(
    ctx,
    "/home/user/ai_generated_script.py"
)

# Check script after generation
script_path = "/tmp/new_agent.py"
# ... AI generates script ...
validation = await check_ai_script_hallucinations(ctx, script_path)
if validation["hallucination_rate"] > 0.2:
    print("Warning: High hallucination rate detected!")
```

#### Validation Types

- **Import validation**: Checks if imported modules/classes exist
- **Method validation**: Verifies methods exist on classes
- **Parameter validation**: Checks function/method parameters
- **Attribute validation**: Verifies class attributes exist
- **Instantiation validation**: Validates constructor parameters

---

### query_knowledge_graph

Query and explore the Neo4j knowledge graph containing repository data.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | Command string to execute (see commands below) |

#### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `repos` | List all repositories | `repos` |
| `explore <repo>` | Get repository overview | `explore pydantic-ai` |
| `classes [repo]` | List classes | `classes` or `classes fastapi` |
| `class <name>` | Get class details | `class Agent` |
| `method <name> [class]` | Find methods | `method run_stream` or `method __init__ Agent` |
| `query <cypher>` | Execute Cypher query | `query MATCH (c:Class) RETURN c.name LIMIT 5` |

#### Returns

```json
{
  "success": true,
  "command": "explore pydantic-ai",
  "data": {
    "repository": "pydantic-ai",
    "statistics": {
      "files": 45,
      "classes": 78,
      "functions": 156,
      "methods": 342
    }
  },
  "metadata": {
    "total_results": 1,
    "limited": false
  }
}
```

#### Example Usage

```python
# List all repositories
result = await query_knowledge_graph(ctx, "repos")

# Explore a repository
result = await query_knowledge_graph(ctx, "explore langchain")

# Find a specific class
result = await query_knowledge_graph(ctx, "class Agent")

# Search for methods
result = await query_knowledge_graph(ctx, "method run_stream")

# Custom Cypher query
result = await query_knowledge_graph(
    ctx,
    "query MATCH (c:Class)-[:HAS_METHOD]->(m:Method) WHERE m.name = 'run' RETURN c.name, m.name LIMIT 10"
)
```

#### Knowledge Graph Schema

**Nodes:**
- `Repository {name: string}`
- `File {path: string, module_name: string}`
- `Class {name: string, full_name: string}`
- `Method {name: string, params_list: [string], return_type: string}`
- `Function {name: string, params_list: [string], return_type: string}`
- `Attribute {name: string, type: string}`

**Relationships:**
- `(Repository)-[:CONTAINS]->(File)`
- `(File)-[:DEFINES]->(Class)`
- `(Class)-[:HAS_METHOD]->(Method)`
- `(Class)-[:HAS_ATTRIBUTE]->(Attribute)`
- `(File)-[:DEFINES]->(Function)`

---

## Error Handling

All tools follow consistent error handling patterns:

### Success Response

```json
{
  "success": true,
  // tool-specific data
}
```

### Error Response

```json
{
  "success": false,
  "error": "Detailed error message",
  // additional context if available
}
```

### Common Error Types

1. **Network Errors**: Connection timeouts, DNS failures
2. **Authentication Errors**: Invalid credentials, access denied
3. **Validation Errors**: Invalid URLs, malformed parameters
4. **Configuration Errors**: Missing environment variables
5. **Resource Errors**: Memory limits, rate limiting

## Best Practices

### General Guidelines

1. **Always check `get_available_sources`** before filtered searches
2. **Start with small `max_depth`** for recursive crawling (2-3)
3. **Use appropriate chunk sizes** (2000-5000 characters)
4. **Monitor memory usage** for large operations
5. **Enable hybrid search** for technical content
6. **Use stealth mode sparingly** (slower performance)

### Performance Tips

1. **Batch similar URLs** when using multi-URL config
2. **Lower concurrency** for stability (3-5 for stealth, 5-10 for regular)
3. **Enable reranking** only when precision is critical
4. **Cache source lists** to avoid repeated queries
5. **Use code search** only when specifically needed

### Configuration Recommendations

**For documentation sites:**
```
USE_HYBRID_SEARCH=true
USE_RERANKING=true
chunk_size=5000
```

**For protected sites:**
```
Use crawl_with_stealth_mode
extra_wait=3-5 seconds
max_concurrent=3
```

**For large-scale operations:**
```
Use crawl_with_memory_monitoring
memory_threshold_mb=300-500
Monitor memory_stats in response
```

---

## GraphRAG Tools (Document Knowledge Graph) 🆕 v1.2.0

GraphRAG extends traditional vector RAG with knowledge graph capabilities for web content. These tools extract entities and relationships from documents, creating a structured knowledge graph that enables richer context, multi-hop reasoning, and reduced hallucinations.

**Key Difference from Code Knowledge Graph:**
- **Code KG Tools** (above): Parse GitHub repositories for code structure analysis
- **GraphRAG Tools** (this section): Extract concepts from any web content for enhanced RAG

See [docs/GRAPHRAG_GUIDE.md](./docs/GRAPHRAG_GUIDE.md) for comprehensive documentation.

---

### crawl_with_graph_extraction

Crawl a URL and extract both vector embeddings (Supabase) AND knowledge graph (Neo4j).

This is the core GraphRAG crawl tool - it performs standard web crawling with vector embeddings PLUS extracts entities and relationships into a knowledge graph for graph-augmented RAG.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to crawl |
| `extract_entities` | boolean | No | true | Whether to extract entities from content |
| `extract_relationships` | boolean | No | true | Whether to extract relationships between entities |
| `chunk_size` | integer | No | 5000 | Size of text chunks for processing |

#### Returns

JSON object with crawl and graph extraction results:
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

#### Example Usage

```python
# Basic usage
result = await crawl_with_graph_extraction(ctx, "https://fastapi.tiangolo.com/tutorial/")

# Disable relationship extraction for faster processing
result = await crawl_with_graph_extraction(
    ctx,
    "https://docs.python.org/3/",
    extract_relationships=False
)
```

#### Prerequisites

- `USE_GRAPHRAG=true` in environment
- Neo4j running and configured
- OpenAI API key for entity extraction

#### Use Cases

- Building knowledge graphs from technical documentation
- Creating interconnected knowledge bases
- Enabling graph-enriched RAG queries
- Understanding entity relationships across documents

---

### graphrag_query

Perform RAG query with optional graph enrichment for richer context.

Combines vector similarity search (traditional RAG) with knowledge graph traversal to provide more comprehensive answers that understand entity relationships, dependencies, and connections.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `use_graph_enrichment` | boolean | No | true | Enable graph context enrichment |
| `max_entities` | integer | No | 15 | Maximum entities to include in enrichment |
| `source_filter` | string | No | null | Optional source domain filter |

#### Returns

JSON object with answer and context:
```json
{
  "success": true,
  "query": "How do I configure OAuth2 in FastAPI?",
  "answer": "[Detailed answer with relationships and dependencies]",
  "graph_enrichment_used": true,
  "documents_found": 5,
  "sources": [
    {"url": "https://fastapi.tiangolo.com/tutorial/security/", "relevance": 0.87},
    ...
  ]
}
```

#### Example Usage

```python
# With graph enrichment (richer context, slower)
answer = await graphrag_query(
    ctx,
    "What are the dependencies for deploying FastAPI with Docker?",
    use_graph_enrichment=True
)

# Without graph enrichment (faster, simpler)
answer = await graphrag_query(
    ctx,
    "What is FastAPI?",
    use_graph_enrichment=False
)

# Filter by source
answer = await graphrag_query(
    ctx,
    "How to use Pydantic?",
    source_filter="fastapi.tiangolo.com"
)
```

#### When to Use Graph Enrichment

**✅ Enable for:**
- Complex "how do X and Y relate?" questions
- Dependency and prerequisite questions
- Multi-step procedures
- Questions requiring deep understanding

**❌ Disable for:**
- Simple factual lookups ("What is X?")
- Time-sensitive queries (graph adds latency)
- Very broad questions

---

### query_document_graph

Execute custom Cypher queries on the document knowledge graph.

Provides direct access to Neo4j document graph for advanced users who want to write custom graph queries for exploration and analysis.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cypher_query` | string | Yes | Cypher query string |

#### Returns

JSON object with query results:
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

#### Example Queries

**Find all technologies:**
```cypher
MATCH (t:Technology)
RETURN t.name, t.description
LIMIT 20
```

**Find dependencies:**
```cypher
MATCH (a)-[r:REQUIRES]->(b)
RETURN a.name, b.name, r.description
```

**Find most-mentioned entities:**
```cypher
MATCH (d:Document)-[m:MENTIONS]->(e)
RETURN e.name, labels(e)[0] as type, sum(m.count) as mentions
ORDER BY mentions DESC
LIMIT 10
```

**Find entities in specific source:**
```cypher
MATCH (d:Document {source_id: 'fastapi.tiangolo.com'})-[:MENTIONS]->(e:Technology)
RETURN DISTINCT e.name, e.description
```

#### Example Usage

```python
query = """
MATCH (c:Configuration)<-[:REQUIRES]-(t:Technology)
RETURN t.name as technology, c.name as config
ORDER BY technology
"""
result = await query_document_graph(ctx, query)
```

#### Prerequisites

- `USE_GRAPHRAG=true` in environment
- Neo4j configured and running
- Documents crawled with `crawl_with_graph_extraction`

---

### get_entity_context

Get comprehensive context for a specific entity from the knowledge graph.

Retrieves an entity and its neighborhood in the graph, including related entities, relationships, and documents mentioning the entity. Useful for understanding what an entity is and how it connects to other concepts.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `entity_name` | string | Yes | - | Name of entity to look up (e.g., "FastAPI", "OAuth2") |
| `max_hops` | integer | No | 2 | Maximum relationship hops to traverse |

#### Returns

JSON object with entity context:
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
    {"id": "...", "url": "https://...", "title": "..."},
    ...
  ],
  "stats": {
    "related_entities_count": 8,
    "relationships_count": 12,
    "documents_count": 3
  }
}
```

#### Example Usage

```python
# Get FastAPI context with 2 hops
context = await get_entity_context(ctx, "FastAPI", max_hops=2)

# Get Docker context with 1 hop (direct relationships only)
context = await get_entity_context(ctx, "Docker", max_hops=1)
```

#### Use Cases

- Understanding what an entity is and how it relates
- Finding all documents about a specific technology
- Exploring entity neighborhoods
- Building context for complex questions

---

## GraphRAG Configuration

Add to your `.env` file:

```bash
# Enable GraphRAG
USE_GRAPHRAG=true

# Neo4j (same as code knowledge graph)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI for entity extraction
OPENAI_API_KEY=sk-your-key-here
```

## GraphRAG vs Traditional RAG

| Feature | Traditional RAG | GraphRAG |
|---------|----------------|----------|
| **Search Method** | Vector similarity only | Vector + Graph traversal |
| **Context Understanding** | Document chunks | Chunks + Entity relationships |
| **Multi-hop Reasoning** | Limited | Excellent |
| **Dependency Detection** | No | Yes (explicit in graph) |
| **Hallucination Risk** | Higher | Lower (structured facts) |
| **Speed** | Faster | Slower (~2-3x) |
| **Setup Complexity** | Simple | Moderate (+ Neo4j) |
| **Cost** | Vector storage | Vector + Graph + Entity extraction |

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and updates.

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/coleam00/mcp-crawl4ai-rag/issues).