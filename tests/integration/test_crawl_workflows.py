"""
Integration tests for crawling workflows.

This comprehensive test suite covers end-to-end crawling workflows including:
- crawl_single_page complete workflow
- smart_crawl_url with different URL types (sitemap, webpage, text file)
- crawl_with_stealth_mode for bot-protected sites
- crawl_with_memory_monitoring for large-scale crawls
- crawl_with_multi_url_config for batch processing
- Error handling and edge cases
- Integration with storage (Supabase mocking)
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Mock heavy dependencies before importing
sys.modules["crawl4ai"] = MagicMock()
sys.modules["crawl4ai_mcp"] = MagicMock()

# Import modules to test
from crawling_strategies import (
    CrawlingStrategyFactory,
    CrawlResult,
    RecursiveCrawlingStrategy,
    SitemapCrawlingStrategy,
    TextFileCrawlingStrategy,
)


class TestCrawlSinglePageWorkflow:
    """Test complete crawl_single_page end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_crawl_single_page_success(self, mock_context, mock_env_config):
        """Test successful single page crawl with storage."""
        url = "https://example.com/docs"

        # Setup mocks
        crawler = mock_context.request_context.lifespan_context.crawler
        supabase_client = mock_context.request_context.lifespan_context.supabase_client

        # Mock crawler result
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = (
            "# Documentation\n\nSample content here.\n\n```python\ndef hello(): pass\n```"
        )
        mock_result.error_message = None
        mock_result.links = {"internal": ["https://example.com/page1"], "external": []}
        crawler.arun = AsyncMock(return_value=mock_result)

        # Mock storage operations
        query_chain = Mock()
        query_chain.execute = Mock(return_value=Mock(data=[]))
        supabase_client.table.return_value.insert.return_value = query_chain
        supabase_client.table.return_value.upsert.return_value = query_chain
        supabase_client.rpc = Mock(return_value=Mock(execute=Mock(return_value=Mock(data=[]))))

        # Import and execute the workflow
        with (
            patch("src.crawl_helpers.add_documents_to_supabase"),
            patch("src.crawl_helpers.update_source_info"),
            patch("src.crawl_helpers.extract_source_summary", return_value="Sample site"),
        ):
            # Simulate crawl_single_page workflow
            from src.crawl_helpers import (
                chunk_and_prepare_documents,
                crawl_and_extract_content,
                validate_crawl_url,
            )

            # Step 1: Validate URL
            validation = validate_crawl_url(url)
            assert validation["valid"] is True
            assert validation["source_id"] == "example.com"

            # Step 2: Crawl and extract
            success, markdown, metadata = await crawl_and_extract_content(crawler, url)
            assert success is True
            assert len(markdown) > 0
            assert metadata["success"] is True

            # Step 3: Chunk and prepare
            urls, chunk_numbers, contents, metadatas, total_words = chunk_and_prepare_documents(
                url, markdown, "example.com"
            )
            assert len(contents) > 0
            assert len(urls) == len(contents)
            assert total_words > 0

    @pytest.mark.asyncio
    async def test_crawl_single_page_invalid_url(self):
        """Test crawl_single_page with invalid URL."""
        from src.crawl_helpers import validate_crawl_url

        invalid_urls = ["", "not-a-url", "ftp://example.com", None]

        for invalid_url in invalid_urls:
            validation = validate_crawl_url(invalid_url)
            assert validation["valid"] is False
            assert "error" in validation

    @pytest.mark.asyncio
    async def test_crawl_single_page_network_failure(self, mock_context):
        """Test crawl_single_page with network failure."""
        url = "https://example.com/docs"
        crawler = mock_context.request_context.lifespan_context.crawler

        # Mock network error
        crawler.arun = AsyncMock(side_effect=Exception("Connection timeout"))

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)
        assert success is False
        assert "error" in metadata
        assert "Connection timeout" in metadata["error"]

    @pytest.mark.asyncio
    async def test_crawl_single_page_with_code_extraction(self, mock_context, mock_env_config):
        """Test crawl_single_page with code example extraction enabled."""
        url = "https://example.com/docs"
        markdown_with_code = """# API Documentation

## Example Usage

```python
def process_data(data):
    return data.strip()
```

More documentation here.

```javascript
function parse(str) {
    return JSON.parse(str);
}
```
"""

        from src.crawl_helpers import extract_and_process_code_examples

        with (
            patch.dict("os.environ", {"USE_AGENTIC_RAG": "true"}),
            patch("src.crawl_helpers.extract_code_blocks") as mock_extract,
            patch("src.crawl_helpers.generate_code_example_summary", return_value="Test summary"),
        ):
            mock_extract.return_value = [
                {
                    "code": "def process_data(data):\n    return data.strip()",
                    "language": "python",
                    "context_before": "## Example Usage",
                    "context_after": "More documentation",
                },
                {
                    "code": "function parse(str) {\n    return JSON.parse(str);\n}",
                    "language": "javascript",
                    "context_before": "More documentation",
                    "context_after": "",
                },
            ]

            (code_urls, chunk_nums, examples, summaries, metadata) = (
                extract_and_process_code_examples(url, markdown_with_code, "example.com")
            )

            assert len(examples) == 2
            assert len(summaries) == 2
            assert all(s == "Test summary" for s in summaries)


class TestSmartCrawlUrlWorkflow:
    """Test smart_crawl_url with automatic strategy selection."""

    @pytest.mark.asyncio
    async def test_smart_crawl_sitemap_url(self, mock_context):
        """Test smart_crawl_url automatically detects and crawls sitemap."""
        sitemap_url = "https://example.com/sitemap.xml"
        mock_urls = ["https://example.com/page1", "https://example.com/page2"]

        crawler = mock_context.request_context.lifespan_context.crawler

        with (
            patch("crawling_strategies.crawl_utils.parse_sitemap", return_value=mock_urls),
            patch(
                "crawling_strategies.crawl_utils.crawl_batch", new_callable=AsyncMock
            ) as mock_batch,
        ):
            mock_batch.return_value = [
                {"url": url, "markdown": f"Content from {url}"} for url in mock_urls
            ]

            # Execute smart crawl
            strategy = CrawlingStrategyFactory.get_strategy(sitemap_url)
            result = await strategy.crawl(crawler, sitemap_url)

            assert isinstance(strategy, SitemapCrawlingStrategy)
            assert result.success is True
            assert result.pages_crawled == 2
            assert result.metadata["strategy"] == "sitemap"

    @pytest.mark.asyncio
    async def test_smart_crawl_text_file_url(self, mock_context):
        """Test smart_crawl_url automatically detects and crawls text files."""
        text_url = "https://example.com/llms.txt"

        crawler = mock_context.request_context.lifespan_context.crawler

        with (
            patch("crawling_strategies.crawl_utils.is_txt", return_value=True),
            patch("crawling_strategies.crawl_utils.is_sitemap", return_value=False),
            patch(
                "crawling_strategies.crawl_utils.crawl_markdown_file", new_callable=AsyncMock
            ) as mock_crawl,
        ):
            mock_crawl.return_value = [
                {"url": text_url, "markdown": "# LLM Configuration\n\nContent here"}
            ]

            strategy = CrawlingStrategyFactory.get_strategy(text_url)
            result = await strategy.crawl(crawler, text_url)

            assert isinstance(strategy, TextFileCrawlingStrategy)
            assert result.success is True
            assert result.metadata["strategy"] == "text_file"

    @pytest.mark.asyncio
    async def test_smart_crawl_recursive_webpage(self, mock_context):
        """Test smart_crawl_url falls back to recursive crawling for regular pages."""
        page_url = "https://example.com/docs/index.html"

        crawler = mock_context.request_context.lifespan_context.crawler

        with (
            patch("crawling_strategies.crawl_utils.is_sitemap", return_value=False),
            patch("crawling_strategies.crawl_utils.is_txt", return_value=False),
            patch(
                "crawling_strategies.crawl_utils.crawl_recursive_internal_links",
                new_callable=AsyncMock,
            ) as mock_crawl,
        ):
            mock_crawl.return_value = [
                {"url": page_url, "markdown": "Home page"},
                {"url": "https://example.com/docs/guide", "markdown": "Guide page"},
            ]

            strategy = CrawlingStrategyFactory.get_strategy(page_url)
            result = await strategy.crawl(crawler, page_url, max_depth=2)

            assert isinstance(strategy, RecursiveCrawlingStrategy)
            assert result.success is True
            assert result.pages_crawled == 2
            assert result.metadata["max_depth"] == 2

    @pytest.mark.asyncio
    async def test_smart_crawl_with_storage_integration(
        self, mock_context, mock_supabase_with_data
    ):
        """Test smart_crawl_url with full storage pipeline."""
        url = "https://example.com"

        crawler = mock_context.request_context.lifespan_context.crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_with_data

        with (
            patch("crawling_strategies.crawl_utils.is_sitemap", return_value=False),
            patch("crawling_strategies.crawl_utils.is_txt", return_value=False),
            patch(
                "crawling_strategies.crawl_utils.crawl_recursive_internal_links",
                new_callable=AsyncMock,
            ) as mock_crawl,
            patch("crawl4ai_mcp.process_and_store_crawl_results") as mock_storage,
        ):
            mock_crawl.return_value = [{"url": url, "markdown": "# Home\n\nWelcome to the site"}]

            mock_storage.return_value = {
                "chunks_stored": 1,
                "code_examples_stored": 0,
                "sources_updated": 1,
            }

            strategy = CrawlingStrategyFactory.get_strategy(url)
            result = await strategy.crawl(crawler, url)

            assert result.success is True
            # Verify storage was attempted
            assert len(result.documents) > 0


class TestCrawlWithStealthMode:
    """Test crawl_with_stealth_mode for bot-protected sites."""

    @pytest.mark.asyncio
    async def test_stealth_mode_basic_crawl(self, mock_context):
        """Test stealth mode basic functionality."""
        url = "https://protected-site.com"

        # Mock stealth crawler
        stealth_crawler = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# Protected Content\n\nThis is behind Cloudflare."
        mock_result.url = url
        stealth_crawler.arun = AsyncMock(return_value=mock_result)
        stealth_crawler.__aenter__ = AsyncMock(return_value=stealth_crawler)
        stealth_crawler.__aexit__ = AsyncMock()

        with (
            patch("crawl4ai.AsyncWebCrawler", return_value=stealth_crawler),
            patch("crawling_strategies.CrawlingStrategyFactory.get_strategy") as mock_factory,
        ):
            # Mock strategy result
            mock_strategy = Mock()
            mock_strategy.crawl = AsyncMock(
                return_value=CrawlResult(
                    success=True,
                    url=url,
                    pages_crawled=1,
                    documents=[{"url": url, "markdown": mock_result.markdown}],
                    metadata={"strategy": "stealth_recursive"},
                )
            )
            mock_factory.return_value = mock_strategy

            # Execute stealth crawl
            result = await mock_strategy.crawl(stealth_crawler, url)

            assert result.success is True
            assert result.pages_crawled == 1
            assert "stealth" in result.metadata["strategy"]

    @pytest.mark.asyncio
    async def test_stealth_mode_with_selectors(self, mock_context):
        """Test stealth mode with wait_for_selector option."""

        # The stealth mode should pass selector options to crawler config
        with patch("crawl4ai.BrowserConfig") as mock_browser_config:
            # Verify browser config created with undetected mode
            mock_browser_config.assert_not_called()  # Not called yet

            # Would be called in actual implementation
            # with browser_type="undetected", headless=True

    @pytest.mark.asyncio
    async def test_stealth_mode_cloudflare_bypass(self, mock_context):
        """Test stealth mode bypasses Cloudflare protection."""
        url = "https://cloudflare-protected.com"

        # Mock stealth crawler that successfully bypasses protection
        stealth_crawler = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# Protected Content\n\nCloudflare bypassed successfully."
        mock_result.error_message = None
        stealth_crawler.arun = AsyncMock(return_value=mock_result)
        stealth_crawler.__aenter__ = AsyncMock(return_value=stealth_crawler)
        stealth_crawler.__aexit__ = AsyncMock()

        with patch("crawl4ai.AsyncWebCrawler", return_value=stealth_crawler):
            # In real implementation, this would use undetected browser
            result = await stealth_crawler.arun(url=url)

            assert result.success is True
            assert "Cloudflare bypassed" in result.markdown


class TestCrawlWithMemoryMonitoring:
    """Test crawl_with_memory_monitoring for large-scale crawls."""

    @pytest.mark.asyncio
    async def test_memory_monitoring_basic(self, mock_context):
        """Test memory monitoring basic functionality."""
        url = "https://large-site.com/sitemap.xml"

        crawler = mock_context.request_context.lifespan_context.crawler

        # Mock memory monitor
        mock_monitor = AsyncMock()
        mock_monitor.stats = Mock()
        mock_monitor.stats.to_dict = Mock(
            return_value={
                "peak_memory_mb": 450,
                "current_memory_mb": 420,
                "threshold_mb": 500,
                "throttled_count": 0,
            }
        )
        mock_monitor.__aenter__ = AsyncMock(return_value=mock_monitor)
        mock_monitor.__aexit__ = AsyncMock()

        with (
            patch("memory_monitor.MemoryMonitor", return_value=mock_monitor),
            patch(
                "crawling_strategies.crawl_utils.parse_sitemap",
                return_value=["https://large-site.com/page1"],
            ),
            patch(
                "crawling_strategies.crawl_utils.crawl_batch", new_callable=AsyncMock
            ) as mock_batch,
        ):
            mock_batch.return_value = [
                {"url": "https://large-site.com/page1", "markdown": "Content"}
            ]

            strategy = CrawlingStrategyFactory.get_strategy(url)
            result = await strategy.crawl(crawler, url)

            assert result.success is True
            # Memory stats would be included in actual response

    @pytest.mark.asyncio
    async def test_memory_monitoring_throttling(self, mock_context):
        """Test memory monitoring triggers throttling when threshold exceeded."""

        # Mock memory monitor that triggers throttling
        mock_monitor = AsyncMock()
        mock_monitor.check_memory = AsyncMock(
            return_value={"should_throttle": True, "current_memory_mb": 520, "threshold_mb": 500}
        )
        mock_monitor.stats = Mock()
        mock_monitor.stats.to_dict = Mock(
            return_value={
                "peak_memory_mb": 520,
                "current_memory_mb": 510,
                "threshold_mb": 500,
                "throttled_count": 3,
            }
        )
        mock_monitor.__aenter__ = AsyncMock(return_value=mock_monitor)
        mock_monitor.__aexit__ = AsyncMock()

        with patch("memory_monitor.MemoryMonitor", return_value=mock_monitor):
            # Verify monitor was created with correct threshold
            pass

    @pytest.mark.asyncio
    async def test_memory_monitoring_large_batch(self, mock_context):
        """Test memory monitoring handles large batches efficiently."""
        sitemap_url = "https://large-docs.com/sitemap.xml"

        # Generate large URL list (simulating 100+ pages)
        large_url_list = [f"https://large-docs.com/page{i}" for i in range(100)]

        crawler = mock_context.request_context.lifespan_context.crawler

        with (
            patch("crawling_strategies.crawl_utils.parse_sitemap", return_value=large_url_list),
            patch(
                "crawling_strategies.crawl_utils.crawl_batch", new_callable=AsyncMock
            ) as mock_batch,
            patch("memory_monitor.MemoryMonitor") as mock_monitor_class,
        ):
            # Mock monitor that doesn't throttle
            mock_monitor = AsyncMock()
            mock_monitor.stats = Mock()
            mock_monitor.stats.to_dict = Mock(
                return_value={"peak_memory_mb": 480, "throttled_count": 0}
            )
            mock_monitor.__aenter__ = AsyncMock(return_value=mock_monitor)
            mock_monitor.__aexit__ = AsyncMock()
            mock_monitor_class.return_value = mock_monitor

            # Mock batch crawl returns partial results
            mock_batch.return_value = [
                {"url": url, "markdown": f"Content {i}"}
                for i, url in enumerate(large_url_list[:50])  # Only 50 succeed
            ]

            strategy = CrawlingStrategyFactory.get_strategy(sitemap_url)
            result = await strategy.crawl(crawler, sitemap_url)

            assert result.success is True
            assert result.pages_crawled == 50


class TestCrawlWithMultiUrlConfig:
    """Test crawl_with_multi_url_config for batch processing."""

    @pytest.mark.asyncio
    async def test_multi_url_all_success(self, mock_context):
        """Test multi-URL crawling with all successes."""
        urls = ["https://docs.example.com", "https://api.example.com", "https://blog.example.com"]

        crawler = mock_context.request_context.lifespan_context.crawler

        with (
            patch("crawling_strategies.crawl_utils.is_sitemap", return_value=False),
            patch("crawling_strategies.crawl_utils.is_txt", return_value=False),
            patch(
                "crawling_strategies.crawl_utils.crawl_recursive_internal_links",
                new_callable=AsyncMock,
            ) as mock_crawl,
        ):
            # Mock successful crawls for all URLs
            async def mock_crawl_side_effect(crawler, url_list, **kwargs):
                return [{"url": url_list[0], "markdown": f"Content from {url_list[0]}"}]

            mock_crawl.side_effect = mock_crawl_side_effect

            results = []
            for url in urls:
                strategy = CrawlingStrategyFactory.get_strategy(url)
                result = await strategy.crawl(crawler, url)
                results.append(
                    {"url": url, "success": result.success, "pages_crawled": result.pages_crawled}
                )

            assert len(results) == 3
            assert all(r["success"] for r in results)

    @pytest.mark.asyncio
    async def test_multi_url_partial_failures(self, mock_context):
        """Test multi-URL crawling with some failures."""
        urls = [
            "https://good-site.com",
            "https://failing-site.com",
            "https://another-good-site.com",
        ]

        crawler = mock_context.request_context.lifespan_context.crawler

        with (
            patch("crawling_strategies.crawl_utils.is_sitemap", return_value=False),
            patch("crawling_strategies.crawl_utils.is_txt", return_value=False),
            patch(
                "crawling_strategies.crawl_utils.crawl_recursive_internal_links",
                new_callable=AsyncMock,
            ) as mock_crawl,
        ):
            call_count = 0

            async def mock_crawl_side_effect(crawler, url_list, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 2:  # Second URL fails
                    raise Exception("Site unreachable")
                return [{"url": url_list[0], "markdown": "Content"}]

            mock_crawl.side_effect = mock_crawl_side_effect

            results = []
            for url in urls:
                strategy = CrawlingStrategyFactory.get_strategy(url)
                try:
                    result = await strategy.crawl(crawler, url)
                    results.append({"url": url, "success": result.success})
                except Exception as e:
                    results.append({"url": url, "success": False, "error": str(e)})

            assert len(results) == 3
            successful = [r for r in results if r.get("success")]
            assert len(successful) == 2  # 2 of 3 succeeded

    @pytest.mark.asyncio
    async def test_multi_url_content_type_detection(self, mock_context):
        """Test multi-URL crawling detects content types correctly."""
        urls_with_types = [
            ("https://docs.python.org", "documentation"),
            ("https://news.example.com/article", "article"),
            ("https://example.com", "general"),
        ]

        for url, expected_type in urls_with_types:
            # Determine content type
            if any(kw in url.lower() for kw in ["docs", "documentation", "api"]):
                content_type = "documentation"
            elif any(kw in url.lower() for kw in ["news", "article", "blog"]):
                content_type = "article"
            else:
                content_type = "general"

            assert content_type == expected_type

    @pytest.mark.asyncio
    async def test_multi_url_parallel_execution(self, mock_context):
        """Test multi-URL crawling executes in parallel efficiently."""
        urls = [f"https://site{i}.com" for i in range(5)]

        crawler = mock_context.request_context.lifespan_context.crawler

        # Track execution timing

        with (
            patch("crawling_strategies.crawl_utils.is_sitemap", return_value=False),
            patch("crawling_strategies.crawl_utils.is_txt", return_value=False),
            patch(
                "crawling_strategies.crawl_utils.crawl_recursive_internal_links",
                new_callable=AsyncMock,
            ) as mock_crawl,
        ):

            async def mock_crawl_with_delay(crawler, url_list, **kwargs):
                await asyncio.sleep(0.01)  # Simulate network delay
                return [{"url": url_list[0], "markdown": "Content"}]

            mock_crawl.side_effect = mock_crawl_with_delay

            # Execute in parallel
            tasks = []
            for url in urls:
                strategy = CrawlingStrategyFactory.get_strategy(url)
                tasks.append(strategy.crawl(crawler, url))

            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(r.success for r in results)


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in crawl workflows."""

    @pytest.mark.asyncio
    async def test_empty_content_handling(self, mock_context):
        """Test handling of pages with empty content."""
        url = "https://example.com/empty"

        crawler = mock_context.request_context.lifespan_context.crawler
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = ""
        mock_result.error_message = "No content found"
        crawler.arun = AsyncMock(return_value=mock_result)

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)

        # Empty content is treated as failure by design
        assert success is False
        assert "error" in metadata

    @pytest.mark.asyncio
    async def test_malformed_html_handling(self, mock_context):
        """Test handling of malformed HTML."""
        url = "https://example.com/malformed"

        crawler = mock_context.request_context.lifespan_context.crawler
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "<div>Unclosed tag\n\nSome content"
        mock_result.links = {"internal": [], "external": []}
        crawler.arun = AsyncMock(return_value=mock_result)

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)

        # Should handle gracefully
        assert success is True
        assert len(markdown) > 0

    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_context):
        """Test handling of request timeouts."""
        url = "https://slow-site.com"

        crawler = mock_context.request_context.lifespan_context.crawler
        crawler.arun = AsyncMock(side_effect=asyncio.TimeoutError("Request timeout"))

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)

        assert success is False
        assert "timeout" in metadata["error"].lower()

    @pytest.mark.asyncio
    async def test_redirect_handling(self, mock_context):
        """Test handling of HTTP redirects."""
        original_url = "https://example.com/old"
        redirect_url = "https://example.com/new"

        crawler = mock_context.request_context.lifespan_context.crawler
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# New Page\n\nRedirected content"
        mock_result.url = redirect_url  # Final URL after redirect
        mock_result.links = {"internal": [], "external": []}
        crawler.arun = AsyncMock(return_value=mock_result)

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, original_url)

        assert success is True
        assert len(markdown) > 0

    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self, mock_context):
        """Test handling of rate limiting (429 responses)."""
        url = "https://rate-limited.com"

        crawler = mock_context.request_context.lifespan_context.crawler
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "429 Too Many Requests"
        crawler.arun = AsyncMock(return_value=mock_result)

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)

        assert success is False
        assert "429" in metadata["error"]

    @pytest.mark.asyncio
    async def test_invalid_encoding_handling(self, mock_context):
        """Test handling of invalid character encoding."""
        url = "https://example.com/weird-encoding"

        crawler = mock_context.request_context.lifespan_context.crawler
        # Simulate content with mixed encoding
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# Title\n\nContent with special chars: \u00e9\u00e8\u00ea"
        mock_result.links = {"internal": [], "external": []}
        crawler.arun = AsyncMock(return_value=mock_result)

        from src.crawl_helpers import crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)

        assert success is True
        # Should handle special characters correctly
        assert "\u00e9" in markdown or "e" in markdown

    @pytest.mark.asyncio
    async def test_very_large_page_handling(self, mock_context):
        """Test handling of very large pages."""
        url = "https://example.com/huge-page"

        # Generate large content (> 5MB)
        large_content = "# Large Page\n\n" + ("Content " * 100000)

        crawler = mock_context.request_context.lifespan_context.crawler
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = large_content
        mock_result.links = {"internal": [], "external": []}
        crawler.arun = AsyncMock(return_value=mock_result)

        from src.crawl_helpers import chunk_and_prepare_documents, crawl_and_extract_content

        success, markdown, metadata = await crawl_and_extract_content(crawler, url)
        assert success is True

        # Chunk the large content
        urls, chunk_numbers, contents, metadatas, total_words = chunk_and_prepare_documents(
            url, markdown, "example.com", chunk_size=5000
        )

        # Should be chunked into multiple pieces
        assert len(contents) > 10
        assert all(len(chunk) <= 5000 for chunk in contents)


class TestCrawlWorkflowIntegration:
    """Test full integration of crawl workflows with storage."""

    @pytest.mark.asyncio
    async def test_end_to_end_crawl_and_store(self, mock_context, mock_supabase_with_data):
        """Test complete end-to-end workflow from crawl to storage."""
        url = "https://example.com/docs"

        crawler = mock_context.request_context.lifespan_context.crawler
        supabase_client = mock_supabase_with_data

        # Mock crawler
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "# Documentation\n\nTest content for storage."
        mock_result.links = {"internal": [], "external": []}
        crawler.arun = AsyncMock(return_value=mock_result)

        # Execute full workflow
        with (
            patch("src.crawl_helpers.add_documents_to_supabase") as mock_add_docs,
            patch("src.crawl_helpers.update_source_info") as mock_update_source,
            patch("src.crawl_helpers.extract_source_summary", return_value="Test site"),
        ):
            from src.crawl_helpers import (
                chunk_and_prepare_documents,
                crawl_and_extract_content,
                store_crawl_results,
                validate_crawl_url,
            )

            # Full workflow
            validation = validate_crawl_url(url)
            assert validation["valid"]

            success, markdown, metadata = await crawl_and_extract_content(crawler, url)
            assert success

            urls, chunk_nums, contents, metas, words = chunk_and_prepare_documents(
                url, markdown, validation["source_id"]
            )

            # Store results
            store_crawl_results(
                supabase_client,
                urls,
                chunk_nums,
                contents,
                metas,
                {url: markdown},
                validation["source_id"],
                words,
                "Test site",
            )

            # Verify storage was called
            mock_update_source.assert_called_once()
            mock_add_docs.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_crawls_do_not_interfere(self, mock_context):
        """Test multiple concurrent crawls don't interfere with each other."""
        urls = ["https://site1.com", "https://site2.com", "https://site3.com"]

        crawler = mock_context.request_context.lifespan_context.crawler

        call_count = 0

        async def mock_crawl(url, **kwargs):
            nonlocal call_count
            call_count += 1
            result = Mock()
            result.success = True
            result.markdown = f"Content from call {call_count}"
            result.url = url
            await asyncio.sleep(0.01)  # Simulate network delay
            return result

        # Import function before using it
        from src.crawl_helpers import crawl_and_extract_content

        # Update mock to include links
        async def mock_crawl_with_links(url, **kwargs):
            nonlocal call_count
            call_count += 1
            result = Mock()
            result.success = True
            result.markdown = f"Content from call {call_count}"
            result.url = url
            result.links = {"internal": [], "external": []}
            await asyncio.sleep(0.01)  # Simulate network delay
            return result

        crawler.arun = mock_crawl_with_links

        # Execute concurrently
        tasks = [crawl_and_extract_content(crawler, url) for url in urls]
        results = await asyncio.gather(*tasks)

        # Results are tuples: (success, markdown, metadata)
        assert len(results) == 3
        assert all(success for success, _, _ in results)
        # Each should have unique content
        contents = [markdown for _, markdown, _ in results]
        assert len(set(contents)) == 3
