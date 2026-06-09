# Import Fix - October 2, 2025

## Problems Identified

After the codebase cleanup and reorganization, the MCP server was crashing immediately after startup with two issues:

### Issue 1: Import Error

```
2025-10-02T21:56:23.210Z [crawl4ai-rag] [info] Server transport closed { metadata: undefined }
```

### Issue 2: Stdio Protocol Violation

```
2025-10-02T22:06:27.911Z [crawl4ai-rag] [error] Unexpected token 'c', "  crawl4ai-setup" is not valid JSON
```

## Root Causes

### Cause 1: Incorrect Import Path

The issue was caused by an incorrect import statement in `src/crawl4ai_mcp.py` line 40:

**Before (BROKEN):**
```python
from utils import (
    get_supabase_client,
    add_documents_to_supabase,
    search_documents,
    # ... other functions
)
```

This was trying to import from `knowledge_graphs/utils.py` (which doesn't exist) instead of `src/utils.py`.

### Cause 2: stdout Contamination

The `run_mcp.py` script was printing diagnostic messages to **stdout** instead of **stderr**:

**Before (BROKEN):**
```python
print(f"Loading environment from: {env_path}")
print(f"Using port: {free_port}")
print(f"Error importing MCP server: {e}")
```

In stdio transport mode, **stdout is reserved exclusively for JSON-RPC messages**. Any text output breaks the protocol.

## Solutions

### Solution 1: Fix Import Path

Changed the import to use relative import from the src module:

**After (FIXED):**
```python
from .utils import (
    get_supabase_client,
    add_documents_to_supabase,
    search_documents,
    # ... other functions
)
```

### Solution 2: Redirect Output to stderr

Created a helper function and replaced all print statements:

**After (FIXED):**
```python
def print_info(*args, **kwargs):
    """Print to stderr to avoid breaking stdio JSON-RPC protocol."""
    print(*args, file=sys.stderr, **kwargs)

# All diagnostic output now uses:
print_info(f"Loading environment from: {env_path}")
print_info(f"Using port: {free_port}")
```

Also fixed the import statement in `run_mcp.py`:
```python
# Changed from:
from crawl4ai_mcp import main

# To:
from src.crawl4ai_mcp import main
```

## Files Modified

- `src/crawl4ai_mcp.py` - Line 40: Changed `from utils import` to `from .utils import`
- `run_mcp.py` - Added `print_info()` helper and redirected all output to stderr
- `run_mcp.py` - Line 70: Changed `from crawl4ai_mcp import main` to `from src.crawl4ai_mcp import main`

## Verification

1. ✅ **Import Test**: `from src.crawl4ai_mcp import mcp` - SUCCESS
2. ✅ **Test Suite**: All 64 tests passed
3. ✅ **Coverage**: 30% overall, 90%+ on refactored modules
4. ✅ **MCP Server**: Now starts successfully in Claude Desktop

## Impact

- **Before Fix**: MCP server crashed immediately on startup
- **After Fix**: MCP server starts successfully and remains running
- **No Breaking Changes**: All tests pass, functionality preserved

## Prevention

This issue occurred because:
1. During the Phase 2 refactoring, `utils.py` was created in the `src/` folder
2. The import path needed to be updated to use relative imports (`.utils`)
3. The dynamic `sys.path.append()` for knowledge_graphs folder created ambiguity

## Related Documentation

- See `docs/CODE_QUALITY_IMPROVEMENTS.md` for the original refactoring
- See `docs/ALL_FIXES_COMPLETE.md` for the complete fix history
- See `docs/SETUP_COMPLETE.md` for current setup instructions
