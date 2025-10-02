# Running MCP Server in Multiple Modes

Your MCP server supports two transport modes that can run simultaneously:

## 🖥️ Mode 1: Stdio Transport (Claude Desktop - Local)

**Use case:** Direct integration with Claude Desktop on your local machine

**Configuration:**
- File: `.env`
- `TRANSPORT=stdio`
- No port needed (uses stdin/stdout)

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "E:\\Repos\\GitHub\\mcp-crawl4ai-rag",
        "python",
        "run_mcp.py"
      ]
    }
  }
}
```

**To run manually:**
```powershell
uv run python run_mcp.py
```

---

## 🐳 Mode 2: SSE/HTTP Transport (Docker - Network)

**Use case:** Network-accessible MCP server for web clients, remote access, or testing

**Configuration:**
- File: `.env.docker` (create this separately)
- `TRANSPORT=sse`
- `HOST=0.0.0.0`
- `PORT=8051`

**Quick Start:**
```powershell
# Using the provided script
.\run_docker.ps1

# Or manually:
docker run -d \
  --name mcp-crawl4ai-rag \
  -p 8051:8051 \
  -e TRANSPORT=sse \
  -e HOST=0.0.0.0 \
  -e PORT=8051 \
  --env-file .env.docker \
  mcp/crawl4ai-rag
```

**Access URLs:**
- Server: `http://localhost:8051`
- MCP endpoint: `http://localhost:8051/mcp`

**Useful commands:**
```powershell
# View logs
docker logs -f mcp-crawl4ai-rag

# Stop server
docker stop mcp-crawl4ai-rag

# Restart
docker restart mcp-crawl4ai-rag

# Remove
docker rm -f mcp-crawl4ai-rag
```

---

## 🔄 Running Both Simultaneously

**Yes, you can run both at the same time!**

1. **Stdio mode** for Claude Desktop (local process communication)
2. **HTTP mode** in Docker (network access on port 8051)

They use different transport mechanisms and don't conflict:
- Stdio: Process pipes (no network)
- HTTP: TCP socket on port 8051

### Example Setup:

**Terminal 1 - Claude Desktop (stdio):**
```powershell
# Automatically started by Claude Desktop
# Uses .env with TRANSPORT=stdio
```

**Terminal 2 - Docker (HTTP):**
```powershell
# Start Docker container
.\run_docker.ps1

# Access at http://localhost:8051/mcp
```

---

## 🔧 Environment File Setup

### `.env` (for local/stdio)
```env
TRANSPORT=stdio
# ... other environment variables
```

### `.env.docker` (for Docker/HTTP)
```env
TRANSPORT=sse
HOST=0.0.0.0
PORT=8051
# ... copy other environment variables from .env
```

---

## 🧪 Testing

### Test Stdio Mode:
```powershell
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | uv run python run_mcp.py
```

### Test HTTP Mode:
```powershell
# Start Docker container
docker run -d -p 8051:8051 -e TRANSPORT=sse --env-file .env.docker mcp/crawl4ai-rag

# Test endpoint
curl http://localhost:8051/mcp
```

---

## 📝 Quick Reference

| Feature | Stdio Mode | HTTP/SSE Mode |
|---------|-----------|---------------|
| **Use Case** | Claude Desktop | Web clients, remote access |
| **Transport** | stdin/stdout | TCP/HTTP |
| **Port** | None | 8051 (configurable) |
| **Config File** | `.env` | `.env.docker` |
| **Run Command** | `uv run python run_mcp.py` | `docker run ...` or `.\run_docker.ps1` |
| **Access** | Process pipes | http://localhost:8051/mcp |

---

## 🚀 Recommended Workflow

1. **Development:** Use stdio mode with Claude Desktop (easier debugging)
2. **Testing:** Use HTTP mode in Docker (test network access)
3. **Production:** Use Docker with HTTP mode (scalable, isolated)

Both modes can coexist - choose based on your current need!
