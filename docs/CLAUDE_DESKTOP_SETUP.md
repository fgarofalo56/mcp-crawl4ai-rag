# Claude Desktop Setup Guide

This guide will help you connect the Crawl4AI RAG MCP server to Claude Desktop.

## Prerequisites

Before starting, ensure you have:
- Claude Desktop installed
- Python 3.12+ installed
- `uv` package manager installed (`pip install uv`)
- API keys for OpenAI and Supabase

## Quick Start

### Step 1: Clone and Setup the Project

```bash
# Clone the repository
git clone https://github.com/coleam00/mcp-crawl4ai-rag.git
cd mcp-crawl4ai-rag

# Install dependencies
uv pip install -e .

# Setup Crawl4AI
crawl4ai-setup
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows

# Edit .env with your credentials
# Open in your preferred editor and add your API keys
```

Required settings in `.env`:
```env
# Use stdio for Claude Desktop
TRANSPORT=stdio

# Required API keys
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Optional: Configure RAG strategies as needed
USE_HYBRID_SEARCH=true
USE_RERANKING=false
```

### Step 3: Setup Supabase Database

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Open the SQL Editor
3. Run the contents of `crawled_pages.sql` to create required tables

### Step 4: Test the Server

Before connecting to Claude Desktop, verify the server works:

```bash
# Using the wrapper script (recommended)
python run_mcp.py

# Or using platform-specific scripts
./run_mcp.sh  # Mac/Linux
run_mcp.bat   # Windows
```

You should see: "Starting Crawl4AI RAG MCP Server..."

Press `Ctrl+C` to stop the test.

## Claude Desktop Configuration

### Method 1: Using the Wrapper Script (Recommended)

The wrapper script automatically loads your `.env` file, so you don't need to specify credentials in Claude's config.

#### Find your Claude Desktop configuration file:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

#### Edit the configuration:

```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/mcp-crawl4ai-rag",
        "python",
        "run_mcp.py"
      ]
    }
  }
}
```

**Important:** Replace `/absolute/path/to/mcp-crawl4ai-rag` with your actual project path.

### Method 2: Using Platform-Specific Scripts

**For Windows:**
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "C:\\path\\to\\mcp-crawl4ai-rag\\run_mcp.bat"
    }
  }
}
```

**For Mac/Linux:**
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "/path/to/mcp-crawl4ai-rag/run_mcp.sh"
    }
  }
}
```

Note: Make the shell script executable first:
```bash
chmod +x run_mcp.sh
```

### Method 3: Manual Configuration (Not Recommended)

If you prefer to specify all environment variables in the Claude config:

```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-crawl4ai-rag",
        "python",
        "src/crawl4ai_mcp.py"
      ],
      "env": {
        "TRANSPORT": "stdio",
        "OPENAI_API_KEY": "your_key",
        "SUPABASE_URL": "your_url",
        "SUPABASE_SERVICE_KEY": "your_key",
        "USE_HYBRID_SEARCH": "true"
      }
    }
  }
}
```

## Verify Connection

1. **Restart Claude Desktop** completely (quit and reopen)
2. **Test the connection** by asking Claude:
   - "What MCP tools do you have available?"
   - "Can you see the crawl4ai tools?"

You should see these tools:
- `crawl_single_page` - Crawl a single webpage
- `smart_crawl_url` - Intelligently crawl websites
- `get_available_sources` - List crawled sources
- `perform_rag_query` - Search crawled content

## Usage Examples

Once connected, try these commands in Claude Desktop:

```
"Crawl the OpenAI documentation at https://platform.openai.com/docs"

"Search for information about GPT-4 from the crawled content"

"What sources have I crawled so far?"

"Crawl this sitemap: https://example.com/sitemap.xml"
```

## Advanced Configuration

### Enable Code Example Extraction

In your `.env` file:
```env
USE_AGENTIC_RAG=true
MODEL_CHOICE=gpt-4o-mini  # For code summaries
```

This enables the `search_code_examples` tool for finding code snippets.

### Enable Knowledge Graph (AI Hallucination Detection)

1. **Install Neo4j** (see main README for details)
2. **Configure in `.env`**:
```env
USE_KNOWLEDGE_GRAPH=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

This enables:
- `parse_github_repository` - Parse repos into knowledge graph
- `check_ai_script_hallucinations` - Validate AI-generated code
- `query_knowledge_graph` - Explore the graph

## Troubleshooting

### Server doesn't appear in Claude

1. **Check configuration syntax** - Ensure valid JSON
2. **Verify paths** - Use absolute paths, not relative
3. **Check quotes** - Use proper JSON quotes (")
4. **Restart Claude** - Fully quit and restart

### Server fails to start

1. **Test manually**:
```bash
python run_mcp.py
```

2. **Check dependencies**:
```bash
uv pip list  # Should show crawl4ai, supabase, etc.
```

3. **Verify .env file**:
```bash
# Check if .env exists and has required keys
cat .env | grep OPENAI_API_KEY
```

### Common Error Messages

**"Missing required environment variables"**
- Ensure your `.env` file contains all required API keys

**"Error importing MCP server"**
- Run `uv pip install -e .` and `crawl4ai-setup`

**"Cannot connect to Supabase"**
- Verify SUPABASE_URL and SUPABASE_SERVICE_KEY are correct
- Ensure you've run the SQL setup script

### Getting Help

- Check the [main README](README.md) for detailed feature documentation
- Review your `.env.example` for all configuration options
- Check Claude Desktop logs for detailed error messages
- Open an issue on GitHub if you encounter bugs

## Tips for Best Experience

1. **Start small** - Crawl individual pages before attempting large sites
2. **Use source filtering** - When searching, specify the source for better results
3. **Monitor usage** - Large crawls consume OpenAI API credits for embeddings
4. **Regular cleanup** - Periodically review and clean up old sources in Supabase

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and rotate them regularly
- Use read-only database credentials when possible
- Be mindful of what sites you crawl (respect robots.txt)
