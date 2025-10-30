# Project Current State

**Last Updated**: 2025-10-29
**Version**: 2.0.0
**Sprint**: Sprint 1 - Code Quality & Testing Improvements (Week 3, Final Week)

## Quick Context

The MCP-Crawl4AI-RAG server is a production-ready Model Context Protocol server providing web crawling and RAG capabilities to AI agents. **Version 2.0.0** features a complete modular refactoring from monolithic architecture to organized src/core/ and src/tools/ structure. The project is in the final week of Sprint 1, focused on code quality and testing improvements.

## Current Sprint Goals

### Primary Objectives
1. **Refactor Large Functions**: 11 functions > 150 lines need breakdown
2. **Improve Test Coverage**: From 30% to 70%+
3. **Add Integration Tests**: Create end-to-end test suite

### Sprint Timeline
- **Start**: 2025-10-07
- **End**: 2025-10-28
- **Duration**: 3 weeks
- **Status**: Week 3 (final week), All P0 tasks completed

## Active Work

### Completed (Sprint 1)
- [x] **Architecture Refactoring** (v2.0.0): Monolithic → Modular structure
- [x] Created `project_tracking/` directory structure
- [x] Created task, sprint, and decision templates
- [x] Created 4 MCP-specific slash commands
- [x] Initialized Sprint 1 tracking file
- [x] Updated Serena memories with workflow
- [x] **Task-001** (P0): Refactored `parse_github_repositories_batch` (274 → 140 lines)
- [x] **Task-002** (P0): Refactored `smart_crawl_url` (232 → 79 lines)
- [x] **Task-013** (P0): Fixed Playwright browser detection bug
- [x] **Task-011** (P1): Fixed source_filter parameter bug
- [x] **Task-012** (P1): Fixed stdout contamination bug

### In Progress
1. **Integration Tests**: Creating test infrastructure (tests/integration/)
2. **P1 Tasks**: Additional refactoring and testing

## Recent Achievements

### October 2-13, 2025
- ✅ Documentation consolidation (23 → 16 docs, 30% reduction)
- ✅ Created 6 utility modules with 90%+ test coverage
- ✅ 64 tests passing
- ✅ Neo4j connection reliability improvements
- ✅ Azure OpenAI configuration updates

### October 14, 2025
- ✅ Complete project tracking infrastructure
- ✅ Sprint planning and task breakdown
- ✅ Custom slash commands for MCP development
- ✅ Task-001 & Task-002 completed (P0 refactoring)
- ✅ Task-011 & Task-012 completed (critical bug fixes)

### October 17-28, 2025
- ✅ **v2.0.0 Modular Architecture**: Complete refactoring from monolithic to modular structure
  - Split 2000+ line crawl4ai_mcp.py into organized modules
  - Created src/core/ for infrastructure (5 modules)
  - Created src/tools/ for MCP tools (5 category modules, 16 tools)
  - Created 20+ utility modules for specific concerns
  - Main entry point reduced to 147 lines (src/server.py)
  - Old file archived in src/archive/
- ✅ Task-013 completed: Fixed critical Playwright browser detection bug
- ✅ All P0 tasks and P0 bug fixes completed

## Known Issues & Blockers

### Current Blockers
None

### Technical Debt
1. **11 Large Functions**: Need refactoring to < 150 lines
   - Largest: `parse_github_repositories_batch` (274 lines)
   - Second: `smart_crawl_url` (232 lines)
2. **Low Overall Coverage**: 30% (target: 70%+)
3. **Missing Integration Tests**: 0 tests (need 20+)

## Project Structure (v2.0.0 - Modular Architecture)

### Key Directories
```
src/                          # Main source code (MODULAR)
├── server.py                # Main MCP server entry point (147 lines)
├── core/                    # Core infrastructure (5 modules)
│   ├── lifespan.py         # Lifecycle management
│   ├── context.py          # Crawl4AIContext dataclass
│   ├── browser_validation.py # Playwright validation
│   ├── validators.py       # Core validation
│   └── reranking.py        # Reranking utilities
├── tools/                   # MCP tool implementations (5 modules, 16 tools)
│   ├── crawling_tools.py   # 5 crawling tools
│   ├── rag_tools.py        # 2 RAG tools
│   ├── graphrag_tools.py   # 4 GraphRAG tools
│   ├── knowledge_graph_tools.py # 4 KG tools
│   └── source_tools.py     # 1 source tool
├── utils.py                # Core utilities (90%+ coverage)
├── rag_utils.py            # RAG-specific functions
├── search_utils.py         # Search strategies
├── crawling_utils.py       # Crawling helpers
├── crawling_strategies.py  # Crawling strategy pattern
├── github_utils.py         # GitHub batch processing
├── memory_monitor.py       # Memory monitoring
├── graphrag_utils.py       # GraphRAG utilities
├── knowledge_graph_commands.py # KG command patterns
├── (+ 10 more utility modules)
├── repositories/           # Data access layer (future)
├── services/               # Business logic layer (future)
├── middleware/             # Middleware (future)
└── archive/                # Archived code
    └── crawl4ai_mcp.py.original # Old 2000+ line monolith

knowledge_graphs/            # Neo4j knowledge graph code
tests/                       # Test suite (64+ tests, 32% coverage)
├── integration/            # Integration tests (IN PROGRESS)
└── (unit tests)
docs/                        # Documentation (42+ docs organized)
project_tracking/            # Sprint and task tracking
```

### Important Files
- `docs/PROJECT_STATUS.md` - High-level status
- `docs/ARCHITECTURE.md` - System architecture
- `project_tracking/sprints/current/sprint-current.md` - Active sprint
- `.serena/memories/` - Persistent project knowledge

## Technology Stack

### Core Dependencies
- **Python**: 3.10+ (3.12 recommended)
- **FastMCP**: 2.12.4 - MCP framework
- **Crawl4AI**: 0.7.4 - Web crawler
- **Supabase**: Vector database (PostgreSQL + pgvector)
- **Neo4j**: 5.0+ (optional) - Knowledge graph
- **OpenAI API**: Embeddings and LLM operations

### Development Tools
- **uv**: Fast package manager
- **pytest**: Testing (64 passing tests)
- **black**: Code formatting (100 char lines)
- **ruff**: Linting
- **mypy**: Type checking
- **Docker**: Containerization

## Development Workflow

### Starting New Work
1. Check `project_tracking/sprints/current/sprint-current.md`
2. Select highest priority `todo` task
3. Create or review task file
4. Update task status to `in_progress`
5. Work on implementation
6. Run tests: `pytest tests/ -v`
7. Update task status to `completed`

### Custom Slash Commands
- `/task-create-tool` - Create new MCP tool task
- `/task-create-refactor` - Create refactoring task
- `/task-create-test` - Create testing task
- `/task-create-rag-improvement` - Create RAG enhancement task

### Running Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_utils.py -v

# Integration tests (when ready)
pytest tests/integration/ -v
```

### Running Server
```bash
# Using wrapper script (recommended)
python run_mcp.py

# Or directly (v2.0.0)
python -m src.server

# Or with uv
uv run python -m src.server

# Or with Docker
docker-compose up -d
```

## Configuration

### Environment Variables (`.env`)
```bash
# MCP Server
HOST=0.0.0.0
PORT=8051
TRANSPORT=sse

# OpenAI
OPENAI_API_KEY=your_key

# Supabase
SUPABASE_URL=your_url
SUPABASE_SERVICE_KEY=your_key

# Optional: Neo4j
USE_KNOWLEDGE_GRAPH=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Optional: RAG Strategies
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false
```

## Common Tasks

### Creating a New MCP Tool (v2.0.0)
1. Use `/task-create-tool {tool_name}`
2. Follow generated task file
3. **Determine tool category**: crawling, rag, graphrag, knowledge_graph, or source
4. Implement in appropriate `src/tools/{category}_tools.py`
5. Register in `src/server.py` (add to tool registration section)
6. Add validation in `src/validators.py` or `src/core/validators.py`
7. Write tests in `tests/test_{tool_name}.py`
8. Update `docs/API_REFERENCE.md`

### Refactoring a Function
1. Use `/task-create-refactor {function_name}`
2. Analyze current function (lines, complexity)
3. Plan helper function extraction
4. Write tests for extracted functions
5. Refactor incrementally
6. Verify all tests still pass

### Adding Tests
1. Use `/task-create-test {test_area}`
2. Create test file in `tests/integration/`
3. Set up fixtures in `conftest.py`
4. Write test scenarios
5. Run and verify tests pass
6. Check coverage improvement

## Quick Reference

### Important Commands
```bash
# View current sprint
cat project_tracking/sprints/current/sprint-current.md

# View task file
cat project_tracking/sprints/current/task-001-*.md

# Check git status
git status

# View recent commits
git log --oneline -10

# Run linting
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

### Getting Help
- Check `docs/QUICK_START.md` for developer setup
- Check `docs/CONTRIBUTING.md` for coding standards
- Check `.serena/memories/task_completion_checklist.md` for task workflow
- Check `project_tracking/sprints/current/sprint-current.md` for current work

## Next Steps

### Immediate (This Week - Sprint End Oct 28)
1. Complete Sprint 1 retrospective
2. Document lessons learned
3. Plan Sprint 2

### Short-term (Post-Sprint)
1. Continue P1 tasks (integration tests, remaining refactoring)
2. Improve test coverage toward 70% goal
3. Address any remaining technical debt

### Long-term (Sprint 2+)
1. Complete remaining refactorings (9/11 functions still need work)
2. Achieve 70%+ test coverage
3. Plan next sprint (potential: Ollama integration, performance optimization, or new features)

---

**Status**: 🟢 Sprint 1 Complete (All P0 Tasks Done)
**Next Review**: Sprint 1 Retrospective (2025-10-28)
**Last Major Change**: v2.0.0 Modular Architecture Refactoring
