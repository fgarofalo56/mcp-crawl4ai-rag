#!/bin/bash
#
# Test Coverage Validation Script
# Run this script to execute all tests and generate coverage reports
#

echo "=========================================="
echo "MCP Crawl4AI RAG - Test Suite"
echo "=========================================="
echo ""

echo "Installing dependencies with uv..."
uv sync

echo ""
echo "Running all tests with coverage..."
uv run python -m pytest tests/ -v \
    --cov=src \
    --cov=knowledge_graphs \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=json \
    --tb=short

echo ""
echo "=========================================="
echo "Coverage Report Generated:"
echo "- HTML: htmlcov/index.html"
echo "- JSON: coverage.json"
echo "=========================================="
echo ""
echo "To view HTML coverage report:"
echo "  open htmlcov/index.html  (macOS)"
echo "  xdg-open htmlcov/index.html  (Linux)"
echo "  start htmlcov/index.html  (Windows)"
echo ""
