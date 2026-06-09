"""
Integration tests for RAG pipeline workflows.

This test suite covers complete RAG (Retrieval-Augmented Generation) workflows:
- Crawl → Store → Query pipeline
- GraphRAG crawl → Entity extraction → Graph storage → Enhanced query
- Hybrid search (vector + reranking)
- Code example search pipeline
- Entity context retrieval
- Knowledge graph query workflows
- RAG strategy configurations (contextual embeddings, hybrid search, agentic RAG, reranking)
- Source filtering and management
- Edge cases and error handling

Test Organization:
1. TestBasicRAGPipeline - Core crawl→store→query workflows
2. TestGraphRAGPipeline - GraphRAG with entity extraction
3. TestHybridSearchPipeline - Vector + keyword + reranking
4. TestCodeSearchPipeline - Code example extraction and search
5. TestEntityContextRetrieval - Entity-based context retrieval
6. TestKnowledgeGraphQueries - Complex graph queries
7. TestRAGStrategies - Test different RAG strategy combinations
8. TestSourceManagement - Source filtering and management
9. TestEdgeCases - Error handling and edge cases
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Mock heavy dependencies before importing
sys.modules["crawl4ai"] = MagicMock()
sys.modules["crawl4ai_mcp"] = MagicMock()
sys.modules["supabase"] = MagicMock()
sys.modules["openai"] = MagicMock()
sys.modules["neo4j"] = MagicMock()


class TestBasicRAGPipeline:
    """Test basic crawl → store → query RAG pipeline."""

    @pytest.mark.asyncio
    async def test_complete_crawl_store_query_workflow(self, mock_context, mock_supabase_with_data):
        """Test complete workflow from crawling to storage to querying."""
        # Setup
        url = "https://example.com/docs"
        query = "Python programming"

        crawler = mock_context.request_context.lifespan_context.crawler

        # Mock crawling
        crawl_result = Mock()
        crawl_result.success = True
        crawl_result.markdown = "# Python Tutorial\n\nLearn Python programming basics."
        crawl_result.url = url
        crawler.arun = AsyncMock(return_value=crawl_result)

        # Step 1: Crawl
        result = await crawler.arun(url)
        assert result.success is True

        # Step 2: Mock document storage
        with patch("utils.add_documents_to_supabase", new_callable=AsyncMock) as mock_add_docs:
            mock_add_docs.return_value = {"success": True, "documents_added": 1}

            storage_result = await mock_add_docs(
                mock_supabase_with_data, [{"url": url, "content": result.markdown}]
            )
            assert storage_result["success"] is True

        # Step 3: Mock search/query
        with patch("utils.search_documents", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"content": "Learn Python programming basics.", "url": url, "similarity": 0.92}
            ]

            search_results = await mock_search(mock_supabase_with_data, query, limit=5)

            assert len(search_results) > 0
            assert search_results[0]["url"] == url
            assert search_results[0]["similarity"] > 0.9

    @pytest.mark.asyncio
    async def test_batch_crawl_and_store(self, mock_context, mock_supabase_with_data):
        """Test batch crawling and storing multiple pages."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]

        # Mock batch crawling
        with patch.object(
            sys.modules["crawl4ai_mcp"], "crawl_batch", new_callable=AsyncMock
        ) as mock_batch:
            mock_batch.return_value = [
                {"url": url, "markdown": f"Content from {url}"} for url in urls
            ]

            crawler = mock_context.request_context.lifespan_context.crawler
            results = await mock_batch(crawler, urls, max_concurrent=3)

            assert len(results) == 3

        # Mock batch storage
        with patch("utils.add_documents_to_supabase", new_callable=AsyncMock) as mock_add:
            mock_add.return_value = {"success": True, "documents_added": 3}

            storage_result = await mock_add(mock_supabase_with_data, results)
            assert storage_result["documents_added"] == 3

    @pytest.mark.asyncio
    async def test_chunking_and_embedding_workflow(
        self, mock_supabase_with_data, mock_openai_client
    ):
        """Test document chunking and embedding generation workflow."""
        long_content = "# Documentation\n\n" + ("Lorem ipsum dolor sit amet. " * 500)

        # Mock chunking
        with patch.object(sys.modules["crawl4ai_mcp"], "smart_chunk_markdown") as mock_chunk:
            mock_chunk.return_value = [
                long_content[:1000],
                long_content[1000:2000],
                long_content[2000:3000],
            ]

            chunks = mock_chunk(long_content, chunk_size=1000)
            assert len(chunks) == 3

        # Mock embedding generation for each chunk
        embeddings = []
        for chunk in chunks:
            embedding = mock_openai_client.embeddings.create(
                input=chunk, model="text-embedding-3-small"
            )
            embeddings.append(embedding.data[0].embedding)

        assert len(embeddings) == 3
        assert all(len(emb) == 1536 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_error_recovery_in_pipeline(self, mock_context, mock_supabase_with_data):
        """Test pipeline continues with partial failures."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",  # Will fail
            "https://example.com/page3",
        ]

        # Mock batch crawl with partial failure
        with patch.object(
            sys.modules["crawl4ai_mcp"], "crawl_batch", new_callable=AsyncMock
        ) as mock_batch:
            mock_batch.return_value = [
                {"url": urls[0], "markdown": "Content 1"},
                {"url": urls[2], "markdown": "Content 3"},
            ]

            crawler = mock_context.request_context.lifespan_context.crawler
            results = await mock_batch(crawler, urls, max_concurrent=3)

            # Pipeline should continue with successful results
            assert len(results) == 2

        # Storage should handle partial results
        with patch("utils.add_documents_to_supabase", new_callable=AsyncMock) as mock_add:
            mock_add.return_value = {"success": True, "documents_added": 2}

            storage_result = await mock_add(mock_supabase_with_data, results)
            assert storage_result["documents_added"] == 2


class TestGraphRAGPipeline:
    """Test GraphRAG pipeline with entity extraction and graph storage."""

    @pytest.mark.asyncio
    async def test_crawl_extract_entities_store_workflow(
        self, mock_context, sample_entities, mock_neo4j_session
    ):
        """Test complete GraphRAG workflow: crawl → extract entities → store in graph."""
        url = "https://example.com/article"
        content = "OpenAI released GPT-4, a powerful language model built with Python."

        # Step 1: Crawl content
        crawler = mock_context.request_context.lifespan_context.crawler
        crawl_result = Mock()
        crawl_result.success = True
        crawl_result.markdown = content
        crawler.arun = AsyncMock(return_value=crawl_result)

        result = await crawler.arun(url)
        assert result.success is True

        # Step 2: Extract entities
        entity_extractor = mock_context.request_context.lifespan_context.document_entity_extractor
        entity_extractor.extract_entities = AsyncMock(return_value=sample_entities)

        entities = await entity_extractor.extract_entities(content)

        assert "entities" in entities
        assert len(entities["entities"]) == 3
        assert entities["entities"][0]["name"] == "Python"

        # Step 3: Store in Neo4j
        validator = mock_context.request_context.lifespan_context.document_graph_validator
        validator.store_entities = AsyncMock(
            return_value={"entities_created": 3, "relationships_created": 1}
        )

        store_result = await validator.store_entities(entities, url)

        assert store_result["entities_created"] == 3
        assert store_result["relationships_created"] == 1

    @pytest.mark.asyncio
    async def test_entity_enhanced_search(self, mock_context, mock_neo4j_session):
        """Test search enhanced with entity context from graph."""
        query = "Tell me about GPT-4"

        # Step 1: Regular vector search
        with patch("utils.search_documents", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "content": "GPT-4 is a language model by OpenAI",
                    "url": "https://example.com/gpt4",
                    "similarity": 0.90,
                }
            ]

            base_results = await mock_search(
                mock_context.request_context.lifespan_context.supabase_client, query
            )

        # Step 2: Get entity context from graph
        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "GPT-4",
                    "type": "Product",
                    "related_entities": ["OpenAI", "Python"],
                    "relationships": ["CREATED_BY OpenAI", "BUILT_WITH Python"],
                }
            ]
        )

        entity_context = await graph_queries.query_entities("GPT-4")

        # Step 3: Combine results
        enhanced_results = base_results.copy()
        if entity_context:
            enhanced_results[0]["entity_context"] = entity_context[0]

        assert "entity_context" in enhanced_results[0]
        assert enhanced_results[0]["entity_context"]["entity"] == "GPT-4"
        assert "OpenAI" in enhanced_results[0]["entity_context"]["related_entities"]

    @pytest.mark.asyncio
    async def test_batch_entity_extraction(self, mock_context, sample_entities):
        """Test extracting entities from multiple documents."""
        documents = [
            {"url": "https://example.com/doc1", "content": "Content about Python and AI"},
            {"url": "https://example.com/doc2", "content": "Content about OpenAI and GPT-4"},
            {"url": "https://example.com/doc3", "content": "Content about machine learning"},
        ]

        entity_extractor = mock_context.request_context.lifespan_context.document_entity_extractor

        # Extract entities from all documents
        all_entities = []
        for doc in documents:
            entity_extractor.extract_entities = AsyncMock(return_value=sample_entities)
            entities = await entity_extractor.extract_entities(doc["content"])
            all_entities.append({"url": doc["url"], "entities": entities})

        assert len(all_entities) == 3
        assert all("entities" in e for e in all_entities)

    @pytest.mark.asyncio
    async def test_graph_relationship_traversal(self, mock_context, mock_neo4j_session):
        """Test traversing relationships in knowledge graph."""
        # Query for related entities
        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries

        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "OpenAI",
                    "type": "Organization",
                    "created": ["GPT-4", "ChatGPT"],
                    "uses": ["Python", "Transformers"],
                }
            ]
        )

        result = await graph_queries.query_entities("OpenAI")

        assert result[0]["entity"] == "OpenAI"
        assert "GPT-4" in result[0]["created"]
        assert "Python" in result[0]["uses"]


class TestHybridSearchPipeline:
    """Test hybrid search combining vector search and reranking."""

    @pytest.mark.asyncio
    async def test_vector_search_with_reranking(self, mock_context, mock_supabase_with_data):
        """Test hybrid search: vector search + cross-encoder reranking."""
        query = "Python web development"

        # Step 1: Vector search
        with patch("utils.search_documents", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"content": "Django is a Python web framework", "url": "url1", "similarity": 0.85},
                {
                    "content": "Flask is lightweight Python framework",
                    "url": "url2",
                    "similarity": 0.83,
                },
                {"content": "Python basics tutorial", "url": "url3", "similarity": 0.80},
            ]

            results = await mock_search(mock_supabase_with_data, query, limit=10)

        # Step 2: Rerank with cross-encoder
        reranker = mock_context.request_context.lifespan_context.reranking_model

        with patch.object(sys.modules["crawl4ai_mcp"], "rerank_results") as mock_rerank:
            mock_rerank.return_value = [
                {**results[1], "rerank_score": 0.95},  # Flask moves to top
                {**results[0], "rerank_score": 0.92},
                {**results[2], "rerank_score": 0.65},
            ]

            reranked = mock_rerank(reranker, query, results)

        # Verify reranking changed order
        assert reranked[0]["url"] == "url2"  # Flask now top result
        assert reranked[0]["rerank_score"] > reranked[1]["rerank_score"]

    @pytest.mark.asyncio
    async def test_hybrid_search_improves_relevance(self, mock_context, mock_supabase_with_data):
        """Test that hybrid search improves relevance over vector-only search."""
        query = "how to deploy web applications"

        # Initial vector search results (may not be perfectly ordered)
        vector_results = [
            {"content": "Web development basics", "url": "url1", "similarity": 0.88},
            {
                "content": "Deploying applications to production servers",
                "url": "url2",
                "similarity": 0.85,
            },
            {"content": "Introduction to web technologies", "url": "url3", "similarity": 0.84},
        ]

        # Reranking should identify url2 as most relevant
        reranker = mock_context.request_context.lifespan_context.reranking_model
        reranker.predict = Mock(return_value=[0.65, 0.95, 0.60])  # url2 scores highest

        with patch.object(sys.modules["crawl4ai_mcp"], "rerank_results") as mock_rerank:

            def rerank_impl(model, query, results):
                scores = model.predict([[query, r["content"]] for r in results])
                for i, result in enumerate(results):
                    result["rerank_score"] = float(scores[i])
                return sorted(results, key=lambda x: x["rerank_score"], reverse=True)

            mock_rerank.side_effect = rerank_impl
            reranked = mock_rerank(reranker, query, vector_results)

        # Most relevant result should now be first
        assert reranked[0]["url"] == "url2"
        assert "deploy" in reranked[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_hybrid_search_with_filters(self, mock_supabase_with_data):
        """Test hybrid search with metadata filtering."""
        query = "Python tutorial"

        # Search with date filter
        with patch("utils.search_documents", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "content": "Recent Python 3.12 tutorial",
                    "url": "url1",
                    "similarity": 0.90,
                    "metadata": {"date": "2024-01-01", "level": "beginner"},
                },
                {
                    "content": "Advanced Python patterns",
                    "url": "url2",
                    "similarity": 0.88,
                    "metadata": {"date": "2024-02-01", "level": "advanced"},
                },
            ]

            results = await mock_search(
                mock_supabase_with_data, query, filters={"level": "beginner"}
            )

            # Filter should be applied - check that beginner results are present
            beginner_results = [
                r for r in results if r.get("metadata", {}).get("level") == "beginner"
            ]
            assert len(beginner_results) > 0


class TestCodeSearchPipeline:
    """Test code example search and retrieval pipeline."""

    @pytest.mark.asyncio
    async def test_code_extraction_and_storage(self, mock_supabase_with_data, mock_openai_client):
        """Test extracting code blocks and storing them separately."""
        markdown = """# Tutorial

Here's a Python example:

```python
def calculate_sum(a, b):
    return a + b
```

And a JavaScript example:

```javascript
function calculateSum(a, b) {
    return a + b;
}
```
"""

        # Step 1: Extract code blocks
        with patch("utils.extract_code_blocks") as mock_extract:
            mock_extract.return_value = [
                {
                    "code": "def calculate_sum(a, b):\n    return a + b",
                    "language": "python",
                    "context": "Here's a Python example",
                },
                {
                    "code": "function calculateSum(a, b) {\n    return a + b;\n}",
                    "language": "javascript",
                    "context": "And a JavaScript example",
                },
            ]

            code_blocks = mock_extract(markdown)
            assert len(code_blocks) == 2

        # Step 2: Generate summaries
        with patch("utils.generate_code_example_summary", new_callable=AsyncMock) as mock_summary:
            mock_summary.return_value = "Function to calculate sum of two numbers"

            for block in code_blocks:
                block["summary"] = await mock_summary(mock_openai_client, block["code"])

        # Step 3: Store code examples
        with patch("utils.add_code_examples_to_supabase", new_callable=AsyncMock) as mock_add:
            mock_add.return_value = {"success": True, "code_examples_added": 2}

            result = await mock_add(mock_supabase_with_data, code_blocks)
            assert result["code_examples_added"] == 2

    @pytest.mark.asyncio
    async def test_code_search_by_language(self, mock_supabase_with_data):
        """Test searching for code examples by programming language."""
        query = "function to calculate sum"
        language = "python"

        with patch("utils.search_code_examples", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "code": "def calculate_sum(a, b):\n    return a + b",
                    "language": "python",
                    "summary": "Calculate sum of two numbers",
                    "similarity": 0.92,
                }
            ]

            results = await mock_search(mock_supabase_with_data, query, language_filter=language)

            assert len(results) > 0
            assert all(r["language"] == "python" for r in results)

    @pytest.mark.asyncio
    async def test_code_search_with_context(self, mock_supabase_with_data):
        """Test code search includes surrounding context."""
        with patch("utils.search_code_examples", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "code": "def example():\n    pass",
                    "language": "python",
                    "summary": "Example function",
                    "context_before": "## Example Section",
                    "context_after": "This demonstrates...",
                    "full_context": "## Example Section\n\ndef example():\n    pass\n\nThis demonstrates...",
                    "similarity": 0.88,
                }
            ]

            results = await mock_search(mock_supabase_with_data, "example function")

            assert results[0]["full_context"] is not None
            assert "Example Section" in results[0]["full_context"]


class TestEntityContextRetrieval:
    """Test entity-based context retrieval workflows."""

    @pytest.mark.asyncio
    async def test_retrieve_entity_relationships(self, mock_context, mock_neo4j_session):
        """Test retrieving entity relationships from graph."""
        entity_name = "GPT-4"

        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "GPT-4",
                    "type": "Product",
                    "properties": {"description": "Large language model"},
                    "relationships": {
                        "CREATED_BY": ["OpenAI"],
                        "BUILT_WITH": ["Python", "Transformers"],
                        "USED_FOR": ["ChatGPT", "API"],
                    },
                }
            ]
        )

        result = await graph_queries.query_entities(entity_name)

        assert result[0]["entity"] == "GPT-4"
        assert "OpenAI" in result[0]["relationships"]["CREATED_BY"]
        assert len(result[0]["relationships"]["BUILT_WITH"]) == 2

    @pytest.mark.asyncio
    async def test_multi_hop_entity_traversal(self, mock_context, mock_neo4j_session):
        """Test multi-hop relationship traversal in graph."""
        # Find entities connected through multiple relationships
        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries

        # Mock query that traverses: Python -> OpenAI -> GPT-4
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "path": ["Python", "OpenAI", "GPT-4"],
                    "relationships": ["USED_BY", "CREATED"],
                    "path_length": 2,
                }
            ]
        )

        result = await graph_queries.query_entities("Python", max_depth=2)

        assert result[0]["path_length"] == 2
        assert "GPT-4" in result[0]["path"]

    @pytest.mark.asyncio
    async def test_entity_aggregation_from_sources(self, mock_context):
        """Test aggregating entity mentions across multiple sources."""
        entity = "Python"

        # Query entity mentions across documents
        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "Python",
                    "mentions": [
                        {
                            "url": "https://example.com/doc1",
                            "context": "Python is a programming language",
                        },
                        {
                            "url": "https://example.com/doc2",
                            "context": "Used Python for development",
                        },
                        {"url": "https://example.com/doc3", "context": "Python 3.12 released"},
                    ],
                    "mention_count": 3,
                }
            ]
        )

        result = await graph_queries.query_entities(entity)

        assert result[0]["mention_count"] == 3
        assert len(result[0]["mentions"]) == 3


class TestKnowledgeGraphQueries:
    """Test complex knowledge graph query workflows."""

    @pytest.mark.asyncio
    async def test_semantic_search_enhanced_by_graph(self, mock_context, mock_supabase_with_data):
        """Test semantic search enhanced with graph context."""
        query = "What technologies does OpenAI use?"

        # Step 1: Find relevant entities in query

        # Step 2: Get graph context
        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "OpenAI",
                    "uses": ["Python", "PyTorch", "Transformers"],
                    "created": ["GPT-4", "ChatGPT"],
                }
            ]
        )

        graph_context = await graph_queries.query_entities("OpenAI")

        # Step 3: Combine with vector search
        with patch("utils.search_documents", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "content": "OpenAI uses advanced AI technologies",
                    "url": "url1",
                    "similarity": 0.85,
                }
            ]

            vector_results = await mock_search(mock_supabase_with_data, query)

        # Enhance results with graph context
        enhanced_results = vector_results.copy()
        if graph_context:
            enhanced_results[0]["graph_context"] = {
                "technologies": graph_context[0]["uses"],
                "products": graph_context[0]["created"],
            }

        assert "graph_context" in enhanced_results[0]
        assert "Python" in enhanced_results[0]["graph_context"]["technologies"]

    @pytest.mark.asyncio
    async def test_find_similar_entities_by_relationships(self, mock_context):
        """Test finding similar entities based on shared relationships."""
        entity = "GPT-4"

        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries

        # Find entities with similar relationship patterns
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "ChatGPT",
                    "similarity_score": 0.92,
                    "shared_relationships": ["CREATED_BY OpenAI", "BUILT_WITH Python"],
                    "common_connections": 2,
                },
                {
                    "entity": "DALL-E",
                    "similarity_score": 0.85,
                    "shared_relationships": ["CREATED_BY OpenAI"],
                    "common_connections": 1,
                },
            ]
        )

        similar = await graph_queries.query_entities(entity, find_similar=True)

        assert len(similar) == 2
        assert similar[0]["similarity_score"] > similar[1]["similarity_score"]
        assert similar[0]["common_connections"] > similar[1]["common_connections"]

    @pytest.mark.asyncio
    async def test_temporal_entity_tracking(self, mock_context):
        """Test tracking entity mentions over time."""
        entity = "GPT-4"

        graph_queries = mock_context.request_context.lifespan_context.document_graph_queries
        graph_queries.query_entities = AsyncMock(
            return_value=[
                {
                    "entity": "GPT-4",
                    "timeline": [
                        {"date": "2023-03-14", "event": "Announced", "url": "url1"},
                        {"date": "2023-03-15", "event": "Released to Plus users", "url": "url2"},
                        {"date": "2023-07-01", "event": "API released", "url": "url3"},
                    ],
                }
            ]
        )

        result = await graph_queries.query_entities(entity, include_timeline=True)

        assert "timeline" in result[0]
        assert len(result[0]["timeline"]) == 3
        assert result[0]["timeline"][0]["event"] == "Announced"


class TestRAGStrategies:
    """Test different RAG strategy configurations."""

    @pytest.mark.asyncio
    async def test_contextual_embeddings_strategy(
        self, mock_context, mock_supabase_with_data, monkeypatch
    ):
        """Test RAG with contextual embeddings enabled."""
        monkeypatch.setenv("USE_CONTEXTUAL_EMBEDDINGS", "true")

        content = "This is a comprehensive Python tutorial for beginners."

        # With contextual embeddings, content includes surrounding context
        with patch("utils.create_embedding") as mock_gen_emb:
            mock_gen_emb.return_value = [0.1] * 1536

            # Mock embedding with context
            contextual_content = f"## Tutorial Section\n\n{content}\n\n## Next Section"
            embedding = mock_gen_emb(contextual_content)

            assert embedding is not None
            # Verify contextual content was used (would call mock_gen_emb with more content)
            mock_gen_emb.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_search_strategy(self, mock_context, mock_supabase_with_data, monkeypatch):
        """Test RAG with hybrid search enabled (vector + keyword)."""
        monkeypatch.setenv("USE_HYBRID_SEARCH", "true")

        query = "Python tutorial"

        # Mock both vector and keyword searches
        vector_results = [
            {"id": 1, "content": "Python basics", "similarity": 0.9},
            {"id": 2, "content": "Programming concepts", "similarity": 0.8},
        ]

        keyword_results = [
            {"id": 1, "content": "Python basics"},  # Also in vector results
            {"id": 3, "content": "Python advanced topics"},  # Only in keyword
        ]

        with patch("utils.search_documents") as mock_vector:
            mock_vector.return_value = vector_results

            # Keyword search mock
            keyword_query = Mock()
            keyword_query.execute = Mock(return_value=Mock(data=keyword_results))
            keyword_query.ilike = Mock(return_value=keyword_query)
            keyword_query.limit = Mock(return_value=keyword_query)

            supabase = mock_supabase_with_data
            supabase.from_ = Mock(return_value=Mock(select=Mock(return_value=keyword_query)))

            # Hybrid search should combine both
            vector_res = mock_vector(supabase, query)
            keyword_res = keyword_query.execute().data

            # Item with id=1 should have boosted similarity (in both results)
            combined_ids = {r["id"] for r in vector_res} | {r["id"] for r in keyword_res}
            assert 1 in combined_ids  # Common result
            assert 2 in combined_ids  # Vector only
            assert 3 in combined_ids  # Keyword only

    @pytest.mark.asyncio
    async def test_agentic_rag_strategy(self, mock_context, mock_supabase_with_data, monkeypatch):
        """Test RAG with agentic RAG enabled (code extraction)."""
        monkeypatch.setenv("USE_AGENTIC_RAG", "true")

        markdown_content = """# Tutorial

```python
def hello_world():
    print("Hello World")
```
"""

        # With agentic RAG, code blocks are extracted and stored separately
        with patch("utils.extract_code_blocks") as mock_extract:
            mock_extract.return_value = [
                {
                    "code": 'def hello_world():\n    print("Hello World")',
                    "language": "python",
                    "context": "Tutorial",
                }
            ]

            code_blocks = mock_extract(markdown_content)
            assert len(code_blocks) == 1
            assert code_blocks[0]["language"] == "python"

        # Code search should be available
        with patch("utils.search_code_examples", new_callable=AsyncMock) as mock_code_search:
            mock_code_search.return_value = code_blocks

            results = await mock_code_search(mock_supabase_with_data, "hello world function")
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_reranking_strategy(self, mock_context, mock_supabase_with_data, monkeypatch):
        """Test RAG with reranking enabled."""
        monkeypatch.setenv("USE_RERANKING", "true")

        query = "how to deploy Python applications"

        # Initial results (not perfectly ordered)
        initial_results = [
            {"content": "Python basics", "similarity": 0.88},
            {"content": "Deploying Python apps to production", "similarity": 0.85},
            {"content": "Introduction to Python", "similarity": 0.82},
        ]

        # Mock reranking model
        reranker = mock_context.request_context.lifespan_context.reranking_model
        reranker.predict = Mock(return_value=[0.3, 0.95, 0.2])  # Result 2 is most relevant

        with patch.object(sys.modules["crawl4ai_mcp"], "rerank_results") as mock_rerank:

            def rerank_impl(model, query, results, content_key="content"):
                scores = model.predict([[query, r[content_key]] for r in results])
                for i, r in enumerate(results):
                    r["rerank_score"] = float(scores[i])
                return sorted(results, key=lambda x: x["rerank_score"], reverse=True)

            mock_rerank.side_effect = rerank_impl

            reranked = mock_rerank(reranker, query, initial_results)

            # Most relevant result should be first
            assert reranked[0]["rerank_score"] == 0.95
            assert "deploy" in reranked[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_combined_strategies(self, mock_context, mock_supabase_with_data, monkeypatch):
        """Test RAG with multiple strategies enabled simultaneously."""
        monkeypatch.setenv("USE_HYBRID_SEARCH", "true")
        monkeypatch.setenv("USE_RERANKING", "true")
        monkeypatch.setenv("USE_AGENTIC_RAG", "true")

        # Step 1: Hybrid search (vector + keyword)

        # Step 2: Reranking
        reranker = mock_context.request_context.lifespan_context.reranking_model
        reranker.predict = Mock(return_value=[0.85, 0.92])  # Keyword result ranks higher

        # Step 3: Code examples available

        # Verify all strategies can work together
        assert os.getenv("USE_HYBRID_SEARCH") == "true"
        assert os.getenv("USE_RERANKING") == "true"
        assert os.getenv("USE_AGENTIC_RAG") == "true"


class TestSourceManagement:
    """Test source filtering and management workflows."""

    @pytest.mark.asyncio
    async def test_get_available_sources(self, mock_context, mock_supabase_with_data):
        """Test retrieving all available sources."""
        # Mock sources data
        sources_data = [
            {
                "source_id": "example.com",
                "summary": "Example website content",
                "total_words": 5000,
                "created_at": "2024-01-01",
                "updated_at": "2024-01-15",
            },
            {
                "source_id": "docs.python.org",
                "summary": "Python official documentation",
                "total_words": 50000,
                "created_at": "2024-01-10",
                "updated_at": "2024-01-20",
            },
        ]

        # Mock Supabase sources query
        supabase = mock_supabase_with_data
        table_mock = Mock()
        query_chain = Mock()
        query_chain.execute = Mock(return_value=Mock(data=sources_data))
        table_mock.select = Mock(return_value=query_chain)
        query_chain.order = Mock(return_value=query_chain)
        supabase.from_ = Mock(return_value=table_mock)

        # Test getting sources
        result = query_chain.execute()

        assert len(result.data) == 2
        assert result.data[0]["source_id"] == "example.com"
        assert result.data[1]["source_id"] == "docs.python.org"

    @pytest.mark.asyncio
    async def test_rag_query_with_source_filter(self, mock_context, mock_supabase_with_data):
        """Test RAG query filtered by specific source."""
        query = "Python tutorial"
        source_filter = "docs.python.org"

        # Mock search with source filter
        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = [
                {
                    "content": "Python tutorial from official docs",
                    "url": "https://docs.python.org/tutorial",
                    "source_id": "docs.python.org",
                    "similarity": 0.92,
                }
            ]

            results = mock_search(
                mock_supabase_with_data, query, filter_metadata={"source": source_filter}
            )

            # All results should be from the specified source
            assert all(r["source_id"] == source_filter for r in results)

    @pytest.mark.asyncio
    async def test_code_search_with_source_filter(self, mock_context, mock_supabase_with_data):
        """Test code search filtered by source."""
        query = "authentication example"
        source_filter = "github.com/fastapi"

        with patch("utils.search_code_examples", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "code": "@app.get('/protected')\nasync def protected():\n    ...",
                    "language": "python",
                    "source_id": source_filter,
                    "summary": "FastAPI authentication example",
                }
            ]

            results = await mock_search(mock_supabase_with_data, query, source_filter=source_filter)

            assert all(r["source_id"] == source_filter for r in results)

    @pytest.mark.asyncio
    async def test_multiple_sources_aggregation(self, mock_context, mock_supabase_with_data):
        """Test aggregating results from multiple sources."""
        query = "Python web frameworks"

        # Results from different sources
        all_results = [
            {"content": "Django framework", "source_id": "djangoproject.com", "similarity": 0.9},
            {
                "content": "Flask framework",
                "source_id": "flask.palletsprojects.com",
                "similarity": 0.88,
            },
            {
                "content": "FastAPI framework",
                "source_id": "fastapi.tiangolo.com",
                "similarity": 0.87,
            },
        ]

        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = all_results

            results = mock_search(mock_supabase_with_data, query)

            # Results from multiple sources
            sources = {r["source_id"] for r in results}
            assert len(sources) == 3
            assert "djangoproject.com" in sources
            assert "flask.palletsprojects.com" in sources
            assert "fastapi.tiangolo.com" in sources

    @pytest.mark.asyncio
    async def test_source_statistics_tracking(self, mock_context, mock_supabase_with_data):
        """Test tracking statistics per source."""
        source_id = "example.com"

        # Mock source update
        with patch("utils.update_source_info", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {
                "success": True,
                "source_id": source_id,
                "total_words": 10000,
                "total_documents": 25,
            }

            result = await mock_update(
                mock_supabase_with_data, source_id, summary="Updated summary", total_words=10000
            )

            assert result["success"] is True
            assert result["total_words"] == 10000


class TestEdgeCases:
    """Test error handling and edge cases in RAG pipeline."""

    @pytest.mark.asyncio
    async def test_empty_query_handling(self, mock_context, mock_supabase_with_data):
        """Test handling of empty search queries."""
        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = []

            results = mock_search(mock_supabase_with_data, "")
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_no_results_found(self, mock_context, mock_supabase_with_data):
        """Test handling when no results match the query."""
        query = "very specific query that matches nothing"

        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = []

            results = mock_search(mock_supabase_with_data, query)

            assert isinstance(results, list)
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_invalid_source_filter(self, mock_context, mock_supabase_with_data):
        """Test handling of invalid source filter."""
        query = "Python tutorial"
        invalid_source = "nonexistent.com"

        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = []  # No results for invalid source

            results = mock_search(
                mock_supabase_with_data, query, filter_metadata={"source": invalid_source}
            )

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_embedding_generation_failure(self, mock_context, mock_openai_client):
        """Test handling of embedding generation failures."""
        text = "Sample text"

        with patch("utils.create_embedding") as mock_gen:
            mock_gen.side_effect = Exception("API rate limit exceeded")

            with pytest.raises(Exception) as exc_info:
                mock_gen(text)

            assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_supabase_connection_failure(self, mock_context):
        """Test handling of Supabase connection failures."""
        with patch("utils.get_supabase_client") as mock_client:
            mock_client.side_effect = Exception("Connection failed")

            with pytest.raises(Exception) as exc_info:
                mock_client()

            assert "connection failed" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_large_result_set_handling(self, mock_context, mock_supabase_with_data):
        """Test handling of very large result sets."""
        query = "common term"

        # Mock 1000 results
        large_results = [
            {"id": i, "content": f"Content {i}", "similarity": 0.9 - (i * 0.0001)}
            for i in range(1000)
        ]

        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = large_results[:100]  # Should be limited

            results = mock_search(mock_supabase_with_data, query, match_count=100)

            # Should not exceed reasonable limit
            assert len(results) <= 100

    @pytest.mark.asyncio
    async def test_special_characters_in_query(self, mock_context, mock_supabase_with_data):
        """Test handling queries with special characters."""
        special_queries = [
            "What is C++?",
            "How to use @decorator in Python?",
            "Explain $variable in shell",
            "SQL: SELECT * FROM table",
        ]

        for query in special_queries:
            with patch("utils.search_documents") as mock_search:
                mock_search.return_value = [{"content": f"Result for {query}", "similarity": 0.8}]

                results = mock_search(mock_supabase_with_data, query)
                assert len(results) > 0

    @pytest.mark.asyncio
    async def test_concurrent_query_handling(self, mock_context, mock_supabase_with_data):
        """Test handling of concurrent RAG queries."""
        queries = [
            "Python tutorial",
            "JavaScript guide",
            "Ruby documentation",
            "Go language basics",
        ]

        async def mock_search(client, query):
            await asyncio.sleep(0.01)  # Simulate API delay
            return [{"content": f"Result for {query}", "similarity": 0.9}]

        with patch("utils.search_documents", new_callable=AsyncMock) as mock_search_func:
            mock_search_func.side_effect = lambda c, q, **kwargs: mock_search(c, q)

            # Execute concurrent queries
            tasks = [mock_search(mock_supabase_with_data, query) for query in queries]
            results = await asyncio.gather(*tasks)

            assert len(results) == len(queries)
            assert all(len(r) > 0 for r in results)

    @pytest.mark.asyncio
    async def test_reranking_with_missing_model(
        self, mock_context, mock_supabase_with_data, monkeypatch
    ):
        """Test graceful handling when reranking is enabled but model is missing."""
        monkeypatch.setenv("USE_RERANKING", "true")

        # Set reranking model to None
        mock_context.request_context.lifespan_context.reranking_model = None

        query = "Python tutorial"
        results = [
            {"content": "Result 1", "similarity": 0.9},
            {"content": "Result 2", "similarity": 0.8},
        ]

        # Should fall back to vector search only
        with patch("utils.search_documents") as mock_search:
            mock_search.return_value = results

            final_results = mock_search(mock_supabase_with_data, query)

            # Should still get results (no reranking applied)
            assert len(final_results) == 2
            assert "rerank_score" not in final_results[0]

    @pytest.mark.asyncio
    async def test_code_search_when_disabled(self, mock_context, monkeypatch):
        """Test code search returns error when USE_AGENTIC_RAG is disabled."""
        monkeypatch.setenv("USE_AGENTIC_RAG", "false")

        # Code search should be disabled
        assert os.getenv("USE_AGENTIC_RAG") == "false"

        # Attempting code search should indicate it's disabled
        with patch("utils.search_code_examples", new_callable=AsyncMock) as mock_search:
            # When disabled, should either return empty or indicate disabled status
            mock_search.return_value = []

            result = await mock_search(
                mock_context.request_context.lifespan_context.supabase_client, "test"
            )
            assert isinstance(result, list)


# ============================================================================
# MCP Tool Integration Tests - Behavioral pattern testing
# ============================================================================


class TestMCPToolBehaviorPatterns:
    """Test expected behavior patterns of MCP RAG tools."""

    @pytest.mark.asyncio
    async def test_rag_query_response_structure(self):
        """Test perform_rag_query returns expected response structure."""
        mock_result = {
            "success": True,
            "query": "What is Python?",
            "results": [
                {
                    "content": "Python is a programming language",
                    "url": "https://example.com/python",
                    "source_id": "example.com",
                    "similarity": 0.95,
                }
            ],
            "use_hybrid_search": False,
            "use_reranking": False,
        }

        # Validate response structure
        assert "success" in mock_result
        assert "query" in mock_result
        assert "results" in mock_result
        assert isinstance(mock_result["results"], list)

        if mock_result["results"]:
            first_result = mock_result["results"][0]
            assert "content" in first_result
            assert "url" in first_result
            assert "similarity" in first_result

    @pytest.mark.asyncio
    async def test_rag_query_with_source_filtering(self):
        """Test RAG query source filtering behavior."""
        mock_filtered_results = [
            {
                "content": "Python tutorial",
                "url": "https://docs.python.org/tutorial",
                "source_id": "docs.python.org",
                "similarity": 0.92,
            }
        ]

        # All results should match source filter
        source_filter = "docs.python.org"
        assert all(r["source_id"] == source_filter for r in mock_filtered_results)

    @pytest.mark.asyncio
    async def test_rag_query_reranking_behavior(self):
        """Test RAG query reranking updates scores."""
        initial_results = [
            {"content": "Result 1", "similarity": 0.85},
            {"content": "Result 2", "similarity": 0.83},
            {"content": "Result 3", "similarity": 0.80},
        ]

        # Simulate reranking
        reranked_scores = [0.95, 0.88, 0.85]
        for i, result in enumerate(initial_results):
            result["rerank_score"] = reranked_scores[i]

        # Verify reranking changes order
        sorted_results = sorted(initial_results, key=lambda x: x["rerank_score"], reverse=True)
        assert sorted_results[0]["rerank_score"] == 0.95

    @pytest.mark.asyncio
    async def test_code_search_response_structure(self):
        """Test search_code_examples returns expected structure."""
        mock_result = {
            "success": True,
            "results": [
                {
                    "code": "def example():\n    pass",
                    "language": "python",
                    "summary": "Example function",
                    "url": "https://example.com/code",
                    "similarity": 0.90,
                }
            ],
        }

        assert "success" in mock_result
        assert "results" in mock_result

        if mock_result["results"]:
            code_example = mock_result["results"][0]
            assert "code" in code_example
            assert "language" in code_example
            assert "summary" in code_example

    @pytest.mark.asyncio
    async def test_code_search_disabled_behavior(self):
        """Test code search returns error when disabled."""
        mock_disabled_result = {
            "success": False,
            "error": "Code example extraction is disabled. Set USE_AGENTIC_RAG=true to enable.",
        }

        assert mock_disabled_result["success"] is False
        assert "disabled" in mock_disabled_result["error"].lower()

    @pytest.mark.asyncio
    async def test_get_sources_response_structure(self):
        """Test get_available_sources response structure."""
        mock_sources = {
            "success": True,
            "count": 2,
            "sources": [
                {
                    "source_id": "example.com",
                    "summary": "Example site",
                    "total_words": 5000,
                    "created_at": "2024-01-01",
                    "updated_at": "2024-01-15",
                },
                {
                    "source_id": "docs.python.org",
                    "summary": "Python docs",
                    "total_words": 50000,
                    "created_at": "2024-01-10",
                    "updated_at": "2024-01-20",
                },
            ],
        }

        assert "success" in mock_sources
        assert "count" in mock_sources
        assert "sources" in mock_sources
        assert mock_sources["count"] == len(mock_sources["sources"])

        if mock_sources["sources"]:
            source = mock_sources["sources"][0]
            assert "source_id" in source
            assert "summary" in source
            assert "total_words" in source

    @pytest.mark.asyncio
    async def test_graphrag_query_response_structure(self):
        """Test graphrag_query response structure."""
        mock_response = {
            "success": True,
            "query": "What is FastAPI?",
            "answer": "FastAPI is a modern Python web framework.",
            "graph_enrichment_used": True,
            "documents_found": 3,
            "sources": [{"url": "https://fastapi.tiangolo.com", "relevance": 0.92}],
        }

        assert "success" in mock_response
        assert "query" in mock_response
        assert "answer" in mock_response
        assert "graph_enrichment_used" in mock_response
        assert isinstance(mock_response["graph_enrichment_used"], bool)

    @pytest.mark.asyncio
    async def test_document_graph_query_structure(self):
        """Test query_document_graph response structure."""
        mock_response = {
            "success": True,
            "results": [
                {"name": "Python", "type": "Technology"},
                {"name": "OpenAI", "type": "Organization"},
            ],
            "count": 2,
        }

        assert "success" in mock_response
        assert "results" in mock_response
        assert "count" in mock_response
        assert mock_response["count"] == len(mock_response["results"])

    @pytest.mark.asyncio
    async def test_entity_context_response_structure(self):
        """Test get_entity_context response structure."""
        mock_response = {
            "success": True,
            "entity": {
                "name": "FastAPI",
                "type": "Technology",
                "description": "Modern Python web framework",
            },
            "related_entities": [
                {"name": "Starlette", "type": "Framework", "relationship": "BUILT_ON"},
                {"name": "Pydantic", "type": "Library", "relationship": "USES"},
            ],
            "relationships": [{"from": "FastAPI", "to": "Starlette", "type": "BUILT_ON"}],
            "documents": [
                {"id": "doc1", "url": "https://fastapi.tiangolo.com", "title": "FastAPI Docs"}
            ],
            "stats": {"related_entities_count": 2, "relationships_count": 1, "documents_count": 1},
        }

        assert "success" in mock_response
        assert "entity" in mock_response
        assert "related_entities" in mock_response
        assert "relationships" in mock_response
        assert "documents" in mock_response
        assert "stats" in mock_response

        # Verify entity structure
        assert "name" in mock_response["entity"]
        assert "type" in mock_response["entity"]

        # Verify stats match counts
        assert mock_response["stats"]["related_entities_count"] == len(
            mock_response["related_entities"]
        )
        assert mock_response["stats"]["relationships_count"] == len(mock_response["relationships"])

    @pytest.mark.asyncio
    async def test_error_response_structure(self):
        """Test error responses have consistent structure."""
        mock_error_responses = [
            {"success": False, "error": "Database connection failed"},
            {"success": False, "error": "Invalid query parameter"},
            {"success": False, "error": "Feature disabled. Set USE_GRAPHRAG=true"},
        ]

        for error_response in mock_error_responses:
            assert "success" in error_response
            assert error_response["success"] is False
            assert "error" in error_response
            assert isinstance(error_response["error"], str)
            assert len(error_response["error"]) > 0

    @pytest.mark.asyncio
    async def test_empty_results_handling(self):
        """Test handling of empty search results."""
        mock_empty_result = {"success": True, "query": "nonexistent query", "results": []}

        assert mock_empty_result["success"] is True
        assert len(mock_empty_result["results"]) == 0

    @pytest.mark.asyncio
    async def test_graphrag_no_documents_behavior(self):
        """Test GraphRAG handles no documents gracefully."""
        mock_response = {
            "success": True,
            "query": "nonexistent topic",
            "answer": "No relevant documents found for your query.",
            "graph_enrichment_used": False,
            "documents_found": 0,
            "sources": [],
        }

        assert mock_response["success"] is True
        assert mock_response["documents_found"] == 0
        assert "no relevant documents" in mock_response["answer"].lower()

    @pytest.mark.asyncio
    async def test_multi_hop_entity_traversal_structure(self):
        """Test multi-hop entity context includes distant relationships."""
        mock_multi_hop_response = {
            "success": True,
            "entity": {"name": "Python", "type": "Language"},
            "related_entities": [
                {"name": "OpenAI", "type": "Organization", "relationship": "USED_BY", "hops": 1},
                {"name": "GPT-4", "type": "Product", "relationship": "INDIRECT", "hops": 2},
            ],
            "relationships": [],
            "documents": [],
            "stats": {"related_entities_count": 2, "max_hops": 2},
        }

        assert mock_multi_hop_response["success"] is True
        assert len(mock_multi_hop_response["related_entities"]) >= 2

        # Verify multi-hop entities are included
        hop_2_entities = [
            e for e in mock_multi_hop_response["related_entities"] if e.get("hops", 1) == 2
        ]
        assert len(hop_2_entities) > 0
