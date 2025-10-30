"""
Knowledge Graph Tools

MCP tools for Neo4j knowledge graph operations including repository parsing
and AI hallucination detection.
"""

import json
import os
import sys
from typing import Any

from ai_script_analyzer import AIScriptAnalyzer
from crawl4ai import AsyncWebCrawler  # For type hints
from fastmcp import Context
from hallucination_reporter import HallucinationReporter

from core import (
    validate_github_url,
    validate_script_path,
)


async def check_ai_script_hallucinations(ctx: Context, script_path: str) -> str:
    """
    Check an AI-generated Python script for hallucinations using the knowledge graph.

    This tool analyzes a Python script for potential AI hallucinations by validating
    imports, method calls, class instantiations, and function calls against a Neo4j
    knowledge graph containing real repository data.

    The tool performs comprehensive analysis including:
    - Import validation against known repositories
    - Method call validation on classes from the knowledge graph
    - Class instantiation parameter validation
    - Function call parameter validation
    - Attribute access validation

    Args:
        ctx: The MCP server provided context
        script_path: Absolute path to the Python script to analyze

    Returns:
        JSON string with hallucination detection results, confidence scores, and recommendations
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get the knowledge validator from context (lazy-loaded)
        knowledge_validator_lazy = ctx.request_context.lifespan_context.knowledge_validator

        if not knowledge_validator_lazy:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph validator not available. Check Neo4j configuration in environment variables.",
                },
                indent=2,
            )

        # Lazy-load the actual validator
        knowledge_validator = await knowledge_validator_lazy.get_validator()
        if not knowledge_validator:
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to initialize knowledge graph validator.",
                },
                indent=2,
            )

        # Validate script path
        validation = validate_script_path(script_path)
        if not validation["valid"]:
            return json.dumps(
                {
                    "success": False,
                    "script_path": script_path,
                    "error": validation["error"],
                },
                indent=2,
            )

        # Step 1: Analyze script structure using AST
        analyzer = AIScriptAnalyzer()
        analysis_result = analyzer.analyze_script(script_path)

        if analysis_result.errors:
            print(
                f"Analysis warnings for {script_path}: {analysis_result.errors}",
                file=sys.stderr,
                flush=True,
            )

        # Step 2: Validate against knowledge graph
        validation_result = await knowledge_validator.validate_script(analysis_result)

        # Step 3: Generate comprehensive report
        reporter = HallucinationReporter()
        report = reporter.generate_comprehensive_report(validation_result)

        # Format response with comprehensive information
        return json.dumps(
            {
                "success": True,
                "script_path": script_path,
                "overall_confidence": validation_result.overall_confidence,
                "validation_summary": {
                    "total_validations": report["validation_summary"]["total_validations"],
                    "valid_count": report["validation_summary"]["valid_count"],
                    "invalid_count": report["validation_summary"]["invalid_count"],
                    "uncertain_count": report["validation_summary"]["uncertain_count"],
                    "not_found_count": report["validation_summary"]["not_found_count"],
                    "hallucination_rate": report["validation_summary"]["hallucination_rate"],
                },
                "hallucinations_detected": report["hallucinations_detected"],
                "recommendations": report["recommendations"],
                "analysis_metadata": {
                    "total_imports": report["analysis_metadata"]["total_imports"],
                    "total_classes": report["analysis_metadata"]["total_classes"],
                    "total_methods": report["analysis_metadata"]["total_methods"],
                    "total_attributes": report["analysis_metadata"]["total_attributes"],
                    "total_functions": report["analysis_metadata"]["total_functions"],
                },
                "libraries_analyzed": report.get("libraries_analyzed", []),
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "script_path": script_path,
                "error": f"Analysis failed: {str(e)}",
            },
            indent=2,
        )


async def query_knowledge_graph(ctx: Context, command: str) -> str:
    """
    Query and explore the Neo4j knowledge graph containing repository data.

    This tool provides comprehensive access to the knowledge graph for exploring repositories,
    classes, methods, functions, and their relationships. Perfect for understanding what data
    is available for hallucination detection and debugging validation results.

    **⚠️ IMPORTANT: Always start with the `repos` command first!**
    Before using any other commands, run `repos` to see what repositories are available
    in your knowledge graph. This will help you understand what data you can explore.

    ## Available Commands:

    **Repository Commands:**
    - `repos` - **START HERE!** List all repositories in the knowledge graph
    - `explore <repo_name>` - Get detailed overview of a specific repository

    **Class Commands:**
    - `classes` - List all classes across all repositories (limited to 20)
    - `classes <repo_name>` - List classes in a specific repository
    - `class <class_name>` - Get detailed information about a specific class including methods and attributes

    **Method Commands:**
    - `method <method_name>` - Search for methods by name across all classes
    - `method <method_name> <class_name>` - Search for a method within a specific class

    **Custom Query:**
    - `query <cypher_query>` - Execute a custom Cypher query (results limited to 20 records)

    ## Knowledge Graph Schema:

    **Node Types:**
    - Repository: `(r:Repository {name: string})`
    - File: `(f:File {path: string, module_name: string})`
    - Class: `(c:Class {name: string, full_name: string})`
    - Method: `(m:Method {name: string, params_list: [string], params_detailed: [string], return_type: string, args: [string]})`
    - Function: `(func:Function {name: string, params_list: [string], params_detailed: [string], return_type: string, args: [string]})`
    - Attribute: `(a:Attribute {name: string, type: string})`

    **Relationships:**
    - `(r:Repository)-[:CONTAINS]->(f:File)`
    - `(f:File)-[:DEFINES]->(c:Class)`
    - `(c:Class)-[:HAS_METHOD]->(m:Method)`
    - `(c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)`
    - `(f:File)-[:DEFINES]->(func:Function)`

    ## Example Workflow:
    ```
    1. repos                                    # See what repositories are available
    2. explore pydantic-ai                      # Explore a specific repository
    3. classes pydantic-ai                      # List classes in that repository
    4. class Agent                              # Explore the Agent class
    5. method run_stream                        # Search for run_stream method
    6. method __init__ Agent                    # Find Agent constructor
    7. query "MATCH (c:Class)-[:HAS_METHOD]->(m:Method) WHERE m.name = 'run' RETURN c.name, m.name LIMIT 5"
    ```

    Args:
        ctx: The MCP server provided context
        command: Command string to execute (see available commands above)

    Returns:
        JSON string with query results, statistics, and metadata
    """
    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get Neo4j driver from context (lazy-loaded)
        repo_extractor_lazy = ctx.request_context.lifespan_context.repo_extractor
        if not repo_extractor_lazy:
            return json.dumps(
                {
                    "success": False,
                    "error": "Neo4j connection not available. Check Neo4j configuration in environment variables.",
                },
                indent=2,
            )

        # Lazy-load the actual extractor
        repo_extractor = await repo_extractor_lazy.get_extractor()
        if not repo_extractor or not repo_extractor.driver:
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to initialize Neo4j extractor. Check Neo4j configuration.",
                },
                indent=2,
            )

        # Use KnowledgeGraphCommands to execute the command
        from .knowledge_graph_commands import KnowledgeGraphCommands

        cmd_handler = KnowledgeGraphCommands(repo_extractor.driver)
        return await cmd_handler.execute(command)

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "command": command,
                "error": f"Query execution failed: {str(e)}",
            },
            indent=2,
        )


async def parse_github_repository(ctx: Context, repo_url: str) -> str:
    """
    Parse a GitHub repository into the Neo4j knowledge graph.

    This tool clones a GitHub repository, analyzes its Python files, and stores
    the code structure (classes, methods, functions, imports) in Neo4j for use
    in hallucination detection. The tool:

    - Clones the repository to a temporary location
    - Analyzes Python files to extract code structure
    - Stores classes, methods, functions, and imports in Neo4j
    - Provides detailed statistics about the parsing results
    - Automatically handles module name detection for imports

    Args:
        ctx: The MCP server provided context
        repo_url: GitHub repository URL (e.g., 'https://github.com/user/repo.git')

    Returns:
        JSON string with parsing results, statistics, and repository information
    """
    from github_utils import build_repository_parse_response, query_repository_statistics

    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get the repository extractor from context (lazy-loaded)
        repo_extractor_lazy = ctx.request_context.lifespan_context.repo_extractor

        if not repo_extractor_lazy:
            return json.dumps(
                {
                    "success": False,
                    "error": "Repository extractor not available. Check Neo4j configuration in environment variables.",
                },
                indent=2,
            )

        # Initialize extractor on first use
        repo_extractor = await repo_extractor_lazy.get_extractor()
        if not repo_extractor:
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to initialize repository extractor. Check Neo4j connection.",
                },
                indent=2,
            )

        # Validate repository URL
        validation = validate_github_url(repo_url)
        if not validation["valid"]:
            return json.dumps(
                {"success": False, "repo_url": repo_url, "error": validation["error"]},
                indent=2,
            )

        repo_name = validation["repo_name"]

        # Parse the repository (this includes cloning, analysis, and Neo4j storage)
        print(f"Starting repository analysis for: {repo_name}", file=sys.stderr, flush=True)
        await repo_extractor.analyze_repository(repo_url)
        print(f"Repository analysis completed for: {repo_name}", file=sys.stderr, flush=True)

        # Query Neo4j for statistics about the parsed repository
        stats = await query_repository_statistics(repo_extractor, repo_name, include_samples=True)

        if not stats:
            return json.dumps(
                {
                    "success": False,
                    "repo_url": repo_url,
                    "error": f"Repository '{repo_name}' not found in database after parsing",
                },
                indent=2,
            )

        # Build and return success response
        response = build_repository_parse_response(repo_url, repo_name, stats)
        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "repo_url": repo_url,
                "error": f"Repository parsing failed: {str(e)}",
            },
            indent=2,
        )


async def parse_github_repositories_batch(
    ctx: Context, repo_urls_json: str, max_concurrent: int = 3, max_retries: int = 2
) -> str:
    """
    Parse multiple GitHub repositories into Neo4j knowledge graph in parallel.

    This tool efficiently processes multiple repositories with intelligent features:
    - Parallel processing with configurable concurrency limits
    - Automatic retry logic for transient failures
    - Detailed per-repository status tracking
    - Aggregate statistics and error reporting
    - Progress visibility for long-running operations

    Perfect for:
    - Bulk importing organization repositories
    - Building comprehensive knowledge graphs
    - Recovering from partial failures
    - Large-scale code analysis projects

    Args:
        ctx: The MCP server provided context
        repo_urls_json: JSON array of GitHub repository URLs
                       Example: '["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]'
        max_concurrent: Maximum number of repositories to process simultaneously (default: 3)
                       Lower values = less memory usage, higher values = faster completion
        max_retries: Number of retry attempts for failed repositories (default: 2)
                    Set to 0 to disable retries

    Returns:
        JSON string with:
        - Overall success status
        - Per-repository results with detailed status
        - Aggregate statistics (total, successful, failed)
        - Failed repositories list for easy retry
        - Processing time metrics

    Example:
        repos = '["https://github.com/openai/openai-python.git", "https://github.com/anthropics/anthropic-sdk-python.git"]'
        parse_github_repositories_batch(repos, max_concurrent=2, max_retries=1)
    """
    import asyncio
    import time

    from github_utils import (
        build_batch_response,
        print_batch_summary,
        process_single_repository,
        validate_batch_input,
        validate_repository_urls,
    )

    try:
        # Check if knowledge graph functionality is enabled
        knowledge_graph_enabled = os.getenv("USE_KNOWLEDGE_GRAPH", "false") == "true"
        if not knowledge_graph_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "Knowledge graph functionality is disabled. Set USE_KNOWLEDGE_GRAPH=true in environment.",
                },
                indent=2,
            )

        # Get the repository extractor from context (lazy-loaded)
        repo_extractor_lazy = ctx.request_context.lifespan_context.repo_extractor
        if not repo_extractor_lazy:
            return json.dumps(
                {
                    "success": False,
                    "error": "Repository extractor not available. Check Neo4j configuration.",
                },
                indent=2,
            )

        # Initialize extractor on first use
        repo_extractor = await repo_extractor_lazy.get_extractor()
        if not repo_extractor:
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to initialize repository extractor. Check Neo4j connection.",
                },
                indent=2,
            )

        # Validate and parse input parameters
        try:
            repo_urls, max_concurrent, max_retries = validate_batch_input(
                repo_urls_json, max_concurrent, max_retries
            )
        except ValueError as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

        start_time = time.time()

        # Validate all repository URLs
        try:
            validated_repos, validation_errors = validate_repository_urls(
                repo_urls, validate_github_url
            )
        except ValueError as e:
            return json.dumps({"success": False, "error": str(e)}, indent=2)

        # Set up parallel processing
        semaphore = asyncio.Semaphore(max_concurrent)

        print(
            f"\nStarting batch processing of {len(validated_repos)} repositories...",
            file=sys.stderr,
            flush=True,
        )
        print(
            f"Concurrency limit: {max_concurrent}, Max retries per repo: {max_retries}\n",
            file=sys.stderr,
            flush=True,
        )

        # Process all repositories in parallel (with concurrency limit)
        tasks = [
            process_single_repository(repo, repo_extractor, semaphore, max_retries)
            for repo in validated_repos
        ]
        results = await asyncio.gather(*tasks)

        # Calculate timing and build response
        elapsed_time = time.time() - start_time
        response = build_batch_response(results, validation_errors, elapsed_time)

        # Print summary to console
        stats = response["summary"]
        print_batch_summary(
            stats["total_repositories"],
            stats["successful"],
            stats["failed"],
            stats["retried"],
        )

        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"Batch processing failed: {str(e)}"}, indent=2
        )


async def crawl_markdown_file(crawler: AsyncWebCrawler, url: str) -> list[dict[str, Any]]:
    """
    Crawl a .txt or markdown file.

    Args:
        crawler: AsyncWebCrawler instance
        url: URL of the file

    Returns:
        List of dictionaries with URL and markdown content
    """
    crawl_config = CrawlerRunConfig()

    result = await crawler.arun(url=url, config=crawl_config)
    if result.success and result.markdown:
        return [{"url": url, "markdown": result.markdown}]
    else:
        print(f"Failed to crawl {url}: {result.error_message}", file=sys.stderr, flush=True)
        return []


async def crawl_batch(
    crawler: AsyncWebCrawler, urls: list[str], max_concurrent: int = 10
) -> list[dict[str, Any]]:
    """
    Batch crawl multiple URLs in parallel.

    Args:
        crawler: AsyncWebCrawler instance
        urls: List of URLs to crawl
        max_concurrent: Maximum number of concurrent browser sessions

    Returns:
        List of dictionaries with URL and markdown content
    """
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent,
    )

    results = await crawler.arun_many(urls=urls, config=crawl_config, dispatcher=dispatcher)
    return [{"url": r.url, "markdown": r.markdown} for r in results if r.success and r.markdown]


# ============================================================================
# GraphRAG Tools - Document Knowledge Graph for Web Content
# ============================================================================


__all__ = [
    "check_ai_script_hallucinations",
    "query_knowledge_graph",
    "parse_github_repository",
    "parse_github_repositories_batch",
]
