"""
Application Lifespan Management

Manages the lifecycle of the Crawl4AI MCP server, including initialization
and cleanup of all resources (browser, database connections, models).
"""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from crawl4ai import AsyncWebCrawler, BrowserConfig
from fastmcp import FastMCP

from .context import Crawl4AIContext


@asynccontextmanager
async def crawl4ai_lifespan(server: FastMCP) -> AsyncIterator[Crawl4AIContext]:
    """
    Manages the Crawl4AI client lifecycle with proper resource cleanup.

    Args:
        server: The FastMCP server instance

    Yields:
        Crawl4AIContext: The context containing the Crawl4AI crawler and all resources
    """
    # Import initialization utilities
    from initialization_utils import (
        cleanup_graphrag,
        cleanup_knowledge_graph,
        initialize_graphrag,
        initialize_knowledge_graph,
        initialize_reranker,
        initialize_supabase,
    )

    # Initialize all resources to None for proper cleanup tracking
    crawler = None
    supabase_client = None
    reranking_model = None
    knowledge_validator = None
    repo_extractor = None
    document_graph_validator = None
    document_entity_extractor = None
    document_graph_queries = None

    print("🔧 Starting MCP server initialization...", file=sys.stderr, flush=True)

    try:
        # Check if browser validation should be skipped (for development/testing)
        skip_validation = os.environ.get("SKIP_BROWSER_VALIDATION", "false").lower() == "true"

        if skip_validation:
            print(
                "⚠️  Skipping browser validation (SKIP_BROWSER_VALIDATION=true)",
                file=sys.stderr,
                flush=True,
            )
            print(
                "⚠️  This is for development only. Crawling tools will not work!",
                file=sys.stderr,
                flush=True,
            )
        else:
            # Validate browser installation BEFORE attempting to initialize
            print("🔧 Validating Playwright browser installation...", file=sys.stderr, flush=True)
            from .browser_validation import print_browser_diagnostics

            browser_valid = print_browser_diagnostics()
            if not browser_valid:
                # Browser validation failed - error message already printed
                raise RuntimeError(
                    "Playwright browsers are not properly installed or accessible. "
                    "Please follow the instructions above to fix the issue."
                )

            print("✓ Browser validation passed", file=sys.stderr, flush=True)

        # Create browser configuration
        print("🔧 Creating browser configuration...", file=sys.stderr, flush=True)
        browser_config = BrowserConfig(headless=True, verbose=False)

        # Initialize the crawler with detailed error handling
        print("🔧 Initializing Crawl4AI browser...", file=sys.stderr, flush=True)
        try:
            crawler = AsyncWebCrawler(config=browser_config)
            await crawler.__aenter__()
            print("✓ Crawl4AI browser ready", file=sys.stderr, flush=True)
        except Exception as browser_error:
            print("\n" + "=" * 80, file=sys.stderr, flush=True)
            print("❌ FAILED TO INITIALIZE CRAWL4AI BROWSER", file=sys.stderr, flush=True)
            print("=" * 80, file=sys.stderr, flush=True)
            print(f"\nError Type: {type(browser_error).__name__}", file=sys.stderr, flush=True)
            print(f"Error Message: {str(browser_error)}", file=sys.stderr, flush=True)

            # Check if it's a Playwright browser installation issue
            error_str = str(browser_error)
            if "Executable doesn't exist" in error_str or "playwright install" in error_str:
                print(
                    "\n🔧 SOLUTION: Playwright browsers not installed", file=sys.stderr, flush=True
                )
                print("\nPlease run ONE of these commands:", file=sys.stderr, flush=True)
                print("  1. uv run playwright install chromium", file=sys.stderr, flush=True)
                print(
                    "  2. .venv\\Scripts\\activate && playwright install chromium",
                    file=sys.stderr,
                    flush=True,
                )
                print("\nThen restart Claude Desktop.\n", file=sys.stderr, flush=True)
            elif "permission" in error_str.lower():
                print("\n🔧 SOLUTION: Permission issue detected", file=sys.stderr, flush=True)
                print(
                    "\nTry running as administrator or check folder permissions.",
                    file=sys.stderr,
                    flush=True,
                )
            else:
                print("\n🔧 TROUBLESHOOTING STEPS:", file=sys.stderr, flush=True)
                print("  1. Ensure Playwright browsers are installed:", file=sys.stderr, flush=True)
                print("     uv run playwright install chromium", file=sys.stderr, flush=True)
                print(
                    "  2. Check antivirus/security software isn't blocking browser files",
                    file=sys.stderr,
                    flush=True,
                )
                print("  3. Verify .venv folder has write permissions", file=sys.stderr, flush=True)
                print("  4. Try deleting .venv and reinstalling:", file=sys.stderr, flush=True)
                print("     rm -rf .venv", file=sys.stderr, flush=True)
                print("     uv venv", file=sys.stderr, flush=True)
                print("     uv pip install -e .[dev]", file=sys.stderr, flush=True)
                print("     uv run playwright install chromium", file=sys.stderr, flush=True)

            print("\n" + "=" * 80, file=sys.stderr, flush=True)
            raise RuntimeError(
                f"Crawl4AI browser initialization failed: {browser_error}"
            ) from browser_error

        # Initialize Supabase client
        print("🔧 Connecting to Supabase...", file=sys.stderr, flush=True)
        supabase_client = initialize_supabase()
        print("✓ Supabase connected", file=sys.stderr, flush=True)

        # Initialize reranking model
        reranking_model = initialize_reranker()

        # Initialize Neo4j knowledge graph components
        knowledge_validator, repo_extractor = await initialize_knowledge_graph()

        # Initialize GraphRAG components
        (
            document_graph_validator,
            document_entity_extractor,
            document_graph_queries,
        ) = await initialize_graphrag()

        print("✓ MCP server initialization complete!", file=sys.stderr, flush=True)

        yield Crawl4AIContext(
            crawler=crawler,
            supabase_client=supabase_client,
            reranking_model=reranking_model,
            knowledge_validator=knowledge_validator,
            repo_extractor=repo_extractor,
            document_graph_validator=document_graph_validator,
            document_entity_extractor=document_entity_extractor,
            document_graph_queries=document_graph_queries,
        )
    finally:
        # Clean up crawler with error handling
        if crawler:
            try:
                print("🔧 Closing Crawl4AI browser...", file=sys.stderr, flush=True)
                await crawler.__aexit__(None, None, None)
                print("✓ Crawl4AI browser closed", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠️  Error closing crawler: {e}", file=sys.stderr, flush=True)

        # Clean up knowledge graph components with error handling
        if knowledge_validator or repo_extractor:
            try:
                print("🔧 Cleaning up knowledge graph...", file=sys.stderr, flush=True)
                await cleanup_knowledge_graph(knowledge_validator, repo_extractor)
                print("✓ Knowledge graph cleaned up", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠️  Error cleaning up knowledge graph: {e}", file=sys.stderr, flush=True)

        # Clean up GraphRAG components with error handling
        if document_graph_validator or document_graph_queries:
            try:
                print("🔧 Cleaning up GraphRAG...", file=sys.stderr, flush=True)
                await cleanup_graphrag(document_graph_validator, document_graph_queries)
                print("✓ GraphRAG cleaned up", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠️  Error cleaning up GraphRAG: {e}", file=sys.stderr, flush=True)

        print("✓ MCP server shutdown complete", file=sys.stderr, flush=True)
