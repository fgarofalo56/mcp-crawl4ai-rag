# MCP Crawl4AI RAG Server

> **Model Context Protocol (MCP) Server** providing intelligent web crawling, RAG (Retrieval Augmented Generation), and knowledge graph capabilities with AI hallucination detection.

**Version**: 2.0.0 (Modular Refactored)
**Python**: 3.10+
**Package Manager**: uv
**MCP Framework**: FastMCP v2.12.4

**🎉 Major Update**: v2.0.0 features complete modular refactoring - monolithic `crawl4ai_mcp.py` (2000+ lines) split into organized `src/core/` and `src/tools/` modules.

---

## 🎯 Project Purpose

This MCP server enables AI assistants to:
1. **Crawl web content** intelligently with multiple strategies (stealth mode, multi-URL, memory monitoring)
2. **Store and search** using vector embeddings (Supabase + pgvector)
3. **Build knowledge graphs** from documentation and code repositories (Neo4j)
4. **Detect AI hallucinations** by validating code against parsed repository structures
5. **Perform GraphRAG queries** combining vector search with graph-based entity relationships

**Primary Use Case**: Provide Claude Desktop and other MCP clients with production-ready web research and code analysis capabilities.

---

## 📋 Repository Organization Rules

### **CRITICAL: Documentation Organization Standards**

This project enforces strict file organization to maintain a clean, navigable codebase. **All contributors and AI assistants MUST follow these rules.**

#### **Root-Level Files (ONLY these are allowed)**

```
mcp-crawl4ai-rag/
├── README.md           # Project overview and quick start
├── CLAUDE.md           # AI assistant instructions (this file)
├── LICENSE             # License file
├── .gitignore          # Git ignore patterns
├── pyproject.toml      # Python project configuration
├── pytest.ini          # Test configuration
├── run_mcp.py          # MCP server entry point
├── docker-compose.yml  # Docker configuration
└── Dockerfile          # Docker build instructions
```

**STRICT RULES**:
1. **ONLY 2 .md files allowed in root**: `README.md` and `CLAUDE.md`
2. **ALL other documentation** → `docs/` (including CHANGELOG.md, CONTRIBUTING.md)
3. **ALL work outputs** (reports, summaries, action plans) → `project_tracking/`
4. **Configuration directories stay in place**: `.serena/`, `.claude/`, `.github/`, etc.

**Violation of these rules will result in file reorganization and PR rejection.**

#### **Documentation Structure (docs/)**

All documentation MUST be organized in the following structure:

```
docs/
├── README.md                    # Documentation hub and index
├── CHANGELOG.md                 # Version history and release notes ✅
├── CONTRIBUTING.md              # Contribution guidelines ✅
├── API_REFERENCE.md             # Complete API documentation
├── ARCHITECTURE.md              # System design and architecture
├── QUICK_START.md               # Developer quick reference
├── PROJECT_MANAGEMENT.md        # Task and sprint tracking guide
├── PROJECT_STATUS.md            # Current development state
├── WORKFLOW_QUICK_REFERENCE.md  # Common workflows
│
├── guides/                      # User and developer guides
│   ├── INDEX.md                # Guide catalog
│   ├── MARKDOWN_STYLE_GUIDE.md # Documentation standards
│   ├── SCALING_GUIDE.md        # Production deployment
│   ├── TROUBLESHOOTING.md      # Problem-solving guide
│   ├── TEST_COVERAGE_SUMMARY.md
│   ├── TEST_EXECUTION_GUIDE.md
│   └── TESTING_QUICK_START.md
│
├── fixes/                       # Technical fixes and solutions
│   ├── INDEX.md                # Fix documentation catalog
│   ├── NEO4J_FIX.md            # Neo4j connection issues
│   ├── AZURE_OPENAI_FIX.md     # Azure OpenAI configuration
│   ├── GRAPHRAG_FIX.md         # GraphRAG implementation fixes
│   ├── LAZY_LOADING_CLEANUP_FIX.md
│   └── STDOUT_CONTAMINATION_FIX.md
│
├── development/                 # Development reports and progress
│   ├── INDEX.md                # Development documentation catalog
│   ├── REFACTORING_*.md        # Refactoring reports
│   ├── IMPLEMENTATION_*.md     # Implementation summaries
│   ├── TEST_*.md               # Testing reports
│   └── *_REPORT.md             # Various development reports
│
└── archive/                     # Historical documentation
    ├── INDEX.md                # Archive catalog
    ├── README.md               # Archive documentation
    └── *.md                    # Archived historical documents
```

#### **Special Folders**

```
project_tracking/               # Sprint, task management, AND work outputs ⭐
├── sprints/current/           # Active sprint tracking
├── templates/                 # Task/sprint templates
├── decisions/                 # Architecture decision records
├── reports/                   # AI-generated reports (reviews, validations, analyses) ✅ NEW
├── summaries/                 # Work summaries (refactoring, documentation, implementation) ✅ NEW
├── action-plans/              # Action plans and implementation plans ✅ NEW
└── reviews/                   # Code reviews and audit reports ✅ NEW

.serena/memories/              # AI assistant persistent memory (DO NOT MOVE)
.claude/                       # Claude Code configuration (DO NOT MOVE)
├── commands/                  # Custom slash commands
├── agents/                    # Custom agent configurations
└── docs/                      # Claude Code documentation
```

**Work Output Policy**:
- **ALL** reports, summaries, action plans, reviews, analyses generated during work → `project_tracking/`
- **Purpose**: Keep work artifacts organized and separate from project documentation
- **Examples**: Refactoring summaries, audit reports, validation results, code reviews
- **DO NOT** create these files in root or docs/ - they belong in `project_tracking/`

### **Markdown Style Guide Compliance**

**ALL markdown files MUST comply with** `docs/guides/MARKDOWN_STYLE_GUIDE.md`:

#### **Required Standards**

1. **File Naming**:
   - Use SCREAMING_SNAKE_CASE for documentation: `API_REFERENCE.md`, `QUICK_START.md`
   - Exception: index files use lowercase: `index.md` or `INDEX.md` (consistent per folder)

2. **File Headers**:
   ```markdown
   # 🚀 Document Title

   Brief 1-2 sentence description of the document's purpose.

   ## Table of Contents
   - [Section 1](#section-1)
   - [Section 2](#section-2)
   ```

3. **Icon Usage**:
   - Use consistent icons per the style guide (🚀 for getting started, 📖 for documentation, etc.)
   - Include icons in H1 and H2 headings for visual navigation

4. **Code Blocks**:
   - Always specify language for syntax highlighting
   - Include comments in code examples
   - Test all code snippets for accuracy

5. **Links**:
   - Use relative paths for internal documentation
   - Verify all links work correctly
   - Use descriptive link text (not "click here")

6. **Line Length**:
   - 100 characters maximum (except code blocks)
   - Use markdownlint to enforce

### **File Reorganization Rules**

When reorganizing or creating documentation:

1. **Determine Document Type**:
   - **Guide**: → `docs/guides/`
   - **Fix/Solution**: → `docs/fixes/`
   - **Development Report**: → `docs/development/`
   - **Historical/Completed**: → `docs/archive/`
   - **Top-Level Reference**: → `docs/` (only major documents)

2. **Update All Links**:
   - Search for references to the moved file
   - Update relative paths in all linking documents
   - Test links after moving

3. **Update Index Files**:
   - Add entry to appropriate INDEX.md
   - Update docs/README.md if top-level guide
   - Maintain alphabetical order in indexes

4. **Git Operations**:
   - Use `git mv` to preserve history
   - Commit with descriptive message: `docs: move X to docs/category/ for organization`

### **Validation Checklist**

Before committing any documentation:

- [ ] File is in correct `docs/` subfolder (not root)
- [ ] Follows MARKDOWN_STYLE_GUIDE.md format
- [ ] Has proper header with title and description
- [ ] Includes table of contents (if > 3 sections)
- [ ] All code snippets tested and working
- [ ] All links verified and working
- [ ] Added to appropriate INDEX.md
- [ ] No trailing whitespace or extra blank lines
- [ ] Passes markdownlint checks

### **Enforcement**

- **AI Assistants**: MUST check file location before creating/editing documentation
- **Pre-commit Hooks**: Run markdownlint on all .md files
- **CI/CD**: GitHub Actions validates documentation structure
- **Code Review**: PRs with documentation must pass organization checks

**Violation of these rules will result in PR rejection.**

---

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (FastMCP)                      │
├─────────────────────────────────────────────────────────────┤
│  16 MCP Tools:                                              │
│  - Web Crawling (6 tools)                                   │
│  - RAG Queries (2 tools)                                    │
│  - Knowledge Graph (4 tools)                                │
│  - Source Management (2 tools)                              │
│  - AI Hallucination Detection (2 tools)                     │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Crawl4AI      │  │    Supabase      │  │     Neo4j        │
│   v0.7.4        │  │  (PostgreSQL +   │  │  (Knowledge      │
│  (Web Crawler)  │  │   pgvector)      │  │   Graph)         │
└─────────────────┘  └──────────────────┘  └──────────────────┘
```

### Technology Stack

- **MCP Framework**: FastMCP (official Anthropic SDK)
- **Web Crawling**: Crawl4AI with Playwright (supports stealth mode)
- **Vector Database**: Supabase (PostgreSQL with pgvector extension)
- **Graph Database**: Neo4j for entity relationships and code structure
- **Embeddings**: Azure OpenAI (text-embedding-3-small, configurable)
- **Testing**: pytest, pytest-asyncio (current coverage: 32%, target: 70%)
- **Code Quality**: Black (100 char lines), Ruff, mypy
- **CI/CD**: GitHub Actions with automated testing

---

## 📁 Project Structure

### Key Directories

```
mcp-crawl4ai-rag/
├── src/                          # Main source code (v2.0.0 modular structure)
│   ├── server.py                # Main entry point (147 lines) ✅
│   ├── core/                    # Core infrastructure ✅
│   │   ├── lifespan.py         # Lifecycle management (197 lines)
│   │   ├── context.py          # Crawl4AIContext dataclass
│   │   └── browser_validation.py # Playwright validation
│   ├── tools/                   # MCP tool implementations ✅
│   │   ├── crawling_tools.py   # 5 crawling tools
│   │   ├── rag_tools.py        # 2 RAG query tools
│   │   ├── graphrag_tools.py   # 4 GraphRAG tools
│   │   ├── source_tools.py     # 1 source management tool
│   │   └── knowledge_graph_tools.py # 4 code KG tools
│   ├── utils.py                 # Core utilities (Supabase, embeddings) ✅
│   ├── rag_utils.py            # RAG-specific functions ✅
│   ├── search_utils.py         # Search strategies and helpers ✅
│   ├── crawling_utils.py       # Crawling helpers ✅
│   ├── github_utils.py          # GitHub batch processing ✅
│   ├── memory_monitor.py        # Memory monitoring utilities ✅
│   ├── initialization_utils.py  # Startup logic ✅
│   ├── graphrag_utils.py       # GraphRAG utilities ✅
│   ├── knowledge_graph_commands.py # KG command patterns ✅
│   ├── logging_config.py        # Logging setup
│   └── archive/                 # Archived code ✅
│       └── crawl4ai_mcp.py.original # Old monolithic file (2000+ lines)
│
├── knowledge_graphs/             # Neo4j knowledge graph tools ✅
│   ├── __init__.py              # Module initialization
│   ├── parse_repo_into_neo4j.py # Repository structure parser
│   ├── ai_hallucination_detector.py  # AI code validation
│   ├── document_entity_extractor.py  # GraphRAG entity extraction
│   └── document_graph_validator.py   # Graph validation
│
├── tests/                        # Test suite (64 tests, 32% coverage)
│   ├── test_*.py                # Unit tests
│   ├── integration/             # Integration tests (in progress)
│   └── conftest.py              # Shared fixtures
│
├── docs/                         # Comprehensive documentation (42 docs) ✅
│   ├── README.md                # Documentation hub
│   ├── API_REFERENCE.md         # All 16 tools documented
│   ├── QUICK_START.md           # Developer quick reference
│   ├── ARCHITECTURE.md          # System design
│   ├── GRAPHRAG_GUIDE.md        # GraphRAG features
│   ├── PROJECT_MANAGEMENT.md    # Task tracking system ⭐
│   ├── fixes/                   # Technical fixes (Neo4j, Azure, GraphRAG) 🆕
│   ├── guides/                  # User guides (with INDEX.md)
│   │   ├── SCALING_GUIDE.md    # Production deployment
│   │   └── TROUBLESHOOTING.md  # Common issues
│   ├── development/             # Development reports (with INDEX.md)
│   └── archive/                 # Historical documentation (with INDEX.md)
│
├── project_tracking/             # Sprint & task management ⭐ NEW
│   ├── sprints/current/         # Active sprint tracking
│   │   ├── sprint-current.md   # Sprint 1 (Oct 7-28, 2025)
│   │   └── task-*.md           # Individual task files
│   ├── templates/               # Task, sprint, decision templates
│   ├── scripts/                 # Helper scripts
│   └── decisions/               # Architecture decision records
│
├── .serena/                      # Serena MCP integration
│   └── memories/                # Persistent context (workflows, conventions)
│
├── .claude/commands/             # Custom slash commands (29 total)
│   ├── primer.md                # Project onboarding
│   ├── task-*.md                # Task management (4 MCP-specific) ⭐
│   └── ...                      # Git, docs, code review commands
│
├── .github/workflows/            # CI/CD pipelines
│   └── test.yml                 # Automated testing on push/PR
│
├── pyproject.toml               # Project dependencies (uv)
├── pytest.ini                   # Test configuration
└── run_mcp.py                   # MCP server entry point
```

### Files That Need Frequent Updates

- `project_tracking/sprints/current/sprint-current.md` - Daily progress updates
- `project_tracking/sprints/current/task-*.md` - Task status tracking
- `CHANGELOG.md` - Version history (update for releases)
- `docs/PROJECT_STATUS.md` - Current development state
- `tests/test_*.py` - Test coverage (goal: 70%+)

---

## 🚀 Development Workflows

### Initial Setup

```bash
# 1. Clone and navigate
git clone <repo-url>
cd mcp-crawl4ai-rag

# 2. Install uv if not present
# See: https://docs.astral.sh/uv/

# 3. Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - SUPABASE_URL
# - SUPABASE_SERVICE_KEY
# - NEO4J credentials (if using knowledge graph)

# 5. Run tests to verify setup
pytest tests/
```

### Common Commands

```bash
# Run MCP server (stdio mode - for Claude Desktop)
python run_mcp.py

# Run tests
pytest tests/                          # All tests
pytest tests/test_utils.py            # Specific file
pytest -v --tb=short                  # Verbose with short tracebacks
pytest --cov=src --cov-report=html    # With coverage report

# Code quality checks
black src/ tests/                     # Format code (100 char lines)
ruff check src/ tests/                # Lint code
mypy src/                             # Type checking

# Docker deployment (with Neo4j)
docker-compose up --build             # Build and run
docker-compose down                   # Stop services

# Project management
/task-create-refactor                 # Create refactoring task
/task-create-feature                  # Create feature task
/task-status                          # Check task status
/sprint-status                        # Check sprint progress
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, test locally
pytest tests/

# Commit with conventional commits
git add .
git commit -m "feat: add new crawling strategy"
# Types: feat, fix, docs, test, refactor, style, chore

# Push and create PR
git push origin feature/your-feature-name
# CI will run tests automatically

# Merge after review
# Use squash merge to keep history clean
```

---

## 🧪 Testing Approach

### Current Status (as of Oct 14, 2025)

- **Total Tests**: 64 tests
- **Coverage**: 32% (target: 70%+)
- **Framework**: pytest with pytest-asyncio
- **CI/CD**: GitHub Actions runs on all PRs

### Test Organization

```python
# Unit tests (test individual functions)
tests/test_utils.py              # Supabase, embeddings, document ops
tests/test_github_utils.py       # GitHub batch processing (23/25 passing)
tests/test_crawling_strategies.py  # Crawling patterns
tests/test_memory_monitor.py     # Memory monitoring

# Integration tests (test workflows end-to-end)
tests/integration/test_crawl_workflows.py      # Full crawl pipeline
tests/integration/test_rag_pipeline.py         # RAG query workflow
tests/integration/test_knowledge_graph.py      # Neo4j integration
```

### Writing Tests

```python
# Unit test example
import pytest
from src.utils import generate_embeddings

def test_generate_embeddings_success():
    """Test successful embedding generation."""
    text = "test content"
    embedding = generate_embeddings(text)

    assert embedding is not None
    assert len(embedding) == 1536  # text-embedding-3-small dimension
    assert all(isinstance(x, float) for x in embedding)

# Async test example
@pytest.mark.asyncio
async def test_async_processing():
    """Test async repository processing."""
    result = await process_single_repository(repo_info, extractor, semaphore, max_retries=3)
    assert result["status"] == "success"
```

### Test Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
addopts = -v --strict-markers --tb=short --cov=src --cov-report=html
asyncio_mode = auto  # Required for async tests
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

---

## 📐 Code Style & Standards

### Python Style

- **Line Length**: 100 characters (Black)
- **Formatter**: Black with `--line-length 100`
- **Linter**: Ruff with strict rules
- **Type Hints**: Required on all new functions
- **Docstrings**: Google style for all public functions

```python
def process_repository(
    repo_url: str,
    max_retries: int = 3,
    timeout: int = 30
) -> Dict[str, Any]:
    """Process a GitHub repository and extract structure.

    Args:
        repo_url: GitHub repository URL (https://github.com/user/repo.git)
        max_retries: Maximum retry attempts for transient failures
        timeout: Operation timeout in seconds

    Returns:
        Processing result with status, statistics, and error info

    Raises:
        ValueError: If repo_url is invalid
        TimeoutError: If operation exceeds timeout
    """
    # Implementation
    pass
```

### Function Size Limits

- **Target**: All functions < 150 lines
- **Current Status**: 11 functions > 150 lines (Sprint 1 goal: refactor all)
- **Pattern**: Extract helper functions, use strategy pattern for complexity

### Refactoring Pattern (Proven in Task-001)

1. **Extract validation functions** (input checking, URL validation)
2. **Extract statistics functions** (calculation, aggregation)
3. **Extract formatting functions** (console output, response building)
4. **Extract processing functions** (core business logic)
5. **Add comprehensive tests** (90%+ coverage on extracted functions)
6. **Document** (Google-style docstrings, inline comments)

---

## 📊 Current Sprint: Sprint 1 (Oct 7-28, 2025)

### Sprint Goal
Improve code maintainability and test coverage to production-grade quality.

### Sprint Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Functions < 150 lines | 100% (11 total) | 9% (1/11) | 🟡 In Progress |
| Test Coverage | 70% | 32% | 🟡 In Progress |
| Integration Tests | 20+ | 0 | 🔴 Not Started |
| P0 Tasks Complete | 2 | 1 (50%) | 🟡 On Track |

### Active Tasks

**P0 (Critical - Must Complete)**
- ✅ Task-001: Refactor `parse_github_repositories_batch` (274 → 140 lines) **COMPLETED**
- ⏳ Task-002: Refactor `smart_crawl_url` (232 lines) **NEXT UP**

**P1 (High Priority)**
- Task-003: Add Integration Tests for Crawl Workflows
- Task-004: Add Integration Tests for RAG Pipeline
- Task-005: Refactor `crawl_with_memory_monitoring` (193 lines)
- Task-006: Refactor `query_knowledge_graph` (181 lines)

### How to Update Sprint Progress

```bash
# 1. Check current sprint status
/sprint-status

# 2. When starting a task
# Update task-*.md file: status: todo → in_progress
# Update sprint-current.md daily progress log

# 3. When completing a task
# Update task-*.md file: status: in_progress → completed
# Update sprint-current.md:
#   - Mark task as completed with checkmark
#   - Update metrics
#   - Add to daily progress log

# 4. Daily updates
# Add entry to sprint-current.md "Daily Progress Log" section
# Update sprint metrics table
```

---

## 🔧 Key Technical Concepts

### MCP (Model Context Protocol)
- **Purpose**: Standard protocol for AI assistants to interact with external tools
- **Framework**: FastMCP (official Anthropic Python SDK)
- **Transport**: stdio (Claude Desktop) or HTTP (server mode)
- **Tools**: 16 tools exposed via MCP (see API_REFERENCE.md)

### RAG (Retrieval Augmented Generation)
- **Strategy**: Vector search with optional enhancements
- **Embeddings**: Azure OpenAI text-embedding-3-small (1536 dimensions)
- **Database**: Supabase PostgreSQL with pgvector extension
- **Enhancements**: Contextual embeddings, hybrid search, agentic RAG, reranking

### GraphRAG
- **Concept**: Combine vector search with knowledge graph traversal
- **Use Case**: Better answers for questions involving entity relationships
- **Implementation**: Supabase (documents) + Neo4j (entity relationships)
- **Workflow**: Crawl → Extract entities → Build graph → Enhanced queries

### Knowledge Graph (Neo4j)
- **Purpose**: Store code structure for AI hallucination detection
- **Schema**: Repository → File → Class → Method/Function → Attribute
- **Use Case**: Validate AI-generated code against real repository structure
- **Tools**: Parse repo, query graph, detect hallucinations

### AI Hallucination Detection
- **Problem**: AI assistants may generate code with non-existent methods/classes
- **Solution**: Parse real repositories into Neo4j, validate generated code
- **Checks**: Import validation, method calls, class instantiation, function calls, attributes
- **Result**: Confidence score + specific issues + recommendations

---

## 🎓 Development Guidelines

### Before Starting Work

1. **Check sprint status**: `/sprint-status` or read `project_tracking/sprints/current/sprint-current.md`
2. **Review related tasks**: Check task dependencies in sprint backlog
3. **Read documentation**: Relevant guides in `docs/` directory
4. **Set up environment**: Ensure .env configured with all required keys

### During Development

1. **Create task file** (if new work): Use `/task-create-*` commands or templates
2. **Write tests first** (TDD): Create test file before implementation
3. **Keep functions small**: Target < 150 lines, extract helpers early
4. **Add type hints**: All function parameters and return types
5. **Document as you go**: Google-style docstrings for public functions
6. **Update sprint daily**: Add progress to sprint-current.md daily log

### Before Committing

```bash
# 1. Format code
black src/ tests/

# 2. Check linting
ruff check src/ tests/

# 3. Type check
mypy src/

# 4. Run relevant tests
pytest tests/test_your_module.py -v

# 5. Check coverage (if modifying existing code)
pytest --cov=src.your_module --cov-report=term-missing

# 6. Update documentation
# - Update CHANGELOG.md if user-facing change
# - Update API_REFERENCE.md if tool signature changed
# - Update task-*.md with progress
# - Update sprint-current.md daily log
```

### When Completing a Task

1. **Mark task complete**: Update task-*.md file status
2. **Update sprint metrics**: Update sprint-current.md metrics table
3. **Add to daily log**: Document completion in sprint daily progress
4. **Create PR**: Use conventional commit message
5. **Update documentation**: If applicable (API changes, new features)

---

## 🚨 Common Pitfalls & Solutions

### Problem: Tests Failing with Async Errors
**Symptom**: "async def functions are not natively supported"
**Solution**: Ensure `asyncio_mode = auto` in pytest.ini and pytest-asyncio installed

### Problem: Print/Output Not Captured in Tests
**Symptom**: Tests checking captured output find empty string
**Solution**: Check if function prints to stderr (`sys.stderr`) - use `captured.err` not `captured.out`

### Problem: Coverage Below Threshold
**Symptom**: "Coverage failure: total of X is less than fail-under=29"
**Solution**:
- For full test run: Add more tests to reach 29%+ overall
- For single file testing: Use `pytest --no-cov` to skip coverage check

### Problem: Neo4j Connection Failed
**Symptom**: "Failed to connect to Neo4j"
**Solution**: Check docs/fixes/NEO4J_FIX.md - ensure Neo4j running, credentials correct, bolt:// protocol

### Problem: Supabase Embeddings Slow
**Symptom**: Embedding generation taking > 5 seconds
**Solution**:
- Check Azure OpenAI quota/rate limits
- Consider batch embedding generation
- Use caching for repeated content

### Problem: Task Context Lost Between Sessions
**Symptom**: Forgetting what was being worked on
**Solution**:
- **Prevention**: Use project_tracking/ system, update sprint-current.md daily
- **Recovery**: Check `.serena/memories/` and `project_tracking/sprints/current/`
- **Best Practice**: Run `/sprint-status` at start of each session

---

## 📚 Essential Documentation

**Start Here**:
- `README.md` - Project overview and quick start
- `docs/README.md` - Documentation hub with all guides
- `docs/QUICK_START.md` - Developer quick reference

**For Development**:
- `docs/ARCHITECTURE.md` - System design and patterns
- `docs/PROJECT_MANAGEMENT.md` - Task tracking system ⭐
- `docs/CODE_QUALITY_IMPROVEMENTS.md` - Code standards
- `CONTRIBUTING.md` - Contribution guidelines

**For Features**:
- `docs/API_REFERENCE.md` - All 16 MCP tools documented
- `docs/GRAPHRAG_GUIDE.md` - Knowledge graph features
- `docs/NEW_FEATURES_GUIDE.md` - Advanced crawling modes
- `docs/guides/SCALING_GUIDE.md` - Production deployment

**For Troubleshooting**:
- `docs/guides/TROUBLESHOOTING.md` - Comprehensive guide
- `docs/fixes/` - Technical fixes (Neo4j, Azure OpenAI, GraphRAG)
- `docs/DOCKER_SETUP.md` - Docker deployment

---

## 🎯 Project Management System

This project uses a **3-layer tracking system** to prevent task loss:

### Layer 1: Sprint Tracking
**Location**: `project_tracking/sprints/current/sprint-current.md`
- Active sprint goals and metrics
- Daily progress log
- Task backlog with priorities
- Updated daily with progress

### Layer 2: Task Tracking
**Location**: `project_tracking/sprints/current/task-*.md`
- Individual task files with detailed status
- Acceptance criteria, dependencies, progress
- Implementation plans and test requirements
- Updated as task progresses

### Layer 3: Persistent Memory
**Location**: `.serena/memories/`
- Cross-session context preservation
- Workflow documentation
- Project conventions
- Automatically updated by Serena MCP

### Key Commands

```bash
/task-create-refactor    # Create refactoring task
/task-create-feature     # Create feature task
/task-status             # Check task status
/sprint-status           # Check sprint progress
/primer:primer-team      # Full project onboarding
```

**Best Practice**: Start each session with `/sprint-status` to see current work and priorities.

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
**File**: `.github/workflows/test.yml`

**Triggers**:
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install uv package manager
4. Install dependencies with uv
5. Run pytest with coverage
6. Upload coverage reports

**Requirements for PR Merge**:
- ✅ All tests passing
- ✅ Coverage ≥ 29% (will increase to 70% in Sprint 1)
- ✅ No linting errors (Ruff)
- ✅ Code formatted (Black)

---

## 💡 Tips for Working with This Codebase

1. **Always check sprint status first**: Prevents duplicate work and context loss
2. **Use templates**: task-template.md, sprint-template.md, decision-template.md
3. **Write tests before code**: TDD approach catches issues early
4. **Keep functions small**: Extract helpers when approaching 100 lines
5. **Document as you go**: Easier than documenting later
6. **Update daily**: Sprint progress log helps maintain context
7. **Use slash commands**: 29 custom commands available in `.claude/commands/`
8. **Check CI before pushing**: Run pytest locally to catch failures early
9. **Read error messages carefully**: Many have solutions in TROUBLESHOOTING.md
10. **Leverage existing patterns**: See completed Task-001 for refactoring example

---

## 🔗 External Resources

- **MCP Specification**: https://modelcontextprotocol.io
- **FastMCP SDK**: https://github.com/anthropics/anthropic-mcp-sdk-python
- **Crawl4AI Docs**: https://crawl4ai.com
- **Supabase Docs**: https://supabase.com/docs (pgvector)
- **Neo4j Docs**: https://neo4j.com/docs
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/

---

**Last Updated**: October 28, 2025 by Claude (Documentation Management Specialist)
**Project Status**: 🟢 Active Development - Sprint 1 In Progress
**Next Sprint Planning**: October 28, 2025

For questions or issues, see `docs/guides/TROUBLESHOOTING.md` or create a GitHub issue.
