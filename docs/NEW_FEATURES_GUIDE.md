# New Features Guide - Crawl4AI MCP Server

## Overview

This guide covers the three powerful new features added to the Crawl4AI MCP server in the latest update. These features leverage Crawl4AI v0.7.4 capabilities to provide advanced crawling for challenging scenarios.

## Table of Contents

1. [Stealth Mode Crawling](#stealth-mode-crawling)
2. [Smart Multi-URL Configuration](#smart-multi-url-configuration)
3. [Memory-Monitored Crawling](#memory-monitored-crawling)
4. [Enhanced Table Extraction](#enhanced-table-extraction)
5. [Adaptive Deep Crawling](#adaptive-deep-crawling)
6. [Migration from Standard Tools](#migration-from-standard-tools)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Stealth Mode Crawling

### What is it?

Stealth mode uses **undetected browser technology** to bypass bot detection systems like Cloudflare, Akamai, PerimeterX, and other anti-scraping measures. It makes your crawler appear as a regular human user.

### When to Use

- ✅ Sites with Cloudflare protection
- ✅ Sites that block headless browsers
- ✅ Content behind aggressive anti-scraping measures
- ✅ Sites with bot detection (Akamai, PerimeterX, etc.)
- ❌ Public APIs or documentation sites (use regular `smart_crawl_url` instead)

### Tool: `crawl_with_stealth_mode`

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to crawl (webpage, sitemap.xml, or .txt file) |
| `max_depth` | int | 3 | Maximum recursion depth for internal links |
| `max_concurrent` | int | 10 | Maximum concurrent browser sessions |
| `chunk_size` | int | 5000 | Size of each content chunk in characters |
| `wait_for_selector` | string | "" | Optional CSS selector to wait for before extraction |
| `extra_wait` | int | 2 | Additional wait time in seconds after page load |

#### Example Usage

```python
# Basic stealth crawling
result = await crawl_with_stealth_mode(
    url="https://protected-site.com",
    max_depth=2,
    extra_wait=3
)

# Wait for specific content to load
result = await crawl_with_stealth_mode(
    url="https://protected-site.com/pricing",
    wait_for_selector="div.pricing-table",
    extra_wait=5
)

# Crawl Cloudflare-protected sitemap
result = await crawl_with_stealth_mode(
    url="https://protected-site.com/sitemap.xml",
    max_concurrent=5
)
```

#### Response Format

```json
{
  "success": true,
  "crawl_type": "stealth_webpage",
  "url": "https://example.com",
  "mode": "stealth (undetected browser)",
  "pages_crawled": 25,
  "total_chunks": 187
}
```

#### How It Works

1. **Undetected Browser**: Uses `browser_type="undetected"` to bypass detection
2. **Human Simulation**: Enables `simulate_user=True` for realistic behavior
3. **Navigator Override**: Sets `override_navigator=True` to hide automation
4. **Extra Args**: Disables automation features with `--disable-blink-features`

#### Best Practices

1. **Respect robots.txt**: Even with stealth mode, follow site policies
2. **Rate Limiting**: Use `max_concurrent` wisely (3-5 for protected sites)
3. **Extra Wait**: Increase `extra_wait` for JavaScript-heavy sites (3-5 seconds)
4. **Selectors**: Use `wait_for_selector` for dynamically loaded content

---

## Smart Multi-URL Configuration

### What is it?

Automatically optimizes crawler settings based on URL patterns and content types. Different strategies for documentation, news, e-commerce, and forums.

### When to Use

- ✅ Crawling multiple domains with different content types
- ✅ Building comprehensive knowledge bases
- ✅ Aggregating content from diverse sources
- ✅ Batch processing with optimized settings per site
- ❌ Single-domain crawling (use regular tools instead)

### Tool: `crawl_with_multi_url_config`

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `urls_json` | string | required | JSON array of URLs to crawl |
| `max_concurrent` | int | 5 | Maximum concurrent browser sessions |
| `chunk_size` | int | 5000 | Size of each content chunk in characters |

#### Content Type Detection

The tool automatically detects content type from URL patterns:

| Content Type | URL Patterns | Optimizations |
|--------------|--------------|---------------|
| **Documentation** | `docs`, `documentation`, `api`, `reference` | Wait for code blocks, target main content |
| **Articles** | `news`, `article`, `blog`, `post` | Focus on article body, higher word threshold |
| **General** | Everything else | Standard settings |

#### Example Usage

```python
# Crawl multiple documentation sites
urls = '[
    "https://docs.python.org",
    "https://fastapi.tiangolo.com",
    "https://docs.djangoproject.com"
]'

result = await crawl_with_multi_url_config(
    urls_json=urls,
    max_concurrent=3,
    chunk_size=5000
)

# Mix of content types
urls = '[
    "https://docs.example.com",
    "https://blog.example.com",
    "https://news.example.com"
]'

result = await crawl_with_multi_url_config(urls_json=urls)
```

#### Response Format

```json
{
  "success": true,
  "urls_processed": 3,
  "total_chunks": 542,
  "results": [
    {
      "url": "https://docs.python.org",
      "content_type": "documentation",
      "success": true,
      "pages_crawled": 45,
      "chunks_stored": 312
    },
    {
      "url": "https://blog.example.com",
      "content_type": "article",
      "success": true,
      "pages_crawled": 12,
      "chunks_stored": 89
    }
  ]
}
```

#### Content-Specific Configurations

**Documentation Sites**:
```python
CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    word_count_threshold=50,  # Lower threshold for code snippets
    css_selector="article, main, .content, .documentation"
)
```

**News/Articles**:
```python
CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    word_count_threshold=100,  # Higher threshold for prose
    css_selector="article, main, .post-content, .article-body"
)
```

#### Best Practices

1. **Group by Type**: Batch similar content types together
2. **Concurrency**: Use lower `max_concurrent` (3-5) for mixed types
3. **URL Array**: Keep arrays under 10 URLs per call
4. **Chunk Size**: Use larger chunks (5000-8000) for documentation

---

## Memory-Monitored Crawling

### What is it?

Monitors memory usage during crawling and automatically throttles concurrency to prevent memory exhaustion. Essential for large-scale operations.

### When to Use

- ✅ Large documentation sites (1000+ pages)
- ✅ Sites with heavy media content
- ✅ Long-running crawl operations (hours)
- ✅ Resource-constrained environments
- ✅ Production deployments
- ❌ Small sites (<100 pages)

### Tool: `crawl_with_memory_monitoring`

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to crawl (webpage, sitemap, or .txt file) |
| `max_depth` | int | 3 | Maximum recursion depth |
| `max_concurrent` | int | 10 | Initial concurrent sessions (auto-adjusted) |
| `chunk_size` | int | 5000 | Chunk size in characters |
| `memory_threshold_mb` | int | 500 | Memory limit before throttling (MB) |

#### Example Usage

```python
# Basic memory monitoring
result = await crawl_with_memory_monitoring(
    url="https://docs.example.com/sitemap.xml",
    memory_threshold_mb=300
)

# Large documentation site
result = await crawl_with_memory_monitoring(
    url="https://docs.example.com",
    max_depth=4,
    max_concurrent=15,
    memory_threshold_mb=500
)

# Resource-constrained environment
result = await crawl_with_memory_monitoring(
    url="https://heavy-media-site.com",
    max_concurrent=5,
    memory_threshold_mb=200  # Lower threshold
)
```

#### Response Format

```json
{
  "success": true,
  "crawl_type": "memory_monitored_sitemap",
  "url": "https://example.com/sitemap.xml",
  "pages_crawled": 1247,
  "total_chunks": 8934,
  "memory_stats": {
    "start_mb": 156.32,
    "end_mb": 423.18,
    "peak_mb": 487.91,
    "delta_mb": 266.86,
    "avg_mb": 342.45,
    "threshold_mb": 500,
    "elapsed_seconds": 1834.23
  }
}
```

#### How It Works

1. **Baseline Measurement**: Records memory at start
2. **Batch Processing**: For sitemaps, processes URLs in batches
3. **Adaptive Throttling**: Reduces `max_concurrent` by 50% when threshold exceeded
4. **Continuous Monitoring**: Samples memory before each batch
5. **Statistics Collection**: Tracks peak, average, and delta

#### Memory Statistics Explained

| Stat | Description |
|------|-------------|
| `start_mb` | Memory usage at crawl start |
| `end_mb` | Memory usage at crawl completion |
| `peak_mb` | Highest memory usage during crawl |
| `delta_mb` | Total memory increase (end - start) |
| `avg_mb` | Average memory across all samples |
| `threshold_mb` | Configured memory limit |
| `elapsed_seconds` | Total crawl time |

#### Best Practices

1. **Set Thresholds**: Use 60-70% of available RAM
2. **Monitor First**: Run once with monitoring to establish baseline
3. **Batch Size**: Sitemaps processed in batches of `max_concurrent`
4. **Production Use**: Always enable for production crawls
5. **Adjust Concurrency**: Start high, let system auto-throttle

#### Troubleshooting

**High Memory Delta**:
- Reduce `max_concurrent` to 3-5
- Decrease `chunk_size` to 3000-4000
- Lower `memory_threshold_mb`

**Slow Performance**:
- Increase `memory_threshold_mb` if you have RAM
- Reduce `max_depth` for recursive crawls
- Use sitemap crawling instead of recursive

**Out of Memory Errors**:
- Set `memory_threshold_mb` to 50% of available RAM
- Use batch processing (manual URL lists)
- Increase chunk size to reduce object count

---

## Comparison Matrix

| Feature | Best For | Concurrency | Memory | Speed |
|---------|----------|-------------|---------|-------|
| **Stealth Mode** | Protected sites | Low (3-5) | Medium | Slow |
| **Multi-URL Config** | Diverse sources | Medium (5-10) | Medium | Medium |
| **Memory Monitoring** | Large-scale ops | Adaptive | Low | Fast |
| **Standard (`smart_crawl_url`)** | General use | High (10-20) | Medium | Fast |

---

## Combining Features

### Example: Large Protected Site

```python
# For a large Cloudflare-protected documentation site
result = await crawl_with_stealth_mode(
    url="https://protected-docs.com/sitemap.xml",
    max_concurrent=3,  # Low for stealth
    chunk_size=4000,   # Smaller chunks for memory
    extra_wait=3
)

# Then monitor memory separately if needed
result = await crawl_with_memory_monitoring(
    url="https://protected-docs.com/sitemap.xml",
    max_concurrent=3,
    memory_threshold_mb=300
)
```

### Example: Multi-Source Knowledge Base

```python
# Crawl documentation from multiple sources
docs_urls = '[
    "https://docs.python.org",
    "https://docs.djangoproject.com",
    "https://fastapi.tiangolo.com"
]'

result = await crawl_with_multi_url_config(
    urls_json=docs_urls,
    max_concurrent=5,
    chunk_size=6000
)
```

---

## Requirements

### Dependencies

All features require:
- `crawl4ai>=0.7.4`
- `fastmcp>=2.12.4`

Memory monitoring additionally requires:
- `psutil>=5.9.0` (auto-installed with package)

### Installation

```bash
# Install/upgrade to latest
uv pip install --upgrade crawl4ai fastmcp psutil

# Or using pip
pip install --upgrade crawl4ai fastmcp psutil
```

---

## Performance Tips

### General

1. **Start Conservative**: Begin with lower concurrency, increase gradually
2. **Use Sitemaps**: Faster and more reliable than recursive crawling
3. **Chunk Appropriately**: 
   - Code/docs: 4000-6000 characters
   - Articles: 5000-8000 characters
   - General: 5000 characters

### Stealth Mode

1. **Reduce Concurrency**: Use 3-5 max (sites detect high concurrency)
2. **Add Delays**: Use `extra_wait=3-5` for JavaScript-heavy sites
3. **Wait for Elements**: Use `wait_for_selector` for dynamic content
4. **Batch Operations**: Process in smaller batches with delays

### Multi-URL Config

1. **Group Similar**: Batch same content types together
2. **Stagger Crawls**: Don't overwhelm servers
3. **Monitor First**: Test one URL before batch processing

### Memory Monitoring

1. **Baseline First**: Run once to see memory patterns
2. **Set Conservative Thresholds**: Use 60-70% of available RAM
3. **Watch Peak**: If peak hits threshold, reduce concurrency
4. **Long Operations**: Essential for any crawl >30 minutes

---

## Troubleshooting

### Stealth Mode Not Working

**Symptoms**: Still getting blocked by Cloudflare

**Solutions**:
1. Increase `extra_wait` to 5-10 seconds
2. Reduce `max_concurrent` to 1-2
3. Add delays between requests
4. Check if site requires cookies/sessions

### Multi-URL Config Failing

**Symptoms**: Some URLs succeed, others fail

**Solutions**:
1. Check URL format (must be valid JSON array)
2. Verify all URLs are accessible
3. Reduce `max_concurrent` to 3
4. Process URLs individually first to identify issues

### Memory Monitoring Throttling Too Much

**Symptoms**: Very slow crawls, low concurrency

**Solutions**:
1. Increase `memory_threshold_mb`
2. Close other applications
3. Use larger `chunk_size` (reduces object count)
4. Check for memory leaks in other processes

---

## Migration Guide

### From `smart_crawl_url` to Stealth Mode

```python
# Before
result = await smart_crawl_url(
    url="https://protected-site.com",
    max_depth=2
)

# After - Add stealth for protected sites
result = await crawl_with_stealth_mode(
    url="https://protected-site.com",
    max_depth=2,
    extra_wait=3
)
```

### From Multiple Calls to Multi-URL Config

```python
# Before - Multiple individual calls
for url in urls:
    result = await smart_crawl_url(url=url)

# After - Single optimized call
urls_json = json.dumps(urls)
result = await crawl_with_multi_url_config(
    urls_json=urls_json,
    max_concurrent=5
)
```

### Adding Memory Monitoring

```python
# Before - No monitoring
result = await smart_crawl_url(
    url="https://large-site.com/sitemap.xml",
    max_concurrent=10
)

# After - With monitoring
result = await crawl_with_memory_monitoring(
    url="https://large-site.com/sitemap.xml",
    max_concurrent=10,
    memory_threshold_mb=400
)
```

---

## FAQ

### Q: Which tool should I use for regular websites?

**A:** Use the standard `smart_crawl_url`. The new tools are for special scenarios:
- **Stealth**: Protected/blocked sites
- **Multi-URL**: Batch processing diverse sources
- **Memory Monitoring**: Large-scale operations

### Q: Can I combine these features?

**A:** Not directly in one call. Use stealth mode if needed, then monitor memory in production. Multi-URL is separate for batch operations.

### Q: How much memory should I allocate?

**A:** Set `memory_threshold_mb` to 60-70% of available RAM. For a 4GB system, use 300-400MB. For 8GB, use 500-700MB.

### Q: Does stealth mode work on all sites?

**A:** Most sites, yes. Very sophisticated detection may still catch it. Try increasing `extra_wait` and reducing `max_concurrent`.

### Q: Is stealth mode slower?

**A:** Yes, typically 2-3x slower than regular crawling. It's the trade-off for bypassing protection.

### Q: Can I use these in Claude Desktop?

**A:** Yes! All tools are available as MCP tools in Claude Desktop. Just call them naturally in your conversation.

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Verify environment variables in `.env`
3. Test with a simple URL first
4. Review error messages carefully

Common log locations:
- MCP Server: `logs/mcp_server.log`
- Crawl4AI: `logs/crawl4ai.log`
- Memory: Check `memory_stats` in response

---

## Changelog

### v1.1.0 - October 2025

**New Features**:
- ✨ Stealth mode crawling with undetected browser
- ✨ Smart multi-URL configuration
- ✨ Memory-monitored crawling with adaptive throttling

**Dependencies**:
- ⬆️ Crawl4AI 0.7.4 (from 0.7.0)
- ⬆️ FastMCP 2.12.4 (from 2.0.0)
- ➕ psutil 5.9.0+ (new requirement)

**Improvements**:
- 🚀 5 new MCP tools for advanced use cases
- 📊 Memory monitoring and statistics
- 🛡️ Bot detection bypass capabilities
- ⚡ Optimized per-content-type configurations
- 📋 Enhanced table extraction for structured data
- 🎯 Adaptive crawling with query relevance

---

## Enhanced Table Extraction

### What is it?

Enhanced table extraction automatically detects and extracts structured tabular data from web pages while preserving table structure. Ideal for scraping pricing tables, statistical data, comparison charts, and database-like information.

### When to Use

- ✅ Pricing pages and product comparisons
- ✅ Statistical reports and data tables
- ✅ Financial data and spreadsheets
- ✅ Database exports or structured content
- ❌ Unstructured text content (use regular crawl instead)

### Tool: `crawl_with_table_extraction`

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to crawl (webpage, sitemap.xml, or .txt file) |
| `max_depth` | int | 3 | Maximum recursion depth for internal links |
| `max_concurrent` | int | 10 | Maximum concurrent browser sessions |
| `chunk_size` | int | 5000 | Size of each content chunk in characters |
| `table_score_threshold` | int | 5 | Minimum score (1-10) for table extraction |

#### Example Usage

```python
# Extract pricing tables
result = await crawl_with_table_extraction(
    url="https://example.com/pricing",
    table_score_threshold=7
)

# Crawl multiple pages with tables
result = await crawl_with_table_extraction(
    url="https://example.com/sitemap.xml",
    max_concurrent=10,
    table_score_threshold=6
)

# Extract data tables from reports
result = await crawl_with_table_extraction(
    url="https://stats.example.com/annual-report",
    table_score_threshold=8
)
```

#### Response Format

```json
{
  "success": true,
  "summary": {
    "url": "https://example.com/pricing",
    "crawl_type": "webpage",
    "pages_crawled": 5,
    "total_chunks": 42,
    "tables_extracted": 3,
    "table_score_threshold": 7,
    "sources_updated": 2
  },
  "tables": [
    {
      "url": "https://example.com/pricing",
      "table": {
        "headers": ["Plan", "Price", "Features"],
        "rows": [...]
      }
    }
  ]
}
```

#### How It Works

1. **Table Detection**: Automatically identifies tables in HTML using scoring algorithm
2. **Structure Preservation**: Maintains table headers, rows, and cell relationships
3. **Quality Filtering**: Only extracts tables above the threshold score
4. **Metadata Enrichment**: Adds table metadata to chunk information

#### Best Practices

1. **Threshold Selection**: 
   - 5-6: General tables (may include lists)
   - 7-8: Well-structured tables only
   - 9-10: Complex data tables with clear structure
2. **URL Patterns**: Works best on pages known to contain tables
3. **Chunk Size**: Consider larger chunks (6000-8000) for tables
4. **Post-Processing**: Tables are stored in metadata for further analysis

---

## Adaptive Deep Crawling

### What is it?

Adaptive deep crawling uses **information foraging algorithms** to intelligently explore websites based on query relevance. It prioritizes pages likely to contain information matching your query and stops when sufficient relevant content is found.

### When to Use

- ✅ Research on large documentation sites
- ✅ Finding specific information without crawling entire sites
- ✅ Query-focused exploration of unknown websites
- ✅ Resource-constrained scenarios (time/memory limits)
- ❌ Complete site archival (use regular crawl instead)

### Tool: `adaptive_deep_crawl`

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | Starting URL for the crawl |
| `query` | string | required | Search query to guide the crawl |
| `max_depth` | int | 5 | Maximum link depth to explore |
| `max_pages` | int | 50 | Maximum number of pages to crawl |
| `relevance_threshold` | float | 0.3 | Minimum relevance score (0-1) to continue |
| `chunk_size` | int | 5000 | Size of each content chunk in characters |
| `strategy` | string | "best_first" | Crawl strategy: "best_first", "bfs", or "dfs" |

#### Example Usage

```python
# Find authentication documentation
result = await adaptive_deep_crawl(
    url="https://docs.example.com",
    query="OAuth2 authentication flow",
    max_pages=30,
    relevance_threshold=0.4
)

# Research API endpoints
result = await adaptive_deep_crawl(
    url="https://api-docs.example.com",
    query="REST API endpoints CRUD operations",
    max_depth=6,
    strategy="best_first"
)

# Deep search with BFS strategy
result = await adaptive_deep_crawl(
    url="https://knowledge.example.com",
    query="machine learning deployment",
    max_pages=100,
    relevance_threshold=0.5,
    strategy="bfs"
)
```

#### Response Format

```json
{
  "success": true,
  "summary": {
    "url": "https://docs.example.com",
    "query": "OAuth2 authentication flow",
    "strategy": "best_first",
    "pages_crawled": 18,
    "total_chunks": 124,
    "max_depth": 5,
    "max_pages": 30,
    "avg_relevance": 0.623,
    "sources_updated": 6
  },
  "top_relevant_sources": [
    {"source": "docs.example.com", "relevance": 0.857},
    {"source": "api.example.com", "relevance": 0.721},
    {"source": "guides.example.com", "relevance": 0.634}
  ]
}
```

#### Crawl Strategies

1. **best_first** (Recommended)
   - Prioritizes most relevant pages first
   - Best for targeted information gathering
   - May skip less relevant branches

2. **bfs** (Breadth-First Search)
   - Explores all pages at current depth before going deeper
   - Good for comprehensive coverage
   - Respects relevance threshold

3. **dfs** (Depth-First Search)
   - Follows links deeply before backtracking
   - Good for exploring specific paths
   - Respects relevance threshold

#### How It Works

1. **URL Scoring**: Analyzes URLs and link text for query keywords
2. **Priority Queue**: Maintains queue of URLs sorted by relevance
3. **Adaptive Selection**: Chooses next URL based on strategy and score
4. **Relevance Calculation**: Scores chunks based on keyword matches
5. **Early Stopping**: Stops when:
   - Max pages reached
   - Max depth reached
   - No more URLs above threshold

#### Best Practices

1. **Query Formulation**: Use specific keywords (3-5 words work best)
2. **Threshold Selection**:
   - 0.2-0.3: Broad exploration
   - 0.4-0.5: Balanced (recommended)
   - 0.6+: Very focused, may miss context
3. **Max Pages**: Start with 30-50, adjust based on results
4. **Strategy Selection**:
   - Use "best_first" for most cases
   - Use "bfs" for comprehensive coverage
   - Use "dfs" for exploring specific paths
5. **Post-Analysis**: Use returned relevance scores to identify best sources

#### Performance Tips

- **Initial URL**: Start at a high-level index or homepage
- **Query Refinement**: Adjust query if relevance scores are low
- **Incremental Crawling**: Start with low max_pages, increase if needed
- **Combine with RAG**: Use results as context for follow-up queries

---

## Migration from Standard Tools

### From `smart_crawl_url` to New Tools

#### When to Migrate

- **To stealth mode**: Site blocks regular crawlers
- **To table extraction**: Need structured data from tables
- **To adaptive crawl**: Want query-focused exploration

#### Migration Examples

```python
# Before: Regular crawl
smart_crawl_url("https://site.com")

# After: If site is protected
crawl_with_stealth_mode("https://site.com")

# After: If page has tables
crawl_with_table_extraction("https://site.com/pricing")

# After: If searching for specific info
adaptive_deep_crawl("https://site.com", query="API documentation")
```

### Combining Multiple Tools

```python
# 1. Try regular crawl first
result1 = smart_crawl_url("https://site.com")

# 2. If blocked, use stealth mode
if not result1["success"]:
    result2 = crawl_with_stealth_mode("https://site.com")

# 3. For specific queries, use adaptive crawl
result3 = adaptive_deep_crawl(
    "https://site.com",
    query="pricing and features"
)

# 4. Extract tables from pricing page
result4 = crawl_with_table_extraction(
    "https://site.com/pricing",
    table_score_threshold=7
)
```

---

## Troubleshooting

### Enhanced Table Extraction

**Issue**: No tables extracted
- **Solution**: Lower `table_score_threshold` (try 4-5)
- **Check**: Ensure page actually contains HTML tables

**Issue**: Too many false positives
- **Solution**: Increase `table_score_threshold` (try 7-8)
- **Check**: Inspect returned tables to tune threshold

### Adaptive Deep Crawl

**Issue**: Low relevance scores
- **Solution**: Refine query with more specific keywords
- **Check**: Verify starting URL is relevant to query

**Issue**: Crawling too many/few pages
- **Solution**: Adjust `relevance_threshold` and `max_pages`
- **Check**: Review top_relevant_sources for guidance

**Issue**: Wrong pages being crawled
- **Solution**: Try different strategy (switch to "best_first")
- **Check**: Ensure query keywords match target content

---

## FAQ

### General

**Q: How many tools are now available?**
A: 18 total tools (16 existing + 2 new: table extraction & adaptive crawl)

**Q: Do new tools work with all URL types?**
A: Yes, all support regular URLs, sitemaps, and text files

**Q: Are there any new dependencies?**
A: No new dependencies required (uses existing Crawl4AI features)

### Enhanced Table Extraction

**Q: What table formats are supported?**
A: HTML tables with proper `<table>`, `<tr>`, `<td>` structure

**Q: Can I extract tables from PDFs?**
A: No, only HTML tables. For PDFs, extract text first then process

**Q: How do I access extracted tables?**
A: Tables are in the response JSON and stored in chunk metadata

### Adaptive Deep Crawl

**Q: How is relevance calculated?**
A: Keyword matching in URL, link text, and page content

**Q: Can I use multiple queries?**
A: Use a single comprehensive query with all important keywords

**Q: Does it work with JavaScript sites?**
A: Yes, but ensure JavaScript is rendered (works by default)

---

## Updates

**Version 1.2.0** (Current)
- ➕ Enhanced Table Extraction tool
- ➕ Adaptive Deep Crawling tool
- 📊 Query-based relevance scoring
- 📋 Structured data extraction

**Version 1.1.0**
- ➕ Stealth Mode Crawling
- ➕ Smart Multi-URL Configuration
- ➕ Memory-Monitored Crawling

---

## Dependencies

**Requirements**:
- ⬆️ Crawl4AI 0.7.4 (from 0.7.0)
- ⬆️ FastMCP 2.12.4 (from 2.0.0)
- ➕ psutil 5.9.0+ (for memory monitoring)

**Improvements**:
- 🚀 5 new MCP tools for advanced use cases
- 📊 Memory monitoring and statistics
- 🛡️ Bot detection bypass capabilities
- ⚡ Optimized per-content-type configurations
- 📋 Enhanced table extraction for structured data
- 🎯 Adaptive crawling with query relevance

---

## License

Same as main project (see LICENSE file).
