# Changelog

All notable changes to the Crawl4AI RAG MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-29

### Major Release: Modular Architecture & Production-Ready Code Quality

This release represents a complete architectural transformation from monolithic to modular design, with comprehensive testing infrastructure and production-grade code quality standards.

### Breaking Changes
**None** - Despite major internal refactoring, all external APIs remain 100% backward compatible.

### Added

#### Modular Architecture (Phase 2)
- **Tool Organization** - 16 MCP tools extracted into 5 category-specific modules:
  - `src/tools/crawling_tools.py` (445 lines, 5 tools)
  - `src/tools/rag_tools.py` (160 lines, 2 tools)
  - `src/tools/knowledge_graph_tools.py` (474 lines, 4 tools)
  - `src/tools/graphrag_tools.py` (565 lines, 4 tools)
  - `src/tools/source_tools.py` (96 lines, 1 tool)

- **Core Components** - Infrastructure separated into dedicated modules:
  - `src/core/context.py` (25 lines) - Crawl4AIContext dataclass
  - `src/core/lifespan.py` (127 lines) - Server lifecycle management
  - `src/core/reranking.py` (54 lines) - Lazy reranking model loading
  - `src/core/validators.py` (72 lines) - Input validation helpers
  - `src/core/browser_validation.py` (210 lines) - Playwright browser detection

- **Service Layer Framework**:
  - `src/services/base_service.py` (57 lines)
  - `src/services/crawl_service.py` (188 lines)

- **Repository Pattern**:
  - `src/repositories/document_repository.py` (148 lines)
  - `src/repositories/supabase_document_repository.py` (194 lines)

#### Integration Test Infrastructure
- **Comprehensive Test Suite** (88 integration tests across 3 files):
  - `tests/integration/test_crawl_workflows.py` (31 tests) - All crawling strategies
  - `tests/integration/test_rag_pipeline.py` (20 tests) - RAG and GraphRAG workflows
  - `tests/integration/test_docker_deployment.py` (37 tests) - Deployment validation
  - `tests/integration/conftest.py` (415 lines) - Shared fixtures

- **Test Documentation**:
  - `tests/integration/README.md` (420 lines) - Complete test guide
  - `docs/guides/INTEGRATION_TESTING.md` - Integration testing best practices
  - `docs/guides/TEST_EXECUTION_GUIDE.md` (350 lines) - How to run tests

#### Utility Modules (8 new modules, 2,900+ lines)
- `src/crawling_strategies.py` (417 lines) - Strategy pattern for crawling
- `src/crawling_utils.py` (528 lines) - Reusable crawling utilities
- `src/github_utils.py` (335 lines) - GitHub batch processing
- `src/knowledge_graph_commands.py` (469 lines) - Neo4j command pattern
- `src/memory_monitor.py` (230 lines) - Memory monitoring utilities
- `src/initialization_utils.py` (257 lines) - Service initialization
- `src/search_strategies.py` (459 lines) - RAG search strategies
- `src/crawl_helpers.py` (297 lines) - Crawling helper functions

### Changed

#### Complete Function Refactoring (All 11 Large Functions)
- **parse_github_repositories_batch**: 274 → 140 lines (49% reduction)
- **smart_crawl_url**: 232 → 79 lines (66% reduction)
- **crawl_with_memory_monitoring**: 193 → 96 lines (50% reduction)
- **query_knowledge_graph**: 181 → 104 lines (42% reduction)
- **crawl4ai_lifespan**: 176 → 63 lines (64% reduction)
- **search_code_examples**: 176 → 112 lines (36% reduction)
- **crawl_with_graph_extraction**: 169 → 115 lines (32% reduction)
- **crawl_with_stealth_mode**: 168 → 93 lines (44% reduction)
- **crawl_with_multi_url_config**: 168 → 115 lines (31% reduction)
- **crawl_single_page**: 159 → 112 lines (30% reduction)
- **perform_rag_query**: 155 → 140 lines (10% reduction)

**Total Lines Reduced**: 1,222 lines eliminated (average 42% reduction per function)

#### File Organization
- **Monolithic file eliminated**: `src/crawl4ai_mcp.py` (2,013 lines) → archived
- **New modular entry point**: `src/server.py` (120 lines)
- **Largest file reduced**: 2,013 → 565 lines (72% reduction)
- **Module count increased**: 21 → 34 files (better organization)
- **Average file size**: ~200 → ~120 lines (40% smaller)

#### Test Coverage Improvements
- **Test count**: 64 → 268 tests (319% increase)
- **Coverage**: 29% → 59% overall (30 percentage point improvement)
- **Test files**: 9 → 21 files
- **Unit test coverage**: 70%+ on utility modules
- **Integration coverage**: 50%+ on workflows

### Fixed

#### Critical P0 Bugs (All Resolved)

1. **Docker SSE Transport Configuration** (2025-11-18)
   - **Issue**: Docker container running with wrong transport (stdio instead of sse)
   - **Symptom**: Container logs showed "transport: stdio" and ".env file not found"
   - **Root Cause**:
     - Dockerfile CMD used obsolete module name `crawl4ai_mcp` (pre-v2.0.0)
     - `run_mcp.py` hardcoded `TRANSPORT=stdio`, overriding Docker env vars
     - `docker-compose.yml` didn't load `.env.docker` file
   - **Fix**:
     - Updated Dockerfile CMD to `python -m src.server` (correct v2.0.0 module)
     - Modified `run_mcp.py` to respect pre-set `TRANSPORT` environment variable
     - Added `env_file: .env.docker` to `docker-compose.yml`
     - Created `.env.docker.example` template for Docker deployments
   - **Result**: Container now runs correctly with SSE transport on port 8051
   - **Documentation**: Updated `docs/DOCKER_SETUP.md`, `README.md`, `.env.example`
   - **Files Changed**: `Dockerfile`, `run_mcp.py`, `docker-compose.yml`, `.env.docker.example`

2. **Playwright Browser Detection** (2025-10-22, Task-013)
   - **Issue**: Server failing to start with "browser not found" error
   - **Solution**: Created comprehensive browser validation module
   - **Files**: `src/core/browser_validation.py` (210 lines)
   - **Tests**: 15 comprehensive tests (100% passing)
   - **Docs**: Updated README, QUICK_START, CLAUDE_DESKTOP_SETUP, TROUBLESHOOTING
   - **Impact**: Server now starts reliably with platform-specific fix instructions

2. **Lazy Loading Cleanup** (2025-10-17)
   - **Issue**: AttributeError during MCP server cleanup/shutdown
   - **Solution**: Added `close()` methods to `LazyKnowledgeGraphComponents` and `LazyGraphRAGComponents`
   - **Tests**: 20 comprehensive tests (100% passing)
   - **Impact**: Clean shutdown, proper Neo4j connection cleanup, no resource leaks
   - **See**: `docs/fixes/LAZY_LOADING_CLEANUP_FIX.md`

3. **Stdout Contamination** (2025-10-17)
   - **Issue**: JSON parsing errors from third-party libraries writing to stdout
   - **Solution**: Created `stdout_safety.py` module with comprehensive stdout protection
   - **Tests**: 30 tests (93% coverage)
   - **Impact**: Clean JSON-RPC communication with Claude Desktop
   - **See**: `docs/fixes/STDOUT_CONTAMINATION_FIX.md`

#### P1 Bug Fixes

4. **Source Filter Parameter** (2025-10-14, Task-011)
   - **Issue**: ValidationError caused by `source` vs `source_filter` naming inconsistency
   - **Solution**: Renamed parameter in function signature and 4 internal references
   - **Tests**: 8 regression tests (100% passing)
   - **Impact**: `perform_rag_query` now works correctly with source filtering

5. **Print Statements Breaking MCP** (2025-10-14, Task-012)
   - **Issue**: 40+ print() statements outputting to stdout instead of stderr
   - **Solution**: Fixed all print statements in `src/utils.py` to use stderr
   - **Impact**: MCP server starts cleanly, all tools functional

### Performance

- **Startup time**: Reduced from ~22s to ~3s (7x faster) via lazy loading
- **Memory efficiency**: Adaptive throttling in batch operations
- **Code maintainability**: 100% of functions now <150 lines
- **Test execution**: Integration tests run in 2-5 seconds total

### Documentation

- **Sprint 1 Retrospective** (comprehensive sprint analysis)
- **Integration Test Guide** (complete testing documentation)
- **Modular Architecture Guide** (docs/ARCHITECTURE.md updated)
- **Browser Installation Guide** (comprehensive troubleshooting)
- **15+ documentation files** updated/created

### Technical Debt Eliminated

- ❌ **Before**: 11 functions >150 lines (largest: 274 lines)
- ✅ **After**: 0 functions >150 lines (largest: 140 lines)
- ❌ **Before**: No integration tests
- ✅ **After**: 88 comprehensive integration tests
- ❌ **Before**: 29% test coverage
- ✅ **After**: 59% test coverage (70%+ on utility modules)
- ❌ **Before**: Monolithic 2,013-line file
- ✅ **After**: Modular 34-file architecture

### Migration Guide

**From v1.x to v2.0.0**:

No migration required! All changes are internal. To upgrade:

```bash
# Pull latest code
git pull

# Install dependencies (no new dependencies added)
uv pip install -e .

# Restart MCP server
# No configuration changes needed
```

**All existing workflows remain unchanged.**

### Notes

- **Zero breaking changes** - 100% backward compatible
- **Production ready** - Comprehensive testing and modular architecture
- **v2.0.0 milestone** - Complete architectural transformation
- Sprint 1 objectives achieved (9.5/10 score)

---

## [1.3.0] - 2025-10-07

### Added
- **Production Scaling Guide** (`SCALING_GUIDE.md`) - Comprehensive guide for production deployments
  - Batch processing strategies and best practices
  - Memory management and optimization techniques
  - Concurrent crawling limits and adaptive concurrency
  - Rate limiting configuration for OpenAI API
  - Database optimization for Supabase and Neo4j
  - Performance benchmarks and metrics
  - Cost optimization strategies
  - Production monitoring and observability
- **Enhanced Troubleshooting Guide** - Expanded TROUBLESHOOTING.md with:
  - GraphRAG-specific troubleshooting
  - Batch processing timeout solutions
  - Performance optimization tips for crawling and RAG queries
  - Additional quick fixes for common issues
- **GraphRAG Scaling Documentation** - Added to GRAPHRAG_GUIDE.md:
  - Batch processing best practices
  - Rate limiting strategies for entity extraction
  - Progress tracking patterns
  - Memory monitoring for large-scale GraphRAG operations
  - Concurrent entity extraction limits by OpenAI tier

### Changed
- **Code Quality Improvements** - Systematic refactoring for maintainability:
  - Documented refactoring plan for 11 large functions (>150 lines)
  - Identified patterns for extraction: crawling strategies, memory monitoring, search strategies
  - Planned modular architecture with strategy pattern
  - Target: Reduce average function size from 81 to 65 lines
- **Documentation Consolidation**:
  - Archived 9 historical/completed documents to `docs/archive/`
  - Updated cross-references in troubleshooting guides
  - Enhanced production readiness documentation
- **Improved Error Messages** - More descriptive error responses for:
  - GraphRAG configuration issues
  - Foreign key constraint violations (should not occur post-v1.1.1)
  - API rate limiting suggestions

### Fixed
- **Critical: Playwright Browser Detection** (2025-10-22) - Fixed "browser not found" error preventing server startup
  - Created comprehensive browser validation module (`src/core/browser_validation.py`)
  - Added pre-flight browser detection before Crawl4AI initialization
  - Detects browsers in global location but inaccessible to virtual environment (most common issue)
  - Provides platform-specific fix instructions (Windows/Linux/Mac)
  - Supports PLAYWRIGHT_BROWSERS_PATH environment variable for custom browser locations
  - Updated all documentation (README, QUICK_START, CLAUDE_DESKTOP_SETUP, TROUBLESHOOTING)
  - See task-013 in project tracking for complete implementation details
- **Critical: Lazy Loading Cleanup** (2025-10-17) - Fixed AttributeError during MCP server cleanup
  - Added `close()` methods to `LazyKnowledgeGraphComponents` and `LazyGraphRAGComponents`
  - Updated cleanup functions to properly handle lazy-loaded Neo4j components
  - Added defensive programming (hasattr checks, exception handling)
  - Created comprehensive test suite (20 tests, all passing)
  - Eliminates error messages in Claude Desktop logs during shutdown
  - Ensures proper Neo4j connection cleanup and prevents resource leaks
  - See `docs/fixes/LAZY_LOADING_CLEANUP_FIX.md` for complete details
- **Critical: Stdout Contamination** (2025-10-17) - Fixed JSON parsing errors caused by third-party libraries writing to stdout
  - Created comprehensive `stdout_safety.py` module for stdout protection
  - Configured all logging to use stderr only (httpx, crawl4ai, playwright, etc.)
  - Set environment variables to suppress verbose library output
  - Added validation tools for development-mode contamination detection
  - Integrated early in `run_mcp.py` before any library imports
  - Created 30 comprehensive tests (all passing, 93% coverage)
  - Eliminates "[FETCH]" and other non-JSON output breaking MCP protocol
  - Ensures clean JSON-RPC communication with Claude Desktop
  - See `docs/fixes/STDOUT_CONTAMINATION_FIX.md` for complete details
- Documentation accuracy improvements across guides
- Corrected scaling recommendations for different deployment sizes
- Updated performance benchmarks with realistic metrics

### Technical Improvements
- **Resilience Enhancements**:
  - Better handling of large-scale operations
  - Improved memory management guidance
  - Rate limiting best practices
  - Connection pooling optimization
- **Developer Experience**:
  - Clear troubleshooting workflows
  - Performance tuning guidance
  - Cost optimization strategies
  - Production deployment checklist

### Documentation
- Total active documentation reduced from 23 to 15 files (35% reduction)
- New comprehensive guides: SCALING_GUIDE.md
- Enhanced existing guides: TROUBLESHOOTING.md, GRAPHRAG_GUIDE.md
- Archived historical documents with clear migration path
- **Complete Documentation Audit** (2025-10-28):
  - Comprehensive review of 94 markdown files (DOCUMENTATION_REVIEW_REPORT.md)
  - Updated .env.example with SKIP_BROWSER_VALIDATION documentation
  - Enhanced TROUBLESHOOTING.md with browser skip option
  - Updated README.md installation section with development option
  - Version number consistency updates across documentation
  - 99% compliance with MARKDOWN_STYLE_GUIDE.md standards

### Notes
- This release focuses on **code quality**, **production readiness**, and **scalability**
- No new MCP tools added (remains 16 tools)
- All improvements are backward compatible
- Refactoring work identified for future releases

## [1.2.0] - 2025-10-07

### Added
- **GraphRAG System** - Complete implementation of graph-augmented RAG for web content
  - `crawl_with_graph_extraction` - Crawl URLs and build knowledge graphs from content
  - `graphrag_query` - RAG queries with optional graph enrichment for richer context
  - `query_document_graph` - Direct Cypher queries on document knowledge graph
  - `get_entity_context` - Explore entity neighborhoods and relationships
- **Document Knowledge Graph Infrastructure**:
  - `DocumentGraphValidator` - Neo4j schema management for document entities
  - `DocumentEntityExtractor` - LLM-based entity and relationship extraction
  - `DocumentGraphQueries` - Graph traversal and enrichment functions
- **Neo4j Document Schema**:
  - Document nodes linked to Supabase IDs
  - Entity nodes (Concept, Technology, Configuration, Person, Organization, Product)
  - Relationship edges (REQUIRES, USES, PART_OF, etc.)
  - Source organization and document linkage
- **Comprehensive Documentation**:
  - New `docs/GRAPHRAG_GUIDE.md` - Complete GraphRAG implementation guide
  - Architecture diagrams and usage examples
  - Best practices and performance considerations
  - Troubleshooting guide
- **Environment Variable**: `USE_GRAPHRAG` - Enable/disable GraphRAG functionality independently

### Changed
- Updated API Reference to document all 16 tools (12 existing + 4 new GraphRAG tools)
- Updated README.md with GraphRAG features and v1.2.0 overview
- Enhanced `Crawl4AIContext` dataclass with document graph components
- Updated `.env.example` with GraphRAG configuration options
- Total tool count increased from 12 to 16 tools
- Version number in health endpoint updated to 1.2.0

### Technical Details
- Separate knowledge graphs: Code repositories (existing) vs. Web documents (new)
- Entity extraction uses `gpt-4o-mini` for cost efficiency
- Configurable concurrency for parallel entity extraction (default: 3)
- Graph enrichment adds ~150-200% latency but significantly improves answer quality
- Backward compatible: Existing tools unchanged, GraphRAG is opt-in

## [1.1.1] - 2025-10-07

### Added
- **Batch Repository Processing** (`parse_github_repositories_batch`) - New tool for parsing multiple GitHub repositories in parallel
  - Configurable concurrency limits to control resource usage
  - Automatic retry logic with exponential backoff for failed repositories
  - Detailed per-repository status tracking and statistics
  - Aggregate statistics across all processed repositories
  - Easy retry support with collected failed repository URLs
  - Progress tracking with real-time console output
- **Health Check Endpoint** - Added `/health` HTTP endpoint for monitoring and load balancers
  - Returns service status, version, and transport information
  - Compatible with Docker healthcheck and Kubernetes probes
  - Only available when using SSE transport

### Fixed
- **Foreign Key Constraint Violations** - Fixed critical database insertion errors in three crawl functions:
  - `crawl_with_multi_url_config`: Now creates source records before inserting documents
  - `crawl_with_stealth_mode`: Now creates source records before inserting documents
  - `crawl_with_memory_monitoring`: Now creates source records before inserting documents with word count tracking
  - All functions now follow the same pattern as `smart_crawl_url` and `crawl_single_page`
- **Error Message**: "insert or update on table "crawled_pages" violates foreign key constraint" no longer occurs

### Changed
- Updated API Reference to document all 12 tools (previously stated 11)
- Updated README.md with v1.1.1 features and bug fixes
- Total tool count increased from 11 to 12 tools
- Improved consistency across crawl functions for source management

## [1.1.0] - 2025-10-02

### Added
- **Stealth Mode Crawling** (`crawl_with_stealth_mode`) - New tool to bypass bot detection systems like Cloudflare, Akamai, and PerimeterX using undetected browser technology
- **Smart Multi-URL Configuration** (`crawl_with_multi_url_config`) - New tool that automatically optimizes crawler settings based on content type (documentation, articles, general)
- **Memory-Monitored Crawling** (`crawl_with_memory_monitoring`) - New tool with active memory monitoring and adaptive throttling for large-scale crawling operations
- Comprehensive documentation guide for new features (`docs/NEW_FEATURES_GUIDE.md`)
- psutil dependency (>=5.9.0) for memory monitoring functionality
- Implementation documentation (`docs/IMPLEMENTATION_COMPLETE.md`)
- Modernization summary documentation (`docs/MODERNIZATION_SUMMARY.md`)

### Changed
- Updated README.md with v1.1.0 features section and quick examples
- Total tool count increased from 8 to 11 tools
- Enhanced error handling with user-friendly messages for Neo4j connectivity issues

### Fixed
- Suppressed deprecation warnings from pydantic and supabase dependencies (commit c6696a9)
- Fixed MCP server startup issues related to Neo4j configuration (commit f67fd3a)
- Improved Neo4j debug output for better troubleshooting (commit 2544316)

## [1.0.0] - 2025-09-15

### Added
- **Knowledge Graph Integration** - Full Neo4j-based knowledge graph functionality for AI hallucination detection
  - `parse_github_repository` tool for extracting repository structure into Neo4j
  - `check_ai_script_hallucinations` tool for validating AI-generated Python scripts
  - `query_knowledge_graph` tool for exploring repository data with Cypher queries
- **Azure OpenAI Support** - Configuration options for Azure-hosted OpenAI endpoints
- **Advanced RAG Strategies**:
  - Contextual embeddings for enriched semantic understanding
  - Hybrid search combining vector and keyword search
  - Agentic RAG for specialized code example extraction
  - Reranking with cross-encoder models for improved relevance
- **Code Example Extraction** - Intelligent extraction and indexing of code snippets from documentation
- **Source Management** - Track and filter content by source domain
- Rich error handling and validation for all knowledge graph operations
- Comprehensive test suite with 64 tests covering validators, error handlers, and configurations
- Docker support with complete containerization setup

### Changed
- Upgraded to FastMCP v2.12.4 for improved MCP server performance
- Updated to Crawl4AI v0.7.4 with latest features
- Enhanced chunking strategy with smart markdown-aware splitting
- Improved parallel processing with MemoryAdaptiveDispatcher
- Better repository structure with separate `knowledge_graphs` module

### Fixed
- Concurrent request handling with proper retry logic
- Nested attribute extraction in knowledge graph parsing
- Repository calculation accuracy in knowledge graph queries

## [0.9.0] - 2025-08-20

### Added
- Initial MCP server implementation with Crawl4AI integration
- Core web crawling tools:
  - `crawl_single_page` for single page extraction
  - `smart_crawl_url` for intelligent URL type detection
  - `get_available_sources` for source discovery
  - `perform_rag_query` for semantic search
- Supabase vector database integration
- Smart content chunking with header preservation
- Recursive crawling with depth control
- Sitemap and text file parsing support
- Basic RAG capabilities with vector search

### Changed
- Migrated from prototype to production-ready MCP server
- Established FastMCP-based architecture

## [0.1.0] - 2025-07-01

### Added
- Initial project setup and prototype
- Basic Crawl4AI integration experiments
- Proof of concept for MCP protocol implementation

---

## Version History Summary

- **v1.1.0** (Current) - Advanced crawling features: stealth mode, multi-URL config, memory monitoring
- **v1.0.0** - Knowledge graph integration, hallucination detection, Azure OpenAI support
- **v0.9.0** - Core MCP server with crawling and RAG capabilities
- **v0.1.0** - Initial prototype

## Upgrade Guide

### From v1.0.0 to v1.1.0
1. Install new dependency: `pip install psutil>=5.9.0`
2. Update project: `git pull && uv pip install -e .`
3. Restart MCP server or Claude Desktop
4. New tools available immediately, no configuration changes required

### From v0.9.0 to v1.0.0
1. Set up Neo4j database if using knowledge graph features
2. Configure environment variables for Neo4j (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
3. Enable features with USE_KNOWLEDGE_GRAPH=true in .env
4. Update dependencies: `uv pip install -e .`

## Links

- [GitHub Repository](https://github.com/coleam00/mcp-crawl4ai-rag)
- [Documentation](./docs/)
- [API Reference](./API_REFERENCE.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
