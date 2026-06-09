# GraphRAG Import Fix

**Issue**: `crawl_with_graph_extraction` returning error: "GraphRAG components not available. Check Neo4j and OpenAI configuration."

**Date**: 2025-10-07
**Status**: ✅ Fixed

## Root Cause

The GraphRAG components (`DocumentGraphValidator`, `DocumentEntityExtractor`, `DocumentGraphQueries`) are located in the `knowledge_graphs/` subdirectory, but the import statements were missing the `knowledge_graphs.` prefix.

### Before (Incorrect):
```python
from document_graph_validator import DocumentGraphValidator
from document_entity_extractor import DocumentEntityExtractor
from document_graph_queries import DocumentGraphQueries
```

### After (Correct):
```python
from knowledge_graphs.document_graph_validator import DocumentGraphValidator
from knowledge_graphs.document_entity_extractor import DocumentEntityExtractor
from knowledge_graphs.document_graph_queries import DocumentGraphQueries
```

## Files Modified

1. **src/crawl4ai_mcp.py** (line 80-82)
   - Fixed imports for GraphRAG components

2. **src/initialization_utils.py** (line 26-28)
   - Fixed imports in the lazy import try/except block

## Verification Steps

### 1. Check Environment Variables

Your `.env` file should have:
```bash
USE_GRAPHRAG=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=sk-...
```

✅ **Status**: All environment variables correctly set

### 2. Verify Neo4j is Running

```bash
# Check if Neo4j is running on port 7687
nc -zv localhost 7687

# Or check with docker
docker ps | grep neo4j
```

✅ **Status**: Neo4j is running on port 7687

### 3. Verify neo4j Package is Installed

```bash
uv pip list | grep neo4j
```

✅ **Status**: neo4j 6.0.2 installed

### 4. Test GraphRAG Components

Run this Python test:

```python
import sys
sys.path.insert(0, '/mnt/e/Repos/GitHub/mcp-crawl4ai-rag')

from knowledge_graphs.document_graph_validator import DocumentGraphValidator
from knowledge_graphs.document_entity_extractor import DocumentEntityExtractor
from knowledge_graphs.document_graph_queries import DocumentGraphQueries

print("✓ All GraphRAG imports successful!")
```

## Testing the Fix

### Option 1: Quick Test

Restart your MCP server and try the `crawl_with_graph_extraction` tool again:

```javascript
// In Claude Desktop or MCP client
{
  "url": "https://example.com",
  "extract_entities": true,
  "extract_relationships": true
}
```

### Option 2: Python Test Script

Create a test file `test_graphrag.py`:

```python
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_graphrag_initialization():
    """Test GraphRAG component initialization"""

    # Import initialization function
    from src.initialization_utils import initialize_graphrag

    # Initialize components
    validator, extractor, queries = await initialize_graphrag()

    if validator and extractor and queries:
        print("✅ GraphRAG components initialized successfully!")
        print(f"  ✓ DocumentGraphValidator: {type(validator).__name__}")
        print(f"  ✓ DocumentEntityExtractor: {type(extractor).__name__}")
        print(f"  ✓ DocumentGraphQueries: {type(queries).__name__}")

        # Cleanup
        if validator:
            await validator.close()
        if queries:
            await queries.close()

        return True
    else:
        print("❌ GraphRAG initialization failed")
        return False

if __name__ == "__main__":
    asyncio.run(test_graphrag_initialization())
```

Run with:
```bash
python test_graphrag.py
```

## Expected Behavior After Fix

When calling `crawl_with_graph_extraction`, you should now see:

### Success Response:
```json
{
  "success": true,
  "url": "https://example.com",
  "source_id": "example.com",
  "crawl_results": {
    "documents_stored": 15,
    "total_words": 5000
  },
  "graph_extraction": {
    "entities_found": 25,
    "entities_stored": 25,
    "relationships_found": 40,
    "relationships_stored": 40,
    "extraction_time": "3.45s"
  },
  "document_id": "a1b2c3d4..."
}
```

### Initialization Logs:
When the server starts, you should see:
```
Initializing GraphRAG components...
✓ Document graph validator initialized
✓ Document graph queries initialized
✓ Document entity extractor initialized (OpenAI)
```

## Troubleshooting

### If you still see "GraphRAG components not available":

1. **Check server logs** for initialization errors
2. **Verify Neo4j connection**:
   ```bash
   cypher-shell -a bolt://localhost:7687 -u neo4j -p your_password "RETURN 1"
   ```
3. **Verify OpenAI API key** is valid
4. **Restart the MCP server** to reload the updated code

### Common issues

| Error | Solution |
|-------|----------|
| "No module named 'neo4j'" | Run `uv pip install neo4j` |
| "Neo4j connection failed" | Check Neo4j is running: `docker ps \| grep neo4j` |
| "OpenAI API error" | Verify OPENAI_API_KEY in .env |
| "Module not found 'knowledge_graphs'" | Ensure you're running from project root |

## Related Documentation

- [GRAPHRAG_GUIDE.md](docs/GRAPHRAG_GUIDE.md) - Complete GraphRAG documentation
- [TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md) - General troubleshooting
- [API_REFERENCE.md](docs/API_REFERENCE.md) - All MCP tools documentation

## Summary

✅ **Fixed**: Import paths corrected in 2 files
✅ **Verified**: Environment variables are correct
✅ **Verified**: Neo4j is running
✅ **Verified**: neo4j package is installed
✅ **Action Required**: Restart MCP server to apply fixes

The GraphRAG functionality should now work correctly!
