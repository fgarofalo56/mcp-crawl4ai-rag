"""
GraphRAG Tools

MCP tools for GraphRAG (Graph + RAG) operations combining vector search
with knowledge graph queries.
"""

from __future__ import annotations

import json
import os
from typing import Any

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from fastmcp import Context

# Try relative imports first, fall back to absolute imports
try:
    from ..core import Crawl4AIContext
    from ..utils import (
        add_documents_to_supabase,
        extract_source_summary,
        get_supabase_client,
        update_source_info,
    )
except ImportError:
    from src.utils import (
        add_documents_to_supabase,
        extract_source_summary,
        update_source_info,
    )

# Knowledge graph imports


async def crawl_with_graph_extraction(
    ctx: Context,
    url: str,
    extract_entities: bool = True,
    extract_relationships: bool = True,
    chunk_size: int = 5000,
) -> str:
    """
    Crawl a URL and extract both vector embeddings (Supabase) and knowledge graph (Neo4j).

    This is the core GraphRAG crawl tool - it performs standard web crawling with
    vector embeddings PLUS extracts entities and relationships into a knowledge graph.

    Use this when you want rich, graph-augmented RAG capabilities where the system
    can understand entity relationships, dependencies, and connections.

    Args:
        ctx: The MCP server provided context
        url: URL to crawl
        extract_entities: Whether to extract entities (default: True)
        extract_relationships: Whether to extract relationships between entities (default: True)
        chunk_size: Size of text chunks for processing (default: 5000)

    Returns:
        JSON string with:
        - Crawl results (documents stored, chunks created)
        - Entity extraction results (entities found, relationships mapped)
        - Graph storage status
        - Statistics

    Example:
        crawl_with_graph_extraction("https://fastapi.tiangolo.com/")
    """
    try:
        try:
            from ..graphrag_utils import (
                build_graphrag_crawl_response,
                extract_source_info,
                generate_document_id,
                initialize_graphrag_components,
                prepare_supabase_data,
                store_graphrag_entities,
                store_graphrag_relationships,
            )
            from ..utils import chunk_content
        except ImportError:
            from src.graphrag_utils import (
                build_graphrag_crawl_response,
                extract_source_info,
                generate_document_id,
                initialize_graphrag_components,
                prepare_supabase_data,
                store_graphrag_entities,
                store_graphrag_relationships,
            )
            from src.utils import chunk_content

        # Initialize and validate GraphRAG components
        components, error = await initialize_graphrag_components(ctx)
        if error:
            return json.dumps({"success": False, "error": error}, indent=2)

        # Extract components
        crawler = components["crawler"]
        supabase_client = components["supabase_client"]
        document_graph_validator = components["document_graph_validator"]
        document_entity_extractor = components["document_entity_extractor"]

        # Step 1: Crawl URL
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            return json.dumps(
                {"success": False, "error": f"Failed to crawl URL: {result.error_message}"},
                indent=2,
            )

        # Step 2: Chunk content and extract source info
        chunks = chunk_content(result.markdown, max_chunk_size=chunk_size)
        source_id, title = extract_source_info(url, result.markdown)
        document_id = generate_document_id(url)  # Generate ID early for Supabase linkage

        # Step 3: Store in Supabase (vector embeddings) with document_id for GraphRAG linking
        total_word_count = len(result.markdown.split())
        source_summary = extract_source_summary(source_id, result.markdown[:5000])
        update_source_info(supabase_client, source_id, source_summary, total_word_count)

        # Prepare and store documents with document_id in metadata for GraphRAG
        supabase_data = prepare_supabase_data(url, chunks, source_id, result.markdown, document_id)
        add_documents_to_supabase(
            client=supabase_client,
            urls=supabase_data["urls_list"],
            chunk_numbers=supabase_data["chunk_numbers"],
            contents=chunks,
            metadatas=supabase_data["metadatas"],
            url_to_full_document=supabase_data["url_to_full_document"],
        )

        # Step 4: Extract entities and relationships
        extraction_result = await document_entity_extractor.extract_entities_from_chunks(
            chunks=chunks[:10],
            max_concurrent=3,  # Limit to first 10 chunks for performance
        )

        if extraction_result.error:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Entity extraction failed: {extraction_result.error}",
                    "crawl_success": True,
                    "documents_stored": len(chunks),
                },
                indent=2,
            )

        # Step 5: Store document node in Neo4j
        await document_graph_validator.store_document_node(
            document_id=document_id, source_id=source_id, url=url, title=title
        )

        # Step 6: Store entities
        entities_stored = await store_graphrag_entities(
            document_graph_validator, document_id, extraction_result, extract_entities
        )

        # Step 7: Store relationships
        relationships_stored = await store_graphrag_relationships(
            document_graph_validator, extraction_result, extract_relationships
        )

        return build_graphrag_crawl_response(
            success=True,
            url=url,
            source_id=source_id,
            chunks_count=len(chunks),
            total_words=total_word_count,
            extraction_result=extraction_result,
            entities_stored=entities_stored,
            relationships_stored=relationships_stored,
            document_id=document_id,
        )

    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {str(e)}"}, indent=2)


async def graphrag_query(
    ctx: Context,
    query: str,
    use_graph_enrichment: bool = True,
    max_entities: int = 15,
    source_filter: str | None = None,
    offset: int = 0,
    max_documents: int = 10,
    max_content_length: int = 1000,
    max_response_tokens: int = 20000,
) -> str:
    """
    Perform RAG query with optional graph enrichment for richer context.

    This tool combines vector similarity search (traditional RAG) with knowledge graph
    traversal (GraphRAG) to provide more comprehensive answers that understand
    entity relationships, dependencies, and connections.

    **Token Limit Safety**: This tool automatically truncates responses to stay within
    MCP client limits (25,000 tokens). Large result sets will be paginated.

    **When to use graph enrichment:**
    - Complex questions about how things relate
    - Questions about dependencies or prerequisites
    - Multi-hop reasoning questions
    - When you need to understand entity connections

    **When to disable graph enrichment (faster):**
    - Simple factual lookups
    - Time-sensitive queries
    - Very broad queries that don't need deep context

    Args:
        ctx: The MCP server provided context
        query: Search query
        use_graph_enrichment: Add graph context to results (default: True)
        max_entities: Maximum entities to include in graph enrichment (default: 15)
        source_filter: Optional source domain filter
        offset: Number of documents to skip for pagination (default: 0)
        max_documents: Maximum documents to retrieve (default: 10)
        max_content_length: Maximum characters per document content (default: 1000)
        max_response_tokens: Maximum tokens in response (default: 20000, hard limit: 25000)

    Returns:
        JSON string with:
        - Answer text with context
        - Source documents
        - Graph entities and relationships (if enrichment enabled)
        - Relevance scores
        - Pagination info

    Example:
        # Standard query with graph enrichment
        graphrag_query("How do I configure OAuth2 in FastAPI?", use_graph_enrichment=True)

        # Paginated query (documents 5-14)
        graphrag_query("machine learning", offset=5, max_documents=10)

        # Truncate content for large responses
        graphrag_query("comprehensive guide", max_content_length=500)
    """
    try:
        # Import required utilities
        try:
            from ..rag_utils import paginate_results
            from ..response_size_manager import (
                SizeConstraints,
                truncate_content,
                truncate_results_to_fit,
            )
            from ..utils import search_documents
        except ImportError:
            from src.rag_utils import paginate_results
            from src.response_size_manager import (
                SizeConstraints,
                truncate_content,
                truncate_results_to_fit,
            )
            from src.utils import search_documents

        from openai import AsyncAzureOpenAI, AsyncOpenAI
    except ImportError as e:
        return json.dumps(
            {"success": False, "error": f"Failed to import required modules: {str(e)}"}, indent=2
        )

    try:
        # Validate and cap parameters
        max_response_tokens = min(max_response_tokens, 20000)  # Hard cap at 20k for safety
        max_documents = min(max_documents, 50)  # Prevent excessive document retrieval

        supabase_client = ctx.request_context.lifespan_context.supabase_client
        document_graph_queries_lazy = ctx.request_context.lifespan_context.document_graph_queries

        # Build filter for source if provided
        filter_metadata = None
        if source_filter:
            filter_metadata = {"source_id": source_filter}

        # Step 1: Vector search (standard RAG) - get more for pagination
        search_limit = max_documents + offset + 10  # Buffer for pagination
        all_documents = search_documents(
            client=supabase_client,
            query=query,
            filter_metadata=filter_metadata,
            match_count=search_limit,
        )

        # Apply pagination
        documents = paginate_results(all_documents, offset=offset, limit=max_documents)

        if not documents:
            return json.dumps(
                {
                    "success": True,
                    "answer": "No relevant documents found for your query.",
                    "documents": [],
                    "graph_enrichment": None,
                },
                indent=2,
            )

        # Step 2: Graph enrichment (if enabled and available)
        enrichment_text = ""
        enrichment_data = None
        document_graph_queries = None

        if use_graph_enrichment and document_graph_queries_lazy:
            # Initialize graph queries on first use
            document_graph_queries = await document_graph_queries_lazy.get_queries()

        if use_graph_enrichment and document_graph_queries:
            # Extract document IDs from search results (stored in metadata during crawl)
            document_ids = []
            for doc in documents[:5]:  # Top 5 documents
                metadata = doc.get("metadata", {})
                if isinstance(metadata, dict):
                    doc_id = metadata.get("document_id")
                    if doc_id:
                        document_ids.append(doc_id)

            # Call the graph enrichment function
            if document_ids:
                enrichment_result = await document_graph_queries.enrich_documents_with_graph(
                    document_ids=document_ids, max_entities=max_entities
                )

                # Use the pre-formatted enrichment text
                enrichment_text = enrichment_result.enrichment_text

                # Store enrichment data for response
                enrichment_data = {
                    "entities_found": len(enrichment_result.entity_contexts),
                    "concepts": enrichment_result.related_concepts,
                    "dependencies": [
                        {"from": dep[0], "to": dep[1]} for dep in enrichment_result.dependencies
                    ],
                }
            else:
                # Document IDs not found - documents may have been crawled without GraphRAG
                enrichment_text = "\n\n**Note**: Graph enrichment unavailable for these documents. Re-crawl with `crawl_with_graph_extraction` to enable GraphRAG.\n"

        # Step 3: Build context for LLM with truncation
        context_parts = []

        # Add graph enrichment first (most important context) - truncate if needed
        if enrichment_text:
            # Truncate enrichment text if it's too long
            truncated_enrichment, was_truncated = truncate_content(
                enrichment_text, max_length=5000, add_ellipsis=True
            )
            context_parts.append(truncated_enrichment)
            context_parts.append("")

        # Add document content with size limits
        for i, doc in enumerate(documents[:5], 1):
            context_parts.append(f"**Source {i}:** {doc.get('url', 'Unknown')}")
            # Truncate document content to max_content_length
            doc_content = doc.get("content", "")
            truncated_doc, _ = truncate_content(
                doc_content, max_length=max_content_length, add_ellipsis=True
            )
            context_parts.append(truncated_doc)
            context_parts.append("")

        context = "\n".join(context_parts)

        # Step 4: Generate answer with LLM
        # Support both Azure OpenAI and standard OpenAI
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if azure_endpoint and azure_key:
            openai_client = AsyncAzureOpenAI(
                api_key=azure_key, azure_endpoint=azure_endpoint, api_version="2024-10-01-preview"
            )
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif openai_key:
            openai_client = AsyncOpenAI(api_key=openai_key)
            model = "gpt-4o-mini"
        else:
            return json.dumps(
                {
                    "success": False,
                    "error": "OpenAI API key not configured. Set OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY.",
                },
                indent=2,
            )

        response = await openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided context. When Knowledge Graph Context is provided, use it to explain relationships, dependencies, and connections between concepts. Provide comprehensive answers that show how different technologies and concepts relate to each other.",
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}\n\nProvide a detailed answer based on the context. If knowledge graph information is present, explain the relationships and dependencies.",
                },
            ],
            temperature=0.3,
        )

        answer = response.choices[0].message.content

        # Build response with pagination and size info
        response_dict = {
            "success": True,
            "query": query,
            "answer": answer,
            "graph_enrichment_used": use_graph_enrichment and enrichment_data is not None,
            "graph_enrichment": enrichment_data,
            "pagination": {
                "offset": offset,
                "requested_documents": max_documents,
                "returned_documents": len(documents),
                "total_available": len(all_documents),
                "has_more": len(all_documents) > offset + max_documents,
            },
            "sources": [
                {"url": doc.get("url", "Unknown"), "relevance": doc.get("similarity", 0)}
                for doc in documents[:5]
            ],
        }

        # Add warnings if content was truncated
        warnings = []
        if len(documents) < len(all_documents[offset : offset + max_documents]):
            warnings.append(
                f"Some documents truncated to fit within {max_response_tokens} token limit"
            )
        if len(all_documents) > offset + max_documents:
            warnings.append(
                f"Use offset parameter to access remaining {len(all_documents) - offset - max_documents} documents"
            )
        if max_content_length < 2000:
            warnings.append(
                f"Document content truncated to {max_content_length} characters per document"
            )

        if warnings:
            response_dict["warnings"] = warnings

        return json.dumps(response_dict, indent=2)

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        return json.dumps(
            {"success": False, "error": f"Query failed: {str(e)}", "details": error_details},
            indent=2,
        )


async def query_document_graph(ctx: Context, cypher_query: str) -> str:
    """
    Execute a custom Cypher query on the document knowledge graph.

    This tool provides direct access to the Neo4j document graph for advanced users
    who want to write custom graph queries.

    **Common query patterns:**

    Find all entities of a type:
    ```cypher
    MATCH (t:Technology)
    RETURN t.name, t.description
    LIMIT 10
    ```

    Find relationships:
    ```cypher
    MATCH (a)-[r:REQUIRES]->(b)
    RETURN a.name, type(r), b.name
    LIMIT 20
    ```

    Find entities mentioned in documents:
    ```cypher
    MATCH (d:Document)-[:MENTIONS]->(e)
    WHERE d.source_id = 'example.com'
    RETURN e.name, labels(e)[0] as type, count(*) as mentions
    ORDER BY mentions DESC
    ```

    Args:
        ctx: The MCP server provided context
        cypher_query: Cypher query string

    Returns:
        JSON string with query results

    Example:
        query_document_graph("MATCH (c:Concept) RETURN c.name LIMIT 10")
    """
    try:
        # Check if GraphRAG is enabled
        graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"
        if not graphrag_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "GraphRAG functionality is disabled. Set USE_GRAPHRAG=true in environment.",
                },
                indent=2,
            )

        document_graph_queries_lazy = ctx.request_context.lifespan_context.document_graph_queries

        if not document_graph_queries_lazy:
            return json.dumps(
                {
                    "success": False,
                    "error": "Document graph queries not available. Check Neo4j configuration.",
                },
                indent=2,
            )

        # Initialize queries on first use
        document_graph_queries = await document_graph_queries_lazy.get_queries()
        if not document_graph_queries:
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to initialize document graph queries. Check Neo4j connection.",
                },
                indent=2,
            )

        # Execute query
        result = await document_graph_queries.query_graph(cypher_query)

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"Query execution failed: {str(e)}"}, indent=2
        )


async def get_entity_context(ctx: Context, entity_name: str, max_hops: int = 2) -> str:
    """
    Get comprehensive context for an entity from the knowledge graph.

    This tool retrieves an entity and its neighborhood in the graph, including:
    - Entity description and type
    - Related entities (connected nodes)
    - Relationships (edges)
    - Documents that mention the entity

    Useful for:
    - Understanding what an entity is and how it relates to other concepts
    - Finding all documents that discuss a specific technology or concept
    - Exploring entity neighborhoods
    - Building context for complex questions

    Args:
        ctx: The MCP server provided context
        entity_name: Name of entity to look up (e.g., "FastAPI", "OAuth2", "Docker")
        max_hops: Maximum relationship hops to traverse (default: 2)

    Returns:
        JSON string with:
        - Entity information
        - Related entities
        - Relationships
        - Documents mentioning the entity

    Example:
        get_entity_context("FastAPI", max_hops=2)
    """
    try:
        # Check if GraphRAG is enabled
        graphrag_enabled = os.getenv("USE_GRAPHRAG", "false") == "true"
        if not graphrag_enabled:
            return json.dumps(
                {
                    "success": False,
                    "error": "GraphRAG functionality is disabled. Set USE_GRAPHRAG=true in environment.",
                },
                indent=2,
            )

        document_graph_queries_lazy = ctx.request_context.lifespan_context.document_graph_queries

        if not document_graph_queries_lazy:
            return json.dumps(
                {
                    "success": False,
                    "error": "Document graph queries not available. Check Neo4j configuration.",
                },
                indent=2,
            )

        # Initialize queries on first use
        document_graph_queries = await document_graph_queries_lazy.get_queries()
        if not document_graph_queries:
            return json.dumps(
                {
                    "success": False,
                    "error": "Failed to initialize document graph queries. Check Neo4j connection.",
                },
                indent=2,
            )

        # Get entity context
        context = await document_graph_queries.get_entity_context(
            entity_name=entity_name, max_hops=max_hops
        )

        if not context:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Entity '{entity_name}' not found in knowledge graph.",
                },
                indent=2,
            )

        return json.dumps(
            {
                "success": True,
                "entity": {
                    "name": context.entity_name,
                    "type": context.entity_type,
                    "description": context.description,
                },
                "related_entities": [
                    {"name": rel["name"], "type": rel["type"], "relationship": rel["relationship"]}
                    for rel in context.related_entities
                ],
                "relationships": [
                    {"from": rel["from"], "to": rel["to"], "type": rel["type"]}
                    for rel in context.relationships
                ],
                "documents": [
                    {"id": doc["id"], "url": doc["url"], "title": doc["title"]}
                    for doc in context.documents
                ],
                "stats": {
                    "related_entities_count": len(context.related_entities),
                    "relationships_count": len(context.relationships),
                    "documents_count": len(context.documents),
                },
            },
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"success": False, "error": f"Failed to get entity context: {str(e)}"}, indent=2
        )


async def crawl_recursive_internal_links(
    crawler: AsyncWebCrawler,
    start_urls: list[str],
    max_depth: int = 3,
    max_concurrent: int = 10,
) -> list[dict[str, Any]]:
    """
    Recursively crawl internal links from start URLs up to a maximum depth.

    Args:
        crawler: AsyncWebCrawler instance
        start_urls: List of starting URLs
        max_depth: Maximum recursion depth
        max_concurrent: Maximum number of concurrent browser sessions

    Returns:
        List of dictionaries with URL and markdown content
    """
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=max_concurrent,
    )

    visited = set()

    def normalize_url(url):
        return urldefrag(url)[0]

    current_urls = {normalize_url(u) for u in start_urls}
    results_all = []

    for _depth in range(max_depth):
        urls_to_crawl = [
            normalize_url(url) for url in current_urls if normalize_url(url) not in visited
        ]
        if not urls_to_crawl:
            break

        results = await crawler.arun_many(
            urls=urls_to_crawl, config=run_config, dispatcher=dispatcher
        )
        next_level_urls = set()

        for result in results:
            norm_url = normalize_url(result.url)
            visited.add(norm_url)

            if result.success and result.markdown:
                results_all.append({"url": result.url, "markdown": result.markdown})
                for link in result.links.get("internal", []):
                    next_url = normalize_url(link["href"])
                    if next_url not in visited:
                        next_level_urls.add(next_url)

        current_urls = next_level_urls

    return results_all


def process_and_store_crawl_results(
    supabase_client,
    crawl_results: list[dict[str, Any]],
    crawl_type: str,
    chunk_size: int = 5000,
) -> dict[str, Any]:
    """
    Process crawl results and store them in Supabase.

    This helper function consolidates the common logic for processing and storing
    crawl results that is shared across multiple crawling functions.

    Args:
        supabase_client: Supabase client instance
        crawl_results: List of crawled documents with 'url' and 'markdown' keys
        crawl_type: Type of crawl (e.g., 'sitemap', 'webpage', 'text_file')
        chunk_size: Size of chunks for splitting content

    Returns:
        Dictionary with processing statistics including:
        - chunks_stored: Number of chunks stored
        - code_examples_stored: Number of code examples stored
        - sources_updated: Number of sources updated
    """
    # Import helper functions from crawl_helpers module
    from .crawl_helpers import (
        extract_code_examples_from_documents,
        process_documentation_chunks,
        update_sources_parallel,
    )

    # Step 1: Process documentation chunks
    (
        urls,
        chunk_numbers,
        contents,
        metadatas,
        url_to_full_document,
        source_content_map,
        source_word_counts,
        chunk_count,
    ) = process_documentation_chunks(crawl_results, chunk_size)

    # Add crawl_type to metadata
    for meta in metadatas:
        meta["crawl_type"] = crawl_type

    # Step 2: Update source information in parallel
    update_sources_parallel(supabase_client, source_content_map, source_word_counts)

    # Step 3: Store documentation chunks in Supabase
    batch_size = 20
    add_documents_to_supabase(
        supabase_client,
        urls,
        chunk_numbers,
        contents,
        metadatas,
        url_to_full_document,
        batch_size=batch_size,
    )

    # Step 4: Extract and process code examples if enabled
    code_examples_count = 0
    extract_code_examples_enabled = os.getenv("USE_AGENTIC_RAG", "false") == "true"
    if extract_code_examples_enabled:
        (code_urls, code_chunk_numbers, code_examples, code_summaries, code_metadatas) = (
            extract_code_examples_from_documents(crawl_results)
        )

        # Store code examples in Supabase
        if code_examples:
            add_code_examples_to_supabase(
                supabase_client,
                code_urls,
                code_chunk_numbers,
                code_examples,
                code_summaries,
                code_metadatas,
                batch_size=batch_size,
            )
            code_examples_count = len(code_examples)

    return {
        "chunks_stored": chunk_count,
        "code_examples_stored": code_examples_count,
        "sources_updated": len(source_content_map),
    }


async def main():
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
                "version": "1.2.0",
                "transport": transport,
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


__all__ = [
    "crawl_with_graph_extraction",
    "graphrag_query",
    "query_document_graph",
    "get_entity_context",
]
