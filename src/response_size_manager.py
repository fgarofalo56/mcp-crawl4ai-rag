"""
Response Size Management

This module provides utilities for managing response sizes to stay within
MCP client token limits (25,000 tokens).

Features:
- Token estimation (using existing count_tokens_estimate from utils)
- Content truncation with safe boundaries
- Result set truncation to fit within limits
- Warning generation for truncated responses
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class SizeConstraints:
    """
    Configuration for response size constraints.

    Attributes:
        max_response_tokens: Maximum tokens allowed in full response (buffer below 25k)
        max_content_length: Maximum characters per content field
        include_full_content: Whether to include full content or truncate
        reserved_tokens: Tokens reserved for response structure/metadata
    """

    max_response_tokens: int = 20000  # Buffer below 25k limit
    max_content_length: int = 1000  # Characters per content field
    include_full_content: bool = True  # Whether to include full content
    reserved_tokens: int = 2000  # Reserved for JSON structure, metadata


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text using rough approximation.

    This uses the same estimation as utils.count_tokens_estimate for consistency.
    For production, consider using tiktoken for accurate counts.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count (1 token ≈ 4 characters)
    """
    if not text:
        return 0
    return len(text) // 4


def truncate_content(content: str, max_length: int, add_ellipsis: bool = True) -> tuple[str, bool]:
    """
    Truncate content to maximum length with safe boundaries.

    This function truncates at word boundaries to avoid cutting mid-word,
    and optionally adds an ellipsis to indicate truncation.

    Args:
        content: Content to truncate
        max_length: Maximum length in characters
        add_ellipsis: Whether to add "..." to indicate truncation

    Returns:
        Tuple of (truncated_content, was_truncated)
    """
    if not content or len(content) <= max_length:
        return content, False

    # Reserve space for ellipsis if needed
    effective_max = max_length - 4 if add_ellipsis else max_length

    # Truncate at word boundary
    truncated = content[:effective_max]

    # Find last space to avoid cutting mid-word
    last_space = truncated.rfind(" ")
    if last_space > 0 and last_space > effective_max * 0.8:  # Don't lose too much
        truncated = truncated[:last_space]

    # Add ellipsis if requested
    if add_ellipsis:
        truncated = truncated + " ..."

    return truncated, True


def truncate_results_to_fit(
    results: list[dict[str, Any]],
    constraints: SizeConstraints,
    content_key: str = "content",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Truncate results to fit within token constraints.

    This function processes results in order, truncating content and limiting
    the number of results to stay within the specified token budget.

    Strategy:
    1. Estimate tokens for response structure (reserved)
    2. Process results one by one, truncating content as needed
    3. Stop adding results when approaching token limit
    4. Track truncation statistics for warning generation

    Args:
        results: List of result dictionaries to truncate
        constraints: Size constraints to enforce
        content_key: Key in result dict that contains main content (default: 'content')

    Returns:
        Tuple of (truncated_results, truncation_info)
        where truncation_info contains:
        - truncated: Whether any truncation occurred
        - original_count: Original number of results
        - final_count: Number of results after truncation
        - content_truncated_count: Number of content fields truncated
        - estimated_tokens: Estimated final token count
    """
    if not results:
        return results, {
            "truncated": False,
            "original_count": 0,
            "final_count": 0,
            "content_truncated_count": 0,
            "estimated_tokens": 0,
        }

    truncated_results = []
    content_truncated_count = 0
    current_tokens = constraints.reserved_tokens  # Start with reserved

    # Calculate available tokens for content
    available_tokens = constraints.max_response_tokens - constraints.reserved_tokens

    for result in results:
        # Create a copy to avoid modifying original
        result_copy = result.copy()

        # Truncate content field if present and needed
        if content_key in result_copy and isinstance(result_copy[content_key], str):
            content = result_copy[content_key]

            if not constraints.include_full_content:
                # Truncate to max_content_length
                truncated, was_truncated = truncate_content(
                    content, constraints.max_content_length, add_ellipsis=True
                )
                result_copy[content_key] = truncated
                if was_truncated:
                    content_truncated_count += 1
                    result_copy["_content_truncated"] = True

        # Estimate tokens for this result
        # Convert result to JSON-like string for estimation
        import json

        result_str = json.dumps(result_copy, ensure_ascii=False)
        result_tokens = estimate_tokens(result_str)

        # Check if adding this result would exceed limit
        if current_tokens + result_tokens > available_tokens:
            # Stop here - we've reached the limit
            print(
                f"⚠️  Stopping at {len(truncated_results)} results to stay within token limit",
                file=sys.stderr,
                flush=True,
            )
            break

        # Add result and update token count
        truncated_results.append(result_copy)
        current_tokens += result_tokens

    # Build truncation info
    truncation_info = {
        "truncated": len(truncated_results) < len(results) or content_truncated_count > 0,
        "original_count": len(results),
        "final_count": len(truncated_results),
        "content_truncated_count": content_truncated_count,
        "estimated_tokens": current_tokens,
    }

    # Log truncation if it occurred
    if truncation_info["truncated"]:
        print(
            f"⚠️  Response truncated: {truncation_info['original_count']} → "
            f"{truncation_info['final_count']} results, "
            f"{truncation_info['content_truncated_count']} contents truncated",
            file=sys.stderr,
            flush=True,
        )
        print(
            f"    Estimated tokens: {truncation_info['estimated_tokens']} / "
            f"{constraints.max_response_tokens}",
            file=sys.stderr,
            flush=True,
        )

    return truncated_results, truncation_info


def generate_truncation_warning(
    truncation_info: dict[str, Any], max_content_length: int
) -> str | None:
    """
    Generate a warning message for truncated responses.

    Args:
        truncation_info: Truncation information from truncate_results_to_fit
        max_content_length: Maximum content length used

    Returns:
        Warning message if truncation occurred, None otherwise
    """
    if not truncation_info.get("truncated"):
        return None

    warnings = []

    # Results truncated
    if truncation_info["final_count"] < truncation_info["original_count"]:
        dropped = truncation_info["original_count"] - truncation_info["final_count"]
        warnings.append(
            f"Only showing {truncation_info['final_count']} of "
            f"{truncation_info['original_count']} results (dropped {dropped} "
            "to stay within token limit)"
        )

    # Content truncated
    if truncation_info["content_truncated_count"] > 0:
        warnings.append(
            f"{truncation_info['content_truncated_count']} content fields truncated "
            f"to {max_content_length} characters"
        )

    # Pagination suggestion
    if truncation_info["final_count"] < truncation_info["original_count"]:
        warnings.append("Use offset and max_documents parameters to paginate through all results")

    return " | ".join(warnings)


__all__ = [
    "SizeConstraints",
    "estimate_tokens",
    "truncate_content",
    "truncate_results_to_fit",
    "generate_truncation_warning",
]
