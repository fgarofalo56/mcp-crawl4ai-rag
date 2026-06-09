"""
Tests for batch processing helper functions in crawl_helpers module.

This module tests the three main helper functions extracted from
process_and_store_crawl_results:
- process_documentation_chunks
- update_sources_parallel
- extract_code_examples_from_documents
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, call, patch

import pytest


@pytest.fixture
def sample_crawl_results():
    """Sample crawl results for testing."""
    return [
        {
            "url": "https://example.com/page1",
            "markdown": "# Page 1\n\nThis is test content for page 1." * 100,
        },
        {
            "url": "https://example.com/page2",
            "markdown": "# Page 2\n\nThis is test content for page 2." * 100,
        },
    ]


@pytest.fixture
def sample_code_crawl_results():
    """Sample crawl results with code blocks for testing."""
    return [
        {
            "url": "https://example.com/tutorial",
            "markdown": """
# Tutorial

Here's how to use the API:

```python
def hello_world():
    print("Hello, World!")
```

That's all!
""",
        }
    ]


class TestProcessDocumentationChunks:
    """Tests for process_documentation_chunks function."""

    def test_basic_processing(self, sample_crawl_results):
        """Test basic document chunking and processing."""
        from src.crawl_helpers import process_documentation_chunks

        result = process_documentation_chunks(sample_crawl_results, chunk_size=500)

        # Unpack results
        (
            urls,
            chunk_numbers,
            contents,
            metadatas,
            url_to_full_document,
            source_content_map,
            source_word_counts,
            chunk_count,
        ) = result

        # Verify we got chunks
        assert chunk_count > 0
        assert len(urls) == chunk_count
        assert len(chunk_numbers) == chunk_count
        assert len(contents) == chunk_count
        assert len(metadatas) == chunk_count

    def test_metadata_structure(self, sample_crawl_results):
        """Test that metadata has correct structure."""
        from src.crawl_helpers import process_documentation_chunks

        result = process_documentation_chunks(sample_crawl_results, chunk_size=500)
        metadatas = result[3]

        # Check first metadata entry
        assert "chunk_index" in metadatas[0]
        assert "url" in metadatas[0]
        assert "source" in metadatas[0]
        assert "word_count" in metadatas[0]
        assert "char_count" in metadatas[0]

    def test_source_extraction(self, sample_crawl_results):
        """Test that sources are correctly extracted."""
        from src.crawl_helpers import process_documentation_chunks

        result = process_documentation_chunks(sample_crawl_results, chunk_size=500)
        source_content_map = result[5]
        source_word_counts = result[6]

        # Should have one source (example.com)
        assert "example.com" in source_content_map
        assert "example.com" in source_word_counts
        assert source_word_counts["example.com"] > 0

    def test_url_to_full_document_mapping(self, sample_crawl_results):
        """Test that full document mapping is created."""
        from src.crawl_helpers import process_documentation_chunks

        result = process_documentation_chunks(sample_crawl_results, chunk_size=500)
        url_to_full_document = result[4]

        # Check both URLs are mapped
        assert "https://example.com/page1" in url_to_full_document
        assert "https://example.com/page2" in url_to_full_document
        assert len(url_to_full_document["https://example.com/page1"]) > 0

    def test_chunk_size_respected(self):
        """Test that chunk size is respected."""
        from src.crawl_helpers import process_documentation_chunks

        # Create large content
        large_content = [{"url": "https://example.com/large", "markdown": "test content " * 1000}]

        result = process_documentation_chunks(large_content, chunk_size=500)
        contents = result[2]

        # Most chunks should be around or under chunk_size
        for content in contents:
            # Allow some flexibility for natural breaks
            assert len(content) <= 700  # 500 + 40% tolerance


class TestUpdateSourcesParallel:
    """Tests for update_sources_parallel function."""

    @patch("src.crawl_helpers.update_source_info")
    @patch("src.crawl_helpers.extract_source_summary")
    def test_parallel_update(self, mock_extract_summary, mock_update_info):
        """Test that sources are updated in parallel."""
        from src.crawl_helpers import update_sources_parallel

        mock_client = Mock()
        mock_extract_summary.return_value = "Test summary"

        source_content_map = {
            "example.com": "content1",
            "test.com": "content2",
        }
        source_word_counts = {
            "example.com": 100,
            "test.com": 200,
        }

        update_sources_parallel(mock_client, source_content_map, source_word_counts, max_workers=2)

        # Verify extract_source_summary was called for each source
        assert mock_extract_summary.call_count == 2

        # Verify update_source_info was called for each source
        assert mock_update_info.call_count == 2

    @patch("src.crawl_helpers.update_source_info")
    @patch("src.crawl_helpers.extract_source_summary")
    def test_correct_parameters(self, mock_extract_summary, mock_update_info):
        """Test that correct parameters are passed to helper functions."""
        from src.crawl_helpers import update_sources_parallel

        mock_client = Mock()
        mock_extract_summary.return_value = "Test summary"

        source_content_map = {"example.com": "content1"}
        source_word_counts = {"example.com": 100}

        update_sources_parallel(mock_client, source_content_map, source_word_counts)

        # Verify extract_source_summary received correct args
        mock_extract_summary.assert_called_once_with("example.com", "content1")

        # Verify update_source_info received correct args
        mock_update_info.assert_called_once_with(mock_client, "example.com", "Test summary", 100)


class TestExtractCodeExamplesFromDocuments:
    """Tests for extract_code_examples_from_documents function."""

    @patch("src.crawl_helpers.extract_code_blocks")
    def test_no_code_blocks(self, mock_extract_code):
        """Test behavior when no code blocks are found."""
        from src.crawl_helpers import extract_code_examples_from_documents

        mock_extract_code.return_value = []

        results = [{"url": "https://example.com", "markdown": "No code here"}]

        result = extract_code_examples_from_documents(results)

        # Should return empty lists
        code_urls, code_chunk_numbers, code_examples, code_summaries, code_metadatas = result
        assert len(code_urls) == 0
        assert len(code_chunk_numbers) == 0
        assert len(code_examples) == 0
        assert len(code_summaries) == 0
        assert len(code_metadatas) == 0

    @patch("src.crawl_helpers.extract_code_blocks")
    @patch("src.crawl_helpers.generate_code_example_summary")
    def test_code_extraction(self, mock_generate_summary, mock_extract_code):
        """Test code block extraction and processing."""
        from src.crawl_helpers import extract_code_examples_from_documents

        # Mock code blocks
        mock_extract_code.return_value = [
            {
                "code": 'print("Hello")',
                "context_before": "Example:",
                "context_after": "Done",
            }
        ]
        mock_generate_summary.return_value = "Print hello world"

        results = [{"url": "https://example.com/tutorial", "markdown": "code content"}]

        result = extract_code_examples_from_documents(results)

        code_urls, code_chunk_numbers, code_examples, code_summaries, code_metadatas = result

        # Verify results
        assert len(code_examples) == 1
        assert code_examples[0] == 'print("Hello")'
        assert code_summaries[0] == "Print hello world"
        assert code_urls[0] == "https://example.com/tutorial"

    @patch("src.crawl_helpers.extract_code_blocks")
    @patch("src.crawl_helpers.generate_code_example_summary")
    def test_metadata_structure(self, mock_generate_summary, mock_extract_code):
        """Test that code metadata has correct structure."""
        from src.crawl_helpers import extract_code_examples_from_documents

        mock_extract_code.return_value = [
            {
                "code": "test_code",
                "context_before": "before",
                "context_after": "after",
            }
        ]
        mock_generate_summary.return_value = "summary"

        results = [{"url": "https://example.com", "markdown": "content"}]

        result = extract_code_examples_from_documents(results)
        code_metadatas = result[4]

        # Check metadata structure
        assert len(code_metadatas) == 1
        metadata = code_metadatas[0]
        assert "chunk_index" in metadata
        assert "url" in metadata
        assert "source" in metadata
        assert "char_count" in metadata
        assert "word_count" in metadata

    @patch("src.crawl_helpers.extract_code_blocks")
    @patch("src.crawl_helpers.generate_code_example_summary")
    def test_multiple_documents(self, mock_generate_summary, mock_extract_code):
        """Test processing multiple documents with code blocks."""
        from src.crawl_helpers import extract_code_examples_from_documents

        # Return different code blocks for each document
        mock_extract_code.side_effect = [
            [
                {
                    "code": "code1",
                    "context_before": "",
                    "context_after": "",
                }
            ],
            [
                {
                    "code": "code2",
                    "context_before": "",
                    "context_after": "",
                }
            ],
        ]
        mock_generate_summary.side_effect = ["summary1", "summary2"]

        results = [
            {"url": "https://example.com/page1", "markdown": "content1"},
            {"url": "https://example.com/page2", "markdown": "content2"},
        ]

        result = extract_code_examples_from_documents(results)

        code_urls, code_chunk_numbers, code_examples, code_summaries, code_metadatas = result

        # Should have 2 code examples
        assert len(code_examples) == 2
        assert code_examples[0] == "code1"
        assert code_examples[1] == "code2"
        assert code_summaries[0] == "summary1"
        assert code_summaries[1] == "summary2"


class TestIntegration:
    """Integration tests for the helper functions."""

    @patch("src.crawl_helpers.extract_code_blocks")
    @patch("src.crawl_helpers.generate_code_example_summary")
    @patch("src.crawl_helpers.update_source_info")
    @patch("src.crawl_helpers.extract_source_summary")
    def test_full_workflow(
        self,
        mock_extract_summary,
        mock_update_info,
        mock_generate_summary,
        mock_extract_code,
    ):
        """Test complete workflow with all helper functions."""
        from src.crawl_helpers import (
            extract_code_examples_from_documents,
            process_documentation_chunks,
            update_sources_parallel,
        )

        # Setup mocks
        mock_extract_summary.return_value = "Source summary"
        mock_extract_code.return_value = []  # No code for simplicity

        # Sample data
        crawl_results = [
            {"url": "https://example.com/page1", "markdown": "# Test\n\n" + "word " * 200}
        ]

        # Step 1: Process documentation chunks
        (
            urls,
            chunk_numbers,
            contents,
            metadatas,
            url_to_full_document,
            source_content_map,
            source_word_counts,
            chunk_count,
        ) = process_documentation_chunks(crawl_results, chunk_size=500)

        assert chunk_count > 0
        assert len(source_content_map) == 1

        # Step 2: Update sources
        mock_client = Mock()
        update_sources_parallel(mock_client, source_content_map, source_word_counts)

        # Verify source updates were called
        assert mock_extract_summary.call_count == 1
        assert mock_update_info.call_count == 1

        # Step 3: Extract code examples
        result = extract_code_examples_from_documents(crawl_results)
        code_urls, _, code_examples, _, _ = result

        # No code blocks in this test
        assert len(code_examples) == 0
