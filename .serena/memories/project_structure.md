# Project Structure and Organization

## Directory Structure
```
mcp-crawl4ai-rag/
├── src/                      # Main source code
│   ├── crawl4ai_mcp.py      # Main MCP server implementation
│   └── utils.py             # Utility functions for embeddings, DB operations
├── knowledge_graphs/         # Knowledge graph modules (optional feature)
│   ├── ai_hallucination_detector.py    # CLI for hallucination detection
│   ├── ai_script_analyzer.py           # AST-based Python script analyzer
│   ├── hallucination_reporter.py       # Report generation for hallucinations
│   ├── knowledge_graph_validator.py    # Validation against Neo4j graph
│   ├── parse_repo_into_neo4j.py       # GitHub repo parser to Neo4j
│   └── query_knowledge_graph.py        # Interactive graph query tool
├── .env.example             # Example environment configuration
├── .gitignore              # Git ignore rules
├── crawled_pages.sql       # Supabase database schema
├── Dockerfile              # Docker container definition
├── LICENSE                 # MIT License
├── pyproject.toml          # Python project configuration
├── README.md               # Project documentation
└── uv.lock                 # Dependency lock file

## Key Components

### MCP Server Tools (src/crawl4ai_mcp.py)
1. **Core Tools** (always available):
   - `crawl_single_page`: Crawl single webpage
   - `smart_crawl_url`: Intelligent multi-page crawling
   - `get_available_sources`: List crawled sources
   - `perform_rag_query`: Semantic search with RAG

2. **Conditional Tools**:
   - `search_code_examples` (requires USE_AGENTIC_RAG=true)
   - `parse_github_repository` (requires USE_KNOWLEDGE_GRAPH=true)
   - `check_ai_script_hallucinations` (requires USE_KNOWLEDGE_GRAPH=true)
   - `query_knowledge_graph` (requires USE_KNOWLEDGE_GRAPH=true)

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
- **Main server**: `src/crawl4ai_mcp.py` (runs with asyncio)
- **Hallucination detector**: `knowledge_graphs/ai_hallucination_detector.py`
- **Repo parser**: `knowledge_graphs/parse_repo_into_neo4j.py`
- **Graph query**: `knowledge_graphs/query_knowledge_graph.py`

## Configuration Flow
1. Load `.env` file (or use environment variables)
2. Initialize MCP server with FastMCP
3. Setup lifespan context (Crawler, Supabase, optional Neo4j)
4. Register tools based on configuration flags
5. Run server in SSE or stdio mode