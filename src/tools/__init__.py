"""
MCP Tools Package

Contains all MCP tool implementations organized by category:
- crawling_tools: Web crawling operations (5 tools)
- rag_tools: RAG query and search operations (2 tools)
- knowledge_graph_tools: Neo4j knowledge graph operations (4 tools)
- graphrag_tools: GraphRAG operations (vector + graph) (4 tools)
- source_tools: Source management operations (1 tool)

Total: 16 MCP tools
"""

from . import crawling_tools, graphrag_tools, rag_tools, source_tools

# Import knowledge_graph_tools conditionally to avoid import errors during testing
try:
    from . import knowledge_graph_tools
except (ImportError, ModuleNotFoundError):
    knowledge_graph_tools = None  # type: ignore

__all__ = [
    "crawling_tools",
    "rag_tools",
    "knowledge_graph_tools",
    "graphrag_tools",
    "source_tools",
]
