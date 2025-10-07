# MCP Crawl4AI RAG - Documentation

Welcome to the documentation for the MCP Crawl4AI RAG server! This directory contains comprehensive guides and references for setting up, using, and maintaining the project.

**Last Updated**: October 7, 2025

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
| [NEO4J_FIX.md](NEO4J_FIX.md) | Neo4j troubleshooting | Neo4j connection issues |

#### Features & Capabilities

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [GRAPHRAG_GUIDE.md](GRAPHRAG_GUIDE.md) | GraphRAG features (v1.2.0) | Using knowledge graphs |
| [NEW_FEATURES_GUIDE.md](NEW_FEATURES_GUIDE.md) | Advanced crawling (v1.1.0) | Stealth mode, multi-URL, memory monitoring |
| [API Reference](../API_REFERENCE.md) | All 16 MCP tools | Looking up tool parameters |

#### Development

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture | Understanding codebase structure |
| [CODE_QUALITY_IMPROVEMENTS.md](CODE_QUALITY_IMPROVEMENTS.md) | Code quality guide | Contributing or refactoring |
| [QUICK_START.md](QUICK_START.md) | Developer quick reference | Daily development |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines | Before submitting PRs |

#### DevOps & Testing

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [CI_CD.md](CI_CD.md) | CI/CD pipeline docs | Setting up workflows |
| [WORKFLOW_QUICK_REFERENCE.md](WORKFLOW_QUICK_REFERENCE.md) | Common workflows | Daily Git operations |
| [Testing Guide](../TESTING_QUICK_START.md) | Test suite information | Running tests |

---

### 🔧 Troubleshooting

#### Common Issues

**Start Here**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Comprehensive troubleshooting guide

**Specific Issues**:
- **Neo4j Connection**: See [NEO4J_FIX.md](NEO4J_FIX.md)
- **Docker Issues**: See [DOCKER_SETUP.md](DOCKER_SETUP.md#troubleshooting)
- **Claude Desktop**: See [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md#troubleshooting)

---

### 📁 Reference Documentation

- **[API Reference](../API_REFERENCE.md)** - Complete tool documentation
- **[Changelog](../CHANGELOG.md)** - Version history
- **[Project Status](../PROJECT_STATUS.md)** - Current development status
- **[Test Coverage](../TEST_COVERAGE_SUMMARY.md)** - Testing metrics

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

**...troubleshoot connection issues**
→ [Troubleshooting](TROUBLESHOOTING.md) → [Neo4j Fix](NEO4J_FIX.md)

**...contribute to the project**
→ [Contributing Guide](../CONTRIBUTING.md) → [Code Quality Improvements](CODE_QUALITY_IMPROVEMENTS.md)

**...understand the architecture**
→ [Architecture](ARCHITECTURE.md)

**...set up CI/CD**
→ [CI/CD Guide](CI_CD.md)

**...look up tool parameters**
→ [API Reference](../API_REFERENCE.md)

---

## 📦 Documentation Structure

```
docs/
├── README.md (this file)          # Documentation hub
│
├── 🚀 Getting Started
│   ├── CLAUDE_DESKTOP_SETUP.md    # Claude Desktop integration
│   ├── DOCKER_SETUP.md             # Docker deployment
│   ├── DUAL_MODE_SETUP.md          # Multiple transports
│   └── QUICK_START.md              # Developer quick reference
│
├── 📖 Features
│   ├── GRAPHRAG_GUIDE.md           # GraphRAG documentation
│   └── NEW_FEATURES_GUIDE.md       # v1.1.0 features
│
├── 🔧 Development
│   ├── ARCHITECTURE.md             # System design
│   ├── CODE_QUALITY_IMPROVEMENTS.md # Code standards
│   └── WORKFLOW_QUICK_REFERENCE.md  # Git workflows
│
├── 🧪 DevOps
│   └── CI_CD.md                    # CI/CD pipelines
│
├── 🔧 Troubleshooting
│   ├── TROUBLESHOOTING.md          # Main troubleshooting guide
│   └── NEO4J_FIX.md                # Neo4j specific issues
│
└── 📁 archive/                     # Historical documentation
    └── README.md                   # Archive index
```

---

## 🏷️ Document Status

All active documentation is up-to-date as of October 7, 2025.

| Category | Documents | Status |
|----------|-----------|--------|
| Setup & Configuration | 4 docs | ✅ Current |
| Features | 2 docs | ✅ Current |
| Development | 3 docs | ✅ Current |
| DevOps | 2 docs | ✅ Current |
| Troubleshooting | 2 docs | ✅ Current |
| **Total Active Docs** | **14 docs** | **✅ Up-to-date** |

**Archived Documentation**: 11 historical documents in `archive/`

---

## 🆕 Recent Updates

### October 7, 2025
- ✅ Documentation restructuring complete
- ✅ Archived 11 historical documents
- ✅ Created PROJECT_STATUS.md for tracking
- ✅ Updated documentation index (this file)
- 🔄 TROUBLESHOOTING.md guide in progress

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
