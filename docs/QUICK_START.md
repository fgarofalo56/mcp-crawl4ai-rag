# ⚡ Quick start guide - using new utilities

> **🏠 [Home](../README.md)** | **📖 [Documentation](README.md)** | **👤 Quick start**

---

This guide shows you how to immediately start using the new utility modules in your code.

## 🚀 Quick examples

### 1. Configuration

```python
from src.config import crawl_config, database_config, get_required_env

# Use configuration constants
chunk_size = crawl_config.DEFAULT_CHUNK_SIZE  # 5000
max_concurrent = crawl_config.MAX_CONCURRENT_BROWSERS  # 10
batch_size = database_config.SUPABASE_BATCH_SIZE  # 20

# Get required environment variables (raises error if missing)
api_key = get_required_env("OPENAI_API_KEY")
```

### 2. Logging

```python
from src.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Starting operation")
logger.warning("This might be a problem")
logger.error("Something went wrong", exc_info=True)
logger.debug("Detailed debug information")
```

### 3. Error Handling

```python
from src.error_handlers import (
    create_error_response,
    create_success_response,
    retry_with_backoff,
    ValidationError
)

# Standardized JSON responses
def my_mcp_tool():
    try:
        result = process_data()
        return create_success_response({"result": result})
    except Exception as e:
        return create_error_response(str(e), error_type="processing_error")

# Retry decorator
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def database_operation():
    return db.execute_query()
```

### 4. Environment Validation

```python
from src.env_validators import (
    load_environment,
    validate_environment,
    get_env_int,
    get_env_bool
)

# Load .env file (automatically finds it)
load_environment()

# Validate all required variables
is_valid, results = validate_environment(raise_on_error=True)

# Get typed environment variables
port = get_env_int("PORT", default=8051, min_val=1000, max_val=65535)
debug_mode = get_env_bool("DEBUG", default=False)
timeout = get_env_float("TIMEOUT", default=30.0)
```

### 5. Input Validation

```python
from src.validators import InputValidator, validate_mcp_tool_input
from src.error_handlers import ValidationError, create_error_response

# Individual validators
validator = InputValidator()

@mcp.tool()
async def crawl_url(ctx: Context, url: str, depth: int, chunk_size: int):
    try:
        # Validate all inputs at once
        validated = validate_mcp_tool_input(
            url=url,
            depth=depth,
            chunk_size=chunk_size
        )

        # Use validated inputs
        result = await crawl(
            validated['url'],
            validated['depth'],
            validated['chunk_size']
        )

        return create_success_response({"result": result})

    except ValidationError as e:
        return create_error_response(str(e), error_type="validation_error")
```

### 6. Complete MCP Tool Example

```python
from src.config import crawl_config
from src.logging_config import get_logger
from src.error_handlers import (
    create_error_response,
    create_success_response,
    retry_with_backoff,
    ValidationError
)
from src.validators import validate_mcp_tool_input

logger = get_logger(__name__)

@mcp.tool()
async def smart_crawl(
    ctx: Context,
    url: str,
    max_depth: int = 3,
    chunk_size: int = 5000,
    max_concurrent: int = 10
) -> str:
    """
    Smart crawl with validation, logging, and error handling.

    Args:
        ctx: MCP context
        url: URL to crawl
        max_depth: Maximum crawl depth (1-10)
        chunk_size: Content chunk size (100-50000)
        max_concurrent: Max concurrent operations (1-50)

    Returns:
        JSON response with crawl results or error
    """
    try:
        # Validate inputs
        validated = validate_mcp_tool_input(
            url=url,
            depth=max_depth,
            chunk_size=chunk_size,
            concurrent_limit=max_concurrent
        )

        logger.info(f"Starting crawl of {validated['url']} with depth {validated['depth']}")

        # Use configuration defaults if not specified
        chunk_size = validated.get('chunk_size', crawl_config.DEFAULT_CHUNK_SIZE)

        # Perform crawl with retry
        @retry_with_backoff(max_retries=3)
        async def do_crawl():
            return await crawler.crawl(
                url=validated['url'],
                depth=validated['depth'],
                chunk_size=chunk_size
            )

        result = await do_crawl()

        logger.info(f"Crawl completed successfully: {len(result)} pages")

        return create_success_response({
            "pages_crawled": len(result),
            "url": validated['url'],
            "depth": validated['depth']
        })

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return create_error_response(str(e), error_type="validation_error")

    except Exception as e:
        logger.error(f"Crawl failed: {e}", exc_info=True)
        return create_error_response(str(e), error_type="crawl_error")
```

## 🔧 Setup

### 1. Install Dependencies

```bash
# Sync dependencies
uv sync

# Install dev dependencies
uv pip install pytest pytest-cov pytest-asyncio
```

### 2. Configure Environment

```bash
# Copy example
cp .env.example .env

# Edit .env with your values
# Required:
#   OPENAI_API_KEY
#   SUPABASE_URL
#   SUPABASE_SERVICE_KEY
```

### 3. Validate Setup

```python
from src.env_validators import load_environment, validate_environment, get_validation_summary

# Load environment
load_environment()

# Validate
is_valid, results = validate_environment(raise_on_error=False)

# Print summary
print(get_validation_summary())
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_validators.py -v

# Watch mode (requires pytest-watch)
ptw tests/
```

### Writing Tests

```python
import pytest
from src.validators import InputValidator
from src.error_handlers import ValidationError

def test_url_validation():
    """Test URL validation."""
    validator = InputValidator()

    # Valid URL
    url = validator.validate_url_input("https://example.com")
    assert url == "https://example.com"

    # Invalid URL
    with pytest.raises(ValidationError):
        validator.validate_url_input("not-a-url")
```

## 📊 Monitoring and Debugging

### View Logs

```bash
# Real-time log viewing
tail -f logs/crawl4ai_mcp.log

# Search logs
grep "ERROR" logs/crawl4ai_mcp.log

# View with timestamps
cat logs/crawl4ai_mcp.log | grep "2025-10-02"
```

### Debug Mode

```python
import logging
from src.logging_config import setup_logging

# Set debug level
logger = setup_logging(name="my_app", level="DEBUG")

# Now all debug messages will be logged
logger.debug("This will be logged")
```

### Configuration Check

```python
from src.config import get_config_summary

# Get current configuration
config = get_config_summary()
print(json.dumps(config, indent=2))
```

## 🎯 Best Practices

### 1. Always Validate Inputs

```python
# ✅ Good
@mcp.tool()
async def my_tool(ctx: Context, url: str):
    validated = validate_mcp_tool_input(url=url)
    return await process(validated['url'])

# ❌ Bad
@mcp.tool()
async def my_tool(ctx: Context, url: str):
    return await process(url)  # No validation!
```

### 2. Use Configuration Constants

```python
# ✅ Good
from src.config import crawl_config
chunk_size = crawl_config.DEFAULT_CHUNK_SIZE

# ❌ Bad
chunk_size = 5000  # Magic number
```

### 3. Log Appropriately

```python
# ✅ Good - Different levels for different situations
logger.debug("Processing item 5 of 100")
logger.info("Starting batch processing")
logger.warning("Retry attempt 2 of 3")
logger.error("Failed to connect", exc_info=True)

# ❌ Bad - Wrong levels
logger.info("Processing every single item...")  # Too verbose
logger.error("Item not found")  # Not an error, just info
```

### 4. Handle Errors Properly

```python
# ✅ Good
try:
    result = risky_operation()
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return create_error_response(str(e), error_type="validation_error")
except DatabaseError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    return create_error_response(str(e), error_type="database_error")

# ❌ Bad
try:
    result = risky_operation()
except Exception as e:
    return {"error": str(e)}  # Too generic, no logging
```

### 5. Use Retry Decorator

```python
# ✅ Good
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def api_call():
    return external_api.fetch_data()

# ❌ Bad
def api_call():
    for i in range(3):
        try:
            return external_api.fetch_data()
        except:
            time.sleep(2 ** i)
```

## 🔍 Troubleshooting

### Import Errors

```python
# If you get import errors, ensure src is in path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Environment Variable Issues

```python
from src.env_validators import get_validation_summary

# Print detailed validation results
print(get_validation_summary())
```

### Test Failures

```bash
# Run with verbose output
pytest tests/ -vv

# Run with print statements
pytest tests/ -s

# Run specific failing test
pytest tests/test_validators.py::test_name -vv
```

## 📚 More Information

- See [CODE_QUALITY_IMPROVEMENTS.md](CODE_QUALITY_IMPROVEMENTS.md) for full details
- Check [README.md](README.md) for project overview
- View tests in `tests/` directory for more examples

## 🎉 You're Ready!

Start using these utilities in your code to improve:
- ✅ Code quality
- ✅ Error handling
- ✅ Maintainability
- ✅ Debugging experience
- ✅ Testing coverage
