FROM python:3.12-slim

ARG PORT=8051

WORKDIR /app

# Install system dependencies
# - curl: for health checks
# - git: for cloning repositories (knowledge graph feature)
# - g++, gcc, make: for building Python packages with C extensions
RUN apt-get update && \
    apt-get install -y curl git g++ gcc make && \
    rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy the MCP server files
COPY . .

# Install Python dependencies and setup Crawl4AI
# Note: Installing directly to system (no virtual environment) for Docker
RUN uv pip install --system -e . && \
    crawl4ai-setup

EXPOSE ${PORT}

# Add src and knowledge_graphs directories to PYTHONPATH for correct module imports
ENV PYTHONPATH=/app/src:/app/knowledge_graphs:${PYTHONPATH}

# ============================================================================
# NEO4J DOCKER NETWORKING NOTES
# ============================================================================
# When connecting to Neo4j from this Docker container, the NEO4J_URI must be
# configured correctly based on where Neo4j is running:
#
# 1. Neo4j on HOST machine:
#    Set NEO4J_URI=bolt://host.docker.internal:7687
#
# 2. Neo4j in Docker Compose:
#    Set NEO4J_URI=bolt://neo4j:7687 (use service name)
#
# 3. Neo4j in Cloud (AuraDB):
#    Set NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
#
# See .env.docker and docker-compose.yml for configuration examples
# ============================================================================

# Health check endpoint (requires curl installed above)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the MCP server as a module
CMD ["python", "-m", "crawl4ai_mcp"]
