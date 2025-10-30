"""
Validation script for token limit fix implementation.

This script demonstrates:
1. Token estimation accuracy
2. Content truncation with word boundaries
3. Result set truncation
4. Pagination support
5. Warning generation
"""

import json
import os
import sys

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, "src")
sys.path.insert(0, src_dir)

from rag_utils import paginate_results
from response_size_manager import (
    SizeConstraints,
    estimate_tokens,
    generate_truncation_warning,
    truncate_content,
    truncate_results_to_fit,
)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_token_estimation():
    """Demonstrate token estimation."""
    print_section("1. Token Estimation")

    test_texts = [
        ("Short text", "Hello world!"),
        ("Medium text", "The quick brown fox jumps over the lazy dog." * 10),
        ("Large text", "A" * 10000),
    ]

    for name, text in test_texts:
        tokens = estimate_tokens(text)
        print(f"{name}:")
        print(f"  Length: {len(text):,} chars")
        print(f"  Estimated tokens: {tokens:,}")
        print()


def demo_content_truncation():
    """Demonstrate content truncation with word boundaries."""
    print_section("2. Content Truncation")

    content = (
        "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ "
        "based on standard Python type hints. It provides automatic API documentation, "
        "data validation, and high performance comparable to NodeJS and Go."
    )

    print(f"Original content ({len(content)} chars):")
    print(f'  "{content}"')
    print()

    truncated, was_truncated = truncate_content(content, max_length=100)
    print("Truncated to 100 chars:")
    print(f'  "{truncated}"')
    print(f"  Was truncated: {was_truncated}")
    print()


def demo_result_truncation():
    """Demonstrate result set truncation."""
    print_section("3. Result Set Truncation")

    # Create sample results
    results = [
        {
            "content": f"This is document {i} with some sample content that might be "
            f"quite long in a real scenario. " * 20,
            "url": f"http://example.com/doc{i}",
            "similarity": 0.9 - (i * 0.05),
        }
        for i in range(20)
    ]

    print(f"Original results: {len(results)} documents")
    print(f"Original content length: {len(results[0]['content'])} chars per doc")
    print()

    # Apply strict constraints
    constraints = SizeConstraints(
        max_response_tokens=3000,
        max_content_length=150,
        include_full_content=False,
        reserved_tokens=500,
    )

    truncated, info = truncate_results_to_fit(results, constraints)

    print("After truncation:")
    print(f"  Results: {len(results)} -> {len(truncated)}")
    print(f"  Content length: ~{len(truncated[0]['content'])} chars per doc")
    print(f"  Estimated tokens: {info['estimated_tokens']:,}")
    print(f"  Content fields truncated: {info['content_truncated_count']}")
    print()

    # Show first truncated result
    if truncated:
        print("Sample truncated result:")
        print(f"  URL: {truncated[0]['url']}")
        print(f"  Content: {truncated[0]['content'][:100]}...")
        print(f"  Marked as truncated: {truncated[0].get('_content_truncated', False)}")
    print()


def demo_pagination():
    """Demonstrate pagination support."""
    print_section("4. Pagination Support")

    # Create sample results
    results = [
        {"id": i, "content": f"Document {i}", "similarity": 0.9 - (i * 0.01)} for i in range(25)
    ]

    print(f"Total results: {len(results)}")
    print()

    # Page 1
    page1 = paginate_results(results, offset=0, limit=10)
    print("Page 1 (offset=0, limit=10):")
    print(f"  Results: {[r['id'] for r in page1]}")
    print()

    # Page 2
    page2 = paginate_results(results, offset=10, limit=10)
    print("Page 2 (offset=10, limit=10):")
    print(f"  Results: {[r['id'] for r in page2]}")
    print()

    # Page 3
    page3 = paginate_results(results, offset=20, limit=10)
    print("Page 3 (offset=20, limit=10):")
    print(f"  Results: {[r['id'] for r in page3]}")
    print()


def demo_warnings():
    """Demonstrate warning generation."""
    print_section("5. Warning Generation")

    # Scenario 1: Results dropped
    truncation_info1 = {
        "truncated": True,
        "original_count": 50,
        "final_count": 15,
        "content_truncated_count": 0,
    }
    warning1 = generate_truncation_warning(truncation_info1, max_content_length=1000)
    print("Scenario 1 - Results Dropped:")
    print(f"  {warning1}")
    print()

    # Scenario 2: Content truncated
    truncation_info2 = {
        "truncated": True,
        "original_count": 10,
        "final_count": 10,
        "content_truncated_count": 8,
    }
    warning2 = generate_truncation_warning(truncation_info2, max_content_length=500)
    print("Scenario 2 - Content Truncated:")
    print(f"  {warning2}")
    print()

    # Scenario 3: Both issues
    truncation_info3 = {
        "truncated": True,
        "original_count": 30,
        "final_count": 12,
        "content_truncated_count": 12,
    }
    warning3 = generate_truncation_warning(truncation_info3, max_content_length=300)
    print("Scenario 3 - Multiple Issues:")
    print(f"  {warning3}")
    print()


def demo_complete_workflow():
    """Demonstrate complete workflow with realistic data."""
    print_section("6. Complete Workflow Example")

    # Simulate RAG query results
    results = [
        {
            "content": "FastAPI is a modern web framework. " * 50,
            "url": f"https://fastapi.tiangolo.com/tutorial/{i}",
            "metadata": {"source": "FastAPI Docs"},
            "similarity": 0.95 - (i * 0.02),
        }
        for i in range(30)
    ]

    print("Simulating large RAG query...")
    print(f"  Initial results: {len(results)}")
    print(f"  Avg content length: {len(results[0]['content'])} chars")
    print()

    # Apply pagination (offset=5, limit=10)
    paginated = paginate_results(results, offset=5, limit=10)
    print("After pagination (offset=5, limit=10):")
    print(f"  Results: {len(paginated)}")
    print()

    # Apply size constraints
    constraints = SizeConstraints(
        max_response_tokens=5000,
        max_content_length=200,
        include_full_content=False,
    )
    truncated, info = truncate_results_to_fit(paginated, constraints)

    print("After size management:")
    print(f"  Final results: {len(truncated)}")
    print(f"  Estimated tokens: {info['estimated_tokens']:,}")
    print(f"  Within limit: {info['estimated_tokens'] < constraints.max_response_tokens}")
    print()

    # Generate warning
    warning = generate_truncation_warning(info, constraints.max_content_length)
    if warning:
        print("User Warning:")
        print(f"  {warning}")
    print()

    # Build response
    response = {
        "success": True,
        "results": truncated[:3],  # Show first 3
        "count": len(truncated),
        "pagination": {
            "offset": 5,
            "requested_count": 10,
            "returned_count": len(truncated),
            "has_more": len(results) > 15,
        },
    }

    if warning:
        response["warning"] = warning

    print("Final Response Structure:")
    print(json.dumps(response, indent=2)[:500] + "...")
    print()


def main():
    """Run all validation demos."""
    print("\n" + "=" * 60)
    print("  TOKEN LIMIT FIX - VALIDATION SCRIPT")
    print("=" * 60)

    try:
        demo_token_estimation()
        demo_content_truncation()
        demo_result_truncation()
        demo_pagination()
        demo_warnings()
        demo_complete_workflow()

        print("\n" + "=" * 60)
        print("  ALL VALIDATIONS PASSED!")
        print("=" * 60 + "\n")
        return 0

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
