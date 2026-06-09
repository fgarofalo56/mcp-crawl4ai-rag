"""
Tests for lazy loading component cleanup functionality.

This test module verifies that the LazyKnowledgeGraphComponents and
LazyGraphRAGComponents classes properly handle initialization and cleanup
of their underlying Neo4j connections.

Bug Fix: Addresses issue where cleanup functions were calling close() on
lazy wrapper objects that didn't have close() methods, causing AttributeError.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add src directory to path for imports
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from initialization_utils import (
    LazyGraphRAGComponents,
    LazyKnowledgeGraphComponents,
    cleanup_graphrag,
    cleanup_knowledge_graph,
)


class TestLazyKnowledgeGraphComponents:
    """Test LazyKnowledgeGraphComponents lazy loading and cleanup."""

    def test_initialization(self):
        """Test that lazy wrapper initializes with None components."""
        lazy_kg = LazyKnowledgeGraphComponents()

        assert lazy_kg.validator is None
        assert lazy_kg.extractor is None
        assert lazy_kg._initialized is False
        assert lazy_kg._initializing is False

    @pytest.mark.asyncio
    async def test_close_without_initialization(self):
        """Test that close() works when components were never initialized."""
        lazy_kg = LazyKnowledgeGraphComponents()

        # Should not raise any errors
        await lazy_kg.close()

        # Components should still be None
        assert lazy_kg.validator is None
        assert lazy_kg.extractor is None

    @pytest.mark.asyncio
    async def test_close_with_mock_components(self):
        """Test that close() properly closes initialized components."""
        lazy_kg = LazyKnowledgeGraphComponents()

        # Mock the initialized state and components
        lazy_kg._initialized = True
        lazy_kg.validator = AsyncMock()
        lazy_kg.validator.close = AsyncMock()
        lazy_kg.extractor = AsyncMock()
        lazy_kg.extractor.close = AsyncMock()

        # Close should call close() on both components
        await lazy_kg.close()

        lazy_kg.validator.close.assert_awaited_once()
        lazy_kg.extractor.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_handles_missing_close_method(self):
        """Test that close() handles components without close() methods."""
        lazy_kg = LazyKnowledgeGraphComponents()

        # Mock initialized state with components that don't have close()
        lazy_kg._initialized = True
        lazy_kg.validator = Mock()  # No close method
        lazy_kg.extractor = Mock()  # No close method

        # Should not raise AttributeError
        await lazy_kg.close()

    @pytest.mark.asyncio
    async def test_close_handles_exceptions(self):
        """Test that close() handles exceptions gracefully."""
        lazy_kg = LazyKnowledgeGraphComponents()

        # Mock initialized state
        lazy_kg._initialized = True
        lazy_kg.validator = AsyncMock()
        lazy_kg.validator.close = AsyncMock(side_effect=Exception("Connection error"))
        lazy_kg.extractor = AsyncMock()
        lazy_kg.extractor.close = AsyncMock()

        # Should not raise exception, should continue to close extractor
        await lazy_kg.close()

        lazy_kg.validator.close.assert_awaited_once()
        lazy_kg.extractor.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_with_none_components(self):
        """Test that close() handles None components (partial initialization)."""
        lazy_kg = LazyKnowledgeGraphComponents()

        # Mock initialized state with only one component
        lazy_kg._initialized = True
        lazy_kg.validator = AsyncMock()
        lazy_kg.validator.close = AsyncMock()
        lazy_kg.extractor = None  # Failed to initialize

        # Should not raise error
        await lazy_kg.close()

        lazy_kg.validator.close.assert_awaited_once()


class TestLazyGraphRAGComponents:
    """Test LazyGraphRAGComponents lazy loading and cleanup."""

    def test_initialization(self):
        """Test that lazy wrapper initializes with None components."""
        lazy_graphrag = LazyGraphRAGComponents()

        assert lazy_graphrag.validator is None
        assert lazy_graphrag.extractor is None
        assert lazy_graphrag.queries is None
        assert lazy_graphrag._initialized is False
        assert lazy_graphrag._initializing is False

    @pytest.mark.asyncio
    async def test_close_without_initialization(self):
        """Test that close() works when components were never initialized."""
        lazy_graphrag = LazyGraphRAGComponents()

        # Should not raise any errors
        await lazy_graphrag.close()

        # Components should still be None
        assert lazy_graphrag.validator is None
        assert lazy_graphrag.extractor is None
        assert lazy_graphrag.queries is None

    @pytest.mark.asyncio
    async def test_close_with_mock_components(self):
        """Test that close() properly closes initialized components."""
        lazy_graphrag = LazyGraphRAGComponents()

        # Mock the initialized state and components
        lazy_graphrag._initialized = True
        lazy_graphrag.validator = AsyncMock()
        lazy_graphrag.validator.close = AsyncMock()
        lazy_graphrag.extractor = AsyncMock()
        lazy_graphrag.extractor.close = AsyncMock()
        lazy_graphrag.queries = AsyncMock()
        lazy_graphrag.queries.close = AsyncMock()

        # Close should call close() on all components
        await lazy_graphrag.close()

        lazy_graphrag.validator.close.assert_awaited_once()
        lazy_graphrag.queries.close.assert_awaited_once()
        lazy_graphrag.extractor.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_handles_missing_close_method(self):
        """Test that close() handles components without close() methods."""
        lazy_graphrag = LazyGraphRAGComponents()

        # Mock initialized state with components that don't have close()
        lazy_graphrag._initialized = True
        lazy_graphrag.validator = Mock()  # No close method
        lazy_graphrag.extractor = Mock()  # No close method
        lazy_graphrag.queries = Mock()  # No close method

        # Should not raise AttributeError
        await lazy_graphrag.close()

    @pytest.mark.asyncio
    async def test_close_handles_exceptions(self):
        """Test that close() handles exceptions gracefully."""
        lazy_graphrag = LazyGraphRAGComponents()

        # Mock initialized state
        lazy_graphrag._initialized = True
        lazy_graphrag.validator = AsyncMock()
        lazy_graphrag.validator.close = AsyncMock(side_effect=Exception("Connection error"))
        lazy_graphrag.queries = AsyncMock()
        lazy_graphrag.queries.close = AsyncMock()
        lazy_graphrag.extractor = AsyncMock()
        lazy_graphrag.extractor.close = AsyncMock()

        # Should not raise exception, should continue to close other components
        await lazy_graphrag.close()

        lazy_graphrag.validator.close.assert_awaited_once()
        lazy_graphrag.queries.close.assert_awaited_once()
        lazy_graphrag.extractor.close.assert_awaited_once()


class TestCleanupFunctions:
    """Test cleanup_knowledge_graph and cleanup_graphrag functions."""

    @pytest.mark.asyncio
    async def test_cleanup_knowledge_graph_with_lazy_wrapper(self):
        """Test cleanup_knowledge_graph with lazy wrapper object."""
        lazy_kg = LazyKnowledgeGraphComponents()
        lazy_kg._initialized = True
        lazy_kg.validator = AsyncMock()
        lazy_kg.validator.close = AsyncMock()
        lazy_kg.extractor = AsyncMock()
        lazy_kg.extractor.close = AsyncMock()

        # Cleanup should call close() on the lazy wrapper
        await cleanup_knowledge_graph(lazy_kg, lazy_kg)

        # Verify components were closed
        lazy_kg.validator.close.assert_awaited_once()
        lazy_kg.extractor.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cleanup_knowledge_graph_with_none(self):
        """Test cleanup_knowledge_graph with None parameters."""
        # Should not raise any errors
        await cleanup_knowledge_graph(None, None)

    @pytest.mark.asyncio
    async def test_cleanup_knowledge_graph_handles_exceptions(self):
        """Test cleanup_knowledge_graph handles exceptions gracefully."""
        lazy_kg = LazyKnowledgeGraphComponents()
        lazy_kg._initialized = True
        lazy_kg.validator = AsyncMock()
        lazy_kg.validator.close = AsyncMock(side_effect=Exception("Cleanup failed"))

        # Should not raise exception
        await cleanup_knowledge_graph(lazy_kg, lazy_kg)

    @pytest.mark.asyncio
    async def test_cleanup_graphrag_with_lazy_wrapper(self):
        """Test cleanup_graphrag with lazy wrapper object."""
        lazy_graphrag = LazyGraphRAGComponents()
        lazy_graphrag._initialized = True
        lazy_graphrag.validator = AsyncMock()
        lazy_graphrag.validator.close = AsyncMock()
        lazy_graphrag.queries = AsyncMock()
        lazy_graphrag.queries.close = AsyncMock()

        # Cleanup should call close() on the lazy wrapper
        await cleanup_graphrag(lazy_graphrag, lazy_graphrag)

        # Verify components were closed
        lazy_graphrag.validator.close.assert_awaited_once()
        lazy_graphrag.queries.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cleanup_graphrag_with_none(self):
        """Test cleanup_graphrag with None parameters."""
        # Should not raise any errors
        await cleanup_graphrag(None, None)

    @pytest.mark.asyncio
    async def test_cleanup_graphrag_handles_exceptions(self):
        """Test cleanup_graphrag handles exceptions gracefully."""
        lazy_graphrag = LazyGraphRAGComponents()
        lazy_graphrag._initialized = True
        lazy_graphrag.validator = AsyncMock()
        lazy_graphrag.validator.close = AsyncMock(side_effect=Exception("Cleanup failed"))

        # Should not raise exception
        await cleanup_graphrag(lazy_graphrag, lazy_graphrag)


class TestCleanupIntegration:
    """Integration tests for the complete cleanup workflow."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_knowledge_graph(self):
        """Test full lifecycle: initialize, use, cleanup for knowledge graph."""
        # Create lazy wrapper
        lazy_kg = LazyKnowledgeGraphComponents()

        # Simulate initialization
        lazy_kg._initialized = True
        lazy_kg.validator = AsyncMock()
        lazy_kg.validator.close = AsyncMock()
        lazy_kg.extractor = AsyncMock()
        lazy_kg.extractor.close = AsyncMock()

        # Verify initialized
        assert lazy_kg._initialized

        # Cleanup
        await cleanup_knowledge_graph(lazy_kg, lazy_kg)

        # Verify cleanup was called
        lazy_kg.validator.close.assert_awaited_once()
        lazy_kg.extractor.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_full_lifecycle_graphrag(self):
        """Test full lifecycle: initialize, use, cleanup for GraphRAG."""
        # Create lazy wrapper
        lazy_graphrag = LazyGraphRAGComponents()

        # Simulate initialization
        lazy_graphrag._initialized = True
        lazy_graphrag.validator = AsyncMock()
        lazy_graphrag.validator.close = AsyncMock()
        lazy_graphrag.queries = AsyncMock()
        lazy_graphrag.queries.close = AsyncMock()
        lazy_graphrag.extractor = AsyncMock()
        lazy_graphrag.extractor.close = AsyncMock()

        # Verify initialized
        assert lazy_graphrag._initialized

        # Cleanup
        await cleanup_graphrag(lazy_graphrag, lazy_graphrag)

        # Verify cleanup was called
        lazy_graphrag.validator.close.assert_awaited_once()
        lazy_graphrag.queries.close.assert_awaited_once()
        lazy_graphrag.extractor.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cleanup_before_initialization(self):
        """Test that cleanup before initialization doesn't cause errors."""
        # Create lazy wrappers without initialization
        lazy_kg = LazyKnowledgeGraphComponents()
        lazy_graphrag = LazyGraphRAGComponents()

        # Cleanup should not raise errors
        await cleanup_knowledge_graph(lazy_kg, lazy_kg)
        await cleanup_graphrag(lazy_graphrag, lazy_graphrag)

        # Verify still not initialized
        assert not lazy_kg._initialized
        assert not lazy_graphrag._initialized
