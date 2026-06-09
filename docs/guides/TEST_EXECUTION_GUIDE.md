# Integration Test Execution Guide

## Prerequisites

Before running integration tests, ensure you have the required dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-xdist
```

## Quick start

### Run All Integration Tests

```bash
# From project root
cd /mnt/e/Repos/GitHub/mcp-crawl4ai-rag

# Run all integration tests with verbose output
pytest tests/integration/ -v

# Run with shorter output
pytest tests/integration/
```

Expected output:
```
tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow::test_sitemap_discovery_and_parallel_crawl PASSED
tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow::test_sitemap_with_empty_sitemap PASSED
...
================================ 88 passed in 2.34s ================================
```

## Run by Category

### Crawling Workflow Tests (31 tests)

```bash
pytest tests/integration/test_crawl_workflows.py -v
```

Tests:
- Sitemap crawling workflows
- Recursive link crawling
- Text file crawling
- Strategy selection
- GitHub batch processing
- Memory monitoring
- Error recovery

### RAG Pipeline Tests (20 tests)

```bash
pytest tests/integration/test_rag_pipeline.py -v
```

Tests:
- Basic crawl → store → query
- GraphRAG entity extraction
- Hybrid search with reranking
- Code example search
- Entity context retrieval
- Knowledge graph queries

### Docker Deployment Tests (37 tests)

```bash
pytest tests/integration/test_docker_deployment.py -v
```

Tests:
- Environment validation
- Service initialization
- Lifespan management
- Graceful degradation
- Configuration loading
- Health checks
- Security
- Error recovery

## Run Specific Test Classes

```bash
# Sitemap crawling tests
pytest tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow -v

# GraphRAG pipeline tests
pytest tests/integration/test_rag_pipeline.py::TestGraphRAGPipeline -v

# Service initialization tests
pytest tests/integration/test_docker_deployment.py::TestServiceInitialization -v
```

## Run Specific Tests

```bash
# Run a single test by name
pytest tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow::test_sitemap_discovery_and_parallel_crawl -v

# Run multiple specific tests
pytest tests/integration/ -k "test_sitemap or test_recursive" -v
```

## Code Coverage

### Generate HTML Coverage Report

```bash
pytest tests/integration/ --cov=src --cov-report=html --cov-report=term

# Open coverage report
# Linux/WSL
xdg-open htmlcov/index.html

# Or manually open: htmlcov/index.html in browser
```

### Generate Terminal Coverage Report

```bash
pytest tests/integration/ --cov=src --cov-report=term-missing
```

Output shows:
- Coverage percentage by file
- Line numbers not covered
- Overall coverage statistics

### Coverage for Specific Modules

```bash
# Coverage for crawling strategies only
pytest tests/integration/ --cov=src.crawling_strategies --cov-report=term

# Coverage for github utils only
pytest tests/integration/ --cov=src.github_utils --cov-report=term

# Coverage for main MCP server
pytest tests/integration/ --cov=src.crawl4ai_mcp --cov-report=term
```

## Advanced Options

### Run Tests in Parallel

```bash
# Requires: pip install pytest-xdist

# Auto-detect CPU cores
pytest tests/integration/ -n auto

# Specific number of workers
pytest tests/integration/ -n 4
```

### Stop on First Failure

```bash
pytest tests/integration/ -x
```

### Show Test Output

```bash
# Show print statements and logging
pytest tests/integration/ -v -s

# Show only failed test output
pytest tests/integration/ -v --tb=short
```

### Run Only Async Tests

```bash
pytest tests/integration/ -v -m asyncio
```

### Verbose Failure Details

```bash
# Show local variables on failure
pytest tests/integration/ -vv --showlocals

# Full traceback
pytest tests/integration/ -vv --tb=long
```

## Test Markers

The integration tests use these markers:

- `@pytest.mark.asyncio` - Async tests requiring asyncio support

Run specific markers:
```bash
pytest tests/integration/ -m asyncio
```

## Troubleshooting

### Import Errors

If you see import errors:

```bash
# Ensure project root is in PYTHONPATH
export PYTHONPATH=/mnt/e/Repos/GitHub/mcp-crawl4ai-rag:$PYTHONPATH

# Or run from project root
cd /mnt/e/Repos/GitHub/mcp-crawl4ai-rag
pytest tests/integration/
```

### Missing Dependencies

```bash
# Install all test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Async Test Warnings

If you see warnings about async tests, ensure pytest-asyncio is installed:

```bash
pip install pytest-asyncio
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: integration
          name: integration-tests
```

### Docker Test Runner

```dockerfile
# Dockerfile.test
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt && \
    pip install pytest pytest-asyncio pytest-cov

COPY . .

CMD ["pytest", "tests/integration/", "-v", "--cov=src", "--cov-report=term"]
```

Run in Docker:
```bash
docker build -f Dockerfile.test -t mcp-crawl4ai-tests .
docker run mcp-crawl4ai-tests
```

## Performance Benchmarking

```bash
# Install pytest-benchmark
pip install pytest-benchmark

# Run with timing
pytest tests/integration/ -v --durations=10

# Shows 10 slowest tests
```

## Filtering Tests

### By Pattern

```bash
# Run tests with "batch" in name
pytest tests/integration/ -k "batch" -v

# Run tests NOT containing "neo4j"
pytest tests/integration/ -k "not neo4j" -v

# Complex filter
pytest tests/integration/ -k "crawl and not github" -v
```

### By Path

```bash
# Run tests in specific directory
pytest tests/integration/test_crawl_workflows.py tests/integration/test_rag_pipeline.py

# Run all test files matching pattern
pytest tests/integration/test_crawl*.py
```

## Debugging Tests

### Drop into Debugger on Failure

```bash
# Requires: pip install ipdb or pdb

pytest tests/integration/ --pdb
```

### Trace Execution

```bash
pytest tests/integration/ --trace
```

### Verbose Logging

```bash
pytest tests/integration/ -v --log-cli-level=DEBUG
```

## Expected Results

When all tests pass, you should see:

```
tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow::test_sitemap_discovery_and_parallel_crawl PASSED [ 1%]
tests/integration/test_crawl_workflows.py::TestSitemapCrawlingWorkflow::test_sitemap_with_empty_sitemap PASSED [ 2%]
...
tests/integration/test_docker_deployment.py::TestPerformanceMonitoring::test_concurrent_request_handling PASSED [100%]

================================ 88 passed in 2.34s ================================
```

### Coverage Report

```
Name                              Stmts   Miss  Cover   Missing
----------------------------------------------------------------
src/crawl4ai_mcp.py                 456     54    88%   123-145, 234-256
src/crawling_strategies.py          145      8    94%   234-241
src/github_utils.py                  89      4    95%   156-159
----------------------------------------------------------------
TOTAL                               690     66    88%
```

## Next Steps After Running Tests

1. **Review Coverage Report**: Check `htmlcov/index.html` for uncovered lines
2. **Fix Failing Tests**: Address any test failures
3. **Add More Tests**: For uncovered code paths
4. **Update Documentation**: If tests reveal documentation gaps
5. **Performance Optimization**: If tests are slow

## Getting Help

If tests fail or you encounter issues:

1. **Check the test output** for specific error messages
2. **Review the test file** to understand what's being tested
3. **Check conftest.py** for fixture definitions
4. **Verify environment variables** if needed
5. **Ensure all dependencies** are installed

---

**Test Suite**: 88 integration tests
**Expected Runtime**: ~2-5 seconds
**Coverage Target**: 88%+
**Dependencies**: pytest, pytest-asyncio, pytest-cov
