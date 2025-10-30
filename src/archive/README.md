# Archived Files

This directory contains files that have been archived during the refactoring process.

## Files

### crawl4ai_mcp_batch.py.bak (390 lines)
- **Original Purpose:** Batch processing for GitHub repositories
- **Archived Reason:** Duplicate functionality - consolidated into `github_utils.py`
- **Date Archived:** October 17, 2025

### crawl4ai_mcp_batch_final.py.bak (329 lines)
- **Original Purpose:** Final version of batch processing
- **Archived Reason:** Duplicate functionality - consolidated into `github_utils.py`
- **Date Archived:** October 17, 2025

### crawl4ai_mcp.py.original (2,013 lines)
- **Original Purpose:** Monolithic MCP server file with all 16 tools
- **Archived Reason:** Refactored into modular architecture (Phase 2 completion)
- **Date Archived:** October 17, 2025
- **New Location:** Tools split across `src/tools/*_tools.py` modules
- **Migration Details:**
  - Crawling tools → `src/tools/crawling_tools.py` (5 tools)
  - RAG tools → `src/tools/rag_tools.py` (2 tools)
  - Knowledge graph tools → `src/tools/knowledge_graph_tools.py` (4 tools)
  - GraphRAG tools → `src/tools/graphrag_tools.py` (4 tools)
  - Source tools → `src/tools/source_tools.py` (1 tool)
  - Core components → `src/core/*.py` (context, lifespan, reranking, validators)
  - Main server → `src/server.py` (new modular entry point)

### extract_tools.py.bak (202 lines)
- **Original Purpose:** Automated tool extraction script
- **Archived Reason:** One-time use script, extraction complete
- **Date Archived:** October 17, 2025

## Notes

These files have been preserved for reference but are no longer in active use. The codebase has been successfully refactored from a monolithic 2,013-line file to a modular architecture with:

- **Core modules:** 4 files, ~280 lines total
- **Tool modules:** 5 files, ~1,740 lines total
- **Server:** 1 file, ~120 lines
- **Maximum file size:** 565 lines (down from 2,013)

All functionality has been preserved. If you need to restore any of these files or understand the migration, they are available here.
