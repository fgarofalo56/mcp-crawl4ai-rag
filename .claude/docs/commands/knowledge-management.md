# 🧠 Knowledge Management Commands

> **Build and leverage persistent project knowledge**

Knowledge management commands help you capture, organize, search, and leverage project knowledge across sessions. Build institutional memory that makes Claude smarter over time.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/kb-add](#kb-add---add-knowledge)
  - [/kb-search](#kb-search---search-knowledge-base)
  - [/kb-extract-patterns](#kb-extract-patterns---extract-code-patterns)
  - [/kb-update](#kb-update---update-knowledge)
  - [/kb-stats](#kb-stats---knowledge-base-statistics)
  - [/kb-export](#kb-export---export-knowledge)
  - [/kb-import](#kb-import---import-knowledge)
- [Knowledge Base Structure](#-knowledge-base-structure)
- [Workflow Patterns](#-workflow-patterns)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

Knowledge management is critical for:

- **Persistent Learning** - Knowledge survives across sessions
- **Pattern Recognition** - Identify and reuse successful patterns
- **Team Sharing** - Share learnings across team members
- **Context Building** - Richer context for better AI outputs
- **Historical Reference** - Track decisions and their rationale

### Knowledge Base Capabilities

- ✅ **Vector Search** - Semantic search over knowledge
- ✅ **Pattern Extraction** - Automatic pattern identification
- ✅ **Cross-Project Learning** - Share knowledge between projects
- ✅ **Versioned Knowledge** - Track knowledge evolution
- ✅ **Export/Import** - Share with team or backup

---

## 📋 Command Reference

### /kb-add - Add Knowledge

**Purpose**: Adds new knowledge to the knowledge base with automatic embedding generation.

**Category**: Knowledge Management

**Execution Time**: 5-15 seconds

**Resources**: Low (embedding generation)

#### What It Does

1. **Accepts Knowledge Input**
   - Markdown content
   - Code snippets
   - Learnings and decisions
   - Research findings

2. **Generates Embeddings**
   - Creates vector embeddings
   - Enables semantic search
   - Indexes for retrieval

3. **Stores Knowledge**
   - Saves to `.claude/knowledge/`
   - Tags with metadata
   - Links related knowledge

4. **Confirms Addition**
   - Shows storage location
   - Displays tags
   - Provides search tips

#### Command Template

```markdown
---
description: Add knowledge to the knowledge base
allowed-tools: Write, Read, Edit
argument-hint: "knowledge content or --file path/to/file.md"
---

# KB Add Command

## Steps

1. **Parse Input**
   - If $ARGUMENTS starts with "--file", read that file
   - Otherwise, treat $ARGUMENTS as knowledge content
   - Extract title from first line or heading

2. **Extract Metadata**
   - Title (required)
   - Tags (optional, comma-separated)
   - Category (auto-detect or user-provided)
   - Date (automatic)
   - Author (from git config or system)

3. **Generate Embedding**
   - Create vector embedding of content
   - Use appropriate embedding model
   - Store embedding with content

4. **Store Knowledge**
   - Save to .claude/knowledge/{category}/{timestamp}-{slug}.md
   - Create index entry
   - Update knowledge base stats

5. **Link Related Knowledge**
   - Search for similar existing knowledge
   - Create bidirectional links
   - Update related entries

6. **Confirm Addition**
   - Display storage path
   - Show generated tags
   - List related knowledge
   - Provide search command
```

#### Usage Examples

**Add Knowledge Inline**:
```bash
# Add a learning
/kb-add "Learning: FastAPI background tasks should use dependency injection for database sessions. This prevents connection leaks and ensures proper cleanup. See src/tasks/email.py for example."

# Add with tags
/kb-add --tags "fastapi,database,patterns" "Pattern: Use repository pattern for data access to improve testability and maintainability."
```

**Add from File**:
```bash
# Add from markdown file
/kb-add --file docs/learnings/oauth2-implementation.md

# Add research findings
/kb-add --file .research/azure-container-apps-networking.md
```

**Add Code Pattern**:
```bash
/kb-add --category "patterns" --tags "python,async,error-handling" "
# Async Error Handling Pattern

## Pattern
```python
async def safe_api_call(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.exception('Unexpected error')
        raise HTTPException(500, 'Internal server error')
```

## Usage
Used in src/api/*.py for all external API calls
"
```

#### Expected Output

```
✅ Knowledge Added

📝 Title: FastAPI Background Task Patterns
📂 Category: patterns
🏷️ Tags: fastapi, background-tasks, database
📅 Date: 2025-01-15
👤 Author: developer@example.com

💾 Stored At:
.claude/knowledge/patterns/2025-01-15-fastapi-background-task-patterns.md

🔗 Related Knowledge:
  - FastAPI Dependency Injection (85% similar)
  - Database Session Management (78% similar)
  - Background Task Error Handling (72% similar)

🔍 Search Command:
/kb-search "fastapi background tasks"
```

---

### /kb-search - Search Knowledge Base

**Purpose**: Searches knowledge base using semantic search.

**Category**: Knowledge Management

**Execution Time**: 1-5 seconds

**Resources**: Low (vector search)

#### What It Does

1. **Performs Semantic Search**
   - Converts query to embedding
   - Searches vector database
   - Ranks by relevance

2. **Filters Results**
   - By category
   - By tags
   - By date range
   - By similarity threshold

3. **Presents Results**
   - Ranked by relevance
   - Shows excerpts
   - Provides full content links
   - Suggests related searches

#### Command Template

```markdown
---
description: Search knowledge base with semantic search
allowed-tools: Read, Grep
argument-hint: "search query" [--category cat] [--tags tag1,tag2] [--limit N]
---

# KB Search Command

## Steps

1. **Parse Search Query**
   - Extract main query from $ARGUMENTS
   - Parse optional flags:
     * --category: Filter by category
     * --tags: Filter by tags
     * --limit: Max results (default 10)
     * --after: Date filter
     * --before: Date filter

2. **Generate Query Embedding**
   - Convert query to vector embedding
   - Use same model as knowledge storage

3. **Search Knowledge Base**
   - Vector similarity search
   - Apply filters (category, tags, date)
   - Rank by similarity score
   - Apply limit

4. **Present Results**
   - Sort by relevance (similarity score)
   - Show:
     * Title
     * Similarity score (%)
     * Excerpt (first 200 chars)
     * Category and tags
     * Date added
     * File path

5. **Suggest Actions**
   - View full content
   - Related searches
   - Add to current context
```

#### Usage Examples

**Basic Search**:
```bash
# Search for topic
/kb-search "fastapi authentication patterns"

# Search with category filter
/kb-search "error handling" --category patterns

# Search with tag filter
/kb-search "database" --tags python,async
```

**Advanced Search**:
```bash
# Limit results
/kb-search "azure deployment" --limit 5

# Date range
/kb-search "security" --after 2025-01-01

# Multiple filters
/kb-search "testing" --category examples --tags python,pytest --limit 3
```

#### Expected Output

```
🔍 Search Results for "fastapi authentication patterns"

Found 8 matches (showing top 5):

1. FastAPI OAuth2 with JWT [96% match]
   📂 patterns | 🏷️ fastapi, auth, jwt | 📅 2025-01-10

   "Complete OAuth2 implementation with JWT tokens.
   Includes token refresh, role-based access, and
   secure password hashing. Reference implementation..."

   📄 .claude/knowledge/patterns/2025-01-10-fastapi-oauth2-jwt.md

2. API Key Authentication Middleware [89% match]
   📂 patterns | 🏷️ fastapi, auth, middleware | 📅 2025-01-08

   "Lightweight API key authentication using FastAPI
   middleware. Suitable for internal services and
   machine-to-machine communication..."

   📄 .claude/knowledge/patterns/2025-01-08-api-key-auth.md

3. Multi-Tenant Authentication [85% match]
   📂 examples | 🏷️ fastapi, auth, multi-tenant | 📅 2024-12-20

   "Authentication pattern for multi-tenant SaaS.
   Includes tenant isolation, per-tenant user
   management, and tenant-specific permissions..."

   📄 .claude/knowledge/examples/2024-12-20-multi-tenant-auth.md

💡 Related Searches:
  - "fastapi security best practices"
  - "jwt token management"
  - "authentication testing"

🔧 Actions:
  /kb-view 1        View full content of result #1
  /kb-add-context 1,2  Add results to current context
```

---

### /kb-extract-patterns - Extract Code Patterns

**Purpose**: Automatically extracts reusable patterns from codebase.

**Category**: Knowledge Management

**Execution Time**: 1-3 minutes

**Resources**: Medium (code analysis agent)

#### What It Does

1. **Analyzes Codebase**
   - Scans source files
   - Identifies patterns
   - Finds common solutions

2. **Extracts Patterns**
   - Design patterns
   - Code structures
   - Best practices
   - Common utilities

3. **Generates Documentation**
   - Pattern description
   - Code examples
   - Use cases
   - Related patterns

4. **Stores in KB**
   - Saves to knowledge base
   - Tags appropriately
   - Links related patterns

#### Command Template

```markdown
---
description: Extract reusable patterns from codebase
allowed-tools: Read, Grep, Glob, Task, Write
argument-hint: [optional-focus-path]
---

# KB Extract Patterns Command

## Steps

1. **Scan Codebase**
   - If $ARGUMENTS provided, focus on that path
   - Otherwise scan src/ or equivalent
   - Identify file types (Python, TypeScript, etc.)

2. **Identify Patterns** (Use Task agent)

   **Look for:**
   - Repeated code structures (3+ occurrences)
   - Utility functions used across files
   - Design pattern implementations
   - Architecture patterns
   - Error handling patterns
   - Testing patterns
   - Configuration patterns

3. **Analyze Each Pattern**
   - Extract core concept
   - Find all examples
   - Identify variations
   - Note best implementation

4. **Generate Documentation**
   For each pattern:
   - Name and description
   - Problem it solves
   - Implementation example
   - Usage locations in codebase
   - Pros and cons
   - Related patterns

5. **Store Patterns**
   - Save to .claude/knowledge/patterns/
   - Tag with language, category
   - Link related patterns
   - Update pattern index

6. **Report Findings**
   - List patterns found
   - Show examples
   - Provide KB search commands
```

#### Usage Examples

```bash
# Extract patterns from entire codebase
/kb-extract-patterns

# Focus on specific directory
/kb-extract-patterns src/api

# Focus on test patterns
/kb-extract-patterns tests/

# Extract by file type
/kb-extract-patterns --type python
```

#### Expected Output

```
🔍 Extracting Patterns from src/

Scanning:
  ✅ src/api/ (15 files)
  ✅ src/services/ (8 files)
  ✅ src/models/ (12 files)
  ✅ src/utils/ (6 files)

📊 Patterns Found: 7

1. ✅ Repository Pattern (Data Access)
   📍 Found in: 8 locations
   📂 Category: architecture
   🏷️ Tags: data-access, repository, testability

   Example locations:
   - src/services/user_service.py
   - src/services/project_service.py
   - src/services/team_service.py

2. ✅ Dependency Injection (FastAPI)
   📍 Found in: 15 locations
   📂 Category: patterns
   🏷️ Tags: fastapi, di, dependencies

   Example locations:
   - src/api/users.py
   - src/api/projects.py
   - src/api/auth.py

3. ✅ Error Response Factory
   📍 Found in: 12 locations
   📂 Category: patterns
   🏷️ Tags: error-handling, api, http

   Example locations:
   - src/api/error_handlers.py
   - src/api/users.py

4. ✅ Async Context Manager (Database)
   📍 Found in: 6 locations
   📂 Category: patterns
   🏷️ Tags: database, async, context-manager

   Example locations:
   - src/services/base.py
   - src/middleware/database.py

... (3 more patterns)

💾 Stored Patterns:
  .claude/knowledge/patterns/repository-pattern-data-access.md
  .claude/knowledge/patterns/dependency-injection-fastapi.md
  .claude/knowledge/patterns/error-response-factory.md
  .claude/knowledge/patterns/async-context-manager-database.md
  ... (3 more files)

🔍 Search Patterns:
/kb-search "repository pattern"
/kb-search "dependency injection"
```

---

### /kb-update - Update Knowledge

**Purpose**: Updates existing knowledge base entries.

**Category**: Knowledge Management

**Execution Time**: 5-10 seconds

**Resources**: Low

#### Usage Examples

```bash
# Update by search
/kb-update "fastapi authentication" --append "New finding: Token refresh should use sliding window expiration"

# Update specific entry
/kb-update --id kb-12345 --replace

# Update tags
/kb-update "database patterns" --add-tags "sqlalchemy,async"
```

---

### /kb-stats - Knowledge Base Statistics

**Purpose**: Displays knowledge base statistics and health.

**Category**: Knowledge Management

**Execution Time**: <5 seconds

**Resources**: Minimal

#### Usage Examples

```bash
# Show statistics
/kb-stats

# Detailed breakdown
/kb-stats --detailed

# By category
/kb-stats --category patterns
```

#### Expected Output

```
📊 Knowledge Base Statistics

📦 Total Entries: 156

📂 By Category:
  patterns:    45 (29%)
  learnings:   38 (24%)
  examples:    32 (21%)
  research:    25 (16%)
  decisions:   16 (10%)

🏷️ Top Tags:
  python:      67 entries
  fastapi:     45 entries
  azure:       38 entries
  testing:     32 entries
  database:    28 entries

📅 Activity (Last 30 Days):
  Added:       28 entries
  Updated:     12 entries
  Searches:    156 queries

💾 Storage:
  Total Size:  2.4 MB
  Location:    .claude/knowledge/

🔍 Most Searched:
  1. "authentication patterns" (23 searches)
  2. "azure deployment" (18 searches)
  3. "testing best practices" (15 searches)
```

---

### /kb-export - Export Knowledge

**Purpose**: Exports knowledge base for backup or sharing.

**Category**: Knowledge Management

**Execution Time**: 5-30 seconds

**Resources**: Low

#### Usage Examples

```bash
# Export all knowledge
/kb-export --output knowledge-backup.json

# Export by category
/kb-export --category patterns --output patterns.json

# Export for sharing (anonymized)
/kb-export --anonymize --output team-knowledge.json
```

---

### /kb-import - Import Knowledge

**Purpose**: Imports knowledge from export file or external source.

**Category**: Knowledge Management

**Execution Time**: 10-60 seconds

**Resources**: Medium

#### Usage Examples

```bash
# Import from file
/kb-import knowledge-backup.json

# Import with merge strategy
/kb-import team-knowledge.json --merge

# Import from URL
/kb-import https://example.com/shared-knowledge.json
```

---

## 🗂️ Knowledge Base Structure

### Directory Organization

```
.claude/knowledge/
├── patterns/               # Reusable code patterns
│   ├── repository-pattern-data-access.md
│   ├── dependency-injection-fastapi.md
│   └── async-context-manager.md
├── learnings/             # Captured learnings
│   ├── fastapi-background-tasks.md
│   ├── azure-container-networking.md
│   └── pytest-async-fixtures.md
├── examples/              # Code examples
│   ├── oauth2-implementation.md
│   ├── multi-tenant-auth.md
│   └── rate-limiting.md
├── research/              # Research findings
│   ├── azure-best-practices.md
│   ├── security-patterns.md
│   └── performance-optimization.md
├── decisions/             # Architecture decisions
│   ├── adr-001-database-choice.md
│   ├── adr-002-auth-strategy.md
│   └── adr-003-deployment-model.md
└── index.json            # Knowledge base index
```

### Entry Format

```markdown
---
title: Repository Pattern for Data Access
category: patterns
tags: [data-access, repository, testability, python]
date: 2025-01-15
author: developer@example.com
related:
  - dependency-injection-fastapi
  - async-context-manager
---

# Repository Pattern for Data Access

## Problem
Direct database access in API routes makes testing difficult and
couples API layer to database implementation.

## Solution
Implement repository pattern to abstract data access.

## Example

```python
# repository base
class BaseRepository:
    def __init__(self, db: Database):
        self.db = db

# user repository
class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: int) -> User:
        return await self.db.query(User).filter_by(id=user_id).first()

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.db.add(user)
        await self.db.commit()
        return user
```

## Usage in Codebase
- `src/services/user_service.py`
- `src/services/project_service.py`
- `src/services/team_service.py`

## Benefits
- Improved testability (mock repository)
- Separation of concerns
- Easier to change database

## Gotchas
- Don't leak database sessions
- Handle transactions at service layer
- Use dependency injection

## Related Patterns
- Dependency Injection
- Unit of Work
- Async Context Managers
```

---

## 🔄 Workflow Patterns

### Continuous Learning Workflow

```bash
# During development
# After solving a problem
/kb-add "Learning: [what you learned]"

# End of day
/kb-extract-patterns

# Weekly
/kb-stats
```

### Research Workflow

```bash
# Before implementing new feature
/kb-search "feature topic"

# Research if not found
/research-topic "feature topic"

# Store research
/kb-add --file .research/feature-topic.md
```

### Pattern Documentation Workflow

```bash
# After implementing pattern multiple times
/kb-extract-patterns src/

# Review extracted patterns
/kb-search "pattern name"

# Refine if needed
/kb-update "pattern name" --append "Additional notes"
```

---

## 💡 Best Practices

### Adding Knowledge

✅ **DO**:
- Add knowledge immediately when learned
- Use clear, descriptive titles
- Include code examples
- Tag appropriately (3-5 tags)
- Link related knowledge

❌ **DON'T**:
- Add trivial or obvious information
- Skip examples
- Use vague titles
- Over-tag or under-tag
- Add duplicate knowledge

### Searching Knowledge

✅ **DO**:
- Use specific queries
- Review multiple results
- Check related knowledge
- Update knowledge if outdated

❌ **DON'T**:
- Use single-word queries
- Only check first result
- Ignore related links
- Assume knowledge is current

### Pattern Extraction

✅ **DO**:
- Run regularly (weekly)
- Review extracted patterns
- Refine pattern documentation
- Remove obsolete patterns

❌ **DON'T**:
- Extract too frequently (noise)
- Accept all patterns blindly
- Keep outdated patterns
- Skip pattern review

---

## 🐛 Troubleshooting

### Knowledge Not Found

```bash
# Check KB exists
ls .claude/knowledge/

# Check stats
/kb-stats

# Try broader search
/kb-search "broader term"

# Re-index if needed
/kb-reindex
```

### Search Returns Irrelevant Results

```bash
# Use more specific query
/kb-search "very specific query with context"

# Use filters
/kb-search "query" --category patterns --tags python

# Update knowledge with better tags
/kb-update "entry" --add-tags relevant,tags
```

### Pattern Extraction Slow

```bash
# Focus on specific directory
/kb-extract-patterns src/api

# Skip tests
/kb-extract-patterns --exclude tests/

# Limit file types
/kb-extract-patterns --type python
```

---

**Navigate**: [← Core Essentials](./core-essentials.md) | [Commands Home](./README.md) | [Azure Development →](./azure-development.md)

---

*Build knowledge, build intelligence*
