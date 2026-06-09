"""
Tests for crawling strategies module.

This test suite covers:
- URL type detection
- Strategy detection and selection
- Factory pattern functionality
- Individual strategy implementations
- CrawlResult data structure
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.crawling_strategies import (
    CrawlingStrategy,
    CrawlingStrategyFactory,
    CrawlResult,
    RecursiveCrawlingStrategy,
    SitemapCrawlingStrategy,
    TextFileCrawlingStrategy,
)


class TestCrawlResult:
    """Test CrawlResult dataclass."""

    def test_crawl_result_success(self):
        """Test creating a successful CrawlResult."""
        result = CrawlResult(
            success=True,
            url="https://example.com",
            pages_crawled=5,
            documents=[{"url": "https://example.com/1", "markdown": "content"}],
            metadata={"strategy": "sitemap"},
        )

        assert result.success is True
        assert result.url == "https://example.com"
        assert result.pages_crawled == 5
        assert len(result.documents) == 1
        assert result.error_message is None
        assert result.metadata["strategy"] == "sitemap"

    def test_crawl_result_failure(self):
        """Test creating a failed CrawlResult."""
        result = CrawlResult(
            success=False,
            url="https://example.com",
            pages_crawled=0,
            documents=[],
            error_message="Network error",
            metadata={"strategy": "recursive"},
        )

        assert result.success is False
        assert result.error_message == "Network error"
        assert len(result.documents) == 0

    def test_crawl_result_minimal(self):
        """Test creating CrawlResult with minimal parameters."""
        result = CrawlResult(success=True, url="https://example.com", pages_crawled=1, documents=[])

        assert result.success is True
        assert result.error_message is None
        assert result.metadata is None


class TestSitemapCrawlingStrategy:
    """Test SitemapCrawlingStrategy implementation."""

    def test_detect_sitemap_xml(self):
        """Test detection of sitemap.xml URLs."""
        assert SitemapCrawlingStrategy.detect("https://example.com/sitemap.xml") is True

    def test_detect_sitemap_in_path(self):
        """Test detection of URLs with sitemap in path."""
        assert SitemapCrawlingStrategy.detect("https://example.com/sitemap_index.xml") is True
        assert SitemapCrawlingStrategy.detect("https://example.com/news/sitemap.xml") is True

    def test_detect_non_sitemap(self):
        """Test detection rejects non-sitemap URLs."""
        assert SitemapCrawlingStrategy.detect("https://example.com/page.html") is False
        assert SitemapCrawlingStrategy.detect("https://example.com/file.txt") is False

    @pytest.mark.asyncio
    async def test_crawl_success(self):
        """Test successful sitemap crawling."""
        # Mock crawler
        mock_crawler = AsyncMock()

        # Mock parse_sitemap to return URLs
        mock_urls = ["https://example.com/page1", "https://example.com/page2"]

        # Mock crawl_batch to return documents
        mock_docs = [
            {"url": "https://example.com/page1", "markdown": "Content 1"},
            {"url": "https://example.com/page2", "markdown": "Content 2"},
        ]

        with patch("crawl4ai_mcp.parse_sitemap", return_value=mock_urls):
            with patch("crawl4ai_mcp.crawl_batch", return_value=mock_docs):
                strategy = SitemapCrawlingStrategy()
                result = await strategy.crawl(
                    mock_crawler, "https://example.com/sitemap.xml", max_concurrent=5
                )

                assert result.success is True
                assert result.pages_crawled == 2
                assert len(result.documents) == 2
                assert result.metadata["strategy"] == "sitemap"
                assert result.metadata["urls_found"] == 2
                assert result.metadata["max_concurrent"] == 5

    @pytest.mark.asyncio
    async def test_crawl_empty_sitemap(self):
        """Test crawling an empty sitemap."""
        mock_crawler = AsyncMock()

        with patch("crawl4ai_mcp.parse_sitemap", return_value=[]):
            strategy = SitemapCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/sitemap.xml")

            assert result.success is False
            assert result.error_message == "No URLs found in sitemap"
            assert result.pages_crawled == 0

    @pytest.mark.asyncio
    async def test_crawl_error_handling(self):
        """Test error handling during sitemap crawling."""
        mock_crawler = AsyncMock()

        with patch("crawl4ai_mcp.parse_sitemap", side_effect=Exception("Parse error")):
            strategy = SitemapCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/sitemap.xml")

            assert result.success is False
            assert "Parse error" in result.error_message
            assert result.pages_crawled == 0

    def test_get_strategy_name(self):
        """Test strategy name extraction."""
        strategy = SitemapCrawlingStrategy()
        assert strategy.get_strategy_name() == "sitemap"


class TestTextFileCrawlingStrategy:
    """Test TextFileCrawlingStrategy implementation."""

    def test_detect_txt_file(self):
        """Test detection of .txt URLs."""
        assert TextFileCrawlingStrategy.detect("https://example.com/llms.txt") is True
        assert TextFileCrawlingStrategy.detect("https://example.com/README.txt") is True

    def test_detect_non_txt(self):
        """Test detection rejects non-txt URLs."""
        assert TextFileCrawlingStrategy.detect("https://example.com/page.html") is False
        assert TextFileCrawlingStrategy.detect("https://example.com/sitemap.xml") is False

    @pytest.mark.asyncio
    async def test_crawl_success(self):
        """Test successful text file crawling."""
        mock_crawler = AsyncMock()

        mock_docs = [{"url": "https://example.com/llms.txt", "markdown": "File content"}]

        with patch("crawl4ai_mcp.crawl_markdown_file", return_value=mock_docs):
            strategy = TextFileCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/llms.txt")

            assert result.success is True
            assert result.pages_crawled == 1
            assert len(result.documents) == 1
            assert result.metadata["strategy"] == "text_file"

    @pytest.mark.asyncio
    async def test_crawl_empty_file(self):
        """Test crawling returns no content."""
        mock_crawler = AsyncMock()

        with patch("crawl4ai_mcp.crawl_markdown_file", return_value=[]):
            strategy = TextFileCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/empty.txt")

            assert result.success is False
            assert "Failed to retrieve text file content" in result.error_message
            assert result.pages_crawled == 0

    @pytest.mark.asyncio
    async def test_crawl_error_handling(self):
        """Test error handling during text file crawling."""
        mock_crawler = AsyncMock()

        with patch("crawl4ai_mcp.crawl_markdown_file", side_effect=Exception("Network error")):
            strategy = TextFileCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/file.txt")

            assert result.success is False
            assert "Network error" in result.error_message

    def test_get_strategy_name(self):
        """Test strategy name extraction."""
        strategy = TextFileCrawlingStrategy()
        assert strategy.get_strategy_name() == "textfile"


class TestRecursiveCrawlingStrategy:
    """Test RecursiveCrawlingStrategy implementation."""

    def test_detect_always_true(self):
        """Test that recursive strategy always matches (fallback)."""
        assert RecursiveCrawlingStrategy.detect("https://example.com/page.html") is True
        assert RecursiveCrawlingStrategy.detect("https://example.com/") is True
        assert RecursiveCrawlingStrategy.detect("https://example.com/anything") is True

    @pytest.mark.asyncio
    async def test_crawl_success(self):
        """Test successful recursive crawling."""
        mock_crawler = AsyncMock()

        mock_docs = [
            {"url": "https://example.com/", "markdown": "Home page"},
            {"url": "https://example.com/about", "markdown": "About page"},
        ]

        with patch("crawl4ai_mcp.crawl_recursive_internal_links", return_value=mock_docs):
            strategy = RecursiveCrawlingStrategy()
            result = await strategy.crawl(
                mock_crawler,
                "https://example.com/",
                max_depth=2,
                max_concurrent=5,
            )

            assert result.success is True
            assert result.pages_crawled == 2
            assert len(result.documents) == 2
            assert result.metadata["strategy"] == "recursive"
            assert result.metadata["max_depth"] == 2
            assert result.metadata["max_concurrent"] == 5

    @pytest.mark.asyncio
    async def test_crawl_no_content(self):
        """Test recursive crawl finds no content."""
        mock_crawler = AsyncMock()

        with patch("crawl4ai_mcp.crawl_recursive_internal_links", return_value=[]):
            strategy = RecursiveCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/")

            assert result.success is False
            assert "No content found" in result.error_message
            assert result.pages_crawled == 0

    @pytest.mark.asyncio
    async def test_crawl_error_handling(self):
        """Test error handling during recursive crawling."""
        mock_crawler = AsyncMock()

        with patch(
            "crawl4ai_mcp.crawl_recursive_internal_links",
            side_effect=Exception("Crawl error"),
        ):
            strategy = RecursiveCrawlingStrategy()
            result = await strategy.crawl(mock_crawler, "https://example.com/")

            assert result.success is False
            assert "Crawl error" in result.error_message

    def test_get_strategy_name(self):
        """Test strategy name extraction."""
        strategy = RecursiveCrawlingStrategy()
        assert strategy.get_strategy_name() == "recursive"


class TestCrawlingStrategyFactory:
    """Test CrawlingStrategyFactory functionality."""

    def test_get_strategy_for_sitemap(self):
        """Test factory returns SitemapCrawlingStrategy for sitemaps."""
        strategy = CrawlingStrategyFactory.get_strategy("https://example.com/sitemap.xml")
        assert isinstance(strategy, SitemapCrawlingStrategy)

    def test_get_strategy_for_txt(self):
        """Test factory returns TextFileCrawlingStrategy for text files."""
        strategy = CrawlingStrategyFactory.get_strategy("https://example.com/llms.txt")
        assert isinstance(strategy, TextFileCrawlingStrategy)

    def test_get_strategy_for_webpage(self):
        """Test factory returns RecursiveCrawlingStrategy for regular pages."""
        strategy = CrawlingStrategyFactory.get_strategy("https://example.com/page.html")
        assert isinstance(strategy, RecursiveCrawlingStrategy)

    def test_get_strategy_priority_order(self):
        """Test that most specific strategies are checked first."""
        # Sitemap should be detected before recursive
        strategy = CrawlingStrategyFactory.get_strategy("https://example.com/sitemap.xml")
        assert isinstance(strategy, SitemapCrawlingStrategy)
        assert not isinstance(strategy, RecursiveCrawlingStrategy)

    def test_register_custom_strategy(self):
        """Test registering a custom strategy."""

        class CustomStrategy(CrawlingStrategy):
            async def crawl(self, crawler, url, **kwargs):
                return CrawlResult(success=True, url=url, pages_crawled=0, documents=[])

            @staticmethod
            def detect(url: str) -> bool:
                return url.endswith(".custom")

        # Register custom strategy at highest priority
        CrawlingStrategyFactory.register_strategy(CustomStrategy, position=0)

        # Test custom strategy is selected
        strategy = CrawlingStrategyFactory.get_strategy("https://example.com/file.custom")
        assert isinstance(strategy, CustomStrategy)

        # Cleanup - remove custom strategy
        strategies = CrawlingStrategyFactory.get_all_strategies()
        strategies.remove(CustomStrategy)

    def test_register_invalid_strategy_raises_error(self):
        """Test that registering a non-strategy class raises TypeError."""

        class NotAStrategy:
            pass

        with pytest.raises(TypeError, match="must inherit from CrawlingStrategy"):
            CrawlingStrategyFactory.register_strategy(NotAStrategy)

    def test_get_all_strategies(self):
        """Test getting all registered strategies."""
        strategies = CrawlingStrategyFactory.get_all_strategies()

        assert len(strategies) >= 3
        assert SitemapCrawlingStrategy in strategies
        assert TextFileCrawlingStrategy in strategies
        assert RecursiveCrawlingStrategy in strategies

    def test_strategy_order_preserved(self):
        """Test that strategy order is preserved (most specific first)."""
        strategies = CrawlingStrategyFactory.get_all_strategies()

        # Sitemap should come before recursive (more specific)
        sitemap_idx = strategies.index(SitemapCrawlingStrategy)
        recursive_idx = strategies.index(RecursiveCrawlingStrategy)

        assert sitemap_idx < recursive_idx


class TestStrategyIntegration:
    """Integration tests for strategy pattern."""

    @pytest.mark.asyncio
    async def test_end_to_end_sitemap_crawl(self):
        """Test complete sitemap crawling workflow."""
        mock_crawler = AsyncMock()

        # Mock all dependencies
        with patch("crawl4ai_mcp.parse_sitemap", return_value=["https://example.com/1"]):
            with patch(
                "crawl4ai_mcp.crawl_batch",
                return_value=[{"url": "https://example.com/1", "markdown": "Content"}],
            ):
                # Factory selects strategy
                strategy = CrawlingStrategyFactory.get_strategy("https://example.com/sitemap.xml")

                # Execute crawl
                result = await strategy.crawl(mock_crawler, "https://example.com/sitemap.xml")

                # Verify results
                assert result.success is True
                assert result.pages_crawled == 1
                assert result.metadata["strategy"] == "sitemap"

    @pytest.mark.asyncio
    async def test_end_to_end_text_file_crawl(self):
        """Test complete text file crawling workflow."""
        mock_crawler = AsyncMock()

        with patch(
            "crawl4ai_mcp.crawl_markdown_file",
            return_value=[{"url": "https://example.com/file.txt", "markdown": "Content"}],
        ):
            strategy = CrawlingStrategyFactory.get_strategy("https://example.com/file.txt")
            result = await strategy.crawl(mock_crawler, "https://example.com/file.txt")

            assert result.success is True
            assert result.pages_crawled == 1
            assert result.metadata["strategy"] == "text_file"

    @pytest.mark.asyncio
    async def test_end_to_end_recursive_crawl(self):
        """Test complete recursive crawling workflow."""
        mock_crawler = AsyncMock()

        with patch(
            "crawl4ai_mcp.crawl_recursive_internal_links",
            return_value=[
                {"url": "https://example.com/", "markdown": "Home"},
                {"url": "https://example.com/about", "markdown": "About"},
            ],
        ):
            strategy = CrawlingStrategyFactory.get_strategy("https://example.com/")
            result = await strategy.crawl(mock_crawler, "https://example.com/", max_depth=2)

            assert result.success is True
            assert result.pages_crawled == 2
            assert result.metadata["strategy"] == "recursive"
            assert result.metadata["max_depth"] == 2

    def test_multiple_urls_use_correct_strategies(self):
        """Test that different URLs get correct strategies."""
        urls_and_expected = [
            ("https://example.com/sitemap.xml", SitemapCrawlingStrategy),
            ("https://example.com/llms.txt", TextFileCrawlingStrategy),
            ("https://example.com/page.html", RecursiveCrawlingStrategy),
            ("https://example.com/", RecursiveCrawlingStrategy),
        ]

        for url, expected_strategy in urls_and_expected:
            strategy = CrawlingStrategyFactory.get_strategy(url)
            assert isinstance(strategy, expected_strategy), f"Failed for URL: {url}"


class TestStrategyExtensibility:
    """Test strategy pattern extensibility."""

    def test_can_create_custom_strategy(self):
        """Test creating a custom strategy implementation."""

        class RSSFeedStrategy(CrawlingStrategy):
            """Custom strategy for RSS feeds."""

            async def crawl(self, crawler, url, **kwargs):
                return CrawlResult(
                    success=True,
                    url=url,
                    pages_crawled=1,
                    documents=[{"url": url, "markdown": "RSS content"}],
                    metadata={"strategy": "rss"},
                )

            @staticmethod
            def detect(url: str) -> bool:
                return url.endswith(".rss") or url.endswith(".xml") and "feed" in url

        # Create instance
        strategy = RSSFeedStrategy()
        assert strategy.get_strategy_name() == "rssfeed"

    def test_strategy_inheritance(self):
        """Test that all strategies properly inherit from base class."""
        strategies = [
            SitemapCrawlingStrategy(),
            TextFileCrawlingStrategy(),
            RecursiveCrawlingStrategy(),
        ]

        for strategy in strategies:
            assert isinstance(strategy, CrawlingStrategy)
            assert hasattr(strategy, "crawl")
            assert hasattr(strategy, "detect")
            assert hasattr(strategy, "get_strategy_name")
