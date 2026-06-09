# 🔄 CI/CD pipeline documentation

> **🏠 [Home](../README.md)** | **📖 [Documentation](README.md)** | **🔄 CI/CD**

---

## Overview

This document describes the automated CI/CD pipeline for the mcp-crawl4ai-rag project. The pipeline uses GitHub Actions to ensure code quality, run tests, and build Docker images automatically.

## Table of contents

- [Workflow Overview](#workflow-overview)
- [Test Workflow](#test-workflow)
- [Lint Workflow](#lint-workflow)
- [Docker Build Workflow](#docker-build-workflow)
- [Dependabot Configuration](#dependabot-configuration)
- [Status Badges](#status-badges)
- [Running Workflows Locally](#running-workflows-locally)
- [Required Secrets](#required-secrets)
- [Troubleshooting](#troubleshooting)

## Workflow overview

The CI/CD pipeline consists of three main workflows:

| Workflow | Trigger | Purpose | Runtime |
|----------|---------|---------|---------|
| **Tests** | Push/PR to main/develop | Run pytest across Python versions and OS | ~10-15 min |
| **Lint** | Push/PR to main/develop | Check code quality with black, ruff, mypy | ~2-3 min |
| **Docker Build** | Push/PR/Tags | Build and test Docker images | ~15-20 min |

### Total CI time

- **Full suite**: ~20-25 minutes (all workflows in parallel)
- **Quick feedback**: ~2-3 minutes (lint workflow completes first)
- **PR checks**: All three workflows must pass before merging

## Test workflow

**File**: `.github/workflows/test.yml`

### What it does

1. Runs pytest test suite with coverage reporting
2. Tests across multiple Python versions (3.10, 3.11, 3.12)
3. Tests on multiple operating systems (Ubuntu, Windows, macOS)
4. Uploads coverage reports to Codecov
5. Generates HTML coverage reports as artifacts

### Matrix strategy

```yaml
matrix:
  python-version: ["3.10", "3.11", "3.12"]
  os: [ubuntu-latest]
  include:
    - python-version: "3.12"
      os: windows-latest
    - python-version: "3.12"
      os: macos-latest
```

This creates 5 test jobs:
- Ubuntu: Python 3.10, 3.11, 3.12
- Windows: Python 3.12
- macOS: Python 3.12

### Key features

- **Dependency Caching**: Uses `actions/cache` to cache uv packages, reducing install time
- **Parallel Execution**: All matrix jobs run in parallel
- **Coverage Reporting**:
  - XML format for Codecov
  - HTML format for artifact download
  - Terminal output for immediate feedback
- **Coverage Threshold**: Currently set to 29%, with a goal of 80%
- **Environment Variables**: Mock credentials for testing

### Environment variables

Tests run with these mock environment variables:

```bash
OPENAI_API_KEY=test-key-for-ci
SUPABASE_URL=https://test.supabase.co
SUPABASE_SERVICE_KEY=test-key
USE_KNOWLEDGE_GRAPH=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=test
```

### Artifacts

- **Coverage HTML Report**: Available for download after workflow completion
- **Retention**: 7 days

## Lint workflow

**File**: `.github/workflows/lint.yml`

### What it does

1. **Black**: Checks code formatting (100 char line length)
2. **Ruff**: Lints for code quality issues
3. **Ruff Format**: Checks formatting consistency
4. **Mypy**: Type checking (continues on error initially)
5. **Code Quality Checks**:
   - Detects print statements in source code
   - Lists TODO comments

### Key features

- **Fast Feedback**: Runs only on Python 3.12, Ubuntu
- **Non-blocking Mypy**: Allows mypy failures during initial type hint adoption
- **Informational Warnings**: Print statements and TODOs generate warnings, not errors

### Expected output

```bash
✅ Black formatting check passed
✅ Ruff linting passed
⚠️  Mypy found type issues (non-blocking)
⚠️  Found print statements in source code
ℹ️  TODO comments found
```

## Docker build workflow

**File**: `.github/workflows/docker.yml`

### What it does

1. Builds Docker image for the MCP server
2. Tests that the container starts and runs correctly
3. Pushes images to GitHub Container Registry (GHCR)
4. Supports multi-platform builds (amd64, arm64)

### Triggers

- **Push to main/develop**: Build and push images
- **Tags (v*)**: Build and push versioned releases
- **Pull Requests**: Build only, no push

### Image tags

The workflow automatically generates tags based on the trigger:

```bash
# Branch push
ghcr.io/coleam00/mcp-crawl4ai-rag:main
ghcr.io/coleam00/mcp-crawl4ai-rag:develop

# Version tags
ghcr.io/coleam00/mcp-crawl4ai-rag:v1.0.0
ghcr.io/coleam00/mcp-crawl4ai-rag:1.0

# Commit SHA
ghcr.io/coleam00/mcp-crawl4ai-rag:main-abc123

# Latest (main branch only)
ghcr.io/coleam00/mcp-crawl4ai-rag:latest
```

### Container testing

The workflow performs automated tests on the built image:

1. **Startup Test**: Verifies container starts successfully
2. **Health Check**: Ensures container runs for at least 5 seconds
3. **Log Analysis**: Checks for errors/exceptions in logs
4. **Cleanup**: Stops and removes test container

### Multi-platform support

Images are built for:
- `linux/amd64` (Intel/AMD processors)
- `linux/arm64` (Apple Silicon, ARM servers)

### Key features

- **BuildKit Caching**: Uses GitHub Actions cache for faster builds
- **Security**: Automatic login to GHCR using GitHub token
- **Metadata**: Proper labels and tags for container discoverability
- **Build Summary**: Generates markdown summary with pull commands

## Dependabot configuration

**File**: `.github/dependabot.yml`

### What it does

Automatically creates pull requests for dependency updates on a weekly schedule (Mondays at 9 AM).

### Managed Ecosystems

1. **GitHub Actions**: Updates action versions in workflows
2. **Python Dependencies**: Updates packages in pyproject.toml/uv.lock
3. **Docker**: Updates base images in Dockerfile

### Dependency Groups

Python dependencies are grouped to reduce PR noise:

- **dev-dependencies**: pytest, black, ruff, mypy
- **ai-dependencies**: openai, transformers, sentence-transformers, torch
- **crawling-dependencies**: crawl4ai, requests
- **database-dependencies**: supabase, neo4j

### Configuration

```yaml
schedule:
  interval: "weekly"
  day: "monday"
  time: "09:00"
open-pull-requests-limit: 10
```

## Status Badges

The README displays real-time status badges for all workflows:

```markdown
![Tests](https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/test.yml/badge.svg)
![Lint](https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/lint.yml/badge.svg)
![Docker Build](https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/docker.yml/badge.svg)
![Coverage](https://codecov.io/gh/coleam00/mcp-crawl4ai-rag/branch/main/graph/badge.svg)
```

### Badge Status

- **Green**: All checks passing
- **Red**: One or more checks failing
- **Yellow**: Workflow running
- **Gray**: No workflow runs yet

## Running Workflows Locally

### Prerequisites

```bash
# Install act (GitHub Actions local runner)
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows
choco install act-cli
```

### Running Tests Locally

```bash
# Run all tests as they would run in CI
act -j test

# Run specific Python version
act -j test -matrix python-version:3.12

# Run with secrets
act -j test -s CODECOV_TOKEN=your-token
```

### Running Lint Locally

```bash
# Run linting checks
act -j lint

# Individual checks
black --check src/ tests/ knowledge_graphs/
ruff check src/ tests/ knowledge_graphs/
mypy src/ --config-file pyproject.toml
```

### Running Docker Build Locally

```bash
# Build and test Docker image
act -j build

# Or use docker directly
docker build -t mcp/crawl4ai-rag:test --build-arg PORT=8051 .
docker run -d --env-file .env -p 8051:8051 mcp/crawl4ai-rag:test
```

### Manual Test Run

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install -e ".[dev]"
uv pip install pytest-cov

# Run tests
pytest -v --cov=src --cov-report=term-missing

# Run specific test
pytest tests/test_config.py -v

# Run with markers
pytest -m "not slow" -v
```

## Required Secrets

### Optional Secrets

These secrets are optional but enhance functionality:

| Secret | Purpose | Required |
|--------|---------|----------|
| `CODECOV_TOKEN` | Upload coverage to Codecov | No (public repos) |
| `GITHUB_TOKEN` | Push Docker images to GHCR | Auto-provided |

### Setting Secrets

1. Go to repository Settings
2. Navigate to Secrets and variables → Actions
3. Click "New repository secret"
4. Add secret name and value

### Codecov Setup

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the upload token
5. Add as `CODECOV_TOKEN` secret in GitHub

**Note**: Public repositories don't require a token for Codecov uploads.

## Troubleshooting

### Common issues

#### 1. Test Failures Due to Missing Dependencies

**Symptom**: Tests fail with import errors

**Solution**:
```yaml
# Add missing dependency to pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=5.0.0",  # Add this
    # ...
]
```

#### 2. Docker Build Timeout

**Symptom**: Docker workflow exceeds 45-minute timeout

**Solution**:
- Use Docker layer caching (already enabled)
- Consider self-hosted runners for large dependencies
- Split test matrix to reduce parallel jobs

```yaml
# Increase timeout
timeout-minutes: 60
```

#### 3. Coverage Upload Fails

**Symptom**: Codecov upload step fails

**Solution**:
- Add `CODECOV_TOKEN` secret
- Use `fail_ci_if_error: false` to not block CI
- Check coverage.xml file is generated

```bash
# Verify coverage file locally
pytest --cov=src --cov-report=xml
ls -la coverage.xml
```

#### 4. Mypy Type Errors Block CI

**Symptom**: Mypy failures cause workflow to fail

**Solution**: Already handled with `continue-on-error: true`

```yaml
- name: Type check with mypy
  run: mypy src/ --config-file pyproject.toml
  continue-on-error: true
```

#### 5. Black Formatting Check Fails

**Symptom**: Black finds formatting issues

**Solution**:
```bash
# Auto-format locally
black src/ tests/ knowledge_graphs/

# Commit changes
git add .
git commit -m "style: format code with black"
```

#### 6. Ruff Linting Errors

**Symptom**: Ruff finds code quality issues

**Solution**:
```bash
# See what ruff would fix
ruff check src/ --diff

# Auto-fix issues
ruff check src/ --fix

# Check again
ruff check src/
```

#### 7. Container Won't Start in Docker Workflow

**Symptom**: Docker container exits immediately

**Solution**:
```bash
# Test locally first
docker build -t test .
docker run --env-file .env.test test

# Check logs
docker logs <container-id>

# Common issues:
# - Missing environment variables
# - Port conflicts
# - Invalid configuration
```

#### 8. Matrix Jobs Failing on Specific OS

**Symptom**: Tests pass on Ubuntu but fail on Windows/macOS

**Solution**:
```python
# Use cross-platform paths
import os
from pathlib import Path

# Instead of:
path = "/tmp/file.txt"

# Use:
path = Path.home() / "file.txt"
```

#### 9. Large Dependencies Slow CI

**Symptom**: PyTorch/transformers take 10+ minutes to install

**Current Optimizations**:
- uv package manager (10x faster than pip)
- Dependency caching with `actions/cache`
- Cache key includes `uv.lock` hash

**Additional Optimizations**:
```yaml
# Use pre-built wheels
- name: Install dependencies
  run: |
    uv pip install --system torch --index-url https://download.pytorch.org/whl/cpu

# Or use conda for faster installs
- uses: conda-incubator/setup-miniconda@v3
  with:
    python-version: 3.12
- run: conda install pytorch -c pytorch
```

### Getting Help

1. **Check workflow logs**: Click on failed workflow in Actions tab
2. **Run locally**: Use `act` to reproduce issues
3. **GitHub Actions docs**: [docs.github.com/actions](https://docs.github.com/en/actions)
4. **Open an issue**: Provide workflow logs and error messages

## Performance Optimization Tips

### 1. Reduce Matrix Size

For faster feedback on PRs, consider running full matrix only on main:

```yaml
strategy:
  matrix:
    python-version: ${{ github.ref == 'refs/heads/main' && fromJSON('["3.10", "3.11", "3.12"]') || fromJSON('["3.12"]') }}
```

### 2. Use Self-Hosted Runners

For repositories with large dependencies:

```yaml
runs-on: self-hosted
```

Benefits:
- Pre-cached dependencies
- Faster hardware
- No GitHub Actions minute limits

### 3. Conditional Workflows

Skip certain jobs based on file changes:

```yaml
paths:
  - 'src/**'
  - 'tests/**'
  - 'pyproject.toml'
```

### 4. Fail Fast

Stop matrix jobs on first failure:

```yaml
strategy:
  fail-fast: true
```

### 5. Artifact Cleanup

Automatically delete old artifacts:

```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 3  # Reduce from 7
```

## Workflow Maintenance

### Regular Tasks

- **Weekly**: Review Dependabot PRs
- **Monthly**: Check workflow run times and optimize
- **Quarterly**: Update action versions manually
- **Annually**: Review matrix strategy (Python versions, OS)

### Metrics to Monitor

1. **Average run time**: Should be < 20 minutes
2. **Success rate**: Should be > 90%
3. **Cache hit rate**: Should be > 80%
4. **Artifact size**: Should be < 50 MB

## Security Best Practices

1. **Pin action versions**: Use `@v4` not `@main`
2. **Minimal secrets**: Only use necessary secrets
3. **Read-only tokens**: Use minimal permissions
4. **Dependabot PRs**: Review before merging
5. **Container scanning**: Consider adding Trivy/Snyk

## Future Enhancements

### Planned Improvements

1. **Semantic Release**: Automated versioning and changelog
2. **Performance Testing**: Add benchmarking workflow
3. **Security Scanning**: Add CodeQL analysis
4. **Documentation**: Auto-generate API docs
5. **Release Automation**: Automated GitHub releases on tags

### Example: Adding CodeQL

```yaml
name: CodeQL
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Act - Local Testing](https://github.com/nektos/act)
- [Codecov Documentation](https://docs.codecov.com)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)

## Questions?

If you have questions or need help with the CI/CD pipeline, please:

1. Check this documentation first
2. Review workflow logs in the Actions tab
3. Open a GitHub issue with the `ci/cd` label
4. Tag @coleam00 for urgent issues
