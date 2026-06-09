# Implementation Action Plan - Documentation Fixes

**Created**: October 28, 2025
**For**: MCP Crawl4AI RAG Server v1.2.0
**Estimated Completion**: 2 hours including testing

---

## Overview

This document provides step-by-step implementation instructions for fixing all documented issues from the API reference validation.

---

## PHASE 1: CRITICAL FIXES (30 minutes)

These fixes must be completed first as they affect tool functionality and documentation accuracy.

### Fix 1.1: Add Missing Import to rag_tools.py

**File**: `src/tools/rag_tools.py`

**Action**: Add missing `import os` statement

**Steps**:
1. Open file: `src/tools/rag_tools.py`
2. Locate the imports section (should be around line 1-10)
3. Find where other imports are (should see `from fastmcp import Context`, `from typing import ...`, `import json`)
4. Add new line with: `import os`

**Before** (lines 1-12):
```python
"""
RAG Tools

MCP tools for Retrieval Augmented Generation queries and code search.
"""

from fastmcp import Context
from typing import Optional, List, Dict, Any
import json

from core import Crawl4AIContext, rerank_results
from utils import (
```

**After** (lines 1-13):
```python
"""
RAG Tools

MCP tools for Retrieval Augmented Generation queries and code search.
"""

from fastmcp import Context
from typing import Optional, List, Dict, Any
import json
import os

from core import Crawl4AIContext, rerank_results
from utils import (
```

**Verification**:
```bash
grep "import os" src/tools/rag_tools.py
# Should output: import os
```

**Why**: The file uses `os.getenv()` in two functions (perform_rag_query and search_code_examples) on lines 32, 116, 152, 180.

---

### Fix 1.2: Add Missing Import to knowledge_graph_tools.py

**File**: `src/tools/knowledge_graph_tools.py`

**Action**: Add missing `import sys` statement

**Steps**:
1. Open file: `src/tools/knowledge_graph_tools.py`
2. Locate the imports section (should be around line 1-15)
3. Find other imports
4. Add new line with: `import sys`

**Before** (lines 1-15):
```python
"""
Knowledge Graph Tools

MCP tools for Neo4j knowledge graph operations including repository parsing
and AI hallucination detection.
"""

from fastmcp import Context
from typing import Optional, Dict, Any, List
import json
import os

from core import (
```

**After** (lines 1-16):
```python
"""
Knowledge Graph Tools

MCP tools for Neo4j knowledge graph operations including repository parsing
and AI hallucination detection.
"""

from fastmcp import Context
from typing import Optional, Dict, Any, List
import json
import os
import sys

from core import (
```

**Verification**:
```bash
grep "import sys" src/tools/knowledge_graph_tools.py
# Should output: import sys
```

**Why**: The file uses `sys.stderr` in the check_ai_script_hallucinations function on lines 52, 65, etc.

---

### Fix 1.3: Update get_available_sources Documentation - Parameters

**File**: `docs/API_REFERENCE.md`

**Action**: Update parameters section for get_available_sources tool

**Locate**: Search for `### get_available_sources` (should be around line 350)

**Current Section** (lines 354-356):
```markdown
#### Parameters

No parameters required.
```

**Replace With**:
```markdown
#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | Context | Yes | The MCP server provided context (implicit in MCP framework) |

Note: The `ctx` parameter is automatically provided by the MCP framework and does not need to be explicitly passed by users.
```

**Why**: All MCP tools require the `ctx` parameter. Documentation should reflect this for clarity.

---

### Fix 1.4: Update get_available_sources Documentation - Return Structure

**File**: `docs/API_REFERENCE.md`

**Action**: Update return structure for get_available_sources tool

**Locate**: Search for `### get_available_sources` return section (should be around line 358-372)

**Current Section** (lines 360-372):
```markdown
#### Returns

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
```

**Replace With**:
```markdown
#### Returns

JSON object containing available sources and statistics:

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

**Response Fields**:
- `sources`: Array of available sources
  - `source`: Domain/source name (string)
  - `document_count`: Number of documents from this source (integer)
  - `unique_urls`: Number of unique URLs from this source (integer)
- `total_sources`: Total count of unique sources (integer)
- `total_documents`: Total documents across all sources (integer)
- `message`: Status message (string)
```

**Why**: This matches the actual implementation in `src/tools/source_tools.py` lines 20-61.

---

### Fix 1.5: Update get_available_sources Documentation - Example

**File**: `docs/API_REFERENCE.md`

**Action**: Fix example code for get_available_sources

**Locate**: Example usage section under get_available_sources (should be around line 375-384)

**Current Example**:
```python
# Get all available sources
sources = await get_available_sources(ctx)

# Use sources for filtered search
for source in sources["sources"]:
    results = await perform_rag_query(ctx, "async functions", source["source_id"])
```

**Replace With**:
```python
# Get all available sources
sources = await get_available_sources(ctx)

# Check available sources
print(f"Found {sources['total_sources']} sources with {sources['total_documents']} total documents")

# Use sources for filtered search
for source in sources["sources"]:
    results = await perform_rag_query(ctx, "async functions", source["source"])
```

**Key Change**: `source["source_id"]` → `source["source"]`

**Why**: The actual field name is `source`, not `source_id`.

---

## PHASE 2: HIGH PRIORITY FIXES (20 minutes)

These fixes improve consistency and prevent user errors.

### Fix 2.1: Update perform_rag_query Parameter Documentation

**File**: `docs/API_REFERENCE.md`

**Action**: Update parameter name for perform_rag_query

**Locate**: perform_rag_query parameters section (should be around line 395-401)

**Current Section**:
```markdown
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `source` | string | No | None | Source domain to filter results |
```

**Replace With**:
```markdown
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `source_filter` | string | No | None | Source domain to filter results (e.g., 'docs.python.org') |
```

**Why**: The actual parameter name in the code is `source_filter`, not `source`.

---

### Fix 2.2: Verify Missing Module Imports

**File**: Multiple source files

**Action**: Check if referenced modules exist

**Verification Steps**:

1. **Check for rag_utils.py**:
   ```bash
   ls -la src/tools/rag_utils.py
   # or
   find . -name "rag_utils.py" -type f
   ```

2. **Check for search_utils.py**:
   ```bash
   ls -la src/tools/search_utils.py
   # or
   find . -name "search_utils.py" -type f
   ```

3. **If files exist**: No action needed
4. **If files don't exist**: EITHER
   - Option A: Create the missing modules with required functions
   - Option B: Update imports in rag_tools.py to correct locations
   - Option C: Remove unused imports and implement functions inline

**Functions being imported from missing modules** (from rag_tools.py lines 42-48):
```python
perform_hybrid_search_for_documents
format_rag_results
build_rag_response
build_rag_error_response
```

**Functions being imported from missing modules** (from rag_tools.py lines 117-123):
```python
check_code_examples_enabled
prepare_source_filter
perform_hybrid_search
execute_vector_search
format_search_results
build_search_response
build_error_response
```

**Severity Note**: This is a code quality issue. If the functions don't exist elsewhere, the code will fail at runtime.

---

## PHASE 3: MEDIUM PRIORITY IMPROVEMENTS (45 minutes)

These improvements enhance documentation quality and user experience.

### Fix 3.1: Add Error Response Examples to Crawling Tools

**File**: `docs/API_REFERENCE.md`

**Action**: Add error response examples to all crawling tools

**Tools to Update**:
1. crawl_single_page
2. crawl_with_stealth_mode
3. smart_crawl_url
4. crawl_with_multi_url_config
5. crawl_with_memory_monitoring

**For each tool, locate the "Returns" section and add after the success example**:

```markdown
#### Error Response Example

```json
{
  "success": false,
  "url": "https://example.com",
  "error": "Connection timeout after 30 seconds"
}
```

Common errors:
- Network timeouts
- Invalid URLs
- Authentication required
- Bot detection blocking access
- Server errors (5xx)
```

**Example for crawl_single_page** (insert after current Returns section, around line 47-60):

```markdown
#### Error Response Example

```json
{
  "success": false,
  "url": "https://example.com",
  "error": "Failed to crawl: Connection refused"
}
```
```

**Why**: Users need to understand error cases.

---

### Fix 3.2: Add Parameter Interaction Notes

**File**: `docs/API_REFERENCE.md`

**Action**: Add notes about parameter relationships

**Tool 1: crawl_with_memory_monitoring** (insert after Parameters table, around line 405):

```markdown
#### Parameter Interactions

- **max_concurrent and memory_threshold_mb**: When memory usage exceeds `memory_threshold_mb`, the `max_concurrent` value is automatically reduced to prevent out-of-memory errors. The actual concurrency may be lower than specified.
- **max_depth and max_concurrent**: Higher depth values require exponentially more memory. Consider reducing `max_concurrent` when using `max_depth > 4`.

#### Memory Monitoring

The tool actively monitors memory usage and adjusts behavior automatically:
1. Tracks peak memory usage
2. Compares against `memory_threshold_mb`
3. Reduces concurrency if threshold is approached
4. Reports final memory statistics in response
```

**Tool 2: crawl_with_stealth_mode** (insert after Parameters table, around line 165):

```markdown
#### Performance Notes

- Stealth mode is 2-3x slower than regular crawling
- `wait_for_selector` adds latency: Use only when necessary
- `extra_wait`: Increase if dynamic content isn't loaded (typical: 2-5 seconds)
- Not all bot detection systems can be bypassed - test before production use
```

**Why**: Helps users understand parameter relationships and choose optimal values.

---

## PHASE 4: TESTING & VERIFICATION (30 minutes)

### Test Step 1: Verify Source Code Imports

```bash
# Test 1.1: Check rag_tools.py imports
python -c "from src.tools.rag_tools import perform_rag_query, search_code_examples; print('✓ rag_tools imports OK')"

# Test 1.2: Check knowledge_graph_tools.py imports
python -c "from src.tools.knowledge_graph_tools import check_ai_script_hallucinations; print('✓ knowledge_graph_tools imports OK')"

# Expected output:
# ✓ rag_tools imports OK
# ✓ knowledge_graph_tools imports OK
```

### Test Step 2: Verify get_available_sources Functionality

```python
# Run this Python test after fixing the code
import asyncio
from src.tools.source_tools import get_available_sources
from fastmcp import Context

# Create mock context if needed
async def test():
    try:
        result = await get_available_sources(None)  # May fail if no real context
        print("Response structure:")
        print(result)

        # Parse JSON
        import json
        data = json.loads(result)

        # Verify fields
        assert "sources" in data, "Missing 'sources' field"
        assert "total_sources" in data, "Missing 'total_sources' field"
        assert "total_documents" in data, "Missing 'total_documents' field"

        # Verify source structure
        if data["sources"]:
            source = data["sources"][0]
            assert "source" in source, "Missing 'source' field in source object"
            assert "document_count" in source, "Missing 'document_count' field"
            assert "unique_urls" in source, "Missing 'unique_urls' field"

            # Verify old fields are gone
            assert "source_id" not in source, "Old field 'source_id' still present"
            assert "summary" not in source, "Old field 'summary' still present"

        print("✓ All assertions passed")

    except Exception as e:
        print(f"✗ Test failed: {e}")

# asyncio.run(test())
```

### Test Step 3: Validate Documentation Examples

```python
# Test that example code from documentation works
async def test_examples():
    # From get_available_sources example
    sources = {"sources": [{"source": "example.com", "document_count": 10}], "total_sources": 1, "total_documents": 10}

    # Verify this line works (from fixed example)
    for source in sources["sources"]:
        domain = source["source"]  # Should work with corrected docs
        print(f"✓ Can access source field: {domain}")
```

### Test Step 4: Check Documentation Accuracy

Run these checks before finalizing:

```bash
# Check 1: Verify parameter names match code
grep -n "source_filter" src/tools/rag_tools.py
grep -n "source_filter" docs/API_REFERENCE.md
# Should show parameter name is consistent

# Check 2: Verify no old field names in docs
grep -n "source_id" src/tools/source_tools.py  # Should find NO matches
grep -n "source_id" docs/API_REFERENCE.md  # Should find NO matches after fix

# Check 3: Verify imports are present
grep -n "^import os" src/tools/rag_tools.py
grep -n "^import sys" src/tools/knowledge_graph_tools.py
# Should find both imports
```

---

## PHASE 5: DOCUMENTATION & RELEASE (optional)

### Step 1: Update CHANGELOG.md

Add to CHANGELOG.md under "Unreleased" or new version section:

```markdown
## [1.2.1] - 2025-10-28 (or next version)

### Fixed
- Fixed missing `import os` in `src/tools/rag_tools.py` - Fixes NameError in perform_rag_query and search_code_examples
- Fixed missing `import sys` in `src/tools/knowledge_graph_tools.py` - Fixes NameError in check_ai_script_hallucinations
- Fixed get_available_sources return structure documentation - Now matches actual implementation
- Fixed get_available_sources parameter documentation - Clarified ctx parameter requirement
- Fixed perform_rag_query parameter name in documentation - Changed from `source` to `source_filter`

### Improved
- Added error response examples to all crawling tools
- Added parameter interaction notes for memory monitoring
- Enhanced documentation examples with clearer explanations
```

### Step 2: Create Summary Report

Create file `VALIDATION_COMPLETED.md`:

```markdown
# API Reference Validation - Completed

Date: 2025-10-28
All critical and high-priority issues have been fixed.

## Issues Fixed
- [x] Missing imports (rag_tools.py, knowledge_graph_tools.py)
- [x] get_available_sources documentation mismatch
- [x] Parameter name inconsistency (perform_rag_query)
- [x] Example code errors

## Testing Completed
- [x] Source code imports verified
- [x] get_available_sources return structure validated
- [x] Example code tested
- [x] Documentation consistency verified

## Status: COMPLETE
All 16 MCP tools are now fully documented and accurate.
```

---

## QUICK REFERENCE: File Changes Summary

### Files to Modify

| File | Changes | Priority | Est. Time |
|------|---------|----------|-----------|
| src/tools/rag_tools.py | Add `import os` | CRITICAL | 1 min |
| src/tools/knowledge_graph_tools.py | Add `import sys` | CRITICAL | 1 min |
| docs/API_REFERENCE.md | 5 changes to get_available_sources, 1 change to perform_rag_query | CRITICAL | 15 min |
| docs/API_REFERENCE.md | Add error examples to 5 crawling tools | MEDIUM | 20 min |
| docs/API_REFERENCE.md | Add parameter notes to 2 tools | MEDIUM | 10 min |
| CHANGELOG.md | Document fixes | OPTIONAL | 5 min |

**Total Time**: ~60 minutes

---

## Rollback Plan

If something goes wrong, revert using:

```bash
# Revert specific file
git checkout HEAD -- docs/API_REFERENCE.md

# Revert all changes
git checkout HEAD -- .

# Or from specific commits
git revert <commit-hash>
```

---

## Success Criteria

Implementation is complete when:

- [ ] All missing imports are added and verified
- [ ] get_available_sources documentation matches implementation
- [ ] perform_rag_query parameter name is consistent
- [ ] All example code in documentation is tested
- [ ] No import errors when running tools
- [ ] All tools return expected response structures
- [ ] Documentation examples execute without errors
- [ ] CHANGELOG is updated
- [ ] PR/Commit is created with changes

---

## Questions & Support

If unsure about any changes:
1. Review the VALIDATION_REPORT.md for detailed explanations
2. Check the DOCUMENTATION_VALIDATION_SUMMARY.md for context
3. Refer to API_REFERENCE_CORRECTIONS.md for specific fix details

---

**Document Version**: 1.0
**Created**: October 28, 2025
**Status**: Ready for Implementation
