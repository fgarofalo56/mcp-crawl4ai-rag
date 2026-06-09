# 🎯 Core Essential Commands

> **Essential commands for daily Claude Code workflows**

These are the foundational commands you'll use most frequently in your development workflow. Master these first for maximum productivity.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/primer](#primer---initialize-project-context)
  - [/task-next](#task-next---get-next-task-with-research)
  - [/research-topic](#research-topic---deep-dive-research)
  - [/structure-validate](#structure-validate---validate-directory-structure)
  - [/help](#help---get-command-help)
  - [/mcp-health-check](#mcp-health-check---check-mcp-server-health)
  - [/troubleshoot](#troubleshoot---diagnose-issues)
- [Workflow Patterns](#-workflow-patterns)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)
- [Related Commands](#-related-commands)

---

## 🎯 Overview

Core essential commands form the foundation of your Claude Code workflow. These commands:

- **Initialize context** - Load project knowledge at session start
- **Plan tasks** - Identify next steps with research
- **Validate structure** - Ensure project organization
- **Research topics** - Deep-dive investigation
- **Diagnose issues** - Troubleshoot problems

### When to Use Core Commands

- ✅ **Every session**: Start with `/primer`
- ✅ **Task planning**: Use `/task-next` for next steps
- ✅ **Learning**: Use `/research-topic` for deep dives
- ✅ **Validation**: Use `/structure-validate` after changes
- ✅ **Troubleshooting**: Use `/troubleshoot` when stuck

---

## 📋 Command Reference

### /primer - Initialize Project Context

**Purpose**: Primes Claude with comprehensive project context at session start.

**Category**: Core

**Execution Time**: 30-60 seconds

**Resources**: Low (1 agent, basic tools)

#### What It Does

1. **Analyzes Project Structure**
   - Scans directory tree
   - Identifies key files
   - Maps dependencies

2. **Loads Core Knowledge**
   - Reads CLAUDE.md
   - Loads project documentation
   - Reviews recent changes

3. **Initializes MCP Servers**
   - Checks MCP health
   - Loads integrations
   - Validates connections

4. **Provides Context Summary**
   - Project overview
   - Recent activity
   - Next suggested actions

#### Command Template

```markdown
---
description: Prime Claude with comprehensive project context
allowed-tools: Read, Glob, Bash, Grep
argument-hint: [optional-focus-area]
---

# Primer Command

## Steps

1. **Load Project Configuration**
   - Read .claude/settings.local.json
   - Read CLAUDE.md and CLAUDE.local.md
   - Load project README.md

2. **Analyze Structure**
   - Scan directory tree (max 3 levels)
   - Identify src/, tests/, docs/ structure
   - Note configuration files

3. **Load Recent Context**
   - Check git log (last 10 commits)
   - Review open files (if any)
   - Check for TODO/FIXME comments

4. **Check Dependencies**
   - Identify language/framework (package.json, pyproject.toml, etc.)
   - List key dependencies
   - Note version constraints

5. **MCP Health Check**
   - Verify MCP servers responding
   - List available tools
   - Note any connection issues

6. **Provide Summary**
   - Project type and tech stack
   - Current state and recent changes
   - Suggested next actions
   - Any warnings or issues

## Optional Focus Area

If $ARGUMENTS provided, focus on that area:
- "testing" - Focus on test infrastructure
- "azure" - Focus on Azure resources
- "docs" - Focus on documentation
```

#### Usage Examples

**Basic Usage**:
```bash
# Load full project context
/primer
```

**With Focus Area**:
```bash
# Focus on Azure infrastructure
/primer azure

# Focus on testing setup
/primer testing

# Focus on documentation
/primer docs
```

#### Expected Output

```
✅ Project Context Loaded

📁 Project Structure:
  - Type: Python web application
  - Framework: FastAPI
  - Structure: src/, tests/, docs/

📦 Key Dependencies:
  - fastapi ^0.104.0
  - pydantic ^2.5.0
  - pytest ^7.4.0

🔧 MCP Servers:
  ✅ microsoft-docs-mcp (responding)
  ✅ serena (responding)
  ✅ azure-mcp (responding)

📝 Recent Activity:
  - Last commit: "Add user authentication" (2 hours ago)
  - 3 modified files in src/auth/
  - 5 new tests added

💡 Suggested Next Actions:
  1. Complete authentication testing
  2. Update API documentation
  3. Review security best practices
```

#### Best Practices

✅ **DO**:
- Run at start of every session
- Re-run after pulling changes
- Use focus areas when needed
- Review the summary output

❌ **DON'T**:
- Skip in new sessions
- Ignore warnings in output
- Run too frequently (once per session usually sufficient)

---

### /task-next - Get Next Task with Research

**Purpose**: Identifies the next logical task based on project state and performs background research.

**Category**: Core

**Execution Time**: 1-3 minutes

**Resources**: Medium (2 agents, MCP servers)

#### What It Does

1. **Analyzes Current State**
   - Reviews recent commits
   - Checks TODO comments
   - Examines open files

2. **Identifies Next Task**
   - Suggests logical next step
   - Prioritizes by importance
   - Considers dependencies

3. **Performs Research**
   - Searches relevant documentation
   - Finds code examples
   - Identifies best practices

4. **Provides Implementation Plan**
   - Step-by-step breakdown
   - Required files/changes
   - Testing approach

#### Command Template

```markdown
---
description: Get next task with background research
allowed-tools: Read, Grep, Glob, Bash, Task
requires-mcp: microsoft-docs, serena
argument-hint: [optional-focus-area]
---

# Task Next Command

## Steps

1. **Analyze Project State**
   - Git status and recent commits
   - Scan for TODO/FIXME/HACK comments
   - Check for incomplete features (commented code, stub functions)
   - Review documentation for planned features

2. **Identify Candidates**
   - List 3-5 potential next tasks
   - Consider:
     * Incomplete features
     * TODO items
     * Documentation gaps
     * Test coverage gaps
     * Technical debt

3. **Prioritize**
   - Rank by:
     * Blocking other work (high priority)
     * User value (medium priority)
     * Technical debt (lower priority)
   - Select top task

4. **Research Task** (parallel agent)
   - Use microsoft-docs for official documentation
   - Use serena for code pattern search
   - Find 2-3 relevant examples
   - Identify best practices and gotchas

5. **Create Implementation Plan**
   - Break into steps (3-7 steps)
   - Identify files to modify
   - Specify testing approach
   - Note validation criteria

6. **Present Task**
   - Task description
   - Why this task now
   - Implementation plan
   - Research findings
   - Estimated complexity
```

#### Usage Examples

**Basic Usage**:
```bash
# Get next task
/task-next
```

**With Focus Area**:
```bash
# Focus on backend tasks
/task-next backend

# Focus on testing tasks
/task-next testing

# Focus on documentation
/task-next docs
```

#### Expected Output

```
🎯 Next Task: Implement User Email Verification

Why This Task:
  - Blocks: User registration flow completion
  - Required for: Production deployment
  - Priority: HIGH

📋 Implementation Plan:

1. Create email verification endpoint
   - File: src/api/auth.py
   - Add POST /verify-email endpoint
   - Validate token from email

2. Add email sending service
   - File: src/services/email.py
   - Use Azure Communication Services
   - Template-based emails

3. Update user model
   - File: src/models/user.py
   - Add email_verified field
   - Add verification_token field

4. Write tests
   - File: tests/test_auth.py
   - Test token generation
   - Test verification flow
   - Test edge cases

📚 Research Findings:

Best Practices:
  - Use time-limited tokens (24h expiry)
  - Include HMAC signature for security
  - Send welcome email after verification

Code Examples:
  - Azure Communication Services email sending
  - Token generation with secrets module
  - Pydantic models for email templates

Gotchas:
  - Handle expired tokens gracefully
  - Prevent email enumeration attacks
  - Rate limit verification attempts

⏱️ Estimated Complexity: Medium (2-3 hours)

📊 Acceptance Criteria:
  ✅ User receives verification email
  ✅ Token validates correctly
  ✅ Invalid tokens return clear errors
  ✅ All tests pass with >90% coverage
```

#### Best Practices

✅ **DO**:
- Run when unsure what to do next
- Review research findings before starting
- Follow suggested implementation plan
- Validate acceptance criteria

❌ **DON'T**:
- Ignore priority rankings
- Skip research findings
- Deviate from plan without reason
- Forget to run tests

---

### /research-topic - Deep Dive Research

**Purpose**: Performs comprehensive research on a specific topic with multiple sources.

**Category**: Core

**Execution Time**: 2-5 minutes

**Resources**: Medium (1-3 research agents, MCP servers)

#### What It Does

1. **Multi-Source Research**
   - Official documentation
   - Code examples
   - Best practices
   - Common pitfalls

2. **Pattern Analysis**
   - Searches codebase for existing patterns
   - Identifies reusable code
   - Notes architectural decisions

3. **Synthesized Output**
   - Comprehensive summary
   - Actionable recommendations
   - Example code
   - Related resources

#### Command Template

```markdown
---
description: Deep-dive research on specific topic
allowed-tools: Read, Grep, Glob, Task, WebFetch
requires-mcp: microsoft-docs, serena
argument-hint: "topic to research"
---

# Research Topic Command

## Steps

1. **Parse Topic**
   - Extract main topic from $ARGUMENTS
   - Identify subtopics
   - Determine research scope

2. **Official Documentation Research** (Agent 1)
   - Use microsoft-docs-mcp for Microsoft/Azure topics
   - Search documentation
   - Extract key concepts
   - Find code examples
   - Note version-specific information

3. **Codebase Pattern Search** (Agent 2 - parallel)
   - Use serena to search current codebase
   - Find existing implementations
   - Identify patterns and conventions
   - Note architectural decisions

4. **Best Practices Research** (Agent 3 - parallel)
   - Search for best practices
   - Identify common pitfalls
   - Find performance considerations
   - Note security implications

5. **Synthesize Findings**
   - Combine all research
   - Remove duplicates
   - Organize by relevance
   - Create actionable summary

6. **Present Results**
   - Overview
   - Key concepts
   - Code examples (2-3)
   - Best practices
   - Common pitfalls
   - Related topics
   - Recommended next steps
```

#### Usage Examples

**Basic Usage**:
```bash
# Research a topic
/research-topic "FastAPI dependency injection patterns"
```

**Complex Topic**:
```bash
# Research with specifics
/research-topic "Azure Container Apps blue-green deployment with zero downtime"

# Research with framework context
/research-topic "Pydantic v2 migration best practices"
```

#### Expected Output

```
🔍 Research: FastAPI Dependency Injection Patterns

## Overview
FastAPI's dependency injection system provides a powerful way to manage
dependencies, implement cross-cutting concerns, and improve testability.

## Key Concepts

1. **Dependency Functions**
   - Functions that can be injected into path operations
   - Support async and sync functions
   - Can have their own dependencies (nested)

2. **Depends()**
   - Core dependency injection mechanism
   - Supports type hints for automatic validation
   - Caches results within request scope

3. **Dependency Scopes**
   - Request scope (default)
   - Application scope (using yield)
   - Background task scope

## Code Examples

### Example 1: Basic Dependency
```python
from fastapi import Depends, FastAPI

def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def get_users(db = Depends(get_db)):
    return db.query(User).all()
```

### Example 2: Nested Dependencies
```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    return decode_token(token)

def get_admin_user(user = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403)
    return user

@app.delete("/users/{id}")
async def delete_user(id: int, admin = Depends(get_admin_user)):
    # Only admins can access
    pass
```

### Example 3: Class-Based Dependencies
```python
class Database:
    def __init__(self, connection_string: str):
        self.connection = connect(connection_string)

    def __call__(self):
        return self.connection

db = Database(connection_string)

@app.get("/items")
async def get_items(conn = Depends(db)):
    return conn.query(Item).all()
```

## Existing Patterns in Codebase

Found 12 usages of dependency injection:
  - src/api/auth.py: User authentication dependencies
  - src/api/users.py: Database session management
  - src/middleware/logging.py: Request logging

Current pattern: Using generator-based dependencies with yield
Matches best practices: ✅

## Best Practices

1. **Use Generator Pattern for Cleanup**
   - Leverage yield for resource management
   - Ensures cleanup even on errors

2. **Cache Expensive Operations**
   - Dependencies cached per request by default
   - Use for database connections, auth checks

3. **Type Hints for Validation**
   - FastAPI uses type hints for validation
   - Clear errors when validation fails

4. **Test with override_dependency()**
   - Mock dependencies in tests
   - Isolate unit tests

## Common Pitfalls

❌ Creating new DB connection per dependency call
   → Solution: Use yield pattern or caching

❌ Circular dependencies
   → Solution: Restructure or use Lazy loading

❌ Forgetting to clean up resources
   → Solution: Always use try/finally or yield

## Performance Considerations

- Dependencies evaluated once per request (cached)
- Async dependencies support concurrent execution
- Generator overhead minimal vs manual cleanup

## Related Topics

- FastAPI middleware patterns
- SQLAlchemy session management
- Authentication and authorization patterns
- Testing with pytest and dependency overrides

## Recommended Next Steps

1. Review current auth.py dependency patterns
2. Standardize database session management
3. Consider adding request ID dependency for logging
4. Add integration tests with dependency overrides
```

#### Best Practices

✅ **DO**:
- Be specific in research queries
- Review all sections of output
- Apply findings to your codebase
- Save important research to KB

❌ **DON'T**:
- Use overly generic queries
- Ignore codebase patterns
- Skip common pitfalls section
- Forget to validate findings

---

### /structure-validate - Validate Directory Structure

**Purpose**: Validates project directory structure against expected patterns.

**Category**: Core

**Execution Time**: <30 seconds

**Resources**: Low (built-in tools only)

#### What It Does

1. **Checks Required Directories**
   - `.claude/` configuration
   - Standard project structure
   - Test directories

2. **Validates Configuration Files**
   - settings.local.json
   - CLAUDE.md
   - Project configs

3. **Identifies Issues**
   - Missing directories
   - Missing files
   - Permission problems

4. **Provides Remediation**
   - Commands to fix issues
   - Suggested structure
   - Best practices

#### Command Template

```markdown
---
description: Validate project directory structure
allowed-tools: Bash, Read, Glob
---

# Structure Validate Command

## Steps

1. **Check .claude Directory**
   - [ ] .claude/ exists
   - [ ] .claude/commands/ exists
   - [ ] .claude/settings.local.json exists
   - [ ] .claude/hooks/ exists (optional)
   - [ ] .claude/knowledge/ exists (optional)

2. **Check Project Files**
   - [ ] CLAUDE.md exists (recommended)
   - [ ] README.md exists
   - [ ] .gitignore exists

3. **Check Project Structure**
   Detect project type and validate structure:

   **Python Project**:
   - [ ] src/ or project_name/ exists
   - [ ] tests/ exists
   - [ ] pyproject.toml or requirements.txt exists

   **TypeScript/Node Project**:
   - [ ] src/ exists
   - [ ] package.json exists
   - [ ] tsconfig.json exists (for TS)

   **Azure Project**:
   - [ ] infrastructure/ or infra/ exists
   - [ ] .azure/ exists (optional)

4. **Check Permissions**
   - .claude/settings.local.json is readable
   - Commands directory is readable

5. **Report Results**
   - ✅ All checks passed
   - ⚠️ Warnings (missing optional items)
   - ❌ Errors (missing required items)
   - 🔧 Remediation commands

6. **Provide Remediation**
   If issues found, show commands to fix:
   ```bash
   mkdir -p .claude/commands
   touch .claude/settings.local.json
   # etc.
   ```
```

#### Usage Examples

**Basic Usage**:
```bash
# Validate structure
/structure-validate
```

#### Expected Output

**All Valid**:
```
✅ Structure Validation: PASSED

📁 Required Directories:
  ✅ .claude/
  ✅ .claude/commands/
  ✅ src/
  ✅ tests/

📄 Required Files:
  ✅ .claude/settings.local.json
  ✅ README.md
  ✅ pyproject.toml

⚠️ Optional Items:
  ⚠️ CLAUDE.md (recommended)
  ⚠️ .claude/hooks/
  ⚠️ .claude/knowledge/

💡 Suggestions:
  - Add CLAUDE.md for project-specific guidance
  - Consider adding hooks for automation
```

**With Issues**:
```
❌ Structure Validation: FAILED

📁 Required Directories:
  ✅ .claude/
  ❌ .claude/commands/ (missing)
  ✅ src/
  ❌ tests/ (missing)

📄 Required Files:
  ✅ .claude/settings.local.json
  ❌ CLAUDE.md (missing)
  ✅ README.md

🔧 Remediation Commands:

# Create missing directories
mkdir -p .claude/commands
mkdir -p tests

# Create missing files
touch CLAUDE.md

# Copy templates
cp ~/templates/CLAUDE.md ./CLAUDE.md

💡 After fixing, run: /structure-validate
```

#### Best Practices

✅ **DO**:
- Run after project initialization
- Run after major restructuring
- Fix errors immediately
- Consider warnings

❌ **DON'T**:
- Ignore validation errors
- Skip recommended files
- Modify structure without revalidating

---

### /help - Get Command Help

**Purpose**: Provides help information about available commands.

**Category**: Core

**Execution Time**: <5 seconds

**Resources**: Minimal (read-only)

#### What It Does

1. **Lists Available Commands**
   - All registered commands
   - Command descriptions
   - Category groupings

2. **Shows Command Details**
   - Usage syntax
   - Arguments
   - Examples

3. **Provides Quick Reference**
   - Common commands
   - Quick start guide
   - Documentation links

#### Usage Examples

**List All Commands**:
```bash
# Show all available commands
/help
```

**Get Command Help**:
```bash
# Help for specific command
/help primer
/help task-next
/help azure-deploy
```

#### Expected Output

**All Commands**:
```
📚 Available Commands

Core Essentials:
  /primer              - Initialize project context
  /task-next           - Get next task with research
  /research-topic      - Deep-dive research
  /structure-validate  - Validate directory structure
  /help                - Get command help

Git Operations:
  /smart-commit        - Intelligent commit creation
  /create-pr           - Create pull request
  /conflict-resolver   - Resolve merge conflicts

Azure Development:
  /azure-deploy        - Deploy to Azure
  /azure-status        - Check deployment status
  /bicep-validate      - Validate Bicep templates

For detailed help: /help [command-name]
For documentation: See commands/README.md
```

**Specific Command**:
```
📖 Command: /primer

Description:
  Prime Claude with comprehensive project context at session start.

Usage:
  /primer [optional-focus-area]

Arguments:
  focus-area (optional): Area to focus on
    - azure: Focus on Azure resources
    - testing: Focus on test infrastructure
    - docs: Focus on documentation

Examples:
  /primer
  /primer azure
  /primer testing

Documentation:
  commands/core-essentials.md#primer

Related Commands:
  /task-next, /structure-validate
```

---

### /mcp-health-check - Check MCP Server Health

**Purpose**: Verifies all MCP servers are responding and healthy.

**Category**: Core

**Execution Time**: 5-15 seconds

**Resources**: Low (MCP ping)

#### What It Does

1. **Pings All MCP Servers**
   - Tests connectivity
   - Checks response time
   - Validates capabilities

2. **Reports Status**
   - Healthy servers (✅)
   - Slow servers (⚠️)
   - Failed servers (❌)

3. **Provides Diagnostics**
   - Error messages
   - Suggested fixes
   - Documentation links

#### Usage Examples

```bash
# Check all MCP servers
/mcp-health-check
```

#### Expected Output

**All Healthy**:
```
✅ MCP Health Check: ALL HEALTHY

MCP Servers:
  ✅ microsoft-docs-mcp (42ms)
  ✅ serena (38ms)
  ✅ azure-mcp (156ms)
  ✅ playwright (89ms)

Total: 4/4 healthy
```

**With Issues**:
```
⚠️ MCP Health Check: ISSUES DETECTED

MCP Servers:
  ✅ microsoft-docs-mcp (45ms)
  ⚠️ serena (2341ms) - SLOW
  ❌ azure-mcp (timeout)
  ✅ playwright (92ms)

Issues:
  ⚠️ serena responding slowly (>2s)
     - May indicate high load
     - Consider restarting

  ❌ azure-mcp not responding
     - Check if server is running
     - Verify connection settings
     - See: architecture/mcp-integration.md

🔧 Remediation:
  # Restart azure-mcp
  # (command depends on how it's running)

Total: 2/4 healthy, 1/4 slow, 1/4 failed
```

---

### /troubleshoot - Diagnose Issues

**Purpose**: Systematic troubleshooting of common issues.

**Category**: Core

**Execution Time**: 30-60 seconds

**Resources**: Medium (diagnostic checks)

#### What It Does

1. **Runs Diagnostic Checks**
   - Configuration validation
   - MCP server health
   - File permissions
   - Git status

2. **Identifies Issues**
   - Configuration errors
   - Missing dependencies
   - Permission problems

3. **Provides Solutions**
   - Step-by-step fixes
   - Documentation links
   - Recovery commands

#### Usage Examples

```bash
# General troubleshooting
/troubleshoot

# Troubleshoot specific area
/troubleshoot mcp
/troubleshoot permissions
```

#### Expected Output

```
🔧 Troubleshooting Report

✅ Configuration:
  ✅ settings.local.json valid
  ✅ CLAUDE.md present
  ✅ Directory structure valid

⚠️ MCP Servers:
  ✅ microsoft-docs-mcp
  ✅ serena
  ⚠️ azure-mcp (slow response)

✅ Permissions:
  ✅ All required tools allowed
  ✅ No permission blocks detected

⚠️ Git:
  ⚠️ 15 uncommitted files
  ⚠️ Diverged from origin/main

🔧 Recommended Actions:

1. azure-mcp Performance:
   - Restart azure-mcp server
   - Check network connectivity
   - See: architecture/mcp-integration.md

2. Git Status:
   - Review uncommitted changes
   - Consider running /smart-commit
   - Sync with remote

Overall Status: ⚠️ MINOR ISSUES (2 warnings)
```

---

## 🔄 Workflow Patterns

### Daily Startup Workflow

```bash
# 1. Initialize context
/primer

# 2. Check health
/mcp-health-check

# 3. Validate structure
/structure-validate

# 4. Get next task
/task-next
```

### Deep Research Workflow

```bash
# 1. Load context
/primer

# 2. Research topic
/research-topic "your topic here"

# 3. Plan next task based on research
/task-next
```

### Troubleshooting Workflow

```bash
# 1. Run diagnostics
/troubleshoot

# 2. Check MCP health
/mcp-health-check

# 3. Validate structure
/structure-validate

# 4. Review help if needed
/help problematic-command
```

---

## 💡 Best Practices

### Session Management

✅ **DO**:
- Always start with `/primer`
- Check MCP health if issues occur
- Re-run `/primer` after pulling changes
- Use `/task-next` when unsure what to do

❌ **DON'T**:
- Skip initialization
- Ignore health check warnings
- Continue with failed MCP servers
- Guess next task without research

### Research Best Practices

✅ **DO**:
- Be specific in research queries
- Apply research findings to code
- Save important research to KB
- Cross-reference with existing patterns

❌ **DON'T**:
- Use overly generic queries
- Ignore codebase context
- Skip best practices section
- Implement without validation

---

## 🐛 Troubleshooting

### Common Issues

**Primer Fails to Load Context**:
```bash
# Check file accessibility
ls -la CLAUDE.md .claude/

# Validate structure
/structure-validate

# Check permissions
cat .claude/settings.local.json
```

**Task-Next Returns No Tasks**:
```bash
# Check for TODOs manually
/research-topic "project roadmap"

# Review recent commits
git log -10 --oneline

# Check documentation
cat README.md
```

**Research Timeout**:
```bash
# Check MCP health
/mcp-health-check

# Use narrower query
/research-topic "specific narrow topic"

# Try again with basic search
/research-topic --simple "topic"
```

---

## 🔗 Related Commands

### Natural Progressions

From → To:
- `/primer` → `/task-next` (after context loaded)
- `/task-next` → `/research-topic` (for deep dive)
- `/research-topic` → Implementation (use findings)
- `/structure-validate` → Fix issues → `/structure-validate`

### Complementary Commands

Core + Other Categories:
- `/primer` + `/azure-status` (Azure projects)
- `/task-next` + `/test-generate` (TDD workflow)
- `/research-topic` + `/kb-add` (save research)

---

**Navigate**: [← Commands Home](./README.md) | [Knowledge Management →](./knowledge-management.md) | [Architecture →](../architecture/README.md)

---

*Essential commands for essential workflows*
