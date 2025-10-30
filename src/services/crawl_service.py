"""
Crawl Service - Business Logic for Web Crawling

This service contains all crawling business logic, extracted from MCP tools.
Tools become thin wrappers that call service methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from crawl4ai import AsyncWebCrawler

from .base_service import BaseService


@dataclass
class CrawlResult:
    """Result of a crawling operation."""

    success: bool
    url: str
    pages_crawled: int
    chunks_stored: int
    code_examples_stored: int = 0
    error: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "url": self.url,
            "pages_crawled": self.pages_crawled,
            "chunks_stored": self.chunks_stored,
            "code_examples_stored": self.code_examples_stored,
            "error": self.error,
            "metadata": self.metadata or {},
        }


class CrawlService(BaseService):
    """
    Service for web crawling operations.

    This service is framework-independent and can be used from:
    - MCP tools (thin wrappers)
    - CLI commands
    - Background jobs
    - API endpoints
    - Tests (easy to mock dependencies)

    Example:
        # In MCP tool
        service = CrawlService(crawler, document_repo, config)
        result = await service.crawl_and_store(url, max_depth=3)
        return json.dumps(result.to_dict(), indent=2)

        # In test
        mock_crawler = Mock()
        mock_repo = Mock()
        service = CrawlService(mock_crawler, mock_repo, test_config)
        result = await service.crawl_and_store("http://test.com")
        assert result.success
    """

    def __init__(
        self,
        crawler: AsyncWebCrawler,
        document_repository: DocumentRepository,
        config: CrawlConfig,
    ):
        """
        Initialize crawl service.

        Args:
            crawler: Crawl4AI crawler instance
            document_repository: Repository for storing documents
            config: Crawling configuration
        """
        super().__init__()
        self.crawler = crawler
        self.document_repo = document_repository
        self.config = config

    async def crawl_and_store(
        self, url: str, max_depth: int = 3, chunk_size: int = 5000, extract_code: bool = False
    ) -> CrawlResult:
        """
        Crawl a URL and store the content.

        This is pure business logic - no MCP context needed.

        Args:
            url: URL to crawl
            max_depth: Maximum depth to crawl
            chunk_size: Size of text chunks for storage
            extract_code: Whether to extract code examples

        Returns:
            CrawlResult with success status and metrics
        """
        self._log_operation("crawl_and_store", url=url, max_depth=max_depth)

        try:
            # Strategy selection
            strategy = self._select_strategy(url)

            # Perform crawl
            crawl_result = await strategy.crawl(crawler=self.crawler, url=url, max_depth=max_depth)

            if not crawl_result.success:
                return CrawlResult(
                    success=False,
                    url=url,
                    pages_crawled=0,
                    chunks_stored=0,
                    error=crawl_result.error_message,
                )

            # Store documents
            chunks_stored = await self.document_repo.save_documents(
                crawl_result.documents, chunk_size=chunk_size
            )

            # Extract and store code if requested
            code_examples_stored = 0
            if extract_code:
                code_examples_stored = await self._extract_and_store_code(crawl_result.documents)

            return CrawlResult(
                success=True,
                url=url,
                pages_crawled=crawl_result.pages_crawled,
                chunks_stored=chunks_stored,
                code_examples_stored=code_examples_stored,
                metadata={"strategy": strategy.__class__.__name__, "chunk_size": chunk_size},
            )

        except Exception as e:
            error_dict = self._handle_error(e, {"url": url, "max_depth": max_depth})
            return CrawlResult(
                success=False,
                url=url,
                pages_crawled=0,
                chunks_stored=0,
                error=error_dict["error"]["message"],
            )

    def _select_strategy(self, url: str) -> CrawlingStrategy:
        """
        Select appropriate crawling strategy based on URL.

        Args:
            url: URL to analyze

        Returns:
            Appropriate crawling strategy
        """
        # Import here to avoid circular dependency
        from ..strategies.crawling_strategy import CrawlingStrategyFactory

        return CrawlingStrategyFactory.get_strategy(url)

    async def _extract_and_store_code(self, documents: list[Document]) -> int:
        """
        Extract code examples from documents and store them.

        Args:
            documents: List of crawled documents

        Returns:
            Number of code examples stored
        """
        # Implementation would go here
        # This is a placeholder for the complete implementation
        return 0
