"""
Tests for crawling utilities module.

This test suite covers:
- URL type detection functions
- Sitemap parsing
- Content chunking
- Metadata extraction
- Batch crawling operations
- Result aggregation
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.crawling_utils import (
    aggregate_crawl_stats,
    crawl_batch,
    crawl_markdown_file,
    crawl_recursive_internal_links,
    detect_url_type,
    extract_section_info,
    is_sitemap,
    is_txt,
    parse_sitemap,
    smart_chunk_markdown,
)


class TestURLDetection:
    """Test URL type detection functions."""

    def test_is_sitemap_with_sitemap_xml(self):
        """Test detection of sitemap.xml URLs."""
        assert is_sitemap("https://example.com/sitemap.xml") is True
        assert is_sitemap("https://example.com/news/sitemap.xml") is True

    def test_is_sitemap_with_sitemap_in_path(self):
        """Test detection of URLs with sitemap in path."""
        assert is_sitemap("https://example.com/sitemap_index.xml") is True
        assert is_sitemap("https://example.com/product-sitemap.xml") is True

    def test_is_sitemap_negative(self):
        """Test that non-sitemap URLs are correctly rejected."""
        assert is_sitemap("https://example.com/page.html") is False
        assert is_sitemap("https://example.com/file.txt") is False
        assert is_sitemap("https://example.com/") is False

    def test_is_txt_positive(self):
        """Test detection of .txt URLs."""
        assert is_txt("https://example.com/llms.txt") is True
        assert is_txt("https://example.com/README.txt") is True
        assert is_txt("https://example.com/docs/guide.txt") is True

    def test_is_txt_negative(self):
        """Test that non-txt URLs are correctly rejected."""
        assert is_txt("https://example.com/page.html") is False
        assert is_txt("https://example.com/sitemap.xml") is False
        assert is_txt("https://example.com/") is False

    def test_detect_url_type_sitemap(self):
        """Test URL type detection for sitemaps."""
        assert detect_url_type("https://example.com/sitemap.xml") == "sitemap"

    def test_detect_url_type_text_file(self):
        """Test URL type detection for text files."""
        assert detect_url_type("https://example.com/llms.txt") == "text_file"

    def test_detect_url_type_webpage(self):
        """Test URL type detection for regular webpages."""
        assert detect_url_type("https://example.com/page.html") == "webpage"
        assert detect_url_type("https://example.com/") == "webpage"


class TestSitemapParsing:
    """Test sitemap parsing functionality."""

    def test_parse_sitemap_success(self):
        """Test successful sitemap parsing."""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/page1</loc></url>
            <url><loc>https://example.com/page2</loc></url>
        </urlset>"""

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = mock_xml.encode()
            mock_get.return_value = mock_response

            urls = parse_sitemap("https://example.com/sitemap.xml")

            assert len(urls) == 2
            assert "https://example.com/page1" in urls
            assert "https://example.com/page2" in urls

    def test_parse_sitemap_with_namespace(self):
        """Test parsing sitemap with different namespaces."""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/test</loc></url>
        </urlset>"""

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = mock_xml.encode()
            mock_get.return_value = mock_response

            urls = parse_sitemap("https://example.com/sitemap.xml")

            assert len(urls) == 1
            assert urls[0] == "https://example.com/test"

    def test_parse_sitemap_http_error(self):
        """Test handling of HTTP errors."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            urls = parse_sitemap("https://example.com/sitemap.xml")

            assert urls == []

    def test_parse_sitemap_malformed_xml(self):
        """Test handling of malformed XML."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<invalid xml"
            mock_get.return_value = mock_response

            urls = parse_sitemap("https://example.com/sitemap.xml")

            assert urls == []

    def test_parse_sitemap_network_error(self):
        """Test handling of network errors."""
        with patch("requests.get", side_effect=Exception("Network error")):
            urls = parse_sitemap("https://example.com/sitemap.xml")

            assert urls == []


class TestContentChunking:
    """Test markdown chunking functionality."""

    def test_smart_chunk_markdown_simple(self):
        """Test chunking simple text."""
        text = "Short text that fits in one chunk."
        chunks = smart_chunk_markdown(text, chunk_size=100)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_smart_chunk_markdown_at_paragraph_boundary(self):
        """Test chunking at paragraph boundaries."""
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = smart_chunk_markdown(text, chunk_size=20)

        # Should split at paragraph boundaries
        assert len(chunks) > 1
        assert all(chunk.strip() for chunk in chunks)

    def test_smart_chunk_markdown_respects_code_blocks(self):
        """Test that code blocks are respected during chunking."""
        text = "Text before.\n\n```python\ncode here\n```\n\nText after."
        chunks = smart_chunk_markdown(text, chunk_size=30)

        # Code blocks should be preserved
        assert len(chunks) >= 1

    def test_smart_chunk_markdown_at_sentence_boundary(self):
        """Test chunking at sentence boundaries."""
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        chunks = smart_chunk_markdown(text, chunk_size=25)

        # Should split at sentence boundaries
        assert len(chunks) > 1

    def test_smart_chunk_markdown_empty_text(self):
        """Test chunking empty text."""
        chunks = smart_chunk_markdown("", chunk_size=100)

        assert chunks == []

    def test_smart_chunk_markdown_exact_chunk_size(self):
        """Test chunking text exactly at chunk size."""
        text = "a" * 100
        chunks = smart_chunk_markdown(text, chunk_size=100)

        assert len(chunks) == 1

    def test_smart_chunk_markdown_larger_than_chunk_size(self):
        """Test chunking text larger than chunk size."""
        text = "a" * 250
        chunks = smart_chunk_markdown(text, chunk_size=100)

        assert len(chunks) >= 2
        # Each chunk should not exceed chunk_size significantly
        for chunk in chunks[:-1]:  # Last chunk can be smaller
            assert len(chunk) <= 100


class TestMetadataExtraction:
    """Test metadata extraction from markdown."""

    def test_extract_section_info_with_headers(self):
        """Test extracting headers from markdown."""
        chunk = "# Title\n\nContent here.\n\n## Section"
        info = extract_section_info(chunk)

        assert "headers" in info
        assert "# Title" in info["headers"]
        assert "## Section" in info["headers"]

    def test_extract_section_info_no_headers(self):
        """Test extracting info from text without headers."""
        chunk = "Just plain text without any headers."
        info = extract_section_info(chunk)

        assert info["headers"] == ""
        assert info["char_count"] > 0
        assert info["word_count"] > 0

    def test_extract_section_info_char_count(self):
        """Test character count extraction."""
        chunk = "Test content"
        info = extract_section_info(chunk)

        assert info["char_count"] == len(chunk)

    def test_extract_section_info_word_count(self):
        """Test word count extraction."""
        chunk = "One two three four"
        info = extract_section_info(chunk)

        assert info["word_count"] == 4

    def test_extract_section_info_empty(self):
        """Test extracting info from empty chunk."""
        info = extract_section_info("")

        assert info["headers"] == ""
        assert info["char_count"] == 0
        assert info["word_count"] == 0


class TestCrawlOperations:
    """Test crawling operation functions."""

    @pytest.mark.asyncio
    async def test_crawl_markdown_file_success(self):
        """Test successful markdown file crawling."""
        mock_crawler = AsyncMock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.markdown = "File content"
        mock_crawler.arun.return_value = mock_result

        result = await crawl_markdown_file(mock_crawler, "https://example.com/file.txt")

        assert len(result) == 1
        assert result[0]["url"] == "https://example.com/file.txt"
        assert result[0]["markdown"] == "File content"

    @pytest.mark.asyncio
    async def test_crawl_markdown_file_failure(self):
        """Test handling of crawl failure."""
        mock_crawler = AsyncMock()
        mock_result = Mock()
        mock_result.success = False
        mock_result.error_message = "Not found"
        mock_crawler.arun.return_value = mock_result

        result = await crawl_markdown_file(mock_crawler, "https://example.com/file.txt")

        assert result == []

    @pytest.mark.asyncio
    async def test_crawl_markdown_file_exception(self):
        """Test exception handling during crawl."""
        mock_crawler = AsyncMock()
        mock_crawler.arun.side_effect = Exception("Network error")

        result = await crawl_markdown_file(mock_crawler, "https://example.com/file.txt")

        assert result == []

    @pytest.mark.asyncio
    async def test_crawl_batch_success(self):
        """Test successful batch crawling."""
        mock_crawler = AsyncMock()

        # Mock successful results
        mock_results = []
        for i in range(3):
            mock_result = Mock()
            mock_result.success = True
            mock_result.url = f"https://example.com/page{i}"
            mock_result.markdown = f"Content {i}"
            mock_results.append(mock_result)

        mock_crawler.arun_many.return_value = mock_results

        urls = [
            "https://example.com/page0",
            "https://example.com/page1",
            "https://example.com/page2",
        ]
        result = await crawl_batch(mock_crawler, urls, max_concurrent=5)

        assert len(result) == 3
        assert all("url" in doc and "markdown" in doc for doc in result)

    @pytest.mark.asyncio
    async def test_crawl_batch_filters_failures(self):
        """Test that batch crawl filters out failed results."""
        mock_crawler = AsyncMock()

        # Mix of success and failure
        mock_results = [
            Mock(success=True, url="https://example.com/1", markdown="Content 1"),
            Mock(success=False, url="https://example.com/2", markdown=None),
            Mock(success=True, url="https://example.com/3", markdown="Content 3"),
        ]

        mock_crawler.arun_many.return_value = mock_results

        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
        result = await crawl_batch(mock_crawler, urls)

        # Should only return successful crawls
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_crawl_batch_exception(self):
        """Test exception handling in batch crawl."""
        mock_crawler = AsyncMock()
        mock_crawler.arun_many.side_effect = Exception("Crawl error")

        urls = ["https://example.com/1", "https://example.com/2"]
        result = await crawl_batch(mock_crawler, urls)

        assert result == []


class TestRecursiveCrawling:
    """Test recursive crawling functionality."""

    @pytest.mark.asyncio
    async def test_crawl_recursive_single_depth(self):
        """Test recursive crawling with depth 1."""
        mock_crawler = AsyncMock()

        # Mock first level results
        mock_result = Mock()
        mock_result.success = True
        mock_result.url = "https://example.com/"
        mock_result.markdown = "Home content"
        mock_result.links = {"internal": []}

        mock_crawler.arun_many.return_value = [mock_result]

        result = await crawl_recursive_internal_links(
            mock_crawler, ["https://example.com/"], max_depth=1
        )

        assert len(result) == 1
        assert result[0]["url"] == "https://example.com/"

    @pytest.mark.asyncio
    async def test_crawl_recursive_multiple_depths(self):
        """Test recursive crawling with multiple depths."""
        mock_crawler = AsyncMock()

        # First call - home page with internal links
        mock_result1 = Mock()
        mock_result1.success = True
        mock_result1.url = "https://example.com/"
        mock_result1.markdown = "Home"
        mock_result1.links = {"internal": [{"href": "https://example.com/about"}]}

        # Second call - about page
        mock_result2 = Mock()
        mock_result2.success = True
        mock_result2.url = "https://example.com/about"
        mock_result2.markdown = "About"
        mock_result2.links = {"internal": []}

        mock_crawler.arun_many.side_effect = [[mock_result1], [mock_result2]]

        result = await crawl_recursive_internal_links(
            mock_crawler, ["https://example.com/"], max_depth=2
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_crawl_recursive_avoids_duplicates(self):
        """Test that recursive crawling avoids duplicate URLs."""
        mock_crawler = AsyncMock()

        # Mock result with link back to itself
        mock_result = Mock()
        mock_result.success = True
        mock_result.url = "https://example.com/"
        mock_result.markdown = "Content"
        mock_result.links = {"internal": [{"href": "https://example.com/"}]}  # Self-reference

        mock_crawler.arun_many.return_value = [mock_result]

        result = await crawl_recursive_internal_links(
            mock_crawler, ["https://example.com/"], max_depth=3
        )

        # Should only crawl once despite self-reference
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_crawl_recursive_exception_handling(self):
        """Test exception handling in recursive crawl."""
        mock_crawler = AsyncMock()
        mock_crawler.arun_many.side_effect = Exception("Crawl error")

        result = await crawl_recursive_internal_links(
            mock_crawler, ["https://example.com/"], max_depth=2
        )

        assert result == []


class TestResultAggregation:
    """Test crawl result aggregation."""

    def test_aggregate_crawl_stats_basic(self):
        """Test basic statistics aggregation."""
        docs = [
            {"url": "https://example.com/1", "markdown": "Content one"},
            {"url": "https://example.com/2", "markdown": "Content two here"},
        ]

        stats = aggregate_crawl_stats(docs)

        assert stats["total_pages"] == 2
        assert stats["total_chars"] > 0
        assert stats["total_words"] > 0
        assert stats["unique_urls"] == 2

    def test_aggregate_crawl_stats_empty(self):
        """Test aggregation with no documents."""
        stats = aggregate_crawl_stats([])

        assert stats["total_pages"] == 0
        assert stats["total_chars"] == 0
        assert stats["total_words"] == 0
        assert stats["avg_chars_per_page"] == 0
        assert stats["avg_words_per_page"] == 0
        assert stats["unique_urls"] == 0

    def test_aggregate_crawl_stats_duplicate_urls(self):
        """Test aggregation handles duplicate URLs."""
        docs = [
            {"url": "https://example.com/page", "markdown": "Content"},
            {"url": "https://example.com/page", "markdown": "More content"},
        ]

        stats = aggregate_crawl_stats(docs)

        assert stats["total_pages"] == 2  # Both documents counted
        assert stats["unique_urls"] == 1  # But only one unique URL

    def test_aggregate_crawl_stats_averages(self):
        """Test that averages are calculated correctly."""
        docs = [
            {"url": "https://example.com/1", "markdown": "a" * 100},
            {"url": "https://example.com/2", "markdown": "b" * 100},
        ]

        stats = aggregate_crawl_stats(docs)

        assert stats["avg_chars_per_page"] == 100
        # Word count is 1 per doc (single word of 100 chars)
        assert stats["avg_words_per_page"] == 1

    def test_aggregate_crawl_stats_missing_markdown(self):
        """Test aggregation handles missing markdown field."""
        docs = [
            {"url": "https://example.com/1", "markdown": "Content"},
            {"url": "https://example.com/2"},  # No markdown field
        ]

        stats = aggregate_crawl_stats(docs)

        # Should handle gracefully
        assert stats["total_pages"] == 2
        assert stats["total_chars"] > 0  # From first doc
