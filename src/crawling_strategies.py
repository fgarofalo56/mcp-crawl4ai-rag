"""
Crawling strategies for different URL types.

This module implements the Strategy pattern for crawling operations,
providing a clean separation of concerns for different crawling methods:
- Sitemap crawling: Extracts and crawls all URLs from XML sitemaps
- Text file crawling: Directly retrieves content from text files
- Recursive crawling: Crawls internal links up to a specified depth

Each strategy implements a common interface for consistent behavior
and easy extensibility.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# Import utility functions for URL detection and crawling
# Note: These imports are from crawl4ai_mcp because the utils haven't been
# moved to crawling_utils yet - this will be part of Phase 2
import crawl4ai_mcp as crawl_utils
from crawl4ai import AsyncWebCrawler


@dataclass
class CrawlResult:
    """
    Result of a crawling operation.

    Attributes:
        success: Whether the crawl was successful
        url: The URL that was crawled
        pages_crawled: Number of pages successfully crawled
        documents: List of crawled documents with URL and markdown content
        error_message: Error message if crawl failed (None if successful)
        metadata: Additional metadata about the crawl operation
    """

    success: bool
    url: str
    pages_crawled: int
    documents: list[dict[str, Any]]
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class CrawlingStrategy(ABC):
    """
    Abstract base class for crawling strategies.

    All concrete crawling strategies must implement the crawl() and detect() methods.
    This provides a consistent interface for different types of crawling operations.
    """

    @abstractmethod
    async def crawl(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        max_depth: int = 3,
        max_concurrent: int = 10,
        **kwargs,
    ) -> CrawlResult:
        """
        Perform the crawling operation.

        Args:
            crawler: AsyncWebCrawler instance to use for crawling
            url: URL to crawl
            max_depth: Maximum recursion depth for recursive crawling
            max_concurrent: Maximum number of concurrent browser sessions
            **kwargs: Additional strategy-specific parameters

        Returns:
            CrawlResult with crawling results and metadata
        """
        pass

    @staticmethod
    @abstractmethod
    def detect(url: str) -> bool:
        """
        Detect if this strategy can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if this strategy can handle the URL, False otherwise
        """
        pass

    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy.

        Returns:
            Strategy name as a string
        """
        name = self.__class__.__name__
        for suffix in ("CrawlingStrategy", "Strategy"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break
        return name.lower()


class SitemapCrawlingStrategy(CrawlingStrategy):
    """
    Strategy for crawling URLs from XML sitemaps.

    This strategy parses a sitemap.xml file and crawls all URLs found
    in parallel with configurable concurrency limits.
    """

    async def crawl(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        max_depth: int = 3,
        max_concurrent: int = 10,
        **kwargs,
    ) -> CrawlResult:
        """
        Crawl all URLs from a sitemap in parallel.

        Args:
            crawler: AsyncWebCrawler instance
            url: URL of the sitemap
            max_depth: Not used for sitemap crawling
            max_concurrent: Maximum number of concurrent browser sessions
            **kwargs: Additional parameters (ignored)

        Returns:
            CrawlResult with all crawled pages from the sitemap
        """
        try:
            # Parse sitemap to extract URLs
            sitemap_urls = crawl_utils.parse_sitemap(url)

            if not sitemap_urls:
                return CrawlResult(
                    success=False,
                    url=url,
                    pages_crawled=0,
                    documents=[],
                    error_message="No URLs found in sitemap",
                    metadata={"strategy": "sitemap"},
                )

            # Crawl all URLs in parallel
            documents = await crawl_utils.crawl_batch(crawler, sitemap_urls, max_concurrent)

            return CrawlResult(
                success=True,
                url=url,
                pages_crawled=len(documents),
                documents=documents,
                metadata={
                    "strategy": "sitemap",
                    "urls_found": len(sitemap_urls),
                    "max_concurrent": max_concurrent,
                },
            )

        except Exception as e:
            return CrawlResult(
                success=False,
                url=url,
                pages_crawled=0,
                documents=[],
                error_message=str(e),
                metadata={"strategy": "sitemap"},
            )

    @staticmethod
    def detect(url: str) -> bool:
        """
        Detect if URL is a sitemap.

        Args:
            url: URL to check

        Returns:
            True if URL appears to be a sitemap, False otherwise
        """
        return crawl_utils.is_sitemap(url)


class TextFileCrawlingStrategy(CrawlingStrategy):
    """
    Strategy for crawling text files (e.g., llms.txt, README.txt).

    This strategy directly retrieves and processes text file content
    without following links or recursive crawling.
    """

    async def crawl(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        max_depth: int = 3,
        max_concurrent: int = 10,
        **kwargs,
    ) -> CrawlResult:
        """
        Crawl a text file directly.

        Args:
            crawler: AsyncWebCrawler instance
            url: URL of the text file
            max_depth: Not used for text file crawling
            max_concurrent: Not used for text file crawling
            **kwargs: Additional parameters (ignored)

        Returns:
            CrawlResult with the text file content
        """
        try:
            # Crawl the text file
            documents = await crawl_utils.crawl_markdown_file(crawler, url)

            if not documents:
                return CrawlResult(
                    success=False,
                    url=url,
                    pages_crawled=0,
                    documents=[],
                    error_message="Failed to retrieve text file content",
                    metadata={"strategy": "text_file"},
                )

            return CrawlResult(
                success=True,
                url=url,
                pages_crawled=len(documents),
                documents=documents,
                metadata={"strategy": "text_file"},
            )

        except Exception as e:
            return CrawlResult(
                success=False,
                url=url,
                pages_crawled=0,
                documents=[],
                error_message=str(e),
                metadata={"strategy": "text_file"},
            )

    @staticmethod
    def detect(url: str) -> bool:
        """
        Detect if URL is a text file.

        Args:
            url: URL to check

        Returns:
            True if URL appears to be a text file, False otherwise
        """
        return crawl_utils.is_txt(url)


class RecursiveCrawlingStrategy(CrawlingStrategy):
    """
    Strategy for recursively crawling internal links from a webpage.

    This strategy starts from a URL and follows internal links up to a
    specified depth, crawling pages in parallel with memory-aware dispatch.
    """

    async def crawl(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        max_depth: int = 3,
        max_concurrent: int = 10,
        **kwargs,
    ) -> CrawlResult:
        """
        Recursively crawl internal links from a starting URL.

        Args:
            crawler: AsyncWebCrawler instance
            url: Starting URL
            max_depth: Maximum recursion depth (default: 3)
            max_concurrent: Maximum number of concurrent browser sessions
            **kwargs: Additional parameters (ignored)

        Returns:
            CrawlResult with all recursively crawled pages
        """
        try:
            # Recursively crawl internal links
            documents = await crawl_utils.crawl_recursive_internal_links(
                crawler, [url], max_depth=max_depth, max_concurrent=max_concurrent
            )

            if not documents:
                return CrawlResult(
                    success=False,
                    url=url,
                    pages_crawled=0,
                    documents=[],
                    error_message="No content found during recursive crawl",
                    metadata={"strategy": "recursive", "max_depth": max_depth},
                )

            return CrawlResult(
                success=True,
                url=url,
                pages_crawled=len(documents),
                documents=documents,
                metadata={
                    "strategy": "recursive",
                    "max_depth": max_depth,
                    "max_concurrent": max_concurrent,
                },
            )

        except Exception as e:
            return CrawlResult(
                success=False,
                url=url,
                pages_crawled=0,
                documents=[],
                error_message=str(e),
                metadata={"strategy": "recursive", "max_depth": max_depth},
            )

    @staticmethod
    def detect(url: str) -> bool:
        """
        Detect if URL is a regular webpage (not sitemap or text file).

        This is the fallback strategy - it handles any URL that isn't
        specifically a sitemap or text file.

        Args:
            url: URL to check

        Returns:
            True (always, as this is the default strategy)
        """
        # This is the default/fallback strategy
        return True


class CrawlingStrategyFactory:
    """
    Factory for selecting the appropriate crawling strategy for a URL.

    This factory uses strategy detection to automatically select the best
    crawling approach based on the URL type.
    """

    # Ordered list of strategies (most specific first)
    _strategies = [
        SitemapCrawlingStrategy,
        TextFileCrawlingStrategy,
        RecursiveCrawlingStrategy,  # Fallback strategy (always matches)
    ]

    @classmethod
    def get_strategy(cls, url: str) -> CrawlingStrategy:
        """
        Get the appropriate crawling strategy for a URL.

        Strategies are checked in order of specificity:
        1. Sitemap crawling (for sitemap.xml files)
        2. Text file crawling (for .txt files)
        3. Recursive crawling (default fallback)

        Args:
            url: URL to get strategy for

        Returns:
            Appropriate CrawlingStrategy instance

        Raises:
            ValueError: If no strategy can handle the URL (should never happen
                       due to fallback strategy)
        """
        for strategy_class in cls._strategies:
            if strategy_class.detect(url):
                return strategy_class()

        # This should never happen due to RecursiveCrawlingStrategy being a fallback
        raise ValueError(f"No crawling strategy found for URL: {url}")

    @classmethod
    def register_strategy(cls, strategy_class: type, position: int = 0):
        """
        Register a new crawling strategy.

        This allows for dynamic extension of the factory with custom strategies.

        Args:
            strategy_class: Class implementing CrawlingStrategy
            position: Position in strategy list (0 = highest priority)

        Raises:
            TypeError: If strategy_class doesn't inherit from CrawlingStrategy
        """
        if not issubclass(strategy_class, CrawlingStrategy):
            raise TypeError(f"{strategy_class.__name__} must inherit from CrawlingStrategy")

        cls._strategies.insert(position, strategy_class)

    @classmethod
    def get_all_strategies(cls) -> list[type]:
        """
        Get list of all registered strategy classes.

        Returns:
            List of strategy classes in priority order
        """
        return cls._strategies.copy()
