"""
Knowledge Graph Command Handler Module

This module provides a command pattern implementation for querying Neo4j knowledge graphs
containing Python repository data. It offers a clean, extensible interface for exploring
repositories, classes, methods, functions, and their relationships.

Classes:
    KnowledgeGraphCommands: Command handler with registry pattern for Neo4j queries
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any


class KnowledgeGraphCommands:
    """
    Command handler for Neo4j knowledge graph queries.

    This class implements a command pattern for executing various types of queries
    on a Neo4j knowledge graph containing Python repository data. Commands are
    registered in a dictionary for easy dispatch and extension.

    Attributes:
        driver: Neo4j driver instance for database connections
        commands: Dictionary mapping command names to handler methods

    Example:
        >>> from neo4j import AsyncGraphDatabase
        >>> driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        >>> cmd_handler = KnowledgeGraphCommands(driver)
        >>> result = await cmd_handler.execute("repos")
    """

    def __init__(self, neo4j_driver):
        """
        Initialize the command handler with a Neo4j driver.

        Args:
            neo4j_driver: Neo4j async driver instance
        """
        self.driver = neo4j_driver
        self.commands: dict[str, Callable] = {
            "repos": self._handle_repos,
            "explore": self._handle_explore,
            "classes": self._handle_classes,
            "class": self._handle_class,
            "method": self._handle_method,
            "query": self._handle_query,
        }

    async def execute(self, command_str: str) -> str:
        """
        Execute a command string and return JSON result.

        Args:
            command_str: Command string (e.g., "repos", "explore myrepo")

        Returns:
            JSON string with query results, statistics, and metadata

        Example:
            >>> await execute("repos")
            >>> await execute("explore pydantic-ai")
            >>> await execute("class Agent")
        """
        command_str = command_str.strip()
        if not command_str:
            return self._error_response(
                "",
                "Command cannot be empty. Available commands: repos, explore <repo>, "
                "classes [repo], class <name>, method <name> [class], query <cypher>",
            )

        parts = command_str.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd not in self.commands:
            return self._error_response(
                command_str,
                f"Unknown command '{cmd}'. Available commands: repos, explore <repo>, "
                f"classes [repo], class <name>, method <name> [class], query <cypher>",
            )

        async with self.driver.session() as session:
            return await self.commands[cmd](session, command_str, args)

    def _error_response(self, command: str, error: str) -> str:
        """Create a standardized error response."""
        return json.dumps({"success": False, "command": command, "error": error}, indent=2)

    def _success_response(
        self, command: str, data: dict[str, Any], metadata: dict[str, Any] | None = None
    ) -> str:
        """Create a standardized success response."""
        response = {"success": True, "command": command, "data": data}
        if metadata:
            response["metadata"] = metadata
        return json.dumps(response, indent=2)

    async def _handle_repos(self, session, command: str, args: list[str]) -> str:
        """
        Handle 'repos' command - list all repositories.

        Args:
            session: Neo4j async session
            command: Original command string
            args: Command arguments (unused)

        Returns:
            JSON with list of repository names
        """
        query = "MATCH (r:Repository) RETURN r.name as name ORDER BY r.name"
        result = await session.run(query)

        repos = []
        async for record in result:
            repos.append(record["name"])

        return self._success_response(
            command, {"repositories": repos}, {"total_results": len(repos), "limited": False}
        )

    async def _handle_explore(self, session, command: str, args: list[str]) -> str:
        """
        Handle 'explore <repo>' command - get repository overview.

        Args:
            session: Neo4j async session
            command: Original command string
            args: Command arguments (repo_name)

        Returns:
            JSON with repository statistics
        """
        if not args:
            return self._error_response(
                command, "Repository name required. Usage: explore <repo_name>"
            )

        repo_name = args[0]

        # Check if repository exists
        repo_check_query = "MATCH (r:Repository {name: $repo_name}) RETURN r.name as name"
        result = await session.run(repo_check_query, repo_name=repo_name)
        repo_record = await result.single()

        if not repo_record:
            return self._error_response(
                command, f"Repository '{repo_name}' not found in knowledge graph"
            )

        # Get file count
        files_query = """
        MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)
        RETURN count(f) as file_count
        """
        result = await session.run(files_query, repo_name=repo_name)
        file_count = (await result.single())["file_count"]

        # Get class count
        classes_query = """
        MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
        RETURN count(DISTINCT c) as class_count
        """
        result = await session.run(classes_query, repo_name=repo_name)
        class_count = (await result.single())["class_count"]

        # Get function count
        functions_query = """
        MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(func:Function)
        RETURN count(DISTINCT func) as function_count
        """
        result = await session.run(functions_query, repo_name=repo_name)
        function_count = (await result.single())["function_count"]

        # Get method count
        methods_query = """
        MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)-[:HAS_METHOD]->(m:Method)
        RETURN count(DISTINCT m) as method_count
        """
        result = await session.run(methods_query, repo_name=repo_name)
        method_count = (await result.single())["method_count"]

        return self._success_response(
            command,
            {
                "repository": repo_name,
                "statistics": {
                    "files": file_count,
                    "classes": class_count,
                    "functions": function_count,
                    "methods": method_count,
                },
            },
            {"total_results": 1, "limited": False},
        )

    async def _handle_classes(self, session, command: str, args: list[str]) -> str:
        """
        Handle 'classes [repo]' command - list classes.

        Args:
            session: Neo4j async session
            command: Original command string
            args: Command arguments (optional repo_name)

        Returns:
            JSON with list of classes
        """
        limit = 20
        repo_name = args[0] if args else None

        if repo_name:
            query = """
            MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
            RETURN c.name as name, c.full_name as full_name
            ORDER BY c.name
            LIMIT $limit
            """
            result = await session.run(query, repo_name=repo_name, limit=limit)
        else:
            query = """
            MATCH (c:Class)
            RETURN c.name as name, c.full_name as full_name
            ORDER BY c.name
            LIMIT $limit
            """
            result = await session.run(query, limit=limit)

        classes = []
        async for record in result:
            classes.append({"name": record["name"], "full_name": record["full_name"]})

        return self._success_response(
            command,
            {"classes": classes, "repository_filter": repo_name},
            {"total_results": len(classes), "limited": len(classes) >= limit},
        )

    async def _handle_class(self, session, command: str, args: list[str]) -> str:
        """
        Handle 'class <name>' command - explore specific class.

        Args:
            session: Neo4j async session
            command: Original command string
            args: Command arguments (class_name)

        Returns:
            JSON with class details including methods and attributes
        """
        if not args:
            return self._error_response(command, "Class name required. Usage: class <class_name>")

        class_name = args[0]

        # Find the class
        class_query = """
        MATCH (c:Class)
        WHERE c.name = $class_name OR c.full_name = $class_name
        RETURN c.name as name, c.full_name as full_name
        LIMIT 1
        """
        result = await session.run(class_query, class_name=class_name)
        class_record = await result.single()

        if not class_record:
            return self._error_response(
                command, f"Class '{class_name}' not found in knowledge graph"
            )

        actual_name = class_record["name"]
        full_name = class_record["full_name"]

        # Get methods
        methods_query = """
        MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
        WHERE c.name = $class_name OR c.full_name = $class_name
        RETURN m.name as name, m.params_list as params_list,
               m.params_detailed as params_detailed, m.return_type as return_type
        ORDER BY m.name
        """
        result = await session.run(methods_query, class_name=class_name)

        methods = []
        async for record in result:
            params_to_use = record["params_detailed"] or record["params_list"] or []
            methods.append(
                {
                    "name": record["name"],
                    "parameters": params_to_use,
                    "return_type": record["return_type"] or "Any",
                }
            )

        # Get attributes
        attributes_query = """
        MATCH (c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)
        WHERE c.name = $class_name OR c.full_name = $class_name
        RETURN a.name as name, a.type as type
        ORDER BY a.name
        """
        result = await session.run(attributes_query, class_name=class_name)

        attributes = []
        async for record in result:
            attributes.append({"name": record["name"], "type": record["type"] or "Any"})

        return self._success_response(
            command,
            {
                "class": {
                    "name": actual_name,
                    "full_name": full_name,
                    "methods": methods,
                    "attributes": attributes,
                }
            },
            {
                "total_results": 1,
                "methods_count": len(methods),
                "attributes_count": len(attributes),
                "limited": False,
            },
        )

    async def _handle_method(self, session, command: str, args: list[str]) -> str:
        """
        Handle 'method <name> [class]' command - search for methods.

        Args:
            session: Neo4j async session
            command: Original command string
            args: Command arguments (method_name, optional class_name)

        Returns:
            JSON with list of methods matching the search
        """
        if not args:
            return self._error_response(
                command, "Method name required. Usage: method <method_name> [class_name]"
            )

        method_name = args[0]
        class_name = args[1] if len(args) > 1 else None

        if class_name:
            query = """
            MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
            WHERE (c.name = $class_name OR c.full_name = $class_name)
              AND m.name = $method_name
            RETURN c.name as class_name, c.full_name as class_full_name,
                   m.name as method_name, m.params_list as params_list,
                   m.params_detailed as params_detailed, m.return_type as return_type,
                   m.args as args
            """
            result = await session.run(query, class_name=class_name, method_name=method_name)
        else:
            query = """
            MATCH (c:Class)-[:HAS_METHOD]->(m:Method)
            WHERE m.name = $method_name
            RETURN c.name as class_name, c.full_name as class_full_name,
                   m.name as method_name, m.params_list as params_list,
                   m.params_detailed as params_detailed, m.return_type as return_type,
                   m.args as args
            ORDER BY c.name
            LIMIT 20
            """
            result = await session.run(query, method_name=method_name)

        methods = []
        async for record in result:
            params_to_use = record["params_detailed"] or record["params_list"] or []
            methods.append(
                {
                    "class_name": record["class_name"],
                    "class_full_name": record["class_full_name"],
                    "method_name": record["method_name"],
                    "parameters": params_to_use,
                    "return_type": record["return_type"] or "Any",
                    "legacy_args": record["args"] or [],
                }
            )

        if not methods:
            return self._error_response(
                command,
                f"Method '{method_name}'"
                + (f" in class '{class_name}'" if class_name else "")
                + " not found",
            )

        return self._success_response(
            command,
            {"methods": methods, "class_filter": class_name},
            {
                "total_results": len(methods),
                "limited": len(methods) >= 20 and not class_name,
            },
        )

    async def _handle_query(self, session, command: str, args: list[str]) -> str:
        """
        Handle 'query <cypher>' command - execute custom Cypher query.

        Args:
            session: Neo4j async session
            command: Original command string
            args: Command arguments (cypher query string)

        Returns:
            JSON with query results
        """
        if not args:
            return self._error_response(
                command, "Cypher query required. Usage: query <cypher_query>"
            )

        cypher_query = " ".join(args)

        try:
            result = await session.run(cypher_query)

            records = []
            count = 0
            async for record in result:
                records.append(dict(record))
                count += 1
                if count >= 20:  # Limit results
                    break

            return self._success_response(
                command,
                {"query": cypher_query, "results": records},
                {"total_results": len(records), "limited": len(records) >= 20},
            )

        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "command": command,
                    "error": f"Cypher query error: {str(e)}",
                    "data": {"query": cypher_query},
                },
                indent=2,
            )
