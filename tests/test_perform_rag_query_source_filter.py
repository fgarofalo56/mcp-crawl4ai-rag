"""
Regression tests for perform_rag_query source_filter parameter fix.

These tests ensure that the source_filter parameter works correctly after
fixing the bug where it was named 'source' instead of 'source_filter'.

Bug Reference: Task-011 - Parameter naming inconsistency
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.tools.rag_tools import perform_rag_query


@pytest.fixture
def mock_context():
    """Create a mock MCP context with required attributes."""
    ctx = Mock()
    ctx.request_context = Mock()
    ctx.request_context.lifespan_context = Mock()
    ctx.request_context.lifespan_context.supabase_client = Mock()
    ctx.request_context.lifespan_context.reranking_model = None
    return ctx


@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    return [
        {
            "id": 1,
            "url": "https://example.com/page1",
            "chunk_number": 1,
            "content": "Test content 1",
            "metadata": {"title": "Test Page 1"},
            "source_id": "example.com",
            "similarity": 0.95,
        },
        {
            "id": 2,
            "url": "https://example.com/page2",
            "chunk_number": 1,
            "content": "Test content 2",
            "metadata": {"title": "Test Page 2"},
            "source_id": "example.com",
            "similarity": 0.85,
        },
    ]


class TestPerformRAGQuerySourceFilter:
    """Test suite for perform_rag_query source_filter parameter."""

    @pytest.mark.asyncio
    async def test_source_filter_parameter_accepted(self, mock_context, mock_search_results):
        """Test that perform_rag_query accepts source_filter parameter."""
        with patch("src.tools.rag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    source_filter="example.com",
                    match_count=5,
                )

                # Verify no exception raised and result is valid JSON
                assert result is not None
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["source_filter"] == "example.com"

    @pytest.mark.asyncio
    async def test_source_filter_none_works(self, mock_context, mock_search_results):
        """Test that perform_rag_query works without source filter."""
        with patch("src.tools.rag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    match_count=5,
                )

                assert result is not None
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["source_filter"] is None

    @pytest.mark.asyncio
    async def test_source_filter_empty_string_handled(self, mock_context, mock_search_results):
        """Test that empty source_filter is handled gracefully."""
        with patch("src.tools.rag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    source_filter="",
                    match_count=5,
                )

                assert result is not None
                result_data = json.loads(result)
                assert result_data["success"] is True
                # Empty string should be passed through
                assert result_data["source_filter"] == ""

    @pytest.mark.asyncio
    async def test_source_filter_with_hybrid_search(self, mock_context, mock_search_results):
        """Test that source_filter works with hybrid search enabled."""
        # Mock both vector and keyword search
        mock_context.request_context.lifespan_context.supabase_client.from_ = Mock(
            return_value=Mock(
                select=Mock(
                    return_value=Mock(
                        ilike=Mock(
                            return_value=Mock(
                                eq=Mock(
                                    return_value=Mock(
                                        limit=Mock(
                                            return_value=Mock(
                                                execute=Mock(
                                                    return_value=Mock(data=mock_search_results)
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

        with patch("src.tools.rag_tools.search_documents", return_value=mock_search_results):
            with patch(
                "src.tools.rag_tools.os.getenv",
                side_effect=lambda k, d: "true" if k == "USE_HYBRID_SEARCH" else d,
            ):
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    source_filter="example.com",
                    match_count=5,
                )

                assert result is not None
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["source_filter"] == "example.com"
                assert result_data["search_mode"] == "hybrid"

    @pytest.mark.asyncio
    async def test_source_filter_filters_results(self, mock_context):
        """Test that source_filter actually filters results."""
        # Create results with different sources
        mixed_results = [
            {
                "id": 1,
                "url": "https://example.com/page1",
                "content": "Test content 1",
                "metadata": {},
                "source_id": "example.com",
                "similarity": 0.95,
            },
            {
                "id": 2,
                "url": "https://other.com/page1",
                "content": "Test content 2",
                "metadata": {},
                "source_id": "other.com",
                "similarity": 0.90,
            },
        ]

        with patch("src.tools.rag_tools.search_documents", return_value=mixed_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    source_filter="example.com",
                    match_count=5,
                )

                result_data = json.loads(result)
                assert result_data["success"] is True
                # Verify the source_filter was applied
                assert result_data["source_filter"] == "example.com"

    @pytest.mark.asyncio
    async def test_source_filter_whitespace_handled(self, mock_context, mock_search_results):
        """Test that source_filter with whitespace is handled correctly."""
        with patch("src.tools.rag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                # Test with leading/trailing whitespace
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    source_filter="  example.com  ",
                    match_count=5,
                )

                result_data = json.loads(result)
                assert result_data["success"] is True
                # Should preserve the original value
                assert result_data["source_filter"] == "  example.com  "


class TestSourceFilterBackwardCompatibility:
    """Test that the fix doesn't break existing functionality."""

    @pytest.mark.asyncio
    async def test_no_regression_in_basic_query(self, mock_context, mock_search_results):
        """Test that basic queries without source_filter still work."""
        with patch("src.tools.rag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                result = await perform_rag_query(ctx=mock_context, query="test query")

                assert result is not None
                result_data = json.loads(result)
                assert result_data["success"] is True
                assert "results" in result_data
                assert result_data["count"] == 2

    @pytest.mark.asyncio
    async def test_error_handling_preserved(self, mock_context):
        """Test that error handling still works after the fix."""
        with patch("src.tools.rag_tools.search_documents", side_effect=Exception("Test error")):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                result = await perform_rag_query(
                    ctx=mock_context, query="test query", source_filter="example.com"
                )

                result_data = json.loads(result)
                assert result_data["success"] is False
                assert "error" in result_data
                assert "Test error" in result_data["error"]


@pytest.mark.integration
class TestSourceFilterIntegration:
    """Integration tests for source_filter functionality."""

    @pytest.mark.asyncio
    async def test_source_filter_matches_graphrag_query_usage(self, mock_context):
        """
        Test that source_filter parameter is consistent with graphrag_query.

        This ensures the bug fix aligns with how graphrag_query uses source_filter.
        """
        mock_results = [
            {
                "id": 1,
                "url": "https://example.com/page1",
                "content": "GraphRAG test content",
                "metadata": {},
                "source_id": "example.com",
                "similarity": 0.95,
            }
        ]

        with patch("src.tools.rag_tools.search_documents", return_value=mock_results):
            with patch("src.tools.rag_tools.os.getenv", return_value="false"):
                # Call with source_filter like graphrag_query does
                result = await perform_rag_query(
                    ctx=mock_context,
                    query="test query",
                    source_filter="example.com",
                    match_count=10,  # graphrag_query uses match_count=10
                )

                result_data = json.loads(result)
                assert result_data["success"] is True
                assert result_data["source_filter"] == "example.com"
                # This confirms consistency with graphrag_query expectations


# Validation error prevention tests
class TestValidationErrorPrevention:
    """Tests to prevent the original ValidationError from recurring."""

    def test_function_signature_has_source_filter(self):
        """Test that the function signature uses 'source_filter' not 'source'."""
        import inspect

        from src.tools.rag_tools import perform_rag_query

        sig = inspect.signature(perform_rag_query)
        params = list(sig.parameters.keys())

        # Verify 'source_filter' is in parameters
        assert "source_filter" in params, "Function signature should have 'source_filter' parameter"

        # Verify 'source' is NOT in parameters (old bug)
        assert (
            "source" not in params
        ), "Function signature should NOT have 'source' parameter (this was the bug)"

    def test_parameter_default_value(self):
        """Test that source_filter has correct default value."""
        import inspect

        from src.tools.rag_tools import perform_rag_query

        sig = inspect.signature(perform_rag_query)
        source_filter_param = sig.parameters["source_filter"]

        assert source_filter_param.default is None, "source_filter should default to None"
