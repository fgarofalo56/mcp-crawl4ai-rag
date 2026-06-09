"""
Result Reranking Utilities

Provides functions for reranking search results using cross-encoder models
to improve relevance scoring.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder
else:
    try:
        from sentence_transformers import CrossEncoder
    except (ImportError, ValueError):
        CrossEncoder = None  # type: ignore


def rerank_results(
    model: CrossEncoder | None,
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
