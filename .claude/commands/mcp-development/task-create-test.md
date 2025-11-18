# Create Integration Test Task

Create a comprehensive task for adding integration tests to the project.

## Usage
```
/task-create-test <test_area> [--priority=P1] [--coverage-target=70]
```

## Description
Creates a structured task for developing integration tests, including test scenarios, setup requirements, and success criteria.

## Implementation

1. **Identify test scenarios** for the area
2. **Plan test environment setup** (Docker, Neo4j, Supabase mocks)
3. **Define test data requirements**
4. **Create test file structure**
5. **Set coverage targets**

## Task File Structure

```markdown
# Task: Add Integration Tests for {test_area}

**Status**: todo
**Priority**: {priority}
**Estimated Effort**: M
**Task Type**: test
**Sprint**: Current
**Created**: {date}
**Labels**: testing, integration-tests, quality

## Description

Add comprehensive integration tests for {test_area} to increase overall test coverage from current 30% to target {coverage_target}%.

## Acceptance Criteria

- [ ] {coverage_target}% coverage achieved for {test_area}
- [ ] All integration test scenarios pass
- [ ] Tests run in CI/CD pipeline
- [ ] Test documentation added
- [ ] Test fixtures created for reuse

## Test Scenarios

### Scenario 1: {Scenario Name}
**Description**: Test that {functionality} works end-to-end

**Test Steps**:
1. Set up test environment
2. Execute action
3. Verify result
4. Clean up

**Expected Result**: {expected outcome}

**Test Data Required**:
- Sample URL or repository
- Expected output format
- Error cases to test

### Scenario 2: {Scenario Name}
**Description**: Test error handling for {error condition}

**Test Steps**:
1. Set up error condition
2. Execute action
3. Verify error response
4. Verify system state unchanged

**Expected Result**: Proper error message and no side effects

### Scenario 3: {Scenario Name}
**Description**: Test performance under load

**Test Steps**:
1. Set up multiple concurrent requests
2. Execute actions in parallel
3. Verify all complete successfully
4. Check performance metrics

**Expected Result**: All requests succeed, no timeouts

## Implementation Plan

### Step 1: Set Up Test Environment

**Files to create**:
- `tests/integration/conftest.py` - Shared fixtures
- `tests/integration/test_{test_area}.py` - Test file

**Environment Setup**:
```python
# tests/integration/conftest.py

import pytest
import asyncio
from src.crawl4ai_mcp import mcp

@pytest.fixture(scope="session")
async def mcp_server():
    \"\"\"Fixture for MCP server.\"\"\"
    # Set up test environment
    async with mcp.run_test_session() as session:
        yield session

@pytest.fixture
async def supabase_test_data():
    \"\"\"Fixture for test data in Supabase.\"\"\"
    # Set up test data
    data = create_test_data()
    yield data
    # Clean up
    cleanup_test_data(data)

@pytest.fixture
async def neo4j_test_graph():
    \"\"\"Fixture for Neo4j test graph.\"\"\"
    # Set up test graph
    graph = create_test_graph()
    yield graph
    # Clean up
    cleanup_test_graph(graph)
```

### Step 2: Write Integration Tests

**Test file structure**:
```python
# tests/integration/test_{test_area}.py

import pytest
from contextlib import asynccontextmanager

class Test{TestArea}Integration:
    \"\"\"Integration tests for {test_area}.\"\"\"

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mcp_server):
        \"\"\"Test complete workflow end-to-end.\"\"\"
        # Arrange
        test_input = prepare_test_input()

        # Act
        result = await mcp_server.call_tool(
            "tool_name",
            param1=test_input
        )

        # Assert
        assert result["success"] is True
        assert "expected_key" in result
        assert result["expected_key"] == expected_value

    @pytest.mark.asyncio
    async def test_error_handling(self, mcp_server):
        \"\"\"Test error handling.\"\"\"
        # Arrange
        invalid_input = create_invalid_input()

        # Act
        result = await mcp_server.call_tool(
            "tool_name",
            param1=invalid_input
        )

        # Assert
        assert result["success"] is False
        assert "error" in result
        assert "validation_error" in result["error_type"]

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mcp_server):
        \"\"\"Test multiple concurrent operations.\"\"\"
        # Arrange
        inputs = [create_test_input(i) for i in range(5)]

        # Act
        results = await asyncio.gather(*[
            mcp_server.call_tool("tool_name", param1=inp)
            for inp in inputs
        ])

        # Assert
        assert all(r["success"] for r in results)
        assert len(results) == 5
```

### Step 3: Add Test Fixtures

**Common test data**:
```python
# tests/integration/fixtures.py

def create_test_crawl_url():
    \"\"\"Create test URL for crawling.\"\"\"
    return "https://example.com"

def create_test_repository():
    \"\"\"Create test repository URL.\"\"\"
    return "https://github.com/test/repo.git"

def create_test_query():
    \"\"\"Create test RAG query.\"\"\"
    return "What is Python?"

async def create_test_embeddings():
    \"\"\"Create test embeddings.\"\"\"
    return [[0.1] * 1536]  # Mock embedding
```

### Step 4: Configure CI/CD

**Update** `.github/workflows/test.yml`:
```yaml
- name: Run integration tests
  run: |
    pytest tests/integration/ -v --cov=src --cov-report=xml
  env:
    # Integration test environment variables
    TEST_SUPABASE_URL: ${{ secrets.TEST_SUPABASE_URL }}
    TEST_NEO4J_URI: bolt://localhost:7687
```

## Testing Requirements

### Test Coverage Targets
| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| {test_area} | X% | {coverage_target}% | High |

### Test Categories
- [ ] Happy path tests
- [ ] Error handling tests
- [ ] Edge case tests
- [ ] Performance tests
- [ ] Concurrent operation tests

### Test Data
- [ ] Sample URLs for crawling
- [ ] Sample repositories for parsing
- [ ] Sample queries for RAG
- [ ] Error scenarios

## Environment Requirements

### Services Needed
- [ ] Supabase test database
- [ ] Neo4j test instance (if applicable)
- [ ] OpenAI test API key

### Docker Setup
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  neo4j-test:
    image: neo4j:5.0
    environment:
      NEO4J_AUTH: neo4j/testpassword
    ports:
      - "7688:7687"
```

## Documentation Updates

- [ ] Add integration test documentation to README
- [ ] Document how to run integration tests
- [ ] Document test fixtures and their usage
- [ ] Add troubleshooting section

## Definition of Done

- [ ] {coverage_target}% coverage achieved
- [ ] All integration tests passing
- [ ] Tests run in CI/CD
- [ ] Test documentation complete
- [ ] No flaky tests
- [ ] Test execution time < 5 minutes

## Performance Requirements

- [ ] Total test suite runs in < 5 minutes
- [ ] No memory leaks during test execution
- [ ] Proper cleanup of resources

## Risks

| Risk | Mitigation |
|------|------------|
| Flaky tests | Use proper async handling, cleanup fixtures |
| Slow test execution | Mock external services, use test database |
| Environment dependencies | Document setup clearly, use Docker |
```

## Example Usage

```bash
/task-create-test crawl-workflows --priority=P1 --coverage-target=70
```

Creates a task for adding integration tests to crawling workflows with 70% coverage target.

## Output

Comprehensive test task file with test scenarios, fixtures, and CI/CD integration plan.
