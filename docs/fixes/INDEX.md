# Technical Fixes Documentation

This directory contains documentation for technical issues, their resolutions, and troubleshooting guidance.

## Purpose

These documents provide detailed information about specific technical problems encountered in the project and their solutions. They serve as references for similar issues in the future.

## Available Fix Documentation

### Azure OpenAI
**[AZURE_OPENAI_FIX.md](AZURE_OPENAI_FIX.md)**
- Issue: Azure OpenAI embedding generation problems
- Solution: Configuration and API usage fixes
- Status: Resolved

### GraphRAG
**[GRAPHRAG_FIX.md](GRAPHRAG_FIX.md)**
- Issue: GraphRAG entity extraction and graph building issues
- Solution: Implementation improvements and error handling
- Status: Resolved

### Neo4j
**[NEO4J_FIX.md](NEO4J_FIX.md)**
- Issue: Neo4j connection and authentication problems
- Solution: Configuration and connection string fixes
- Status: Resolved

### Import Issues
**[IMPORT_FIX_APPLIED.md](IMPORT_FIX_APPLIED.md)**
- Issue: Import errors and module resolution problems
- Solution: Import path corrections and module structure fixes
- Status: Resolved

### Lazy Loading Cleanup
**[LAZY_LOADING_CLEANUP_FIX.md](LAZY_LOADING_CLEANUP_FIX.md)**
- Issue: Browser instance cleanup and resource management
- Solution: Proper cleanup of Playwright browser instances
- Status: Resolved

### stdout Contamination
**[STDOUT_CONTAMINATION_FIX.md](STDOUT_CONTAMINATION_FIX.md)**
- Issue: Debug output contaminating MCP protocol communication
- Solution: Redirect debug output to stderr and implement output safety
- Status: Resolved

### WSL2 Docker Integration
**[WSL2_DOCKER_INTEGRATION_FIX.md](WSL2_DOCKER_INTEGRATION_FIX.md)**
- Issue: Docker commands not available in WSL2 environment
- Solution: Enable Docker Desktop WSL2 integration in settings
- Status: Resolved

## Related Documentation

For additional troubleshooting:
- **Comprehensive Guide**: [docs/guides/TROUBLESHOOTING.md](../guides/TROUBLESHOOTING.md)
- **Docker Setup Issues**: [docs/DOCKER_SETUP.md](../DOCKER_SETUP.md)
- **Claude Desktop Setup**: [docs/CLAUDE_DESKTOP_SETUP.md](../CLAUDE_DESKTOP_SETUP.md)

## Navigation

- **For main documentation**: See [docs/README.md](../README.md)
- **For historical fixes**: See [docs/archive/](../archive/)
- **For setup guides**: See [docs/guides/](../guides/)

---

**Note**: These are resolved issues. If you encounter similar problems, refer to the relevant fix document for the solution approach.

**Last Updated**: October 28, 2025
