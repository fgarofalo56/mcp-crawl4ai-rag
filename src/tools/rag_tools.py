"""
RAG Tools

MCP tools for Retrieval Augmented Generation queries and code search.
"""

import json
import os

from fastmcp import Context

from core import rerank_results
from utils import (
    search_documents,
)


async def perform_rag_query(
    ctx: Context,
    query: str,
    source_filter: str = None,
    match_count: int = 5,
    offset: int = 0,
    max_content_length: int = 1000,
    include_full_content: bool = True,
    max_response_tokens: int = 20000,
) -> str:
    """
    Perform a RAG (Retrieval Augmented Generation) query on the stored content.

    This tool searches the vector database for content relevant to the query and returns
    the matching documents. Optionally filter by source domain.
    Get the source by using the get_available_sources tool before calling this search!

    **Token Limit Safety**: This tool automatically truncates responses to stay within
    MCP client limits (25,000 tokens). Large result sets will be paginated.

    Args:
        ctx: The MCP server provided context
        query: The search query
        source_filter: Optional source domain to filter results (e.g., 'example.com')
        match_count: Maximum number of results to return (default: 5)
        offset: Number of results to skip for pagination (default: 0)
        max_content_length: Maximum characters per content field (default: 1000)
        include_full_content: Whether to include full content or truncate (default: True)
        max_response_tokens: Maximum tokens in response (default: 20000, hard limit: 25000)

    Returns:
        JSON string with the search results

    Example:
        # First page (results 0-4)
        perform_rag_query("machine learning", match_count=5, offset=0)

        # Second page (results 5-9)
        perform_rag_query("machine learning", match_count=5, offset=5)

        # Truncate content to 500 chars
        perform_rag_query("machine learning", max_content_length=500, include_full_content=False)
    """
    # Import RAG utilities
    from rag_utils import (
        build_rag_error_response,
        format_rag_results,
        paginate_results,
        perform_hybrid_search_for_documents,
    )
    from response_size_manager import (
        SizeConstraints,
        generate_truncation_warning,
        truncate_results_to_fit,
    )

    try:
        # Validate and cap max_response_tokens
        max_response_tokens = min(max_response_tokens, 20000)  # Hard cap at 20k for safety

        # Get the Supabase client from the context
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"

        # Prepare filter if source is provided and not empty
        filter_metadata = None
        if source_filter and source_filter.strip():
            filter_metadata = {"source": source_filter}

        # Execute search based on mode (get more results than needed for pagination)
        search_limit = match_count + offset + 10  # Buffer for pagination
        if use_hybrid_search:
            results = perform_hybrid_search_for_documents(
                supabase_client,
                query,
                source_filter,
                search_limit,
                filter_metadata,
                search_documents,
            )
        else:
            # Standard vector search only
            results = search_documents(
                client=supabase_client,
                query=query,
                match_count=search_limit,
                filter_metadata=filter_metadata,
            )

        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(
                ctx.request_context.lifespan_context.reranking_model,
                query,
                results,
                content_key="content",
            )

        # Apply pagination BEFORE size management
        paginated_results = paginate_results(results, offset=offset, limit=match_count)

        # Apply size constraints to stay within token limits
        constraints = SizeConstraints(
            max_response_tokens=max_response_tokens,
            max_content_length=max_content_length,
            include_full_content=include_full_content,
            reserved_tokens=2000,
        )
        truncated_results, truncation_info = truncate_results_to_fit(
            paginated_results, constraints, content_key="content"
        )

        # Format results
        formatted_results = format_rag_results(truncated_results)

        # Generate truncation warning if needed
        warning = generate_truncation_warning(truncation_info, max_content_length)

        # Build response with truncation info
        response_dict = {
            "success": True,
            "query": query,
            "source_filter": source_filter,
            "search_mode": "hybrid" if use_hybrid_search else "vector",
            "reranking_applied": use_reranking
            and ctx.request_context.lifespan_context.reranking_model is not None,
            "results": formatted_results,
            "count": len(formatted_results),
            "pagination": {
                "offset": offset,
                "requested_count": match_count,
                "returned_count": len(formatted_results),
                "has_more": len(results) > offset + match_count,
            },
        }

        # Add truncation warning if present
        if warning:
            response_dict["warning"] = warning
            response_dict["truncation_info"] = truncation_info

        return json.dumps(response_dict, indent=2)

    except Exception as e:
        return build_rag_error_response(query, e)


async def search_code_examples(
    ctx: Context, query: str, source_id: str = None, match_count: int = 5
) -> str:
    """
    Search for code examples relevant to the query.

    This tool searches the vector database for code examples relevant to the query and returns
    the matching examples with their summaries. Optionally filter by source_id.
    Get the source_id by using the get_available_sources tool before calling this search!

    Use the get_available_sources tool first to see what sources are available for filtering.

    Args:
        ctx: The MCP server provided context
        query: The search query
        source_id: Optional source ID to filter results (e.g., 'example.com')
        match_count: Maximum number of results to return (default: 5)

    Returns:
        JSON string with the search results
    """
    # Import search utilities
    from .search_utils import (
        build_error_response,
        build_search_response,
        check_code_examples_enabled,
        execute_vector_search,
        format_search_results,
        perform_hybrid_search,
        prepare_source_filter,
    )

    # Check if code example extraction is enabled
    enabled, error_msg = check_code_examples_enabled()
    if not enabled:
        return error_msg

    try:
        # Get the Supabase client from the context
        supabase_client = ctx.request_context.lifespan_context.supabase_client

        # Check if hybrid search is enabled
        use_hybrid_search = os.getenv("USE_HYBRID_SEARCH", "false") == "true"

        # Prepare filter metadata
        filter_metadata = prepare_source_filter(source_id)

        # Import the search function from utils
        from .utils import search_code_examples as search_code_examples_impl

        # Execute search based on mode
        if use_hybrid_search:
            results = perform_hybrid_search(
                supabase_client,
                query,
                source_id,
                match_count,
                filter_metadata,
                search_code_examples_impl,
            )
        else:
            results = execute_vector_search(
                supabase_client, query, match_count, filter_metadata, search_code_examples_impl
            )

        # Apply reranking if enabled
        use_reranking = os.getenv("USE_RERANKING", "false") == "true"
        if use_reranking and ctx.request_context.lifespan_context.reranking_model:
            results = rerank_results(
                ctx.request_context.lifespan_context.reranking_model,
                query,
                results,
                content_key="content",
            )

        # Format results and build response
        formatted_results = format_search_results(results)
        return build_search_response(
            query,
            source_id,
            formatted_results,
            use_hybrid_search,
            use_reranking,
            ctx.request_context.lifespan_context.reranking_model is not None,
        )

    except Exception as e:
        return build_error_response(query, e)


__all__ = ["perform_rag_query", "search_code_examples"]
