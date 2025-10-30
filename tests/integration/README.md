# Integration Tests for MCP Crawl4AI RAG Server

This directory contains comprehensive integration tests for the MCP Crawl4AI RAG server. These tests validate complete workflows and interactions between multiple components while mocking external services.

## Test Structure

### Files Created

1. **conftest.py** - Shared pytest fixtures for all integration tests
   - Mock MCP context with all services
   - Mock Supabase client with realistic data
   - Mock Neo4j session with query results
   - Mock OpenAI client
   - Sample test data fixtures
   - Environment configuration

2. **test_crawl_workflows.py** (31 tests) - End-to-end crawling workflows
   - Sitemap crawling with batch processing
   - Recursive link crawling with depth limits
   - Text file crawling
   - GitHub repository batch processing
   - Strategy selection and factory pattern
   - Memory-monitored crawling
   - Error recovery and retry logic

3. **test_rag_pipeline.py** (20 tests) - Complete RAG pipeline workflows
   - Basic crawl → store → query workflow
   - GraphRAG entity extraction and graph storage
   - Hybrid search (vector + reranking)
   - Code example extraction and search
   - Entity context retrieval
   - Knowledge graph query workflows
   - Multi-hop entity traversal

4. **test_docker_deployment.py** (37 tests) - Docker deployment scenarios
   - Environment variable validation
   - Service initialization (Supabase, Neo4j, OpenAI)
   - Lifespan context creation and cleanup
   - Graceful degradation with missing services
   - Configuration loading from environment
   - Health check endpoints
   - Security configuration
   - Error recovery and resilience

## Total Test Count

**88 Integration Tests** covering:
- Complete workflow scenarios
- Service integration
- Error handling and recovery
- Configuration management
- Performance and monitoring

## Running the Tests

### Prerequisites

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run All Integration Tests

```bash
# From project root
pytest tests/integration/ -v

# With coverage report
pytest tests/integration/ --cov=src --cov-report=html --cov-report=term
```

### Run Specific Test Files

```bash
# Crawl workflows only
pytest tests/integration/test_crawl_workflows.py -v

# RAG pipeline only
pytest tests/integration/test_rag_pipeline.py -v

# Docker deployment only
pytest tests/integration/test_docker_deployment.py -v
```

### Run Specific Test Classes

```bash
# Test sitemap crawling
pytest tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow -v

# Test GraphRAG pipeline
pytest tests/integration/test_rag_pipeline.py::TestGraphRAGPipeline -v

# Test service initialization
pytest tests/integration/test_docker_deployment.py::TestServiceInitialization -v
```

### Run with Markers

```bash
# Run only async tests
pytest tests/integration/ -v -m asyncio

# Run tests in parallel (requires pytest-xdist)
pytest tests/integration/ -n auto
```

## Test Coverage Areas

### 1. Crawling Workflows (31 tests)

#### Sitemap Crawling
- Discovery and parallel crawling
- Empty sitemap handling
- Partial failure recovery
- Network error handling

#### Recursive Crawling
- Depth limit enforcement
- Internal link following
- No content scenarios
- Error propagation

#### Text File Crawling
- Direct file retrieval
- Empty file handling
- Format validation

#### Strategy Selection
- Automatic strategy detection
- Factory pattern validation
- End-to-end workflow integration

#### GitHub Batch Processing
- Input validation
- URL validation
- Statistics calculation
- Retry logic
- Batch response building
- Single repository processing
- Retry exhaustion handling

#### Error Recovery
- Partial batch failures
- Exponential backoff
- Memory adaptive dispatching

### 2. RAG Pipeline (20 tests)

#### Basic RAG
- Crawl → Store → Query workflow
- Batch crawling and storage
- Chunking and embedding
- Error recovery in pipeline

#### GraphRAG
- Entity extraction workflow
- Graph storage
- Entity-enhanced search
- Batch entity extraction
- Relationship traversal

#### Hybrid Search
- Vector + reranking
- Relevance improvement
- Metadata filtering

#### Code Search
- Code extraction and storage
- Language-specific search
- Context inclusion

#### Entity Context
- Relationship retrieval
- Multi-hop traversal
- Entity aggregation

#### Knowledge Graph Queries
- Semantic search enhancement
- Entity similarity
- Temporal tracking

### 3. Docker Deployment (37 tests)

#### Environment Validation
- Required variable checking
- Optional variable validation
- Feature flag parsing
- Missing variable error handling

#### Service Initialization
- Supabase client setup
- Neo4j driver setup
- OpenAI client setup
- Crawler initialization
- Reranker initialization
- Initialization ordering

#### Lifespan Management
- Context creation
- Resource cleanup
- Error handling during cleanup

#### Graceful Degradation
- Missing Neo4j handling
- Connection failure logging
- Missing reranker fallback
- Partial service availability

#### Configuration
- Transport mode settings
- Host/port configuration
- Default values
- Boolean flag parsing
- Model configuration

#### Health Checks
- Endpoint responsiveness
- Service information
- Component status

#### Networking
- Internal service URLs
- External API endpoints
- Service discovery

#### Security
- API key protection
- Sensitive data masking
- Environment validation

#### Error Recovery
- Service restart recovery
- Transient error retry
- Circuit breaker pattern

#### Performance
- Initialization timing
- Memory usage tracking
- Concurrent request handling

## Mock Strategy

All tests use **comprehensive mocking** of external services:

- **Supabase**: Mocked with realistic data responses
- **Neo4j**: Mocked sessions with query results
- **OpenAI**: Mocked embeddings and chat completions
- **Crawl4AI**: Mocked crawler with realistic results

This approach ensures:
- Tests run fast (no network calls)
- Tests are deterministic
- No external service dependencies
- Easy to simulate edge cases and errors

## Test Quality Standards

Each test follows these standards:
- **Clear docstrings** explaining what is tested
- **Comprehensive assertions** verifying behavior
- **Both success and failure paths** tested
- **Realistic mock data** resembling production
- **Error scenarios** included
- **Async/await** properly handled
- **Cleanup** after tests (via fixtures)

## Adding New Tests

When adding new integration tests:

1. **Choose the right file**:
   - Crawling workflows → `test_crawl_workflows.py`
   - RAG/search workflows → `test_rag_pipeline.py`
   - Deployment/config → `test_docker_deployment.py`

2. **Use existing fixtures** from `conftest.py`

3. **Follow the pattern**:
   ```python
   @pytest.mark.asyncio
   async def test_my_workflow(self, mock_context, other_fixtures):
       """Test complete workflow for X."""
       # Setup
       # Execute
       # Verify
       assert expected_result
   ```

4. **Test both paths**:
   - Success scenario
   - Failure scenario
   - Edge cases

5. **Add docstrings** explaining the test purpose

## Continuous Integration

These tests are designed for CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  run: |
    pytest tests/integration/ -v --cov=src --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Test Maintenance

- **Review tests** when adding new features
- **Update mocks** when changing APIs
- **Add tests** for bug fixes
- **Keep fixtures** in sync with code changes
- **Monitor test performance** (should be fast)

## Known Limitations

1. **External services not tested**: Real Supabase/Neo4j integration requires separate E2E tests
2. **Network conditions not simulated**: Timeouts, retries tested via mocks only
3. **Large-scale scenarios**: Memory tests use small datasets

For full system testing with real services, see `tests/e2e/` (if available).

## Support

For questions or issues with integration tests:
1. Check test output for specific failures
2. Review mock setup in `conftest.py`
3. Verify environment variables in test fixtures
4. Check async/await syntax for async tests

---

**Last Updated**: October 2025
**Test Count**: 88 integration tests
**Coverage**: Crawling workflows, RAG pipeline, Docker deployment
