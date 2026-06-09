# Production Scaling Guide

**Version**: 1.3.0
**Last Updated**: 2025-10-07
**Target Audience**: DevOps Engineers, Production Deployments

---

## Table of contents

- [Overview](#overview)
- [Architecture for Scale](#architecture-for-scale)
- [Batch Processing Strategies](#batch-processing-strategies)
- [Memory Management](#memory-management)
- [Concurrent Crawling](#concurrent-crawling)
- [Rate Limiting Configuration](#rate-limiting-configuration)
- [Database Optimization](#database-optimization)
- [Performance Benchmarks](#performance-benchmarks)
- [Monitoring and Observability](#monitoring-and-observability)
- [Cost Optimization](#cost-optimization)
- [Troubleshooting at Scale](#troubleshooting-at-scale)

---

## Overview

This guide provides best practices for scaling the Crawl4AI RAG MCP Server for production deployments, covering:

- Processing hundreds to thousands of pages
- Managing concurrent operations
- Optimizing database performance
- Controlling costs
- Monitoring system health

### Scale Targets

| Scale | Pages | Entities | Concurrent Operations | Recommended Setup |
|-------|-------|----------|----------------------|-------------------|
| **Small** | <100 | <1,000 | 3-5 | Single server, local DB |
| **Medium** | 100-1,000 | 1,000-10,000 | 5-10 | Docker Compose, cloud DB optional |
| **Large** | 1,000-10,000 | 10,000-100,000 | 10-20 | Kubernetes, cloud DB required |
| **Enterprise** | 10,000+ | 100,000+ | 20-50 | Multi-region, dedicated infrastructure |

---

## Architecture for Scale

### Single Server (Small Scale)

```
┌─────────────────────────────┐
│  MCP Server (stdio/SSE)     │
│  - Max 5 concurrent crawls  │
│  - Memory limit: 4GB        │
└─────────────────────────────┘
         │         │
         ▼         ▼
    ┌────────┐  ┌──────────┐
    │ Neo4j  │  │ Supabase │
    │ Local  │  │  Cloud   │
    └────────┘  └──────────┘
```

**Best For**: Development, small teams, <100 pages
**Infrastructure**: Docker Compose or local installation
**Costs**: Minimal (Supabase free tier, local Neo4j)

### Distributed Architecture (Medium-Large Scale)

```
┌──────────────────────────────────────────┐
│  Load Balancer (Nginx/Traefik)           │
└──────────────────────────────────────────┘
         │          │          │
         ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │  MCP   │ │  MCP   │ │  MCP   │
    │ Server │ │ Server │ │ Server │
    │ (SSE)  │ │ (SSE)  │ │ (SSE)  │
    └────────┘ └────────┘ └────────┘
         │          │          │
         └──────────┴──────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    ┌──────────┐      ┌─────────────┐
    │  Neo4j   │      │  Supabase   │
    │  Cluster │      │  Production │
    └──────────┘      └─────────────┘
```

**Best For**: Production, multiple teams, 1,000+ pages
**Infrastructure**: Kubernetes, Docker Swarm, or managed services
**Costs**: Moderate to high (cloud databases, multiple servers)

---

## Batch Processing Strategies

### Sequential Processing (Safest)

For maximum reliability, process one item at a time:

```python
def crawl_documentation_sequential(urls):
    """Process URLs one by one with full error handling."""
    results = []
    for i, url in enumerate(urls):
        print(f"Processing {i+1}/{len(urls)}: {url}")
        try:
            result = crawl_with_graph_extraction(url)
            results.append({"url": url, "status": "success", "data": result})
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})
        # Pause between requests
        time.sleep(2)

    return results
```

**Pros**: Predictable memory usage, simple error handling
**Cons**: Slower processing
**Use When**: Memory constrained, unreliable network, critical operations

### Batch Processing (Faster)

Process URLs in batches to balance speed and reliability:

```python
def crawl_in_batches(urls, batch_size=10, delay_between_batches=5):
    """Process URLs in batches with delays."""
    all_results = []

    for batch_num, i in enumerate(range(0, len(urls), batch_size)):
        batch = urls[i:i+batch_size]
        print(f"Batch {batch_num+1}: Processing {len(batch)} URLs")

        batch_results = []
        for url in batch:
            try:
                result = crawl_with_graph_extraction(url)
                batch_results.append(result)
            except Exception as e:
                print(f"Error on {url}: {e}")
                batch_results.append({"error": str(e)})

        all_results.extend(batch_results)

        # Delay between batches to avoid rate limits
        if i + batch_size < len(urls):
            time.sleep(delay_between_batches)

    return all_results
```

**Pros**: Faster than sequential, manageable memory
**Cons**: More complex error handling
**Use When**: Processing 50+ pages, reliable network

### Parallel Processing with Concurrency Control

For maximum speed with controlled resource usage:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading

def crawl_with_concurrency_limit(urls, max_workers=5):
    """Process URLs in parallel with concurrency limit."""
    results = {}
    failed = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(crawl_with_graph_extraction, url): url
            for url in urls
        }

        # Process completed tasks
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results[url] = result
            except Exception as e:
                failed.append({"url": url, "error": str(e)})

    return {"successful": results, "failed": failed}
```

**Pros**: Fastest processing, efficient resource use
**Cons**: Complex error handling, higher memory usage
**Use When**: Processing 100+ pages, powerful infrastructure

### Repository Batch Processing

Use the built-in batch processor for GitHub repositories:

```python
# Built-in batch processing with automatic retries
repos = [
    "https://github.com/openai/openai-python.git",
    "https://github.com/anthropics/anthropic-sdk-python.git",
    "https://github.com/langchain-ai/langchain.git"
]

result = parse_github_repositories_batch(
    repo_urls_json=json.dumps(repos),
    max_concurrent=3,  # Adjust based on resources
    max_retries=2      # Automatic retry on failure
)

# Check aggregate statistics
print(f"Successful: {result['summary']['successful']}")
print(f"Failed: {result['summary']['failed']}")
print(f"Total classes: {result['aggregate_statistics']['total_classes_created']}")
```

---

## Memory Management

### Memory Monitoring Best Practices

Always use memory monitoring for large-scale operations:

```python
# Crawl with memory monitoring
result = crawl_with_memory_monitoring(
    url="https://large-docs.com/sitemap.xml",
    max_depth=3,
    max_concurrent=10,
    memory_threshold_mb=500  # Adjust based on available memory
)

# Check memory statistics
print(f"Peak memory: {result['memory_stats']['peak_mb']}MB")
print(f"Average memory: {result['memory_stats']['avg_mb']}MB")
```

### Memory Limits by Deployment Type

| Deployment | Recommended Limit | Threshold Setting | Max Concurrent |
|------------|------------------|-------------------|----------------|
| Local Dev | 2GB | 400MB | 5 |
| Docker (4GB) | 3GB | 500MB | 10 |
| Docker (8GB) | 6GB | 800MB | 15 |
| Kubernetes Pod | 80% of limit | Varies | 20+ |

### Memory Optimization Techniques

#### 1. Adjust Chunk Sizes

Smaller chunks = lower memory usage but more API calls:

```python
# High memory usage (default)
crawl_with_graph_extraction(url, chunk_size=5000)

# Lower memory usage
crawl_with_graph_extraction(url, chunk_size=2000)

# Minimal memory usage
crawl_with_graph_extraction(url, chunk_size=1000)
```

#### 2. Process and Release

Process results immediately instead of accumulating:

```python
# BAD: Accumulates all results in memory
results = [crawl_single_page(url) for url in urls]

# GOOD: Process and release
for url in urls:
    result = crawl_single_page(url)
    process_result(result)  # Use immediately
    del result  # Release memory
```

#### 3. Use Streaming for Large Sitemaps

```python
import xml.etree.ElementTree as ET

def process_large_sitemap_streaming(sitemap_url):
    """Process sitemap without loading all URLs into memory."""
    response = requests.get(sitemap_url, stream=True)

    for event, elem in ET.iterparse(response.raw):
        if elem.tag.endswith('url'):
            loc = elem.find('.//{*}loc')
            if loc is not None:
                url = loc.text
                crawl_single_page(url)
                elem.clear()  # Release memory
```

---

## Concurrent Crawling

### Concurrency Limits by Site Type

Different sites require different concurrency levels:

| Site Type | Max Concurrent | Reason |
|-----------|----------------|--------|
| Documentation Sites | 10-15 | Usually well-structured, reliable |
| News/Blogs | 5-8 | Dynamic content, may have rate limits |
| E-commerce | 3-5 | Bot detection, anti-scraping measures |
| Protected Sites (Cloudflare) | 2-3 | Stealth mode required, slower |
| APIs/Sitemaps | 15-20 | Simple, predictable responses |

### Adaptive Concurrency

Automatically adjust concurrency based on performance:

```python
class AdaptiveCrawler:
    def __init__(self, initial_concurrency=5):
        self.concurrency = initial_concurrency
        self.success_rate = 1.0
        self.errors = 0
        self.successes = 0

    def adjust_concurrency(self):
        """Adjust concurrency based on success rate."""
        if self.success_rate < 0.7:
            # Too many errors, reduce concurrency
            self.concurrency = max(1, self.concurrency - 1)
        elif self.success_rate > 0.95 and self.concurrency < 20:
            # High success rate, increase concurrency
            self.concurrency += 1

    def crawl_adaptive(self, urls):
        for url in urls:
            try:
                result = crawl_single_page(url)
                self.successes += 1
            except Exception as e:
                self.errors += 1

            total = self.successes + self.errors
            self.success_rate = self.successes / total if total > 0 else 1.0

            # Adjust after every 10 requests
            if total % 10 == 0:
                self.adjust_concurrency()
```

---

## Rate Limiting Configuration

### OpenAI API Rate Limits

GraphRAG and embedding generation use OpenAI API. Know your limits:

| Tier | Requests Per Minute (RPM) | Tokens Per Minute (TPM) | Monthly Cost |
|------|--------------------------|------------------------|--------------|
| Free | 3 | 40,000 | $0 |
| Tier 1 | 3,500 | 200,000 | $5+ |
| Tier 2 | 5,000 | 300,000 | $50+ |
| Tier 3 | 10,000 | 1,000,000 | $100+ |
| Tier 4 | 30,000 | 5,000,000 | $250+ |

### Rate Limit Configuration

```python
# Install rate limiting library
# pip install ratelimit

from ratelimit import limits, sleep_and_retry

# Tier 1: 3,500 RPM = ~58 requests per second
@sleep_and_retry
@limits(calls=50, period=60)  # 50 calls per minute (conservative)
def rate_limited_crawl(url):
    return crawl_with_graph_extraction(url)

# Use in batch processing
for url in urls:
    result = rate_limited_crawl(url)
```

### Exponential Backoff for API Errors

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    retry=retry_if_exception_type(OpenAIError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def crawl_with_retry(url):
    """Automatically retry on API errors with exponential backoff."""
    return crawl_with_graph_extraction(url)
```

---

## Database Optimization

### Supabase (PostgreSQL + pgvector)

#### Connection Pooling

```python
from supabase import create_client, Client

# Use connection pooling for high concurrency
supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_KEY"),
    options={
        "db": {
            "pool": {
                "min": 2,
                "max": 10  # Adjust based on concurrent operations
            }
        }
    }
)
```

#### Batch Insertions

Insert multiple documents at once:

```python
# BAD: One insert per document
for doc in documents:
    supabase.table("crawled_pages").insert(doc).execute()

# GOOD: Batch insert
supabase.table("crawled_pages").insert(documents).execute()
```

#### Indexes for Performance

Ensure proper indexes exist (run in Supabase SQL editor):

```sql
-- Index on source_id for filtered searches
CREATE INDEX IF NOT EXISTS idx_crawled_pages_source
ON crawled_pages(source_id);

-- Index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_crawled_pages_created
ON crawled_pages(created_at DESC);

-- Index for full-text search (if using hybrid search)
CREATE INDEX IF NOT EXISTS idx_crawled_pages_content_gin
ON crawled_pages USING gin(to_tsvector('english', content));
```

### Neo4j Optimization

#### Connection Pooling

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    uri=os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    max_connection_pool_size=50,  # Adjust based on concurrent operations
    connection_timeout=30
)
```

#### Batch Graph Operations

Create nodes and relationships in batches:

```cypher
-- Create multiple nodes at once
UNWIND $entities AS entity
CREATE (e:Entity {name: entity.name, type: entity.type, description: entity.description})

-- Create multiple relationships at once
UNWIND $relationships AS rel
MATCH (a:Entity {name: rel.from})
MATCH (b:Entity {name: rel.to})
CREATE (a)-[r:RELATIONSHIP {type: rel.type}]->(b)
```

#### Essential Indexes

```cypher
-- Entity name index (critical for graph queries)
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);

-- Document ID index
CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.id);

-- Source index
CREATE INDEX source_id IF NOT EXISTS FOR (s:Source) ON (s.id);

-- Composite index for document-entity relationships
CREATE INDEX doc_entity IF NOT EXISTS FOR ()-[m:MENTIONS]-() ON (m.count);
```

#### Query Optimization

```cypher
-- BAD: No index usage
MATCH (e:Entity)
WHERE e.name CONTAINS "FastAPI"
RETURN e

-- GOOD: Uses index
MATCH (e:Entity {name: "FastAPI"})
RETURN e

-- GOOD: Index range scan
MATCH (e:Entity)
WHERE e.name STARTS WITH "Fast"
RETURN e
```

---

## Performance Benchmarks

### Crawling Performance

| Operation | Small Scale | Medium Scale | Large Scale | Notes |
|-----------|-------------|--------------|-------------|-------|
| Single page crawl | 2-3s | 2-3s | 2-3s | Network dependent |
| Sitemap (100 URLs) | 5-8 min | 3-5 min | 2-3 min | Parallel processing |
| GraphRAG extraction | 4-6s/page | 4-6s/page | 4-6s/page | LLM API dependent |
| Repository parsing | 2-5 min | 1-3 min | <1 min | Repo size dependent |

### RAG Query Performance

| Query Type | Vector Only | + Hybrid | + Reranking | + Graph |
|-----------|-------------|----------|-------------|---------|
| Simple | 150ms | 200ms | 300ms | 400ms |
| Complex | 150ms | 200ms | 300ms | 600ms |
| Code search | 180ms | 250ms | 350ms | N/A |

### Memory Usage

| Operation | Base | +Context | +Agentic | +GraphRAG |
|-----------|------|----------|----------|-----------|
| Single page | 50MB | 60MB | 80MB | 120MB |
| Sitemap (100) | 200MB | 300MB | 500MB | 800MB |
| Repository | 150MB | N/A | N/A | 200MB |

---

## Monitoring and Observability

### Health Checks

Implement health check endpoint:

```python
# Available at /health when using SSE transport
curl http://localhost:8051/health

# Response:
{
    "status": "healthy",
    "version": "1.3.0",
    "transport": "sse",
    "components": {
        "supabase": "connected",
        "neo4j": "connected",
        "openai": "authenticated"
    }
}
```

### Logging Best Practices

Configure structured logging:

```python
import logging
import json

# Structured logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log with context
logger.info("Crawl started", extra={
    "url": url,
    "concurrent_requests": 10,
    "memory_threshold_mb": 500
})
```

### Metrics to Track

Key metrics for production monitoring:

| Metric | Description | Alert Threshold |
|--------|-------------|----------------|
| Crawl success rate | % of successful crawls | <90% |
| Average crawl time | Time per page | >10s |
| Memory usage | Peak memory consumption | >80% limit |
| API error rate | % of API failures | >5% |
| Graph query latency | Neo4j query time | >2s |
| Vector search latency | Supabase query time | >1s |

### Example Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
crawl_requests = Counter('crawl_requests_total', 'Total crawl requests')
crawl_duration = Histogram('crawl_duration_seconds', 'Crawl duration')
memory_usage = Gauge('memory_usage_mb', 'Current memory usage')

# Use in code
@crawl_duration.time()
def crawl_with_metrics(url):
    crawl_requests.inc()
    result = crawl_single_page(url)
    memory_usage.set(psutil.Process().memory_info().rss / 1024 / 1024)
    return result
```

---

## Cost Optimization

### Cost Breakdown

Estimated monthly costs at different scales:

| Component | Small | Medium | Large | Enterprise |
|-----------|-------|--------|-------|------------|
| **Supabase** | Free | $25 | $599 | $2,499 |
| **Neo4j** | Free (local) | $65 (AuraDB) | $200 | $1,000+ |
| **OpenAI API** | $5-10 | $50-100 | $500-1,000 | $5,000+ |
| **Hosting** | $0 (local) | $20 (Docker) | $200 (K8s) | $1,000+ |
| **Total** | $5-10 | $160-210 | $1,499-1,999 | $9,499+ |

### Cost Optimization Strategies

#### 1. Use Cheaper Embedding Models

```python
# Expensive: text-embedding-3-large (3072 dimensions)
# Cost: $0.13 per 1M tokens

# Cheaper: text-embedding-3-small (1536 dimensions)
# Cost: $0.02 per 1M tokens
# Use: For most use cases
```

#### 2. Reduce Entity Extraction Calls

```python
# Expensive: Extract from all chunks
crawl_with_graph_extraction(url)

# Cheaper: Limit chunks processed
# Modify in code to process only first 10 chunks
# Reduces API costs by 50-80%
```

#### 3. Cache Embeddings

Store embeddings locally to avoid re-generating:

```python
import hashlib
import json

embedding_cache = {}

def get_cached_embedding(text):
    """Get embedding with caching."""
    cache_key = hashlib.md5(text.encode()).hexdigest()

    if cache_key in embedding_cache:
        return embedding_cache[cache_key]

    embedding = create_embedding(text)
    embedding_cache[cache_key] = embedding
    return embedding
```

#### 4. Use Batch Operations

Batch operations reduce API overhead:

```python
# Expensive: Individual embeddings
embeddings = [create_embedding(text) for text in texts]

# Cheaper: Batch embeddings
embeddings = create_embeddings_batch(texts)  # Uses existing batch function
```

---

## Troubleshooting at Scale

### Common issues

#### 1. Memory Exhaustion

**Symptom**: Out of memory errors, process killed

**Solutions**:
- Reduce `max_concurrent` parameter
- Lower `chunk_size` setting
- Use `crawl_with_memory_monitoring`
- Increase server memory allocation
- Process in smaller batches

#### 2. API Rate Limiting

**Symptom**: 429 errors, API timeouts

**Solutions**:
- Implement rate limiting (see Rate Limiting section)
- Add delays between requests
- Upgrade OpenAI tier
- Reduce `max_concurrent` for GraphRAG
- Use batch processing with delays

#### 3. Database Connection Pool Exhausted

**Symptom**: "Too many connections" errors

**Solutions**:
```python
# Increase connection pool size
# For Supabase
options={"db": {"pool": {"max": 20}}}

# For Neo4j
max_connection_pool_size=50
```

#### 4. Slow Graph Queries

**Symptom**: Neo4j queries taking >5s

**Solutions**:
- Add indexes (see Database Optimization)
- Optimize Cypher queries
- Use `LIMIT` clauses
- Consider query caching
- Increase Neo4j heap size

#### 5. Disk Space Exhaustion

**Symptom**: "No space left on device"

**Solutions**:
- Clean up old crawl data
- Implement data retention policies
- Use external storage (S3)
- Increase disk allocation
- Compress old data

### Performance Debugging

Enable debug logging to identify bottlenecks:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add timing decorators
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logging.debug(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@timing_decorator
def crawl_single_page(url):
    # ... existing code
```

---

## Production Checklist

Before deploying to production:

### Infrastructure
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented

### Configuration
- [ ] Environment variables secured
- [ ] API keys rotated
- [ ] Rate limits configured
- [ ] Memory limits set
- [ ] Connection pools tuned

### Monitoring
- [ ] Health checks enabled
- [ ] Metrics collection configured
- [ ] Alerting rules defined
- [ ] Log aggregation setup
- [ ] Dashboard created

### Optimization
- [ ] Database indexes created
- [ ] Caching implemented
- [ ] Batch operations verified
- [ ] Connection pooling enabled
- [ ] Resource limits tested

### Documentation
- [ ] Deployment runbook created
- [ ] Troubleshooting guide updated
- [ ] Scaling procedures documented
- [ ] On-call procedures defined
- [ ] Team trained

---

## Next Steps

1. **Start Small**: Begin with small-scale deployment
2. **Monitor**: Track key metrics for 1-2 weeks
3. **Optimize**: Identify and fix bottlenecks
4. **Scale Gradually**: Increase load incrementally
5. **Automate**: Implement auto-scaling where possible

## Support

For production support:
- GitHub Issues: [mcp-crawl4ai-rag/issues](https://github.com/coleam00/mcp-crawl4ai-rag/issues)
- Documentation: [docs/README.md](/mnt/e/Repos/GitHub/mcp-crawl4ai-rag/docs/README.md)
- Troubleshooting: [TROUBLESHOOTING.md](/mnt/e/Repos/GitHub/mcp-crawl4ai-rag/TROUBLESHOOTING.md)

---

**Version**: 1.3.0
**Last Updated**: 2025-10-07
**Maintainers**: MCP Crawl4AI RAG Team
