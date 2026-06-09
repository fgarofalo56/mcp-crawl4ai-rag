# API_REFERENCE.md Correction Guide

## Summary
This document shows the exact corrections needed for `docs/API_REFERENCE.md` to match the actual implementation of the tools.

---

## Issue #1: get_available_sources - Parameter Description

### Location
Line 356 in `docs/API_REFERENCE.md`

### Current Text
```
#### Parameters

No parameters required.
```

### Corrected Text
```
#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ctx` | Context | Yes | The MCP server provided context (implicit parameter) |

Note: The `ctx` parameter is automatically provided by the MCP framework and does not need to be explicitly passed by users.
```

### Explanation
All MCP tools require the `ctx` parameter as the first argument. This is an MCP framework requirement, not a user-provided parameter. The documentation should note this for clarity.

---

## Issue #2: get_available_sources - Return Structure

### Location
Lines 360-372 in `docs/API_REFERENCE.md`

### Current Text
```json
{
  "success": true,
  "sources": [
    {
      "source_id": "docs.python.org",
      "summary": "Official Python documentation...",
      "total_words": 450000,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-20T15:45:00Z"
    }
  ],
  "count": 5
}
```

### Corrected Text
```json
{
  "sources": [
    {
      "source": "docs.python.org",
      "document_count": 150,
      "unique_urls": 100
    }
  ],
  "total_sources": 1,
  "total_documents": 150,
  "message": "Found 1 unique sources"
}
```

### Explanation
The actual implementation (verified from `src/tools/source_tools.py` lines 20-61) returns:
- `source`: Domain name (string), not `source_id`
- `document_count`: Number of documents from that domain (integer)
- `unique_urls`: Count of unique URLs from that domain (integer)
- `total_sources`: Total count of unique sources (integer)
- `total_documents`: Total count of documents across all sources (integer)
- `message`: Status message (string)

The documented fields (`source_id`, `summary`, `total_words`, `created_at`, `updated_at`) do not exist in the actual implementation.

---

## Issue #3: get_available_sources - Example Usage

### Location
Lines 375-384 in `docs/API_REFERENCE.md`

### Current Text
```python
# Get all available sources
sources = await get_available_sources(ctx)

# Use sources for filtered search
for source in sources["sources"]:
    results = await perform_rag_query(ctx, "async functions", source["source_id"])
```

### Corrected Text
```python
# Get all available sources
sources = await get_available_sources(ctx)

# Use sources for filtered search
for source in sources["sources"]:
    results = await perform_rag_query(ctx, "async functions", source["source"])
```

### Explanation
The example references `source["source_id"]` which doesn't exist. The correct field is `source["source"]` (the domain name).

---

## Issue #4: perform_rag_query - Parameter Name Consistency

### Location
Lines 395-401 in `docs/API_REFERENCE.md` and source docstring in `src/tools/rag_tools.py`

### Note
There is a minor inconsistency between the documentation and the source code docstring:
- Documentation table calls it: `source`
- Source code parameter: `source_filter`
- Source code docstring: Says `source`

### Current Documentation
```
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `source` | string | No | None | Source domain to filter results |
```

### Recommended Documentation
```
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `source_filter` | string | No | None | Source domain to filter results (e.g., 'docs.python.org') |
```

### Explanation
The documentation uses `source` but the code parameter is actually `source_filter`. Either:
1. Update documentation to use `source_filter` (preferred - matches code)
2. Update code to use `source` (breaking change)

The source code in `src/tools/rag_tools.py` line 16 shows: `source_filter: str = None`

---

## Issue #5: search_code_examples - Parameter Naming

### Location
Lines 476-482 in `docs/API_REFERENCE.md`

### Current Text
```
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query for code examples |
| `source_id` | string | No | None | Source to filter results |
```

### Issue
This is correct - the actual source code uses `source_id` as the parameter name (unlike perform_rag_query which uses `source_filter`).

### Status
✅ No change needed - documentation is accurate

---

## Summary of Required Changes

### Critical (Must Fix for Accuracy)

1. **get_available_sources - Parameter Section**
   - Change: "No parameters required" → Show ctx parameter with note
   - File: docs/API_REFERENCE.md
   - Lines: 354-356

2. **get_available_sources - Return Structure**
   - Change: Update JSON structure to match actual return values
   - File: docs/API_REFERENCE.md
   - Lines: 360-372
   - Fields to update: source, document_count, unique_urls, total_sources, total_documents, message

3. **get_available_sources - Example Usage**
   - Change: source["source_id"] → source["source"]
   - File: docs/API_REFERENCE.md
   - Line: 381

### Recommended (Better Consistency)

4. **perform_rag_query - Parameter Name**
   - Change: `source` → `source_filter` in table
   - File: docs/API_REFERENCE.md
   - Line: 398
   - Reason: Matches actual code parameter name

---

## Code Quality Issues (Not Documentation)

Note: These are issues in the source code, not documentation:

1. **Missing `import os` in src/tools/rag_tools.py**
   - Used in: perform_rag_query (line 32), search_code_examples (line 116)
   - Error: NameError: name 'os' is not defined
   - Fix: Add `import os` at top of file

2. **Missing `import sys` in src/tools/knowledge_graph_tools.py**
   - Used in: check_ai_script_hallucinations (line 52)
   - Error: NameError: name 'sys' is not defined
   - Fix: Add `import sys` at top of file

3. **Missing function implementations in src/tools/rag_tools.py**
   - Lines 42-48: Importing from `.rag_utils` (may not exist)
   - Lines 117-123: Importing from `.search_utils` (may not exist)
   - Lines 156: Importing from `.utils` (may not exist)
   - Fix: Verify imports exist or implement missing functions

---

## Validation Checklist

Before publishing corrected documentation:

- [ ] Run `grep "import os" src/tools/rag_tools.py` - should find the import
- [ ] Run `grep "import sys" src/tools/knowledge_graph_tools.py` - should find the import
- [ ] Test `get_available_sources` tool and verify return structure matches corrected docs
- [ ] Test `perform_rag_query` with the `source_filter` parameter name
- [ ] Update any examples that reference old field names
- [ ] Run all tools to ensure they execute without import errors
- [ ] Re-generate documentation if using autodoc tools

---

## Implementation Priority

**Phase 1 (Immediate)**: Fix source code imports
- Add missing `import os` statements
- Add missing `import sys` statements
- Verify all imports resolve correctly

**Phase 2 (Short-term)**: Update documentation
- Update get_available_sources return structure
- Update get_available_sources example code
- Update parameter name consistency (source vs source_filter)

**Phase 3 (Verification)**: Test and validate
- Run all tools
- Verify documentation examples work
- Test return structures match documentation
- Update CHANGELOG if needed

---

## Files to Modify

1. **docs/API_REFERENCE.md** (Corrections needed)
   - Lines 354-356: Parameter section
   - Lines 360-372: Return structure
   - Lines 375-384: Example usage
   - Lines 398: Parameter name (optional)

2. **src/tools/rag_tools.py** (Code fixes needed)
   - Top of file: Add `import os`

3. **src/tools/knowledge_graph_tools.py** (Code fixes needed)
   - Top of file: Add `import sys`

---

**Prepared**: 2025-10-28
**For**: MCP Crawl4AI RAG Server v1.2.0
**Status**: Ready for implementation
