"""
Integration tests for full GraphRAG functionality.

Tests the complete workflow:
1. Crawl with graph extraction (stores document_id in Supabase)
2. Query with graph enrichment (uses document_id to enrich results)
3. Verify the enrichment is working correctly
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestGraphRAGIntegration:
    """Test complete GraphRAG workflow."""

    @pytest.mark.asyncio
    async def test_crawl_stores_document_id_in_metadata(self):
        """Test that crawl_with_graph_extraction stores document_id in Supabase metadata."""
        # This tests the fix: document_id should be in metadata for GraphRAG linking

        from src.graphrag_utils import generate_document_id, prepare_supabase_data

        url = "https://example.com/test"
        chunks = ["chunk1", "chunk2"]
        source_id = "example.com"
        markdown = "# Test\n\nContent"
        document_id = generate_document_id(url)

        # Call prepare_supabase_data WITH document_id
        result = prepare_supabase_data(url, chunks, source_id, markdown, document_id)

        # Verify document_id is in ALL metadata entries
        assert len(result["metadatas"]) == 2
        for metadata in result["metadatas"]:
            assert "document_id" in metadata
            assert metadata["document_id"] == document_id
            assert metadata["source_id"] == source_id

    @pytest.mark.asyncio
    async def test_graphrag_query_extracts_document_ids(self):
        """Test that graphrag_query extracts document IDs from search results."""
        from src.tools.graphrag_tools import graphrag_query

        # Mock context
        mock_ctx = Mock()
        mock_supabase = Mock()
        mock_graph_queries_lazy = AsyncMock()
        mock_graph_queries = AsyncMock()

        # Mock search results with document_id in metadata
        mock_search_results = [
            {
                "url": "https://example.com/page1",
                "content": "Test content 1",
                "similarity": 0.9,
                "metadata": {"source_id": "example.com", "document_id": "doc123"},
            },
            {
                "url": "https://example.com/page2",
                "content": "Test content 2",
                "similarity": 0.8,
                "metadata": {"source_id": "example.com", "document_id": "doc456"},
            },
        ]

        # Mock enrichment result
        from knowledge_graphs.document_graph_queries import EntityContext, GraphEnrichmentResult

        mock_entity_context = EntityContext(
            entity_name="FastAPI",
            entity_type="Technology",
            description="Modern Python web framework",
            related_entities=[{"name": "Python", "type": "Technology", "relationship": "USES"}],
            relationships=[{"from": "FastAPI", "to": "Python", "type": "USES"}],
        )

        mock_enrichment = GraphEnrichmentResult(
            document_ids=["doc123", "doc456"],
            entity_contexts=[mock_entity_context],
            related_concepts=["FastAPI"],
            dependencies=[("FastAPI", "Python")],
            enrichment_text="## Knowledge Graph Context\n\n**FastAPI** (Technology)\n  Modern Python web framework",
        )

        # Mock graph queries
        mock_graph_queries.enrich_documents_with_graph = AsyncMock(return_value=mock_enrichment)
        mock_graph_queries_lazy.get_queries = AsyncMock(return_value=mock_graph_queries)

        # Setup context
        mock_ctx.request_context.lifespan_context.supabase_client = mock_supabase
        mock_ctx.request_context.lifespan_context.document_graph_queries = mock_graph_queries_lazy

        # Mock LLM response
        mock_llm_response = Mock()
        mock_llm_response.choices = [Mock()]
        mock_llm_response.choices[0].message = Mock()
        mock_llm_response.choices[0].message.content = "FastAPI is a modern Python web framework."

        with patch("src.tools.graphrag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.graphrag_tools.AsyncOpenAI") as mock_openai_class:
                mock_openai_instance = AsyncMock()
                mock_openai_instance.chat.completions.create = AsyncMock(
                    return_value=mock_llm_response
                )
                mock_openai_class.return_value = mock_openai_instance

                # Call graphrag_query
                result_json = await graphrag_query(
                    ctx=mock_ctx,
                    query="What is FastAPI?",
                    use_graph_enrichment=True,
                    max_entities=15,
                )

                result = json.loads(result_json)

                # Verify graph enrichment was used
                assert result["success"] is True
                assert result["graph_enrichment_used"] is True
                assert result["graph_enrichment"] is not None

                # Verify enrichment data
                enrichment = result["graph_enrichment"]
                assert enrichment["entities_found"] == 1
                assert "FastAPI" in enrichment["concepts"]
                assert len(enrichment["dependencies"]) == 1

                # Verify enrich_documents_with_graph was called with correct document IDs
                mock_graph_queries.enrich_documents_with_graph.assert_called_once()
                call_args = mock_graph_queries.enrich_documents_with_graph.call_args
                assert set(call_args[1]["document_ids"]) == {"doc123", "doc456"}

    @pytest.mark.asyncio
    async def test_graphrag_query_without_document_ids(self):
        """Test that graphrag_query handles documents without document_ids gracefully."""
        from src.tools.graphrag_tools import graphrag_query

        # Mock context
        mock_ctx = Mock()
        mock_supabase = Mock()
        mock_graph_queries_lazy = AsyncMock()
        mock_graph_queries = AsyncMock()

        # Mock search results WITHOUT document_id in metadata (old crawls)
        mock_search_results = [
            {
                "url": "https://example.com/page1",
                "content": "Test content 1",
                "similarity": 0.9,
                "metadata": {"source_id": "example.com"},  # No document_id!
            }
        ]

        # Mock graph queries
        mock_graph_queries_lazy.get_queries = AsyncMock(return_value=mock_graph_queries)

        # Setup context
        mock_ctx.request_context.lifespan_context.supabase_client = mock_supabase
        mock_ctx.request_context.lifespan_context.document_graph_queries = mock_graph_queries_lazy

        # Mock LLM response
        mock_llm_response = Mock()
        mock_llm_response.choices = [Mock()]
        mock_llm_response.choices[0].message = Mock()
        mock_llm_response.choices[0].message.content = "Answer based on available context."

        with patch("src.tools.graphrag_tools.search_documents", return_value=mock_search_results):
            with patch("src.tools.graphrag_tools.AsyncOpenAI") as mock_openai_class:
                mock_openai_instance = AsyncMock()
                mock_openai_instance.chat.completions.create = AsyncMock(
                    return_value=mock_llm_response
                )
                mock_openai_class.return_value = mock_openai_instance

                # Call graphrag_query
                result_json = await graphrag_query(
                    ctx=mock_ctx, query="What is FastAPI?", use_graph_enrichment=True
                )

                result = json.loads(result_json)

                # Verify fallback behavior
                assert result["success"] is True
                assert result["graph_enrichment_used"] is False
                assert result["graph_enrichment"] is None

                # Verify enrichment function was NOT called (no document IDs available)
                mock_graph_queries.enrich_documents_with_graph.assert_not_called()

    @pytest.mark.asyncio
    async def test_document_id_generation_consistency(self):
        """Test that document IDs are generated consistently for the same URL."""
        from src.graphrag_utils import generate_document_id

        url1 = "https://example.com/page"
        url2 = "https://example.com/page"
        url3 = "https://example.com/other-page"

        id1 = generate_document_id(url1)
        id2 = generate_document_id(url2)
        id3 = generate_document_id(url3)

        # Same URL should generate same ID
        assert id1 == id2

        # Different URL should generate different ID
        assert id1 != id3

        # IDs should be MD5 hashes (32 hex characters)
        assert len(id1) == 32
        assert all(c in "0123456789abcdef" for c in id1)
