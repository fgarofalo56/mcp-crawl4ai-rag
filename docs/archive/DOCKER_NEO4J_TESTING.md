# Docker + Neo4j Testing Guide

This guide provides step-by-step testing procedures to verify that the Neo4j knowledge graph functionality works correctly when the MCP server runs in Docker.

## Quick Test Checklist

- [ ] Docker Compose services start successfully
- [ ] Neo4j browser is accessible
- [ ] MCP server initializes Neo4j connection
- [ ] Repository can be parsed into knowledge graph
- [ ] Knowledge graph can be queried
- [ ] AI hallucination detection works

## Test 1: Service Startup

### Start Services

```bash
# From project root
cd /path/to/mcp-crawl4ai-rag

# Start services
docker-compose up -d
```

### Verify Services are Running

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                   STATUS          PORTS
# mcp-crawl4ai-neo4j     Up (healthy)    0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
# mcp-crawl4ai-server    Up (healthy)    0.0.0.0:8051->8051/tcp
```

**✅ PASS**: Both containers show "Up (healthy)" status
**❌ FAIL**: Containers show "Exit" or "Restarting" - check logs with `docker-compose logs`

## Test 2: Neo4j Browser Access

### Access Neo4j Browser

1. Open your web browser to: http://localhost:7474
2. You should see the Neo4j Browser interface

### Login to Neo4j

- **Connect URL**: `bolt://localhost:7687`
- **Username**: `neo4j`
- **Password**: The value you set in `NEO4J_PASSWORD` env var

**✅ PASS**: Successfully logged into Neo4j Browser
**❌ FAIL**: Cannot connect - verify Neo4j container logs

### Test Neo4j with a Query

In Neo4j Browser, run:
```cypher
// Test query
RETURN "Neo4j is working!" as message
```

**✅ PASS**: Query returns the message
**❌ FAIL**: Query fails - Neo4j database may not be initialized properly

## Test 3: MCP Server Neo4j Connection

### Check MCP Server Logs

```bash
# View server startup logs
docker-compose logs mcp-server | grep -i neo4j

# Look for these success messages:
# ✓ Knowledge graph validator initialized
# ✓ Repository extractor initialized
```

**✅ PASS**: Both success messages appear in logs
**❌ FAIL**: Error messages appear - check Neo4j URI configuration

### Common Connection Errors

#### Error: "Cannot connect to Neo4j"

**Cause**: MCP server cannot reach Neo4j

**Fix**:
```bash
# Verify both containers are on same network
docker network ls
docker network inspect mcp-crawl4ai-rag_mcp-network

# Both containers should appear in the network
```

#### Error: "Authentication failed"

**Cause**: Wrong password

**Fix**:
```bash
# Check password in container
docker exec mcp-crawl4ai-server env | grep NEO4J_PASSWORD

# Should match your .env file
# If not, recreate containers:
docker-compose down
docker-compose up -d
```

## Test 4: Parse a GitHub Repository

### Using MCP Client

If you have an MCP client connected, run:

```
Please parse https://github.com/pydantic/pydantic-ai.git into the knowledge graph
```

### Using curl (Direct API Call)

```bash
curl -X POST http://localhost:8051/tools/parse_github_repository \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pydantic/pydantic-ai.git"
  }'
```

### Expected Response

```json
{
  "success": true,
  "repo_name": "pydantic-ai",
  "message": "Successfully parsed repository 'pydantic-ai' into knowledge graph",
  "statistics": {
    "repository": "pydantic-ai",
    "files_processed": 42,
    "classes_created": 28,
    "methods_created": 156,
    "functions_created": 34,
    "attributes_created": 87
  }
}
```

**✅ PASS**: Repository parsed successfully with statistics
**❌ FAIL**: Error in response - check logs

### Verify in Neo4j Browser

Run this query in Neo4j Browser:

```cypher
// Check if repository was added
MATCH (r:Repository {name: "pydantic-ai"})
RETURN r.name as repository

// Count nodes created
MATCH (r:Repository {name: "pydantic-ai"})-[:CONTAINS]->(f:File)
RETURN count(f) as file_count

// See some classes
MATCH (r:Repository {name: "pydantic-ai"})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
RETURN c.name, c.full_name
LIMIT 10
```

**✅ PASS**: Queries return data from the parsed repository
**❌ FAIL**: No data returned - parsing may have failed silently

## Test 5: Query Knowledge Graph

### Test Basic Query

Using MCP client:
```
Query the knowledge graph: repos
```

Or with curl:
```bash
curl -X POST http://localhost:8051/tools/query_knowledge_graph \
  -H "Content-Type: application/json" \
  -d '{
    "command": "repos"
  }'
```

### Expected Response

```json
{
  "success": true,
  "command": "repos",
  "data": {
    "repositories": ["pydantic-ai"]
  }
}
```

**✅ PASS**: Lists available repositories
**❌ FAIL**: Empty list or error

### Test Class Query

```
Query the knowledge graph: classes pydantic-ai
```

Should return list of classes from the repository.

**✅ PASS**: Returns class information
**❌ FAIL**: Error or no classes found

### Test Method Search

```
Query the knowledge graph: method __init__
```

Should return information about `__init__` methods across all classes.

**✅ PASS**: Returns method information
**❌ FAIL**: Method not found despite repository being parsed

## Test 6: AI Hallucination Detection

### Create Test Script

Create a test file `test_script.py`:

```python
# test_script.py - Test AI hallucination detection
from pydantic_ai import Agent

# Correct usage
agent = Agent("openai:gpt-4")

# Potential hallucination - made-up method
result = agent.fake_method_that_doesnt_exist()
```

### Run Hallucination Check

Using MCP client:
```
Check this script for hallucinations: /full/path/to/test_script.py
```

Or with curl (must copy script into container first):
```bash
# Copy script into container
docker cp test_script.py mcp-crawl4ai-server:/app/test_script.py

# Run check
docker exec mcp-crawl4ai-server python -c "
import json
from knowledge_graphs.ai_script_analyzer import AIScriptAnalyzer
from knowledge_graphs.knowledge_graph_validator import KnowledgeGraphValidator
from knowledge_graphs.hallucination_reporter import HallucinationReporter

analyzer = AIScriptAnalyzer()
analysis = analyzer.analyze_script('/app/test_script.py')

validator = KnowledgeGraphValidator('bolt://neo4j:7687', 'neo4j', 'your-password')
await validator.initialize()
validation = await validator.validate_script(analysis)

reporter = HallucinationReporter()
report = reporter.generate_comprehensive_report(validation)
print(json.dumps(report, indent=2))
"
```

### Expected Response

```json
{
  "success": true,
  "script_path": "/app/test_script.py",
  "overall_confidence": 0.5,
  "hallucinations_detected": [
    {
      "type": "method_call",
      "name": "fake_method_that_doesnt_exist",
      "confidence": "invalid",
      "message": "Method 'fake_method_that_doesnt_exist' not found in class 'Agent'"
    }
  ]
}
```

**✅ PASS**: Hallucination detected correctly
**❌ FAIL**: Hallucination not detected or wrong results

## Test 7: Network Configuration Validation

### Test 1: Verify Docker Network

```bash
# List networks
docker network ls | grep mcp

# Inspect the MCP network
docker network inspect mcp-crawl4ai-rag_mcp-network
```

**Expected**: Both `mcp-crawl4ai-server` and `mcp-crawl4ai-neo4j` containers listed

**✅ PASS**: Both containers on same network
**❌ FAIL**: Containers on different networks

### Test 2: Container-to-Container Connectivity

```bash
# Enter MCP server container
docker exec -it mcp-crawl4ai-server bash

# Test connectivity to Neo4j
curl http://neo4j:7474

# Should return HTML (Neo4j browser page)

# Test bolt protocol port
nc -zv neo4j 7687

# Should show "succeeded"

# Exit container
exit
```

**✅ PASS**: Both connectivity tests succeed
**❌ FAIL**: Connection refused - network misconfiguration

### Test 3: Environment Variables

```bash
# Check Neo4j URI in MCP container
docker exec mcp-crawl4ai-server env | grep NEO4J

# Should show:
# NEO4J_URI=bolt://neo4j:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
```

**✅ PASS**: Variables set correctly with `bolt://neo4j:7687`
**❌ FAIL**: URI still shows `localhost` or `host.docker.internal` - wrong configuration

## Test 8: Data Persistence

### Test Data Survives Container Restart

```bash
# Parse a repository (if not already done)
# ... (see Test 4)

# Stop containers
docker-compose stop

# Start containers again
docker-compose start

# Check if data persists
docker exec mcp-crawl4ai-neo4j cypher-shell -u neo4j -p your_password \
  "MATCH (r:Repository) RETURN r.name"
```

**✅ PASS**: Repository data still exists after restart
**❌ FAIL**: Data lost - volume not configured properly

## Test 9: Memory and Performance

### Monitor Resource Usage

```bash
# Check container stats
docker stats mcp-crawl4ai-server mcp-crawl4ai-neo4j

# Watch for:
# - Memory usage staying below limits
# - CPU usage reasonable during parsing
# - No container restarts
```

### Large Repository Test

Try parsing a larger repository:

```bash
# FastAPI (medium-sized repository)
curl -X POST http://localhost:8051/tools/parse_github_repository \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/tiangolo/fastapi.git"
  }'
```

**✅ PASS**: Completes without memory errors
**❌ FAIL**: Container crashes or runs out of memory

## Test 10: Health Checks

### Verify Health Check Status

```bash
# Check health status
docker-compose ps

# Both should show (healthy)
```

### Manual Health Check

```bash
# MCP Server health
curl -f http://localhost:8051/health

# Neo4j health
curl -f http://localhost:7474
```

**✅ PASS**: Both return successful responses
**❌ FAIL**: 404 or connection refused

## Troubleshooting Failed Tests

### If Tests Fail: Debugging Steps

1. **Check Logs**:
   ```bash
   # All logs
   docker-compose logs

   # Specific service
   docker-compose logs mcp-server
   docker-compose logs neo4j

   # Follow logs in real-time
   docker-compose logs -f
   ```

2. **Verify Configuration**:
   ```bash
   # Check .env file
   cat .env | grep NEO4J

   # Check docker-compose.yml
   cat docker-compose.yml | grep -A 5 NEO4J
   ```

3. **Reset Everything**:
   ```bash
   # Stop and remove everything
   docker-compose down -v  # WARNING: Deletes all data!

   # Rebuild from scratch
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Check Docker Networking**:
   ```bash
   # Ensure host.docker.internal works (Windows/Mac)
   docker run --rm alpine ping -c 1 host.docker.internal

   # Check container can reach Neo4j
   docker exec mcp-crawl4ai-server ping -c 1 neo4j
   ```

## Test Summary Template

Use this template to record your test results:

```
# Docker + Neo4j Testing Results

Date: __________
Tester: __________

## Environment
- OS: __________
- Docker Version: __________
- Docker Compose Version: __________

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| 1. Service Startup | [ ] PASS [ ] FAIL | |
| 2. Neo4j Browser Access | [ ] PASS [ ] FAIL | |
| 3. MCP Server Connection | [ ] PASS [ ] FAIL | |
| 4. Parse Repository | [ ] PASS [ ] FAIL | |
| 5. Query Knowledge Graph | [ ] PASS [ ] FAIL | |
| 6. Hallucination Detection | [ ] PASS [ ] FAIL | |
| 7. Network Configuration | [ ] PASS [ ] FAIL | |
| 8. Data Persistence | [ ] PASS [ ] FAIL | |
| 9. Memory & Performance | [ ] PASS [ ] FAIL | |
| 10. Health Checks | [ ] PASS [ ] FAIL | |

## Overall Result
[ ] ALL TESTS PASSED - Production Ready
[ ] SOME FAILURES - See notes above
[ ] MAJOR ISSUES - Requires investigation

## Notes
_Add any additional observations or issues_
```

## Automated Test Script

For convenience, here's a bash script that runs all tests automatically:

```bash
#!/bin/bash
# test_docker_neo4j.sh - Automated testing script

set -e  # Exit on error

echo "=== Docker + Neo4j Integration Test Suite ==="
echo ""

# Test 1: Service Startup
echo "[1/10] Testing service startup..."
docker-compose up -d
sleep 10  # Wait for services to initialize

if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ PASS: Services started successfully"
else
    echo "❌ FAIL: Services not healthy"
    exit 1
fi

# Test 2: Neo4j Browser
echo "[2/10] Testing Neo4j browser access..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:7474 | grep -q "200"; then
    echo "✅ PASS: Neo4j browser accessible"
else
    echo "❌ FAIL: Cannot access Neo4j browser"
    exit 1
fi

# Test 3: MCP Server Neo4j Connection
echo "[3/10] Testing MCP server Neo4j connection..."
if docker-compose logs mcp-server | grep -q "Knowledge graph validator initialized"; then
    echo "✅ PASS: MCP server connected to Neo4j"
else
    echo "❌ FAIL: MCP server cannot connect to Neo4j"
    exit 1
fi

# Test 4: Parse Repository
echo "[4/10] Testing repository parsing..."
response=$(curl -s -X POST http://localhost:8051/tools/parse_github_repository \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/pydantic/pydantic-ai.git"}')

if echo "$response" | grep -q '"success": true'; then
    echo "✅ PASS: Repository parsed successfully"
else
    echo "❌ FAIL: Repository parsing failed"
    echo "$response"
    exit 1
fi

# Test 5: Query Knowledge Graph
echo "[5/10] Testing knowledge graph query..."
response=$(curl -s -X POST http://localhost:8051/tools/query_knowledge_graph \
  -H "Content-Type: application/json" \
  -d '{"command": "repos"}')

if echo "$response" | grep -q "pydantic-ai"; then
    echo "✅ PASS: Knowledge graph query successful"
else
    echo "❌ FAIL: Knowledge graph query failed"
    exit 1
fi

echo ""
echo "=== All Tests Passed! ==="
echo "Docker + Neo4j integration is working correctly"
```

Save as `test_docker_neo4j.sh`, make executable (`chmod +x test_docker_neo4j.sh`), and run:

```bash
./test_docker_neo4j.sh
```

## Continuous Integration

For CI/CD pipelines, add this to your `.github/workflows/docker-neo4j-test.yml`:

```yaml
name: Docker + Neo4j Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Create .env file
        run: |
          echo "NEO4J_PASSWORD=test_password" > .env
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env
          echo "SUPABASE_URL=${{ secrets.SUPABASE_URL }}" >> .env
          echo "SUPABASE_SERVICE_KEY=${{ secrets.SUPABASE_SERVICE_KEY }}" >> .env
          echo "USE_KNOWLEDGE_GRAPH=true" >> .env

      - name: Start services
        run: docker-compose up -d

      - name: Wait for healthy containers
        run: |
          for i in {1..30}; do
            if docker-compose ps | grep -q "Up (healthy)"; then
              echo "Services are healthy"
              exit 0
            fi
            echo "Waiting for services... ($i/30)"
            sleep 10
          done
          echo "Services failed to become healthy"
          exit 1

      - name: Run integration tests
        run: ./test_docker_neo4j.sh

      - name: Cleanup
        if: always()
        run: docker-compose down -v
```

## Support

If you encounter issues during testing:

1. Review logs: `docker-compose logs`
2. Check [Docker Setup Guide](DOCKER_SETUP.md) troubleshooting section
3. Open an issue on GitHub with:
   - Your test results
   - Docker version
   - OS information
   - Relevant log excerpts
