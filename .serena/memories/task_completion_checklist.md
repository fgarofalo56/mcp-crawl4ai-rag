# Task Completion Checklist

When completing a development task on this project, follow these steps:

## 1. Code Quality Checks

### Syntax Validation
```bash
# Compile Python files to check for syntax errors
python -m py_compile src/crawl4ai_mcp.py
python -m py_compile src/utils.py
python -m py_compile knowledge_graphs/*.py
```

### Import Verification
```bash
# Test that all imports work correctly
python -c "from src.crawl4ai_mcp import *"
python -c "from src.utils import *"
```

## 2. Type Hints and Documentation

- [ ] Ensure all new functions have type hints for parameters and return values
- [ ] Add comprehensive docstrings for new functions/classes following the project style:
  - Brief description
  - Detailed explanation (if needed)
  - Args section with parameter descriptions
  - Returns section with return value description
- [ ] Update existing docstrings if function behavior changed

## 3. Testing

### Manual Testing
Since the project doesn't have automated tests, perform manual testing:

1. **Server Startup Test**:
   ```bash
   # Test that server starts without errors
   uv run src/crawl4ai_mcp.py
   ```

2. **Tool Testing** (if modified):
   - Test each MCP tool through the client
   - Verify error handling with invalid inputs
   - Check response format is correct JSON

3. **Knowledge Graph Testing** (if USE_KNOWLEDGE_GRAPH=true):
   ```bash
   # Test repository parsing
   python knowledge_graphs/parse_repo_into_neo4j.py https://github.com/test/repo.git
   
   # Test hallucination detection
   python knowledge_graphs/ai_hallucination_detector.py test_script.py
   ```

## 4. Environment and Configuration

- [ ] Update `.env.example` if new environment variables added
- [ ] Document any new configuration options in README.md
- [ ] Ensure all required environment variables have sensible defaults

## 5. Dependencies

If dependencies changed:
```bash
# Update pyproject.toml with new dependencies
# Reinstall to verify everything works
uv pip install -e .
```

## 6. Docker Compatibility

If changes might affect Docker deployment:
```bash
# Rebuild Docker image
docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .

# Test Docker container
docker run --env-file .env -p 8051:8051 mcp/crawl4ai-rag
```

## 7. Documentation Updates

- [ ] Update README.md if functionality changed
- [ ] Update inline comments for complex logic
- [ ] Document any breaking changes
- [ ] Update configuration examples if needed

## 8. Git Commit

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: description of feature" # for new features
git commit -m "fix: description of fix"     # for bug fixes
git commit -m "docs: description of change"  # for documentation
git commit -m "refactor: description"        # for refactoring

# Push to repository
git push
```

## 9. Final Verification

- [ ] Server starts without errors
- [ ] All MCP tools are visible to clients
- [ ] No import errors or missing dependencies
- [ ] Configuration works with both .env and environment variables
- [ ] Docker build succeeds (if applicable)
- [ ] Knowledge graph tools work (if enabled)

## Common Issues to Check

1. **Import Errors**: Ensure all imports are available in the environment
2. **Async/Await**: Verify async functions are properly awaited
3. **Type Errors**: Check type hints match actual usage
4. **JSON Serialization**: Ensure all return values are JSON-serializable
5. **Error Handling**: Verify try-except blocks return proper error format
6. **Environment Variables**: Test with missing optional variables

## Notes

- No automated testing framework currently in place
- No linting/formatting tools configured (consider adding ruff or black)
- Manual testing is critical given lack of automated tests
- Docker and direct Python execution should both be tested for major changes