"""
Shared pytest fixtures for integration tests.

This module provides comprehensive fixtures for testing complete workflows
with mocked external services (Supabase, Neo4j, OpenAI) while testing
real component integration logic.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


@pytest.fixture
def mock_context():
    """
    Fixture for MCP context with mocked services.

    Provides a complete mock context with all required services configured
    for integration testing. All external dependencies are mocked.
    """
    context = Mock()

    # Create lifespan context with all components
    lifespan_context = Mock()

    # Mock crawler
    crawler = AsyncMock()
    result = Mock()
    result.success = True
    result.markdown = "# Test Content\n\nSome test markdown content."
    result.error_message = None
    result.url = "https://example.com"
    result.links = {"internal": [], "external": []}
    crawler.arun = AsyncMock(return_value=result)
    crawler.arun_many = AsyncMock(return_value=[result])
    lifespan_context.crawler = crawler

    # Mock Supabase client
    supabase_client = Mock()
    table_mock = Mock()
    query_chain = Mock()
    query_chain.execute = Mock(return_value=Mock(data=[]))
    table_mock.select = Mock(return_value=query_chain)
    table_mock.insert = Mock(return_value=query_chain)
    table_mock.update = Mock(return_value=query_chain)
    table_mock.delete = Mock(return_value=query_chain)
    table_mock.eq = Mock(return_value=query_chain)
    table_mock.in_ = Mock(return_value=query_chain)
    table_mock.ilike = Mock(return_value=query_chain)
    table_mock.or_ = Mock(return_value=query_chain)
    table_mock.order = Mock(return_value=query_chain)
    table_mock.limit = Mock(return_value=query_chain)
    supabase_client.table = Mock(return_value=table_mock)
    supabase_client.rpc = Mock(return_value=Mock(execute=Mock(return_value=Mock(data=[]))))
    lifespan_context.supabase_client = supabase_client

    # Mock reranking model
    reranking_model = Mock()
    reranking_model.predict = Mock(return_value=[0.9, 0.8, 0.7])
    lifespan_context.reranking_model = reranking_model

    # Mock Neo4j validator
    knowledge_validator = AsyncMock()
    knowledge_validator.initialize = AsyncMock()
    knowledge_validator.close = AsyncMock()
    knowledge_validator.validate_schema = AsyncMock(return_value={"valid": True})
    lifespan_context.knowledge_validator = knowledge_validator

    # Mock repository extractor
    repo_extractor = AsyncMock()
    repo_extractor.initialize = AsyncMock()
    repo_extractor.close = AsyncMock()
    repo_extractor.analyze_repository = AsyncMock()
    repo_extractor.driver = Mock()
    session = AsyncMock()
    session.run = AsyncMock()
    session.close = AsyncMock()
    repo_extractor.driver.session = Mock(
        return_value=MagicMock(__aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock())
    )
    lifespan_context.repo_extractor = repo_extractor

    # Mock GraphRAG components
    document_graph_validator = AsyncMock()
    document_graph_validator.initialize = AsyncMock()
    document_graph_validator.close = AsyncMock()
    lifespan_context.document_graph_validator = document_graph_validator

    document_entity_extractor = AsyncMock()
    document_entity_extractor.extract_entities = AsyncMock(
        return_value={
            "entities": [
                {"name": "Test Entity", "type": "Organization", "description": "A test entity"}
            ],
            "relationships": [],
        }
    )
    lifespan_context.document_entity_extractor = document_entity_extractor

    document_graph_queries = AsyncMock()
    document_graph_queries.initialize = AsyncMock()
    document_graph_queries.close = AsyncMock()
    document_graph_queries.query_entities = AsyncMock(return_value=[])
    lifespan_context.document_graph_queries = document_graph_queries

    # Setup context structure
    context.request_context = Mock()
    context.request_context.lifespan_context = lifespan_context

    return context


@pytest.fixture
def mock_supabase_with_data():
    """
    Fixture for mocked Supabase client with realistic data.

    Returns a Supabase mock that simulates database responses
    for various query patterns.
    """
    client = Mock()

    # Sample data
    documents = [
        {
            "id": 1,
            "url": "https://example.com/page1",
            "content": "This is test content about Python programming",
            "metadata": {"chunk_index": 0},
            "source_id": "example.com",
            "embedding": [0.1] * 1536,
            "similarity": 0.95,
        },
        {
            "id": 2,
            "url": "https://example.com/page2",
            "content": "This is test content about web development",
            "metadata": {"chunk_index": 1},
            "source_id": "example.com",
            "embedding": [0.2] * 1536,
            "similarity": 0.85,
        },
    ]

    code_examples = [
        {
            "id": 1,
            "code": "def hello():\n    print('Hello')",
            "language": "python",
            "summary": "A simple hello function",
            "url": "https://example.com/code1",
        }
    ]

    def mock_table(table_name):
        """Create table-specific mock."""
        table_mock = Mock()
        query_chain = Mock()

        # Configure responses based on table
        if table_name == "documents":
            query_chain.execute = Mock(return_value=Mock(data=documents))
        elif table_name == "code_examples":
            query_chain.execute = Mock(return_value=Mock(data=code_examples))
        elif table_name == "sources":
            query_chain.execute = Mock(
                return_value=Mock(
                    data=[
                        {
                            "id": "example.com",
                            "url": "https://example.com",
                            "summary": "Example site",
                        }
                    ]
                )
            )
        else:
            query_chain.execute = Mock(return_value=Mock(data=[]))

        # Setup chainable methods
        table_mock.select = Mock(return_value=query_chain)
        table_mock.insert = Mock(return_value=query_chain)
        table_mock.update = Mock(return_value=query_chain)
        table_mock.delete = Mock(return_value=query_chain)

        # Query modifiers
        for method in ["eq", "in_", "ilike", "or_", "order", "limit", "gte", "lte"]:
            setattr(query_chain, method, Mock(return_value=query_chain))

        return table_mock

    client.table = mock_table

    # Mock RPC for vector search
    def mock_rpc(function_name, **params):
        rpc_mock = Mock()
        if function_name == "match_documents":
            rpc_mock.execute = Mock(return_value=Mock(data=documents))
        elif function_name == "match_code_examples":
            rpc_mock.execute = Mock(return_value=Mock(data=code_examples))
        else:
            rpc_mock.execute = Mock(return_value=Mock(data=[]))
        return rpc_mock

    client.rpc = mock_rpc

    return client


@pytest.fixture
def mock_neo4j_session():
    """
    Fixture for mocked Neo4j session with query results.

    Provides a realistic Neo4j session mock that returns
    test data for common queries.
    """
    session = AsyncMock()

    # Mock query results
    async def mock_run(query, **params):
        result = AsyncMock()

        # Repository statistics query
        if "files_count" in query:
            record = Mock()
            record.__getitem__ = lambda self, key: {
                "repo_name": "test-repo",
                "files_count": 10,
                "classes_count": 5,
                "methods_count": 20,
                "functions_count": 15,
            }[key]
            result.single = AsyncMock(return_value=record)
        # Entity query
        elif "MATCH (e:Entity)" in query:
            records = [
                Mock(data=lambda: {"e": {"name": "Entity1", "type": "Person"}}),
                Mock(data=lambda: {"e": {"name": "Entity2", "type": "Organization"}}),
            ]
            result.data = AsyncMock(return_value=[r.data() for r in records])
        # Default empty result
        else:
            result.single = AsyncMock(return_value=None)
            result.data = AsyncMock(return_value=[])

        return result

    session.run = mock_run
    session.close = AsyncMock()

    return session


@pytest.fixture
def mock_crawler_result():
    """
    Fixture for mock crawler result.

    Returns a realistic crawler result object for testing.
    """
    result = Mock()
    result.success = True
    result.markdown = """# Test Documentation

## Introduction
This is comprehensive test content.

## Code Example
```python
def example_function():
    return "test"
```

## More Information
Additional content here.
"""
    result.error_message = None
    result.url = "https://example.com/test"
    result.links = {
        "internal": ["https://example.com/page1", "https://example.com/page2"],
        "external": ["https://external.com"],
    }
    return result


@pytest.fixture
def sample_crawl_results():
    """
    Fixture for sample crawling results.

    Returns a list of realistic crawl results for batch testing.
    """
    return [
        {
            "url": "https://example.com/page1",
            "markdown": "# Page 1\n\nContent for page 1",
            "success": True,
        },
        {
            "url": "https://example.com/page2",
            "markdown": "# Page 2\n\nContent for page 2 with code:\n```python\ndef test(): pass\n```",
            "success": True,
        },
        {
            "url": "https://example.com/page3",
            "markdown": "# Page 3\n\nContent for page 3",
            "success": True,
        },
    ]


@pytest.fixture
def sample_entities():
    """
    Fixture for sample extracted entities.

    Returns realistic entity extraction results.
    """
    return {
        "entities": [
            {"name": "Python", "type": "Technology", "description": "A programming language"},
            {"name": "OpenAI", "type": "Organization", "description": "AI research company"},
            {"name": "GPT-4", "type": "Product", "description": "Large language model"},
        ],
        "relationships": [
            {
                "source": "OpenAI",
                "target": "GPT-4",
                "type": "CREATED",
                "description": "OpenAI created GPT-4",
            }
        ],
    }


@pytest.fixture
def mock_openai_client():
    """
    Fixture for mocked Azure OpenAI client.

    Returns a client mock with embeddings and chat completions.
    """
    client = Mock()

    # Mock embeddings API
    embeddings_mock = Mock()
    embedding_response = Mock()
    embedding_response.data = [Mock(embedding=[0.1] * 1536)]
    embeddings_mock.create = Mock(return_value=embedding_response)
    client.embeddings = embeddings_mock

    # Mock chat completions API
    chat_mock = Mock()
    completions_mock = Mock()
    completion_response = Mock()
    completion_response.choices = [
        Mock(message=Mock(content="This is a test summary of the content"))
    ]
    completions_mock.create = Mock(return_value=completion_response)
    chat_mock.completions = completions_mock
    client.chat = chat_mock

    return client


@pytest.fixture
def mock_env_config(monkeypatch):
    """
    Fixture for setting up environment variables.

    Configures all required environment variables for testing.
    """
    env_vars = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_KEY": "test-service-key-12345",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test-api-key-12345",
        "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
        "DEPLOYMENT_NAME": "o4-mini",
        "EMBEDDING_DEPLOYMENT": "text-embedding-3-small",
        "MODEL_CHOICE": "gpt-4o-mini",
        "USE_RERANKING": "true",
        "USE_HYBRID_SEARCH": "true",
        "USE_KNOWLEDGE_GRAPH": "true",
        "USE_GRAPHRAG": "true",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "test-password",
        "OPENAI_API_KEY": "test-openai-key",
        "OPENAI_MODEL": "gpt-4o-mini",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def mock_batch_repo_results():
    """
    Fixture for batch repository processing results.

    Returns realistic results from batch GitHub repository processing.
    """
    return [
        {
            "url": "https://github.com/user/repo1",
            "repository": "repo1",
            "status": "success",
            "attempt": 1,
            "statistics": {
                "files_processed": 15,
                "classes_created": 8,
                "methods_created": 42,
                "functions_created": 23,
            },
        },
        {
            "url": "https://github.com/user/repo2",
            "repository": "repo2",
            "status": "success",
            "attempt": 2,
            "statistics": {
                "files_processed": 20,
                "classes_created": 12,
                "methods_created": 56,
                "functions_created": 31,
            },
        },
        {
            "url": "https://github.com/user/repo3",
            "repository": "repo3",
            "status": "failed",
            "attempt": 3,
            "error": "Connection timeout",
            "retries_exhausted": True,
        },
    ]


@pytest.fixture
async def async_cleanup():
    """
    Fixture for async cleanup operations.

    Yields control and ensures cleanup happens even if test fails.
    """
    cleanup_tasks = []

    def register_cleanup(coro):
        cleanup_tasks.append(coro)

    yield register_cleanup

    # Run all cleanup tasks
    for task in cleanup_tasks:
        try:
            await task
        except Exception as e:
            print(f"Cleanup error: {e}")
