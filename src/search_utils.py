"""
Helper functions for search operations (code examples and documents).

This module provides utilities for:
- Query parameter validation and processing
- Hybrid search combining vector and keyword search
- Search result merging and ranking
- Result formatting
"""

from __future__ import annotations

import json
import os
from typing import Any

from supabase import Client


def check_code_examples_enabled() -> tuple[bool, str | None]:
    """
    Check if code example extraction is enabled.

    Returns:
        Tuple of (enabled: bool, error_message: Optional[str])
    """
    extract_code_examples_enabled = os.getenv("USE_AGENTIC_RAG", "false") == "true"
    if not extract_code_examples_enabled:
        error_response = {
            "success": False,
            "error": "Code example extraction is disabled. Perform a normal RAG search.",
        }
        return False, json.dumps(error_response, indent=2)
    return True, None


def prepare_source_filter(source_id: str | None) -> dict[str, str] | None:
    """
    Prepare filter metadata from source ID.

    Args:
        source_id: Optional source ID to filter by

    Returns:
        Filter metadata dictionary or None
    """
    if source_id and source_id.strip():
        return {"source": source_id}
    return None


def execute_vector_search(
    supabase_client: Client,
    query: str,
    match_count: int,
    filter_metadata: dict[str, str] | None,
    search_function,
) -> list[dict[str, Any]]:
    """
    Execute vector search for code examples.

    Args:
        supabase_client: Supabase client instance
        query: Search query
        match_count: Number of results to return
        filter_metadata: Optional metadata filter
        search_function: The search function to call

    Returns:
        List of search results
    """
    return search_function(
        client=supabase_client,
        query=query,
        match_count=match_count,
        filter_metadata=filter_metadata,
    )


def execute_keyword_search(
    supabase_client: Client, query: str, source_id: str | None, match_count: int
) -> list[dict[str, Any]]:
    """
    Execute keyword search on code examples table.

    Args:
        supabase_client: Supabase client instance
        query: Search query
        source_id: Optional source ID filter
        match_count: Number of results to return

    Returns:
        List of keyword search results
    """
    # Build keyword query using ILIKE on both content and summary
    keyword_query = (
        supabase_client.from_("code_examples")
        .select("id, url, chunk_number, content, summary, metadata, source_id")
        .or_(f"content.ilike.%{query}%,summary.ilike.%{query}%")
    )

    # Apply source filter if provided
    if source_id and source_id.strip():
        keyword_query = keyword_query.eq("source_id", source_id)

    # Execute keyword search
    keyword_response = keyword_query.limit(match_count * 2).execute()
    return keyword_response.data if keyword_response.data else []


def merge_vector_and_keyword_results(
    vector_results: list[dict[str, Any]], keyword_results: list[dict[str, Any]], match_count: int
) -> list[dict[str, Any]]:
    """
    Merge vector and keyword search results with preference for overlapping items.

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
                    "summary": kr["summary"],
                    "metadata": kr["metadata"],
                    "source_id": kr["source_id"],
                    "similarity": 0.5,  # Default similarity for keyword-only matches
                }
            )
            seen_ids.add(kr["id"])

    return combined_results[:match_count]


def perform_hybrid_search(
    supabase_client: Client,
    query: str,
    source_id: str | None,
    match_count: int,
    filter_metadata: dict[str, str] | None,
    search_function,
) -> list[dict[str, Any]]:
    """
    Perform hybrid search combining vector and keyword searches.

    Args:
        supabase_client: Supabase client instance
        query: Search query
        source_id: Optional source ID filter
        match_count: Number of results to return
        filter_metadata: Optional metadata filter
        search_function: Vector search function to use

    Returns:
        Combined search results
    """
    # Execute vector search (get more to account for filtering)
    vector_results = execute_vector_search(
        supabase_client, query, match_count * 2, filter_metadata, search_function
    )

    # Execute keyword search
    keyword_results = execute_keyword_search(supabase_client, query, source_id, match_count)

    # Merge results
    return merge_vector_and_keyword_results(vector_results, keyword_results, match_count)


def format_search_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Format search results for code examples response.

    Args:
        results: Raw search results

    Returns:
        Formatted results with consistent structure
    """
    formatted_results = []
    for result in results:
        formatted_result = {
            "url": result.get("url"),
            "code": result.get("content"),
            "summary": result.get("summary"),
            "metadata": result.get("metadata"),
            "source_id": result.get("source_id"),
            "similarity": result.get("similarity"),
        }
        # Include rerank score if available
        if "rerank_score" in result:
            formatted_result["rerank_score"] = result["rerank_score"]
        formatted_results.append(formatted_result)

    return formatted_results


def build_search_response(
    query: str,
    source_id: str | None,
    formatted_results: list[dict[str, Any]],
    use_hybrid_search: bool,
    use_reranking: bool,
    reranking_model_available: bool,
) -> str:
    """
    Build final JSON response for code example search.

    Args:
        query: Original search query
        source_id: Source filter used
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
        "source_filter": source_id,
        "search_mode": "hybrid" if use_hybrid_search else "vector",
        "reranking_applied": use_reranking and reranking_model_available,
        "results": formatted_results,
        "count": len(formatted_results),
    }
    return json.dumps(response, indent=2)


def build_error_response(query: str, error: Exception) -> str:
    """
    Build error response JSON.

    Args:
        query: Original search query
        error: Exception that occurred

    Returns:
        JSON string error response
    """
    return json.dumps({"success": False, "query": query, "error": str(error)}, indent=2)
