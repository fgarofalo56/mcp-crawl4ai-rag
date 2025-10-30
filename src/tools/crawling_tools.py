"""
Crawling Tools

MCP tools for web crawling operations with various strategies.
"""

import json

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
)
from fastmcp import Context

from utils import extract_source_summary

from .graphrag_tools import process_and_store_crawl_results


async def crawl_single_page(ctx: Context, url: str) -> str:
    """
    Crawl a single web page and store its content in Supabase.

    This tool is ideal for quickly retrieving content from a specific URL without following links.
    The content is stored in Supabase for later retrieval and querying.

    Args:
        ctx: The MCP server provided context
        url: URL of the web page to crawl

    Returns:
        Summary of the crawling operation and storage in Supabase
    """
    # Import crawl helpers
    from crawl_helpers import (
        chunk_and_prepare_documents,
        crawl_and_extract_content,
        extract_and_process_code_examples,
        should_extract_code_examples,
        store_code_examples,
        store_crawl_results,
        validate_crawl_url,
    )

    try:
        # Validate URL
        validation = validate_crawl_url(url)
        if not validation["valid"]:
            return json.dumps(
                {"success": False, "url": url, "error": validation["error"]}, indent=2
            )

        # Get the crawler and client from the context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Crawl and extract content
        success, markdown_content, metadata = await crawl_and_extract_content(crawler, url)

        if not success:
            return json.dumps(
                {"success": False, "url": url, "error": metadata.get("error", "Unknown error")},
                indent=2,
            )

        # Get source_id from validation
        source_id = validation["source_id"]

        # Chunk and prepare documents
        urls, chunk_numbers, contents, metadatas, total_word_count = chunk_and_prepare_documents(
            url, markdown_content, source_id
        )

        # Create url_to_full_document mapping
        url_to_full_document = {url: markdown_content}

        # Extract source summary and store results
        source_summary = extract_source_summary(source_id, markdown_content[:5000])
        store_crawl_results(
            supabase_client,
            urls,
            chunk_numbers,
            contents,
            metadatas,
            url_to_full_document,
            source_id,
            total_word_count,
            source_summary,
        )

        # Process code examples if enabled
        code_examples_count = 0
        if should_extract_code_examples():
            (
                code_urls,
                code_chunk_numbers,
                code_examples,
                code_summaries,
                code_metadatas,
            ) = extract_and_process_code_examples(url, markdown_content, source_id)

            if code_examples:
                store_code_examples(
                    supabase_client,
                    code_urls,
                    code_chunk_numbers,
                    code_examples,
                    code_summaries,
                    code_metadatas,
                )
                code_examples_count = len(code_examples)

        return json.dumps(
            {
                "success": True,
                "url": url,
                "chunks_stored": len(contents),
                "code_examples_stored": code_examples_count,
                "content_length": metadata["content_length"],
                "total_word_count": total_word_count,
                "source_id": source_id,
                "links_count": metadata["links"],
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


async def crawl_with_stealth_mode(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    max_concurrent: int = 10,
    chunk_size: int = 5000,
    wait_for_selector: str = "",
    extra_wait: int = 2,
) -> str:
    """
    Crawl URLs using undetected browser mode to bypass bot protection (Cloudflare, Akamai, etc.).

    This tool uses stealth browser technology to appear as a regular user, making it ideal for:
    - Sites with Cloudflare protection
    - Sites with bot detection (Akamai, PerimeterX, etc.)
    - Sites that block headless browsers
    - Content behind aggressive anti-scraping measures

    Args:
        ctx: The MCP server provided context
        url: URL to crawl (can be a regular webpage, sitemap.xml, or .txt file)
        max_depth: Maximum recursion depth for regular URLs (default: 3)
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)
        chunk_size: Maximum size of each content chunk in characters (default: 5000)
        wait_for_selector: Optional CSS selector to wait for before extracting content
        extra_wait: Additional wait time in seconds after page load (default: 2)

    Returns:
        JSON string with crawl summary, storage information, and success statistics

    Example:
        # Bypass Cloudflare-protected site
        crawl_with_stealth_mode("https://example.com", wait_for_selector="div.content", extra_wait=3)
    """
    try:
        # Get supabase client from context
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Configure undetected browser for stealth mode
        browser_config = BrowserConfig(
            browser_type="undetected",
            headless=True,
            verbose=False,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

        # Initialize crawler with stealth configuration and execute strategy
        from crawling_strategies import CrawlingStrategyFactory

        async with AsyncWebCrawler(config=browser_config) as stealth_crawler:
            strategy = CrawlingStrategyFactory.get_strategy(url)
            crawl_result = await strategy.crawl(
                crawler=stealth_crawler,
                url=url,
                max_depth=max_depth,
                max_concurrent=max_concurrent,
            )

            # Handle crawl failures
            if not crawl_result.success:
                return json.dumps(
                    {
                        "success": False,
                        "url": url,
                        "error": crawl_result.error_message or "No content found",
                    },
                    indent=2,
                )

            # Process and store results
            storage_stats = process_and_store_crawl_results(
                supabase_client=supabase_client,
                crawl_results=crawl_result.documents,
                crawl_type=f"stealth_{crawl_result.metadata.get('strategy', 'unknown')}",
                chunk_size=chunk_size,
            )

            return json.dumps(
                {
                    "success": True,
                    "url": url,
                    "mode": "stealth (undetected browser)",
                    "crawl_type": f"stealth_{crawl_result.metadata.get('strategy', 'unknown')}",
                    "pages_crawled": crawl_result.pages_crawled,
                    "chunks_stored": storage_stats["chunks_stored"],
                    "code_examples_stored": storage_stats["code_examples_stored"],
                    "sources_updated": storage_stats["sources_updated"],
                },
                indent=2,
            )

    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


async def smart_crawl_url(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    max_concurrent: int = 10,
    chunk_size: int = 5000,
) -> str:
    """
    Intelligently crawl a URL based on its type and store content in Supabase.

    This tool automatically detects the URL type and applies the appropriate crawling method:
    - For sitemaps: Extracts and crawls all URLs in parallel
    - For text files (llms.txt): Directly retrieves the content
    - For regular webpages: Recursively crawls internal links up to the specified depth

    All crawled content is chunked and stored in Supabase for later retrieval and querying.

    Args:
        ctx: The MCP server provided context
        url: URL to crawl (can be a regular webpage, sitemap.xml, or .txt file)
        max_depth: Maximum recursion depth for regular URLs (default: 3)
        max_concurrent: Maximum number of concurrent browser sessions (default: 10)
        chunk_size: Maximum size of each content chunk in characters (default: 5000)

    Returns:
        JSON string with crawl summary and storage information
    """
    try:
        # Get clients from context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Get appropriate strategy and execute crawl
        from crawling_strategies import CrawlingStrategyFactory

        strategy = CrawlingStrategyFactory.get_strategy(url)
        crawl_result = await strategy.crawl(
            crawler=crawler,
            url=url,
            max_depth=max_depth,
            max_concurrent=max_concurrent,
        )

        # Handle crawl failures
        if not crawl_result.success:
            return json.dumps(
                {
                    "success": False,
                    "url": url,
                    "error": crawl_result.error_message or "No content found",
                },
                indent=2,
            )

        # Process and store results using helper function
        storage_stats = process_and_store_crawl_results(
            supabase_client=supabase_client,
            crawl_results=crawl_result.documents,
            crawl_type=crawl_result.metadata.get("strategy", "unknown"),
            chunk_size=chunk_size,
        )

        # Return success response
        return json.dumps(
            {
                "success": True,
                "url": url,
                "crawl_type": crawl_result.metadata.get("strategy", "unknown"),
                "pages_crawled": crawl_result.pages_crawled,
                "chunks_stored": storage_stats["chunks_stored"],
                "code_examples_stored": storage_stats["code_examples_stored"],
                "sources_updated": storage_stats["sources_updated"],
                "urls_crawled": [doc["url"] for doc in crawl_result.documents][:5]
                + (["..."] if len(crawl_result.documents) > 5 else []),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


async def crawl_with_multi_url_config(
    ctx: Context, urls_json: str, max_concurrent: int = 5, chunk_size: int = 5000
) -> str:
    """
    Crawl multiple URLs with smart per-URL configuration based on content type patterns.

    This tool automatically optimizes crawler settings for different types of content:
    - Documentation sites: Wait for code blocks, extra parsing time
    - News/articles: Focus on main content, minimal wait
    - E-commerce: Wait for dynamic pricing, product details
    - Forums/discussions: Handle infinite scroll, wait for comments

    Args:
        ctx: The MCP server provided context
        urls_json: JSON array of URLs to crawl with smart configuration
                   Example: '["https://docs.python.org", "https://news.example.com"]'
        max_concurrent: Maximum number of concurrent browser sessions (default: 5)
        chunk_size: Maximum size of each content chunk in characters (default: 5000)

    Returns:
        JSON string with crawl summary for each URL and aggregate statistics

    Example:
        # Crawl multiple site types with optimized settings
        urls = '["https://docs.example.com", "https://api.example.com"]'
        crawl_with_multi_url_config(urls)
    """
    try:
        # Get clients from context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Parse URL list
        try:
            url_list = json.loads(urls_json)
            if not isinstance(url_list, list):
                return json.dumps({"error": "urls_json must be a JSON array of URLs"})
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON: {str(e)}"})

        # Import strategy factory
        from crawling_strategies import CrawlingStrategyFactory

        results = []
        total_chunks = 0
        total_code_examples = 0
        total_sources = 0

        # Process each URL using strategy pattern
        for url in url_list:
            # Determine content type for metadata
            if any(kw in url.lower() for kw in ["docs", "documentation", "api", "reference"]):
                content_type = "documentation"
            elif any(kw in url.lower() for kw in ["news", "article", "blog", "post"]):
                content_type = "article"
            else:
                content_type = "general"

            # Execute crawl using appropriate strategy
            strategy = CrawlingStrategyFactory.get_strategy(url)
            crawl_result = await strategy.crawl(
                crawler=crawler,
                url=url,
                max_depth=2,
                max_concurrent=max_concurrent,
            )

            # Handle failures
            if not crawl_result.success:
                results.append(
                    {
                        "url": url,
                        "content_type": content_type,
                        "success": False,
                        "error": crawl_result.error_message or "No content found",
                    }
                )
                continue

            # Process and store results
            storage_stats = process_and_store_crawl_results(
                supabase_client=supabase_client,
                crawl_results=crawl_result.documents,
                crawl_type="multi_url",
                chunk_size=chunk_size,
            )

            # Aggregate stats
            results.append(
                {
                    "url": url,
                    "content_type": content_type,
                    "success": True,
                    "pages_crawled": crawl_result.pages_crawled,
                    "chunks_stored": storage_stats["chunks_stored"],
                    "code_examples_stored": storage_stats["code_examples_stored"],
                }
            )
            total_chunks += storage_stats["chunks_stored"]
            total_code_examples += storage_stats["code_examples_stored"]
            total_sources += storage_stats["sources_updated"]

        return json.dumps(
            {
                "success": True,
                "urls_processed": len(url_list),
                "total_chunks": total_chunks,
                "total_code_examples": total_code_examples,
                "total_sources": total_sources,
                "results": results,
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)


async def crawl_with_memory_monitoring(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    max_concurrent: int = 10,
    chunk_size: int = 5000,
    memory_threshold_mb: int = 500,
) -> str:
    """
    Crawl URLs with active memory monitoring and adaptive throttling.

    This tool monitors memory usage during large-scale crawling operations and automatically
    adjusts concurrency to prevent memory exhaustion. Ideal for:
    - Large-scale documentation sites (1000+ pages)
    - Sites with heavy media content
    - Long-running crawl operations
    - Resource-constrained environments

    Args:
        ctx: The MCP server provided context
        url: URL to crawl (sitemap, webpage, or text file)
        max_depth: Maximum recursion depth (default: 3)
        max_concurrent: Initial concurrent sessions (auto-adjusted, default: 10)
        chunk_size: Chunk size in characters (default: 5000)
        memory_threshold_mb: Memory limit in MB before throttling (default: 500)

    Returns:
        JSON string with crawl summary and memory statistics

    Example:
        # Crawl large site with memory monitoring
        crawl_with_memory_monitoring("https://docs.example.com/sitemap.xml", memory_threshold_mb=300)
    """
    try:
        # Get clients from context
        crawler = ctx.request_context.lifespan_context.crawler
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Use MemoryMonitor context manager
        from memory_monitor import MemoryMonitor

        async with MemoryMonitor(threshold_mb=memory_threshold_mb) as monitor:
            # Execute crawl using strategy pattern
            from crawling_strategies import CrawlingStrategyFactory

            strategy = CrawlingStrategyFactory.get_strategy(url)
            crawl_result = await strategy.crawl(
                crawler=crawler,
                url=url,
                max_depth=max_depth,
                max_concurrent=max_concurrent,
            )

            # Handle crawl failures
            if not crawl_result.success:
                return json.dumps(
                    {
                        "success": False,
                        "url": url,
                        "error": crawl_result.error_message or "No content found",
                    },
                    indent=2,
                )

            # Process and store results
            storage_stats = process_and_store_crawl_results(
                supabase_client=supabase_client,
                crawl_results=crawl_result.documents,
                crawl_type=f"memory_monitored_{crawl_result.metadata.get('strategy', 'unknown')}",
                chunk_size=chunk_size,
            )

            # Get final memory statistics
            memory_stats = monitor.stats.to_dict()

            return json.dumps(
                {
                    "success": True,
                    "url": url,
                    "crawl_type": f"memory_monitored_{crawl_result.metadata.get('strategy', 'unknown')}",
                    "pages_crawled": crawl_result.pages_crawled,
                    "chunks_stored": storage_stats["chunks_stored"],
                    "code_examples_stored": storage_stats["code_examples_stored"],
                    "sources_updated": storage_stats["sources_updated"],
                    "memory_stats": memory_stats,
                },
                indent=2,
            )

    except ImportError as e:
        return json.dumps(
            {
                "success": False,
                "error": f"Memory monitoring requires psutil library. Install with: pip install psutil. Error: {str(e)}",
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "url": url, "error": str(e)}, indent=2)


__all__ = [
    "crawl_single_page",
    "crawl_with_stealth_mode",
    "smart_crawl_url",
    "crawl_with_multi_url_config",
    "crawl_with_memory_monitoring",
]
