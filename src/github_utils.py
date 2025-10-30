"""
GitHub repository processing utilities.

This module contains helper functions for batch processing GitHub repositories,
including validation, statistics calculation, and response building.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any


def validate_batch_input(
    repo_urls_json: str, max_concurrent: int, max_retries: int
) -> tuple[list[str], int, int]:
    """
    Validate and parse batch processing input parameters.

    Args:
        repo_urls_json: JSON string containing array of repository URLs
        max_concurrent: Maximum number of concurrent operations
        max_retries: Maximum number of retry attempts

    Returns:
        Tuple of (parsed_urls, validated_max_concurrent, validated_max_retries)

    Raises:
        ValueError: If input validation fails
        json.JSONDecodeError: If JSON parsing fails
    """
    # Parse JSON
    try:
        repo_urls = json.loads(repo_urls_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")

    # Validate it's a list
    if not isinstance(repo_urls, list):
        raise ValueError("repo_urls_json must be a JSON array of URLs")

    # Validate not empty
    if not repo_urls:
        raise ValueError("No repository URLs provided")

    # Validate concurrency and retry parameters
    if max_concurrent <= 0:
        raise ValueError("max_concurrent must be greater than 0")

    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    return repo_urls, max_concurrent, max_retries


def validate_repository_urls(
    urls: list[str], validate_github_url_func: callable
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """
    Validate a list of GitHub repository URLs.

    Args:
        urls: List of repository URLs to validate
        validate_github_url_func: Function to validate individual GitHub URLs
                                 Should return dict with 'valid', 'error', and 'repo_name' keys

    Returns:
        Tuple of (validated_repos, validation_errors)
        - validated_repos: List of dicts with 'url' and 'name' keys
        - validation_errors: List of dicts with 'url' and 'error' keys

    Raises:
        ValueError: If no valid repository URLs are found
    """
    validated_repos = []
    validation_errors = []

    for url in urls:
        validation = validate_github_url_func(url)
        if validation["valid"]:
            validated_repos.append({"url": url, "name": validation["repo_name"]})
        else:
            validation_errors.append({"url": url, "error": validation["error"]})

    if not validated_repos:
        raise ValueError(f"No valid repository URLs found. Validation errors: {validation_errors}")

    return validated_repos, validation_errors


def calculate_batch_statistics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate aggregate statistics from batch processing results.

    Args:
        results: List of repository processing results

    Returns:
        Dictionary containing aggregate statistics including:
        - Counts of successful/failed/retried repositories
        - Aggregate file/class/method/function counts
        - Lists of failed repositories for retry
    """
    successful_repos = [r for r in results if r["status"] == "success"]
    failed_repos = [r for r in results if r["status"] == "failed"]
    retried_repos = [r for r in results if r.get("attempt", 1) > 1]

    stats = {
        "total_repositories": len(results),
        "successful": len(successful_repos),
        "failed": len(failed_repos),
        "retried": len(retried_repos),
    }

    # Calculate aggregate statistics for successful repos
    if successful_repos:
        total_files = sum(r["statistics"]["files_processed"] for r in successful_repos)
        total_classes = sum(r["statistics"]["classes_created"] for r in successful_repos)
        total_methods = sum(r["statistics"]["methods_created"] for r in successful_repos)
        total_functions = sum(r["statistics"]["functions_created"] for r in successful_repos)

        stats["aggregate_statistics"] = {
            "total_files_processed": total_files,
            "total_classes_created": total_classes,
            "total_methods_created": total_methods,
            "total_functions_created": total_functions,
        }

    # Build failed repositories list for easy retry
    if failed_repos:
        stats["failed_repositories"] = [
            {
                "url": r["url"],
                "repository": r["repository"],
                "error": r.get("error", "Unknown error"),
                "attempts": r.get("attempt", 1),
            }
            for r in failed_repos
        ]
        stats["retry_urls"] = [r["url"] for r in failed_repos]

    return stats


def build_batch_response(
    results: list[dict[str, Any]],
    validation_errors: list[dict[str, str]],
    elapsed_time: float,
) -> dict[str, Any]:
    """
    Build the final response dictionary for batch processing.

    Args:
        results: List of repository processing results
        validation_errors: List of validation errors from URL validation
        elapsed_time: Total elapsed time in seconds

    Returns:
        Dictionary containing the complete response with:
        - success status
        - summary statistics
        - detailed results
        - validation errors (if any)
        - timing information
    """
    stats = calculate_batch_statistics(results)

    response = {
        "success": stats["failed"] == 0,
        "summary": {
            "total_repositories": stats["total_repositories"],
            "successful": stats["successful"],
            "failed": stats["failed"],
            "retried": stats["retried"],
            "validation_errors": len(validation_errors),
            "elapsed_seconds": round(elapsed_time, 2),
            "average_time_per_repo": (
                round(elapsed_time / stats["total_repositories"], 2)
                if stats["total_repositories"] > 0
                else 0
            ),
        },
        "results": results,
    }

    # Add optional sections
    if validation_errors:
        response["validation_errors"] = validation_errors

    if "failed_repositories" in stats:
        response["failed_repositories"] = stats["failed_repositories"]
        response["retry_urls"] = stats["retry_urls"]

    if "aggregate_statistics" in stats:
        response["aggregate_statistics"] = stats["aggregate_statistics"]

    return response


def print_batch_summary(
    total_repos: int, successful_count: int, failed_count: int, retried_count: int
) -> None:
    """
    Print a summary of batch processing results to console.

    Args:
        total_repos: Total number of repositories processed
        successful_count: Number of successfully processed repositories
        failed_count: Number of failed repositories
        retried_count: Number of repositories that required retries
    """
    print("\nBatch processing complete!", file=sys.stderr, flush=True)
    print(f"✓ Successful: {successful_count}/{total_repos}", file=sys.stderr, flush=True)
    print(f"✗ Failed: {failed_count}/{total_repos}", file=sys.stderr, flush=True)
    if retried_count > 0:
        print(f"↻ Retried: {retried_count}", file=sys.stderr, flush=True)


async def query_repository_statistics(
    repo_extractor: Any, repo_name: str, include_samples: bool = True
) -> dict[str, Any] | None:
    """
    Query Neo4j for repository statistics.

    Args:
        repo_extractor: DirectNeo4jExtractor instance with Neo4j driver
        repo_name: Name of the repository to query
        include_samples: Whether to include sample module names (default: True)

    Returns:
        Dictionary with statistics, or None if repository not found:
        - repository: Repository name
        - files_processed: Number of files
        - classes_created: Number of classes
        - methods_created: Number of methods
        - functions_created: Number of functions
        - attributes_created: Number of attributes (if include_samples=True)
        - sample_modules: List of sample module names (if include_samples=True)
    """
    async with repo_extractor.driver.session() as session:
        if include_samples:
            # Full query with attributes and sample modules
            stats_query = """
            MATCH (r:Repository {name: $repo_name})
            OPTIONAL MATCH (r)-[:CONTAINS]->(f:File)
            OPTIONAL MATCH (f)-[:DEFINES]->(c:Class)
            OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
            OPTIONAL MATCH (f)-[:DEFINES]->(func:Function)
            OPTIONAL MATCH (c)-[:HAS_ATTRIBUTE]->(a:Attribute)
            WITH r,
                 count(DISTINCT f) as files_count,
                 count(DISTINCT c) as classes_count,
                 count(DISTINCT m) as methods_count,
                 count(DISTINCT func) as functions_count,
                 count(DISTINCT a) as attributes_count

            // Get some sample module names
            OPTIONAL MATCH (r)-[:CONTAINS]->(sample_f:File)
            WITH r, files_count, classes_count, methods_count, functions_count, attributes_count,
                 collect(DISTINCT sample_f.module_name)[0..5] as sample_modules

            RETURN
                r.name as repo_name,
                files_count,
                classes_count,
                methods_count,
                functions_count,
                attributes_count,
                sample_modules
            """

            result = await session.run(stats_query, repo_name=repo_name)
            record = await result.single()

            if record:
                return {
                    "repository": record["repo_name"],
                    "files_processed": record["files_count"],
                    "classes_created": record["classes_count"],
                    "methods_created": record["methods_count"],
                    "functions_created": record["functions_count"],
                    "attributes_created": record["attributes_count"],
                    "sample_modules": record["sample_modules"] or [],
                }
        else:
            # Simplified query without attributes and samples
            stats_query = """
            MATCH (r:Repository {name: $repo_name})
            OPTIONAL MATCH (r)-[:CONTAINS]->(f:File)
            OPTIONAL MATCH (f)-[:DEFINES]->(c:Class)
            OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
            OPTIONAL MATCH (f)-[:DEFINES]->(func:Function)
            WITH r,
                 count(DISTINCT f) as files_count,
                 count(DISTINCT c) as classes_count,
                 count(DISTINCT m) as methods_count,
                 count(DISTINCT func) as functions_count
            RETURN
                r.name as repo_name,
                files_count,
                classes_count,
                methods_count,
                functions_count
            """

            result = await session.run(stats_query, repo_name=repo_name)
            record = await result.single()

            if record:
                return {
                    "repository": record["repo_name"],
                    "files_processed": record["files_count"],
                    "classes_created": record["classes_count"],
                    "methods_created": record["methods_count"],
                    "functions_created": record["functions_count"],
                }

        return None


def build_repository_parse_response(
    repo_url: str, repo_name: str, stats: dict[str, Any]
) -> dict[str, Any]:
    """
    Build success response for repository parsing.

    Args:
        repo_url: Repository URL
        repo_name: Repository name
        stats: Statistics dictionary from query_repository_statistics

    Returns:
        Dictionary with success response containing:
        - success: True
        - repo_url: Repository URL
        - repo_name: Repository name
        - message: Success message
        - statistics: Statistics dictionary
        - ready_for_validation: True
        - next_steps: List of next steps
    """
    return {
        "success": True,
        "repo_url": repo_url,
        "repo_name": repo_name,
        "message": f"Successfully parsed repository '{repo_name}' into knowledge graph",
        "statistics": stats,
        "ready_for_validation": True,
        "next_steps": [
            "Repository is now available for hallucination detection",
            f"Use check_ai_script_hallucinations to validate scripts against {repo_name}",
            "The knowledge graph contains classes, methods, and functions from this repository",
        ],
    }


async def process_single_repository(
    repo_info: dict[str, str],
    repo_extractor: Any,
    semaphore: asyncio.Semaphore,
    max_retries: int,
    attempt: int = 1,
) -> dict[str, Any]:
    """
    Process a single GitHub repository with retry logic.

    This function clones and analyzes a GitHub repository, extracting its structure
    into a Neo4j knowledge graph. It includes automatic retry logic for transient
    failures and queries Neo4j for statistics after successful processing.

    Args:
        repo_info: Dictionary with 'url' and 'name' keys
        repo_extractor: DirectNeo4jExtractor instance for repository analysis
        semaphore: Asyncio semaphore for concurrency control
        max_retries: Maximum number of retry attempts
        attempt: Current attempt number (used for recursion)

    Returns:
        Dictionary containing:
        - url: Repository URL
        - repository: Repository name
        - status: 'success' or 'failed'
        - attempt: Number of attempts made
        - statistics: Dict with counts (on success)
        - error: Error message (on failure)
        - retries_exhausted: True if all retries were used (on failure)
    """
    async with semaphore:
        repo_url = repo_info["url"]
        repo_name = repo_info["name"]

        print(f"[{attempt}/{max_retries + 1}] Processing: {repo_name}", file=sys.stderr, flush=True)

        try:
            # Parse the repository
            await repo_extractor.analyze_repository(repo_url)

            # Query Neo4j for statistics (simplified version for batch processing)
            stats = await query_repository_statistics(
                repo_extractor, repo_name, include_samples=False
            )

            if stats:
                return {
                    "url": repo_url,
                    "repository": repo_name,
                    "status": "success",
                    "attempt": attempt,
                    "statistics": {
                        "files_processed": stats["files_processed"],
                        "classes_created": stats["classes_created"],
                        "methods_created": stats["methods_created"],
                        "functions_created": stats["functions_created"],
                    },
                }
            else:
                return {
                    "url": repo_url,
                    "repository": repo_name,
                    "status": "failed",
                    "attempt": attempt,
                    "error": "Repository processed but no data found in Neo4j",
                }

        except Exception as e:
            error_msg = str(e)
            print(
                f"Error processing {repo_name} (attempt {attempt}): {error_msg}",
                file=sys.stderr,
                flush=True,
            )

            # Retry logic
            if attempt <= max_retries:
                print(f"Retrying {repo_name} in 2 seconds...", file=sys.stderr, flush=True)
                await asyncio.sleep(2)  # Brief delay before retry
                return await process_single_repository(
                    repo_info, repo_extractor, semaphore, max_retries, attempt + 1
                )
            else:
                return {
                    "url": repo_url,
                    "repository": repo_name,
                    "status": "failed",
                    "attempt": attempt,
                    "error": error_msg,
                    "retries_exhausted": True,
                }
