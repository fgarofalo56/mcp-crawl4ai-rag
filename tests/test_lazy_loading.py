"""
Tests for lazy loading initialization of expensive components.

This test suite validates the lazy loading mechanism for:
- Reranking model (CrossEncoder)
- Neo4j knowledge graph components
- GraphRAG components

Ensures fast server startup (<5s) by deferring initialization until first use.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


class TestLazyReranker:
    """Test LazyReranker lazy loading."""

    def test_lazy_reranker_creation_is_instant(self):
        """Test that creating LazyReranker doesn't load the model."""
        from src.initialization_utils import LazyReranker

        start_time = time.time()
        reranker = LazyReranker()
        elapsed = time.time() - start_time

        # Should be instant (no model loading)
        assert elapsed < 0.1
        assert reranker._model is None
        assert reranker._device is None

    def test_lazy_reranker_loads_on_first_use(self):
        """Test that model loads on first predict() call."""
        from src.initialization_utils import LazyReranker

        with patch("sentence_transformers.CrossEncoder") as MockEncoder:
            with patch("torch.cuda.is_available", return_value=False):
                mock_model = Mock()
                mock_model.predict.return_value = [0.9, 0.8]
                MockEncoder.return_value = mock_model

                reranker = LazyReranker()
                assert reranker._model is None

                # First call loads model
                result = reranker.predict([("query", "doc1"), ("query", "doc2")])

                assert reranker._model is not None
                assert MockEncoder.called
                assert result == [0.9, 0.8]

    def test_lazy_reranker_caches_model(self):
        """Test that model is only loaded once."""
        from src.initialization_utils import LazyReranker

        with patch("sentence_transformers.CrossEncoder") as MockEncoder:
            with patch("torch.cuda.is_available", return_value=False):
                mock_model = Mock()
                mock_model.predict.return_value = [0.9]
                MockEncoder.return_value = mock_model

                reranker = LazyReranker()

                # First call
                reranker.predict([("query", "doc")])
                assert MockEncoder.call_count == 1

                # Second call - should NOT load again
                reranker.predict([("query", "doc")])
                assert MockEncoder.call_count == 1  # Still 1

    def test_lazy_reranker_detects_gpu(self):
        """Test that LazyReranker detects GPU correctly."""
        from src.initialization_utils import LazyReranker

        with patch("sentence_transformers.CrossEncoder") as MockEncoder:
            with patch("torch.cuda.is_available", return_value=True):
                with patch("torch.cuda.get_device_name", return_value="NVIDIA RTX 4090"):
                    mock_model = Mock()
                    mock_model.predict.return_value = [0.9]
                    MockEncoder.return_value = mock_model

                    reranker = LazyReranker()
                    reranker.predict([("query", "doc")])

                    assert reranker._device == "cuda"
                    MockEncoder.assert_called_once_with(
                        "cross-encoder/ms-marco-MiniLM-L-6-v2", device="cuda"
                    )

    def test_lazy_reranker_falls_back_on_error(self):
        """Test that LazyReranker returns neutral scores on error."""
        from src.initialization_utils import LazyReranker

        with (
            patch("sentence_transformers.CrossEncoder", side_effect=Exception("Model load failed")),
            patch("torch.cuda.is_available", return_value=False),
        ):
            reranker = LazyReranker()
            result = reranker.predict([("q", "d1"), ("q", "d2")])

            # Should return neutral scores
            assert result == [0.5, 0.5]


class TestLazyKnowledgeGraphComponents:
    """Test lazy loading of Neo4j knowledge graph components."""

    @pytest.mark.asyncio
    async def test_lazy_kg_creation_is_instant(self):
        """Test that creating lazy KG components is instant."""
        from src.initialization_utils import LazyKnowledgeGraphComponents

        start_time = time.time()
        lazy_kg = LazyKnowledgeGraphComponents()
        elapsed = time.time() - start_time

        # Should be instant (no Neo4j connection)
        assert elapsed < 0.1
        assert lazy_kg.validator is None
        assert lazy_kg.extractor is None
        assert lazy_kg._initialized is False

    @pytest.mark.asyncio
    async def test_lazy_kg_initializes_on_first_use(self, mock_env_vars):
        """Test that KG components initialize on first get_validator()."""
        from src.initialization_utils import LazyKnowledgeGraphComponents

        with patch("src.initialization_utils.KnowledgeGraphValidator") as MockValidator:
            with patch("src.initialization_utils.DirectNeo4jExtractor") as MockExtractor:
                mock_validator = AsyncMock()
                mock_validator.initialize = AsyncMock()
                MockValidator.return_value = mock_validator

                mock_extractor = AsyncMock()
                mock_extractor.initialize = AsyncMock()
                MockExtractor.return_value = mock_extractor

                lazy_kg = LazyKnowledgeGraphComponents()

                # Should not be initialized yet
                assert lazy_kg._initialized is False

                # First call initializes
                validator = await lazy_kg.get_validator()

                assert lazy_kg._initialized is True
                assert mock_validator.initialize.called
                assert validator is not None

    @pytest.mark.asyncio
    async def test_lazy_kg_caches_components(self, mock_env_vars):
        """Test that KG components are only initialized once."""
        from src.initialization_utils import LazyKnowledgeGraphComponents

        with patch("src.initialization_utils.KnowledgeGraphValidator") as MockValidator:
            with patch("src.initialization_utils.DirectNeo4jExtractor") as MockExtractor:
                mock_validator = AsyncMock()
                mock_validator.initialize = AsyncMock()
                MockValidator.return_value = mock_validator

                mock_extractor = AsyncMock()
                mock_extractor.initialize = AsyncMock()
                MockExtractor.return_value = mock_extractor

                lazy_kg = LazyKnowledgeGraphComponents()

                # Multiple calls
                await lazy_kg.get_validator()
                await lazy_kg.get_extractor()
                await lazy_kg.get_validator()  # Again

                # Should only initialize once
                assert MockValidator.call_count == 1
                assert MockExtractor.call_count == 1

    @pytest.mark.asyncio
    async def test_lazy_kg_handles_initialization_errors(self, mock_env_vars):
        """Test that KG handles initialization errors gracefully."""
        from src.initialization_utils import LazyKnowledgeGraphComponents

        with (
            patch(
                "src.initialization_utils.KnowledgeGraphValidator",
                side_effect=Exception("Connection refused"),
            ),
            patch("src.initialization_utils.DirectNeo4jExtractor") as MockExtractor,
        ):
            mock_extractor = AsyncMock()
            mock_extractor.initialize = AsyncMock()
            MockExtractor.return_value = mock_extractor

            lazy_kg = LazyKnowledgeGraphComponents()

            # Should not raise, just log error
            validator = await lazy_kg.get_validator()

            # Validator failed, but extractor should still work
            assert validator is None

            extractor = await lazy_kg.get_extractor()
            assert extractor is not None


class TestLazyGraphRAGComponents:
    """Test lazy loading of GraphRAG components."""

    @pytest.mark.asyncio
    async def test_lazy_graphrag_creation_is_instant(self):
        """Test that creating lazy GraphRAG components is instant."""
        from src.initialization_utils import LazyGraphRAGComponents

        start_time = time.time()
        lazy_gr = LazyGraphRAGComponents()
        elapsed = time.time() - start_time

        # Should be instant
        assert elapsed < 0.1
        assert lazy_gr.validator is None
        assert lazy_gr.extractor is None
        assert lazy_gr.queries is None
        assert lazy_gr._initialized is False

    @pytest.mark.asyncio
    async def test_lazy_graphrag_initializes_on_first_use(self, mock_env_vars):
        """Test that GraphRAG components initialize on first use."""
        from src.initialization_utils import LazyGraphRAGComponents

        with patch("src.initialization_utils.DocumentGraphValidator") as MockValidator:
            with patch("src.initialization_utils.DocumentGraphQueries") as MockQueries:
                with patch("src.initialization_utils.DocumentEntityExtractor") as MockExtractor:
                    mock_validator = AsyncMock()
                    mock_validator.initialize = AsyncMock()
                    MockValidator.return_value = mock_validator

                    mock_queries = AsyncMock()
                    mock_queries.initialize = AsyncMock()
                    MockQueries.return_value = mock_queries

                    mock_extractor = Mock()
                    MockExtractor.return_value = mock_extractor

                    lazy_gr = LazyGraphRAGComponents()

                    # First call initializes all components
                    queries = await lazy_gr.get_queries()

                    assert lazy_gr._initialized is True
                    assert queries is not None
                    assert mock_queries.initialize.called

    @pytest.mark.asyncio
    async def test_lazy_graphrag_uses_azure_openai(self, mock_env_vars, monkeypatch):
        """Test that GraphRAG correctly uses Azure OpenAI."""
        from src.initialization_utils import LazyGraphRAGComponents

        # Set Azure env vars
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("DEPLOYMENT", "gpt-4o-mini")

        with patch("src.initialization_utils.DocumentGraphValidator") as MockValidator:
            with patch("src.initialization_utils.DocumentGraphQueries") as MockQueries:
                with patch("src.initialization_utils.DocumentEntityExtractor") as MockExtractor:
                    mock_validator = AsyncMock()
                    mock_validator.initialize = AsyncMock()
                    MockValidator.return_value = mock_validator

                    mock_queries = AsyncMock()
                    mock_queries.initialize = AsyncMock()
                    MockQueries.return_value = mock_queries

                    mock_extractor = Mock()
                    MockExtractor.return_value = mock_extractor

                    lazy_gr = LazyGraphRAGComponents()
                    await lazy_gr.get_extractor()

                    # Should use Azure endpoint
                    MockExtractor.assert_called_once()
                    call_kwargs = MockExtractor.call_args[1]
                    assert "azure_openai_endpoint" in call_kwargs
                    assert call_kwargs["azure_openai_endpoint"] == "https://test.openai.azure.com"


class TestStartupPerformance:
    """Test that lazy loading achieves fast startup times."""

    @pytest.mark.asyncio
    async def test_initialize_reranker_is_fast(self, monkeypatch):
        """Test that initialize_reranker() is instant."""
        from src.initialization_utils import initialize_reranker

        monkeypatch.setenv("USE_RERANKING", "true")

        start_time = time.time()
        reranker = initialize_reranker()
        elapsed = time.time() - start_time

        # Should be instant (returns LazyReranker, doesn't load model)
        assert elapsed < 0.1
        assert reranker is not None

    @pytest.mark.asyncio
    async def test_initialize_knowledge_graph_is_fast(self, mock_env_vars, monkeypatch):
        """Test that initialize_knowledge_graph() is instant."""
        from src.initialization_utils import initialize_knowledge_graph

        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")

        start_time = time.time()
        validator, extractor = await initialize_knowledge_graph()
        elapsed = time.time() - start_time

        # Should be instant (returns lazy wrapper, doesn't connect to Neo4j)
        assert elapsed < 0.5
        assert validator is not None
        assert extractor is not None

    @pytest.mark.asyncio
    async def test_initialize_graphrag_is_fast(self, mock_env_vars, monkeypatch):
        """Test that initialize_graphrag() is instant."""
        from src.initialization_utils import initialize_graphrag

        monkeypatch.setenv("USE_GRAPHRAG", "true")

        start_time = time.time()
        validator, extractor, queries = await initialize_graphrag()
        elapsed = time.time() - start_time

        # Should be instant
        assert elapsed < 0.5
        assert validator is not None
        assert extractor is not None
        assert queries is not None

    @pytest.mark.asyncio
    async def test_full_server_startup_under_5_seconds(self, mock_env_vars, monkeypatch):
        """Test that full server startup completes in <5 seconds."""
        monkeypatch.setenv("USE_RERANKING", "true")
        monkeypatch.setenv("USE_KNOWLEDGE_GRAPH", "true")
        monkeypatch.setenv("USE_GRAPHRAG", "true")

        from src.initialization_utils import (
            initialize_graphrag,
            initialize_knowledge_graph,
            initialize_reranker,
            initialize_supabase,
        )

        with patch("src.initialization_utils.get_supabase_client", return_value=Mock()):
            start_time = time.time()

            # Simulate full initialization sequence
            supabase = initialize_supabase()
            reranker = initialize_reranker()
            kg_validator, kg_extractor = await initialize_knowledge_graph()
            gr_validator, gr_extractor, gr_queries = await initialize_graphrag()

            elapsed = time.time() - start_time

            # Should complete in under 5 seconds (with lazy loading)
            assert elapsed < 5.0

            # All components should be available (as lazy wrappers)
            assert supabase is not None
            assert reranker is not None
            assert kg_validator is not None
            assert gr_queries is not None


class TestCleanupFunctions:
    """Test cleanup of lazy-loaded components."""

    @pytest.mark.asyncio
    async def test_cleanup_knowledge_graph_with_lazy_components(self):
        """Test cleanup works with lazy KG components."""
        from src.initialization_utils import LazyKnowledgeGraphComponents, cleanup_knowledge_graph

        lazy_kg = LazyKnowledgeGraphComponents()

        # Mock initialized components
        mock_validator = AsyncMock()
        mock_validator.close = AsyncMock()
        lazy_kg.validator = mock_validator
        lazy_kg._initialized = True

        mock_extractor = AsyncMock()
        mock_extractor.close = AsyncMock()
        lazy_kg.extractor = mock_extractor

        # Cleanup should call close on both
        await cleanup_knowledge_graph(lazy_kg, lazy_kg)

        assert mock_validator.close.called
        assert mock_extractor.close.called

    @pytest.mark.asyncio
    async def test_cleanup_graphrag_with_lazy_components(self):
        """Test cleanup works with lazy GraphRAG components."""
        from src.initialization_utils import LazyGraphRAGComponents, cleanup_graphrag

        lazy_gr = LazyGraphRAGComponents()

        # Mock initialized components
        mock_validator = AsyncMock()
        mock_validator.close = AsyncMock()
        lazy_gr.validator = mock_validator
        lazy_gr._initialized = True

        mock_queries = AsyncMock()
        mock_queries.close = AsyncMock()
        lazy_gr.queries = mock_queries

        # Cleanup should call close on both
        await cleanup_graphrag(lazy_gr, lazy_gr)

        assert mock_validator.close.called
        assert mock_queries.close.called

    @pytest.mark.asyncio
    async def test_cleanup_handles_uninitialized_components(self):
        """Test cleanup handles components that were never initialized."""
        from src.initialization_utils import LazyKnowledgeGraphComponents, cleanup_knowledge_graph

        lazy_kg = LazyKnowledgeGraphComponents()

        # Components never initialized (still None)
        assert lazy_kg.validator is None
        assert lazy_kg.extractor is None

        # Cleanup should not raise
        await cleanup_knowledge_graph(lazy_kg, lazy_kg)

        # Should complete without error
        assert True
