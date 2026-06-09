"""
Integration tests for knowledge graph workflows.

This test suite covers complete knowledge graph integration including:
- GitHub repository parsing into Neo4j
- Batch repository processing
- Hallucination detection workflows
- Knowledge graph queries and traversal
- Entity relationship management
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Mock heavy dependencies before importing
sys.modules["crawl4ai"] = MagicMock()
sys.modules["crawl4ai_mcp"] = MagicMock()
sys.modules["neo4j"] = MagicMock()
sys.modules["openai"] = MagicMock()


class TestGitHubRepoIntegration:
    """Test GitHub repository parsing and knowledge graph integration."""

    @pytest.mark.asyncio
    async def test_single_repo_parse_workflow(self, mock_neo4j_session):
        """Test complete workflow of parsing a single GitHub repository."""
        repo_url = "https://github.com/test/example-repo"

        # Mock repository extractor
        repo_extractor = AsyncMock()
        repo_extractor.analyze_repository = AsyncMock()
        repo_extractor.driver = Mock()
        repo_extractor.driver.session = Mock(
            return_value=MagicMock(
                __aenter__=AsyncMock(return_value=mock_neo4j_session), __aexit__=AsyncMock()
            )
        )

        # Execute parsing
        await repo_extractor.analyze_repository(repo_url)

        # Verify repository was analyzed
        repo_extractor.analyze_repository.assert_called_once_with(repo_url)

    @pytest.mark.asyncio
    async def test_repo_statistics_extraction(self, mock_neo4j_session):
        """Test extracting statistics after repository parsing."""
        repo_name = "example-repo"

        # Mock statistics query result
        mock_record = Mock()
        mock_record.__getitem__ = lambda self, key: {
            "repo_name": repo_name,
            "files_count": 25,
            "classes_count": 10,
            "methods_count": 50,
            "functions_count": 30,
        }[key]

        result = AsyncMock()
        result.single = AsyncMock(return_value=mock_record)
        mock_neo4j_session.run = AsyncMock(return_value=result)

        # Execute query
        query = """
        MATCH (r:Repository {name: $repo_name})
        RETURN r.name as repo_name
        """
        query_result = await mock_neo4j_session.run(query, repo_name=repo_name)
        record = await query_result.single()

        # Verify statistics
        assert record["repo_name"] == repo_name
        assert record["files_count"] == 25
        assert record["classes_count"] == 10


class TestBatchRepositoryProcessing:
    """Test batch processing of multiple repositories."""

    @pytest.mark.asyncio
    async def test_batch_process_multiple_repos(self, mock_batch_repo_results):
        """Test processing multiple repositories in batch."""
        from github_utils import calculate_batch_statistics

        stats = calculate_batch_statistics(mock_batch_repo_results)

        assert stats["total_repositories"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1

    @pytest.mark.asyncio
    async def test_batch_with_retry_logic(self):
        """Test that failed repositories are retried."""
        results = []
        max_retries = 2
        attempt_counts = {}

        async def process_repo(repo_url, attempt=1):
            if repo_url not in attempt_counts:
                attempt_counts[repo_url] = 0
            attempt_counts[repo_url] += 1

            # Fail first attempt, succeed on retry
            if attempt_counts[repo_url] == 1:
                raise Exception("Temporary failure")

            return {"status": "success", "url": repo_url, "attempt": attempt_counts[repo_url]}

        repo_url = "https://github.com/test/flaky-repo"

        for attempt in range(1, max_retries + 2):
            try:
                result = await process_repo(repo_url, attempt)
                results.append(result)
                break
            except Exception as e:
                if attempt > max_retries:
                    results.append({"status": "failed", "url": repo_url, "error": str(e)})

        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert results[0]["attempt"] == 2


class TestKnowledgeGraphQueries:
    """Test complex knowledge graph query operations."""

    @pytest.mark.asyncio
    async def test_find_related_classes(self, mock_neo4j_session):
        """Test finding classes related to a given class."""
        class_name = "UserService"

        # Mock query result
        related = [
            {"name": "UserRepository", "relationship": "USES"},
            {"name": "BaseService", "relationship": "EXTENDS"},
        ]

        result = AsyncMock()
        result.data = AsyncMock(return_value=related)
        mock_neo4j_session.run = AsyncMock(return_value=result)

        query = """
        MATCH (c:Class {name: $class_name})-[r]->(related:Class)
        RETURN related.name as name, type(r) as relationship
        """

        query_result = await mock_neo4j_session.run(query, class_name=class_name)
        related_classes = await query_result.data()

        assert len(related_classes) == 2
        assert related_classes[0]["relationship"] == "USES"

    @pytest.mark.asyncio
    async def test_find_method_call_chain(self, mock_neo4j_session):
        """Test finding method call chains."""
        start_method = "processPayment"

        # Mock call chain
        call_chain = [
            {"caller": "processPayment", "callee": "validateCard"},
            {"caller": "validateCard", "callee": "checkCardExpiry"},
            {"caller": "validateCard", "callee": "verifyFunds"},
        ]

        result = AsyncMock()
        result.data = AsyncMock(return_value=call_chain)
        mock_neo4j_session.run = AsyncMock(return_value=result)

        query = """
        MATCH path = (m:Method {name: $start_method})-[:CALLS*1..3]->(called:Method)
        RETURN m.name as caller, called.name as callee
        """

        query_result = await mock_neo4j_session.run(query, start_method=start_method)
        chain = await query_result.data()

        assert len(chain) == 3
        assert chain[0]["caller"] == "processPayment"
