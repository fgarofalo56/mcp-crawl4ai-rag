"""
Initialization utilities for the Crawl4AI MCP server.

This module provides focused initialization functions for different components
of the MCP server lifecycle, extracted from the main lifespan function for
improved modularity and testability.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from supabase import Client

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder
else:
    try:
        from sentence_transformers import CrossEncoder
    except (ImportError, ValueError):
        CrossEncoder = None  # type: ignore

# Add knowledge_graphs folder to path for importing knowledge graph modules
knowledge_graphs_path = Path(__file__).resolve().parent.parent / "knowledge_graphs"
sys.path.append(str(knowledge_graphs_path))

from utils import get_supabase_client

# Import knowledge graph modules (lazy imports to avoid circular dependencies)
try:
    from knowledge_graph_validator import KnowledgeGraphValidator
    from parse_repo_into_neo4j import DirectNeo4jExtractor

    from knowledge_graphs.document_entity_extractor import DocumentEntityExtractor
    from knowledge_graphs.document_graph_queries import DocumentGraphQueries
    from knowledge_graphs.document_graph_validator import DocumentGraphValidator

    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False


def initialize_supabase() -> Client:
    """
    Initialize the Supabase client.

    Returns:
        Client: Initialized Supabase client

    Raises:
        Exception: If Supabase initialization fails
    """
    try:
        supabase_client = get_supabase_client()
        return supabase_client
    except Exception as e:
        raise Exception(f"Failed to initialize Supabase client: {str(e)}")


class LazyReranker:
    """
    Lazy-loading wrapper for CrossEncoder model.

    This delays model loading until first use to avoid startup timeout.
    The model is loaded on first call to predict() and cached for subsequent calls.
    """

    def __init__(self) -> None:
        self._model: Any | None = None
        self._device: str | None = None

    def _load_model(self) -> None:
        """Load the model with GPU support if available."""
        import sys

        import torch

        if self._model is not None:
            return

        try:
            # Detect best available device
            if torch.cuda.is_available():
                self._device = "cuda"
                print(
                    f"✓ GPU detected: {torch.cuda.get_device_name(0)}", file=sys.stderr, flush=True
                )
            else:
                self._device = "cpu"
                print("⚠ No GPU detected, using CPU for reranking", file=sys.stderr, flush=True)

            # Load model on the selected device
            self._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self._device)
            print(
                f"✓ Reranking model loaded on {self._device.upper()}", file=sys.stderr, flush=True
            )
        except Exception as e:
            print(f"Failed to load reranking model: {e}", file=sys.stderr, flush=True)
            self._model = None

    def predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        """Lazy-load model and make predictions."""
        if self._model is None:
            self._load_model()

        if self._model is None:
            # Model failed to load, return neutral scores
            return [0.5] * len(pairs)

        return self._model.predict(pairs)


def initialize_reranker() -> LazyReranker | None:
    """
    Initialize the reranking model wrapper (lazy-loading).

    Returns:
        Optional[LazyReranker]: Lazy reranker wrapper or None if disabled
    """
    import sys

    if os.getenv("USE_RERANKING", "false") != "true":
        return None

    print("✓ Reranking enabled (will load on first use)", file=sys.stderr, flush=True)
    return LazyReranker()


def _format_neo4j_error(error: Exception) -> str:
    """Format Neo4j connection errors for user-friendly messages."""
    error_str = str(error).lower()
    if "authentication" in error_str or "unauthorized" in error_str:
        return "Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD."
    elif "connection" in error_str or "refused" in error_str or "timeout" in error_str:
        return "Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running."
    elif "database" in error_str:
        return "Neo4j database error. Check if the database exists and is accessible."
    else:
        return f"Neo4j error: {str(error)}"


class LazyKnowledgeGraphComponents:
    """Lazy-loading wrapper for Neo4j knowledge graph components."""

    def __init__(self) -> None:
        self.validator: Any | None = None
        self.extractor: Any | None = None
        self._initialized: bool = False
        self._initializing: bool = False

    async def _ensure_initialized(self) -> None:
        """Initialize components on first use."""
        if self._initialized or self._initializing:
            return

        self._initializing = True
        import sys

        try:
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")

            print("Lazy-loading knowledge graph components...", file=sys.stderr, flush=True)

            # Initialize validator
            try:
                from knowledge_graph_validator import KnowledgeGraphValidator

                self.validator = KnowledgeGraphValidator(neo4j_uri, neo4j_user, neo4j_password)
                await self.validator.initialize()
                print("✓ Knowledge graph validator loaded", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Validator failed: {_format_neo4j_error(e)}", file=sys.stderr, flush=True)

            # Initialize extractor
            try:
                from parse_repo_into_neo4j import DirectNeo4jExtractor

                self.extractor = DirectNeo4jExtractor(neo4j_uri, neo4j_user, neo4j_password)
                await self.extractor.initialize()
                print("✓ Repository extractor loaded", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Extractor failed: {_format_neo4j_error(e)}", file=sys.stderr, flush=True)

            self._initialized = True
        finally:
            self._initializing = False

    async def get_validator(self) -> Any | None:
        """Get validator, initializing if needed."""
        await self._ensure_initialized()
        return self.validator

    async def get_extractor(self) -> Any | None:
        """Get extractor, initializing if needed."""
        await self._ensure_initialized()
        return self.extractor

    async def close(self) -> None:
        """Close all initialized components."""
        import sys

        # Only attempt cleanup if we've been initialized
        if not self._initialized:
            return

        # Close validator if it exists and has a close method
        if self.validator:
            try:
                if hasattr(self.validator, "close"):
                    await self.validator.close()
                    print("✓ Knowledge graph validator closed", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Error closing validator: {e}", file=sys.stderr, flush=True)

        # Close extractor if it exists and has a close method
        if self.extractor:
            try:
                if hasattr(self.extractor, "close"):
                    await self.extractor.close()
                    print("✓ Repository extractor closed", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Error closing extractor: {e}", file=sys.stderr, flush=True)


async def initialize_knowledge_graph() -> tuple[Any | None, Any | None]:
    """
    Initialize Neo4j knowledge graph components (lazy-loaded).

    Returns:
        Tuple[Optional[Any], Optional[Any]]: (lazy_components, lazy_components)
        Returns lazy wrapper that loads on first use, or (None, None) if disabled.
    """
    import sys

    # Check if knowledge graph functionality is enabled
    knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"

    if not knowledge_graph_enabled:
        print("Knowledge graph functionality disabled", file=sys.stderr, flush=True)
        return None, None

    if not KNOWLEDGE_GRAPH_AVAILABLE:
        print("Knowledge graph modules not available", file=sys.stderr, flush=True)
        return None, None

    # Get Neo4j credentials
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        print("Neo4j credentials not configured", file=sys.stderr, flush=True)
        return None, None

    print("✓ Knowledge graph enabled (will load on first use)", file=sys.stderr, flush=True)
    lazy_components = LazyKnowledgeGraphComponents()
    return lazy_components, lazy_components


class LazyGraphRAGComponents:
    """Lazy-loading wrapper for GraphRAG components."""

    def __init__(self) -> None:
        self.validator: Any | None = None
        self.extractor: Any | None = None
        self.queries: Any | None = None
        self._initialized: bool = False
        self._initializing: bool = False

    async def _ensure_initialized(self) -> None:
        """Initialize components on first use."""
        if self._initialized or self._initializing:
            return

        self._initializing = True
        import sys

        try:
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")

            print("Lazy-loading GraphRAG components...", file=sys.stderr, flush=True)

            # Initialize validator
            try:
                from knowledge_graphs.document_graph_validator import DocumentGraphValidator

                self.validator = DocumentGraphValidator(neo4j_uri, neo4j_user, neo4j_password)
                await self.validator.initialize()
                print("✓ Document graph validator loaded", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Validator failed: {e}", file=sys.stderr, flush=True)

            # Initialize queries
            try:
                from knowledge_graphs.document_graph_queries import DocumentGraphQueries

                self.queries = DocumentGraphQueries(neo4j_uri, neo4j_user, neo4j_password)
                await self.queries.initialize()
                print("✓ Document graph queries loaded", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Queries failed: {e}", file=sys.stderr, flush=True)

            # Initialize entity extractor
            try:
                from knowledge_graphs.document_entity_extractor import DocumentEntityExtractor

                if azure_openai_endpoint and azure_openai_key:
                    deployment = os.getenv("DEPLOYMENT") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    self.extractor = DocumentEntityExtractor(
                        azure_openai_endpoint=azure_openai_endpoint,
                        azure_openai_key=azure_openai_key,
                        model=deployment,
                    )
                    print(
                        f"✓ Entity extractor loaded (Azure, {deployment})",
                        file=sys.stderr,
                        flush=True,
                    )
                elif openai_api_key:
                    self.extractor = DocumentEntityExtractor(
                        openai_api_key=openai_api_key, model="gpt-4o-mini"
                    )
                    print("✓ Entity extractor loaded (OpenAI)", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Extractor failed: {e}", file=sys.stderr, flush=True)

            self._initialized = True
        finally:
            self._initializing = False

    async def get_validator(self) -> Any | None:
        """Get validator, initializing if needed."""
        await self._ensure_initialized()
        return self.validator

    async def get_extractor(self) -> Any | None:
        """Get extractor, initializing if needed."""
        await self._ensure_initialized()
        return self.extractor

    async def get_queries(self) -> Any | None:
        """Get queries, initializing if needed."""
        await self._ensure_initialized()
        return self.queries

    async def close(self) -> None:
        """Close all initialized components."""
        import sys

        # Only attempt cleanup if we've been initialized
        if not self._initialized:
            return

        # Close validator if it exists and has a close method
        if self.validator:
            try:
                if hasattr(self.validator, "close"):
                    await self.validator.close()
                    print("✓ Document graph validator closed", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Error closing document validator: {e}", file=sys.stderr, flush=True)

        # Close queries if it exists and has a close method
        if self.queries:
            try:
                if hasattr(self.queries, "close"):
                    await self.queries.close()
                    print("✓ Document graph queries closed", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Error closing document queries: {e}", file=sys.stderr, flush=True)

        # Entity extractor typically doesn't need cleanup (no persistent connections)
        # but check anyway for consistency
        if self.extractor:
            try:
                if hasattr(self.extractor, "close"):
                    await self.extractor.close()
                    print("✓ Entity extractor closed", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠ Error closing extractor: {e}", file=sys.stderr, flush=True)


async def initialize_graphrag() -> tuple[Any | None, Any | None, Any | None]:
    """
    Initialize GraphRAG components (lazy-loaded).

    Returns:
        Tuple[Optional[Any], Optional[Any], Optional[Any]]:
        (lazy_components, lazy_components, lazy_components)
        Returns lazy wrapper that loads on first use, or (None, None, None) if disabled.
    """
    import sys

    graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"

    if not graphrag_enabled:
        print("GraphRAG functionality disabled", file=sys.stderr, flush=True)
        return None, None, None

    if not KNOWLEDGE_GRAPH_AVAILABLE:
        print("GraphRAG modules not available", file=sys.stderr, flush=True)
        return None, None, None

    # Get Neo4j credentials
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")

    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        print("Neo4j credentials not configured", file=sys.stderr, flush=True)
        return None, None, None

    print("✓ GraphRAG enabled (will load on first use)", file=sys.stderr, flush=True)
    lazy_components = LazyGraphRAGComponents()
    return lazy_components, lazy_components, lazy_components


async def cleanup_knowledge_graph(
    knowledge_validator: Any | None, repo_extractor: Any | None
) -> None:
    """
    Clean up knowledge graph components.

    Args:
        knowledge_validator: LazyKnowledgeGraphComponents instance (or None)
        repo_extractor: LazyKnowledgeGraphComponents instance (same as knowledge_validator, or None)

    Note:
        Both parameters typically point to the same LazyKnowledgeGraphComponents instance.
        The function calls close() on the lazy wrapper, which properly closes all
        initialized underlying components (validator, extractor).
    """
    import sys

    # Since both parameters typically reference the same lazy wrapper,
    # we only need to close once. Check knowledge_validator first.
    if knowledge_validator:
        try:
            # Check if this is a lazy wrapper with a close method
            if hasattr(knowledge_validator, "close"):
                await knowledge_validator.close()
            else:
                print(
                    "⚠ Knowledge graph components don't have close method",
                    file=sys.stderr,
                    flush=True,
                )
        except Exception as e:
            print(f"⚠ Error during knowledge graph cleanup: {e}", file=sys.stderr, flush=True)
    elif repo_extractor and hasattr(repo_extractor, "close"):
        # Fallback: if knowledge_validator is None but repo_extractor exists
        try:
            await repo_extractor.close()
        except Exception as e:
            print(f"⚠ Error during repository extractor cleanup: {e}", file=sys.stderr, flush=True)


async def cleanup_graphrag(
    document_graph_validator: Any | None, document_graph_queries: Any | None
) -> None:
    """
    Clean up GraphRAG components.

    Args:
        document_graph_validator: LazyGraphRAGComponents instance (or None)
        document_graph_queries: LazyGraphRAGComponents instance (same as document_graph_validator, or None)

    Note:
        Both parameters typically point to the same LazyGraphRAGComponents instance.
        The function calls close() on the lazy wrapper, which properly closes all
        initialized underlying components (validator, queries, extractor).
    """
    import sys

    # Since both parameters typically reference the same lazy wrapper,
    # we only need to close once. Check document_graph_validator first.
    if document_graph_validator:
        try:
            # Check if this is a lazy wrapper with a close method
            if hasattr(document_graph_validator, "close"):
                await document_graph_validator.close()
            else:
                print("⚠ GraphRAG components don't have close method", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"⚠ Error during GraphRAG cleanup: {e}", file=sys.stderr, flush=True)
    elif document_graph_queries and hasattr(document_graph_queries, "close"):
        # Fallback: if document_graph_validator is None but document_graph_queries exists
        try:
            await document_graph_queries.close()
        except Exception as e:
            print(
                f"⚠ Error during document graph queries cleanup: {e}", file=sys.stderr, flush=True
            )
