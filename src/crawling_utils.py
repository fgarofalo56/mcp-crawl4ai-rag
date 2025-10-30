"""
Utility functions for crawling operations.

This module contains reusable helper functions for:
- URL type detection
- Sitemap parsing
- Content chunking
- Batch crawling
- Recursive link crawling

These utilities are used by the crawling strategies to perform
specific crawling operations.
"""

import re
import sys
from typing import Any
from urllib.parse import urldefrag, urlparse
from xml.etree import ElementTree

import requests
from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    MemoryAdaptiveDispatcher,
)

# ============================================================================
# URL Type Detection
# ============================================================================


def is_sitemap(url: str) -> bool:
    """
    Check if a URL is a sitemap.

    Detects sitemaps by checking for:
    - URLs ending with "sitemap.xml"
    - URLs containing "sitemap" in the path

    Args:
        url: URL to check

    Returns:
        True if the URL appears to be a sitemap, False otherwise

    Examples:
        >>> is_sitemap("https://example.com/sitemap.xml")
        True
        >>> is_sitemap("https://example.com/sitemap_index.xml")
        True
        >>> is_sitemap("https://example.com/page.html")
        False
    """
    return url.endswith("sitemap.xml") or "sitemap" in urlparse(url).path


def is_txt(url: str) -> bool:
    """
    Check if a URL is a text file.

    Detects text files by checking if the URL ends with ".txt".

    Args:
        url: URL to check

    Returns:
        True if the URL appears to be a text file, False otherwise

    Examples:
        >>> is_txt("https://example.com/llms.txt")
        True
        >>> is_txt("https://example.com/README.txt")
        True
        >>> is_txt("https://example.com/page.html")
        False
    """
    return url.endswith(".txt")


def detect_url_type(url: str) -> str:
    """
    Detect the type of URL for strategy selection.

    Args:
        url: URL to detect type for

    Returns:
        One of: "sitemap", "text_file", "webpage"

    Examples:
        >>> detect_url_type("https://example.com/sitemap.xml")
        'sitemap'
        >>> detect_url_type("https://example.com/llms.txt")
        'text_file'
        >>> detect_url_type("https://example.com/page.html")
        'webpage'
    """
    if is_sitemap(url):
        return "sitemap"
    elif is_txt(url):
        return "text_file"
    else:
        return "webpage"


# ============================================================================
# Sitemap Parsing
# ============================================================================


def parse_sitemap(sitemap_url: str) -> list[str]:
    """
    Parse a sitemap XML file and extract all URLs.

    This function fetches the sitemap, parses the XML, and extracts
    all <loc> elements containing URLs.

    Args:
        sitemap_url: URL of the sitemap to parse

    Returns:
        List of URLs found in the sitemap (empty list if parsing fails)

    Examples:
        >>> urls = parse_sitemap("https://example.com/sitemap.xml")
        >>> len(urls) > 0
        True

    Note:
        - Handles XML parsing errors gracefully
        - Returns empty list on HTTP errors or malformed XML
        - Supports standard sitemap XML format with namespace
    """
    try:
        resp = requests.get(sitemap_url, timeout=30)
        urls = []

        if resp.status_code == 200:
            try:
                tree = ElementTree.fromstring(resp.content)
                # Handle XML namespaces using wildcard
                urls = [loc.text for loc in tree.findall(".//{*}loc") if loc.text]
            except ElementTree.ParseError as e:
                print(f"Error parsing sitemap XML: {e}", file=sys.stderr, flush=True)
                return []
        else:
            print(
                f"Failed to fetch sitemap (HTTP {resp.status_code}): {sitemap_url}",
                file=sys.stderr,
                flush=True,
            )
            return []

        return urls

    except requests.RequestException as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}", file=sys.stderr, flush=True)
        return []
    except Exception as e:
        print(f"Unexpected error parsing sitemap {sitemap_url}: {e}", file=sys.stderr, flush=True)
        return []


# ============================================================================
# Content Chunking
# ============================================================================


def smart_chunk_markdown(text: str, chunk_size: int = 5000) -> list[str]:
    """
    Split text into chunks, respecting code blocks and paragraphs.

    This function intelligently splits text at natural boundaries:
    1. Code blocks (```) - preferred boundary
    2. Paragraph breaks (\\n\\n)
    3. Sentence boundaries (. )
    4. Hard limit at chunk_size

    Args:
        text: Text to split into chunks
        chunk_size: Maximum size of each chunk in characters (default: 5000)

    Returns:
        List of text chunks

    Examples:
        >>> text = "# Header\\n\\nParagraph 1.\\n\\nParagraph 2."
        >>> chunks = smart_chunk_markdown(text, chunk_size=20)
        >>> len(chunks) >= 1
        True

    Note:
        - Respects markdown structure for better semantic preservation
        - Ensures chunks are at least 30% of chunk_size before breaking
        - Strips whitespace from chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # If we're at the end of the text, just take what's left
        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a code block boundary first (```)
        chunk = text[start:end]
        code_block = chunk.rfind("```")
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # If no code block, try to break at a paragraph
        elif "\n\n" in chunk:
            # Find the last paragraph break
            last_break = chunk.rfind("\n\n")
            if last_break > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_break

        # If no paragraph break, try to break at a sentence
        elif ". " in chunk:
            # Find the last sentence break
            last_period = chunk.rfind(". ")
            if last_period > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_period + 1

        # Extract chunk and clean it up
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position for next chunk
        start = end

    return chunks


def extract_section_info(chunk: str) -> dict[str, Any]:
    """
    Extract metadata from a markdown chunk.

    Extracts headers and basic statistics from a chunk of text.

    Args:
        chunk: Markdown chunk to analyze

    Returns:
        Dictionary containing:
        - headers: Semicolon-separated list of headers with levels
        - char_count: Number of characters in chunk
        - word_count: Number of words in chunk

    Examples:
        >>> chunk = "# Title\\n\\nContent here.\\n\\n## Section"
        >>> info = extract_section_info(chunk)
        >>> "headers" in info
        True
        >>> info["char_count"] > 0
        True
    """
    # Extract markdown headers
    headers = re.findall(r"^(#+)\s+(.+)$", chunk, re.MULTILINE)
    header_str = "; ".join([f"{h[0]} {h[1]}" for h in headers]) if headers else ""

    return {
        "headers": header_str,
        "char_count": len(chunk),
        "word_count": len(chunk.split()),
    }


# ============================================================================
# Crawling Operations
# ============================================================================


async def crawl_markdown_file(crawler: AsyncWebCrawler, url: str) -> list[dict[str, Any]]:
    """
    Crawl a text file or markdown document.

    This is a simple crawl operation that retrieves the content
    of a single file without following links.

    Args:
        crawler: AsyncWebCrawler instance
        url: URL of the file to crawl

    Returns:
        List containing a single dictionary with:
        - url: The file URL
        - markdown: The file content as markdown

    Examples:
        >>> # async example
        >>> # crawler = AsyncWebCrawler()
        >>> # result = await crawl_markdown_file(crawler, "https://example.com/file.txt")
        >>> # result[0]["url"] == "https://example.com/file.txt"
        True
    """
    crawl_config = CrawlerRunConfig()

    try:
        result = await crawler.arun(url=url, config=crawl_config)
        if result.success and result.markdown:
            return [{"url": url, "markdown": result.markdown}]
        else:
            error_msg = getattr(result, "error_message", "Unknown error")
            print(f"Failed to crawl {url}: {error_msg}", file=sys.stderr, flush=True)
            return []
    except Exception as e:
        print(f"Exception while crawling {url}: {e}", file=sys.stderr, flush=True)
        return []


async def crawl_batch(
    crawler: AsyncWebCrawler, urls: list[str], max_concurrent: int = 10
) -> list[dict[str, Any]]:
    """
    Batch crawl multiple URLs in parallel.

    Uses memory-adaptive dispatching to prevent resource exhaustion
    while maximizing parallelism.

    Args:
        crawler: AsyncWebCrawler instance
        urls: List of URLs to crawl
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)

    Returns:
        List of dictionaries, each containing:
        - url: The crawled URL
        - markdown: The page content as markdown

    Note:
        - Only returns successful crawls
        - Uses memory-adaptive dispatcher (70% threshold)
        - Bypasses cache for fresh content

    Examples:
        >>> # async example
        >>> # crawler = AsyncWebCrawler()
        >>> # urls = ["https://example.com/page1", "https://example.com/page2"]
        >>> # results = await crawl_batch(crawler, urls, max_concurrent=5)
        >>> # len(results) <= len(urls)
        True
    """
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent,
    )

    try:
        results = await crawler.arun_many(urls=urls, config=crawl_config, dispatcher=dispatcher)
        return [{"url": r.url, "markdown": r.markdown} for r in results if r.success and r.markdown]
    except Exception as e:
        print(f"Exception during batch crawl: {e}", file=sys.stderr, flush=True)
        return []


async def crawl_recursive_internal_links(
    crawler: AsyncWebCrawler,
    start_urls: list[str],
    max_depth: int = 3,
    max_concurrent: int = 10,
) -> list[dict[str, Any]]:
    """
    Recursively crawl internal links from start URLs up to a maximum depth.

    This function performs breadth-first crawling, visiting each depth level
    completely before moving to the next. It tracks visited URLs to avoid
    duplicates and only follows internal links.

    Args:
        crawler: AsyncWebCrawler instance
        start_urls: List of starting URLs
        max_depth: Maximum recursion depth (default: 3)
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)

    Returns:
        List of dictionaries, each containing:
        - url: The crawled URL
        - markdown: The page content as markdown

    Note:
        - Uses URL normalization (removes fragments)
        - Tracks visited URLs to prevent duplicates
        - Only follows internal links
        - Memory-adaptive dispatching for efficiency

    Examples:
        >>> # async example
        >>> # crawler = AsyncWebCrawler()
        >>> # results = await crawl_recursive_internal_links(
        >>> #     crawler,
        >>> #     ["https://example.com"],
        >>> #     max_depth=2,
        >>> #     max_concurrent=5
        >>> # )
        >>> # len(results) >= 1
        True
    """
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent,
    )

    visited = set()

    def normalize_url(url):
        """Remove URL fragments for consistent comparison."""
        return urldefrag(url)[0]

    current_urls = {normalize_url(u) for u in start_urls}
    results_all = []

    try:
        for _depth in range(max_depth):
            # Get URLs to crawl at this depth (not yet visited)
            urls_to_crawl = [
                normalize_url(url) for url in current_urls if normalize_url(url) not in visited
            ]

            if not urls_to_crawl:
                break

            # Crawl all URLs at this depth
            results = await crawler.arun_many(
                urls=urls_to_crawl, config=run_config, dispatcher=dispatcher
            )

            next_level_urls = set()

            # Process results and extract internal links
            for result in results:
                norm_url = normalize_url(result.url)
                visited.add(norm_url)

                if result.success and result.markdown:
                    results_all.append({"url": result.url, "markdown": result.markdown})

                    # Extract internal links for next depth level
                    internal_links = result.links.get("internal", [])
                    for link in internal_links:
                        next_url = normalize_url(link["href"])
                        if next_url not in visited:
                            next_level_urls.add(next_url)

            # Move to next depth level
            current_urls = next_level_urls

    except Exception as e:
        print(f"Exception during recursive crawl: {e}", file=sys.stderr, flush=True)

    return results_all


# ============================================================================
# Result Aggregation
# ============================================================================


def aggregate_crawl_stats(documents: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Aggregate statistics from crawled documents.

    Args:
        documents: List of crawled documents

    Returns:
        Dictionary with aggregated statistics:
        - total_pages: Number of documents
        - total_chars: Total character count
        - total_words: Total word count
        - avg_chars_per_page: Average characters per document
        - avg_words_per_page: Average words per document
        - unique_urls: Number of unique URLs

    Examples:
        >>> docs = [
        ...     {"url": "https://example.com/1", "markdown": "Test content"},
        ...     {"url": "https://example.com/2", "markdown": "More content here"}
        ... ]
        >>> stats = aggregate_crawl_stats(docs)
        >>> stats["total_pages"] == 2
        True
    """
    if not documents:
        return {
            "total_pages": 0,
            "total_chars": 0,
            "total_words": 0,
            "avg_chars_per_page": 0,
            "avg_words_per_page": 0,
            "unique_urls": 0,
        }

    total_chars = sum(len(doc.get("markdown", "")) for doc in documents)
    total_words = sum(len(doc.get("markdown", "").split()) for doc in documents)
    unique_urls = len({doc["url"] for doc in documents if "url" in doc})

    total_pages = len(documents)

    return {
        "total_pages": total_pages,
        "total_chars": total_chars,
        "total_words": total_words,
        "avg_chars_per_page": total_chars // total_pages if total_pages > 0 else 0,
        "avg_words_per_page": total_words // total_pages if total_pages > 0 else 0,
        "unique_urls": unique_urls,
    }
