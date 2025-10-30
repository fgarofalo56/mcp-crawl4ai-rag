"""
Shared pytest fixtures for testing the MCP Crawl4AI RAG server.

This module provides reusable fixtures for mocking external dependencies
like Supabase, OpenAI, Neo4j, and Crawl4AI components.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add knowledge_graphs to Python path so imports work
repo_root = Path(__file__).parent.parent
knowledge_graphs_path = repo_root / "knowledge_graphs"
if str(knowledge_graphs_path) not in sys.path:
    sys.path.insert(0, str(knowledge_graphs_path))


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with common operations."""
    client = Mock()

    # Mock table operations
    table_mock = Mock()
    client.table.return_value = table_mock

    # Mock chainable query methods
    query_chain = Mock()
    query_chain.execute.return_value = Mock(data=[])

    table_mock.select.return_value = query_chain
    table_mock.insert.return_value = query_chain
    table_mock.update.return_value = query_chain
    table_mock.delete.return_value = query_chain
    table_mock.eq.return_value = query_chain
    table_mock.in_.return_value = query_chain
    table_mock.ilike.return_value = query_chain
    table_mock.or_.return_value = query_chain
    table_mock.order.return_value = query_chain
    table_mock.limit.return_value = query_chain

    # Mock RPC calls
    client.rpc.return_value.execute.return_value = Mock(data=[])

    return client


@pytest.fixture
def mock_openai_client():
    """Mock Azure OpenAI client."""
    client = Mock()

    # Mock embeddings API
    embeddings_mock = Mock()
    embedding_response = Mock()
    embedding_response.data = [Mock(embedding=[0.1] * 1536)]
    embeddings_mock.create.return_value = embedding_response
    client.embeddings = embeddings_mock

    # Mock chat completions API
    chat_mock = Mock()
    completions_mock = Mock()
    completion_response = Mock()
    completion_response.choices = [Mock(message=Mock(content="Test summary"))]
    completions_mock.create.return_value = completion_response
    chat_mock.completions = completions_mock
    client.chat = chat_mock

    return client


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver with async session support."""
    driver = Mock()

    # Mock async session
    session = AsyncMock()
    session.run = AsyncMock()
    session.close = AsyncMock()

    # Mock session context manager
    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)
    driver.session.return_value.__aexit__ = AsyncMock()

    driver.close = AsyncMock()

    return driver


@pytest.fixture
def mock_crawler():
    """Mock AsyncWebCrawler."""
    crawler = AsyncMock()

    # Mock crawl result
    result = Mock()
    result.success = True
    result.markdown = "# Test Content\n\nSome test markdown content."
    result.error_message = None
    result.url = "https://example.com"
    result.links = {"internal": [], "external": []}

    crawler.arun = AsyncMock(return_value=result)
    crawler.arun_many = AsyncMock(return_value=[result])

    # Mock context manager methods
    crawler.__aenter__ = AsyncMock(return_value=crawler)
    crawler.__aexit__ = AsyncMock()

    return crawler


@pytest.fixture
def mock_context():
    """Mock FastMCP context with lifespan context."""
    context = Mock()

    # Create lifespan context
    lifespan_context = Mock()
    lifespan_context.crawler = Mock()
    lifespan_context.supabase_client = Mock()
    lifespan_context.reranking_model = None
    lifespan_context.knowledge_validator = None
    lifespan_context.repo_extractor = None

    # Setup context structure
    context.request_context = Mock()
    context.request_context.lifespan_context = lifespan_context

    return context


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return r"""# Test Documentation

## Introduction
This is a test document with code examples.

## Code Example
```python
def hello_world():
    print("Hello, World!")
    return True
```

## Another Section
More content here with additional information.

```javascript
function greet(name) {
    console.log(\`Hello, \${name}!\`);
}
```

End of document.
"""


@pytest.fixture
def sample_code_blocks():
    """Sample code blocks extracted from markdown."""
    return [
        {
            "code": 'def hello_world():\n    print("Hello, World!")\n    return True',
            "language": "python",
            "context_before": "## Code Example",
            "context_after": "## Another Section",
            "full_context": '## Code Example\n\ndef hello_world():\n    print("Hello, World!")\n    return True\n\n## Another Section',
        },
        {
            "code": "function greet(name) {\n    console.log(\\`Hello, \\${name}!\\`);\n}",
            "language": "javascript",
            "context_before": "More content here",
            "context_after": "End of document",
            "full_context": "More content here\n\nfunction greet(name) {\n    console.log(\\`Hello, \\${name}!\\`);\n}\n\nEnd of document",
        },
    ]


@pytest.fixture
def sample_search_results():
    """Sample search results from vector database."""
    return [
        {
            "id": 1,
            "url": "https://example.com/page1",
            "content": "This is test content for search result 1",
            "metadata": {"chunk_index": 0, "source": "example.com"},
            "source_id": "example.com",
            "similarity": 0.95,
        },
        {
            "id": 2,
            "url": "https://example.com/page2",
            "content": "This is test content for search result 2",
            "metadata": {"chunk_index": 0, "source": "example.com"},
            "source_id": "example.com",
            "similarity": 0.85,
        },
    ]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up common environment variables for testing."""
    env_vars = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_KEY": "test-key-123",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "test-api-key",
        "AZURE_OPENAI_API_VERSION": "2025-01-01-preview",
        "DEPLOYMENT_NAME": "o4-mini",
        "EMBEDDING_DEPLOYMENT": "text-embedding-3-small",
        "MODEL_CHOICE": "gpt-4",
        "USE_RERANKING": "false",
        "USE_HYBRID_SEARCH": "false",
        "USE_AGENTIC_RAG": "false",
        "USE_CONTEXTUAL_EMBEDDINGS": "false",
        "USE_KNOWLEDGE_GRAPH": "false",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars
