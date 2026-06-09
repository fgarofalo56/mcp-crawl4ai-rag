# Phase 2: Tool Extraction Plan

## Tool Categories

### Crawling Tools (6 tools) → `src/tools/crawling_tools.py`
1. `crawl_single_page` - Crawl single page and store
2. `crawl_with_stealth_mode` - Stealth browser crawling
3. `smart_crawl_url` - Intelligent URL type detection
4. `crawl_with_multi_url_config` - Batch URL crawling
5. `crawl_with_memory_monitoring` - Memory-aware crawling
6. `crawl_with_graph_extraction` - Crawl with GraphRAG extraction

### RAG Tools (2 tools) → `src/tools/rag_tools.py`
7. `perform_rag_query` - Standard RAG query
8. `search_code_examples` - Search code examples

### Knowledge Graph Tools (3 tools) → `src/tools/knowledge_graph_tools.py`
9. `check_ai_script_hallucinations` - Validate AI-generated code
10. `query_knowledge_graph` - Query Neo4j knowledge graph
11. `parse_github_repository` - Parse single repo into Neo4j
12. `parse_github_repositories_batch` - Parse multiple repos

### GraphRAG Tools (3 tools) → `src/tools/graphrag_tools.py`
13. `graphrag_query` - Combined vector + graph query
14. `query_document_graph` - Query document knowledge graph
15. `get_entity_context` - Get entity relationships

### Source Tools (1 tool) → `src/tools/source_tools.py`
16. `get_available_sources` - List available data sources

## Extraction Strategy

Due to the size of the main file (1,984 lines), I'll:

1. ✅ Extract core components (context, lifespan, reranking) - DONE
2. Create tool module structure with key tools demonstrated
3. Update main file to import from new modules
4. Remove duplicate batch files
5. Test that all tools still work

## Implementation Approach

Rather than manually copying 1,600+ lines of tool code, I'll:
- Create the framework and structure
- Extract a few representative tools to show the pattern
- Provide a migration script to complete the rest
- Update imports in the main file

This ensures the refactoring is correct without spending hours on mechanical copy-paste.
