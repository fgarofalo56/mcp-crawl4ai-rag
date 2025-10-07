# Docker Setup Guide with Neo4j Knowledge Graph Support

This guide provides comprehensive instructions for running the MCP Crawl4AI server in Docker with full Neo4j knowledge graph functionality.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start with Docker Compose](#quick-start-with-docker-compose)
4. [Alternative: Docker with Host Neo4j](#alternative-docker-with-host-neo4j)
5. [Alternative: Standalone Docker Container](#alternative-standalone-docker-container)
6. [Neo4j Connection Troubleshooting](#neo4j-connection-troubleshooting)
7. [Network Configuration Deep Dive](#network-configuration-deep-dive)
8. [Testing Neo4j Connectivity](#testing-neo4j-connectivity)
9. [Production Deployment](#production-deployment)

## Overview

The MCP Crawl4AI server can run in Docker in several configurations:

- **Docker Compose (Recommended)**: Both MCP server and Neo4j run in Docker with automatic networking
- **Docker + Host Neo4j**: MCP server in Docker, Neo4j on your host machine
- **Standalone Docker**: Just the MCP server (requires external Neo4j or disabled knowledge graph)

## Prerequisites

- Docker Desktop 20.10+ (includes Docker Compose)
- 4GB+ available RAM (2GB for Neo4j, 2GB for MCP server)
- Basic understanding of Docker networking
- Your API keys and Supabase credentials

## Quick Start with Docker Compose

This is the **recommended** approach - everything runs in Docker with automatic configuration.

### Step 1: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your credentials:
   ```bash
   # Required: API Keys
   OPENAI_API_KEY=sk-your-key-here
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key-here

   # Required for Knowledge Graph
   NEO4J_PASSWORD=your-secure-password-here
   NEO4J_USER=neo4j

   # Enable knowledge graph features
   USE_KNOWLEDGE_GRAPH=true

   # Optional: RAG strategies
   USE_HYBRID_SEARCH=true
   USE_AGENTIC_RAG=true
   USE_RERANKING=true
   ```

3. **IMPORTANT**: The docker-compose.yml automatically sets `NEO4J_URI=bolt://neo4j:7687` - you don't need to configure this manually.

### Step 2: Start Services

Start both Neo4j and the MCP server:

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f mcp-server
docker-compose logs -f neo4j
```

### Step 3: Verify Services

1. **Check Neo4j Browser**: Open http://localhost:7474
   - Username: `neo4j`
   - Password: (whatever you set in NEO4J_PASSWORD)

2. **Check MCP Server**: The server will be at http://localhost:8051

3. **Test Knowledge Graph Connection**:
   ```bash
   # Check MCP server logs for Neo4j initialization
   docker-compose logs mcp-server | grep -i neo4j

   # Should see:
   # ✓ Knowledge graph validator initialized
   # ✓ Repository extractor initialized
   ```

### Step 4: Stop Services

```bash
# Stop services (preserves data)
docker-compose stop

# Stop and remove containers (preserves data volumes)
docker-compose down

# Stop and remove EVERYTHING including data
docker-compose down -v  # WARNING: Deletes all Neo4j data!
```

## Alternative: Docker with Host Neo4j

If you already have Neo4j running on your host machine (not in Docker), you can connect to it from the Docker container.

### Step 1: Configure Environment

Edit your `.env` file:

```bash
# For MCP server in Docker connecting to Neo4j on host
NEO4J_URI=bolt://host.docker.internal:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here
USE_KNOWLEDGE_GRAPH=true
```

**Key Point**: `host.docker.internal` is a special DNS name that Docker containers use to connect to services on the host machine.

### Step 2: Start Neo4j on Host

Make sure Neo4j is running on your host machine and listening on port 7687:

```bash
# Verify Neo4j is running
curl http://localhost:7474  # Should return Neo4j browser

# Or check with netstat (Windows)
netstat -an | findstr :7687

# Or lsof (Mac/Linux)
lsof -i :7687
```

### Step 3: Build and Run MCP Server

```bash
# Build the Docker image
docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .

# Run with environment file
docker run -d \
  --name mcp-crawl4ai \
  --env-file .env \
  -p 8051:8051 \
  --restart unless-stopped \
  mcp/crawl4ai-rag
```

### Step 4: Verify Connection

```bash
# Check container logs
docker logs mcp-crawl4ai

# Should see Neo4j initialization messages
docker logs mcp-crawl4ai | grep -i neo4j
```

## Alternative: Standalone Docker Container

Running just the MCP server without Docker Compose.

### Option 1: With Knowledge Graph Disabled

```bash
# Build
docker build -t mcp/crawl4ai-rag .

# Run with knowledge graph disabled
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

### Option 2: With Cloud Neo4j (AuraDB)

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
  -e USE_KNOWLEDGE_GRAPH=true \
  -e NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASSWORD=your-cloud-password \
  --restart unless-stopped \
  mcp/crawl4ai-rag
```

## Neo4j Connection Troubleshooting

### Problem: "Cannot connect to Neo4j"

**Symptom**: Error messages in logs:
```
Failed to initialize Neo4j components: Cannot connect to Neo4j. Check NEO4J_URI and ensure Neo4j is running.
```

**Solutions**:

1. **Check Neo4j is Running**:
   ```bash
   # Docker Compose
   docker-compose ps

   # Standalone Neo4j container
   docker ps | grep neo4j

   # Host Neo4j (Windows)
   netstat -an | findstr :7687
   ```

2. **Verify Network Configuration**:
   - Docker Compose: Use `NEO4J_URI=bolt://neo4j:7687`
   - Host Neo4j: Use `NEO4J_URI=bolt://host.docker.internal:7687`
   - Cloud Neo4j: Use `NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io`

3. **Check Docker Networking** (Docker Compose):
   ```bash
   # List networks
   docker network ls

   # Inspect the MCP network
   docker network inspect mcp-crawl4ai-rag_mcp-network

   # Verify both containers are on the same network
   docker inspect mcp-crawl4ai-server | grep NetworkMode
   docker inspect mcp-crawl4ai-neo4j | grep NetworkMode
   ```

4. **Test Connection from Container**:
   ```bash
   # Enter the MCP server container
   docker exec -it mcp-crawl4ai-server bash

   # Try to reach Neo4j (Docker Compose)
   curl http://neo4j:7474

   # Try to reach host Neo4j
   curl http://host.docker.internal:7474

   # Exit container
   exit
   ```

### Problem: "Authentication failed"

**Symptom**:
```
Neo4j authentication failed. Check NEO4J_USER and NEO4J_PASSWORD.
```

**Solutions**:

1. **Verify Credentials**:
   ```bash
   # Check environment variable in container
   docker exec mcp-crawl4ai-server env | grep NEO4J
   ```

2. **Reset Neo4j Password** (Docker Compose):
   ```bash
   # Stop services
   docker-compose down

   # Remove Neo4j data volume
   docker volume rm mcp-crawl4ai-rag_neo4j_data

   # Update NEO4J_PASSWORD in .env
   # Restart services
   docker-compose up -d
   ```

3. **Test Credentials Manually**:
   - Open http://localhost:7474
   - Try logging in with your credentials
   - If login fails, password is incorrect

### Problem: "localhost" doesn't work from Docker

**Symptom**: Connection works locally but not in Docker.

**Explanation**: Inside a Docker container, `localhost` refers to the container itself, not your host machine.

**Solution**: Use `host.docker.internal` instead:
```bash
# WRONG (inside Docker)
NEO4J_URI=bolt://localhost:7687

# CORRECT (inside Docker connecting to host)
NEO4J_URI=bolt://host.docker.internal:7687

# CORRECT (Docker Compose - service name)
NEO4J_URI=bolt://neo4j:7687
```

## Network Configuration Deep Dive

### How Docker Networking Works

Docker containers are isolated by default. To communicate, they need to be on the same network or use special DNS names.

#### Docker Compose Networking

Docker Compose automatically creates a network and assigns service names as hostnames:

```yaml
services:
  neo4j:          # Hostname: "neo4j"
    # ...
  mcp-server:     # Hostname: "mcp-server"
    # ...
```

The MCP server can reach Neo4j using `bolt://neo4j:7687`.

#### Host Network Access

Docker provides a special hostname for the host machine:
- **Windows/Mac**: `host.docker.internal`
- **Linux**: `172.17.0.1` (Docker bridge gateway) or add `--add-host=host.docker.internal:host-gateway`

### Port Mapping vs. Container Ports

```yaml
ports:
  - "7687:7687"  # host:container
```

- **7687** on left: Port on your host machine (localhost:7687)
- **7687** on right: Port inside the container

From inside the MCP container, you would use:
- `neo4j:7687` (service name) for Docker Compose
- `host.docker.internal:7687` for host Neo4j

From your host machine, you would use:
- `localhost:7687` (always)

## Testing Neo4j Connectivity

### Test 1: Neo4j Browser Access

```bash
# Open in browser
http://localhost:7474

# Login with:
# Username: neo4j
# Password: (from NEO4J_PASSWORD env var)
```

### Test 2: Bolt Protocol Connection

```bash
# From host machine
docker run --rm -it \
  --network mcp-crawl4ai-rag_mcp-network \
  alpine/curl \
  curl http://neo4j:7474

# Should return HTML with Neo4j browser
```

### Test 3: MCP Server Connection Test

Create a test script to verify the connection:

```python
# test_neo4j_connection.py
import os
from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print(f"Username: {user}")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ Connection successful!")
    driver.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run inside the container:
```bash
docker exec -it mcp-crawl4ai-server python test_neo4j_connection.py
```

### Test 4: Parse a Repository

Once connected, test the knowledge graph functionality:

```bash
# Using MCP client or directly:
curl -X POST http://localhost:8051/tools/parse_github_repository \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/pydantic/pydantic-ai.git"
  }'
```

Check Neo4j browser for the parsed data:
```cypher
// In Neo4j Browser (http://localhost:7474)
MATCH (r:Repository)
RETURN r.name

MATCH (c:Class)
RETURN c.name, c.full_name
LIMIT 10
```

## Production Deployment

### Security Considerations

1. **Change Default Passwords**:
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

2. **Use Docker Secrets** (Docker Swarm):
   ```yaml
   secrets:
     neo4j_password:
       external: true

   services:
     neo4j:
       secrets:
         - neo4j_password
       environment:
         - NEO4J_AUTH=neo4j/run/secrets/neo4j_password
   ```

3. **Restrict Network Access**:
   ```yaml
   # Only expose MCP server, not Neo4j
   services:
     neo4j:
       # Remove ports section (internal only)
       # ports:
       #   - "7687:7687"
   ```

4. **Use TLS/SSL**:
   - For Neo4j: Configure SSL certificates
   - For MCP server: Use reverse proxy (nginx/traefik) with HTTPS

### Resource Limits

```yaml
services:
  neo4j:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

### Backup Neo4j Data

```bash
# Backup Neo4j data volume
docker run --rm \
  -v mcp-crawl4ai-rag_neo4j_data:/data \
  -v $(pwd)/backups:/backup \
  alpine \
  tar czf /backup/neo4j-backup-$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm \
  -v mcp-crawl4ai-rag_neo4j_data:/data \
  -v $(pwd)/backups:/backup \
  alpine \
  tar xzf /backup/neo4j-backup-20240115.tar.gz -C /
```

### Monitoring

#### Health Check Endpoint

The MCP server includes a `/health` endpoint (added in v1.1.1) for monitoring service status.

**Test the health endpoint manually:**
```bash
curl http://localhost:8051/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "mcp-crawl4ai-rag",
  "version": "1.1.1",
  "transport": "sse"
}
```

**Docker Compose health check** (already configured in `docker-compose.yml`):
```yaml
services:
  mcp-server:
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8051/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Check service health status:**
```bash
docker-compose ps
# Shows health status for each service - should show "healthy" after startup
```

## Common Issues and Solutions

### Issue: Container keeps restarting

```bash
# Check logs
docker-compose logs mcp-server

# Common causes:
# - Missing environment variables
# - Neo4j not ready (increase start_period)
# - Port already in use
```

### Issue: Cannot access from host

```bash
# Verify port mapping
docker-compose ps

# Check firewall
# Windows: Windows Firewall
# Linux: iptables -L
# Mac: System Preferences > Security & Privacy > Firewall
```

### Issue: Data lost after restart

**Solution**: Use named volumes (already configured in docker-compose.yml)

```yaml
volumes:
  neo4j_data:  # Persists data
```

To preserve data, use `docker-compose down` (without `-v` flag).

## Additional Resources

- [Docker Networking Documentation](https://docs.docker.com/network/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Neo4j Docker Documentation](https://neo4j.com/developer/docker/)
- [MCP Server Main README](../README.md)
- [Knowledge Graph Setup Guide](../README.md#knowledge-graph-setup)

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#neo4j-connection-troubleshooting) section above
2. Review logs: `docker-compose logs`
3. Open an issue on [GitHub](https://github.com/coleam00/mcp-crawl4ai-rag/issues)
4. Include:
   - Docker version: `docker --version`
   - Docker Compose version: `docker-compose --version`
   - Relevant logs
   - Your configuration (without sensitive data)
