"""
MCP Server Main Entry Point (Refactored)

This is the new modular server that imports tools from organized modules.
All 16 tools are now organized by category for better maintainability.
"""

import asyncio
import os
import sys
from pathlib import Path

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_GRAPHS_PATH = PROJECT_ROOT / "knowledge_graphs"

if str(KNOWLEDGE_GRAPHS_PATH) not in sys.path:
    sys.path.append(str(KNOWLEDGE_GRAPHS_PATH))

if __package__ in (None, ""):
    # Support running as a standalone script by configuring package imports.
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from src.core import crawl4ai_lifespan  # type: ignore
    from src.tools.crawling_tools import (  # type: ignore
        crawl_single_page,
        crawl_with_memory_monitoring,
        crawl_with_multi_url_config,
        crawl_with_stealth_mode,
        smart_crawl_url,
    )
    from src.tools.graphrag_tools import (  # type: ignore
        crawl_with_graph_extraction,
        get_entity_context,
        graphrag_query,
        query_document_graph,
    )
    from src.tools.rag_tools import (  # type: ignore
        perform_rag_query,
        search_code_examples,
    )
    from src.tools.source_tools import get_available_sources  # type: ignore

    try:
        from src.tools.knowledge_graph_tools import (  # type: ignore
            check_ai_script_hallucinations,
            parse_github_repositories_batch,
            parse_github_repository,
            query_knowledge_graph,
        )

        KNOWLEDGE_GRAPH_TOOLS_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        KNOWLEDGE_GRAPH_TOOLS_AVAILABLE = False
        check_ai_script_hallucinations = None  # type: ignore
        query_knowledge_graph = None  # type: ignore
        parse_github_repository = None  # type: ignore
        parse_github_repositories_batch = None  # type: ignore
else:
    from .core import crawl4ai_lifespan
    from .tools.crawling_tools import (
        crawl_single_page,
        crawl_with_memory_monitoring,
        crawl_with_multi_url_config,
        crawl_with_stealth_mode,
        smart_crawl_url,
    )
    from .tools.graphrag_tools import (
        crawl_with_graph_extraction,
        get_entity_context,
        graphrag_query,
        query_document_graph,
    )
    from .tools.rag_tools import (
        perform_rag_query,
        search_code_examples,
    )
    from .tools.source_tools import get_available_sources

    try:
        from .tools.knowledge_graph_tools import (
            check_ai_script_hallucinations,
            parse_github_repositories_batch,
            parse_github_repository,
            query_knowledge_graph,
        )

        KNOWLEDGE_GRAPH_TOOLS_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        KNOWLEDGE_GRAPH_TOOLS_AVAILABLE = False
        check_ai_script_hallucinations = None  # type: ignore
        query_knowledge_graph = None  # type: ignore
        parse_github_repository = None  # type: ignore
        parse_github_repositories_batch = None  # type: ignore


# Initialize FastMCP server with modular lifespan
mcp = FastMCP(
    name="mcp-crawl4ai-rag",
    lifespan=crawl4ai_lifespan,
)

# Register all tools with the MCP server
# Crawling tools (5)
mcp.tool()(crawl_single_page)
mcp.tool()(crawl_with_stealth_mode)
mcp.tool()(smart_crawl_url)
mcp.tool()(crawl_with_multi_url_config)
mcp.tool()(crawl_with_memory_monitoring)

# RAG tools (2)
mcp.tool()(perform_rag_query)
mcp.tool()(search_code_examples)

# Knowledge graph tools (4) - only register if available
if KNOWLEDGE_GRAPH_TOOLS_AVAILABLE:
    mcp.tool()(check_ai_script_hallucinations)
    mcp.tool()(query_knowledge_graph)
    mcp.tool()(parse_github_repository)
    mcp.tool()(parse_github_repositories_batch)

# GraphRAG tools (4)
mcp.tool()(crawl_with_graph_extraction)
mcp.tool()(graphrag_query)
mcp.tool()(query_document_graph)
mcp.tool()(get_entity_context)

# Source tools (1)
mcp.tool()(get_available_sources)

# Total: 16 tools registered


async def main():
    """Main entry point for the MCP server."""
    transport = os.getenv("TRANSPORT", "sse")

    # Add health check endpoint using FastMCP's custom_route decorator
    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request):
        """Health check endpoint for monitoring and load balancers."""
        from starlette.responses import JSONResponse

        return JSONResponse(
            {
                "status": "healthy",
                "service": "mcp-crawl4ai-rag",
                "version": "2.0.0",  # Updated version after refactoring
                "transport": transport,
                "tools_registered": 16,
                "modules": [
                    "crawling",
                    "rag",
                    "knowledge_graph",
                    "graphrag",
                    "source",
                ],
            }
        )

    if transport == "sse":
        # Run the MCP server with SSE transport
        host = os.getenv("HOST", "localhost")
        port = int(os.getenv("PORT", "8051"))
        await mcp.run_async(transport="sse", host=host, port=port)
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()


if __name__ == "__main__":
    import sys

    print(
        "✓ MCP Server configured with 16 tools across 5 categories",
        file=sys.stderr,
    )
    print("  - Crawling: 5 tools", file=sys.stderr)
    print("  - RAG: 2 tools", file=sys.stderr)
    print("  - Knowledge Graph: 4 tools", file=sys.stderr)
    print("  - GraphRAG: 4 tools", file=sys.stderr)
    print("  - Source Management: 1 tool", file=sys.stderr)

    asyncio.run(main())
