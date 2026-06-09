# 🧪 Integration Testing Guide

Comprehensive guide for running and developing integration tests for the MCP Crawl4AI RAG Server.

## Table of Contents

- [Overview](#overview)
- [Test Infrastructure](#test-infrastructure)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Writing Integration Tests](#writing-integration-tests)
- [Fixtures Reference](#fixtures-reference)
- [Test Patterns](#test-patterns)
- [Coverage Goals](#coverage-goals)
- [Troubleshooting](#troubleshooting)

---

## Overview

Integration tests verify that multiple components work together correctly in realistic scenarios. Unlike unit tests that test individual functions in isolation, integration tests:

- Test complete workflows end-to-end
- Use mocked external services (Supabase, Neo4j, OpenAI)
- Verify component interactions
- Ensure proper error handling across boundaries
- Validate MCP tool behavior patterns

### Current Status

- **Total Integration Tests**: 123 tests
- **Passing Tests**: 109 (89%)
- **Coverage**: 59.17% (Target: 70%)
- **Test Files**: 4 main test suites

### Test Suites

1. **test_crawl_workflows.py** (27 tests)
   - Single page crawling workflows
   - Smart crawl URL detection (sitemap, text, recursive)
   - Stealth mode crawling
   - Memory monitoring
   - Multi-URL configuration
   - Error handling and edge cases

2. **test_rag_pipeline.py** (70 tests)
   - Complete RAG workflow (crawl → store → query)
   - GraphRAG with entity extraction
   - Hybrid search with reranking
   - Code search pipeline
   - Entity context retrieval
   - Source management
   - Edge cases and error handling

3. **test_knowledge_graph_integration.py** (6 tests)
   - GitHub repository parsing
   - Batch repository processing
   - Knowledge graph queries

4. **test_docker_deployment.py** (20 tests)
   - Environment validation
   - Service initialization
   - Lifespan context management
   - Graceful degradation
   - Docker networking
   - Security configuration

---

## Test Infrastructure

### Directory Structure

```
tests/
├── conftest.py                      # Shared fixtures for unit tests
├── integration/
│   ├── __init__.py
│   ├── conftest.py                 # Integration test fixtures
│   ├── test_crawl_workflows.py    # Crawling integration tests
│   ├── test_rag_pipeline.py       # RAG integration tests
│   ├── test_knowledge_graph_integration.py
│   └── test_docker_deployment.py
└── test_*.py                       # Unit tests (27 files)
```

### Fixtures (tests/integration/conftest.py)

The integration test infrastructure provides comprehensive fixtures for testing complete workflows:

#### Core Fixtures

1. **mock_context**: Complete MCP context with all services
   - Crawler, Supabase, Neo4j, OpenAI mocks
   - Lifespan context structure
   - All optional features enabled

2. **mock_supabase_with_data**: Supabase mock with realistic test data
   - Pre-populated documents
   - Code examples
   - Source information

3. **mock_neo4j_session**: Neo4j session mock
   - Repository statistics
   - Entity queries
   - Relationship traversal

4. **mock_openai_client**: Azure OpenAI mock
   - Embeddings API
   - Chat completions API

5. **mock_env_config**: Environment variables
   - All required configuration
   - Feature flags enabled

#### Data Fixtures

- **sample_crawl_results**: Batch crawl results
- **sample_entities**: Entity extraction results
- **mock_crawler_result**: Single crawl result
- **mock_batch_repo_results**: GitHub batch processing results

#### Utility Fixtures

- **async_cleanup**: Async cleanup registration
  ```python
  async def test_with_cleanup(async_cleanup):
      register_cleanup = await async_cleanup
      # ... test code ...
      register_cleanup(some_async_cleanup_function())
  ```

---

## Running Tests

### Basic Commands

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_crawl_workflows.py -v

# Run specific test class
pytest tests/integration/test_rag_pipeline.py::TestBasicRAGPipeline -v

# Run specific test
pytest tests/integration/test_crawl_workflows.py::TestCrawlSinglePageWorkflow::test_crawl_single_page_success -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html

# Run only integration tests (skip unit tests)
pytest -m integration -v

# Run with detailed output
pytest tests/integration/ -vvs --tb=long
```

### Performance Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest tests/integration/ -n auto

# Stop on first failure
pytest tests/integration/ -x

# Run last failed tests only
pytest --lf

# Show slowest tests
pytest tests/integration/ --durations=10
```

### Coverage Options

```bash
# Generate HTML coverage report
pytest tests/integration/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Show missing lines in terminal
pytest tests/integration/ --cov=src --cov-report=term-missing

# Generate XML coverage for CI
pytest tests/integration/ --cov=src --cov-report=xml
```

---

## Test Organization

### Test Class Structure

Integration tests are organized by workflow or feature area:

```python
class TestCrawlSinglePageWorkflow:
    """Test complete crawl_single_page end-to-end workflow."""

    @pytest.mark.asyncio
    async def test_crawl_single_page_success(self, mock_context, mock_env_config):
        """Test successful single page crawl with storage."""
        # Arrange: Setup mocks and test data
        url = "https://example.com/docs"
        crawler = mock_context.request_context.lifespan_context.crawler

        # Act: Execute the workflow
        result = await crawl_workflow(url, crawler)

        # Assert: Verify results
        assert result["success"] is True
        assert len(result["documents"]) > 0
```

### Test Naming Convention

- **Test Files**: `test_<feature>_<type>.py`
  - Example: `test_crawl_workflows.py`, `test_rag_pipeline.py`

- **Test Classes**: `Test<Feature><Workflow>`
  - Example: `TestCrawlSinglePageWorkflow`, `TestBasicRAGPipeline`

- **Test Methods**: `test_<scenario>_<expected_outcome>`
  - Example: `test_crawl_single_page_success`, `test_invalid_url_raises_error`

### Markers

Integration tests use pytest markers for organization:

```python
@pytest.mark.asyncio        # For async tests
@pytest.mark.integration    # Mark as integration test
@pytest.mark.slow           # For slow-running tests
```

Filter by markers:
```bash
pytest -m integration       # Run only integration tests
pytest -m "not slow"        # Skip slow tests
pytest -m "integration and not slow"  # Combined
```

---

## Writing Integration Tests

### Basic Pattern

```python
import pytest
from unittest.mock import AsyncMock, Mock, patch

class TestMyWorkflow:
    """Test my workflow integration."""

    @pytest.mark.asyncio
    async def test_successful_workflow(self, mock_context, mock_env_config):
        """Test successful execution of complete workflow."""
        # 1. Arrange: Setup mocks
        crawler = mock_context.request_context.lifespan_context.crawler
        mock_result = Mock(success=True, markdown="# Test")
        crawler.arun = AsyncMock(return_value=mock_result)

        # 2. Act: Execute workflow
        result = await my_workflow_function(crawler, "https://example.com")

        # 3. Assert: Verify behavior
        assert result["success"] is True
        crawler.arun.assert_called_once()
```

### Testing Error Handling

```python
@pytest.mark.asyncio
async def test_network_failure_handling(self, mock_context):
    """Test workflow handles network failures gracefully."""
    crawler = mock_context.request_context.lifespan_context.crawler

    # Mock network error
    crawler.arun = AsyncMock(side_effect=Exception("Connection timeout"))

    # Execute and verify error handling
    result = await my_workflow_function(crawler, "https://example.com")

    assert result["success"] is False
    assert "Connection timeout" in result["error"]
```

### Testing Async Workflows

```python
@pytest.mark.asyncio
async def test_async_batch_processing(self, mock_context):
    """Test batch processing completes all items."""
    urls = ["https://example.com/1", "https://example.com/2"]

    # Mock async batch execution
    results = await batch_crawl_workflow(urls, mock_context)

    assert len(results) == 2
    assert all(r["success"] for r in results)
```

### Testing with Real External Services (Optional)

For testing with live services (use sparingly):

```python
@pytest.mark.integration
@pytest.mark.slow
async def test_with_live_supabase():
    """Test with live Supabase instance (requires credentials)."""
    if not os.getenv("SUPABASE_URL"):
        pytest.skip("Live Supabase credentials not available")

    from src.utils import get_supabase_client

    client = get_supabase_client()
    # Perform test with live client
    # IMPORTANT: Clean up test data after test
```

---

## Fixtures Reference

### mock_context

Complete MCP context with all services mocked:

```python
def test_with_context(mock_context):
    # Access components
    crawler = mock_context.request_context.lifespan_context.crawler
    supabase = mock_context.request_context.lifespan_context.supabase_client
    neo4j_validator = mock_context.request_context.lifespan_context.knowledge_validator
```

Components available:
- `crawler`: AsyncWebCrawler mock
- `supabase_client`: Supabase client mock
- `reranking_model`: CrossEncoder mock
- `knowledge_validator`: Neo4j validator mock
- `repo_extractor`: Repository extractor mock
- `document_graph_validator`: GraphRAG validator
- `document_entity_extractor`: Entity extraction
- `document_graph_queries`: Graph queries

### mock_supabase_with_data

Supabase mock with pre-populated data:

```python
def test_with_data(mock_supabase_with_data):
    # Access pre-populated data
    result = mock_supabase_with_data.rpc("match_documents", query="test").execute()
    documents = result.data  # Returns 2 sample documents
```

Includes:
- 2 sample documents with embeddings
- 1 sample code example
- 1 sample source entry

### mock_env_config

Sets all required environment variables:

```python
def test_with_env(mock_env_config):
    # All env vars are set
    assert os.getenv("SUPABASE_URL") == "https://test.supabase.co"
    assert os.getenv("USE_KNOWLEDGE_GRAPH") == "true"
```

### async_cleanup

Register async cleanup functions:

```python
async def test_with_cleanup(async_cleanup):
    register_cleanup = await async_cleanup

    # Create resources
    resource = await create_resource()

    # Register cleanup
    register_cleanup(resource.close())

    # Test with resource
    # Cleanup runs automatically even if test fails
```

---

## Test Patterns

### Pattern 1: End-to-End Workflow

Test complete user workflow from start to finish:

```python
@pytest.mark.asyncio
async def test_complete_rag_workflow(self, mock_context, mock_env_config):
    """Test: Crawl URL → Store in Supabase → Query with RAG."""
    # Step 1: Crawl
    crawl_result = await crawl_single_page("https://example.com")
    assert crawl_result["success"]

    # Step 2: Store
    store_result = await store_documents(crawl_result["documents"])
    assert store_result["documents_stored"] > 0

    # Step 3: Query
    query_result = await rag_query("test query")
    assert len(query_result["results"]) > 0
```

### Pattern 2: Component Integration

Test two or more components working together:

```python
@pytest.mark.asyncio
async def test_crawler_and_storage_integration(self, mock_context):
    """Test crawler output is correctly stored in database."""
    # Crawl with crawler
    crawl_output = await crawler.arun("https://example.com")

    # Process and store
    chunks = chunk_content(crawl_output.markdown)
    store_result = await store_chunks(chunks)

    # Verify integration
    assert store_result["success"]
```

### Pattern 3: Error Propagation

Test errors propagate correctly across component boundaries:

```python
@pytest.mark.asyncio
async def test_storage_error_propagates_to_workflow(self, mock_context):
    """Test storage failures are handled by workflow."""
    # Mock storage failure
    supabase = mock_context.request_context.lifespan_context.supabase_client
    supabase.table().insert().execute.side_effect = Exception("DB Error")

    # Execute workflow
    result = await complete_workflow("https://example.com")

    # Verify error handling
    assert result["success"] is False
    assert "DB Error" in result["error"]
```

### Pattern 4: Concurrent Execution

Test workflows handle concurrent operations:

```python
@pytest.mark.asyncio
async def test_concurrent_crawls_do_not_interfere(self):
    """Test multiple concurrent crawls complete independently."""
    urls = ["https://example.com/1", "https://example.com/2"]

    # Execute concurrently
    results = await asyncio.gather(*[crawl_workflow(url) for url in urls])

    # Verify independence
    assert all(r["success"] for r in results)
    assert len(set(r["url"] for r in results)) == 2
```

---

## Coverage Goals

### Current Coverage: 59.17%

**Target Coverage: 70%+**

### Coverage by Module

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| src/utils.py | 85% | 90% | P2 |
| src/crawling_utils.py | 78% | 85% | P2 |
| src/rag_utils.py | 72% | 80% | P2 |
| src/search_utils.py | 65% | 75% | P1 |
| src/graphrag_utils.py | 58% | 70% | P1 |
| src/github_utils.py | 55% | 70% | P1 |
| src/memory_monitor.py | 45% | 65% | P0 |

### Coverage Best Practices

1. **Prioritize critical paths**: Test main workflows first
2. **Test error handling**: Error paths are often untested
3. **Test edge cases**: Boundary conditions, empty inputs
4. **Avoid testing mocks**: Test real logic, not mock behavior
5. **Use coverage reports**: Identify untested code paths

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src.crawl4ai_mcp'`

**Solution**: The old monolithic file was refactored. Update imports:
```python
# OLD (broken)
from src.crawl4ai_mcp import smart_chunk_markdown

# NEW (correct)
from src.crawling_utils import smart_chunk_markdown
```

#### 2. Async Test Failures

**Problem**: `async def functions are not natively supported`

**Solution**: Ensure pytest-asyncio is installed and configured:
```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

**Problem**: `object MagicMock can't be used in 'await' expression`

**Solution**: Use `AsyncMock` for async functions:
```python
from unittest.mock import AsyncMock

crawler.arun = AsyncMock(return_value=result)  # Not Mock()
```

#### 3. Coverage Too Low

**Problem**: `Coverage failure: total of 59% is less than fail-under=70%`

**Solution**: Run with lower threshold for now:
```bash
pytest --cov-fail-under=29  # Current project threshold
```

Or add more integration tests to increase coverage.

#### 4. Fixtures Not Found

**Problem**: `fixture 'mock_context' not found`

**Solution**: Ensure using correct conftest.py:
- Unit tests → `tests/conftest.py`
- Integration tests → `tests/integration/conftest.py`

#### 5. Environment Variable Issues

**Problem**: Tests fail due to missing env vars

**Solution**: Use `mock_env_config` fixture:
```python
def test_with_env(mock_env_config):
    # All required env vars are set by fixture
    pass
```

#### 6. Test Isolation Issues

**Problem**: Tests fail when run together but pass individually

**Solution**: Ensure proper cleanup and avoid global state:
```python
@pytest.fixture(autouse=True)
def cleanup():
    yield
    # Clean up any global state
    cache.clear()
```

### Debug Tips

1. **Run with verbose output**:
   ```bash
   pytest tests/integration/ -vvs
   ```

2. **Show full tracebacks**:
   ```bash
   pytest tests/integration/ --tb=long
   ```

3. **Drop into debugger on failure**:
   ```bash
   pytest tests/integration/ --pdb
   ```

4. **Print captured output**:
   ```python
   def test_something(capsys):
       print("Debug info")
       # ... test code ...
       captured = capsys.readouterr()
       print(captured.out)  # See what was printed
   ```

5. **Use markers to isolate**:
   ```bash
   # Run only one test class
   pytest tests/integration/test_rag_pipeline.py::TestBasicRAGPipeline -v
   ```

---

## Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Internal Guides

- [QUICK_START.md](../QUICK_START.md) - Developer quick reference
- [TESTING_QUICK_START.md](TESTING_QUICK_START.md) - Testing overview
- [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md) - Running tests
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

### Project Files

- `tests/integration/conftest.py` - Fixture definitions
- `pytest.ini` - Test configuration
- `.github/workflows/test.yml` - CI/CD test pipeline

---

## Next Steps

### For Task-003 (Integration Test Infrastructure)

✅ **Completed**:
- Integration test fixtures created (`tests/integration/conftest.py`)
- 123 integration tests across 4 test suites
- 109 passing tests (89% pass rate)
- Coverage increased to 59.17%
- Documentation created (this guide)

⏳ **In Progress**:
- Fix remaining 14 failing tests
- Increase coverage to 70%+

📋 **Next Steps**:
1. Fix crawling strategy detection tests
2. Fix multi-URL configuration tests
3. Fix error handling edge cases
4. Add more integration tests for uncovered modules
5. Update CI/CD to run integration tests separately

### Contributing

When adding new integration tests:

1. Follow the patterns in this guide
2. Use existing fixtures when possible
3. Add new fixtures to `conftest.py` if needed
4. Document complex test scenarios
5. Update this guide with new patterns

---

**Last Updated**: October 29, 2025
**Author**: Testing Infrastructure Specialist
**Status**: ✅ Active Development - Task-003 In Progress
