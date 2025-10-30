#!/usr/bin/env pwsh
# Script to run the complete MCP Crawl4AI-RAG stack with Docker Compose
# This starts both Neo4j and the MCP server with full knowledge graph capabilities

Write-Host "🐳 Starting Complete MCP Crawl4AI-RAG Stack (Neo4j + MCP Server)" -ForegroundColor Cyan
Write-Host ""

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ docker-compose.yml not found in current directory" -ForegroundColor Red
    Write-Host "   Please run this script from the repository root" -ForegroundColor Yellow
    exit 1
}

# Check if .env.docker exists
if (-not (Test-Path ".env.docker")) {
    Write-Host "⚠️  Warning: .env.docker not found" -ForegroundColor Yellow
    Write-Host "   Docker Compose will use default values or existing .env file" -ForegroundColor Gray
    Write-Host ""
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Build and start all services
Write-Host "🔨 Building and starting services (Neo4j + MCP Server)..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes on first run..." -ForegroundColor Gray
Write-Host ""

docker-compose --env-file .env.docker up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    Write-Host "   Run 'docker-compose logs' to see error details" -ForegroundColor Yellow
    exit 1
}

# Wait a moment for services to initialize
Write-Host ""
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service status
Write-Host ""
Write-Host "📊 Checking service status..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "✅ Complete Stack Started Successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Details:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "🔷 Neo4j Database:" -ForegroundColor Cyan
Write-Host "  🌐 Browser UI:  http://localhost:7474" -ForegroundColor Gray
Write-Host "  🔌 Bolt:        bolt://localhost:7687" -ForegroundColor Gray
Write-Host "  👤 Username:    neo4j" -ForegroundColor Gray
Write-Host "  🔑 Password:    (check .env.docker or docker-compose.yml)" -ForegroundColor Gray
Write-Host ""
Write-Host "� MCP Server:" -ForegroundColor Cyan
Write-Host "  🌐 HTTP URL:    http://localhost:8051" -ForegroundColor Gray
Write-Host "  🔗 MCP URL:     http://localhost:8051/mcp" -ForegroundColor Gray
Write-Host "  📡 Transport:   SSE (Server-Sent Events)" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 Useful Commands:" -ForegroundColor White
Write-Host "  View all logs:        docker-compose logs -f" -ForegroundColor Gray
Write-Host "  View MCP logs:        docker-compose logs -f mcp-server" -ForegroundColor Gray
Write-Host "  View Neo4j logs:      docker-compose logs -f neo4j" -ForegroundColor Gray
Write-Host "  Stop all services:    docker-compose down" -ForegroundColor Gray
Write-Host "  Restart services:     docker-compose restart" -ForegroundColor Gray
Write-Host "  Rebuild services:     docker-compose up -d --build" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor White
Write-Host "  1. Open Neo4j Browser at http://localhost:7474" -ForegroundColor Gray
Write-Host "  2. Connect to MCP server at http://localhost:8051/mcp" -ForegroundColor Gray
Write-Host "  3. Use MCP tools to crawl websites and build knowledge graphs" -ForegroundColor Gray
Write-Host ""
