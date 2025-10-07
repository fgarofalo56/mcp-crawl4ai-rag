# Changelog

All notable changes to the Crawl4AI RAG MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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