"""
Search strategies for RAG queries.

This module implements the Strategy pattern for search operations,
providing a clean separation of concerns for different types of queries:
- RAG search: Hybrid vector + keyword search for general content
- Code search: Specialized search for code examples with summaries

Each strategy implements a common interface for consistent behavior
and easy extensibility.
"""

from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from sentence_transformers import CrossEncoder
from supabase import Client


@dataclass
class SearchResult:
    """
    Result of a search operation.

    Attributes:
        success: Whether the search was successful
        query: The original search query
        results: List of search results with content and metadata
        result_count: Number of results returned
        error_message: Error message if search failed (None if successful)
        metadata: Additional metadata about the search operation
    """

    success: bool
    query: str
    results: list[dict[str, Any]]
    result_count: int
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class SearchStrategy(ABC):
    """
    Abstract base class for search strategies.

    All concrete search strategies must implement the execute_search() method.
    This provides a consistent interface for different types of search operations.
    """

    @abstractmethod
    async def execute_search(
        self,
        supabase_client: Client,
        query: str,
        source_filter: str | None = None,
        match_count: int = 5,
        reranking_model: CrossEncoder | None = None,
        **kwargs,
    ) -> SearchResult:
        """
        Execute the search operation.

        Args:
            supabase_client: Supabase client for database access
            query: Search query string
            source_filter: Optional source domain filter (e.g., 'example.com')
            match_count: Maximum number of results to return
            reranking_model: Optional cross-encoder model for result reranking
            **kwargs: Additional strategy-specific parameters

        Returns:
            SearchResult with search results and metadata
        """
        pass

    def format_results(self, results: list[dict[str, Any]]) -> str:
        """
        Format search results as a JSON string.

        Args:
            results: List of search results

        Returns:
            JSON-formatted string of results
        """
        return json.dumps(results, indent=2)


class RAGSearchStrategy(SearchStrategy):
    """
    Strategy for general RAG queries using hybrid search.

    This strategy performs hybrid vector + keyword search on document content,
    with optional reranking for improved relevance.
    """

    async def execute_search(
        self,
        supabase_client: Client,
        query: str,
        source_filter: str | None = None,
        match_count: int = 5,
        reranking_model: CrossEncoder | None = None,
        **kwargs,
    ) -> SearchResult:
        """
        Execute hybrid RAG search.

        Args:
            supabase_client: Supabase client for database access
            query: Search query string
            source_filter: Optional source domain filter
            match_count: Maximum number of results to return
            reranking_model: Optional reranking model
            **kwargs: Additional parameters:
                - use_hybrid_search: Whether to use hybrid search (default: from env)

        Returns:
            SearchResult with matched documents
        """
        try:
            # Import search_documents from utils
            import os

            from utils import search_documents

            # Check if hybrid search is enabled
            use_hybrid_search = kwargs.get(
                "use_hybrid_search", os.getenv("USE_HYBRID_SEARCH", "false") == "true"
            )

            # Prepare filter if source is provided
            filter_metadata = None
            if source_filter and source_filter.strip():
                filter_metadata = {"source": source_filter}

            if use_hybrid_search:
                results = self._execute_hybrid_search(
                    supabase_client, query, source_filter, match_count, filter_metadata
                )
            else:
                # Standard vector search only
                results = search_documents(
                    client=supabase_client,
                    query=query,
                    match_count=match_count,
                    filter_metadata=filter_metadata,
                )

            # Rerank results if model is provided
            if reranking_model and results:
                results = self._rerank_results(
                    reranking_model, query, results, content_key="content"
                )

            return SearchResult(
                success=True,
                query=query,
                results=results,
                result_count=len(results),
                metadata={
                    "search_type": "hybrid" if use_hybrid_search else "vector",
                    "source_filter": source_filter,
                    "reranked": reranking_model is not None,
                },
            )

        except Exception as e:
            return SearchResult(
                success=False,
                query=query,
                results=[],
                result_count=0,
                error_message=str(e),
                metadata={"search_type": "rag"},
            )

    def _execute_hybrid_search(
        self,
        supabase_client: Client,
        query: str,
        source_filter: str | None,
        match_count: int,
        filter_metadata: dict[str, str] | None,
    ) -> list[dict[str, Any]]:
        """
        Execute hybrid search combining vector and keyword search.

        Args:
            supabase_client: Supabase client
            query: Search query
            source_filter: Optional source filter
            match_count: Number of results to return
            filter_metadata: Metadata filter

        Returns:
            Combined search results
        """
        from utils import search_documents

        # 1. Get vector search results
        vector_results = search_documents(
            client=supabase_client,
            query=query,
            match_count=match_count * 2,
            filter_metadata=filter_metadata,
        )

        # 2. Get keyword search results using ILIKE
        keyword_query = (
            supabase_client.from_("crawled_pages")
            .select("id, url, chunk_number, content, metadata, source_id")
            .ilike("content", f"%{query}%")
        )

        if source_filter and source_filter.strip():
            keyword_query = keyword_query.eq("source_id", source_filter)

        keyword_response = keyword_query.limit(match_count * 2).execute()
        keyword_results = keyword_response.data if keyword_response.data else []

        # 3. Combine results
        seen_ids = set()
        combined_results = []

        # First, add items appearing in both (best matches)
        vector_ids = {r.get("id") for r in vector_results if r.get("id")}
        for kr in keyword_results:
            if kr["id"] in vector_ids and kr["id"] not in seen_ids:
                for vr in vector_results:
                    if vr.get("id") == kr["id"]:
                        # Boost similarity for items in both
                        vr["similarity"] = min(1.0, vr.get("similarity", 0) * 1.2)
                        combined_results.append(vr)
                        seen_ids.add(kr["id"])
                        break

        # Add remaining vector results
        for vr in vector_results:
            if vr.get("id") and vr["id"] not in seen_ids and len(combined_results) < match_count:
                combined_results.append(vr)
                seen_ids.add(vr["id"])

        # Add pure keyword matches
        for kr in keyword_results:
            if kr["id"] not in seen_ids and len(combined_results) < match_count:
                combined_results.append(
                    {
                        "id": kr["id"],
                        "url": kr["url"],
                        "chunk_number": kr["chunk_number"],
                        "content": kr["content"],
                        "metadata": kr["metadata"],
                        "source_id": kr["source_id"],
                        "similarity": 0.5,
                    }
                )
                seen_ids.add(kr["id"])

        return combined_results[:match_count]

    def _rerank_results(
        self,
        model: CrossEncoder,
        query: str,
        results: list[dict[str, Any]],
        content_key: str = "content",
    ) -> list[dict[str, Any]]:
        """
        Rerank search results using a cross-encoder model.

        Args:
            model: The cross-encoder model to use for reranking
            query: The search query
            results: List of search results
            content_key: The key in each result dict that contains the text content

        Returns:
            Reranked list of results
        """
        if not model or not results:
            return results

        try:
            # Extract content from results
            texts = [result.get(content_key, "") for result in results]

            # Create pairs of [query, document] for the cross-encoder
            pairs = [[query, text] for text in texts]

            # Get relevance scores from the cross-encoder
            scores = model.predict(pairs)

            # Add scores to results and sort by score (descending)
            for i, result in enumerate(results):
                result["rerank_score"] = float(scores[i])

            # Sort by rerank score
            reranked = sorted(results, key=lambda x: x.get("rerank_score", 0), reverse=True)

            return reranked
        except Exception as e:
            print(f"Error during reranking: {e}", file=sys.stderr, flush=True)
            return results


class CodeSearchStrategy(SearchStrategy):
    """
    Strategy for searching code examples.

    This strategy searches for code examples with their summaries,
    using hybrid search optimized for code content.
    """

    async def execute_search(
        self,
        supabase_client: Client,
        query: str,
        source_filter: str | None = None,
        match_count: int = 5,
        reranking_model: CrossEncoder | None = None,
        **kwargs,
    ) -> SearchResult:
        """
        Execute code example search.

        Args:
            supabase_client: Supabase client for database access
            query: Search query string
            source_filter: Optional source domain filter
            match_count: Maximum number of results to return
            reranking_model: Optional reranking model
            **kwargs: Additional parameters (ignored)

        Returns:
            SearchResult with matched code examples
        """
        try:
            # Import search_code_examples from utils
            from utils import search_code_examples

            # Execute code search
            results = search_code_examples(
                supabase_client, query, source_id=source_filter, match_count=match_count
            )

            # Rerank results if model is provided
            if reranking_model and results:
                # Use code example summary for reranking
                results = self._rerank_results(
                    reranking_model, query, results, content_key="summary"
                )

            return SearchResult(
                success=True,
                query=query,
                results=results,
                result_count=len(results),
                metadata={
                    "search_type": "code_examples",
                    "source_filter": source_filter,
                    "reranked": reranking_model is not None,
                },
            )

        except Exception as e:
            return SearchResult(
                success=False,
                query=query,
                results=[],
                result_count=0,
                error_message=str(e),
                metadata={"search_type": "code_examples"},
            )

    def _rerank_results(
        self,
        model: CrossEncoder,
        query: str,
        results: list[dict[str, Any]],
        content_key: str = "summary",
    ) -> list[dict[str, Any]]:
        """
        Rerank code search results using a cross-encoder model.

        Args:
            model: The cross-encoder model to use for reranking
            query: The search query
            results: List of search results
            content_key: The key in each result dict that contains the text content

        Returns:
            Reranked list of results
        """
        if not model or not results:
            return results

        try:
            # Extract content from results (summaries for code)
            texts = [result.get(content_key, "") for result in results]

            # Create pairs of [query, document] for the cross-encoder
            pairs = [[query, text] for text in texts]

            # Get relevance scores from the cross-encoder
            scores = model.predict(pairs)

            # Add scores to results and sort by score (descending)
            for i, result in enumerate(results):
                result["rerank_score"] = float(scores[i])

            # Sort by rerank score
            reranked = sorted(results, key=lambda x: x.get("rerank_score", 0), reverse=True)

            return reranked
        except Exception as e:
            print(f"Error during reranking: {e}", file=sys.stderr, flush=True)
            return results


class SearchStrategyFactory:
    """
    Factory for selecting the appropriate search strategy.

    This factory provides a simple way to get the right search strategy
    based on the search type.
    """

    @staticmethod
    def get_rag_strategy() -> RAGSearchStrategy:
        """
        Get the RAG search strategy.

        Returns:
            RAGSearchStrategy instance
        """
        return RAGSearchStrategy()

    @staticmethod
    def get_code_strategy() -> CodeSearchStrategy:
        """
        Get the code search strategy.

        Returns:
            CodeSearchStrategy instance
        """
        return CodeSearchStrategy()
