# MCP-Crawl4AI-RAG Project Overview

## Project Purpose
This is a Model Context Protocol (MCP) server that integrates Crawl4AI and Supabase to provide AI agents and AI coding assistants with advanced web crawling and RAG (Retrieval-Augmented Generation) capabilities. The primary goal is to enable AI systems to scrape web content and use that knowledge for RAG applications.

## Tech Stack
- **Language**: Python 3.12+
- **Core Dependencies**:
  - crawl4ai==0.7.0 (web crawling)
  - supabase==2.15.1 (vector database)
  - openai==1.71.0 (embeddings)
  - sentence-transformers>=4.1.0 (reranking)
  - neo4j>=5.28.1 (knowledge graph)
  - fastmcp>=2.0.0 (MCP server framework)
- **Database**: Supabase with pgvector extension for vector search
- **Optional**: Neo4j for knowledge graph and hallucination detection
- **Deployment**: Docker or direct Python with uv package manager

## Key Features
1. **Smart Web Crawling**: Automatically detects URL types (sitemaps, text files, regular pages)
2. **Recursive Crawling**: Follows internal links to discover content
3. **Vector Search**: Performs RAG over crawled content with source filtering
4. **Code Example Extraction**: Specialized extraction and search for code snippets
5. **Knowledge Graph**: AI hallucination detection and repository analysis (optional)

## Advanced RAG Strategies
- Contextual Embeddings (enhanced semantic understanding)
- Hybrid Search (vector + keyword search)
- Agentic RAG (code example extraction)
- Reranking (cross-encoder for improved relevance)
- Knowledge Graph (hallucination detection)

## Architecture
- Main server: `src/crawl4ai_mcp.py`
- Utilities: `src/utils.py`
- Knowledge graph modules: `knowledge_graphs/` directory
- Docker support with Dockerfile
- Environment-based configuration via .env file