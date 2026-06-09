# Crawling Strategies Guide

Quick reference for using the crawling strategies and utilities modules.

## Table of contents

1. [Quick Start](#quick-start)
2. [Strategy Pattern Usage](#strategy-pattern-usage)
3. [Utility Functions Reference](#utility-functions-reference)
4. [Adding Custom Strategies](#adding-custom-strategies)
5. [Testing Guide](#testing-guide)

---

## Quick start

### Basic Usage with Factory

```python
from crawl4ai import AsyncWebCrawler
from crawling_strategies import CrawlingStrategyFactory

# Automatic strategy selection
async def crawl_url(url: str):
    async with AsyncWebCrawler() as crawler:
        # Factory selects the right strategy based on URL
        strategy = CrawlingStrategyFactory.get_strategy(url)

        # Execute crawl
        result = await strategy.crawl(
            crawler=crawler,
            url=url,
            max_depth=3,
            max_concurrent=10
        )

        # Handle result
        if result.success:
            print(f"Crawled {result.pages_crawled} pages")
            for doc in result.documents:
                print(f"- {doc['url']}")
        else:
            print(f"Error: {result.error_message}")
```

### URL Type Detection

```python
from crawling_utils import detect_url_type, is_sitemap, is_txt

# Detect URL type
url_type = detect_url_type("https://example.com/sitemap.xml")
# Returns: "sitemap", "text_file", or "webpage"

# Specific checks
if is_sitemap(url):
    print("This is a sitemap")
elif is_txt(url):
    print("This is a text file")
else:
    print("This is a regular webpage")
```

---

## Strategy Pattern Usage

### Available Strategies

#### 1. SitemapCrawlingStrategy

Handles XML sitemaps by parsing URLs and crawling in parallel.

```python
from crawling_strategies import SitemapCrawlingStrategy

strategy = SitemapCrawlingStrategy()

# Check if it can handle a URL
can_handle = strategy.detect("https://example.com/sitemap.xml")  # True

# Crawl
result = await strategy.crawl(
    crawler=crawler,
    url="https://example.com/sitemap.xml",
    max_concurrent=20  # Parallel crawl limit
)

print(f"Found {result.metadata['urls_found']} URLs in sitemap")
print(f"Successfully crawled {result.pages_crawled} pages")
```

#### 2. TextFileCrawlingStrategy

Handles plain text files (.txt) without following links.

```python
from crawling_strategies import TextFileCrawlingStrategy

strategy = TextFileCrawlingStrategy()

# Check if it can handle a URL
can_handle = strategy.detect("https://example.com/llms.txt")  # True

# Crawl
result = await strategy.crawl(
    crawler=crawler,
    url="https://example.com/llms.txt"
)

if result.success:
    content = result.documents[0]['markdown']
    print(f"Retrieved {len(content)} characters")
```

#### 3. RecursiveCrawlingStrategy

Recursively crawls internal links up to a specified depth (default strategy).

```python
from crawling_strategies import RecursiveCrawlingStrategy

strategy = RecursiveCrawlingStrategy()

# Always returns True (fallback strategy)
can_handle = strategy.detect("https://example.com/")  # True

# Crawl with depth control
result = await strategy.crawl(
    crawler=crawler,
    url="https://example.com/",
    max_depth=2,        # Only go 2 levels deep
    max_concurrent=10   # Parallel crawl limit
)

print(f"Crawled {result.pages_crawled} pages across {result.metadata['max_depth']} levels")
```

### Understanding CrawlResult

All strategies return a `CrawlResult` object:

```python
@dataclass
class CrawlResult:
    success: bool                      # True if crawl succeeded
    url: str                          # The URL that was crawled
    pages_crawled: int                # Number of pages successfully crawled
    documents: List[Dict[str, Any]]   # List of {url, markdown} dicts
    error_message: Optional[str]      # Error message if failed
    metadata: Optional[Dict[str, Any]] # Strategy-specific metadata

# Example usage
result = await strategy.crawl(crawler, url)

if result.success:
    for doc in result.documents:
        print(f"URL: {doc['url']}")
        print(f"Content: {doc['markdown'][:100]}...")
else:
    print(f"Crawl failed: {result.error_message}")
```

### Factory Pattern

The factory automatically selects the best strategy:

```python
from crawling_strategies import CrawlingStrategyFactory

# Priority order (most specific first):
# 1. SitemapCrawlingStrategy (if URL is sitemap)
# 2. TextFileCrawlingStrategy (if URL ends with .txt)
# 3. RecursiveCrawlingStrategy (fallback - always matches)

strategy = CrawlingStrategyFactory.get_strategy(url)

# Get all registered strategies
all_strategies = CrawlingStrategyFactory.get_all_strategies()
for strategy_class in all_strategies:
    print(strategy_class.__name__)
```

---

## Utility Functions Reference

### URL Detection

```python
from crawling_utils import is_sitemap, is_txt, detect_url_type

# Check if URL is a sitemap
is_sitemap("https://example.com/sitemap.xml")      # True
is_sitemap("https://example.com/news-sitemap.xml") # True

# Check if URL is a text file
is_txt("https://example.com/llms.txt")    # True
is_txt("https://example.com/README.txt")  # True

# Detect URL type (returns "sitemap", "text_file", or "webpage")
detect_url_type("https://example.com/sitemap.xml")  # "sitemap"
detect_url_type("https://example.com/llms.txt")     # "text_file"
detect_url_type("https://example.com/page.html")    # "webpage"
```

### Sitemap Parsing

```python
from crawling_utils import parse_sitemap

# Parse sitemap and extract URLs
urls = parse_sitemap("https://example.com/sitemap.xml")

# Returns empty list on errors (graceful degradation)
# Handles: HTTP errors, malformed XML, network issues
for url in urls:
    print(f"Found: {url}")
```

### Content Chunking

```python
from crawling_utils import smart_chunk_markdown

# Intelligently chunk text at natural boundaries
text = """
# Documentation

## Section 1
Content here.

```python
def example():
    pass
```

## Section 2
More content.
"""

chunks = smart_chunk_markdown(text, chunk_size=200)

# Respects:
# 1. Code blocks (```) - highest priority
# 2. Paragraph breaks (\n\n)
# 3. Sentence boundaries (. )
# 4. Hard limit at chunk_size

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {len(chunk)} chars")
```

### Metadata Extraction

```python
from crawling_utils import extract_section_info

chunk = """
# Main Title

Some content here with multiple words.

## Subsection
"""

info = extract_section_info(chunk)

# Returns:
# {
#     "headers": "# Main Title; ## Subsection",
#     "char_count": 68,
#     "word_count": 10
# }

print(f"Headers: {info['headers']}")
print(f"Characters: {info['char_count']}")
print(f"Words: {info['word_count']}")
```

### Crawling Operations

```python
from crawling_utils import (
    crawl_markdown_file,
    crawl_batch,
    crawl_recursive_internal_links
)

# Single file crawl
docs = await crawl_markdown_file(crawler, "https://example.com/file.txt")
# Returns: [{"url": "...", "markdown": "..."}]

# Batch crawl (parallel)
urls = ["https://example.com/1", "https://example.com/2"]
docs = await crawl_batch(crawler, urls, max_concurrent=10)
# Returns: [{"url": "...", "markdown": "..."}, ...]

# Recursive crawl
start_urls = ["https://example.com/"]
docs = await crawl_recursive_internal_links(
    crawler,
    start_urls,
    max_depth=3,
    max_concurrent=10
)
# Returns: [{"url": "...", "markdown": "..."}, ...]
```

### Statistics Aggregation

```python
from crawling_utils import aggregate_crawl_stats

documents = [
    {"url": "https://example.com/1", "markdown": "Content 1 here"},
    {"url": "https://example.com/2", "markdown": "Content 2 here"}
]

stats = aggregate_crawl_stats(documents)

# Returns:
# {
#     "total_pages": 2,
#     "total_chars": 30,
#     "total_words": 6,
#     "avg_chars_per_page": 15,
#     "avg_words_per_page": 3,
#     "unique_urls": 2
# }

print(f"Crawled {stats['total_pages']} pages")
print(f"Average {stats['avg_words_per_page']} words per page")
```

---

## Adding Custom Strategies

### Step 1: Implement Strategy Class

```python
from crawling_strategies import CrawlingStrategy, CrawlResult
from crawl4ai import AsyncWebCrawler

class RSSFeedStrategy(CrawlingStrategy):
    """Custom strategy for RSS feeds."""

    async def crawl(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        max_depth: int = 3,
        max_concurrent: int = 10,
        **kwargs
    ) -> CrawlResult:
        """Crawl RSS feed."""
        try:
            # Your custom RSS parsing logic here
            # Example: Parse RSS XML, extract article URLs, crawl them

            articles = await self._parse_rss(url)
            documents = await self._crawl_articles(crawler, articles)

            return CrawlResult(
                success=True,
                url=url,
                pages_crawled=len(documents),
                documents=documents,
                metadata={"strategy": "rss", "article_count": len(articles)}
            )
        except Exception as e:
            return CrawlResult(
                success=False,
                url=url,
                pages_crawled=0,
                documents=[],
                error_message=str(e),
                metadata={"strategy": "rss"}
            )

    @staticmethod
    def detect(url: str) -> bool:
        """Detect RSS feed URLs."""
        return url.endswith(".rss") or url.endswith(".xml") and "feed" in url.lower()

    async def _parse_rss(self, url: str):
        """Parse RSS feed and extract article URLs."""
        # Implementation here
        pass

    async def _crawl_articles(self, crawler, articles):
        """Crawl article URLs from RSS feed."""
        # Implementation here
        pass
```

### Step 2: Register Strategy

```python
from crawling_strategies import CrawlingStrategyFactory

# Register at highest priority (position 0)
CrawlingStrategyFactory.register_strategy(RSSFeedStrategy, position=0)

# Now the factory will use your strategy
strategy = CrawlingStrategyFactory.get_strategy("https://example.com/feed.rss")
# Returns: RSSFeedStrategy instance
```

### Step 3: Use Strategy

```python
# Automatic via factory
result = await CrawlingStrategyFactory.get_strategy(url).crawl(crawler, url)

# Or direct instantiation
rss_strategy = RSSFeedStrategy()
result = await rss_strategy.crawl(crawler, "https://example.com/feed.rss")
```

---

## Testing Guide

### Testing Strategies

```python
import pytest
from unittest.mock import AsyncMock, patch
from crawling_strategies import SitemapCrawlingStrategy

class TestCustomStrategy:
    @pytest.mark.asyncio
    async def test_successful_crawl(self):
        """Test successful crawl operation."""
        mock_crawler = AsyncMock()

        # Mock dependencies
        with patch("crawl4ai_mcp.parse_sitemap", return_value=["https://example.com/1"]):
            with patch("crawl4ai_mcp.crawl_batch", return_value=[{"url": "...", "markdown": "..."}]):
                strategy = SitemapCrawlingStrategy()
                result = await strategy.crawl(mock_crawler, "https://example.com/sitemap.xml")

                assert result.success is True
                assert result.pages_crawled == 1

    def test_url_detection(self):
        """Test URL detection logic."""
        assert SitemapCrawlingStrategy.detect("https://example.com/sitemap.xml") is True
        assert SitemapCrawlingStrategy.detect("https://example.com/page.html") is False
```

### Testing Utilities

```python
import pytest
from crawling_utils import smart_chunk_markdown, extract_section_info

def test_smart_chunking():
    """Test markdown chunking."""
    text = "# Title\n\nContent here.\n\n## Section"
    chunks = smart_chunk_markdown(text, chunk_size=20)

    assert len(chunks) > 0
    assert all(len(chunk) <= 20 for chunk in chunks[:-1])

def test_metadata_extraction():
    """Test section info extraction."""
    chunk = "# Header\n\nContent"
    info = extract_section_info(chunk)

    assert "# Header" in info["headers"]
    assert info["char_count"] > 0
    assert info["word_count"] > 0
```

### Running Tests

```bash
# Run all strategy tests
pytest tests/test_crawling_strategies.py -v

# Run all utility tests
pytest tests/test_crawling_utils.py -v

# Run with coverage
pytest tests/ --cov=src/crawling_strategies --cov=src/crawling_utils

# Run specific test class
pytest tests/test_crawling_strategies.py::TestSitemapCrawlingStrategy -v
```

---

## Best practices

### 1. Always Use Factory

```python
# Good: Let factory select strategy
strategy = CrawlingStrategyFactory.get_strategy(url)
result = await strategy.crawl(crawler, url)

# Avoid: Manual strategy selection (unless you have a specific reason)
if url.endswith("sitemap.xml"):
    strategy = SitemapCrawlingStrategy()
```

### 2. Handle Errors Gracefully

```python
result = await strategy.crawl(crawler, url)

if result.success:
    # Process documents
    for doc in result.documents:
        process_document(doc)
else:
    # Log error and continue
    logger.error(f"Crawl failed for {url}: {result.error_message}")
    # Don't raise exception - graceful degradation
```

### 3. Use Type Hints

```python
from typing import List, Dict, Any
from crawling_strategies import CrawlResult

async def process_crawl(url: str) -> CrawlResult:
    """Type hints help with IDE support and documentation."""
    strategy = CrawlingStrategyFactory.get_strategy(url)
    return await strategy.crawl(crawler, url)
```

### 4. Test with Mocks

```python
# Don't make actual HTTP requests in tests
with patch("crawl4ai_mcp.parse_sitemap", return_value=["..."]):
    result = await strategy.crawl(mock_crawler, url)
```

### 5. Configure Concurrency

```python
# Adjust based on target server capacity
result = await strategy.crawl(
    crawler,
    url,
    max_concurrent=5  # Lower for rate-limited sites
)
```

---

## Common Patterns

### Pattern 1: Crawl and Store

```python
from crawling_strategies import CrawlingStrategyFactory
from crawling_utils import smart_chunk_markdown, extract_section_info

async def crawl_and_store(url: str, db_client):
    """Crawl URL and store chunks in database."""
    strategy = CrawlingStrategyFactory.get_strategy(url)
    result = await strategy.crawl(crawler, url)

    if not result.success:
        return {"error": result.error_message}

    # Chunk and store
    for doc in result.documents:
        chunks = smart_chunk_markdown(doc["markdown"], chunk_size=5000)

        for i, chunk in enumerate(chunks):
            metadata = extract_section_info(chunk)
            metadata["url"] = doc["url"]
            metadata["chunk_index"] = i

            db_client.insert(chunk, metadata)

    return {"pages": result.pages_crawled, "chunks": len(chunks)}
```

### Pattern 2: Batch Processing with Different Strategies

```python
async def process_urls(urls: List[str]):
    """Process multiple URLs with appropriate strategies."""
    results = {}

    for url in urls:
        strategy = CrawlingStrategyFactory.get_strategy(url)
        result = await strategy.crawl(crawler, url)

        results[url] = {
            "success": result.success,
            "pages": result.pages_crawled,
            "strategy": result.metadata.get("strategy")
        }

    return results
```

### Pattern 3: Retry Logic

```python
async def crawl_with_retry(url: str, max_retries: int = 3):
    """Crawl with automatic retry on failure."""
    strategy = CrawlingStrategyFactory.get_strategy(url)

    for attempt in range(max_retries):
        result = await strategy.crawl(crawler, url)

        if result.success:
            return result

        logger.warning(f"Attempt {attempt + 1} failed: {result.error_message}")
        await asyncio.sleep(2 ** attempt)  # Exponential backoff

    # All retries failed
    return result
```

---

## Troubleshooting

### Issue: Strategy not selected

**Problem**: Factory returns wrong strategy for URL.

**Solution**: Check detection order and implement custom strategy with higher priority.

```python
# Check which strategy is selected
strategy = CrawlingStrategyFactory.get_strategy(url)
print(strategy.__class__.__name__)

# Register custom strategy with higher priority
CrawlingStrategyFactory.register_strategy(MyStrategy, position=0)
```

### Issue: Crawl returns no documents

**Problem**: `result.documents` is empty but `result.success` is True.

**Solution**: Check if pages have content or if filters are too restrictive.

```python
result = await strategy.crawl(crawler, url)

if result.success and not result.documents:
    logger.warning(f"Crawl succeeded but found no content for {url}")
    # Check metadata for clues
    print(result.metadata)
```

### Issue: Chunking creates too many/few chunks

**Problem**: Chunks are too small or too large.

**Solution**: Adjust `chunk_size` parameter.

```python
# Smaller chunks (more granular)
chunks = smart_chunk_markdown(text, chunk_size=1000)

# Larger chunks (fewer, longer)
chunks = smart_chunk_markdown(text, chunk_size=10000)
```

---

## Migration Guide

### Migrating from `smart_crawl_url`

**Before (Phase 1)**:
```python
# Direct function calls
if is_txt(url):
    crawl_results = await crawl_markdown_file(crawler, url)
elif is_sitemap(url):
    sitemap_urls = parse_sitemap(url)
    crawl_results = await crawl_batch(crawler, sitemap_urls, max_concurrent)
else:
    crawl_results = await crawl_recursive_internal_links(crawler, [url], max_depth, max_concurrent)
```

**After (Phase 2)**:
```python
# Strategy pattern
strategy = CrawlingStrategyFactory.get_strategy(url)
result = await strategy.crawl(crawler, url, max_depth, max_concurrent)
crawl_results = result.documents
```

---

## Performance Tips

1. **Adjust Concurrency**: Lower for rate-limited sites, higher for fast servers
2. **Use Batch Crawling**: More efficient than sequential crawls
3. **Cache Strategy Instances**: Reuse strategy objects across crawls
4. **Monitor Memory**: Use memory-adaptive dispatching for large crawls
5. **Chunk Size**: Larger chunks = fewer embeddings but less granular search

---

*For more information, see PHASE1_REFACTORING_REPORT.md*
