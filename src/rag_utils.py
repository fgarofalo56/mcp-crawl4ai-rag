"""
Helper functions for RAG (Retrieval Augmented Generation) query operations.

This module provides utilities for:
- Hybrid search for document retrieval (combining vector and keyword search)
- Result merging and ranking for RAG queries
- Result formatting for RAG responses
- Pagination for large result sets
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from supabase import Client


@dataclass
class PaginationParams:
    """
    Pagination parameters for RAG queries.

    Attributes:
        offset: Number of results to skip (for pagination)
        limit: Maximum number of results to return
    """

    offset: int = 0
    limit: int = 5


def paginate_results(
    results: list[dict[str, Any]], offset: int = 0, limit: int | None = None
) -> list[dict[str, Any]]:
    """
    Apply pagination to search results.

    Args:
        results: List of search results to paginate
        offset: Number of results to skip (default: 0)
        limit: Maximum number of results to return (None = no limit)

    Returns:
        Paginated subset of results
    """
    if not results:
        return results

    # Apply offset
    if offset > 0:
        results = results[offset:]

    # Apply limit
    if limit is not None and limit > 0:
        results = results[:limit]

    return results


def execute_vector_search_for_documents(
    supabase_client: Client,
    query: str,
    match_count: int,
    filter_metadata: dict[str, str] | None,
    search_documents_func,
) -> list[dict[str, Any]]:
    """
    Execute vector search for documents.

    Args:
        supabase_client: Supabase client instance
        query: Search query
        match_count: Number of results to return
        filter_metadata: Optional metadata filter
        search_documents_func: The search_documents function from utils

    Returns:
        List of search results
    """
    return search_documents_func(
        client=supabase_client,
        query=query,
        match_count=match_count,
        filter_metadata=filter_metadata,
    )


def execute_keyword_search_for_documents(
    supabase_client: Client, query: str, source_filter: str | None, match_count: int
) -> list[dict[str, Any]]:
    """
    Execute keyword search on crawled_pages table.

    Args:
        supabase_client: Supabase client instance
        query: Search query
        source_filter: Optional source filter
        match_count: Number of results to return

    Returns:
        List of keyword search results
    """
    # Build keyword query using ILIKE
    keyword_query = (
        supabase_client.from_("crawled_pages")
        .select("id, url, chunk_number, content, metadata, source_id")
        .ilike("content", f"%{query}%")
    )

    # Apply source filter if provided
    if source_filter and source_filter.strip():
        keyword_query = keyword_query.eq("source_id", source_filter)

    # Execute keyword search
    keyword_response = keyword_query.limit(match_count * 2).execute()
    return keyword_response.data if keyword_response.data else []


def merge_document_search_results(
    vector_results: list[dict[str, Any]], keyword_results: list[dict[str, Any]], match_count: int
) -> list[dict[str, Any]]:
    """
    Merge vector and keyword search results for documents.

    This function combines results from vector and keyword searches, giving priority to:
    1. Items appearing in both searches (boosted similarity score)
    2. Remaining vector results (semantic matches)
    3. Pure keyword matches (if more results needed)

    Args:
        vector_results: Results from vector search
        keyword_results: Results from keyword search
        match_count: Maximum number of results to return

    Returns:
        Merged and ranked list of results
    """
    seen_ids = set()
    combined_results = []

    # Create set of vector result IDs for quick lookup
    vector_ids = {r.get("id") for r in vector_results if r.get("id")}

    # Step 1: Add items appearing in both searches (best matches)
    for kr in keyword_results:
        if kr["id"] in vector_ids and kr["id"] not in seen_ids:
            # Find the vector result to get similarity score
            for vr in vector_results:
                if vr.get("id") == kr["id"]:
                    # Boost similarity score for items in both results
                    vr["similarity"] = min(1.0, vr.get("similarity", 0) * 1.2)
                    combined_results.append(vr)
                    seen_ids.add(kr["id"])
                    break

    # Step 2: Add remaining vector results (semantic matches)
    for vr in vector_results:
        if vr.get("id") and vr["id"] not in seen_ids and len(combined_results) < match_count:
            combined_results.append(vr)
            seen_ids.add(vr["id"])

    # Step 3: Add pure keyword matches if needed
    for kr in keyword_results:
        if kr["id"] not in seen_ids and len(combined_results) < match_count:
            # Convert keyword result to match vector result format
            combined_results.append(
                {
                    "id": kr["id"],
                    "url": kr["url"],
                    "chunk_number": kr["chunk_number"],
                    "content": kr["content"],
                    "metadata": kr["metadata"],
                    "source_id": kr["source_id"],
                    "similarity": 0.5,  # Default similarity for keyword-only matches
                }
            )
            seen_ids.add(kr["id"])

    return combined_results[:match_count]


def perform_hybrid_search_for_documents(
    supabase_client: Client,
    query: str,
    source_filter: str | None,
    match_count: int,
    filter_metadata: dict[str, str] | None,
    search_documents_func,
) -> list[dict[str, Any]]:
    """
    Perform hybrid search combining vector and keyword searches for documents.

    Args:
        supabase_client: Supabase client instance
        query: Search query
        source_filter: Optional source filter
        match_count: Number of results to return
        filter_metadata: Optional metadata filter
        search_documents_func: Vector search function to use

    Returns:
        Combined search results
    """
    # Execute vector search (get more to account for filtering)
    vector_results = execute_vector_search_for_documents(
        supabase_client, query, match_count * 2, filter_metadata, search_documents_func
    )

    # Execute keyword search
    keyword_results = execute_keyword_search_for_documents(
        supabase_client, query, source_filter, match_count
    )

    # Merge results
    return merge_document_search_results(vector_results, keyword_results, match_count)


def format_rag_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Format search results for RAG query response.

    Args:
        results: Raw search results

    Returns:
        Formatted results with consistent structure
    """
    formatted_results = []
    for result in results:
        formatted_result = {
            "url": result.get("url"),
            "content": result.get("content"),
            "metadata": result.get("metadata"),
            "similarity": result.get("similarity"),
        }
        # Include rerank score if available
        if "rerank_score" in result:
            formatted_result["rerank_score"] = result["rerank_score"]
        formatted_results.append(formatted_result)

    return formatted_results


def build_rag_response(
    query: str,
    source_filter: str | None,
    formatted_results: list[dict[str, Any]],
    use_hybrid_search: bool,
    use_reranking: bool,
    reranking_model_available: bool,
) -> str:
    """
    Build final JSON response for RAG query.

    Args:
        query: Original search query
        source_filter: Source filter used
        formatted_results: Formatted search results
        use_hybrid_search: Whether hybrid search was used
        use_reranking: Whether reranking was requested
        reranking_model_available: Whether reranking model is available

    Returns:
        JSON string response
    """
    response = {
        "success": True,
        "query": query,
        "source_filter": source_filter,
        "search_mode": "hybrid" if use_hybrid_search else "vector",
        "reranking_applied": use_reranking and reranking_model_available,
        "results": formatted_results,
        "count": len(formatted_results),
    }
    return json.dumps(response, indent=2)


def build_rag_error_response(query: str, error: Exception) -> str:
    """
    Build error response JSON for RAG query.

    Args:
        query: Original search query
        error: Exception that occurred

    Returns:
        JSON string error response
    """
    return json.dumps({"success": False, "query": query, "error": str(error)}, indent=2)
