# Suggested Commands for Development

## Setup and Installation

### Using uv (Recommended for development)
```bash
# Install uv if not already installed
pip install uv

# Create and activate virtual environment
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
uv pip install -e .

# Setup Crawl4AI
crawl4ai-setup
```

### Using Docker
```bash
# Build Docker image
docker build -t mcp/crawl4ai-rag --build-arg PORT=8051 .

# Run Docker container
docker run -d --env-file .env -p 8051:8051 mcp/crawl4ai-rag

# Run with auto-restart
docker run -d --env-file .env -p 8051:8051 --restart unless-stopped mcp/crawl4ai-rag
```

## Running the Server

### Direct Python execution
```bash
# With uv
uv run src/crawl4ai_mcp.py

# Or with Python directly (after activation)
python src/crawl4ai_mcp.py
```

### Environment Configuration
```bash
# Copy example environment file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Edit .env file with your credentials
```

## Knowledge Graph Tools (Optional)

### Parse a GitHub repository
```bash
python knowledge_graphs/parse_repo_into_neo4j.py https://github.com/user/repo.git
```

### Check for AI hallucinations in a script
```bash
python knowledge_graphs/ai_hallucination_detector.py path/to/script.py
```

### Query the knowledge graph
```bash
python knowledge_graphs/query_knowledge_graph.py
```

## Database Setup

### Supabase
1. Create a new project in Supabase
2. Go to SQL Editor in dashboard
3. Run the contents of `crawled_pages.sql`

### Neo4j (Optional)
1. Install Neo4j Desktop or use Docker
2. Create new database
3. Set credentials in .env file

## Common Windows Commands

### File Operations
```bash
# List files
dir /B
dir /S  # Recursive

# Find files
where *.py
dir /S /B *.py

# View file content
type filename.txt
more filename.txt

# Copy files
copy source.txt dest.txt
xcopy /E /I source_dir dest_dir  # Copy directory

# Delete files
del filename.txt
rmdir /S directory  # Remove directory
```

### Git Commands
```bash
# Basic Git operations
git status
git add .
git commit -m "message"
git push
git pull

# Branch operations
git branch
git checkout -b new-branch
git merge branch-name
```

### Python/uv Commands
```bash
# Check Python version
python --version

# Install packages
uv pip install package-name
uv pip install -r requirements.txt
uv pip install -e .  # Install in editable mode

# List installed packages
uv pip list
uv pip freeze

# Upgrade packages
uv pip install --upgrade package-name
```

## Development Workflow

1. Make changes to code
2. Test locally: `uv run src/crawl4ai_mcp.py`
3. Check for syntax errors: `python -m py_compile src/crawl4ai_mcp.py`
4. Commit changes: `git add . && git commit -m "description"`
5. Push to repository: `git push`

## Debugging

### View logs
```bash
# Run with verbose output
python src/crawl4ai_mcp.py

# Check Docker logs
docker logs container-name
```

### Test individual components
```bash
# Test imports
python -c "from src.utils import get_supabase_client"

# Test Neo4j connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))"
```