# Project Structure and Organization

## Directory Structure (v2.0.0 - Modular Architecture)
```
mcp-crawl4ai-rag/
├── src/                      # Main source code (modular structure)
│   ├── server.py            # Main MCP server entry point (147 lines)
│   ├── core/                # Core infrastructure modules
│   │   ├── __init__.py
│   │   ├── lifespan.py     # Lifecycle management (197 lines)
│   │   ├── context.py      # Crawl4AIContext dataclass
│   │   ├── browser_validation.py # Playwright validation
│   │   ├── validators.py   # Core validation functions
│   │   └── reranking.py    # Reranking utilities
│   ├── tools/               # MCP tool implementations (16 tools)
│   │   ├── __init__.py
│   │   ├── crawling_tools.py       # 5 crawling tools
│   │   ├── rag_tools.py            # 2 RAG query tools
│   │   ├── graphrag_tools.py       # 4 GraphRAG tools
│   │   ├── knowledge_graph_tools.py # 4 code KG tools
│   │   └── source_tools.py         # 1 source management tool
│   ├── utils.py             # Core utilities (Supabase, embeddings)
│   ├── rag_utils.py         # RAG-specific functions
│   ├── search_utils.py      # Search strategies and helpers
│   ├── crawling_utils.py    # Crawling helpers
│   ├── crawling_strategies.py # Crawling strategy pattern
│   ├── crawl_helpers.py     # Crawl helper functions
│   ├── github_utils.py      # GitHub batch processing
│   ├── memory_monitor.py    # Memory monitoring utilities
│   ├── initialization_utils.py # Startup logic
│   ├── graphrag_utils.py    # GraphRAG utilities
│   ├── knowledge_graph_commands.py # KG command patterns
│   ├── response_size_manager.py # Response size management
│   ├── timeout_utils.py     # Timeout utilities
│   ├── stdout_safety.py     # Stdout contamination prevention
│   ├── config.py            # Configuration management
│   ├── validators.py        # Input validation
│   ├── env_validators.py    # Environment validation
│   ├── error_handlers.py    # Error handling
│   ├── logging_config.py    # Logging setup
│   ├── repositories/        # Data access layer
│   │   └── (future: abstraction layer)
│   ├── services/            # Business logic layer
│   │   └── (future: service layer)
│   ├── middleware/          # Request/response middleware
│   │   └── (future: middleware)
│   └── archive/             # Archived code
│       └── crawl4ai_mcp.py.original # Old monolithic file (2000+ lines)
├── knowledge_graphs/         # Knowledge graph modules (optional feature)
│   ├── ai_hallucination_detector.py    # CLI for hallucination detection
│   ├── ai_script_analyzer.py           # AST-based Python script analyzer
│   ├── hallucination_reporter.py       # Report generation for hallucinations
│   ├── knowledge_graph_validator.py    # Validation against Neo4j graph
│   ├── parse_repo_into_neo4j.py       # GitHub repo parser to Neo4j
│   ├── query_knowledge_graph.py        # Interactive graph query tool
│   ├── document_entity_extractor.py    # GraphRAG entity extraction
│   └── document_graph_validator.py     # Graph validation
├── .env.example             # Example environment configuration
├── .gitignore              # Git ignore rules
├── crawled_pages.sql       # Supabase database schema
├── Dockerfile              # Docker container definition
├── LICENSE                 # MIT License
├── pyproject.toml          # Python project configuration
├── README.md               # Project documentation
└── uv.lock                 # Dependency lock file

## Key Components

### MCP Server Entry Point (src/server.py)
- Main entry point: 147 lines
- Initializes FastMCP server
- Registers all 16 tools from src/tools/
- Manages lifecycle with src/core/lifespan.py
- Import pattern: `from src.tools import crawling_tools, rag_tools, graphrag_tools, knowledge_graph_tools, source_tools`

### MCP Server Tools (16 Total)
**Crawling Tools (src/tools/crawling_tools.py - 5 tools)**:
1. `crawl_single_page`: Crawl single webpage
2. `smart_crawl_url`: Intelligent multi-page crawling
3. `crawl_with_stealth_mode`: Bypass bot protection
4. `crawl_with_multi_url_config`: Multi-URL crawling
5. `crawl_with_memory_monitoring`: Memory-aware crawling

**RAG Tools (src/tools/rag_tools.py - 2 tools)**:
1. `perform_rag_query`: Semantic search with RAG
2. `search_code_examples`: Code example search (requires USE_AGENTIC_RAG=true)

**GraphRAG Tools (src/tools/graphrag_tools.py - 4 tools)**:
1. `crawl_with_graph_extraction`: Crawl + entity extraction
2. `graphrag_query`: RAG with graph enrichment
3. `query_document_graph`: Cypher queries
4. `get_entity_context`: Entity neighborhood exploration

**Knowledge Graph Tools (src/tools/knowledge_graph_tools.py - 4 tools)**:
1. `parse_github_repository`: Parse repo structure to Neo4j
2. `parse_github_repositories_batch`: Batch processing
3. `check_ai_script_hallucinations`: Validate AI-generated code
4. `query_knowledge_graph`: Interactive graph query

**Source Management Tools (src/tools/source_tools.py - 1 tool)**:
1. `get_available_sources`: List crawled sources

### Utility Functions (src/utils.py)
- Supabase client management
- OpenAI embeddings generation
- Contextual embedding creation
- Document chunking and storage
- Hybrid search implementation
- Code block extraction and summarization

### Knowledge Graph Components
- **Neo4j Schema**:
  - Nodes: Repository, File, Class, Method, Function, Attribute
  - Relationships: CONTAINS, DEFINES, HAS_METHOD, HAS_ATTRIBUTE
- **Analysis Pipeline**:
  1. Parse repository with AST
  2. Extract code structure to Neo4j
  3. Validate AI scripts against graph
  4. Generate hallucination reports

## Database Schema (Supabase)

### Main Tables
1. **crawled_pages**: Stores document chunks with embeddings
   - url, chunk_number, content, embedding, metadata

2. **crawled_code_examples**: Stores extracted code examples
   - url, chunk_number, code_example, summary, embedding, metadata

3. **source_info**: Metadata about crawled sources
   - source_id, summary, total_chunks, total_word_count, last_updated

## Entry Points
- **Main server**: `src/server.py` (147 lines) - MCP server entry point
- **Server launcher**: `run_mcp.py` - Wrapper script for running the server
- **Hallucination detector**: `knowledge_graphs/ai_hallucination_detector.py`
- **Repo parser**: `knowledge_graphs/parse_repo_into_neo4j.py`
- **Graph query**: `knowledge_graphs/query_knowledge_graph.py`

## Module Import Patterns (v2.0.0)
```python
# In src/server.py
from src.core.lifespan import lifespan
from src.tools import crawling_tools
from src.tools import rag_tools
from src.tools import graphrag_tools
from src.tools import knowledge_graph_tools
from src.tools import source_tools

# Tool modules are registered dynamically:
mcp.tool()(crawling_tools.crawl_single_page)
mcp.tool()(rag_tools.perform_rag_query)
# ... etc for all 16 tools
```

## Configuration Flow
1. Load `.env` file (or use environment variables)
2. Initialize MCP server with FastMCP (in src/server.py)
3. Setup lifespan context (Crawler, Supabase, optional Neo4j) via src/core/lifespan.py
4. Register 16 tools from src/tools/ modules
5. Run server in SSE or stdio mode

## Architecture Changes (v2.0.0)
**Before (v1.x)**:
- Monolithic `src/crawl4ai_mcp.py` (2000+ lines, all tools in one file)
- All business logic mixed with tool definitions
- Difficult to maintain and test

**After (v2.0.0)**:
- Modular structure: `src/core/` + `src/tools/` + utility modules
- Clear separation: infrastructure (core), tools (tools), utilities (root)
- Main entry point reduced to 147 lines
- Tool modules organized by category (crawling, rag, graphrag, kg, source)
- 20+ utility modules for specific concerns
- Old monolithic file archived in `src/archive/crawl4ai_mcp.py.original`
