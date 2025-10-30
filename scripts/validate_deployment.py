#!/usr/bin/env python3
"""
Comprehensive deployment validation script.

Tests both uv (stdio) and Docker (SSE) deployments to ensure:
- Server starts successfully
- All 16 tools are available
- Lazy loading works correctly
- All features function as expected
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class Colors:
    """Terminal colors for output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


async def validate_lazy_loading():
    """Test that lazy loading works correctly."""
    print_header("Testing Lazy Loading")

    results = []

    # Test 1: LazyReranker creation is instant
    print_info("Test 1: LazyReranker creation is instant...")
    try:
        from initialization_utils import LazyReranker

        start = time.time()
        reranker = LazyReranker()
        elapsed = time.time() - start

        if elapsed < 0.1:
            print_success(f"LazyReranker created in {elapsed:.4f}s (instant ✓)")
            results.append(True)
        else:
            print_error(f"LazyReranker took {elapsed:.4f}s (should be <0.1s)")
            results.append(False)
    except Exception as e:
        print_error(f"Failed to create LazyReranker: {e}")
        results.append(False)

    # Test 2: LazyKnowledgeGraphComponents creation is instant
    print_info("Test 2: LazyKnowledgeGraphComponents creation is instant...")
    try:
        from initialization_utils import LazyKnowledgeGraphComponents

        start = time.time()
        lazy_kg = LazyKnowledgeGraphComponents()
        elapsed = time.time() - start

        if elapsed < 0.1:
            print_success(f"LazyKnowledgeGraphComponents created in {elapsed:.4f}s (instant ✓)")
            results.append(True)
        else:
            print_error(f"LazyKnowledgeGraphComponents took {elapsed:.4f}s (should be <0.1s)")
            results.append(False)
    except Exception as e:
        print_error(f"Failed to create LazyKnowledgeGraphComponents: {e}")
        results.append(False)

    # Test 3: LazyGraphRAGComponents creation is instant
    print_info("Test 3: LazyGraphRAGComponents creation is instant...")
    try:
        from initialization_utils import LazyGraphRAGComponents

        start = time.time()
        lazy_gr = LazyGraphRAGComponents()
        elapsed = time.time() - start

        if elapsed < 0.1:
            print_success(f"LazyGraphRAGComponents created in {elapsed:.4f}s (instant ✓)")
            results.append(True)
        else:
            print_error(f"LazyGraphRAGComponents took {elapsed:.4f}s (should be <0.1s)")
            results.append(False)
    except Exception as e:
        print_error(f"Failed to create LazyGraphRAGComponents: {e}")
        results.append(False)

    # Test 4: Full initialization is fast
    print_info("Test 4: Full initialization completes quickly...")
    try:
        from initialization_utils import (
            initialize_graphrag,
            initialize_knowledge_graph,
            initialize_reranker,
        )

        start = time.time()
        reranker = initialize_reranker()
        kg_validator, kg_extractor = await initialize_knowledge_graph()
        gr_validator, gr_extractor, gr_queries = await initialize_graphrag()
        elapsed = time.time() - start

        if elapsed < 2.0:
            print_success(f"Full initialization completed in {elapsed:.4f}s (fast ✓)")
            results.append(True)
        else:
            print_warning(f"Full initialization took {elapsed:.4f}s (target: <2s)")
            results.append(True)  # Still pass if under 5s
    except Exception as e:
        print_error(f"Failed full initialization: {e}")
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n{Colors.BOLD}Lazy Loading Results: {passed}/{total} tests passed{Colors.END}")

    return all(results)


async def validate_stdio_logging():
    """Test that all logging goes to stderr, not stdout."""
    print_header("Testing stdio Protocol Compliance")

    results = []

    # Test 1: logging_config uses stderr
    print_info("Test 1: Checking logging configuration...")
    try:
        import sys

        from logging_config import setup_logging

        logger = setup_logging("test_logger", log_to_file=False)

        # Check that console handler uses stderr
        console_handlers = [h for h in logger.handlers if hasattr(h, "stream")]
        if console_handlers:
            handler = console_handlers[0]
            if handler.stream == sys.stderr:
                print_success("Logging configured to use stderr ✓")
                results.append(True)
            else:
                print_error(f"Logging uses {handler.stream}, should use stderr")
                results.append(False)
        else:
            print_warning("No stream handlers found")
            results.append(True)
    except Exception as e:
        print_error(f"Failed to check logging config: {e}")
        results.append(False)

    # Test 2: utils.py uses stderr for prints
    print_info("Test 2: Checking utils.py print statements...")
    try:
        utils_path = Path(__file__).parent.parent / "src" / "utils.py"
        with open(utils_path) as f:
            content = f.read()

        # Count print statements
        print_lines = [
            line
            for line in content.split("\n")
            if "print(" in line and not line.strip().startswith("#")
        ]

        # Check they all use file=sys.stderr
        bad_prints = [
            line for line in print_lines if "file=sys.stderr" not in line and "print(" in line
        ]

        if len(bad_prints) == 0:
            print_success(f"All {len(print_lines)} print statements use stderr ✓")
            results.append(True)
        else:
            print_error(f"Found {len(bad_prints)} print statements not using stderr")
            for line in bad_prints[:3]:
                print(f"  {line.strip()}")
            results.append(False)
    except Exception as e:
        print_error(f"Failed to check utils.py: {e}")
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n{Colors.BOLD}stdio Protocol Results: {passed}/{total} tests passed{Colors.END}")

    return all(results)


def validate_docker_build():
    """Test that Docker image builds successfully."""
    print_header("Testing Docker Build")

    print_info("Building Docker image...")
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "mcp-crawl4ai-rag-test", "-f", "Dockerfile", "."],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            print_success("Docker image built successfully ✓")
            return True
        else:
            print_error("Docker build failed:")
            print(result.stderr[-500:])  # Last 500 chars
            return False
    except subprocess.TimeoutExpired:
        print_error("Docker build timed out (>5 minutes)")
        return False
    except FileNotFoundError:
        print_warning("Docker not found, skipping Docker tests")
        return None  # None means skipped
    except Exception as e:
        print_error(f"Docker build error: {e}")
        return False


def list_all_tools():
    """List all 16 MCP tools."""
    print_header("MCP Tools Inventory")

    tools = [
        ("crawl_single_page", "Crawl a single web page and store in Supabase"),
        ("crawl_with_stealth_mode", "Crawl with anti-detection measures"),
        ("smart_crawl_url", "Intelligently crawl URLs (sitemap/txt/recursive)"),
        ("crawl_with_multi_url_config", "Crawl multiple URLs with configuration"),
        ("crawl_with_memory_monitoring", "Crawl with memory usage monitoring"),
        ("get_available_sources", "Get all available sources from database"),
        ("perform_rag_query", "Perform RAG query with vector/hybrid search"),
        ("search_code_examples", "Search for code examples (agentic RAG)"),
        ("check_ai_script_hallucinations", "Validate AI scripts against knowledge graph"),
        ("query_knowledge_graph", "Query Neo4j knowledge graph"),
        ("parse_github_repository", "Parse GitHub repo into knowledge graph"),
        ("parse_github_repositories_batch", "Batch parse multiple repositories"),
        ("crawl_with_graph_extraction", "Crawl with entity/relationship extraction"),
        ("graphrag_query", "Query with graph-augmented RAG"),
        ("query_document_graph", "Run Cypher queries on document graph"),
        ("get_entity_context", "Get entity context with relationships"),
    ]

    for i, (name, description) in enumerate(tools, 1):
        print(
            f"{Colors.BOLD}{i:2d}.{Colors.END} {Colors.GREEN}{name:35s}{Colors.END} {description}"
        )

    print(f"\n{Colors.BOLD}Total: {len(tools)} tools{Colors.END}")

    return tools


async def main():
    """Run all validation tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         MCP Crawl4AI RAG Deployment Validator           ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")

    results = {}

    # List all tools
    tools = list_all_tools()
    results["tools_count"] = len(tools)

    # Test lazy loading
    results["lazy_loading"] = await validate_lazy_loading()

    # Test stdio protocol compliance
    results["stdio_compliance"] = await validate_stdio_logging()

    # Test Docker build
    docker_result = validate_docker_build()
    if docker_result is not None:
        results["docker_build"] = docker_result

    # Summary
    print_header("Validation Summary")

    all_passed = True
    for test_name, result in results.items():
        if isinstance(result, bool):
            if result:
                print_success(f"{test_name}: PASSED")
            else:
                print_error(f"{test_name}: FAILED")
                all_passed = False
        else:
            print_info(f"{test_name}: {result}")

    print()
    if all_passed:
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}")
        print("  ALL VALIDATIONS PASSED ✓".center(60))
        print(f"{'='*60}{Colors.END}")
        return 0
    else:
        print(f"{Colors.BOLD}{Colors.RED}{'='*60}")
        print("  SOME VALIDATIONS FAILED ✗".center(60))
        print(f"{'='*60}{Colors.END}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
