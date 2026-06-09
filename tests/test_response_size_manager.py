"""
Tests for response size management functionality.

This test suite verifies:
- Token estimation accuracy
- Content truncation with word boundaries
- Result set truncation to fit token limits
- Warning generation for truncated responses
"""

import pytest

from src.response_size_manager import (
    SizeConstraints,
    estimate_tokens,
    generate_truncation_warning,
    truncate_content,
    truncate_results_to_fit,
)


class TestEstimateTokens:
    """Tests for token estimation function."""

    def test_estimate_tokens_empty_string(self):
        """Test token estimation for empty string."""
        assert estimate_tokens("") == 0

    def test_estimate_tokens_short_text(self):
        """Test token estimation for short text."""
        text = "Hello world"
        tokens = estimate_tokens(text)
        # Rough estimate: 1 token ≈ 4 chars
        assert tokens == len(text) // 4

    def test_estimate_tokens_long_text(self):
        """Test token estimation for long text."""
        text = "A" * 1000
        tokens = estimate_tokens(text)
        assert tokens == 250  # 1000 / 4

    def test_estimate_tokens_none(self):
        """Test token estimation for None."""
        assert estimate_tokens(None) == 0


class TestTruncateContent:
    """Tests for content truncation function."""

    def test_truncate_content_no_truncation_needed(self):
        """Test that short content is not truncated."""
        content = "Short text"
        truncated, was_truncated = truncate_content(content, max_length=100)
        assert truncated == content
        assert was_truncated is False

    def test_truncate_content_at_word_boundary(self):
        """Test that truncation respects word boundaries."""
        content = "The quick brown fox jumps over the lazy dog"
        truncated, was_truncated = truncate_content(content, max_length=20)
        assert was_truncated is True
        assert truncated.endswith(" ...")
        # Should not cut mid-word
        assert "jump" not in truncated or "jumps" in truncated

    def test_truncate_content_with_ellipsis(self):
        """Test that ellipsis is added when truncated."""
        content = "A" * 100
        truncated, was_truncated = truncate_content(content, max_length=50, add_ellipsis=True)
        assert was_truncated is True
        assert truncated.endswith(" ...")
        assert len(truncated) <= 50

    def test_truncate_content_without_ellipsis(self):
        """Test truncation without ellipsis."""
        content = "A" * 100
        truncated, was_truncated = truncate_content(content, max_length=50, add_ellipsis=False)
        assert was_truncated is True
        assert not truncated.endswith(" ...")
        assert len(truncated) <= 50

    def test_truncate_content_empty_string(self):
        """Test truncation of empty string."""
        truncated, was_truncated = truncate_content("", max_length=100)
        assert truncated == ""
        assert was_truncated is False

    def test_truncate_content_exact_length(self):
        """Test content exactly at max length."""
        content = "A" * 100
        truncated, was_truncated = truncate_content(content, max_length=100)
        assert truncated == content
        assert was_truncated is False


class TestTruncateResultsToFit:
    """Tests for result set truncation function."""

    def test_truncate_results_empty_list(self):
        """Test truncation of empty results list."""
        results = []
        constraints = SizeConstraints()
        truncated, info = truncate_results_to_fit(results, constraints)
        assert truncated == []
        assert info["original_count"] == 0
        assert info["final_count"] == 0
        assert info["truncated"] is False

    def test_truncate_results_within_limits(self):
        """Test that small result sets are not truncated."""
        results = [
            {"content": "Short text 1", "url": "http://example.com/1"},
            {"content": "Short text 2", "url": "http://example.com/2"},
        ]
        constraints = SizeConstraints(max_response_tokens=10000)
        truncated, info = truncate_results_to_fit(results, constraints)
        assert len(truncated) == 2
        assert info["truncated"] is False

    def test_truncate_results_exceeds_token_limit(self):
        """Test that large result sets are truncated."""
        # Create large results that will exceed token limit
        results = [{"content": "A" * 10000, "url": f"http://example.com/{i}"} for i in range(20)]
        constraints = SizeConstraints(max_response_tokens=5000, reserved_tokens=500)
        truncated, info = truncate_results_to_fit(results, constraints)
        # Should have fewer results than original
        assert len(truncated) < len(results)
        assert info["truncated"] is True
        assert info["original_count"] == 20
        assert info["final_count"] < 20

    def test_truncate_results_content_truncation(self):
        """Test that individual content fields are truncated."""
        results = [
            {"content": "A" * 5000, "url": "http://example.com/1"},
            {"content": "B" * 5000, "url": "http://example.com/2"},
        ]
        constraints = SizeConstraints(
            max_response_tokens=10000,
            max_content_length=100,
            include_full_content=False,
        )
        truncated, info = truncate_results_to_fit(results, constraints)
        # Content should be truncated
        assert len(truncated[0]["content"]) <= 104  # 100 + " ..."
        assert info["content_truncated_count"] > 0

    def test_truncate_results_preserve_structure(self):
        """Test that result structure is preserved."""
        results = [
            {
                "content": "Test content",
                "url": "http://example.com/1",
                "metadata": {"key": "value"},
                "similarity": 0.95,
            }
        ]
        constraints = SizeConstraints()
        truncated, info = truncate_results_to_fit(results, constraints)
        assert "url" in truncated[0]
        assert "metadata" in truncated[0]
        assert "similarity" in truncated[0]

    def test_truncate_results_marks_truncated_content(self):
        """Test that truncated content is marked."""
        results = [{"content": "A" * 5000, "url": "http://example.com/1"}]
        constraints = SizeConstraints(max_content_length=100, include_full_content=False)
        truncated, info = truncate_results_to_fit(results, constraints)
        assert truncated[0].get("_content_truncated") is True

    def test_truncate_results_custom_content_key(self):
        """Test truncation with custom content key."""
        results = [
            {"body": "A" * 5000, "url": "http://example.com/1"},
            {"body": "B" * 5000, "url": "http://example.com/2"},
        ]
        constraints = SizeConstraints(max_content_length=100, include_full_content=False)
        truncated, info = truncate_results_to_fit(results, constraints, content_key="body")
        assert len(truncated[0]["body"]) <= 104  # 100 + " ..."


class TestGenerateTruncationWarning:
    """Tests for truncation warning generation."""

    def test_no_warning_when_not_truncated(self):
        """Test that no warning is generated when nothing is truncated."""
        truncation_info = {
            "truncated": False,
            "original_count": 5,
            "final_count": 5,
            "content_truncated_count": 0,
        }
        warning = generate_truncation_warning(truncation_info, max_content_length=1000)
        assert warning is None

    def test_warning_for_dropped_results(self):
        """Test warning when results are dropped."""
        truncation_info = {
            "truncated": True,
            "original_count": 10,
            "final_count": 5,
            "content_truncated_count": 0,
        }
        warning = generate_truncation_warning(truncation_info, max_content_length=1000)
        assert warning is not None
        assert "5 of 10" in warning
        assert "dropped 5" in warning

    def test_warning_for_truncated_content(self):
        """Test warning when content is truncated."""
        truncation_info = {
            "truncated": True,
            "original_count": 5,
            "final_count": 5,
            "content_truncated_count": 3,
        }
        warning = generate_truncation_warning(truncation_info, max_content_length=500)
        assert warning is not None
        assert "3 content fields" in warning
        assert "500 characters" in warning

    def test_warning_includes_pagination_suggestion(self):
        """Test that warning includes pagination suggestion."""
        truncation_info = {
            "truncated": True,
            "original_count": 20,
            "final_count": 10,
            "content_truncated_count": 0,
        }
        warning = generate_truncation_warning(truncation_info, max_content_length=1000)
        assert "offset" in warning
        assert "paginate" in warning

    def test_warning_combines_multiple_issues(self):
        """Test warning with multiple truncation issues."""
        truncation_info = {
            "truncated": True,
            "original_count": 20,
            "final_count": 10,
            "content_truncated_count": 5,
        }
        warning = generate_truncation_warning(truncation_info, max_content_length=500)
        assert warning is not None
        # Should contain multiple parts separated by " | "
        assert " | " in warning


class TestSizeConstraints:
    """Tests for SizeConstraints dataclass."""

    def test_default_constraints(self):
        """Test default constraint values."""
        constraints = SizeConstraints()
        assert constraints.max_response_tokens == 20000
        assert constraints.max_content_length == 1000
        assert constraints.include_full_content is True
        assert constraints.reserved_tokens == 2000

    def test_custom_constraints(self):
        """Test custom constraint values."""
        constraints = SizeConstraints(
            max_response_tokens=15000,
            max_content_length=500,
            include_full_content=False,
            reserved_tokens=1000,
        )
        assert constraints.max_response_tokens == 15000
        assert constraints.max_content_length == 500
        assert constraints.include_full_content is False
        assert constraints.reserved_tokens == 1000


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_full_truncation_workflow(self):
        """Test complete truncation workflow."""
        # Create realistic search results with very large content
        results = [
            {
                "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                * 500,  # Much larger content
                "url": f"http://example.com/doc{i}",
                "similarity": 0.9 - (i * 0.05),
            }
            for i in range(50)  # More results
        ]

        # Apply strict constraints to force result truncation
        constraints = SizeConstraints(
            max_response_tokens=2000,  # Very low token limit
            max_content_length=200,
            include_full_content=False,
            reserved_tokens=500,
        )
        truncated, info = truncate_results_to_fit(results, constraints)

        # Verify truncation occurred
        assert info["truncated"] is True
        # Either results were dropped OR content was truncated (or both)
        assert len(truncated) <= len(results)
        assert info["content_truncated_count"] > 0 or len(truncated) < len(results)

        # Verify content is truncated
        for result in truncated:
            assert len(result["content"]) <= 204  # 200 + " ..."

        # Generate warning
        warning = generate_truncation_warning(info, constraints.max_content_length)
        assert warning is not None

    def test_no_truncation_needed_workflow(self):
        """Test workflow when no truncation is needed."""
        results = [
            {
                "content": "Short content",
                "url": f"http://example.com/doc{i}",
                "similarity": 0.9,
            }
            for i in range(3)
        ]

        constraints = SizeConstraints(max_response_tokens=20000)
        truncated, info = truncate_results_to_fit(results, constraints)

        # Should not be truncated
        assert info["truncated"] is False
        assert len(truncated) == len(results)
        assert generate_truncation_warning(info, 1000) is None
