# CI/CD Workflow Quick Reference

Quick reference guide for developers working with the CI/CD pipeline.

## Quick Commands

### Local Development

```bash
# Setup
git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
cd mcp-crawl4ai-rag
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests
pytest -v --cov=src --cov-report=term-missing

# Code quality
black src/ tests/ knowledge_graphs/
ruff check src/ tests/ knowledge_graphs/ --fix
mypy src/ --config-file pyproject.toml

# Quick test (no slow tests)
pytest -m "not slow" -v
```

### Docker Testing

```bash
# Build
docker build -t mcp/crawl4ai-rag:test --build-arg PORT=8051 .

# Test run
docker run -d --env-file .env -p 8051:8051 --name test-mcp mcp/crawl4ai-rag:test

# Check logs
docker logs test-mcp

# Cleanup
docker stop test-mcp && docker rm test-mcp
```

### Local CI Simulation

```bash
# Install act
brew install act  # macOS
# or: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflows
act -j test          # Test workflow
act -j lint          # Lint workflow
act -j build         # Docker build
```

## Workflow Status

| Workflow | Trigger | Duration | Purpose |
|----------|---------|----------|---------|
| Tests | Push/PR | ~10-15min | Run pytest across Python versions |
| Lint | Push/PR | ~2-3min | Check code quality |
| Docker | Push/PR | ~15-20min | Build and test container |
| Release | Tag push | ~5min | Create GitHub release |

## Branch Protection Rules

### Main Branch

- Require PR reviews (1 approver)
- Require status checks to pass:
  - Tests (Python 3.10, 3.11, 3.12)
  - Lint
  - Docker Build
- No force pushes
- No deletions

### Develop Branch

- Same as main branch
- Integration testing ground

## PR Checklist

Before submitting:

- [ ] Tests pass locally: `pytest -v`
- [ ] Code formatted: `black --check src/`
- [ ] Linting clean: `ruff check src/`
- [ ] Coverage maintained/improved
- [ ] Documentation updated
- [ ] Conventional commits used
- [ ] Branch up to date with main

## Test Markers

```bash
# Unit tests only
pytest -m "unit" -v

# Integration tests only
pytest -m "integration" -v

# Skip slow tests
pytest -m "not slow" -v

# Async tests only
pytest -m "async" -v
```

## Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| Overall | 29% | 80% |
| Core (src/crawl4ai_mcp.py) | TBD | 85% |
| Utils | TBD | 90% |
| Config | 90%+ | 95% |

## Common CI Failures

### 1. Black formatting
```bash
# Fix
black src/ tests/ knowledge_graphs/
git add . && git commit -m "style: format with black"
```

### 2. Ruff linting
```bash
# Check what will change
ruff check src/ --diff

# Auto-fix
ruff check src/ --fix

# Commit
git add . && git commit -m "style: fix linting issues"
```

### 3. Test failures
```bash
# Run failing test with verbose output
pytest tests/test_failing.py -v -s

# Debug with breakpoint
# Add: import pdb; pdb.set_trace() in code
pytest tests/test_failing.py -s
```

### 4. Import errors
```bash
# Reinstall dependencies
uv pip install -e ".[dev]"

# Check imports
python -c "from src.crawl4ai_mcp import mcp"
```

### 5. Coverage below threshold
```bash
# See what's not covered
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Add tests for uncovered lines
```

## Environment Variables for CI

Tests use these mock values:

```bash
OPENAI_API_KEY=test-key-for-ci
SUPABASE_URL=https://test.supabase.co
SUPABASE_SERVICE_KEY=test-key
USE_KNOWLEDGE_GRAPH=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=test
```

## Docker Image Tags

Images are automatically tagged based on trigger:

```bash
# Branch push
ghcr.io/coleam00/mcp-crawl4ai-rag:main
ghcr.io/coleam00/mcp-crawl4ai-rag:develop

# Version tag
ghcr.io/coleam00/mcp-crawl4ai-rag:v1.0.0
ghcr.io/coleam00/mcp-crawl4ai-rag:1.0

# Latest (main only)
ghcr.io/coleam00/mcp-crawl4ai-rag:latest

# Pull image
docker pull ghcr.io/coleam00/mcp-crawl4ai-rag:latest
```

## Dependabot

Automated updates every Monday at 9 AM:

- **GitHub Actions**: Action version updates
- **Python packages**: Grouped by category
- **Docker**: Base image updates

Review and merge Dependabot PRs weekly.

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit: `git commit -m "chore: bump version to v1.2.0"`
4. Tag: `git tag v1.2.0`
5. Push: `git push origin v1.2.0`
6. GitHub Actions creates release automatically

## Secrets Required

Only for public features:

- `CODECOV_TOKEN`: Optional for public repos
- `GITHUB_TOKEN`: Auto-provided by GitHub Actions

## Performance Tips

### Speed up local tests

```bash
# Run in parallel (if you have pytest-xdist)
pytest -n auto -v

# Only test changed files
pytest --lf -v  # Last failed
pytest --ff -v  # Failed first

# Skip slow tests
pytest -m "not slow" -v
```

### Speed up CI

- Use pre-commit hooks to catch issues before push
- Run `black` and `ruff` before committing
- Test locally with `act` before pushing
- Keep PRs small and focused

## Getting Logs

### GitHub Actions Logs

1. Go to Actions tab
2. Click on workflow run
3. Click on failed job
4. Expand step to see logs
5. Download logs (top right)

### Local Act Logs

```bash
# Verbose output
act -j test -v

# Save to file
act -j test > logs.txt 2>&1
```

## Badge Status

Check workflow status in README:

- 🟢 Green: All passing
- 🔴 Red: Failures
- 🟡 Yellow: Running
- ⚫ Gray: Not run

## Links

- [Full CI/CD Documentation](CI_CD.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Act (Local Testing)](https://github.com/nektos/act)
- [Codecov](https://codecov.io)

## Support

Questions? Issues?

1. Check [CI_CD.md](CI_CD.md) documentation
2. Search existing [GitHub issues](https://github.com/coleam00/mcp-crawl4ai-rag/issues)
3. Open new issue with `ci/cd` label
4. Tag @coleam00 for urgent matters
