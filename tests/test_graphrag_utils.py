"""
Tests for graphrag_utils module.

Tests utility functions for GraphRAG operations including entity extraction,
storage, and response building.
"""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.graphrag_utils import (
    build_graphrag_crawl_response,
    extract_source_info,
    generate_document_id,
    initialize_graphrag_components,
    prepare_supabase_data,
    store_graphrag_entities,
    store_graphrag_relationships,
)


class TestGenerateDocumentId:
    """Tests for generate_document_id function."""

    def test_generate_document_id_consistency(self):
        """Test that same URL generates same ID."""
        url = "https://example.com/page"
        id1 = generate_document_id(url)
        id2 = generate_document_id(url)
        assert id1 == id2

    def test_generate_document_id_different_urls(self):
        """Test that different URLs generate different IDs."""
        id1 = generate_document_id("https://example.com/page1")
        id2 = generate_document_id("https://example.com/page2")
        assert id1 != id2

    def test_generate_document_id_format(self):
        """Test that generated ID is valid MD5 hash."""
        doc_id = generate_document_id("https://example.com")
        assert len(doc_id) == 32  # MD5 hash length
        assert all(c in "0123456789abcdef" for c in doc_id)


class TestExtractSourceInfo:
    """Tests for extract_source_info function."""

    def test_extract_source_info_with_title(self):
        """Test extracting source info with valid title."""
        url = "https://example.com/page"
        content = "# Main Title\n\nContent here"

        source_id, title = extract_source_info(url, content)

        assert source_id == "example.com"
        assert title == "# Main Title"

    def test_extract_source_info_empty_content(self):
        """Test extracting source info with empty content."""
        url = "https://example.com/page"
        content = ""

        source_id, title = extract_source_info(url, content)

        assert source_id == "example.com"
        assert title == "Untitled"

    def test_extract_source_info_long_title(self):
        """Test that title is truncated to 200 characters."""
        url = "https://example.com/page"
        long_title = "A" * 300
        content = f"{long_title}\n\nContent"

        source_id, title = extract_source_info(url, content)

        assert len(title) == 200
        assert title == "A" * 200

    def test_extract_source_info_no_netloc(self):
        """Test with URL that has no netloc (path only)."""
        url = "/local/path"
        content = "Title\nContent"

        source_id, title = extract_source_info(url, content)

        assert source_id == "/local/path"
        assert title == "Title"


@pytest.mark.asyncio
class TestStoreGraphragEntities:
    """Tests for store_graphrag_entities function."""

    async def test_store_entities_success(self):
        """Test successful entity storage."""
        # Mock document graph validator
        validator = Mock()
        validator.store_entities = AsyncMock(return_value=3)

        # Mock extraction result
        extraction_result = Mock()
        extraction_result.entities = [
            Mock(type="Technology", name="Python", description="Programming language", mentions=5),
            Mock(type="Framework", name="FastAPI", description="Web framework", mentions=3),
            Mock(type="Tool", name="Docker", description="Container platform", mentions=2),
        ]

        count = await store_graphrag_entities(
            validator, "doc123", extraction_result, extract_entities=True
        )

        assert count == 3
        validator.store_entities.assert_called_once()

    async def test_store_entities_disabled(self):
        """Test when entity extraction is disabled."""
        validator = Mock()
        validator.store_entities = AsyncMock()
        extraction_result = Mock()
        extraction_result.entities = [Mock()]

        count = await store_graphrag_entities(
            validator, "doc123", extraction_result, extract_entities=False
        )

        assert count == 0
        validator.store_entities.assert_not_called()

    async def test_store_entities_empty_list(self):
        """Test with no entities extracted."""
        validator = Mock()
        validator.store_entities = AsyncMock()
        extraction_result = Mock()
        extraction_result.entities = []

        count = await store_graphrag_entities(
            validator, "doc123", extraction_result, extract_entities=True
        )

        assert count == 0
        validator.store_entities.assert_not_called()


@pytest.mark.asyncio
class TestStoreGraphragRelationships:
    """Tests for store_graphrag_relationships function."""

    async def test_store_relationships_success(self):
        """Test successful relationship storage."""
        validator = Mock()
        validator.store_relationships = AsyncMock(return_value=2)

        extraction_result = Mock()
        extraction_result.relationships = [
            Mock(
                from_entity="Python",
                to_entity="FastAPI",
                relationship_type="uses",
                description="FastAPI uses Python",
                confidence=0.95,
            ),
            Mock(
                from_entity="FastAPI",
                to_entity="Docker",
                relationship_type="deploys_with",
                description="FastAPI deploys with Docker",
                confidence=0.90,
            ),
        ]

        count = await store_graphrag_relationships(
            validator, extraction_result, extract_relationships=True
        )

        assert count == 2
        validator.store_relationships.assert_called_once()

    async def test_store_relationships_disabled(self):
        """Test when relationship extraction is disabled."""
        validator = Mock()
        validator.store_relationships = AsyncMock()
        extraction_result = Mock()
        extraction_result.relationships = [Mock()]

        count = await store_graphrag_relationships(
            validator, extraction_result, extract_relationships=False
        )

        assert count == 0
        validator.store_relationships.assert_not_called()


class TestBuildGraphragCrawlResponse:
    """Tests for build_graphrag_crawl_response function."""

    def test_build_success_response(self):
        """Test building a successful response."""
        extraction_result = Mock()
        extraction_result.entities = [Mock(), Mock(), Mock()]
        extraction_result.relationships = [Mock(), Mock()]
        extraction_result.extraction_time = 1.5

        response_json = build_graphrag_crawl_response(
            success=True,
            url="https://example.com",
            source_id="example.com",
            chunks_count=10,
            total_words=5000,
            extraction_result=extraction_result,
            entities_stored=3,
            relationships_stored=2,
            document_id="abc123",
        )

        import json

        response = json.loads(response_json)

        assert response["success"] is True
        assert response["url"] == "https://example.com"
        assert response["source_id"] == "example.com"
        assert response["crawl_results"]["documents_stored"] == 10
        assert response["crawl_results"]["total_words"] == 5000
        assert response["graph_extraction"]["entities_found"] == 3
        assert response["graph_extraction"]["entities_stored"] == 3
        assert response["graph_extraction"]["relationships_found"] == 2
        assert response["graph_extraction"]["relationships_stored"] == 2
        assert response["document_id"] == "abc123"

    def test_build_error_response(self):
        """Test building an error response."""
        extraction_result = Mock()
        extraction_result.entities = []
        extraction_result.relationships = []

        response_json = build_graphrag_crawl_response(
            success=False,
            url="https://example.com",
            source_id="example.com",
            chunks_count=0,
            total_words=0,
            extraction_result=extraction_result,
            entities_stored=0,
            relationships_stored=0,
            document_id="",
            error="Failed to crawl URL",
        )

        import json

        response = json.loads(response_json)

        assert response["success"] is False
        assert response["error"] == "Failed to crawl URL"


class TestPrepareSupabaseData:
    """Tests for prepare_supabase_data function."""

    def test_prepare_supabase_data(self):
        """Test preparing data for Supabase storage."""
        url = "https://example.com/page"
        chunks = ["chunk1", "chunk2", "chunk3"]
        source_id = "example.com"
        markdown = "# Title\n\nFull content here"

        data = prepare_supabase_data(url, chunks, source_id, markdown)

        assert data["urls_list"] == [url, url, url]
        assert data["chunk_numbers"] == [0, 1, 2]
        assert len(data["metadatas"]) == 3
        assert all(m["source_id"] == source_id for m in data["metadatas"])
        assert data["url_to_full_document"][url] == markdown

    def test_prepare_supabase_data_empty_chunks(self):
        """Test with no chunks."""
        data = prepare_supabase_data("https://example.com", [], "example.com", "content")

        assert data["urls_list"] == []
        assert data["chunk_numbers"] == []
        assert data["metadatas"] == []


@pytest.mark.asyncio
class TestInitializeGraphragComponents:
    """Tests for initialize_graphrag_components function."""

    async def test_initialization_success(self):
        """Test successful GraphRAG components initialization."""
        # Mock context
        ctx = Mock()
        ctx.request_context.lifespan_context.crawler = Mock()
        ctx.request_context.lifespan_context.supabase_client = Mock()

        # Mock lazy loaders
        validator_lazy = Mock()
        validator_lazy.get_validator = AsyncMock(return_value=Mock())
        ctx.request_context.lifespan_context.document_graph_validator = validator_lazy

        extractor_lazy = Mock()
        extractor_lazy.get_extractor = AsyncMock(return_value=Mock())
        ctx.request_context.lifespan_context.document_entity_extractor = extractor_lazy

        # Mock environment
        import os

        os.environ["USE_GRAPHRAG"] = "true"

        components, error = await initialize_graphrag_components(ctx)

        assert error is None
        assert components is not None
        assert "crawler" in components
        assert "supabase_client" in components
        assert "document_graph_validator" in components
        assert "document_entity_extractor" in components

    async def test_initialization_graphrag_disabled(self):
        """Test when GraphRAG is disabled."""
        import os

        os.environ["USE_GRAPHRAG"] = "false"

        ctx = Mock()
        components, error = await initialize_graphrag_components(ctx)

        assert components is None
        assert "GraphRAG functionality is disabled" in error

    async def test_initialization_missing_components(self):
        """Test when components are not available."""
        import os

        os.environ["USE_GRAPHRAG"] = "true"

        ctx = Mock()
        ctx.request_context.lifespan_context.crawler = Mock()
        ctx.request_context.lifespan_context.supabase_client = Mock()
        ctx.request_context.lifespan_context.document_graph_validator = None
        ctx.request_context.lifespan_context.document_entity_extractor = None

        components, error = await initialize_graphrag_components(ctx)

        assert components is None
        assert "GraphRAG components not available" in error

    async def test_initialization_failed(self):
        """Test when initialization fails."""
        import os

        os.environ["USE_GRAPHRAG"] = "true"

        ctx = Mock()
        ctx.request_context.lifespan_context.crawler = Mock()
        ctx.request_context.lifespan_context.supabase_client = Mock()

        # Mock lazy loaders that return None
        validator_lazy = Mock()
        validator_lazy.get_validator = AsyncMock(return_value=None)
        ctx.request_context.lifespan_context.document_graph_validator = validator_lazy

        extractor_lazy = Mock()
        extractor_lazy.get_extractor = AsyncMock(return_value=Mock())
        ctx.request_context.lifespan_context.document_entity_extractor = extractor_lazy

        components, error = await initialize_graphrag_components(ctx)

        assert components is None
        assert "Failed to initialize GraphRAG components" in error
