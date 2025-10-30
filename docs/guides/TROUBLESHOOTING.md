# 🔧 Troubleshooting guide

> **🏠 [Home](../../README.md)** | **📖 [Documentation](../README.md)** | **📚 [Guides](README.md)** | **👤 Troubleshooting**

---

This guide helps you resolve common issues with the mcp-crawl4ai-rag project. Issues are organized by category with clear symptoms, causes, and step-by-step solutions.

## Table of contents

- [Installation issues](#installation-issues)
  - [Playwright Browser Not Found](#playwright-browser-not-found) ⭐ NEW
  - [Dependency Conflicts](#dependency-conflicts)
  - [Docker Setup Problems](#docker-setup-problems)
  - [Neo4j Connection Failures](#neo4j-connection-failures)
  - [Python Version Issues](#python-version-issues)
  - [UV Installation Problems](#uv-installation-problems)
- [Runtime Issues](#runtime-issues)
  - [Crawling Failures](#crawling-failures)
  - [Memory Problems](#memory-problems)
  - [Neo4j Query Timeouts](#neo4j-query-timeouts)
  - [Supabase Connection Errors](#supabase-connection-errors)
  - [Import Errors](#import-errors)
- [Configuration Issues](#configuration-issues)
  - [Environment Variable Problems](#environment-variable-problems)
  - [Transport Mode Configuration](#transport-mode-configuration)
  - [RAG Strategy Conflicts](#rag-strategy-conflicts)
  - [Neo4j URI Configuration](#neo4j-uri-configuration)
  - [Docker Networking Issues](#docker-networking-issues)
- [Claude Desktop Integration](#claude-desktop-integration)
  - [Server Not Appearing](#server-not-appearing)
  - [Connection Timeouts](#connection-timeouts)
  - [Stdio Protocol Violations](#stdio-protocol-violations)
  - [Restarting Claude Desktop](#restarting-claude-desktop)
- [Development Issues](#development-issues)
  - [Test Failures](#test-failures)
  - [Coverage Reporting](#coverage-reporting)
  - [Pre-commit Hook Failures](#pre-commit-hook-failures)
  - [Linting Errors](#linting-errors)
- [Debugging Tools & Techniques](#debugging-tools--techniques)
  - [Log Locations](#log-locations)
  - [Verbose Mode Activation](#verbose-mode-activation)
  - [Component Testing](#component-testing)
  - [Health Checks](#health-checks)
  - [Manual Connection Testing](#manual-connection-testing)

---

## Installation Issues

### Playwright Browser Not Found

#### Symptom: Server fails to start with browser error
```
❌ FAILED TO INITIALIZE CRAWL4AI BROWSER
Error: Executable doesn't exist at C:\Users\...\playwright\driver\package\.local-browsers\chromium-1187\chrome-win\chrome.exe
```

OR

```
⚠️  Browsers installed globally at: C:\Users\...\AppData\Local\ms-playwright
   But virtual environment cannot access them.
```

#### Cause
Playwright browsers are either:
1. Not installed at all
2. Installed globally but the virtual environment can't access them (most common)
3. Installed in a different Python environment

#### Solution

**Option 1: Set Environment Variable (Quick Fix - Recommended)**

The server will automatically detect this issue and provide the exact command to run. If browsers are already installed globally:

Windows:
```bash
setx PLAYWRIGHT_BROWSERS_PATH "C:\Users\YourUsername\AppData\Local\ms-playwright"
```

Linux/Mac:
```bash
export PLAYWRIGHT_BROWSERS_PATH="$HOME/.cache/ms-playwright"
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

Then restart your terminal/IDE and try again.

**Option 2: Install Browsers in Virtual Environment**

```bash
# Activate your virtual environment first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install browsers
playwright install chromium
```

**Option 3: Skip Browser Validation (Development Only)**

For development environments where you don't need crawling functionality:

```bash
# In your .env file:
SKIP_BROWSER_VALIDATION=true
```

**⚠️ WARNING**: This option:
- Should ONLY be used in development/testing environments
- Disables all crawling tools (crawl_single_page, smart_crawl_url, etc.)
- RAG, knowledge graph, and other non-crawling tools will work normally
- Useful for CI/CD pipelines testing non-crawling functionality
- Useful for local development focusing on RAG/knowledge graph features

Do NOT use this in production or if you need any crawling functionality!

**Option 5: Use uv (if using uv for package management)**

```bash
uv run playwright install chromium
```

**Option 6: Docker (browsers pre-installed)**

```bash
docker-compose up --build
```

#### Verification

After applying the fix, test the server:
```bash
python run_mcp.py
```

You should see:
```
🔧 Validating Playwright browser installation...
✓ Browser validation passed
✓ Crawl4AI browser ready
```

---

### Dependency Conflicts

#### Symptom: Websockets deprecation warnings
```
DeprecationWarning: websockets 14.0 introduces breaking changes
```

#### Cause
The `websockets` library version 14.0+ introduces breaking changes that cause deprecation warnings.

#### Solution
1. Pin the websockets version in `pyproject.toml`:
```toml
[project.dependencies]
websockets = ">=13.0,<14.0"
```

2. Update dependencies:
```bash
uv pip install -e .
# OR if using pip
pip install -e . --upgrade
```

3. Verify the fix:
```bash
uv run python -c "import websockets; print(websockets.__version__)"
# Should show 13.x
```

---

### Docker Setup Problems

#### Symptom: Docker container fails to start
```
Error: crawl4ai-setup command not found
```

#### Cause
The Crawl4AI browser dependencies are not installed in the Docker image.

#### Solution
1. Ensure the Dockerfile includes:
```dockerfile
RUN uv pip install --system -e . && \
    crawl4ai-setup
```

2. Rebuild the Docker image:
```bash
# Using PowerShell script (Windows)
.\scripts\run_docker.ps1

# OR manually
docker build -t mcp-crawl4ai-rag .
docker run -p 8051:8051 --env-file .env.docker mcp-crawl4ai-rag
```

3. Verify container is running:
```bash
docker ps | grep mcp-crawl4ai-rag
```

---

### Neo4j Connection Failures

#### Symptom: "Neo4j connection not available" error
```json
{
  "success": false,
  "error": "Neo4j connection not available. Check Neo4j configuration in environment variables."
}
```

#### Cause
Incorrect Neo4j URI configuration for the current runtime mode.

#### Solution

**For Local/Stdio Mode (Claude Desktop):**
1. Edit `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
USE_KNOWLEDGE_GRAPH=true
```

**For Docker Mode:**
1. Edit `.env.docker`:
```env
# If Neo4j is on host machine:
NEO4J_URI=bolt://host.docker.internal:7687

# If Neo4j is in Docker Compose:
NEO4J_URI=bolt://neo4j:7687
```

2. Test the connection:
```bash
# Create test script
cat > test_neo4j.py << EOF
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as session:
    result = session.run("RETURN 1")
    print("✅ Neo4j connection successful!")
driver.close()
EOF

uv run python test_neo4j.py
```

---

### Python Version Issues

#### Symptom: Import errors or syntax errors
```
SyntaxError: invalid syntax
ImportError: cannot import name 'TypeAlias' from 'typing'
```

#### Cause
Python version < 3.10 doesn't support newer type hints.

#### Solution
1. Verify Python version:
```bash
python --version
# Should be Python 3.10 or higher
```

2. Install correct Python version:
```bash
# Using pyenv
pyenv install 3.12
pyenv local 3.12

# Using conda
conda create -n mcp-crawl4ai python=3.12
conda activate mcp-crawl4ai
```

3. Reinstall dependencies:
```bash
uv pip install -e .
```

---

### UV Installation Problems

#### Symptom: "uv: command not found"

#### Solution
1. Install UV:
```bash
# Using pip
pip install uv

# Using pipx (recommended)
pipx install uv

# On macOS
brew install uv

# On Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

2. Verify installation:
```bash
uv --version
```

---

## Runtime Issues

### Crawling Failures

#### Symptom: Timeout errors during crawling
```
TimeoutError: Page load timeout after 30 seconds
```

#### Solution
1. Increase timeout in crawl request:
```python
result = await crawl_website(
    url="https://example.com",
    timeout=60000,  # 60 seconds
    wait_for="networkidle"
)
```

2. Use stealth mode for bot detection issues:
```python
result = await crawl_website(
    url="https://example.com",
    stealth_mode=True,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)
```

3. Adjust concurrent crawls in `.env`:
```env
MAX_CONCURRENT_CRAWLS=5  # Reduce from default 15
```

---

### Memory Problems

#### Symptom: Out of memory errors during large crawls
```
MemoryError: Unable to allocate array
```

#### Solution
1. Reduce chunk size in `.env`:
```env
DEFAULT_CHUNK_SIZE=2000  # Reduce from 5000
```

2. Use selective extraction:
```python
result = await crawl_website(
    url="https://example.com",
    css_selector=".main-content",  # Only extract specific sections
    exclude_selectors=[".comments", ".sidebar"]
)
```

3. For Docker, increase memory limits:
```yaml
# docker-compose.yml
services:
  mcp-server:
    mem_limit: 4g
    memswap_limit: 4g
```

---

### Neo4j Query Timeouts

#### Symptom: Query timeout errors
```
Neo4jError: The transaction has been terminated
```

#### Solution
1. Increase Neo4j timeout settings:
```env
# In docker-compose.yml
environment:
  - NEO4J_dbms_transaction_timeout=30s
  - NEO4J_dbms_lock_acquisition_timeout=10s
```

2. Optimize queries with indexes:
```cypher
CREATE INDEX repo_name IF NOT EXISTS FOR (r:Repository) ON (r.name);
CREATE INDEX class_name IF NOT EXISTS FOR (c:Class) ON (c.name);
```

3. Use pagination for large results:
```python
MATCH (n:Node)
RETURN n
SKIP 0 LIMIT 100
```

---

### Supabase Connection Errors

#### Symptom: "Invalid API key" or connection refused
```
AuthError: Invalid API key
```

#### Solution
1. Verify Supabase credentials in `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...  # Full service key
```

2. Test connection:
```bash
curl -X GET "YOUR_SUPABASE_URL/rest/v1/" \
  -H "apikey: YOUR_SERVICE_KEY" \
  -H "Authorization: Bearer YOUR_SERVICE_KEY"
```

3. For local Supabase:
```env
SUPABASE_URL=http://localhost:8000
# Use local service key from docker logs
```

---

### Import Errors

#### Symptom: ModuleNotFoundError on server startup
```
ModuleNotFoundError: No module named 'utils'
```

#### Cause
Incorrect import paths after code refactoring.

#### Solution
1. Fix imports in `src/crawl4ai_mcp.py`:
```python
# Change from:
from utils import get_supabase_client

# To:
from .utils import get_supabase_client
```

2. Ensure PYTHONPATH is set correctly:
```bash
export PYTHONPATH=/path/to/project/src:$PYTHONPATH
```

3. For Docker, verify Dockerfile:
```dockerfile
ENV PYTHONPATH=/app/src:/app/knowledge_graphs:${PYTHONPATH}
```

---

### Azure OpenAI Rate Limits

#### Symptom: Rate limit errors during embedding generation or entity extraction
```
RateLimitError: Rate limit exceeded for gpt-4o-mini in organization
openai.error.RateLimitError: You exceeded your current quota
```

#### Cause
Azure OpenAI has rate limits based on your subscription tier (tokens per minute/requests per minute).

#### Solution

**1. Check your rate limits**:
- Go to Azure Portal → Your OpenAI resource → Quotas
- Note your TPM (tokens per minute) and RPM (requests per minute) limits

**2. Adjust concurrency in `.env`**:
```env
# For embedding generation
MAX_CONCURRENT_CRAWLS=3  # Reduce from default 15

# For entity extraction (GraphRAG)
# Edit in knowledge_graphs/document_entity_extractor.py
# Default: max_concurrent=3, reduce to 1-2 for lower tiers
```

**3. Add retry logic with exponential backoff**:
The server already implements this, but you can adjust:
```python
# In .env
MAX_RETRIES=5  # Increase retry attempts
RETRY_DELAY=2  # Initial delay in seconds
```

**4. Use batch processing for large operations**:
```python
# Instead of:
crawl_with_graph_extraction(large_site_url)

# Use memory-monitored crawling:
crawl_with_memory_monitoring(large_site_url, max_concurrent=2)
```

**5. Monitor usage**:
- Azure Portal → Your resource → Metrics
- Check "Total Tokens", "Processed PromptTokens", "Generated Tokens"

**Rate Limit Tiers** (as reference):
- **Free tier**: ~3 RPM, ~40,000 TPM
- **Standard**: ~60 RPM, ~240,000 TPM
- **Scale up**: Request quota increase in Azure Portal

**Prevention**:
```env
# Set conservative defaults
MAX_CONCURRENT_CRAWLS=5
USE_CONTEXTUAL_EMBEDDINGS=false  # Reduces embedding calls
USE_RERANKING=false  # Saves API calls for most queries
```

---

## Configuration Issues

### Environment Variable Problems

#### Symptom: "Missing required environment variables"

#### Solution
1. Check `.env` file exists:
```bash
ls -la .env
# If missing, copy from example:
cp .env.example .env
```

2. Verify required variables:
```bash
# Create verification script
cat > check_env.py << EOF
import os
from dotenv import load_dotenv

load_dotenv()

required = [
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY"
]

for var in required:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * 10}{value[-4:]}")
    else:
        print(f"❌ {var}: NOT SET")
EOF

uv run python check_env.py
```

---

### Transport Mode Configuration

#### Symptom: Server timeout in Claude Desktop (60 seconds)

#### Cause
Wrong transport mode configuration.

#### Solution

**For Claude Desktop (stdio mode):**
1. Edit `.env`:
```env
TRANSPORT=stdio
# No HOST or PORT needed
```

2. Update Claude Desktop config:
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "E:\\Repos\\GitHub\\mcp-crawl4ai-rag",
        "python",
        "run_mcp.py"
      ]
    }
  }
}
```

**For HTTP/Web clients (SSE mode):**
1. Edit `.env` or `.env.docker`:
```env
TRANSPORT=sse
HOST=0.0.0.0  # For Docker
PORT=8051
```

---

### RAG Strategy Conflicts

#### Symptom: Conflicting RAG features cause errors

#### Solution
1. Check compatible combinations in `.env`:
```env
# Safe combination 1: Basic RAG
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false

# Safe combination 2: Full RAG
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
```

2. Dependencies for advanced features:
```env
# Knowledge Graph requires Neo4j
USE_KNOWLEDGE_GRAPH=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# GraphRAG requires Knowledge Graph
USE_GRAPHRAG=true
USE_KNOWLEDGE_GRAPH=true
```

---

### Neo4j URI Configuration

#### Quick Reference Table

| Runtime Mode | Neo4j Location | NEO4J_URI |
|-------------|---------------|-----------|
| Local (stdio) | Host machine | `bolt://localhost:7687` |
| Docker | Host machine | `bolt://host.docker.internal:7687` |
| Docker | Docker Compose | `bolt://neo4j:7687` |
| Any | Cloud (AuraDB) | `neo4j+s://instance.databases.neo4j.io` |

---

### Docker Networking Issues

#### Symptom: Cannot connect to services from Docker

#### Solution
1. For services on host machine:
```env
# In .env.docker
NEO4J_URI=bolt://host.docker.internal:7687
SUPABASE_URL=http://host.docker.internal:8000
```

2. For Docker Compose services:
```yaml
# docker-compose.yml
services:
  mcp-server:
    networks:
      - mcp-network
  neo4j:
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

3. Test connectivity:
```bash
# From inside container
docker exec -it mcp-crawl4ai-rag sh
ping host.docker.internal
nc -zv host.docker.internal 7687
```

---

## Claude Desktop Integration

### Server Not Appearing

#### Symptom: MCP server not listed in Claude Desktop

#### Solution
1. Check config file location:
```bash
# Windows
%APPDATA%\Claude\claude_desktop_config.json

# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Linux
~/.config/Claude/claude_desktop_config.json
```

2. Verify config syntax:
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-crawl4ai-rag",
        "python",
        "run_mcp.py"
      ]
    }
  }
}
```

3. Restart Claude Desktop after changes

---

### Connection Timeouts

#### Symptom: "Server timed out after 60 seconds"

#### Solution
1. Switch to stdio transport in `.env`:
```env
TRANSPORT=stdio
```

2. Remove port from Claude Desktop config:
```json
{
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "/path/to/project",
    "python",
    "run_mcp.py"
  ]
  // No --port argument!
}
```

3. Test server manually:
```bash
cd /path/to/project
uv run python run_mcp.py
# Should see: "MCP server running in stdio mode"
```

---

### Stdio Protocol Violations

#### Symptom: "Unexpected token" or "not valid JSON" errors
```
Unexpected token 'c', "crawl4ai-setup" is not valid JSON
```

#### Cause
Non-JSON output to stdout breaks the stdio protocol.

#### Solution
1. Ensure all debug output goes to stderr:
```python
# In run_mcp.py or any startup script
import sys

def print_info(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Use print_info instead of print
print_info("Debug: Loading environment...")
```

2. Suppress warnings:
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Or via environment
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"
```

---

### Restarting Claude Desktop

#### When to Restart
- After changing `.env` configuration
- After modifying Claude Desktop config
- After fixing import errors
- When server appears stuck

#### How to Properly Restart
1. **Windows:**
   - Right-click system tray icon → Quit
   - Start from Start Menu

2. **macOS:**
   - Cmd+Q to quit
   - Reopen from Applications

3. **Linux:**
   - Close all windows
   - Kill process: `pkill -f claude`
   - Restart from launcher

4. **Verify restart worked:**
   - Open Developer Tools (Ctrl/Cmd+Shift+I)
   - Check Console for MCP server logs

---

## Development Issues

### Test Failures

#### Symptom: Tests fail with import errors

#### Solution
1. Ensure test environment is set up:
```bash
# Install test dependencies
uv pip install -e ".[dev]"

# Run tests with proper path
PYTHONPATH=src:knowledge_graphs uv run pytest
```

2. Fix common test issues:
```python
# In conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

---

### Coverage Reporting

#### Symptom: Low coverage or missing files

#### Solution
1. Run with coverage:
```bash
uv run pytest --cov=src --cov-report=html --cov-report=term-missing
```

2. Check coverage report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

3. Exclude test files from coverage:
```ini
# pytest.ini
[tool:pytest]
addopts = --cov-config=.coveragerc

# .coveragerc
[run]
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
```

---

### Pre-commit Hook Failures

#### Symptom: Git commit blocked by pre-commit hooks

#### Solution
1. Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

2. Fix specific issues:
```bash
# Auto-fix formatting
black src/
isort src/

# Check types
mypy src/

# Fix linting
ruff src/ --fix
```

3. Skip hooks temporarily (not recommended):
```bash
git commit --no-verify -m "Emergency fix"
```

---

### Linting Errors

#### Common issues and Fixes

```python
# F401: Unused import
# Remove unused imports or add to __all__
__all__ = ["function1", "function2"]

# E501: Line too long
# Break long lines
long_string = (
    "This is a very long string that would "
    "exceed the line length limit"
)

# W503: Line break before binary operator
# Move operator to end of previous line
result = (value1 +
          value2 +
          value3)
# Change to:
result = (value1 +
          value2 +
          value3)
```

---

### Type Checking Errors (mypy)

#### Common Type Errors and Solutions

**1. "error: Incompatible return value type"**

```python
# ❌ Problem
def get_user_name(user_id: int) -> str:
    user = db.get_user(user_id)
    return user  # Returns Optional[User], not str

# ✅ Solution
def get_user_name(user_id: int) -> Optional[str]:
    user = db.get_user(user_id)
    if user is None:
        return None
    return user.name
```

**2. "error: Argument has incompatible type"**

```python
# ❌ Problem
def process_items(items: List[str]) -> None:
    pass

process_items([1, 2, 3])  # Passing List[int]

# ✅ Solution 1: Fix the call
process_items(["1", "2", "3"])

# ✅ Solution 2: Make function generic
from typing import TypeVar, List
T = TypeVar('T')
def process_items(items: List[T]) -> None:
    pass
```

**3. "error: Missing type parameters"**

```python
# ❌ Problem
def get_data() -> dict:
    return {"key": "value"}

# ✅ Solution: Specify type parameters
from typing import Dict
def get_data() -> Dict[str, str]:
    return {"key": "value"}

# Or use newer syntax (Python 3.9+)
def get_data() -> dict[str, str]:
    return {"key": "value"}
```

**4. "error: Need type annotation"**

```python
# ❌ Problem
items = []  # mypy doesn't know the type

# ✅ Solution: Add type annotation
from typing import List
items: List[str] = []

# Or use assignment with type
items = []  # type: List[str]
```

**5. "error: Cannot determine type of"**

```python
# ❌ Problem
result = None
if condition:
    result = "value"
# mypy sees result as None or str

# ✅ Solution: Declare type upfront
result: Optional[str] = None
if condition:
    result = "value"
```

**6. Async function type issues**

```python
# ❌ Problem
async def fetch_data() -> str:
    return await get_data()  # Returns Coroutine

# ✅ Solution: Proper async type hints
from typing import Coroutine
async def fetch_data() -> str:
    data = await get_data()  # Await the coroutine
    return data

# For async generators
from typing import AsyncGenerator
async def stream_data() -> AsyncGenerator[str, None]:
    for item in items:
        yield item
```

**Configuration Tips**

Create or update `mypy.ini`:
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False  # Set True for strict typing
ignore_missing_imports = True

# Per-module overrides
[mypy-tests.*]
ignore_errors = True

[mypy-crawl4ai.*]
ignore_missing_imports = True
```

**Running mypy**

```bash
# Check all files
mypy src/

# Check specific file
mypy src/crawl4ai_mcp.py

# Ignore missing imports
mypy --ignore-missing-imports src/

# Show error codes
mypy --show-error-codes src/

# Generate HTML report
mypy --html-report mypy-report src/
```

**Quick Fixes for Project**

```bash
# Common issues in this project
# 1. Neo4j types
pip install types-neo4j

# 2. Supabase types (often need ignore)
# Add to mypy.ini:
[mypy-supabase.*]
ignore_missing_imports = True

# 3. Crawl4AI types
[mypy-crawl4ai.*]
ignore_missing_imports = True
```

**Suppressing specific errors** (use sparingly):

```python
# Ignore single line
result = some_function()  # type: ignore

# Ignore specific error code
result = some_function()  # type: ignore[return-value]

# Ignore entire function
def some_function() -> None:
    # type: ignore
    pass
```

---

## Debugging Tools & Techniques

### Log Locations

#### Application Logs
```bash
# Stdio mode (Claude Desktop)
# Logs appear in stderr, view in Claude Desktop Developer Tools

# Docker mode
docker logs mcp-crawl4ai-rag

# Neo4j logs
docker logs mcp-crawl4ai-neo4j

# File-based logs (if configured)
tail -f logs/mcp-server.log
```

---

### Verbose Mode Activation

#### Enable Debug Logging
1. In code:
```python
# src/logging_config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Via environment:
```env
LOG_LEVEL=DEBUG
PYTHONVERBOSE=1
```

3. For specific modules:
```python
import logging
logging.getLogger("crawl4ai").setLevel(logging.DEBUG)
logging.getLogger("neo4j").setLevel(logging.DEBUG)
```

---

### Component Testing

#### Test Neo4j Connection
```bash
# Quick test
uv run python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('✅ Neo4j connected')
driver.close()
"
```

#### Test Supabase Connection
```bash
# Quick test
uv run python -c "
from supabase import create_client
client = create_client('YOUR_URL', 'YOUR_KEY')
result = client.table('documents').select('id').limit(1).execute()
print('✅ Supabase connected')
"
```

#### Test OpenAI API
```bash
# Quick test
uv run python -c "
import openai
openai.api_key = 'YOUR_KEY'
response = openai.Model.list()
print('✅ OpenAI connected')
"
```

---

### Health Checks

#### Docker Health Check
```bash
# Check container health
docker inspect mcp-crawl4ai-rag --format='{{.State.Health.Status}}'

# Manual health check
curl http://localhost:8051/health
```

#### Create Health Check Endpoint
```python
# Add to src/crawl4ai_mcp.py
@app.route("/health")
async def health_check():
    checks = {
        "server": "ok",
        "neo4j": check_neo4j(),
        "supabase": check_supabase(),
        "openai": check_openai()
    }

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503

    return JSONResponse(checks, status_code=status_code)
```

---

### Manual Connection Testing

#### Complete Test Script
```python
#!/usr/bin/env python
"""
Comprehensive connection test script.
Save as test_connections.py
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment
load_dotenv()

def test_neo4j():
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"✅ Neo4j: Connected ({count} nodes)")
        driver.close()
        return True
    except Exception as e:
        print(f"❌ Neo4j: {e}")
        return False

def test_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not key:
            print("❌ Supabase: Missing credentials")
            return False

        client = create_client(url, key)
        result = client.table("documents").select("id").limit(1).execute()
        print(f"✅ Supabase: Connected")
        return True
    except Exception as e:
        print(f"❌ Supabase: {e}")
        return False

def test_openai():
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            print("❌ OpenAI: Missing API key")
            return False

        openai.api_key = api_key
        models = openai.Model.list()
        print(f"✅ OpenAI: Connected")
        return True
    except Exception as e:
        print(f"❌ OpenAI: {e}")
        return False

def test_crawl4ai():
    try:
        from crawl4ai import AsyncWebCrawler
        print("✅ Crawl4AI: Module loaded")
        return True
    except Exception as e:
        print(f"❌ Crawl4AI: {e}")
        return False

def main():
    print("Testing all connections...\n")

    results = {
        "Neo4j": test_neo4j(),
        "Supabase": test_supabase(),
        "OpenAI": test_openai(),
        "Crawl4AI": test_crawl4ai(),
    }

    print("\n" + "="*50)
    print("Summary:")
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {service}")

    if all(results.values()):
        print("\n✨ All connections successful!")
        sys.exit(0)
    else:
        print("\n⚠️  Some connections failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Run with:
```bash
uv run python test_connections.py
```

---

## Common Error Messages & Solutions

This section provides quick solutions for specific error messages you might encounter.

### "JSON parsing error" - Stdout Contamination

#### Full Error Message
```
Unexpected token 'c', "crawl4ai-setup" is not valid JSON
JSON.parse: unexpected character at line 1 column 1
Error: Failed to parse JSON from server
```

#### Cause
The MCP stdio protocol requires that **only valid JSON** is written to stdout. Any other output (print statements, warnings, setup messages) breaks the protocol and Claude Desktop cannot parse responses.

#### Solution

**1. Redirect all debug output to stderr**:
```python
# In run_mcp.py and any startup scripts
import sys

def debug_print(*args, **kwargs):
    """Print debug messages to stderr to avoid contaminating stdout"""
    print(*args, file=sys.stderr, **kwargs)

# Use debug_print instead of print
debug_print("Loading environment variables...")
debug_print(f"Neo4j URI: {neo4j_uri}")
```

**2. Suppress warnings**:
```python
# At the top of run_mcp.py
import warnings
import os

# Suppress all warnings
warnings.filterwarnings("ignore")

# Or via environment variable
os.environ["PYTHONWARNINGS"] = "ignore"
```

**3. Capture Crawl4AI setup output**:
```python
import subprocess
import sys

# Run setup silently
result = subprocess.run(
    ["crawl4ai-setup"],
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print(f"Setup failed: {result.stderr}", file=sys.stderr)
```

**4. Verify clean stdout**:
```bash
# Test your server
cd /path/to/project
uv run python run_mcp.py 2>/dev/null | head -1

# Should output valid JSON or nothing (if waiting for input)
# Should NOT output: "crawl4ai-setup", "Loading...", etc.
```

**Prevention**:
- Never use `print()` for logging in stdio mode - use logging module
- Configure logging to write to stderr or file:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # ← stderr, not stdout
        logging.FileHandler('mcp-server.log')
    ]
)
```

---

### "ValidationError: source vs source_filter" - Parameter Mismatch

#### Full Error Message
```
ValidationError: 1 validation error for perform_rag_query
source_filter
  Field required [type=missing, input_value={'query': '...', 'source': '...'}, input_types={'query': 'str', 'source': 'str'}]

OR

ValidationError: Extra inputs are not permitted [type=extra_forbidden, input_value={'query': '...', 'source': '...'}]
```

#### Cause
The `perform_rag_query` tool parameter was renamed from `source` to `source_filter` in v1.1.1 for clarity, but old code or cached requests are using the old parameter name.

#### Solution

**1. Update tool calls to use `source_filter`**:
```python
# ❌ Old (will fail)
perform_rag_query(query="FastAPI routing", source="docs.fastapi.com")

# ✅ New (correct)
perform_rag_query(query="FastAPI routing", source_filter="docs.fastapi.com")
```

**2. Check API Reference**:
```bash
# View current parameter names
cat docs/API_REFERENCE.md | grep -A 10 "perform_rag_query"
```

**3. Clear Claude Desktop cache** (if using Claude):
- Quit Claude Desktop completely
- Delete cache (optional):
  - Windows: `%LOCALAPPDATA%\Claude\Cache`
  - macOS: `~/Library/Caches/Claude`
- Restart Claude Desktop

**4. Verify with test**:
```python
# Test script
from src.crawl4ai_mcp import mcp

# This should work
result = mcp.call_tool(
    "perform_rag_query",
    {
        "query": "test query",
        "source_filter": "example.com",  # ← correct parameter name
        "match_count": 5
    }
)
print(result)
```

**Current Parameter Names** (v1.2.0+):
- `perform_rag_query`: Uses `source_filter` (optional)
- `search_code_examples`: Uses `source_id` (optional)
- `graphrag_query`: Uses `source_filter` (optional)

---

### "Neo4j connection failed" - Configuration Issues

#### Full Error Messages
```
Failed to connect to Neo4j at bolt://localhost:7687
ServiceUnavailable: Unable to retrieve routing information
AuthError: The client is unauthorized due to authentication failure
```

#### Cause
Neo4j service not running, incorrect credentials, or wrong URI format.

#### Solution

**1. Check Neo4j is running**:
```bash
# Docker
docker ps | grep neo4j

# Should see something like:
# 5a3d4b7c8e9f   neo4j:latest   "Up 10 minutes"   0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp

# If not running:
docker-compose up -d neo4j
# OR
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

**2. Verify connection from command line**:
```bash
# Using cypher-shell
cypher-shell -a bolt://localhost:7687 -u neo4j -p your_password "RETURN 1"

# Should output: 1

# Using Python
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('✅ Connected')
driver.close()
"
```

**3. Check URI format**:
```env
# ✅ Correct formats
NEO4J_URI=bolt://localhost:7687
NEO4J_URI=bolt://host.docker.internal:7687  # From Docker to host
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io  # AuraDB cloud

# ❌ Wrong formats
NEO4J_URI=http://localhost:7687  # Wrong protocol
NEO4J_URI=localhost:7687  # Missing protocol
NEO4J_URI=bolt://neo4j:7687  # Won't work for local unless in Docker network
```

**4. Reset password if forgotten**:
```bash
# Stop Neo4j
docker stop neo4j

# Start with auth disabled
docker run --rm -it \
  -v neo4j_data:/data \
  -e NEO4J_AUTH=none \
  neo4j:latest \
  neo4j-admin set-initial-password new_password

# Restart normally
docker start neo4j
```

**5. Check firewall/network**:
```bash
# Test if port is open
nc -zv localhost 7687
telnet localhost 7687

# Should connect without "Connection refused"
```

**Common URI patterns by environment**:
| Environment | Neo4j Location | URI |
|------------|----------------|-----|
| Local dev | Host machine | `bolt://localhost:7687` |
| MCP in Docker | Host Neo4j | `bolt://host.docker.internal:7687` |
| Docker Compose | Neo4j in compose | `bolt://neo4j:7687` |
| Cloud (AuraDB) | Neo4j Cloud | `neo4j+s://xxxxx.databases.neo4j.io` |

---

### "Failed to generate embeddings" - Azure OpenAI Issues

#### Full Error Messages
```
Error: Failed to generate embeddings for content
openai.error.AuthenticationError: Incorrect API key provided
openai.error.InvalidRequestError: The API deployment for this resource does not exist
```

#### Root Causes & Solutions

**1. Missing or incorrect API key**:
```bash
# Check if key is set
echo $AZURE_OPENAI_API_KEY

# Should output a long string starting with letters/numbers
# If empty, set in .env:
AZURE_OPENAI_API_KEY=your_actual_key_here
```

**2. Wrong deployment name**:
```env
# ❌ Wrong - using model name
DEPLOYMENT=text-embedding-3-small

# ✅ Correct - using your deployment name from Azure Portal
DEPLOYMENT=my-embedding-deployment
```

**How to find your deployment name**:
1. Go to Azure Portal → Your Azure OpenAI resource
2. Navigate to "Deployments" or "Model deployments"
3. Find your embedding model deployment
4. Copy the **Deployment name** column (not Model name)

**3. Wrong endpoint**:
```env
# ✅ Correct format
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/

# ❌ Wrong - missing trailing slash
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com

# ❌ Wrong - using API endpoint instead
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/openai/deployments/...
```

**4. Embedding model not deployed**:
- Solution: Deploy `text-embedding-3-small` or `text-embedding-ada-002` in Azure Portal
- Update `DEPLOYMENT` in `.env` with the deployment name

**5. Rate limiting** (see Azure OpenAI Rate Limits section above)

**6. Regional availability**:
- Not all models available in all regions
- Check: [Azure OpenAI Model Availability](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability)

**Test embeddings directly**:
```python
# test_embeddings.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-10-01-preview"
)

response = client.embeddings.create(
    input="test",
    model=os.getenv("DEPLOYMENT", "text-embedding-3-small")
)

print(f"✅ Embedding generated: {len(response.data[0].embedding)} dimensions")
```

---

## Quick Fixes Reference

### Most Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Server timeout (60s) | Set `TRANSPORT=stdio` in `.env` |
| Neo4j connection failed | Use `bolt://localhost:7687` for local |
| Import error | Change `from utils` to `from .utils` |
| Websockets warning | Pin to version 13.x in dependencies |
| Stdio protocol violation | Redirect prints to stderr |
| Server not in Claude | Restart Claude Desktop |
| Docker can't connect | Use `host.docker.internal` |
| Missing env vars | Copy `.env.example` to `.env` |
| JSON parsing error | Check stdout contamination, use stderr for logs |
| Azure OpenAI rate limit | Reduce `MAX_CONCURRENT_CRAWLS` in `.env` |
| ValidationError: source | Use `source_filter` parameter instead |
| Failed to generate embeddings | Check `DEPLOYMENT` name in Azure Portal |
| Type checking errors (mypy) | Add type annotations, install types packages |

---

## Getting Help

If you're still experiencing issues:

1. **Check the logs** - Most errors include helpful messages
2. **Run the test script** - Use `test_connections.py` above
3. **Search existing issues** - GitHub Issues may have solutions
4. **Ask for help** - Include:
   - Error message
   - Your `.env` configuration (without secrets)
   - Output from `test_connections.py`
   - Steps to reproduce

---

## Additional Quick Fixes

### GraphRAG Not Enabled
**Symptom**: GraphRAG tools not available or "GraphRAG functionality is disabled"
**Solution**:
```env
# In .env file
USE_GRAPHRAG=true
NEO4J_URI=bolt://localhost:7687
OPENAI_API_KEY=sk-...
```
Restart the MCP server after changes.

### Entity Extraction Failing
**Symptom**: "Entity extraction failed" during graph crawling
**Common Causes**:
1. Missing OpenAI API key
2. Rate limiting (reduce concurrent extraction)
3. Content too short for entity extraction

**Solution**:
```python
# Check API key is set
echo $OPENAI_API_KEY

# For rate limiting, use slower extraction:
crawl_with_graph_extraction(url, chunk_size=3000)  # Smaller chunks
```

### Batch Processing Timeouts
**Symptom**: Timeout errors when processing multiple URLs or repositories
**Solution**:
```python
# Reduce concurrency
parse_github_repositories_batch(repos, max_concurrent=2, max_retries=3)

# Or process sequentially
crawl_with_multi_url_config(urls, max_concurrent=1)
```

### Foreign Key Constraint Violations
**Symptom**: "violates foreign key constraint" errors during crawling
**This should not occur in v1.1.1+** (fixed)
**If you see this**:
1. Update to latest version: `git pull && uv pip install -e .`
2. Verify version: Check CHANGELOG.md for v1.1.1 fixes
3. Report as bug if persists

---

## Performance Optimization Tips

### Crawling Performance
1. **Adjust concurrency based on site**:
   - Documentation sites: `max_concurrent=10`
   - Dynamic sites: `max_concurrent=5`
   - Protected sites (stealth): `max_concurrent=3`

2. **Use appropriate chunk sizes**:
   - Technical docs: `chunk_size=5000`
   - News/articles: `chunk_size=3000`
   - Code-heavy: `chunk_size=7000`

3. **Enable memory monitoring for large crawls**:
   ```python
   crawl_with_memory_monitoring(url, memory_threshold_mb=400)
   ```

### RAG Query Performance
1. **Disable graph enrichment for simple queries**:
   ```python
   graphrag_query("What is FastAPI?", use_graph_enrichment=False)
   ```

2. **Use source filtering to reduce search space**:
   ```python
   perform_rag_query(query, source="docs.python.org", match_count=5)
   ```

3. **Toggle reranking based on needs**:
   ```env
   USE_RERANKING=true   # Better accuracy, slower
   USE_RERANKING=false  # Faster, adequate for most queries
   ```

---

## Related Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Initial setup
- [Dual Mode Setup](docs/DUAL_MODE_SETUP.md) - Running both stdio and HTTP
- [Docker Setup](docs/DOCKER_SETUP.md) - Docker deployment and Neo4j configuration
- [GraphRAG Guide](docs/GRAPHRAG_GUIDE.md) - Graph-augmented RAG documentation
- [New Features Guide](docs/NEW_FEATURES_GUIDE.md) - v1.1.0 features (stealth mode, memory monitoring)
- [Architecture Documentation](docs/ARCHITECTURE.md) - System design and component relationships
- [Code Quality Guide](docs/CODE_QUALITY_IMPROVEMENTS.md) - Development best practices
- [Historical Fixes](../archive/ALL_FIXES_COMPLETE.md) - Archived troubleshooting reference
