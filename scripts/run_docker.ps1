#!/usr/bin/env pwsh
# Script to run the MCP server in Docker with HTTP/SSE transport

Write-Host "🐳 Starting MCP Server in Docker with HTTP/SSE transport" -ForegroundColor Cyan
Write-Host ""

# Stop and remove existing container if it exists
Write-Host "🛑 Stopping existing container..." -ForegroundColor Yellow
docker stop mcp-crawl4ai-rag 2>$null
docker rm mcp-crawl4ai-rag 2>$null

# Build the image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -t mcp/crawl4ai-rag .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

# Run the container with SSE transport
Write-Host "🚀 Starting container..." -ForegroundColor Yellow
docker run -d `
    --name mcp-crawl4ai-rag `
    -p 8051:8051 `
    --env-file .env.docker `
    -e TRANSPORT=sse `
    -e HOST=0.0.0.0 `
    -e PORT=8051 `
    mcp/crawl4ai-rag

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ MCP Server started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Connection Details:" -ForegroundColor White
    Write-Host "  🔗 HTTP URL: http://localhost:8051" -ForegroundColor Gray
    Write-Host "  🔗 MCP URL:  http://localhost:8051/mcp" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📝 Useful Commands:" -ForegroundColor White
    Write-Host "  View logs:    docker logs -f mcp-crawl4ai-rag" -ForegroundColor Gray
    Write-Host "  Stop server:  docker stop mcp-crawl4ai-rag" -ForegroundColor Gray
    Write-Host "  Restart:      docker restart mcp-crawl4ai-rag" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "❌ Failed to start container" -ForegroundColor Red
    exit 1
}
