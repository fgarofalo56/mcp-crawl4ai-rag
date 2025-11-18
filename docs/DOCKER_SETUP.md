# Docker Setup Guide (External Neo4j)

This guide explains how to run the MCP Crawl4AI server in Docker while connecting to an existing Neo4j instance (local, remote, or cloud hosted). The project no longer provisions Neo4j via Docker Compose, so you are free to point the server at any Neo4j deployment that fits your environment.

## Table of contents

- [Docker Setup Guide (External Neo4j)](#docker-setup-guide-external-neo4j)
  - [Table of contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Provision Neo4j](#provision-neo4j)
  - [Quick Start with Docker Compose](#quick-start-with-docker-compose)
    - [Step 1: Create an environment file](#step-1-create-an-environment-file)
    - [Step 2: Launch the container](#step-2-launch-the-container)
    - [Step 3: Verify startup](#step-3-verify-startup)
  - [Running with `docker run`](#running-with-docker-run)
  - [Neo4j Connection Troubleshooting](#neo4j-connection-troubleshooting)
    - ["Cannot connect to Neo4j"](#cannot-connect-to-neo4j)
      - [Symptom](#symptom)
      - [Checklist](#checklist)
    - ["Authentication failed"](#authentication-failed)
    - ["localhost" behaves differently inside Docker](#localhost-behaves-differently-inside-docker)
  - [Testing Neo4j Connectivity](#testing-neo4j-connectivity)
  - [Production Deployment Notes](#production-deployment-notes)

## Overview

The MCP Crawl4AI Docker image provides the server component only. You can combine it with any Neo4j installation; popular options include:

- **Neo4j Desktop or local install** on the same machine (recommended for development)
- **Docker container** you manage independently of this project
- **Neo4j Aura or other cloud offering**

Because Neo4j is external, the Docker configuration is now lightweight and focused solely on the MCP server. Knowledge-graph features are still fully supported once the server can reach your Neo4j instance.

## Prerequisites

- Docker Desktop 20.10+ (includes Docker Compose)
- API keys and Supabase credentials required by the server
- Access to a running Neo4j database (self-hosted or cloud)

## Provision Neo4j

Ensure you have a reachable Neo4j instance before starting the MCP server. Below are common setups:

| Scenario | Connection URI | Notes |
| --- | --- | --- |
| Neo4j running on the same host machine | `bolt://localhost:7687` (when running MCP locally) or `bolt://host.docker.internal:7687` (when MCP runs in Docker) | Default development workflow; start Neo4j Desktop or a standalone Docker container |
| Remote/server Neo4j | `bolt://<hostname>:7687` | Open network access and ensure firewalls permit Bolt traffic |
| Neo4j Aura (cloud) | `neo4j+s://<instance>.databases.neo4j.io` | Requires TLS; credentials provided by Aura |

> 💡 **Tip**: When running MCP in Docker on Linux, `host.docker.internal` is not available by default. Use `--add-host=host.docker.internal:host-gateway` on `docker run` (or update `/etc/hosts`) to mirror the behavior.

## Quick Start with Docker Compose

The repository ships with a minimal `docker-compose.yml` that launches only the MCP server. Configure environment variables so the container can authenticate with your external Neo4j instance.

### Step 1: Create an environment file

For Docker deployments, use the dedicated Docker environment template:

```bash
cp .env.docker.example .env.docker
```

Update `.env.docker` with your actual credentials and configuration. At minimum set:

```bash
# Transport configuration (automatically set for Docker)
TRANSPORT=sse
HOST=0.0.0.0
PORT=8051

# API Keys
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# Enable knowledge graph features (optional)
USE_KNOWLEDGE_GRAPH=true

# Neo4j connectivity (required if USE_KNOWLEDGE_GRAPH=true)
NEO4J_URI=bolt://host.docker.internal:7687   # or your remote URI
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

> **Note**: The `.env.docker` file is automatically loaded by `docker-compose.yml` via the `env_file` directive. The `TRANSPORT` is set to `sse` for Docker (HTTP/network mode), while local development with Claude Desktop uses `stdio`.

See `.env.docker.example` for all available options (GraphRAG, contextual embeddings, hybrid search, etc.). Leave `USE_KNOWLEDGE_GRAPH=false` if you do not plan to connect to Neo4j.

### Step 2: Launch the container

```bash
# Start in the foreground
docker compose up

# Or start in detached mode
docker compose up -d
```

Available commands:

```bash
# View aggregated logs
docker compose logs -f

# View only MCP server logs
docker compose logs -f mcp-server

# Stop the container
docker compose down
```

### Step 3: Verify startup

1. **Check container logs** for successful startup:

   ```bash
   docker logs mcp-crawl4ai-server
   ```

   You should see:
   ```text
   ✓ MCP Server configured with 16 tools across 5 categories
     - Crawling: 5 tools
     - RAG: 2 tools
     - Knowledge Graph: 4 tools
     - GraphRAG: 4 tools
     - Source Management: 1 tool

   Running on http://0.0.0.0:8051 (transport: sse)
   ```

2. **Verify the health endpoint** returns healthy status:

   ```bash
   curl http://localhost:8051/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "mcp-crawl4ai-rag",
     "version": "2.0.0",
     "transport": "sse",
     "tools_registered": 16
   }
   ```

3. **If using Neo4j**, confirm the instance is reachable from your machine:
   - Neo4j Browser: `http://localhost:7474`
   - Check logs for: `✓ Knowledge graph validator initialized`

If the container reports connection failures or shows `transport: stdio` instead of `transport: sse`, see the [troubleshooting](#neo4j-connection-troubleshooting) section.

## Running with `docker run`

You can also run the image manually without Compose. This is useful when orchestrating the container in another system or when you prefer custom arguments.

```bash
docker build -t mcp/crawl4ai-rag .

docker run -d `
  --name mcp-crawl4ai `
  -p 8051:8051 `
  --env-file .env.docker `
  --restart unless-stopped `
  mcp/crawl4ai-rag
```

When knowledge-graph features are disabled:

```bash
docker run -d \
  --name mcp-crawl4ai \
  -p 8051:8051 \
  -e TRANSPORT=sse \
  -e HOST=0.0.0.0 \
  -e PORT=8051 \
  -e OPENAI_API_KEY=your-key \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_SERVICE_KEY=your-key \
  -e USE_KNOWLEDGE_GRAPH=false \
  --restart unless-stopped \
  mcp/crawl4ai-rag
```

## Neo4j Connection Troubleshooting

### "Cannot connect to Neo4j"

#### Symptom

```text
Failed to initialize Neo4j components: Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running.
```

#### Checklist

1. Verify Neo4j is running and listening on the expected port.

   ```bash
   # macOS / Linux
   lsof -i :7687

   # Windows PowerShell
   Get-NetTCPConnection -LocalPort 7687
   ```

2. Confirm the connection string. Examples:
   - Local host: `bolt://localhost:7687`
   - From Docker (macOS/Windows): `bolt://host.docker.internal:7687`
   - AuraDB: `neo4j+s://your-instance.databases.neo4j.io`
3. Make sure firewalls allow outbound Bolt traffic (tcp/7687) from the container.
4. From inside the container, test connectivity:

   ```bash
   docker exec -it mcp-crawl4ai /bin/bash
   apt-get update && apt-get install -y curl || true
   curl -I http://host.docker.internal:7474
   ```

### "Authentication failed"

```text
Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD.
```

- Verify credentials by logging into the Neo4j Browser (`http://localhost:7474`).
- Regenerate or reset the password if necessary, then update the environment variables and restart the container.

### "localhost" behaves differently inside Docker

Inside a container, `localhost` refers to the container itself. Use `host.docker.internal` (or the host gateway IP on Linux) to reach services running on the host machine.

```bash
# Wrong (from inside container)
NEO4J_URI=bolt://localhost:7687

# Correct (container -> host)
NEO4J_URI=bolt://host.docker.internal:7687

# Correct (container -> remote server)
NEO4J_URI=bolt://my-remote-server:7687
```

### Container shows "transport: stdio" instead of "transport: sse"

#### Symptom

Container logs show:
```text
transport: stdio
No .env file found. Using system environment variables.
```

#### Solution

This was fixed in v2.0.0. If you see this issue:

1. **Update your configuration files**:
   - Ensure `docker-compose.yml` includes `env_file: .env.docker`
   - Verify `Dockerfile` CMD uses `python -m src.server` (not old module name)
   - Check that `TRANSPORT=sse` is set in `.env.docker`

2. **Rebuild the container** with latest changes:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Verify the fix** by checking logs:
   ```bash
   docker logs mcp-crawl4ai-server | grep "transport:"
   ```
   Should show: `Running on http://0.0.0.0:8051 (transport: sse)`

**Root cause**: Earlier versions had the wrong module path in Dockerfile and didn't properly load `.env.docker` file. This is now fixed.

## Testing Neo4j Connectivity

Create a quick script to test the Bolt connection from the MCP container:

```python
# scripts/test_neo4j_connection.py
import os
from neo4j import GraphDatabase

uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
user = os.environ.get("NEO4J_USER", "neo4j")
password = os.environ.get("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")

driver = GraphDatabase.driver(uri, auth=(user, password))
driver.verify_connectivity()
print("✅ Connection successful!")
driver.close()
```

Run it with:

```bash
docker exec -it mcp-crawl4ai python scripts/test_neo4j_connection.py
```

If `verify_connectivity()` raises an exception, double check the URI, credentials, and network path.

## Production Deployment Notes

- **Secure credentials**: Store API keys and Neo4j credentials in a secrets manager or inject them at runtime (e.g., Docker secrets, Kubernetes secrets).
- **Use TLS**: When exposing the MCP server publicly, front it with a reverse proxy (nginx, Traefik) that terminates TLS. For Neo4j Aura, TLS is required automatically.
- **Monitor health**: The container exposes `http://localhost:8051/health`. Docker Compose already registers a health check that leverages this endpoint.
- **Scaling**: Because the MCP server is stateless, you can run multiple replicas (with a load balancer) that all point to the same Neo4j instance.

---

Need additional help? Review the [main README](../README.md) or open an issue on [GitHub](https://github.com/coleam00/mcp-crawl4ai-rag/issues) with logs and configuration details (omit secrets).
