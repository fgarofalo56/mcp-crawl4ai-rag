"""
Tests for search_utils module - code example search helpers.

This module tests all helper functions extracted from the search_code_examples function,
including validation, filtering, hybrid search, and result formatting.
"""

import json
import os
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import functions to test
from src.search_utils import (
    build_error_response,
    build_search_response,
    check_code_examples_enabled,
    execute_keyword_search,
    execute_vector_search,
    format_search_results,
    merge_vector_and_keyword_results,
    perform_hybrid_search,
    prepare_source_filter,
)


class TestCheckCodeExamplesEnabled:
    """Tests for check_code_examples_enabled function."""

    def test_enabled_when_env_var_true(self):
        """Test that code examples are enabled when USE_AGENTIC_RAG=true."""
        with patch.dict(os.environ, {"USE_AGENTIC_RAG": "true"}):
            enabled, error_msg = check_code_examples_enabled()

            assert enabled is True
            assert error_msg is None

    def test_disabled_when_env_var_false(self):
        """Test that code examples are disabled when USE_AGENTIC_RAG=false."""
        with patch.dict(os.environ, {"USE_AGENTIC_RAG": "false"}, clear=True):
            enabled, error_msg = check_code_examples_enabled()

            assert enabled is False
            assert error_msg is not None

            # Check error message structure
            error_json = json.loads(error_msg)
            assert error_json["success"] is False
            assert "disabled" in error_json["error"].lower()

    def test_disabled_when_env_var_missing(self):
        """Test that code examples are disabled when USE_AGENTIC_RAG is not set."""
        with patch.dict(os.environ, {}, clear=True):
            enabled, error_msg = check_code_examples_enabled()

            assert enabled is False
            assert error_msg is not None


class TestPrepareSourceFilter:
    """Tests for prepare_source_filter function."""

    def test_returns_filter_with_valid_source_id(self):
        """Test that filter is created with valid source ID."""
        filter_metadata = prepare_source_filter("example.com")

        assert filter_metadata is not None
        assert filter_metadata == {"source": "example.com"}

    def test_returns_none_with_empty_source_id(self):
        """Test that None is returned with empty source ID."""
        assert prepare_source_filter("") is None
        assert prepare_source_filter("   ") is None

    def test_returns_none_with_none_source_id(self):
        """Test that None is returned with None source ID."""
        assert prepare_source_filter(None) is None


class TestExecuteVectorSearch:
    """Tests for execute_vector_search function."""

    def test_executes_search_with_correct_parameters(self):
        """Test that vector search is executed with correct parameters."""
        mock_client = Mock()
        mock_search_function = Mock(return_value=[{"id": 1, "content": "test"}])

        results = execute_vector_search(
            mock_client, "test query", 5, {"source": "example.com"}, mock_search_function
        )

        # Verify search function was called with correct parameters
        mock_search_function.assert_called_once_with(
            client=mock_client,
            query="test query",
            match_count=5,
            filter_metadata={"source": "example.com"},
        )

        assert len(results) == 1
        assert results[0]["id"] == 1

    def test_handles_empty_results(self):
        """Test handling of empty search results."""
        mock_client = Mock()
        mock_search_function = Mock(return_value=[])

        results = execute_vector_search(mock_client, "test query", 5, None, mock_search_function)

        assert results == []


class TestExecuteKeywordSearch:
    """Tests for execute_keyword_search function."""

    def test_executes_keyword_search_without_filter(self):
        """Test keyword search without source filter."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{"id": 1, "content": "test content", "summary": "test summary"}]

        # Set up mock chain
        mock_query = Mock()
        mock_query.limit.return_value.execute.return_value = mock_response
        mock_select = Mock()
        mock_select.or_.return_value = mock_query
        mock_from = Mock()
        mock_from.select.return_value = mock_select
        mock_client.from_.return_value = mock_from

        results = execute_keyword_search(mock_client, "test", None, 5)

        assert len(results) == 1
        assert results[0]["id"] == 1

    def test_executes_keyword_search_with_filter(self):
        """Test keyword search with source filter."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [{"id": 1, "content": "test", "source_id": "example.com"}]

        # Set up mock chain with source filter
        mock_query = Mock()
        mock_query.eq.return_value.limit.return_value.execute.return_value = mock_response
        mock_select = Mock()
        mock_select.or_.return_value = mock_query
        mock_from = Mock()
        mock_from.select.return_value = mock_select
        mock_client.from_.return_value = mock_from

        results = execute_keyword_search(mock_client, "test", "example.com", 5)

        assert len(results) == 1

    def test_handles_empty_keyword_results(self):
        """Test handling of empty keyword search results."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = None

        # Set up mock chain
        mock_query = Mock()
        mock_query.limit.return_value.execute.return_value = mock_response
        mock_select = Mock()
        mock_select.or_.return_value = mock_query
        mock_from = Mock()
        mock_from.select.return_value = mock_select
        mock_client.from_.return_value = mock_from

        results = execute_keyword_search(mock_client, "test", None, 5)

        assert results == []


class TestMergeVectorAndKeywordResults:
    """Tests for merge_vector_and_keyword_results function."""

    def test_prioritizes_overlapping_results(self):
        """Test that results appearing in both searches are prioritized."""
        vector_results = [
            {
                "id": 1,
                "content": "test1",
                "similarity": 0.8,
                "url": "test.com",
                "summary": "summary1",
                "metadata": {},
                "source_id": "test.com",
            },
            {
                "id": 2,
                "content": "test2",
                "similarity": 0.7,
                "url": "test.com",
                "summary": "summary2",
                "metadata": {},
                "source_id": "test.com",
            },
        ]
        keyword_results = [
            {
                "id": 1,
                "url": "test.com",
                "content": "test1",
                "summary": "summary1",
                "chunk_number": 0,
                "metadata": {},
                "source_id": "test.com",
            },
            {
                "id": 3,
                "url": "test.com",
                "content": "test3",
                "summary": "summary3",
                "chunk_number": 0,
                "metadata": {},
                "source_id": "test.com",
            },
        ]

        merged = merge_vector_and_keyword_results(vector_results, keyword_results, 3)

        # First result should be the overlapping one with boosted similarity
        assert merged[0]["id"] == 1
        assert merged[0]["similarity"] > 0.8  # Should be boosted

    def test_adds_remaining_vector_results(self):
        """Test that non-overlapping vector results are added."""
        vector_results = [
            {"id": 1, "content": "test1", "similarity": 0.8},
            {"id": 2, "content": "test2", "similarity": 0.7},
        ]
        keyword_results = []

        merged = merge_vector_and_keyword_results(vector_results, keyword_results, 3)

        assert len(merged) == 2
        assert merged[0]["id"] == 1
        assert merged[1]["id"] == 2

    def test_adds_pure_keyword_matches(self):
        """Test that pure keyword matches are added when needed."""
        vector_results = [
            {"id": 1, "content": "test1", "similarity": 0.8},
        ]
        keyword_results = [
            {
                "id": 2,
                "url": "test.com",
                "content": "test2",
                "summary": "sum2",
                "chunk_number": 0,
                "metadata": {},
                "source_id": "test.com",
            },
        ]

        merged = merge_vector_and_keyword_results(vector_results, keyword_results, 2)

        assert len(merged) == 2
        assert merged[1]["id"] == 2
        assert merged[1]["similarity"] == 0.5  # Default for keyword-only

    def test_respects_match_count_limit(self):
        """Test that merged results respect match_count limit."""
        vector_results = [{"id": i, "content": f"test{i}", "similarity": 0.8} for i in range(10)]
        keyword_results = []

        merged = merge_vector_and_keyword_results(vector_results, keyword_results, 3)

        assert len(merged) == 3

    def test_handles_empty_inputs(self):
        """Test handling of empty input lists."""
        merged = merge_vector_and_keyword_results([], [], 5)
        assert merged == []


class TestPerformHybridSearch:
    """Tests for perform_hybrid_search function."""

    def test_combines_vector_and_keyword_searches(self):
        """Test that hybrid search combines both search types."""
        mock_client = Mock()
        mock_search_function = Mock(return_value=[{"id": 1, "content": "test1", "similarity": 0.8}])

        # Mock keyword search
        mock_response = Mock()
        mock_response.data = [
            {
                "id": 2,
                "url": "test.com",
                "content": "test2",
                "summary": "sum2",
                "chunk_number": 0,
                "metadata": {},
                "source_id": "test.com",
            }
        ]

        mock_query = Mock()
        mock_query.eq.return_value.limit.return_value.execute.return_value = mock_response
        mock_select = Mock()
        mock_select.or_.return_value = mock_query
        mock_from = Mock()
        mock_from.select.return_value = mock_select
        mock_client.from_.return_value = mock_from

        results = perform_hybrid_search(
            mock_client, "test query", "test.com", 2, {"source": "test.com"}, mock_search_function
        )

        # Should have results from both searches
        assert len(results) <= 2
        mock_search_function.assert_called_once()


class TestFormatSearchResults:
    """Tests for format_search_results function."""

    def test_formats_results_correctly(self):
        """Test that results are formatted with correct structure."""
        raw_results = [
            {
                "url": "http://example.com",
                "content": "code content",
                "summary": "code summary",
                "metadata": {"key": "value"},
                "source_id": "example.com",
                "similarity": 0.85,
            }
        ]

        formatted = format_search_results(raw_results)

        assert len(formatted) == 1
        assert formatted[0]["url"] == "http://example.com"
        assert formatted[0]["code"] == "code content"
        assert formatted[0]["summary"] == "code summary"
        assert formatted[0]["similarity"] == 0.85

    def test_includes_rerank_score_when_present(self):
        """Test that rerank score is included when available."""
        raw_results = [
            {
                "url": "http://example.com",
                "content": "code content",
                "summary": "summary",
                "metadata": {},
                "source_id": "example.com",
                "similarity": 0.85,
                "rerank_score": 0.95,
            }
        ]

        formatted = format_search_results(raw_results)

        assert formatted[0]["rerank_score"] == 0.95

    def test_handles_empty_results(self):
        """Test handling of empty results list."""
        formatted = format_search_results([])
        assert formatted == []


class TestBuildSearchResponse:
    """Tests for build_search_response function."""

    def test_builds_response_with_hybrid_search(self):
        """Test building response for hybrid search."""
        formatted_results = [
            {"url": "http://example.com", "code": "test", "summary": "test summary"}
        ]

        response_json = build_search_response(
            "test query",
            "example.com",
            formatted_results,
            use_hybrid_search=True,
            use_reranking=True,
            reranking_model_available=True,
        )

        response = json.loads(response_json)

        assert response["success"] is True
        assert response["query"] == "test query"
        assert response["source_filter"] == "example.com"
        assert response["search_mode"] == "hybrid"
        assert response["reranking_applied"] is True
        assert response["count"] == 1

    def test_builds_response_with_vector_search(self):
        """Test building response for vector-only search."""
        formatted_results = []

        response_json = build_search_response(
            "test query",
            None,
            formatted_results,
            use_hybrid_search=False,
            use_reranking=False,
            reranking_model_available=False,
        )

        response = json.loads(response_json)

        assert response["search_mode"] == "vector"
        assert response["reranking_applied"] is False
        assert response["count"] == 0


class TestBuildErrorResponse:
    """Tests for build_error_response function."""

    def test_builds_error_response_correctly(self):
        """Test building error response with exception."""
        error = ValueError("Test error message")

        response_json = build_error_response("test query", error)
        response = json.loads(response_json)

        assert response["success"] is False
        assert response["query"] == "test query"
        assert response["error"] == "Test error message"

    def test_handles_different_exception_types(self):
        """Test handling of different exception types."""
        errors = [
            RuntimeError("Runtime error"),
            KeyError("key_name"),
            TypeError("Type error"),
        ]

        for error in errors:
            response_json = build_error_response("query", error)
            response = json.loads(response_json)

            assert response["success"] is False
            assert "error" in response


# Integration-style tests
class TestSearchUtilsIntegration:
    """Integration tests combining multiple functions."""

    def test_full_hybrid_search_workflow(self):
        """Test a complete hybrid search workflow."""
        # Mock the entire workflow
        mock_client = Mock()

        # Mock vector search
        mock_search_function = Mock(
            return_value=[
                {
                    "id": 1,
                    "content": "test1",
                    "similarity": 0.8,
                    "url": "test.com",
                    "summary": "summary1",
                    "metadata": {},
                    "source_id": "test.com",
                }
            ]
        )

        # Mock keyword search
        mock_response = Mock()
        mock_response.data = [
            {
                "id": 1,
                "url": "test.com",
                "content": "test1",
                "summary": "summary1",
                "chunk_number": 0,
                "metadata": {},
                "source_id": "test.com",
            }
        ]

        mock_query = Mock()
        mock_query.eq.return_value.limit.return_value.execute.return_value = mock_response
        mock_select = Mock()
        mock_select.or_.return_value = mock_query
        mock_from = Mock()
        mock_from.select.return_value = mock_select
        mock_client.from_.return_value = mock_from

        # Execute hybrid search
        results = perform_hybrid_search(
            mock_client, "test query", "test.com", 5, {"source": "test.com"}, mock_search_function
        )

        # Format results
        formatted = format_search_results(results)

        # Build response
        response_json = build_search_response(
            "test query",
            "test.com",
            formatted,
            use_hybrid_search=True,
            use_reranking=False,
            reranking_model_available=False,
        )

        response = json.loads(response_json)

        assert response["success"] is True
        assert response["search_mode"] == "hybrid"
        assert len(response["results"]) > 0
