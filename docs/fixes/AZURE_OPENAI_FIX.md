# Azure OpenAI Client Fix

**Issue**: GraphRAG initialization failing with error: "AsyncOpenAI.__init__() got an unexpected keyword argument 'api_version'"

**Date**: 2025-10-07
**Status**: ✅ Fixed

## Root Cause

The GraphRAG entity extractor was using the standard `AsyncOpenAI` client class for Azure OpenAI endpoints. However, Azure OpenAI requires a different client class (`AsyncAzureOpenAI`) with Azure-specific initialization parameters.

### The Problem

When using Azure OpenAI, the code attempted to pass `api_version` to `AsyncOpenAI.__init__()`, but the standard OpenAI client doesn't accept this parameter.

**Before (Incorrect)**:
```python
from openai import AsyncOpenAI

# This fails for Azure because AsyncOpenAI doesn't accept api_version
self.client = AsyncOpenAI(
    api_key=azure_openai_key,
    base_url=azure_openai_endpoint,
    api_version="2024-10-01-preview"  # ❌ Not supported by AsyncOpenAI
)
```

**After (Correct)**:
```python
from openai import AsyncOpenAI, AsyncAzureOpenAI

# Use Azure-specific client for Azure endpoints
if azure_openai_endpoint and azure_openai_key:
    self.client = AsyncAzureOpenAI(
        api_key=azure_openai_key,
        azure_endpoint=azure_openai_endpoint,  # ✅ Correct parameter name
        api_version="2024-10-01-preview"       # ✅ Supported by AsyncAzureOpenAI
    )
    self.is_azure = True
elif openai_api_key:
    self.client = AsyncOpenAI(api_key=openai_api_key)
    self.is_azure = False
```

## Key Differences: AsyncOpenAI vs AsyncAzureOpenAI

| Parameter | AsyncOpenAI | AsyncAzureOpenAI |
|-----------|-------------|------------------|
| `api_key` | ✅ Required | ✅ Required |
| `base_url` | ✅ Optional | ❌ Not used |
| `azure_endpoint` | ❌ Not used | ✅ Required |
| `api_version` | ❌ Not supported | ✅ Required |
| Model name | Full model name (e.g., `gpt-4o-mini`) | Deployment name (from Azure portal) |

## Files Modified

### 1. knowledge_graphs/document_entity_extractor.py

**Lines 15-19**: Updated imports
```python
try:
    from openai import AsyncOpenAI, AsyncAzureOpenAI
except ImportError:
    AsyncOpenAI = None
    AsyncAzureOpenAI = None
```

**Lines 137-157**: Fixed client initialization
```python
# Initialize OpenAI client (Azure or standard)
if azure_openai_endpoint and azure_openai_key:
    # Use Azure-specific client
    if not AsyncAzureOpenAI:
        raise ImportError("openai package with Azure support required")

    self.client = AsyncAzureOpenAI(
        api_key=azure_openai_key,
        azure_endpoint=azure_openai_endpoint,
        api_version="2024-10-01-preview"
    )
    self.is_azure = True
elif openai_api_key:
    self.client = AsyncOpenAI(api_key=openai_api_key)
    self.is_azure = False
else:
    raise ValueError("Either openai_api_key or azure_openai_endpoint+key must be provided")
```

### 2. src/initialization_utils.py

**Lines 183-201**: Updated entity extractor initialization to use deployment name
```python
# Initialize entity extractor (requires OpenAI)
document_entity_extractor = None
if azure_openai_endpoint and azure_openai_key:
    # For Azure, model should be the deployment name
    deployment_name = os.getenv("DEPLOYMENT") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    document_entity_extractor = DocumentEntityExtractor(
        azure_openai_endpoint=azure_openai_endpoint,
        azure_openai_key=azure_openai_key,
        model=deployment_name
    )
    print(f"✓ Document entity extractor initialized (Azure OpenAI, deployment: {deployment_name})")
elif openai_api_key:
    document_entity_extractor = DocumentEntityExtractor(
        openai_api_key=openai_api_key,
        model="gpt-4o-mini"
    )
    print("✓ Document entity extractor initialized (OpenAI)")
else:
    print("⚠ OpenAI API key not configured - entity extraction will be unavailable")
```

## Environment Variables

### For Azure OpenAI (Recommended)

```bash
# GraphRAG
USE_GRAPHRAG=true

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_key
DEPLOYMENT=your-deployment-name  # e.g., "gpt-4o-mini"
```

### For Standard OpenAI

```bash
# GraphRAG
USE_GRAPHRAG=true

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI
OPENAI_API_KEY=sk-...
```

## Deployment Name vs Model Name

**Important**: When using Azure OpenAI, you must use your **deployment name**, not the model name.

### Finding Your Azure Deployment Name

1. Go to Azure Portal → Your Azure OpenAI resource
2. Navigate to "Model deployments"
3. Find the deployment you want to use
4. Copy the "deployment name" (NOT the model name)

Example:
- ❌ Model name: `gpt-4o-mini` (generic model identifier)
- ✅ Deployment name: `my-gpt4o-deployment` (your specific deployment)

Set this in `.env`:
```bash
DEPLOYMENT=my-gpt4o-deployment
```

## Testing the Fix

### 1. Restart Docker Containers

```bash
docker-compose restart mcp-server
```

### 2. Check Initialization Logs

You should see:
```
Initializing GraphRAG components...
✓ Document graph validator initialized
✓ Document graph queries initialized
✓ Document entity extractor initialized (Azure OpenAI, deployment: your-deployment-name)
```

### 3. Test GraphRAG Extraction

Use the `crawl_with_graph_extraction` tool:

```json
{
  "url": "https://example.com",
  "extract_entities": true,
  "extract_relationships": true
}
```

**Expected Success Response**:
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

## Troubleshooting

### Error: "openai package with Azure support required"

**Solution**: Update the openai package
```bash
docker-compose exec mcp-server uv pip install --upgrade openai
```

### Error: "The API deployment for this resource does not exist"

**Cause**: Incorrect deployment name in environment variable

**Solution**:
1. Verify your deployment name in Azure Portal
2. Update `DEPLOYMENT` in `.env` file
3. Restart containers

### Error: "Access denied due to invalid subscription key"

**Cause**: Incorrect Azure OpenAI API key

**Solution**:
1. Get correct API key from Azure Portal → Your resource → Keys and Endpoint
2. Update `AZURE_OPENAI_API_KEY` in `.env`
3. Restart containers

### Still Getting "api_version" Error

**Cause**: Old code still cached

**Solution**:
```bash
# Rebuild containers to ensure fresh code
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Verification Checklist

✅ **Environment Variables**
- [ ] `USE_GRAPHRAG=true`
- [ ] `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` set
- [ ] Either `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` + `DEPLOYMENT` OR `OPENAI_API_KEY` set

✅ **Services Running**
- [ ] Neo4j running on configured port
- [ ] Docker containers restarted

✅ **Code Changes**
- [ ] `knowledge_graphs/document_entity_extractor.py` updated
- [ ] `src/initialization_utils.py` updated
- [ ] Changes reflected in container (via restart)

✅ **Testing**
- [ ] Initialization logs show success
- [ ] `crawl_with_graph_extraction` returns success
- [ ] Entities and relationships extracted correctly

## Related Issues

This fix resolves two related issues:
1. **Import Path Issue**: [GRAPHRAG_FIX.md](GRAPHRAG_FIX.md) - Fixed missing `knowledge_graphs.` prefix
2. **Azure Client Issue**: This document - Fixed Azure OpenAI client initialization

Both fixes were needed for GraphRAG to work properly.

## Technical Details

### Why Two Different Client Classes?

Azure OpenAI and OpenAI have different:
- **Authentication mechanisms**: Azure uses subscription keys, OpenAI uses API keys
- **Endpoint formats**: Azure uses resource-specific endpoints, OpenAI uses api.openai.com
- **API versioning**: Azure requires explicit version, OpenAI doesn't
- **Model references**: Azure uses deployment names, OpenAI uses model names

The `openai` Python package provides separate client classes to handle these differences cleanly.

### API Version

We use `api_version="2024-10-01-preview"` which is the latest stable API version for Azure OpenAI at the time of this fix. This version supports:
- JSON mode responses
- GPT-4o models
- Structured outputs
- All features needed for entity extraction

## Summary

✅ **Fixed**: Azure OpenAI client initialization
✅ **Updated**: 2 files (document_entity_extractor.py, initialization_utils.py)
✅ **Required**: Restart containers with `docker-compose restart mcp-server`
✅ **Verified**: Code changes syntactically correct
⏳ **Next**: User verification of GraphRAG functionality

---

*This fix was completed as part of the GraphRAG troubleshooting process*
*Last updated: 2025-10-07*
