"""
Application Context

Defines the main context object that holds all application state and resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from crawl4ai import AsyncWebCrawler
from supabase import Client


@dataclass
class Crawl4AIContext:
    """Context for the Crawl4AI MCP server containing all application resources."""

    crawler: AsyncWebCrawler
    supabase_client: Client
    reranking_model: Any | None = None  # CrossEncoder or LazyReranker when available
    knowledge_validator: Any | None = None  # KnowledgeGraphValidator when available
    repo_extractor: Any | None = None  # DirectNeo4jExtractor when available
    # GraphRAG components (document knowledge graph)
    document_graph_validator: Any | None = None  # DocumentGraphValidator when available
    document_entity_extractor: Any | None = None  # DocumentEntityExtractor when available
    document_graph_queries: Any | None = None  # DocumentGraphQueries when available
