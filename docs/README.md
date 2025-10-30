# MCP Crawl4AI RAG - Documentation

Welcome to the documentation for the MCP Crawl4AI RAG server! This directory contains comprehensive guides and references for setting up, using, and maintaining the project.

**Last Updated**: October 14, 2025

## 📚 Quick Navigation

### 🚀 Getting Started

**New Users Start Here:**

1. **[Main README](../README.md)** - Project overview, features, and quick start
2. **[Claude Desktop Setup](CLAUDE_DESKTOP_SETUP.md)** - Step-by-step setup for Claude Desktop
3. **[Quick Start Guide](QUICK_START.md)** - Developer quick reference

**Deployment Options:**

- **[Docker Setup](DOCKER_SETUP.md)** - Docker deployment with Neo4j (recommended)
- **[Dual Mode Setup](DUAL_MODE_SETUP.md)** - Running stdio + HTTP transports simultaneously

---

### 📖 Core Documentation

#### Setup & Configuration

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) | Connect to Claude Desktop | Setting up MCP client |
| [DOCKER_SETUP.md](DOCKER_SETUP.md) | Docker deployment guide | Deploying with Docker |
| [DUAL_MODE_SETUP.md](DUAL_MODE_SETUP.md) | Multiple transport modes | Running both stdio and HTTP |

#### Features & Capabilities

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [GRAPHRAG_GUIDE.md](GRAPHRAG_GUIDE.md) | GraphRAG features (v1.2.0) | Using knowledge graphs |
| [NEW_FEATURES_GUIDE.md](NEW_FEATURES_GUIDE.md) | Advanced crawling (v1.1.0) | Stealth mode, multi-URL, memory monitoring |
| [Scaling Guide](guides/SCALING_GUIDE.md) | Production deployment (v1.3.0) | Large-scale operations, batch processing 🆕 |
| [API Reference](API_REFERENCE.md) | All 16 MCP tools | Looking up tool parameters |

#### Development

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [PROJECT_MANAGEMENT.md](PROJECT_MANAGEMENT.md) | Task & sprint tracking | Managing work, preventing task loss 🆕 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture | Understanding codebase structure |
| [CODE_QUALITY_IMPROVEMENTS.md](CODE_QUALITY_IMPROVEMENTS.md) | Code quality guide | Contributing or refactoring |
| [QUICK_START.md](QUICK_START.md) | Developer quick reference | Daily development |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines | Before submitting PRs |

#### DevOps & Testing

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [CI_CD.md](CI_CD.md) | CI/CD pipeline docs | Setting up workflows |
| [WORKFLOW_QUICK_REFERENCE.md](WORKFLOW_QUICK_REFERENCE.md) | Common workflows | Daily Git operations |
| [Testing Quick Start](guides/TESTING_QUICK_START.md) | Test suite information | Running tests |
| [Test Coverage Summary](guides/TEST_COVERAGE_SUMMARY.md) | Coverage metrics | Reviewing test status |
| [Test Execution Guide](guides/TEST_EXECUTION_GUIDE.md) | Running integration tests | Test execution |

---

### 🔧 Troubleshooting

#### Common issues

**Start Here**: [TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md) - Comprehensive troubleshooting guide

**Technical Fixes** (see [fixes/](fixes/) directory):
- **Neo4j Connection**: See [fixes/NEO4J_FIX.md](fixes/NEO4J_FIX.md)
- **Azure OpenAI Issues**: See [fixes/AZURE_OPENAI_FIX.md](fixes/AZURE_OPENAI_FIX.md)
- **GraphRAG Problems**: See [fixes/GRAPHRAG_FIX.md](fixes/GRAPHRAG_FIX.md)

**Setup Issues**:
- **Docker Issues**: See [DOCKER_SETUP.md](DOCKER_SETUP.md#troubleshooting)
- **Claude Desktop**: See [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md#troubleshooting)

---

### 📁 Reference Documentation

- **[API Reference](API_REFERENCE.md)** - Complete tool documentation
- **[Changelog](../CHANGELOG.md)** - Version history
- **[Project Status](PROJECT_STATUS.md)** - Current development status
- **[Test Coverage](guides/TEST_COVERAGE_SUMMARY.md)** - Testing metrics
- **[Documentation Reorganization Summary](DOCUMENTATION_REORGANIZATION_SUMMARY.md)** - File organization and validation status 🆕

### 📊 Development Reports

See [development/](development/) directory for:
- Complete development summary
- Refactoring reports (Phase 1, P0, P1, P2)
- Integration test reports
- Implementation summaries
- CI/CD implementation details

---

## 📋 Documentation by Task

### I want to...

**...get started quickly**
→ [Main README](../README.md) → [Claude Desktop Setup](CLAUDE_DESKTOP_SETUP.md)

**...deploy with Docker**
→ [Docker Setup](DOCKER_SETUP.md)

**...use GraphRAG features**
→ [GraphRAG Guide](GRAPHRAG_GUIDE.md)

**...use advanced crawling (stealth, multi-URL, memory monitoring)**
→ [New Features Guide](NEW_FEATURES_GUIDE.md)

**...deploy for production or scale to 1000+ pages**
→ [Scaling Guide](guides/SCALING_GUIDE.md)

**...troubleshoot connection issues**
→ [Troubleshooting](guides/TROUBLESHOOTING.md) → [Technical Fixes](fixes/)

**...contribute to the project**
→ [Contributing Guide](../CONTRIBUTING.md) → [Code Quality Improvements](CODE_QUALITY_IMPROVEMENTS.md)

**...understand the architecture**
→ [Architecture](ARCHITECTURE.md)

**...manage tasks and sprints (prevent task loss)**
→ [Project Management Guide](PROJECT_MANAGEMENT.md)

**...set up CI/CD**
→ [CI/CD Guide](CI_CD.md)

**...look up tool parameters**
→ [API Reference](API_REFERENCE.md)

**...review development reports and refactoring summaries**
→ [Development Reports](development/)

---

## 📦 Documentation Structure

```
docs/
├── README.md (this file)          # Documentation hub
├── API_REFERENCE.md                # Complete MCP tools reference
├── PROJECT_STATUS.md               # Current development status
│
├── 🚀 Getting Started
│   ├── CLAUDE_DESKTOP_SETUP.md    # Claude Desktop integration
│   ├── DOCKER_SETUP.md             # Docker deployment
│   ├── DUAL_MODE_SETUP.md          # Multiple transports
│   └── QUICK_START.md              # Developer quick reference
│
├── 📖 Features
│   ├── GRAPHRAG_GUIDE.md           # GraphRAG documentation
│   ├── NEW_FEATURES_GUIDE.md       # v1.1.0 features
│   └── CRAWLING_STRATEGIES_GUIDE.md # Crawling patterns
│
├── 🔧 Development
│   ├── PROJECT_MANAGEMENT.md        # Task & sprint tracking 🆕
│   ├── ARCHITECTURE.md             # System design
│   ├── CODE_QUALITY_IMPROVEMENTS.md # Code standards
│   └── WORKFLOW_QUICK_REFERENCE.md  # Git workflows
│
├── 🧪 DevOps
│   └── CI_CD.md                    # CI/CD pipelines
│
├── 🔨 fixes/                       # Technical fixes (organized) 🆕
│   ├── INDEX.md                    # Fixes directory index
│   ├── NEO4J_FIX.md                # Neo4j connection issues
│   ├── AZURE_OPENAI_FIX.md         # Azure OpenAI fixes
│   └── GRAPHRAG_FIX.md             # GraphRAG issues
│
├── 📚 guides/                      # User guides
│   ├── INDEX.md                    # Guides directory index 🆕
│   ├── SCALING_GUIDE.md            # Production deployment ⭐
│   ├── TROUBLESHOOTING.md          # Comprehensive troubleshooting ⭐
│   ├── TESTING_QUICK_START.md      # Test suite overview
│   ├── TEST_COVERAGE_SUMMARY.md    # Coverage metrics
│   └── TEST_EXECUTION_GUIDE.md     # Integration test execution
│
├── 📊 development/                 # Development reports
│   ├── INDEX.md                    # Development directory index 🆕
│   ├── COMPREHENSIVE_TEST_REPORT.md     # Test suite analysis 🆕
│   ├── INTEGRATION_TEST_REPORT.md       # Integration tests 🆕
│   ├── INTEGRATION_TESTS_SUMMARY.md     # Test overview 🆕
│   ├── REFACTORING_ARCHITECTURE.md      # Architecture refactor 🆕
│   ├── REFACTORING_CHECKLIST.md         # Refactor checklist 🆕
│   ├── REFACTORING_README.md            # Refactor overview 🆕
│   ├── REFACTORING_REPORT.md            # Refactor analysis 🆕
│   ├── REFACTORING_SUMMARY.md           # Refactor summary 🆕
│   ├── TEST_COVERAGE_IMPROVEMENT_REPORT.md # Coverage tracking 🆕
│   ├── TEST_SUMMARY.md                  # Test summary 🆕
│   ├── DEVELOPMENT_COMPLETE_SUMMARY.md  # Sprint summary
│   ├── PHASE1_REFACTORING_REPORT.md     # Phase 1 details
│   ├── REFACTORING_COMPLETE.md          # P0 completion
│   ├── PRIORITY_2_REFACTORING_SUMMARY.md # P2 summary
│   ├── INTEGRATION_TESTS_REPORT.md      # Test suite details
│   ├── BATCH_EXTRACTION_IMPLEMENTATION.md # GraphRAG batch
│   ├── BATCH_FUNCTION_REFACTORING.md    # GitHub utils refactor
│   ├── CI_CD_IMPLEMENTATION_REPORT.md   # CI/CD setup
│   ├── IMPLEMENTATION_SUMMARY.md        # Implementation notes
│   ├── DOCUMENTATION_UPDATE_SUMMARY.md  # Doc changes
│   └── WORK_COMPLETED_SUMMARY.md        # Work summary
│
└── 📁 archive/                     # Historical documentation
    ├── INDEX.md                    # Archive directory index 🆕
    ├── ARCHIVE_TASK_SUMMARY.md     # Task archive 🆕
    ├── ARCHIVE_VALIDATION_REPORT.md # Validation report 🆕
    ├── DEVELOPMENT_SPRINT_COMPLETE.md # Sprint complete 🆕
    ├── DOCKER_BUILD_FIX.md         # Docker fix 🆕
    ├── DOCUMENTATION_ARCHIVE_COMPLETE.md # Archive complete 🆕
    ├── MARKDOWN_STANDARDIZATION_COMPLETE.md # Markdown done 🆕
    ├── MARKDOWN_STANDARDIZATION_REPORT.md # Standards report 🆕
    └── [12 more historical documents]
```

---

## 🏷️ Document Status

All active documentation is up-to-date as of October 14, 2025.

| Category | Documents | Status |
|----------|-----------|--------|
| Setup & Configuration | 3 docs | ✅ Current |
| Features | 3 docs | ✅ Current |
| Development | 4 docs | ✅ Current |
| DevOps | 1 doc | ✅ Current |
| Technical Fixes | 3 docs (fixes/) | ✅ Current |
| Guides | 5 docs (+ INDEX) | ✅ Current |
| Development Reports | 21 docs (+ INDEX) | ✅ Current |
| Reference | 2 docs | ✅ Current |
| **Total Active Docs** | **42 docs** | **✅ Up-to-date** |

**Archived Documentation**: 19 historical documents in `archive/` (+ INDEX)
**Organization**: 4 INDEX.md files for improved navigation

---

## 🆕 Recent Updates

### October 14, 2025 - Documentation Organization & Project Management
- ✅ **NEW**: Organized 22 root-level markdown files into proper directories
- ✅ **NEW**: Created `docs/fixes/` directory for technical fix documentation
- ✅ **NEW**: Added 4 INDEX.md files for improved navigation
- ✅ **NEW**: PROJECT_MANAGEMENT.md - Complete project tracking guide
- ✅ Created `project_tracking/` directory structure
- ✅ Added task and sprint management helper scripts
- ✅ Created 4 MCP-specific slash commands
- ✅ Updated Serena memories with workflow documentation
- ✅ Moved 7 files to `docs/archive/` (historical work)
- ✅ Moved 10 files to `docs/development/` (development reports)
- ✅ Moved 3 fix files to `docs/fixes/` (technical fixes)
- ✅ Cleaned root directory to only 4 essential files

### October 7, 2025 - v1.3.0 Documentation
- ✅ **NEW**: SCALING_GUIDE.md - Production deployment and scaling guide
- ✅ Enhanced TROUBLESHOOTING.md with GraphRAG and batch processing guidance
- ✅ Updated GRAPHRAG_GUIDE.md with batch processing best practices
- ✅ Expanded ARCHITECTURE.md with refactoring plans
- ✅ Created v1.3.0 CHANGELOG entry
- ✅ Documentation consolidation (23 → 15 docs, 35% reduction)
- ✅ Updated README.md with v1.3.0 features

### October 6, 2025
- ✅ CI/CD pipeline implementation complete
- ✅ All GitHub Actions workflows operational
- ✅ Test coverage reporting configured

### October 2, 2025
- ✅ Code quality improvements (Phases 1-3)
- ✅ 6 new utility modules created
- ✅ 64 tests passing, 90%+ coverage on utils

---

## 💡 Contributing to Documentation

Found an issue or want to improve documentation?

1. **Report Issues**: [GitHub Issues](https://github.com/coleam00/mcp-crawl4ai-rag/issues)
2. **Submit PRs**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
3. **Ask Questions**: Use GitHub Discussions

### Documentation Standards

- Use clear, concise language
- Include code examples where applicable
- Keep troubleshooting sections practical
- Update the status table when modifying docs
- Cross-reference related documentation

---

## 🔗 External Resources

- **[MCP Documentation](https://modelcontextprotocol.io)** - Model Context Protocol
- **[Crawl4AI Docs](https://crawl4ai.com)** - Web crawling library
- **[Supabase Docs](https://supabase.com/docs)** - Vector database
- **[Neo4j Docs](https://neo4j.com/docs)** - Graph database

---

*For the main project README and overview, see [../README.md](../README.md)*
