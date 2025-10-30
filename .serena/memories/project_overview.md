# MCP-Crawl4AI-RAG Project Overview

## Project Purpose
This is a Model Context Protocol (MCP) server that integrates Crawl4AI and Supabase to provide AI agents and AI coding assistants with advanced web crawling and RAG (Retrieval-Augmented Generation) capabilities. The primary goal is to enable AI systems to scrape web content and use that knowledge for RAG applications.

**Version 2.0.0** features a complete modular architecture refactoring, transitioning from a 2000+ line monolithic file to an organized structure with clear separation of concerns.

## Tech Stack
- **Language**: Python 3.10+ (3.12 recommended)
- **Core Dependencies**:
  - crawl4ai==0.7.4 (web crawling)
  - supabase==2.15.1+ (vector database)
  - openai==1.71.0+ (embeddings via Azure OpenAI)
  - sentence-transformers>=4.1.0 (reranking)
  - neo4j>=5.28.1 (knowledge graph)
  - fastmcp>=2.12.4 (MCP server framework)
- **Database**: Supabase with pgvector extension for vector search
- **Optional**: Neo4j for knowledge graph and hallucination detection
- **Deployment**: Docker or direct Python with uv package manager
- **Package Manager**: uv (fast Python package installer)

## Key Features
1. **Smart Web Crawling**: Automatically detects URL types (sitemaps, text files, regular pages)
2. **Multiple Crawling Strategies**:
   - Single page crawling
   - Smart multi-page crawling
   - Stealth mode (bypass bot protection)
   - Multi-URL batch crawling
   - Memory-monitored crawling
3. **Recursive Crawling**: Follows internal links to discover content
4. **Vector Search**: Performs RAG over crawled content with source filtering
5. **Code Example Extraction**: Specialized extraction and search for code snippets
6. **Knowledge Graph**: AI hallucination detection and repository analysis (optional)
7. **GraphRAG**: Combines vector search with knowledge graph traversal for better answers

## Advanced RAG Strategies
- Contextual Embeddings (enhanced semantic understanding)
- Hybrid Search (vector + keyword search)
- Agentic RAG (code example extraction)
- Reranking (cross-encoder for improved relevance)
- Knowledge Graph (hallucination detection)

## Architecture (v2.0.0 - Modular Structure)

### Core Components
- **Main entry point**: `src/server.py` (147 lines)
- **Core infrastructure**: `src/core/` directory (5 modules)
  - `lifespan.py` - Lifecycle management for MCP server
  - `context.py` - Crawl4AIContext dataclass
  - `browser_validation.py` - Playwright browser validation
  - `validators.py` - Core validation functions
  - `reranking.py` - Reranking utilities
- **MCP Tools**: `src/tools/` directory (5 category modules, 16 tools total)
  - `crawling_tools.py` - 5 crawling tools
  - `rag_tools.py` - 2 RAG query tools
  - `graphrag_tools.py` - 4 GraphRAG tools
  - `knowledge_graph_tools.py` - 4 code knowledge graph tools
  - `source_tools.py` - 1 source management tool
- **Utilities**: 20+ specialized utility modules in `src/`
  - `utils.py` - Core utilities (Supabase, embeddings)
  - `rag_utils.py` - RAG-specific functions
  - `search_utils.py` - Search strategies
  - `crawling_utils.py` - Crawling helpers
  - `github_utils.py` - GitHub batch processing
  - `memory_monitor.py` - Memory monitoring
  - `graphrag_utils.py` - GraphRAG utilities
  - `knowledge_graph_commands.py` - KG command patterns
  - (+ 12 more specialized modules)
- **Knowledge graph modules**: `knowledge_graphs/` directory
- **Docker support**: Dockerfile and docker-compose.yml
- **Configuration**: Environment-based via .env file

### Architecture Evolution
**Before (v1.x)**: Monolithic `src/crawl4ai_mcp.py` (2000+ lines, all functionality in one file)
**After (v2.0.0)**: Modular structure with clear separation:
- Infrastructure code → `src/core/`
- MCP tools → `src/tools/`
- Shared utilities → `src/` root level
- Old monolithic file archived in `src/archive/`

This refactoring improves maintainability, testability, and makes it easier to add new features.
