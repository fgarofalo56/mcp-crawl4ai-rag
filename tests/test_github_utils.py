"""
Unit tests for GitHub utilities module.

Tests cover validation, statistics calculation, response building,
and single repository processing functions.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add src to path without importing the main module
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import github_utils
from github_utils import (
    build_batch_response,
    calculate_batch_statistics,
    print_batch_summary,
    process_single_repository,
    validate_batch_input,
    validate_repository_urls,
)


class TestValidateBatchInput:
    """Tests for validate_batch_input function."""

    def test_valid_input(self):
        """Test with valid JSON array input."""
        json_input = '["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]'
        urls, max_concurrent, max_retries = validate_batch_input(json_input, 3, 2)

        assert urls == [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git",
        ]
        assert max_concurrent == 3
        assert max_retries == 2

    def test_invalid_json(self):
        """Test with invalid JSON string."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            validate_batch_input("not valid json", 3, 2)

    def test_not_a_list(self):
        """Test with JSON that's not an array."""
        with pytest.raises(ValueError, match="must be a JSON array"):
            validate_batch_input('{"url": "test"}', 3, 2)

    def test_empty_list(self):
        """Test with empty array."""
        with pytest.raises(ValueError, match="No repository URLs provided"):
            validate_batch_input("[]", 3, 2)

    def test_invalid_max_concurrent(self):
        """Test with invalid max_concurrent value."""
        with pytest.raises(ValueError, match="max_concurrent must be greater than 0"):
            validate_batch_input('["https://github.com/user/repo.git"]', 0, 2)

    def test_negative_max_concurrent(self):
        """Test with negative max_concurrent value."""
        with pytest.raises(ValueError, match="max_concurrent must be greater than 0"):
            validate_batch_input('["https://github.com/user/repo.git"]', -1, 2)

    def test_negative_max_retries(self):
        """Test with negative max_retries value."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            validate_batch_input('["https://github.com/user/repo.git"]', 3, -1)

    def test_zero_max_retries(self):
        """Test that zero retries is valid."""
        json_input = '["https://github.com/user/repo.git"]'
        urls, max_concurrent, max_retries = validate_batch_input(json_input, 3, 0)

        assert max_retries == 0


class TestValidateRepositoryUrls:
    """Tests for validate_repository_urls function."""

    def test_all_valid_urls(self):
        """Test with all valid GitHub URLs."""
        mock_validator = Mock(
            side_effect=[
                {"valid": True, "repo_name": "repo1"},
                {"valid": True, "repo_name": "repo2"},
            ]
        )

        urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git",
        ]
        validated, errors = validate_repository_urls(urls, mock_validator)

        assert len(validated) == 2
        assert validated[0] == {"url": urls[0], "name": "repo1"}
        assert validated[1] == {"url": urls[1], "name": "repo2"}
        assert len(errors) == 0

    def test_mixed_valid_invalid_urls(self):
        """Test with mix of valid and invalid URLs."""
        mock_validator = Mock(
            side_effect=[
                {"valid": True, "repo_name": "repo1"},
                {"valid": False, "error": "Invalid URL format"},
                {"valid": True, "repo_name": "repo3"},
            ]
        )

        urls = [
            "https://github.com/user/repo1.git",
            "not-a-valid-url",
            "https://github.com/user/repo3.git",
        ]
        validated, errors = validate_repository_urls(urls, mock_validator)

        assert len(validated) == 2
        assert validated[0]["name"] == "repo1"
        assert validated[1]["name"] == "repo3"
        assert len(errors) == 1
        assert errors[0] == {"url": "not-a-valid-url", "error": "Invalid URL format"}

    def test_all_invalid_urls(self):
        """Test with all invalid URLs."""
        mock_validator = Mock(
            side_effect=[
                {"valid": False, "error": "Invalid URL 1"},
                {"valid": False, "error": "Invalid URL 2"},
            ]
        )

        urls = ["bad-url-1", "bad-url-2"]

        with pytest.raises(ValueError, match="No valid repository URLs found"):
            validate_repository_urls(urls, mock_validator)


class TestCalculateBatchStatistics:
    """Tests for calculate_batch_statistics function."""

    def test_all_successful_results(self):
        """Test with all successful repository processing results."""
        results = [
            {
                "status": "success",
                "attempt": 1,
                "statistics": {
                    "files_processed": 10,
                    "classes_created": 5,
                    "methods_created": 20,
                    "functions_created": 15,
                },
            },
            {
                "status": "success",
                "attempt": 1,
                "statistics": {
                    "files_processed": 8,
                    "classes_created": 3,
                    "methods_created": 12,
                    "functions_created": 10,
                },
            },
        ]

        stats = calculate_batch_statistics(results)

        assert stats["total_repositories"] == 2
        assert stats["successful"] == 2
        assert stats["failed"] == 0
        assert stats["retried"] == 0
        assert stats["aggregate_statistics"]["total_files_processed"] == 18
        assert stats["aggregate_statistics"]["total_classes_created"] == 8
        assert stats["aggregate_statistics"]["total_methods_created"] == 32
        assert stats["aggregate_statistics"]["total_functions_created"] == 25

    def test_mixed_success_failure(self):
        """Test with mix of successful and failed results."""
        results = [
            {
                "url": "https://github.com/user/repo1.git",
                "repository": "repo1",
                "status": "success",
                "attempt": 2,
                "statistics": {
                    "files_processed": 10,
                    "classes_created": 5,
                    "methods_created": 20,
                    "functions_created": 15,
                },
            },
            {
                "url": "https://github.com/user/repo2.git",
                "repository": "repo2",
                "status": "failed",
                "attempt": 3,
                "error": "Network error",
            },
        ]

        stats = calculate_batch_statistics(results)

        assert stats["total_repositories"] == 2
        assert stats["successful"] == 1
        assert stats["failed"] == 1
        assert stats["retried"] == 2  # Both had retries (attempt > 1)
        assert "aggregate_statistics" in stats
        assert stats["aggregate_statistics"]["total_files_processed"] == 10
        assert "failed_repositories" in stats
        assert len(stats["failed_repositories"]) == 1
        assert stats["failed_repositories"][0]["repository"] == "repo2"
        assert stats["failed_repositories"][0]["error"] == "Network error"
        assert stats["failed_repositories"][0]["attempts"] == 3
        assert stats["retry_urls"] == ["https://github.com/user/repo2.git"]

    def test_all_failed_results(self):
        """Test with all failed results."""
        results = [
            {
                "url": "https://github.com/user/repo1.git",
                "repository": "repo1",
                "status": "failed",
                "attempt": 1,
                "error": "Error 1",
            },
            {
                "url": "https://github.com/user/repo2.git",
                "repository": "repo2",
                "status": "failed",
                "attempt": 1,
                "error": "Error 2",
            },
        ]

        stats = calculate_batch_statistics(results)

        assert stats["total_repositories"] == 2
        assert stats["successful"] == 0
        assert stats["failed"] == 2
        assert stats["retried"] == 0
        assert "aggregate_statistics" not in stats
        assert len(stats["failed_repositories"]) == 2
        assert len(stats["retry_urls"]) == 2

    def test_empty_results(self):
        """Test with empty results list."""
        stats = calculate_batch_statistics([])

        assert stats["total_repositories"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["retried"] == 0


class TestBuildBatchResponse:
    """Tests for build_batch_response function."""

    def test_successful_response(self):
        """Test building response for successful batch."""
        results = [
            {
                "status": "success",
                "attempt": 1,
                "statistics": {
                    "files_processed": 10,
                    "classes_created": 5,
                    "methods_created": 20,
                    "functions_created": 15,
                },
            }
        ]
        validation_errors = []
        elapsed_time = 12.5

        response = build_batch_response(results, validation_errors, elapsed_time)

        assert response["success"] is True
        assert response["summary"]["total_repositories"] == 1
        assert response["summary"]["successful"] == 1
        assert response["summary"]["failed"] == 0
        assert response["summary"]["elapsed_seconds"] == 12.5
        assert response["summary"]["average_time_per_repo"] == 12.5
        assert response["summary"]["validation_errors"] == 0
        assert "validation_errors" not in response
        assert "failed_repositories" not in response
        assert "aggregate_statistics" in response

    def test_failed_response_with_validation_errors(self):
        """Test building response with failures and validation errors."""
        results = [
            {
                "url": "https://github.com/user/repo1.git",
                "repository": "repo1",
                "status": "failed",
                "attempt": 1,
                "error": "Failed to clone",
            }
        ]
        validation_errors = [{"url": "bad-url", "error": "Invalid format"}]
        elapsed_time = 5.0

        response = build_batch_response(results, validation_errors, elapsed_time)

        assert response["success"] is False
        assert response["summary"]["validation_errors"] == 1
        assert "validation_errors" in response
        assert response["validation_errors"] == validation_errors
        assert "failed_repositories" in response
        assert len(response["failed_repositories"]) == 1
        assert "retry_urls" in response

    def test_response_with_zero_elapsed_time(self):
        """Test that average time calculation handles zero total repos."""
        response = build_batch_response([], [], 0.0)

        assert response["summary"]["average_time_per_repo"] == 0


class TestPrintBatchSummary:
    """Tests for print_batch_summary function."""

    def test_print_summary_no_retries(self, capsys):
        """Test printing summary without retries."""
        print_batch_summary(10, 8, 2, 0)

        captured = capsys.readouterr()
        assert "Batch processing complete!" in captured.err
        assert "Successful: 8/10" in captured.err
        assert "Failed: 2/10" in captured.err
        assert "Retried" not in captured.err

    def test_print_summary_with_retries(self, capsys):
        """Test printing summary with retries."""
        print_batch_summary(10, 7, 3, 5)

        captured = capsys.readouterr()
        assert "Batch processing complete!" in captured.err
        assert "Successful: 7/10" in captured.err
        assert "Failed: 3/10" in captured.err
        assert "Retried: 5" in captured.err


class TestProcessSingleRepository:
    """Tests for process_single_repository async function."""

    @pytest.mark.asyncio
    async def test_successful_processing(self):
        """Test successful repository processing on first attempt."""
        # Mock repository extractor
        mock_extractor = AsyncMock()
        mock_extractor.analyze_repository = AsyncMock()

        # Mock Neo4j session and result
        mock_record = {
            "repo_name": "test-repo",
            "files_count": 10,
            "classes_count": 5,
            "methods_count": 20,
            "functions_count": 15,
        }
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=mock_record)

        mock_session = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_extractor.driver.session = Mock(return_value=mock_session)

        # Create test inputs
        repo_info = {"url": "https://github.com/user/test-repo.git", "name": "test-repo"}
        semaphore = asyncio.Semaphore(1)

        # Execute
        result = await process_single_repository(
            repo_info, mock_extractor, semaphore, max_retries=2
        )

        # Assert
        assert result["status"] == "success"
        assert result["repository"] == "test-repo"
        assert result["attempt"] == 1
        assert result["statistics"]["files_processed"] == 10
        assert result["statistics"]["classes_created"] == 5
        assert result["statistics"]["methods_created"] == 20
        assert result["statistics"]["functions_created"] == 15

    @pytest.mark.skip(reason="Async sleep mocking causes test to hang - needs investigation")
    @pytest.mark.asyncio
    @patch("builtins.print")  # Suppress print output
    @patch("github_utils.asyncio.sleep", new_callable=AsyncMock)  # Mock sleep
    async def test_processing_with_retry_success(self, mock_sleep, mock_print):
        """Test repository processing that fails first but succeeds on retry."""
        # Sleep is now an AsyncMock that returns immediately

        mock_extractor = AsyncMock()

        # Track call count
        call_count = [0]

        async def analyze_with_failure(url):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Network timeout")
            # Second call succeeds (no exception)

        mock_extractor.analyze_repository = analyze_with_failure

        # Mock successful Neo4j query (for second attempt)
        mock_record = {
            "repo_name": "test-repo",
            "files_count": 5,
            "classes_count": 2,
            "methods_count": 10,
            "functions_count": 8,
        }
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=mock_record)

        mock_session = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_extractor.driver.session = Mock(return_value=mock_session)

        repo_info = {"url": "https://github.com/user/test-repo.git", "name": "test-repo"}
        semaphore = asyncio.Semaphore(1)

        result = await process_single_repository(
            repo_info, mock_extractor, semaphore, max_retries=2
        )

        assert result["status"] == "success"
        assert result["attempt"] == 2  # Second attempt succeeded
        assert call_count[0] == 2  # Called twice

    @pytest.mark.skip(reason="Async sleep mocking causes test to hang - needs investigation")
    @pytest.mark.asyncio
    @patch("builtins.print")  # Suppress print output
    @patch("github_utils.asyncio.sleep", new_callable=AsyncMock)  # Mock sleep
    async def test_processing_exhausted_retries(self, mock_sleep, mock_print):
        """Test repository processing that exhausts all retries."""
        # Sleep is now an AsyncMock that returns immediately

        mock_extractor = AsyncMock()
        mock_extractor.analyze_repository = AsyncMock(side_effect=Exception("Persistent error"))

        repo_info = {"url": "https://github.com/user/test-repo.git", "name": "test-repo"}
        semaphore = asyncio.Semaphore(1)

        result = await process_single_repository(
            repo_info, mock_extractor, semaphore, max_retries=2
        )

        assert result["status"] == "failed"
        assert result["attempt"] == 3  # Initial + 2 retries
        assert "Persistent error" in result["error"]
        assert result["retries_exhausted"] is True

    @pytest.mark.asyncio
    async def test_processing_no_data_in_neo4j(self):
        """Test when repository is processed but no data found in Neo4j."""
        mock_extractor = AsyncMock()
        mock_extractor.analyze_repository = AsyncMock()

        # Mock Neo4j query returning None
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.run = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_extractor.driver.session = Mock(return_value=mock_session)

        repo_info = {"url": "https://github.com/user/test-repo.git", "name": "test-repo"}
        semaphore = asyncio.Semaphore(1)

        result = await process_single_repository(
            repo_info, mock_extractor, semaphore, max_retries=2
        )

        assert result["status"] == "failed"
        assert "no data found in Neo4j" in result["error"]

    @pytest.mark.asyncio
    @patch("builtins.print")  # Suppress print output
    async def test_processing_zero_retries(self, mock_print):
        """Test processing with max_retries set to 0."""
        mock_extractor = AsyncMock()
        mock_extractor.analyze_repository = AsyncMock(side_effect=Exception("Immediate failure"))

        repo_info = {"url": "https://github.com/user/test-repo.git", "name": "test-repo"}
        semaphore = asyncio.Semaphore(1)

        result = await process_single_repository(
            repo_info, mock_extractor, semaphore, max_retries=0
        )

        assert result["status"] == "failed"
        assert result["attempt"] == 1  # No retries
        assert result["retries_exhausted"] is True
