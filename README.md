<h1 align="center">Crawl4AI RAG MCP Server</h1>

<p align="center">
  <em>Web Crawling and RAG Capabilities for AI Agents and AI Coding Assistants</em>
</p>

<p align="center">
  <a href="https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/test.yml">
    <img src="https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/test.yml/badge.svg" alt="Tests">
  </a>
  <a href="https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/lint.yml">
    <img src="https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/lint.yml/badge.svg" alt="Lint">
  </a>
  <a href="https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/docker.yml">
    <img src="https://github.com/coleam00/mcp-crawl4ai-rag/actions/workflows/docker.yml/badge.svg" alt="Docker Build">
  </a>
  <a href="https://codecov.io/gh/coleam00/mcp-crawl4ai-rag">
    <img src="https://codecov.io/gh/coleam00/mcp-crawl4ai-rag/branch/main/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://github.com/coleam00/mcp-crawl4ai-rag/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/coleam00/mcp-crawl4ai-rag" alt="License">
  </a>
  <a href="https://github.com/coleam00/mcp-crawl4ai-rag">
    <img src="https://img.shields.io/github/stars/coleam00/mcp-crawl4ai-rag?style=social" alt="GitHub stars">
  </a>
</p>

A powerful implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) integrated with [Crawl4AI](https://crawl4ai.com) and [Supabase](https://supabase.com/) for providing AI agents and AI coding assistants with advanced web crawling and RAG capabilities.

With this MCP server, you can <b>scrape anything</b> and then <b>use that knowledge anywhere</b> for RAG.

The primary goal is to bring this MCP server into [Archon](https://github.com/coleam00/Archon) as I evolve it to be more of a knowledge engine for AI coding assistants to build AI agents. This first version of the Crawl4AI/RAG MCP server will be improved upon greatly soon, especially making it more configurable so you can use different embedding models and run everything locally with Ollama.

Consider this GitHub repository a testbed, hence why I haven't been super actively address issues and pull requests yet. I certainly will though as I bring this into Archon V2!

## Overview

This MCP server provides tools that enable AI agents to crawl websites, store content in a vector database (Supabase), and perform RAG over the crawled content. It follows the best practices for building MCP servers based on the [Mem0 MCP server template](https://github.com/coleam00/mcp-mem0/) I provided on my channel previously.

The server includes several advanced RAG strategies that can be enabled to enhance retrieval quality:
- **Contextual Embeddings** for enriched semantic understanding
- **Hybrid Search** combining vector and keyword search
- **Agentic RAG** for specialized code example extraction
- **Reranking** for improved result relevance using cross-encoder models
- **Knowledge Graph** for AI hallucination detection and repository code analysis

See the [Configuration section](#configuration) below for details on how to enable and configure these strategies.

## Vision

The Crawl4AI RAG MCP server is just the beginning. Here's where we're headed:

1. **Integration with Archon**: Building this system directly into [Archon](https://github.com/coleam00/Archon) to create a comprehensive knowledge engine for AI coding assistants to build better AI agents.

2. **Multiple Embedding Models**: Expanding beyond OpenAI to support a variety of embedding models, including the ability to run everything locally with Ollama for complete control and privacy.

3. **Advanced RAG Strategies**: Implementing sophisticated retrieval techniques like contextual retrieval, late chunking, and others to move beyond basic "naive lookups" and significantly enhance the power and precision of the RAG system, especially as it integrates with Archon.

4. **Enhanced Chunking Strategy**: Implementing a Context 7-inspired chunking approach that focuses on examples and creates distinct, semantically meaningful sections for each chunk, improving retrieval precision.

5. **Performance Optimization**: Increasing crawling and indexing speed to make it more realistic to "quickly" index new documentation to then leverage it within the same prompt in an AI coding assistant.

## Features

- **Smart URL Detection**: Automatically detects and handles different URL types (regular webpages, sitemaps, text files)
- **Recursive Crawling**: Follows internal links to discover content
- **Parallel Processing**: Efficiently crawls multiple pages simultaneously
- **Content Chunking**: Intelligently splits content by headers and size for better processing
- **Vector Search**: Performs RAG over crawled content, optionally filtering by data source for precision
- **Source Retrieval**: Retrieve sources available for filtering to guide the RAG process
- **🆕 Stealth Mode**: Bypass bot detection (Cloudflare, Akamai) with undetected browser technology
- **🆕 Smart Multi-URL Config**: Automatically optimize crawler settings based on content type
- **🆕 Memory Monitoring**: Track and control memory usage during large-scale crawls

## Tools

The server provides essential web crawling and search tools:

### Core Tools (Always Available)

1. **`crawl_single_page`**: Quickly crawl a single web page and store its content in the vector database
2. **`smart_crawl_url`**: Intelligently crawl a full website based on the type of URL provided (sitemap, llms-full.txt, or a regular webpage that needs to be crawled recursively)
3. **`get_available_sources`**: Get a list of all available sources (domains) in the database
4. **`perform_rag_query`**: Search for relevant content using semantic search with optional source filtering

### Advanced Crawling Tools 🆕

5. **`crawl_with_stealth_mode`**: Crawl protected sites using undetected browser to bypass Cloudflare, Akamai, and other bot detection
6. **`crawl_with_multi_url_config`**: Crawl multiple URLs with automatic per-URL optimization based on content type (docs, articles, general)
7. **`crawl_with_memory_monitoring`**: Crawl with active memory monitoring and adaptive throttling for large-scale operations

### Conditional Tools

5. **`search_code_examples`** (requires `USE_AGENTIC_RAG=true`): Search specifically for code examples and their summaries from crawled documentation. This tool provides targeted code snippet retrieval for AI coding assistants.

### Knowledge Graph Tools (requires `USE_KNOWLEDGE_GRAPH=true`, see below)

8. **`parse_github_repository`**: Parse a GitHub repository into a Neo4j knowledge graph, extracting classes, methods, functions, and their relationships for hallucination detection
9. **`parse_github_repositories_batch`** 🆕: Parse multiple GitHub repositories in parallel with intelligent retry logic, progress tracking, and aggregate statistics
10. **`check_ai_script_hallucinations`**: Analyze Python scripts for AI hallucinations by validating imports, method calls, and class usage against the knowledge graph
11. **`query_knowledge_graph`**: Explore and query the Neo4j knowledge graph with commands like `repos`, `classes`, `methods`, and custom Cypher queries
12. **`crawl_with_graph_extraction`** 🆕: Crawl URLs and build knowledge graphs from content (GraphRAG)
13. **`graphrag_query`** 🆕: RAG queries with optional graph enrichment for richer context
14. **`query_document_graph`** 🆕: Execute Cypher queries on document knowledge graph
15. **`get_entity_context`** 🆕: Explore entity neighborhoods and relationships

> **Total: 16 MCP Tools** - See [API Reference](API_REFERENCE.md) for detailed documentation

## 🚀 What's New in v1.2.0 - GraphRAG

### Graph-Augmented RAG for Web Content

**GraphRAG** extends traditional vector RAG with knowledge graph capabilities:

```
Traditional RAG:    Query → Vector Search → Documents → LLM → Answer
GraphRAG:          Query → [Vector + Graph] → Enriched Context → LLM → Better Answer
```

**4 New Tools:**

1. **`crawl_with_graph_extraction`** - Build knowledge graphs from web pages
   ```
   Extracts: Entities (FastAPI, OAuth2, Docker) + Relationships (REQUIRES, USES, PART_OF)
   Stores: Vector embeddings (Supabase) + Knowledge graph (Neo4j)
   Use when: Need structured understanding of entity relationships
   ```

2. **`graphrag_query`** - Graph-enriched question answering
   ```
   Adds: Entity relationships, dependencies, multi-hop reasoning
   Best for: "How do X and Y relate?", prerequisite questions, complex procedures
   Trade-off: ~2-3x slower but significantly better answers
   ```

3. **`query_document_graph`** - Direct Cypher queries
   ```cypher
   MATCH (t:Technology)-[r:REQUIRES]->(dep)
   RETURN t.name, dep.name, r.description
   ```

4. **`get_entity_context`** - Explore entity neighborhoods
   ```
   Input: "FastAPI"
   Output: Related technologies, dependencies, documents, relationship graph
   ```

**When to Use GraphRAG:**
- ✅ Technical documentation with interconnected concepts
- ✅ Questions about dependencies or how things relate
- ✅ Multi-step procedures requiring context
- ❌ Simple factual lookups (use regular RAG for speed)

**Setup:**
```bash
# Enable in .env
USE_GRAPHRAG=true
NEO4J_URI=bolt://localhost:7687
OPENAI_API_KEY=sk-...  # For entity extraction

# Crawl with graph extraction
crawl_with_graph_extraction("https://fastapi.tiangolo.com/")

# Query with graph enrichment
graphrag_query("How to implement OAuth2 in FastAPI?", use_graph_enrichment=True)
```

📖 **Full Guide:** [docs/GRAPHRAG_GUIDE.md](docs/GRAPHRAG_GUIDE.md)

## 🆕 What's New in v1.1.1

### Critical Bug Fixes & New Batch Processing

1. **Batch GitHub Repository Processing** - Process multiple repositories efficiently
   ```
   Use when: Building comprehensive knowledge graphs from multiple repos
   Features: Parallel processing, automatic retries, detailed error tracking
   Example: Parse all repos in an organization simultaneously
   ```

2. **Foreign Key Constraint Fixes** - Fixed database insertion errors
   ```
   Fixed: Source creation now happens before document insertion
   Affected: crawl_with_multi_url_config, crawl_with_stealth_mode, crawl_with_memory_monitoring
   ```

3. **Health Check Endpoint** - Added `/health` endpoint for monitoring
   ```
   Use when: Running in Docker, Kubernetes, or behind load balancers
   Returns: Service status, version, and transport information
   ```

## What's New in v1.1.0

### Three Powerful New Features

1. **Stealth Mode Crawling** - Bypass Cloudflare and bot detection
   ```
   Use when: Sites block regular crawlers, need to appear as human user
   Example: Crawl protected documentation or e-commerce sites
   ```

2. **Smart Multi-URL Configuration** - Optimize settings per content type
   ```
   Use when: Crawling multiple domains with different content types
   Example: Batch crawl docs, blogs, and news sites with auto-optimization
   ```

3. **Memory-Monitored Crawling** - Prevent memory exhaustion on large crawls
   ```
   Use when: Large-scale operations (1000+ pages), long-running jobs
   Example: Crawl entire documentation sites with memory tracking
   ```

**📖 Full Guide**: See [New Features Guide](docs/NEW_FEATURES_GUIDE.md) for detailed examples, parameters, and best practices.

**Quick Examples**:
```python
# Bypass Cloudflare protection
crawl_with_stealth_mode("https://protected-site.com", extra_wait=3)

# Batch crawl with optimization
crawl_with_multi_url_config('["https://docs.python.org", "https://fastapi.tiangolo.com"]')

# Large-scale with memory monitoring
crawl_with_memory_monitoring("https://docs.example.com/sitemap.xml", memory_threshold_mb=400)
```

## Quick Start for Claude Desktop

If you're looking to connect this server to Claude Desktop, check out our **[Claude Desktop Setup Guide](CLAUDE_DESKTOP_SETUP.md)** for step-by-step instructions.

## Prerequisites

- [Docker/Docker Desktop](https://www.docker.com/products/docker-desktop/) if running the MCP server as a container (recommended)
- [Python 3.12+](https://www.python.org/downloads/) if running the MCP server directly through uv
- [Supabase](https://supabase.com/) (database for RAG)
- [OpenAI API key](https://platform.openai.com/api-keys) (for generating embeddings)
- [Neo4j](https://neo4j.com/) (optional, for knowledge graph functionality) - see [Knowledge Graph Setup](#knowledge-graph-setup) section

## Installation

### Using Docker Compose (Recommended for Neo4j Support)

**Best for running with Neo4j knowledge graph!** Everything runs together with automatic networking.

1. Clone this repository:
   ```bash
   git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
   cd mcp-crawl4ai-rag
   ```

2. Create your environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

3. Start everything with Docker Compose:
   ```bash
   # Start MCP server + Neo4j

   # Using the powershell script (Windows)
   .\scripts\run_docker.ps1
   
   # Or manually:
   docker-compose --env-file .env.docker up -d --build
   docker-compose up -d

   # View logs
   docker-compose logs -f
   ```

**See the comprehensive [Docker Setup Guide](docs/DOCKER_SETUP.md) for:**
- Full configuration instructions with Neo4j networking
- Troubleshooting connection issues
- Production deployment tips

### Using Docker (Without Compose)

1. Clone this repository:
   ```bash
   git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
   cd mcp-crawl4ai-rag
   ```

2. Build the Docker image:
   ```bash
   docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .
   ```

3. Create `.env` file and configure Neo4j connection:
   - For Neo4j on host: Set `NEO4J_URI=bolt://host.docker.internal:7687`
   - For cloud Neo4j: Set `NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io`
   - See [Docker Setup Guide](docs/DOCKER_SETUP.md) for full details

### Using uv directly (no Docker)

1. Clone this repository:
   ```bash
   git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
   cd mcp-crawl4ai-rag
   ```

2. Install uv if you don't have it:
   ```bash
   pip install uv
   ```

3. Create and activate a virtual environment:
   ```bash
   uv venv
   .venv\Scripts\activate
   # on Mac/Linux: source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   uv pip install -e . --link-mode=copy
   crawl4ai-setup
   ```

5. Create a `.env` file based on the configuration section below

## Database Setup

Before running the server, you need to set up the database with the pgvector extension:

1. Go to the SQL Editor in your Supabase dashboard (create a new project first if necessary)

2. Create a new query and paste the contents of `crawled_pages.sql`

3. Run the query to create the necessary tables and functions

## Knowledge Graph Setup (Optional)

To enable AI hallucination detection and repository analysis features, you need to set up Neo4j.

**✅ Docker Support Now Available!** The knowledge graph is now fully compatible with Docker. You can run the MCP server with Neo4j using:
- **Docker Compose** (recommended): Everything runs together with automatic networking - see [Docker Setup Guide](docs/DOCKER_SETUP.md)
- **Docker + Host Neo4j**: MCP server in Docker connecting to Neo4j on your machine
- **Local with uv**: Both running directly on your machine (original method)

For installing Neo4j:

### Local AI Package (Recommended)

The easiest way to get Neo4j running locally is with the [Local AI Package](https://github.com/coleam00/local-ai-packaged) - a curated collection of local AI services including Neo4j:

1. **Clone the Local AI Package**:
   ```bash
   git clone https://github.com/coleam00/local-ai-packaged.git
   cd local-ai-packaged
   ```

2. **Start Neo4j**:
   Follow the instructions in the Local AI Package repository to start Neo4j with Docker Compose

3. **Default connection details**:
   - URI: `bolt://localhost:7687`
   - Username: `neo4j`
   - Password: Check the Local AI Package documentation for the default password

### Manual Neo4j Installation

Alternatively, install Neo4j directly:

1. **Install Neo4j Desktop**: Download from [neo4j.com/download](https://neo4j.com/download/)

2. **Create a new database**:
   - Open Neo4j Desktop
   - Create a new project and database
   - Set a password for the `neo4j` user
   - Start the database

3. **Note your connection details**:
   - URI: `bolt://localhost:7687` (default)
   - Username: `neo4j` (default)
   - Password: Whatever you set during creation

## Configuration

Create a `.env` file in the project root with the following variables:

```
# MCP Server Configuration
HOST=0.0.0.0
PORT=8051
TRANSPORT=sse

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key

# LLM for summaries and contextual embeddings
MODEL_CHOICE=gpt-4.1-nano

# RAG Strategies (set to "true" or "false", default to "false")
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false
USE_KNOWLEDGE_GRAPH=false

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Neo4j Configuration (required for knowledge graph functionality)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### RAG Strategy Options

The Crawl4AI RAG MCP server supports four powerful RAG strategies that can be enabled independently:

#### 1. **USE_CONTEXTUAL_EMBEDDINGS**
When enabled, this strategy enhances each chunk's embedding with additional context from the entire document. The system passes both the full document and the specific chunk to an LLM (configured via `MODEL_CHOICE`) to generate enriched context that gets embedded alongside the chunk content.

- **When to use**: Enable this when you need high-precision retrieval where context matters, such as technical documentation where terms might have different meanings in different sections.
- **Trade-offs**: Slower indexing due to LLM calls for each chunk, but significantly better retrieval accuracy.
- **Cost**: Additional LLM API calls during indexing.

#### 2. **USE_HYBRID_SEARCH**
Combines traditional keyword search with semantic vector search to provide more comprehensive results. The system performs both searches in parallel and intelligently merges results, prioritizing documents that appear in both result sets.

- **When to use**: Enable this when users might search using specific technical terms, function names, or when exact keyword matches are important alongside semantic understanding.
- **Trade-offs**: Slightly slower search queries but more robust results, especially for technical content.
- **Cost**: No additional API costs, just computational overhead.

#### 3. **USE_AGENTIC_RAG**
Enables specialized code example extraction and storage. When crawling documentation, the system identifies code blocks (≥300 characters), extracts them with surrounding context, generates summaries, and stores them in a separate vector database table specifically designed for code search.

- **When to use**: Essential for AI coding assistants that need to find specific code examples, implementation patterns, or usage examples from documentation.
- **Trade-offs**: Significantly slower crawling due to code extraction and summarization, requires more storage space.
- **Cost**: Additional LLM API calls for summarizing each code example.
- **Benefits**: Provides a dedicated `search_code_examples` tool that AI agents can use to find specific code implementations.

#### 4. **USE_RERANKING**
Applies cross-encoder reranking to search results after initial retrieval. Uses a lightweight cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to score each result against the original query, then reorders results by relevance.

- **When to use**: Enable this when search precision is critical and you need the most relevant results at the top. Particularly useful for complex queries where semantic similarity alone might not capture query intent.
- **Trade-offs**: Adds ~100-200ms to search queries depending on result count, but significantly improves result ordering.
- **Cost**: No additional API costs - uses a local model that runs on CPU.
- **Benefits**: Better result relevance, especially for complex queries. Works with both regular RAG search and code example search.

#### 5. **USE_KNOWLEDGE_GRAPH**
Enables AI hallucination detection and repository analysis using Neo4j knowledge graphs. When enabled, the system can parse GitHub repositories into a graph database and validate AI-generated code against real repository structures. **✅ Now fully compatible with Docker** - see [Docker Setup Guide](docs/DOCKER_SETUP.md)

- **When to use**: Enable this for AI coding assistants that need to validate generated code against real implementations, or when you want to detect when AI models hallucinate non-existent methods, classes, or incorrect usage patterns.
- **Trade-offs**: Requires Neo4j setup and additional dependencies. Repository parsing can be slow for large codebases, and validation requires repositories to be pre-indexed.
- **Cost**: No additional API costs for validation, but requires Neo4j infrastructure (can use free local installation or cloud AuraDB).
- **Benefits**: Provides three powerful tools: `parse_github_repository` for indexing codebases, `check_ai_script_hallucinations` for validating AI-generated code, and `query_knowledge_graph` for exploring indexed repositories.

You can now tell the AI coding assistant to add a Python GitHub repository to the knowledge graph like:

"Add https://github.com/pydantic/pydantic-ai.git to the knowledge graph"

Make sure the repo URL ends with .git.

You can also have the AI coding assistant check for hallucinations with scripts it just created, or you can manually run the command:

```
python knowledge_graphs/ai_hallucination_detector.py [full path to your script to analyze]
```

### Recommended Configurations

**For general documentation RAG:**
```
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=false
USE_RERANKING=true
```

**For AI coding assistant with code examples:**
```
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
USE_KNOWLEDGE_GRAPH=false
```

**For AI coding assistant with hallucination detection:**
```
USE_CONTEXTUAL_EMBEDDINGS=true
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=true
USE_RERANKING=true
USE_KNOWLEDGE_GRAPH=true
```

**For fast, basic RAG:**
```
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=true
USE_AGENTIC_RAG=false
USE_RERANKING=false
USE_KNOWLEDGE_GRAPH=false
```

## Running the Server

### Quick Start with Wrapper Scripts

The easiest way to run the server is using the provided wrapper scripts that automatically load your `.env` file:

**Windows:**
```bash
run_mcp.bat
```

**Mac/Linux:**
```bash
chmod +x run_mcp.sh  # Make executable (first time only)
./run_mcp.sh
```

**Python (cross-platform):**
```bash
python run_mcp.py
```

### Using Docker

```bash
docker run -d --env-file .env -p 8051:8051 mcp/crawl4ai-rag

docker run -d --env-file .env -p 8051:8051 --restart unless-stopped mcp/crawl4ai-rag

docker update --restart unless-stopped <container_name_or_id>
```

### Using Python Directly

```bash
uv run src/crawl4ai_mcp.py
```

The server will start and listen on the configured host and port.

## Integration with MCP Clients

### Claude Desktop Setup (Recommended)

For detailed instructions on connecting this server to Claude Desktop, see our **[Claude Desktop Setup Guide](CLAUDE_DESKTOP_SETUP.md)**.

The guide covers:
- Step-by-step configuration
- Using the wrapper script for automatic `.env` loading
- Troubleshooting common issues
- Platform-specific instructions

**Quick Config for Claude Desktop:**
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-crawl4ai-rag",
        "python",
        "run_mcp.py"
      ]
    }
  }
}
```

### SSE Configuration

Once you have the server running with SSE transport, you can connect to it using this configuration:

```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "transport": "sse",
      "url": "http://localhost:8051/sse"
    }
  }
}
```

> **Note for Windsurf users**: Use `serverUrl` instead of `url` in your configuration:
> ```json
> {
>   "mcpServers": {
>     "crawl4ai-rag": {
>       "transport": "sse",
>       "serverUrl": "http://localhost:8051/sse"
>     }
>   }
> }
> ```
>
> **Note for Docker users**: Use `host.docker.internal` instead of `localhost` if your client is running in a different container. This will apply if you are using this MCP server within n8n!

> **Note for Claude Code users**: 
```
claude mcp add-json crawl4ai-rag '{"type":"http","url":"http://localhost:8051/sse"}' --scope user
```

### Stdio Configuration

Add this server to your MCP configuration for Claude Desktop, Windsurf, or any other MCP client:

```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "python",
      "args": ["path/to/crawl4ai-mcp/src/crawl4ai_mcp.py"],
      "env": {
        "TRANSPORT": "stdio",
        "OPENAI_API_KEY": "your_openai_api_key",
        "SUPABASE_URL": "your_supabase_url",
        "SUPABASE_SERVICE_KEY": "your_supabase_service_key",
        "USE_KNOWLEDGE_GRAPH": "false",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_neo4j_password"
      }
    }
  }
}
```

### Docker with Stdio Configuration

```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT", 
               "-e", "OPENAI_API_KEY", 
               "-e", "SUPABASE_URL", 
               "-e", "SUPABASE_SERVICE_KEY",
               "-e", "USE_KNOWLEDGE_GRAPH",
               "-e", "NEO4J_URI",
               "-e", "NEO4J_USER",
               "-e", "NEO4J_PASSWORD",
               "mcp/crawl4ai"],
      "env": {
        "TRANSPORT": "stdio",
        "OPENAI_API_KEY": "your_openai_api_key",
        "SUPABASE_URL": "your_supabase_url",
        "SUPABASE_SERVICE_KEY": "your_supabase_service_key",
        "USE_KNOWLEDGE_GRAPH": "false",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_neo4j_password"
      }
    }
  }
}
```

## Knowledge Graph Architecture

The knowledge graph system stores repository code structure in Neo4j with the following components:

### Core Components (`knowledge_graphs/` folder):

- **`parse_repo_into_neo4j.py`**: Clones and analyzes GitHub repositories, extracting Python classes, methods, functions, and imports into Neo4j nodes and relationships
- **`ai_script_analyzer.py`**: Parses Python scripts using AST to extract imports, class instantiations, method calls, and function usage
- **`knowledge_graph_validator.py`**: Validates AI-generated code against the knowledge graph to detect hallucinations (non-existent methods, incorrect parameters, etc.)
- **`hallucination_reporter.py`**: Generates comprehensive reports about detected hallucinations with confidence scores and recommendations
- **`query_knowledge_graph.py`**: Interactive CLI tool for exploring the knowledge graph (functionality now integrated into MCP tools)

### Knowledge Graph Schema:

The Neo4j database stores code structure as:

**Nodes:**
- `Repository`: GitHub repositories
- `File`: Python files within repositories  
- `Class`: Python classes with methods and attributes
- `Method`: Class methods with parameter information
- `Function`: Standalone functions
- `Attribute`: Class attributes

**Relationships:**
- `Repository` -[:CONTAINS]-> `File`
- `File` -[:DEFINES]-> `Class`
- `File` -[:DEFINES]-> `Function`
- `Class` -[:HAS_METHOD]-> `Method`
- `Class` -[:HAS_ATTRIBUTE]-> `Attribute`

### Workflow:

1. **Repository Parsing**: Use `parse_github_repository` tool to clone and analyze open-source repositories
2. **Code Validation**: Use `check_ai_script_hallucinations` tool to validate AI-generated Python scripts
3. **Knowledge Exploration**: Use `query_knowledge_graph` tool to explore available repositories, classes, and methods

## Building Your Own Server

This implementation provides a foundation for building more complex MCP servers with web crawling capabilities. To build your own:

1. Add your own tools by creating methods with the `@mcp.tool()` decorator
2. Create your own lifespan function to add your own dependencies
3. Modify the `utils.py` file for any helper functions you need
4. Extend the crawling capabilities by adding more specialized crawlers


## 📚 Documentation

For comprehensive guides, setup instructions, and troubleshooting:

- **[API Reference](API_REFERENCE.md)** - Complete documentation for all 16 MCP tools
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Documentation Index](docs/README.md)** - Complete documentation hub
- **[Quick Start Guide](docs/QUICK_START.md)** - Developer quick reference
- **[Code Quality Guide](docs/CODE_QUALITY_IMPROVEMENTS.md)** - Development best practices
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Links

- [Claude Desktop Setup](docs/CLAUDE_DESKTOP_SETUP.md)
- [Docker Setup with Neo4j](docs/DOCKER_SETUP.md) - **NEW!** Complete guide for Docker + Neo4j
- [Dual Mode Configuration](docs/DUAL_MODE_SETUP.md) (stdio + HTTP)
- [Neo4j Configuration](docs/NEO4J_FIX.md)
- [Developer Quick Start](docs/QUICK_START.md)
- [New Features Guide v1.1.0](docs/NEW_FEATURES_GUIDE.md)

## 📁 Project Structure

```plaintext
mcp-crawl4ai-rag/
├── docs/                    # 📚 All documentation
│   ├── README.md            # Documentation index
│   ├── QUICK_START.md       # Developer quick reference
│   ├── archive/             # Historical documentation
│   └── ...                  # Additional guides
├── scripts/                 # 🔧 Utility scripts
│   ├── run_docker.ps1       # Docker startup script
│   ├── update_dependencies.ps1
│   └── setup_vscode_python.ps1
├── src/                     # 💻 Source code
│   ├── config.py            # Configuration management
│   ├── logging_config.py    # Logging utilities
│   ├── error_handlers.py    # Error handling
│   ├── validators.py        # Input validation
│   └── crawl4ai_mcp.py      # Main MCP server
├── tests/                   # ✅ Test suite (64 tests, 90%+ coverage)
├── knowledge_graphs/        # 🧠 Knowledge graph tools
├── run_mcp.py              # Server entry point
├── .env.example             # Environment template
└── README.md               # This file
```

## 🚀 Scripts

All utility scripts are now organized in the `scripts/` folder:

- **`scripts/run_docker.ps1`** - Start MCP server in Docker with HTTP transport
- **`scripts/update_dependencies.ps1`** - Update Python dependencies
- **`scripts/setup_vscode_python.ps1`** - Configure VS Code for Python development

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code of conduct
- Development setup with uv
- Code style and testing requirements
- Pull request process
- Issue reporting guidelines

Quick start for contributors:
```bash
git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
cd mcp-crawl4ai-rag
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
pytest tests/ -v
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and releases.

### Recent Releases

- **v1.1.0** (Current) - Added stealth mode, multi-URL config, and memory monitoring
- **v1.0.0** - Knowledge graph integration with Neo4j for hallucination detection
- **v0.9.0** - Initial MCP server with core crawling and RAG capabilities

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
