# Contributing to Crawl4AI RAG MCP Server

Thank you for your interest in contributing to the Crawl4AI RAG MCP Server! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

### Our Pledge

We are committed to providing a friendly, safe, and welcoming environment for all contributors, regardless of experience level, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, nationality, or other similar characteristics.

### Expected Behavior

- Be respectful and inclusive in your language and actions
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members
- Be collaborative and helpful

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Public or private harassment
- Publishing others' private information without permission
- Any conduct that could reasonably be considered inappropriate in a professional setting

## Getting Started

### Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
   cd mcp-crawl4ai-rag
   ```

2. **Install uv (recommended package manager)**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Create virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   uv pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

Follow the code style guidelines and ensure your changes are well-tested.

### 3. Write Tests

Add tests for any new functionality:
```bash
# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### 4. Format and Lint Your Code

```bash
# Format with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

### 5. Commit Your Changes

Follow the commit message conventions (see below).

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guide

### Python Style

We use Python 3.12+ and follow these conventions:

1. **Formatting**: Use `black` with 100-character line length
   ```bash
   black --line-length 100 src/ tests/
   ```

2. **Linting**: Use `ruff` for linting
   ```bash
   ruff check src/ tests/
   ```

3. **Type Hints**: Use type hints for all function signatures
   ```python
   def process_url(url: str, max_depth: int = 3) -> Dict[str, Any]:
       """Process a URL and return results."""
       ...
   ```

4. **Docstrings**: Use Google-style docstrings
   ```python
   def crawl_page(url: str, config: CrawlerConfig) -> CrawlResult:
       """
       Crawl a single web page.

       Args:
           url: The URL to crawl
           config: Crawler configuration settings

       Returns:
           CrawlResult containing the page content and metadata

       Raises:
           CrawlError: If the page cannot be crawled
       """
   ```

5. **Async/Await**: Prefer async functions for I/O operations
   ```python
   async def fetch_content(url: str) -> str:
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return await response.text()
   ```

### Import Organization

Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local imports

```python
# Standard library
import asyncio
import json
from typing import Dict, List, Any

# Third-party
from fastmcp import FastMCP
from crawl4ai import AsyncWebCrawler
import requests

# Local
from .utils import process_markdown
from .config import settings
```

## CI/CD Pipeline

All pull requests are automatically checked by our CI/CD pipeline. See [docs/CI_CD.md](docs/CI_CD.md) for detailed documentation.

### Automated Workflows

When you submit a PR, these workflows run automatically:

1. **Tests** (~10-15 min): Runs pytest on Python 3.10, 3.11, 3.12 across Ubuntu, Windows, macOS
2. **Lint** (~2-3 min): Checks Black formatting, Ruff linting, mypy type checking
3. **Docker Build** (~15-20 min): Builds and tests Docker image

All workflows must pass before your PR can be merged.

### Running CI Locally

Use [act](https://github.com/nektos/act) to run workflows locally:

```bash
# Install act
brew install act  # macOS/Linux

# Run test workflow
act -j test

# Run lint workflow
act -j lint
```

## Testing Requirements

### Test Coverage

We aim for **80% code coverage**. New features should include comprehensive tests.

### Test Structure

```python
# tests/test_feature.py
import pytest
from src.crawl4ai_mcp import your_function

class TestYourFeature:
    """Test suite for YourFeature."""

    async def test_normal_operation(self):
        """Test normal operation of the feature."""
        result = await your_function("input")
        assert result.success is True

    async def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ExpectedError):
            await your_function("invalid_input")

    @pytest.mark.parametrize("input,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    async def test_multiple_cases(self, input, expected):
        """Test multiple input cases."""
        result = await your_function(input)
        assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_crawling.py

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run with verbose output
pytest tests/ -v

# Run only marked tests
pytest tests/ -m "not slow"
```

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `pytest tests/`
2. **Check code formatting**: `black --check src/ tests/`
3. **Run linting**: `ruff check src/ tests/`
4. **Update documentation** if needed
5. **Add an entry to CHANGELOG.md** under "Unreleased"

### PR Guidelines

1. **Title**: Use a clear, descriptive title
   - ✅ "Add memory monitoring to crawl operations"
   - ❌ "Fix bug"

2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Related issues (use "Fixes #123" to auto-close issues)

3. **Size**: Keep PRs focused and reasonably sized
   - Prefer multiple small PRs over one large PR
   - Aim for < 500 lines of code changes

4. **Documentation**: Update relevant documentation
   - README.md for user-facing changes
   - API_REFERENCE.md for new/modified tools
   - Inline comments for complex logic

### Review Process

1. **Automated checks** must pass (tests, linting)
2. **Code review** by at least one maintainer
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Merge** once approved

## Issue Reporting Guidelines

### Bug Reports

When reporting bugs, include:

1. **Environment information**:
   ```
   - OS: [e.g., Ubuntu 22.04, Windows 11, macOS 14]
   - Python version: [e.g., 3.12.1]
   - Package versions: [run `uv pip list`]
   ```

2. **Steps to reproduce**:
   ```python
   # Minimal code example that reproduces the issue
   from crawl4ai_mcp import crawl_single_page
   result = await crawl_single_page(ctx, "https://example.com")
   ```

3. **Expected behavior**: What should happen

4. **Actual behavior**: What actually happens

5. **Error messages**: Full traceback if applicable

### Feature Requests

For feature requests, provide:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: How you envision the feature working
3. **Alternatives considered**: Other approaches you've thought about
4. **Additional context**: Any other relevant information

## Commit Message Conventions

We follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```bash
# Feature
git commit -m "feat(crawling): add stealth mode for bypassing bot detection"

# Bug fix
git commit -m "fix(rag): resolve memory leak in vector search"

# Documentation
git commit -m "docs(api): update tool descriptions in API reference"

# With body
git commit -m "feat(crawling): add memory monitoring support

Implements real-time memory tracking during crawl operations
using psutil. Automatically throttles concurrency when memory
threshold is exceeded.

Closes #45"
```

## Development Tips

### Local Testing with MCP

Test your changes with the MCP server locally:

```python
# run_test_server.py
import asyncio
from src.crawl4ai_mcp import mcp

async def test_server():
    # Set test environment variables
    os.environ["TRANSPORT"] = "stdio"
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(test_server())
```

### Debugging

1. **Enable verbose logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use debugger**:
   ```python
   import pdb; pdb.set_trace()
   # or with ipdb for better experience
   import ipdb; ipdb.set_trace()
   ```

3. **Test with Claude Desktop**:
   - Install your development version
   - Check logs at: `~/Library/Logs/Claude/` (macOS)

### Performance Profiling

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # Your code here
    result = expensive_operation()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release date
3. Create git tag: `git tag v1.2.0`
4. Push tag: `git push origin v1.2.0`
5. GitHub Actions will handle the rest

## Getting Help

- **Discord**: Join our community for discussions
- **GitHub Issues**: For bugs and feature requests
- **Documentation**: Check `/docs` folder
- **Examples**: See `/examples` for usage examples

## Recognition

Contributors are recognized in:
- CHANGELOG.md (for significant contributions)
- GitHub contributors page
- Project documentation

Thank you for contributing to Crawl4AI RAG MCP Server! 🚀