"""
Utility functions for GraphRAG operations (entity extraction and storage).

This module provides helper functions for the crawl_with_graph_extraction tool,
separating concerns and improving maintainability.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any
from urllib.parse import urlparse


async def initialize_graphrag_components(
    ctx: Any,
) -> tuple[dict[str, Any] | None, str | None]:
    """
    Initialize and validate GraphRAG components from context.

    Args:
        ctx: The MCP server provided context

    Returns:
        Tuple of (components_dict, error_message)
        components_dict contains: crawler, supabase_client, document_graph_validator,
        document_entity_extractor
        If initialization fails, returns (None, error_message)
    """
    # Check if GraphRAG is enabled
    graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"
    if not graphrag_enabled:
        return None, "GraphRAG functionality is disabled. Set USE_GRAPHRAG=true in environment."

    # Get components from context
    crawler = ctx.request_context.lifespan_context.crawler
    supabase_client = ctx.request_context.lifespan_context.supabase_client
    document_graph_validator_lazy = ctx.request_context.lifespan_context.document_graph_validator
    document_entity_extractor_lazy = ctx.request_context.lifespan_context.document_entity_extractor

    if not document_graph_validator_lazy or not document_entity_extractor_lazy:
        return (
            None,
            "GraphRAG components not available. Check Neo4j and OpenAI configuration.",
        )

    # Initialize GraphRAG components
    document_graph_validator = await document_graph_validator_lazy.get_validator()
    document_entity_extractor = await document_entity_extractor_lazy.get_extractor()

    if not document_graph_validator or not document_entity_extractor:
        return (
            None,
            "Failed to initialize GraphRAG components. Check Neo4j and OpenAI connection.",
        )

    return {
        "crawler": crawler,
        "supabase_client": supabase_client,
        "document_graph_validator": document_graph_validator,
        "document_entity_extractor": document_entity_extractor,
    }, None


def generate_document_id(url: str) -> str:
    """
    Generate a unique document ID from a URL using MD5 hash.

    Args:
        url: The URL to generate an ID for

    Returns:
        32-character hexadecimal document ID
    """
    return hashlib.md5(url.encode()).hexdigest()


def extract_source_info(url: str, markdown_content: str) -> tuple[str, str]:
    """
    Extract source ID and document title from URL and content.

    Args:
        url: The URL being crawled
        markdown_content: The markdown content from the crawl

    Returns:
        Tuple of (source_id, title)
    """
    parsed_url = urlparse(url)
    source_id = parsed_url.netloc or parsed_url.path

    # Extract title from first line of markdown
    title = "Untitled"
    if markdown_content:
        first_line = markdown_content.split("\n")[0]
        if first_line:
            title = first_line[:200]

    return source_id, title


async def store_graphrag_entities(
    document_graph_validator: Any,
    document_id: str,
    extraction_result: Any,
    extract_entities: bool,
) -> int:
    """
    Store extracted entities in the Neo4j knowledge graph.

    Args:
        document_graph_validator: The document graph validator instance
        document_id: Unique identifier for the document
        extraction_result: Result from entity extraction with entities list
        extract_entities: Whether to extract entities

    Returns:
        Number of entities stored
    """
    entities_stored = 0

    if extract_entities and extraction_result.entities:
        entities_dict = [
            {
                "type": entity.type,
                "name": entity.name,
                "description": entity.description,
                "mentions": entity.mentions,
            }
            for entity in extraction_result.entities
        ]
        entities_stored = await document_graph_validator.store_entities(
            document_id=document_id, entities=entities_dict
        )

    return entities_stored


async def store_graphrag_relationships(
    document_graph_validator: Any,
    extraction_result: Any,
    extract_relationships: bool,
) -> int:
    """
    Store extracted relationships in the Neo4j knowledge graph.

    Args:
        document_graph_validator: The document graph validator instance
        extraction_result: Result from entity extraction with relationships list
        extract_relationships: Whether to extract relationships

    Returns:
        Number of relationships stored
    """
    relationships_stored = 0

    if extract_relationships and extraction_result.relationships:
        relationships_dict = [
            {
                "from_entity": rel.from_entity,
                "to_entity": rel.to_entity,
                "relationship_type": rel.relationship_type,
                "description": rel.description,
                "confidence": rel.confidence,
            }
            for rel in extraction_result.relationships
        ]
        relationships_stored = await document_graph_validator.store_relationships(
            relationships=relationships_dict
        )

    return relationships_stored


def build_graphrag_crawl_response(
    success: bool,
    url: str,
    source_id: str,
    chunks_count: int,
    total_words: int,
    extraction_result: Any,
    entities_stored: int,
    relationships_stored: int,
    document_id: str,
    error: str = None,
) -> str:
    """
    Build a JSON response for the GraphRAG crawl operation.

    Args:
        success: Whether the operation was successful
        url: The URL that was crawled
        source_id: The source identifier
        chunks_count: Number of document chunks created
        total_words: Total word count in the document
        extraction_result: Result from entity extraction
        entities_stored: Number of entities stored in graph
        relationships_stored: Number of relationships stored in graph
        document_id: Unique document identifier
        error: Optional error message

    Returns:
        JSON string with operation results
    """
    response = {
        "success": success,
        "url": url,
        "source_id": source_id,
    }

    if success:
        response.update(
            {
                "crawl_results": {
                    "documents_stored": chunks_count,
                    "total_words": total_words,
                },
                "graph_extraction": {
                    "entities_found": len(extraction_result.entities),
                    "entities_stored": entities_stored,
                    "relationships_found": len(extraction_result.relationships),
                    "relationships_stored": relationships_stored,
                    "extraction_time": f"{extraction_result.extraction_time:.2f}s",
                },
                "document_id": document_id,
            }
        )
    else:
        response["error"] = error

    return json.dumps(response, indent=2)


def prepare_supabase_data(
    url: str, chunks: list[str], source_id: str, markdown_content: str, document_id: str = None
) -> dict[str, Any]:
    """
    Prepare data for storing in Supabase (vector database).

    Args:
        url: The URL being crawled
        chunks: List of content chunks
        source_id: The source identifier
        markdown_content: Full markdown content
        document_id: Optional document ID for Neo4j linkage (enables GraphRAG)

    Returns:
        Dictionary with prepared data for add_documents_to_supabase
    """
    # Build metadata with source_id and optionally document_id for GraphRAG
    if document_id:
        metadatas = [{"source_id": source_id, "document_id": document_id} for _ in chunks]
    else:
        metadatas = [{"source_id": source_id} for _ in chunks]

    return {
        "urls_list": [url] * len(chunks),
        "chunk_numbers": list(range(len(chunks))),
        "metadatas": metadatas,
        "url_to_full_document": {url: markdown_content},
    }
