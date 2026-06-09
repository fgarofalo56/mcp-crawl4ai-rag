"""Tests for utility functions (RAG, Supabase, embeddings, code extraction)."""

import os
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from src.utils import (
    add_code_examples_to_supabase,
    add_documents_to_supabase,
    create_embedding,
    create_embeddings_batch,
    extract_code_blocks,
    extract_source_summary,
    generate_code_example_summary,
    generate_contextual_embedding,
    get_supabase_client,
    search_code_examples,
    search_documents,
    update_source_info,
)


class TestSupabaseClient:
    """Test Supabase client initialization."""

    def test_get_supabase_client_success(self, mock_env_vars):
        """Test successful Supabase client creation."""
        with patch("src.utils.create_client") as mock_create:
            mock_create.return_value = Mock()

            client = get_supabase_client()

            assert client is not None
            mock_create.assert_called_once_with("https://test.supabase.co", "test-key-123")

    def test_get_supabase_client_missing_url(self, monkeypatch):
        """Test Supabase client creation with missing URL."""
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-key")

        with pytest.raises(ValueError, match="SUPABASE_URL"):
            get_supabase_client()

    def test_get_supabase_client_missing_key(self, monkeypatch):
        """Test Supabase client creation with missing key."""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

        with pytest.raises(ValueError, match="SUPABASE_SERVICE_KEY"):
            get_supabase_client()


class TestEmbeddings:
    """Test embedding creation functions."""

    def test_create_embeddings_batch_success(self, mock_openai_client, mock_env_vars):
        """Test successful batch embedding creation."""
        with patch("src.utils.client", mock_openai_client):
            texts = ["text 1", "text 2", "text 3"]
            embeddings = create_embeddings_batch(texts)

            assert len(embeddings) == 3
            assert all(len(emb) == 1536 for emb in embeddings)
            mock_openai_client.embeddings.create.assert_called_once()

    def test_create_embeddings_batch_empty(self):
        """Test batch embedding creation with empty list."""
        embeddings = create_embeddings_batch([])
        assert embeddings == []

    def test_create_embeddings_batch_retry(self, mock_openai_client, mock_env_vars):
        """Test batch embedding creation with retry logic."""
        with patch("src.utils.client", mock_openai_client):
            # First call fails, second succeeds
            mock_openai_client.embeddings.create.side_effect = [
                Exception("API Error"),
                Mock(data=[Mock(embedding=[0.1] * 1536)]),
            ]

            with patch("src.utils.time.sleep"):  # Skip sleep in tests
                embeddings = create_embeddings_batch(["text"])

                assert len(embeddings) == 1
                assert mock_openai_client.embeddings.create.call_count == 2

    def test_create_embedding_success(self, mock_openai_client, mock_env_vars):
        """Test single embedding creation."""
        with patch("src.utils.client", mock_openai_client):
            embedding = create_embedding("test text")

            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)

    def test_create_embedding_error_fallback(self, mock_env_vars):
        """Test single embedding creation with error fallback."""
        with patch("src.utils.create_embeddings_batch", return_value=[]):
            embedding = create_embedding("test text")

            # Should return zero embedding on failure
            assert len(embedding) == 1536
            assert all(x == 0.0 for x in embedding)

    def test_generate_contextual_embedding_success(self, mock_openai_client, mock_env_vars):
        """Test contextual embedding generation."""
        with patch("src.utils.client", mock_openai_client):
            full_doc = "This is a long document with context."
            chunk = "This is the chunk."

            contextual_text, success = generate_contextual_embedding(full_doc, chunk)

            assert success is True
            assert "---" in contextual_text
            assert chunk in contextual_text

    def test_generate_contextual_embedding_error(self, mock_env_vars):
        """Test contextual embedding generation with error."""
        with patch("src.utils.client") as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            chunk = "Test chunk"
            contextual_text, success = generate_contextual_embedding("doc", chunk)

            assert success is False
            assert contextual_text == chunk


class TestDocumentOperations:
    """Test document storage and search operations."""

    def test_add_documents_to_supabase_basic(self, mock_supabase_client, mock_env_vars):
        """Test adding documents to Supabase."""
        with patch("src.utils.create_embeddings_batch", return_value=[[0.1] * 1536]):
            add_documents_to_supabase(
                mock_supabase_client,
                urls=["https://example.com"],
                chunk_numbers=[0],
                contents=["Test content"],
                metadatas=[{"test": "meta"}],
                url_to_full_document={"https://example.com": "Full doc"},
            )

            # Verify delete and insert were called
            mock_supabase_client.table.assert_called()
            assert (
                mock_supabase_client.table().delete().in_().execute.called
                or mock_supabase_client.table().insert().execute.called
            )

    def test_add_documents_with_contextual_embeddings(
        self, mock_supabase_client, mock_env_vars, monkeypatch
    ):
        """Test adding documents with contextual embeddings enabled."""
        monkeypatch.setenv("USE_CONTEXTUAL_EMBEDDINGS", "true")

        with (
            patch("src.utils.create_embeddings_batch", return_value=[[0.1] * 1536]),
            patch(
                "src.utils.generate_contextual_embedding", return_value=("contextual text", True)
            ),
        ):
            add_documents_to_supabase(
                mock_supabase_client,
                urls=["https://example.com"],
                chunk_numbers=[0],
                contents=["Test content"],
                metadatas=[{"test": "meta"}],
                url_to_full_document={"https://example.com": "Full doc"},
            )

            # Verify contextual embedding was used
            assert mock_supabase_client.table().insert().execute.called

    def test_search_documents_success(
        self, mock_supabase_client, mock_env_vars, sample_search_results
    ):
        """Test document search."""
        mock_supabase_client.rpc().execute.return_value = Mock(data=sample_search_results)

        with patch("src.utils.create_embedding", return_value=[0.1] * 1536):
            results = search_documents(mock_supabase_client, query="test query", match_count=5)

            assert len(results) == 2
            assert results[0]["url"] == "https://example.com/page1"
            mock_supabase_client.rpc.assert_called_once()

    def test_search_documents_with_filter(self, mock_supabase_client, mock_env_vars):
        """Test document search with metadata filter."""
        mock_supabase_client.rpc().execute.return_value = Mock(data=[])

        with patch("src.utils.create_embedding", return_value=[0.1] * 1536):
            search_documents(
                mock_supabase_client,
                query="test query",
                match_count=5,
                filter_metadata={"source": "example.com"},
            )

            # Verify filter was passed
            call_args = mock_supabase_client.rpc.call_args
            assert "filter" in call_args[1]

    def test_search_documents_error(self, mock_supabase_client, mock_env_vars):
        """Test document search with error."""
        mock_supabase_client.rpc.side_effect = Exception("DB Error")

        with patch("src.utils.create_embedding", return_value=[0.1] * 1536):
            results = search_documents(mock_supabase_client, query="test query")

            assert results == []


class TestCodeExtraction:
    """Test code block extraction and processing."""

    def test_extract_code_blocks_with_language(self):
        """Test extracting code blocks with language specifiers."""
        markdown = """
# Test

```python
def hello():
    print("Hello")
```

```javascript
console.log("Hi");
```
"""
        blocks = extract_code_blocks(markdown, min_length=5)

        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert "def hello" in blocks[0]["code"]
        assert blocks[1]["language"] == "javascript"

    def test_extract_code_blocks_no_language(self):
        """Test extracting code blocks without language specifiers."""
        markdown = """
```
generic code block
with multiple lines
and no language
```
"""
        blocks = extract_code_blocks(markdown, min_length=5)

        assert len(blocks) == 1
        assert blocks[0]["language"] == ""
        assert "generic code block" in blocks[0]["code"]

    def test_extract_code_blocks_with_context(self):
        """Test code block context extraction."""
        markdown = "Before\n\n```python\ncode\n```\n\nAfter"
        blocks = extract_code_blocks(markdown, min_length=1)

        assert len(blocks) == 1
        assert "Before" in blocks[0]["context_before"]
        assert "After" in blocks[0]["context_after"]

    def test_extract_code_blocks_min_length(self):
        """Test code block minimum length filtering."""
        markdown = """
```python
short
```

```python
this is a much longer code block that should be included
because it exceeds the minimum length requirement
```
"""
        blocks = extract_code_blocks(markdown, min_length=50)

        assert len(blocks) == 1
        assert "longer code block" in blocks[0]["code"]

    def test_extract_code_blocks_empty(self):
        """Test extracting code blocks from empty content."""
        blocks = extract_code_blocks("")
        assert blocks == []

    def test_generate_code_example_summary_success(self, mock_openai_client, mock_env_vars):
        """Test code example summary generation."""
        with patch("src.utils.client", mock_openai_client):
            summary = generate_code_example_summary(
                code="def test(): pass",
                context_before="Example function",
                context_after="Usage notes",
            )

            assert summary == "Test summary"
            mock_openai_client.chat.completions.create.assert_called_once()

    def test_generate_code_example_summary_error(self, mock_env_vars):
        """Test code example summary generation with error."""
        with patch("src.utils.client") as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            summary = generate_code_example_summary("code", "before", "after")

            assert "demonstration purposes" in summary.lower()


class TestCodeExampleStorage:
    """Test code example storage operations."""

    def test_add_code_examples_to_supabase(self, mock_supabase_client, mock_env_vars):
        """Test adding code examples to Supabase."""
        with patch("src.utils.create_embeddings_batch", return_value=[[0.1] * 1536]):
            add_code_examples_to_supabase(
                mock_supabase_client,
                urls=["https://example.com"],
                chunk_numbers=[0],
                code_examples=["def test(): pass"],
                summaries=["Test function"],
                metadatas=[{"test": "meta"}],
            )

            # Verify operations were called
            assert mock_supabase_client.table().delete().eq().execute.called
            assert mock_supabase_client.table().insert().execute.called

    def test_add_code_examples_empty(self, mock_supabase_client):
        """Test adding empty code examples list."""
        add_code_examples_to_supabase(
            mock_supabase_client,
            urls=[],
            chunk_numbers=[],
            code_examples=[],
            summaries=[],
            metadatas=[],
        )

        # Should return early without calling table operations
        mock_supabase_client.table.assert_not_called()

    def test_search_code_examples_success(self, mock_supabase_client, mock_env_vars):
        """Test code example search."""
        mock_results = [
            {
                "id": 1,
                "url": "https://example.com",
                "content": "def test(): pass",
                "summary": "Test function",
                "similarity": 0.9,
            }
        ]
        mock_supabase_client.rpc().execute.return_value = Mock(data=mock_results)

        with patch("src.utils.create_embedding", return_value=[0.1] * 1536):
            results = search_code_examples(
                mock_supabase_client, query="test function", match_count=5
            )

            assert len(results) == 1
            assert results[0]["content"] == "def test(): pass"

    def test_search_code_examples_with_source_filter(self, mock_supabase_client, mock_env_vars):
        """Test code example search with source filter."""
        mock_supabase_client.rpc().execute.return_value = Mock(data=[])

        with patch("src.utils.create_embedding", return_value=[0.1] * 1536):
            search_code_examples(mock_supabase_client, query="test", source_id="example.com")

            # Verify source filter was passed
            call_args = mock_supabase_client.rpc.call_args
            assert "source_filter" in call_args[1]


class TestSourceOperations:
    """Test source information operations."""

    def test_update_source_info_new_source(self, mock_supabase_client):
        """Test creating new source info."""
        # Mock update returning no data (source doesn't exist)
        mock_supabase_client.table().update().eq().execute.return_value = Mock(data=[])

        update_source_info(
            mock_supabase_client, source_id="example.com", summary="Test source", word_count=1000
        )

        # Verify insert was called
        assert mock_supabase_client.table().insert().execute.called

    def test_update_source_info_existing_source(self, mock_supabase_client):
        """Test updating existing source info."""
        # Mock update returning data (source exists)
        mock_supabase_client.table().update().eq().execute.return_value = Mock(
            data=[{"source_id": "example.com"}]
        )

        update_source_info(
            mock_supabase_client,
            source_id="example.com",
            summary="Updated summary",
            word_count=2000,
        )

        # Verify update was called
        assert mock_supabase_client.table().update().eq().execute.called

    def test_extract_source_summary_success(self, mock_openai_client, mock_env_vars):
        """Test source summary extraction."""
        with patch("src.utils.client", mock_openai_client):
            summary = extract_source_summary(
                source_id="example.com", content="This is documentation for the example library."
            )

            assert summary == "Test summary"

    def test_extract_source_summary_empty_content(self, mock_env_vars):
        """Test source summary with empty content."""
        summary = extract_source_summary("example.com", "")

        assert "example.com" in summary

    def test_extract_source_summary_long_content(self, mock_openai_client, mock_env_vars):
        """Test source summary with very long content."""
        with patch("src.utils.client", mock_openai_client):
            long_content = "x" * 50000
            summary = extract_source_summary("example.com", long_content)

            # Should truncate content before sending to API
            assert summary == "Test summary"

    def test_extract_source_summary_error(self, mock_env_vars):
        """Test source summary extraction with error."""
        with patch("src.utils.client") as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            summary = extract_source_summary("example.com", "content")

            assert "example.com" in summary


class TestBatchOperations:
    """Test batch processing operations."""

    def test_add_documents_batch_processing(self, mock_supabase_client, mock_env_vars):
        """Test document batching."""
        with patch("src.utils.create_embeddings_batch", return_value=[[0.1] * 1536] * 25):
            # Add 25 documents (should process in 2 batches with batch_size=20)
            add_documents_to_supabase(
                mock_supabase_client,
                urls=["https://example.com"] * 25,
                chunk_numbers=list(range(25)),
                contents=["content"] * 25,
                metadatas=[{"i": i} for i in range(25)],
                url_to_full_document={"https://example.com": "doc"},
                batch_size=20,
            )

            # Verify multiple batch inserts
            assert mock_supabase_client.table().insert().execute.call_count >= 2

    def test_add_code_examples_batch_processing(self, mock_supabase_client, mock_env_vars):
        """Test code example batching."""
        with patch("src.utils.create_embeddings_batch", return_value=[[0.1] * 1536] * 25):
            # Add 25 code examples (should process in 2 batches with batch_size=20)
            add_code_examples_to_supabase(
                mock_supabase_client,
                urls=["https://example.com"] * 25,
                chunk_numbers=list(range(25)),
                code_examples=["code"] * 25,
                summaries=["summary"] * 25,
                metadatas=[{"i": i} for i in range(25)],
                batch_size=20,
            )

            # Verify multiple batch inserts
            assert mock_supabase_client.table().insert().execute.call_count >= 2
