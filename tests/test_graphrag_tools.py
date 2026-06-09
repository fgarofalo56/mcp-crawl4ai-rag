"""
Tests for GraphRAG (Graph-augmented RAG) MCP tools.

This test suite covers:
- crawl_with_graph_extraction
- graphrag_query
- query_document_graph
- get_entity_context
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestCrawlWithGraphExtraction:
    """Test crawl_with_graph_extraction MCP tool."""

    @pytest.mark.asyncio
    async def test_graph_extraction_disabled(self, mock_context, mock_env_vars):
        """Test graph extraction when GraphRAG is disabled."""
        from src.tools.graphrag_tools import crawl_with_graph_extraction

        response = await crawl_with_graph_extraction(mock_context, "https://example.com")

        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_graph_extraction_success(
        self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars, monkeypatch
    ):
        """Test successful crawl with graph extraction."""
        from src.tools.graphrag_tools import crawl_with_graph_extraction

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        # Setup context
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client

        # Mock lazy GraphRAG components
        mock_validator_lazy = AsyncMock()
        mock_validator = AsyncMock()
        mock_validator_lazy.get_validator = AsyncMock(return_value=mock_validator)
        mock_context.request_context.lifespan_context.document_graph_validator = mock_validator_lazy

        mock_extractor_lazy = AsyncMock()
        mock_extractor = AsyncMock()
        mock_extraction_result = Mock()
        mock_extraction_result.error = None
        mock_extraction_result.entities = [{"name": "Entity1", "type": "Concept"}]
        mock_extraction_result.relationships = [
            {"source": "E1", "target": "E2", "type": "RELATES_TO"}
        ]
        mock_extractor.extract_entities_from_chunks = AsyncMock(return_value=mock_extraction_result)
        mock_extractor_lazy.get_extractor = AsyncMock(return_value=mock_extractor)
        mock_context.request_context.lifespan_context.document_entity_extractor = (
            mock_extractor_lazy
        )

        # Mock crawler result
        result = Mock()
        result.success = True
        result.markdown = "# Test Content\n\nThis is a test document."
        result.links = {"internal": [], "external": []}
        mock_crawler.arun = AsyncMock(return_value=result)

        # Mock validator store
        mock_validator.store_document_graph = AsyncMock()

        with patch("src.utils.add_documents_to_supabase"):
            with patch("src.utils.update_source_info"):
                with patch("src.utils.extract_source_summary", return_value="Summary"):
                    response = await crawl_with_graph_extraction(
                        mock_context, "https://example.com"
                    )

        data = json.loads(response)
        assert data["success"] is True
        assert data["url"] == "https://example.com"
        assert "graph_stats" in data
        assert data["graph_stats"]["entities"] == 1
        assert data["graph_stats"]["relationships"] == 1

    @pytest.mark.asyncio
    async def test_graph_extraction_handles_extraction_errors(
        self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars, monkeypatch
    ):
        """Test graph extraction handles entity extraction errors gracefully."""
        from src.tools.graphrag_tools import crawl_with_graph_extraction

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client

        # Mock lazy components
        mock_validator_lazy = AsyncMock()
        mock_validator = AsyncMock()
        mock_validator_lazy.get_validator = AsyncMock(return_value=mock_validator)
        mock_context.request_context.lifespan_context.document_graph_validator = mock_validator_lazy

        mock_extractor_lazy = AsyncMock()
        mock_extractor = AsyncMock()
        mock_extraction_result = Mock()
        mock_extraction_result.error = "Failed to extract entities"
        mock_extractor.extract_entities_from_chunks = AsyncMock(return_value=mock_extraction_result)
        mock_extractor_lazy.get_extractor = AsyncMock(return_value=mock_extractor)
        mock_context.request_context.lifespan_context.document_entity_extractor = (
            mock_extractor_lazy
        )

        # Mock crawler
        result = Mock()
        result.success = True
        result.markdown = "Content"
        result.links = {"internal": [], "external": []}
        mock_crawler.arun = AsyncMock(return_value=result)

        with patch("src.utils.add_documents_to_supabase"):
            with patch("src.utils.update_source_info"):
                with patch("src.utils.extract_source_summary", return_value="Summary"):
                    response = await crawl_with_graph_extraction(
                        mock_context, "https://example.com"
                    )

        data = json.loads(response)
        assert data["success"] is False
        assert "Failed to extract entities" in data["error"]


class TestGraphRAGQuery:
    """Test graphrag_query MCP tool."""

    @pytest.mark.asyncio
    async def test_graphrag_query_vector_only(
        self, mock_context, mock_supabase_client, mock_env_vars
    ):
        """Test GraphRAG query with vector search only."""
        from src.tools.graphrag_tools import graphrag_query

        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        mock_context.request_context.lifespan_context.document_graph_queries = None

        mock_results = [
            {"id": 1, "url": "https://example.com", "content": "Test content", "similarity": 0.9}
        ]

        with patch("src.utils.search_documents", return_value=mock_results):
            with patch("openai.AsyncOpenAI") as MockOpenAI:
                mock_client = AsyncMock()
                mock_response = AsyncMock()
                mock_response.choices = [Mock(message=Mock(content="Answer based on context"))]
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
                MockOpenAI.return_value = mock_client

                response = await graphrag_query(mock_context, "What is the test about?")

        data = json.loads(response)
        assert data["success"] is True
        assert "answer" in data
        assert len(data["documents"]) == 1

    @pytest.mark.asyncio
    async def test_graphrag_query_with_graph_enrichment(
        self, mock_context, mock_supabase_client, mock_env_vars, monkeypatch
    ):
        """Test GraphRAG query with graph enrichment enabled."""
        from src.tools.graphrag_tools import graphrag_query

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client

        # Mock lazy queries component
        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        mock_results = [
            {"id": 1, "url": "https://example.com", "content": "Test content", "similarity": 0.9}
        ]

        with patch("src.utils.search_documents", return_value=mock_results):
            with patch("openai.AsyncOpenAI") as MockOpenAI:
                mock_client = AsyncMock()
                mock_response = AsyncMock()
                mock_response.choices = [Mock(message=Mock(content="Enriched answer"))]
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
                MockOpenAI.return_value = mock_client

                response = await graphrag_query(
                    mock_context, "Complex question about relationships?", use_graph_enrichment=True
                )

        data = json.loads(response)
        assert data["success"] is True
        assert "answer" in data

    @pytest.mark.asyncio
    async def test_graphrag_query_no_results(self, mock_context, mock_supabase_client):
        """Test GraphRAG query when no documents found."""
        from src.tools.graphrag_tools import graphrag_query

        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client
        mock_context.request_context.lifespan_context.document_graph_queries = None

        with patch("src.utils.search_documents", return_value=[]):
            response = await graphrag_query(mock_context, "Query with no results")

        data = json.loads(response)
        assert data["success"] is True
        assert "No relevant documents found" in data["answer"]


class TestQueryDocumentGraph:
    """Test query_document_graph MCP tool."""

    @pytest.mark.asyncio
    async def test_query_document_graph_disabled(self, mock_context, mock_env_vars):
        """Test document graph query when GraphRAG is disabled."""
        from src.tools.graphrag_tools import query_document_graph

        response = await query_document_graph(mock_context, "MATCH (n:Document) RETURN n LIMIT 5")

        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_query_document_graph_success(self, mock_context, mock_env_vars, monkeypatch):
        """Test successful document graph query."""
        from src.tools.graphrag_tools import query_document_graph

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        # Mock lazy queries component
        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()
        mock_query_result = {
            "success": True,
            "results": [{"title": "Doc1", "entities": 5}, {"title": "Doc2", "entities": 3}],
            "count": 2,
        }
        mock_queries.query_graph = AsyncMock(return_value=mock_query_result)
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        response = await query_document_graph(
            mock_context,
            "MATCH (d:Document) RETURN d.title, size((d)-[:HAS_ENTITY]->()) as entities",
        )

        data = json.loads(response)
        assert data["success"] is True
        assert data["count"] == 2
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_query_document_graph_invalid_cypher(
        self, mock_context, mock_env_vars, monkeypatch
    ):
        """Test document graph query with invalid Cypher."""
        from src.tools.graphrag_tools import query_document_graph

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()
        mock_queries.query_graph = AsyncMock(side_effect=Exception("Invalid Cypher syntax"))
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        response = await query_document_graph(mock_context, "INVALID CYPHER")

        data = json.loads(response)
        assert data["success"] is False
        assert "Invalid Cypher" in data["error"]


class TestGetEntityContext:
    """Test get_entity_context MCP tool."""

    @pytest.mark.asyncio
    async def test_get_entity_context_disabled(self, mock_context, mock_env_vars):
        """Test entity context when GraphRAG is disabled."""
        from src.tools.graphrag_tools import get_entity_context

        response = await get_entity_context(mock_context, "Python")

        data = json.loads(response)
        assert data["success"] is False
        assert "disabled" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_entity_context_success(self, mock_context, mock_env_vars, monkeypatch):
        """Test successful entity context retrieval."""
        from src.tools.graphrag_tools import get_entity_context

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        # Mock lazy queries component
        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()

        mock_entity_context = Mock()
        mock_entity_context.entity_name = "Python"
        mock_entity_context.entity_type = "ProgrammingLanguage"
        mock_entity_context.direct_relationships = [
            {"type": "USES", "target": "Django"},
            {"type": "USES", "target": "Flask"},
        ]
        mock_entity_context.extended_relationships = [
            {"type": "FRAMEWORK_FOR", "source": "Django", "target": "Web Development"}
        ]
        mock_entity_context.related_documents = [
            {"title": "Python Tutorial", "url": "https://example.com/python"}
        ]

        mock_queries.get_entity_context = AsyncMock(return_value=mock_entity_context)
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        response = await get_entity_context(mock_context, "Python", max_hops=2)

        data = json.loads(response)
        assert data["success"] is True
        assert data["entity"]["name"] == "Python"
        assert data["entity"]["type"] == "ProgrammingLanguage"
        assert len(data["entity"]["direct_relationships"]) == 2
        assert len(data["entity"]["related_documents"]) == 1

    @pytest.mark.asyncio
    async def test_get_entity_context_not_found(self, mock_context, mock_env_vars, monkeypatch):
        """Test entity context when entity not found."""
        from src.tools.graphrag_tools import get_entity_context

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()
        mock_queries.get_entity_context = AsyncMock(return_value=None)
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        response = await get_entity_context(mock_context, "NonExistentEntity")

        data = json.loads(response)
        assert data["success"] is False
        assert "not found" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_entity_context_with_max_hops(self, mock_context, mock_env_vars, monkeypatch):
        """Test entity context with different max_hops values."""
        from src.tools.graphrag_tools import get_entity_context

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()

        mock_entity_context = Mock()
        mock_entity_context.entity_name = "FastAPI"
        mock_entity_context.entity_type = "Framework"
        mock_entity_context.direct_relationships = []
        mock_entity_context.extended_relationships = []
        mock_entity_context.related_documents = []

        mock_queries.get_entity_context = AsyncMock(return_value=mock_entity_context)
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        response = await get_entity_context(mock_context, "FastAPI", max_hops=3)

        data = json.loads(response)
        assert data["success"] is True

        # Verify max_hops was passed correctly
        mock_queries.get_entity_context.assert_called_once_with(entity_name="FastAPI", max_hops=3)


class TestGraphRAGIntegration:
    """Integration tests for GraphRAG workflow."""

    @pytest.mark.asyncio
    async def test_full_graphrag_workflow(
        self, mock_context, mock_crawler, mock_supabase_client, mock_env_vars, monkeypatch
    ):
        """Test complete GraphRAG workflow: crawl -> extract -> query."""
        from src.tools.graphrag_tools import crawl_with_graph_extraction, graphrag_query

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        # Setup all mock components
        mock_context.request_context.lifespan_context.crawler = mock_crawler
        mock_context.request_context.lifespan_context.supabase_client = mock_supabase_client

        # Mock GraphRAG lazy components
        mock_validator_lazy = AsyncMock()
        mock_validator = AsyncMock()
        mock_validator_lazy.get_validator = AsyncMock(return_value=mock_validator)
        mock_validator.store_document_graph = AsyncMock()
        mock_context.request_context.lifespan_context.document_graph_validator = mock_validator_lazy

        mock_extractor_lazy = AsyncMock()
        mock_extractor = AsyncMock()
        mock_extraction_result = Mock()
        mock_extraction_result.error = None
        mock_extraction_result.entities = [{"name": "GraphRAG", "type": "Technology"}]
        mock_extraction_result.relationships = [{"source": "E1", "target": "E2", "type": "USES"}]
        mock_extractor.extract_entities_from_chunks = AsyncMock(return_value=mock_extraction_result)
        mock_extractor_lazy.get_extractor = AsyncMock(return_value=mock_extractor)
        mock_context.request_context.lifespan_context.document_entity_extractor = (
            mock_extractor_lazy
        )

        mock_queries_lazy = AsyncMock()
        mock_queries = AsyncMock()
        mock_queries_lazy.get_queries = AsyncMock(return_value=mock_queries)
        mock_context.request_context.lifespan_context.document_graph_queries = mock_queries_lazy

        # Step 1: Crawl with graph extraction
        result = Mock()
        result.success = True
        result.markdown = "# GraphRAG Tutorial\n\nThis explains GraphRAG technology."
        result.links = {"internal": [], "external": []}
        mock_crawler.arun = AsyncMock(return_value=result)

        with patch("src.utils.add_documents_to_supabase"):
            with patch("src.utils.update_source_info"):
                with patch("src.utils.extract_source_summary", return_value="GraphRAG guide"):
                    crawl_response = await crawl_with_graph_extraction(
                        mock_context, "https://example.com/graphrag"
                    )

        crawl_data = json.loads(crawl_response)
        assert crawl_data["success"] is True
        assert crawl_data["graph_stats"]["entities"] == 1

        # Step 2: Query with graph enrichment
        mock_search_results = [
            {
                "id": 1,
                "url": "https://example.com/graphrag",
                "content": "GraphRAG content",
                "similarity": 0.95,
            }
        ]

        with patch("src.utils.search_documents", return_value=mock_search_results):
            with patch("openai.AsyncOpenAI") as MockOpenAI:
                mock_client = AsyncMock()
                mock_response = AsyncMock()
                mock_response.choices = [
                    Mock(message=Mock(content="GraphRAG combines graphs with RAG"))
                ]
                mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
                MockOpenAI.return_value = mock_client

                query_response = await graphrag_query(
                    mock_context, "What is GraphRAG?", use_graph_enrichment=True
                )

        query_data = json.loads(query_response)
        assert query_data["success"] is True
        assert "GraphRAG" in query_data["answer"]
