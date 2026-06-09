"""
Tests for Knowledge Graph Commands Module

This module tests the KnowledgeGraphCommands class which provides a command
pattern implementation for querying Neo4j knowledge graphs.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.knowledge_graph_commands import KnowledgeGraphCommands


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver."""
    driver = MagicMock()
    session = AsyncMock()
    driver.session.return_value.__aenter__.return_value = session
    driver.session.return_value.__aexit__.return_value = None
    return driver, session


@pytest.fixture
def command_handler(mock_neo4j_driver):
    """Create a KnowledgeGraphCommands instance with mock driver."""
    driver, _ = mock_neo4j_driver
    return KnowledgeGraphCommands(driver)


class TestKnowledgeGraphCommandsInit:
    """Test initialization of KnowledgeGraphCommands."""

    def test_init_with_driver(self, mock_neo4j_driver):
        """Test that initialization sets up driver and command registry."""
        driver, _ = mock_neo4j_driver
        handler = KnowledgeGraphCommands(driver)

        assert handler.driver == driver
        assert "repos" in handler.commands
        assert "explore" in handler.commands
        assert "classes" in handler.commands
        assert "class" in handler.commands
        assert "method" in handler.commands
        assert "query" in handler.commands


class TestExecuteCommand:
    """Test command execution and dispatch."""

    @pytest.mark.asyncio
    async def test_execute_empty_command(self, command_handler):
        """Test that empty command returns error."""
        result = await command_handler.execute("")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "cannot be empty" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_unknown_command(self, command_handler):
        """Test that unknown command returns error."""
        result = await command_handler.execute("unknown_cmd")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "unknown command" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_repos_command(self, command_handler, mock_neo4j_driver):
        """Test repos command execution."""
        _, session = mock_neo4j_driver

        # Mock the query result
        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter([{"name": "repo1"}, {"name": "repo2"}])
        session.run.return_value = mock_result

        result = await command_handler.execute("repos")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert "repositories" in result_data["data"]
        assert len(result_data["data"]["repositories"]) == 2


class TestReposCommand:
    """Test 'repos' command handler."""

    @pytest.mark.asyncio
    async def test_handle_repos_success(self, command_handler, mock_neo4j_driver):
        """Test successful repos command."""
        _, session = mock_neo4j_driver

        # Mock the query result
        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter([{"name": "pydantic-ai"}, {"name": "fastapi"}])
        session.run.return_value = mock_result

        result = await command_handler.execute("repos")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["repositories"] == ["pydantic-ai", "fastapi"]
        assert result_data["metadata"]["total_results"] == 2
        assert result_data["metadata"]["limited"] is False

    @pytest.mark.asyncio
    async def test_handle_repos_empty(self, command_handler, mock_neo4j_driver):
        """Test repos command with no repositories."""
        _, session = mock_neo4j_driver

        # Mock empty result
        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter([])
        session.run.return_value = mock_result

        result = await command_handler.execute("repos")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["repositories"] == []
        assert result_data["metadata"]["total_results"] == 0


class TestExploreCommand:
    """Test 'explore <repo>' command handler."""

    @pytest.mark.asyncio
    async def test_explore_missing_repo_name(self, command_handler):
        """Test explore command without repo name."""
        result = await command_handler.execute("explore")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "repository name required" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_explore_nonexistent_repo(self, command_handler, mock_neo4j_driver):
        """Test explore command with nonexistent repo."""
        _, session = mock_neo4j_driver

        # Mock repo check returning None
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)
        session.run.return_value = mock_result

        result = await command_handler.execute("explore nonexistent")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_explore_success(self, command_handler, mock_neo4j_driver):
        """Test successful explore command."""
        _, session = mock_neo4j_driver

        # Track call order
        call_count = [0]

        # Mock multiple queries for explore command
        async def mock_run(query, **kwargs):
            result = AsyncMock()
            call_count[0] += 1

            if call_count[0] == 1:
                # First call: Repo check
                result.single = AsyncMock(return_value={"name": "pydantic-ai"})
            elif call_count[0] == 2:
                # Second call: File count
                result.single = AsyncMock(return_value={"file_count": 10})
            elif call_count[0] == 3:
                # Third call: Class count
                result.single = AsyncMock(return_value={"class_count": 5})
            elif call_count[0] == 4:
                # Fourth call: Function count
                result.single = AsyncMock(return_value={"function_count": 15})
            elif call_count[0] == 5:
                # Fifth call: Method count
                result.single = AsyncMock(return_value={"method_count": 25})
            return result

        session.run = mock_run

        result = await command_handler.execute("explore pydantic-ai")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["repository"] == "pydantic-ai"
        assert result_data["data"]["statistics"]["files"] == 10
        assert result_data["data"]["statistics"]["classes"] == 5
        assert result_data["data"]["statistics"]["functions"] == 15
        assert result_data["data"]["statistics"]["methods"] == 25


class TestClassesCommand:
    """Test 'classes [repo]' command handler."""

    @pytest.mark.asyncio
    async def test_classes_all_repos(self, command_handler, mock_neo4j_driver):
        """Test classes command for all repositories."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter(
            [
                {"name": "Agent", "full_name": "pydantic_ai.Agent"},
                {"name": "Model", "full_name": "pydantic_ai.Model"},
            ]
        )
        session.run.return_value = mock_result

        result = await command_handler.execute("classes")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]["classes"]) == 2
        assert result_data["data"]["repository_filter"] is None

    @pytest.mark.asyncio
    async def test_classes_specific_repo(self, command_handler, mock_neo4j_driver):
        """Test classes command for specific repository."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter(
            [{"name": "Agent", "full_name": "pydantic_ai.Agent"}]
        )
        session.run.return_value = mock_result

        result = await command_handler.execute("classes pydantic-ai")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]["classes"]) == 1
        assert result_data["data"]["repository_filter"] == "pydantic-ai"


class TestClassCommand:
    """Test 'class <name>' command handler."""

    @pytest.mark.asyncio
    async def test_class_missing_name(self, command_handler):
        """Test class command without class name."""
        result = await command_handler.execute("class")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "class name required" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_class_not_found(self, command_handler, mock_neo4j_driver):
        """Test class command with nonexistent class."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value=None)
        session.run.return_value = mock_result

        result = await command_handler.execute("class NonExistent")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_class_success(self, command_handler, mock_neo4j_driver):
        """Test successful class command."""
        _, session = mock_neo4j_driver

        # Mock query results
        async def mock_run(query, **kwargs):
            result = AsyncMock()
            if "RETURN c.name as name" in query:
                # Class lookup
                result.single = AsyncMock(
                    return_value={"name": "Agent", "full_name": "pydantic_ai.Agent"}
                )
            elif "HAS_METHOD" in query:
                # Methods
                result.__aiter__.return_value = iter(
                    [
                        {
                            "name": "__init__",
                            "params_list": ["self"],
                            "params_detailed": None,
                            "return_type": "None",
                        }
                    ]
                )
            elif "HAS_ATTRIBUTE" in query:
                # Attributes
                result.__aiter__.return_value = iter([{"name": "model", "type": "str"}])
            return result

        session.run = mock_run

        result = await command_handler.execute("class Agent")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["class"]["name"] == "Agent"
        assert result_data["metadata"]["methods_count"] == 1
        assert result_data["metadata"]["attributes_count"] == 1


class TestMethodCommand:
    """Test 'method <name> [class]' command handler."""

    @pytest.mark.asyncio
    async def test_method_missing_name(self, command_handler):
        """Test method command without method name."""
        result = await command_handler.execute("method")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "method name required" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_method_not_found(self, command_handler, mock_neo4j_driver):
        """Test method command with nonexistent method."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter([])
        session.run.return_value = mock_result

        result = await command_handler.execute("method nonexistent_method")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "not found" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_method_search_all_classes(self, command_handler, mock_neo4j_driver):
        """Test method search across all classes."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter(
            [
                {
                    "class_name": "Agent",
                    "class_full_name": "pydantic_ai.Agent",
                    "method_name": "run",
                    "params_list": ["self"],
                    "params_detailed": None,
                    "return_type": "str",
                    "args": [],
                }
            ]
        )
        session.run.return_value = mock_result

        result = await command_handler.execute("method run")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]["methods"]) == 1
        assert result_data["data"]["class_filter"] is None

    @pytest.mark.asyncio
    async def test_method_search_specific_class(self, command_handler, mock_neo4j_driver):
        """Test method search in specific class."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter(
            [
                {
                    "class_name": "Agent",
                    "class_full_name": "pydantic_ai.Agent",
                    "method_name": "__init__",
                    "params_list": ["self"],
                    "params_detailed": None,
                    "return_type": "None",
                    "args": [],
                }
            ]
        )
        session.run.return_value = mock_result

        result = await command_handler.execute("method __init__ Agent")
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["data"]["class_filter"] == "Agent"


class TestQueryCommand:
    """Test 'query <cypher>' command handler."""

    @pytest.mark.asyncio
    async def test_query_missing_cypher(self, command_handler):
        """Test query command without Cypher query."""
        result = await command_handler.execute("query")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "query required" in result_data["error"].lower()

    @pytest.mark.asyncio
    async def test_query_success(self, command_handler, mock_neo4j_driver):
        """Test successful custom Cypher query."""
        _, session = mock_neo4j_driver

        mock_result = AsyncMock()
        mock_result.__aiter__.return_value = iter(
            [{"name": "Agent", "count": 5}, {"name": "Model", "count": 3}]
        )
        session.run.return_value = mock_result

        result = await command_handler.execute(
            "query MATCH (c:Class) RETURN c.name as name LIMIT 2"
        )
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert len(result_data["data"]["results"]) == 2
        assert "query" in result_data["data"]

    @pytest.mark.asyncio
    async def test_query_error(self, command_handler, mock_neo4j_driver):
        """Test Cypher query with syntax error."""
        _, session = mock_neo4j_driver

        # Mock query raising an exception
        session.run.side_effect = Exception("Syntax error")

        result = await command_handler.execute("query INVALID CYPHER")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "error" in result_data["error"].lower()


class TestHelperMethods:
    """Test helper methods."""

    def test_error_response_format(self, command_handler):
        """Test error response formatting."""
        result = command_handler._error_response("test command", "test error")
        result_data = json.loads(result)

        assert result_data["success"] is False
        assert result_data["command"] == "test command"
        assert result_data["error"] == "test error"

    def test_success_response_format(self, command_handler):
        """Test success response formatting."""
        result = command_handler._success_response("test command", {"key": "value"}, {"count": 1})
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["command"] == "test command"
        assert result_data["data"]["key"] == "value"
        assert result_data["metadata"]["count"] == 1

    def test_success_response_without_metadata(self, command_handler):
        """Test success response without metadata."""
        result = command_handler._success_response("test command", {"key": "value"})
        result_data = json.loads(result)

        assert result_data["success"] is True
        assert "metadata" not in result_data
