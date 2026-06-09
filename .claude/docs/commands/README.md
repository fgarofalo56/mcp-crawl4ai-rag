# 🚀 Commands Documentation

> **Complete command reference for Claude Code workflows**

This directory contains comprehensive documentation for all custom slash commands available in the Claude Code base project setup. Commands are organized by category to help you quickly find the right tool for your task.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Command Categories](#-command-categories)
- [Command Organization](#-command-organization)
- [Usage Patterns](#-usage-patterns)
- [Permission Model](#-permission-model)
- [Creating Custom Commands](#-creating-custom-commands)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)
- [Related Documentation](#-related-documentation)

---

## 🎯 Overview

Custom slash commands transform repetitive development tasks into single-command workflows. They leverage Claude Code's capabilities for:

- **Parallel Processing** - Execute multiple agents concurrently
- **Deep Code Analysis** - Understand patterns and architecture
- **Intelligent Automation** - Context-aware task execution
- **Knowledge Management** - Persistent learning across sessions
- **Azure Integration** - Cloud development workflows

### What are Slash Commands?

Slash commands are user-facing interfaces that:
- Start with `/` (e.g., `/primer`, `/task-next`)
- Accept optional parameters
- Orchestrate agents, tools, and MCP servers
- Provide structured, repeatable workflows
- Can be project-specific or global

### Command Hierarchy

Commands are organized into logical categories:

```
commands/
├── core-essentials.md          ← Essential workflow commands
├── knowledge-management.md     ← Knowledge base commands
├── azure-development.md        ← Azure-specific commands
├── development-support.md      ← General development commands
├── testing-qa.md              ← Testing and quality commands
├── git-operations.md          ← Git workflow commands
├── advanced-workflows.md      ← Complex multi-agent workflows
└── creating-custom-commands.md ← Guide for building commands
```

---

## 🚀 Quick Start

### Installing Commands

**Project-Specific Commands**:
```bash
# Create commands directory if it doesn't exist
mkdir -p .claude/commands/

# Copy command file to project
cp ~/templates/commands/my-command.md .claude/commands/
```

**Global Commands** (available in all projects):
```bash
# Create global commands directory
mkdir -p ~/.claude/commands/

# Copy command file
cp ~/templates/commands/my-command.md ~/.claude/commands/
```

### Using Commands

```bash
# Basic usage
/command-name

# With parameters
/command-name parameter1 parameter2

# With complex arguments
/command-name "argument with spaces" --flag=value
```

### Essential First Commands

```bash
# Prime Claude with project context
/primer

# Get next task with research
/task-next

# Review code quality
/review-general

# Create smart commit
/smart-commit

# Get help
/help
```

---

## 📋 Command Categories

### 1. Core Essentials
**File**: [core-essentials.md](./core-essentials.md)

Essential commands for daily development workflows:
- `/primer` - Initialize project context
- `/task-next` - Get next task with research
- `/research-topic` - Deep-dive research
- `/structure-validate` - Validate directory structure
- `/help` - Get help with commands

**Use when**: Starting sessions, planning tasks, validating structure

---

### 2. Knowledge Management
**File**: [knowledge-management.md](./knowledge-management.md)

Commands for managing project knowledge and patterns:
- `/kb-add` - Add knowledge to knowledge base
- `/kb-search` - Search knowledge base
- `/kb-extract-patterns` - Extract patterns from code
- `/kb-update` - Update knowledge base
- `/kb-stats` - View knowledge base statistics

**Use when**: Capturing learnings, searching patterns, building institutional knowledge

---

### 3. Azure Development
**File**: [azure-development.md](./azure-development.md)

Azure-specific development and deployment commands:
- `/azure-init` - Initialize Azure resources
- `/azure-deploy` - Deploy to Azure
- `/azure-status` - Check deployment status
- `/bicep-validate` - Validate Bicep templates
- `/azure-logs` - View Azure logs

**Use when**: Working with Azure resources, deployments, infrastructure

---

### 4. Development Support
**File**: [development-support.md](./development-support.md)

General development support commands:
- `/debug-rca` - Root cause analysis
- `/refactor-simple` - Quick refactoring
- `/code-explain` - Explain code
- `/dependencies-check` - Check dependencies
- `/security-scan` - Security analysis

**Use when**: Debugging, refactoring, understanding code, security checks

---

### 5. Testing & QA
**File**: [testing-qa.md](./testing-qa.md)

Testing and quality assurance commands:
- `/test-generate` - Generate tests
- `/test-run` - Run test suite
- `/coverage-check` - Check test coverage
- `/review-staged` - Review staged changes
- `/review-general` - Comprehensive code review

**Use when**: Writing tests, reviewing code, ensuring quality

---

### 6. Git Operations
**File**: [git-operations.md](./git-operations.md)

Git workflow and operations commands:
- `/smart-commit` - Intelligent commit creation
- `/create-pr` - Create pull request
- `/conflict-resolver` - Resolve merge conflicts
- `/new-dev-branch` - Create development branch
- `/git-cleanup` - Clean up branches

**Use when**: Committing, creating PRs, resolving conflicts, branch management

---

### 7. Advanced Workflows
**File**: [advanced-workflows.md](./advanced-workflows.md)

Complex multi-agent workflow commands:
- `/hackathon-prp` - Rapid prototyping (25 agents)
- `/parallel-prp-creation` - Multiple PRP variations
- `/research-validate-implement` - Full development cycle
- `/onboarding-generate` - Generate onboarding docs
- `/architecture-review` - Architecture analysis

**Use when**: Rapid development, complex tasks, comprehensive analysis

---

## 🗂️ Command Organization

### File Location Strategy

Commands can be placed in multiple locations, with priority order:

1. **Project Local** (`.claude/commands/`) - Highest priority
2. **Home Global** (`~/.claude/commands/`) - Fallback
3. **Template Examples** (`claude_examples/slash-commands/`) - Reference only

### Naming Conventions

Commands follow a hierarchical naming pattern:

```
/category:command-name
```

**Examples**:
```bash
# Core commands (no prefix)
/primer
/help

# Categorized commands
/azure:deploy
/git:smart-commit
/kb:search
/test:coverage-check

# Experimental commands
/experimental:hackathon-prp
/experimental:parallel-research
```

### Command Structure

Each command file follows this structure:

```markdown
---
description: Brief description of what the command does
allowed-tools: Edit, Read, Bash, Task
argument-hint: [optional-arguments]
requires-mcp: microsoft-docs, serena
---

# Command Instructions

Detailed instructions for Claude Code.
Use $ARGUMENTS to reference user input.

## Example Usage

Example of how to use the command.
```

---

## 🔧 Usage Patterns

### Basic Patterns

**1. Simple Invocation**:
```bash
/primer
```

**2. With Arguments**:
```bash
/research-topic "Azure Container Apps security best practices"
```

**3. Chained Commands**:
```bash
/primer && /task-next
```

### Advanced Patterns

**1. Conditional Execution**:
```bash
# Only if tests pass
/test-run && /deploy
```

**2. Multiple Parameters**:
```bash
/azure-deploy production westus2 --skip-tests
```

**3. Complex Arguments**:
```bash
/research-validate-implement "Feature: Add user authentication with OAuth2"
```

### Parallel Execution

Some commands execute multiple agents in parallel:

```bash
# 25 parallel agents
/hackathon-prp "Build real-time chat application"

# 4 parallel research agents
/parallel-research "Best practices for microservices"
```

### Command Composition

Commands can compose other commands:

```markdown
---
description: Full development workflow
---

# Research → Implement → Test → Deploy

1. Run /research-topic $ARGUMENTS
2. Implement based on research
3. Run /test-generate
4. Run /test-run
5. If tests pass, run /smart-commit
```

---

## 🔒 Permission Model

### Three-Tier Security

Commands operate under a permission model:

1. **Allow** - Automatic execution
2. **Deny** - Blocked operations
3. **Ask** - Require user approval

### Command-Level Permissions

Specified in command frontmatter:

```markdown
---
description: Deploy to Azure
allowed-tools: Bash, Read, Edit
required-permissions:
  - Bash(az:*)
  - Bash(docker:*)
---
```

### User Approval

Commands that require approval:

```bash
# Will ask before executing
/azure-deploy production

# Pre-approved in settings
/azure-status
```

### Dangerous Operations

Always require explicit approval:
- `git push --force`
- `rm -rf`
- `docker system prune -a`
- Production deployments
- Database migrations

---

## 🛠️ Creating Custom Commands

### Quick Template

```markdown
---
description: Your command description
allowed-tools: Read, Write, Edit, Bash
argument-hint: [your-argument]
---

# Your Command Name

## Purpose
What does this command do?

## Instructions

Step-by-step instructions for Claude Code.

1. Parse $ARGUMENTS
2. Perform task
3. Report results

## Example

Example usage and expected output.
```

### Full Guide

See [creating-custom-commands.md](./creating-custom-commands.md) for:
- Detailed template structure
- Advanced features (MCP servers, agents, hooks)
- Testing and validation
- Best practices
- Real-world examples

---

## 💡 Best Practices

### Command Design

✅ **DO**:
- Use clear, descriptive names
- Provide detailed descriptions
- Include usage examples
- Handle errors gracefully
- Document prerequisites
- Test thoroughly

❌ **DON'T**:
- Create overly generic commands
- Skip error handling
- Hardcode values
- Ignore security implications
- Forget to document

### Command Usage

✅ **DO**:
- Use `/primer` at session start
- Review command output
- Provide clear arguments
- Check permissions first
- Read command descriptions

❌ **DON'T**:
- Skip validation steps
- Ignore error messages
- Run unknown commands
- Bypass security prompts
- Chain risky operations

### Organization

✅ **DO**:
- Group related commands
- Use consistent naming
- Keep commands focused
- Maintain documentation
- Version control commands

❌ **DON'T**:
- Mix unrelated functionality
- Use inconsistent patterns
- Create monolithic commands
- Skip documentation
- Hardcode in commands

---

## 🐛 Troubleshooting

### Common Issues

**Command Not Found**:
```bash
# Check command exists
ls .claude/commands/
ls ~/.claude/commands/

# Verify file extension (.md)
# Check file naming (lowercase, hyphens)
```

**Permission Denied**:
```bash
# Check settings.local.json
cat .claude/settings.local.json

# Add permission:
{
  "permissions": {
    "allow": ["Bash(your-command:*)"]
  }
}
```

**MCP Server Unavailable**:
```bash
# Check MCP server health
/mcp-health-check

# Restart MCP server
# See architecture/mcp-integration.md
```

**Command Fails Silently**:
```bash
# Check Claude Code output
# Enable debug mode
# Review command syntax
# Validate frontmatter YAML
```

### Debug Commands

```bash
# Validate command file
/command-validate my-command

# Test command syntax
/command-test my-command

# Check permissions
/permissions-check my-command

# View command details
/command-info my-command
```

### Getting Help

1. **Check Documentation**:
   - This README
   - Specific command category docs
   - [creating-custom-commands.md](./creating-custom-commands.md)

2. **Review Examples**:
   ```bash
   # View example commands
   ls claude_examples/slash-commands/
   ```

3. **Use Help Command**:
   ```bash
   /help
   /help my-command
   ```

4. **Check Architecture**:
   - [architecture/README.md](../architecture/README.md)
   - [architecture/system-design.md](../architecture/system-design.md)

---

## 🔗 Related Documentation

### Essential Reading

| Document | Purpose | Priority |
|----------|---------|----------|
| [Core Essentials](./core-essentials.md) | Essential daily commands | HIGH |
| [Creating Custom Commands](./creating-custom-commands.md) | Build your own commands | HIGH |
| [Azure Development](./azure-development.md) | Azure workflows | MEDIUM |
| [Git Operations](./git-operations.md) | Git workflows | MEDIUM |
| [Advanced Workflows](./advanced-workflows.md) | Complex patterns | LOW |

### Architecture Documentation

| Document | Purpose |
|----------|---------|
| [System Design](../architecture/system-design.md) | Overall architecture |
| [Data Flow](../architecture/data-flow.md) | How commands execute |
| [MCP Integration](../architecture/mcp-integration.md) | External capabilities |

### Related Components

| Component | Documentation |
|-----------|---------------|
| **Agents** | [agents/README.md](../agents/README.md) |
| **Hooks** | [hooks/README.md](../hooks/README.md) |
| **Settings** | [settings/README.md](../settings/README.md) |
| **MCP Servers** | [architecture/mcp-integration.md](../architecture/mcp-integration.md) |

---

## 📊 Command Catalog Quick Reference

### By Frequency of Use

| Command | Category | Frequency | Description |
|---------|----------|-----------|-------------|
| `/primer` | Core | Daily | Initialize context |
| `/task-next` | Core | Daily | Get next task |
| `/smart-commit` | Git | Daily | Create commit |
| `/test-run` | Testing | Daily | Run tests |
| `/azure-status` | Azure | Hourly | Check status |
| `/review-general` | Testing | Weekly | Code review |
| `/kb-search` | Knowledge | As needed | Search KB |
| `/hackathon-prp` | Advanced | Rarely | Rapid prototype |

### By Execution Time

| Command | Time | Agents | Resources |
|---------|------|--------|-----------|
| `/primer` | <1 min | 1 | Low |
| `/task-next` | 1-2 min | 2 | Medium |
| `/review-general` | 2-5 min | 1 | Medium |
| `/parallel-research` | 5-15 min | 15 | High |
| `/hackathon-prp` | 30-60 min | 25 | Very High |

### By Complexity

| Level | Commands | Description |
|-------|----------|-------------|
| **Basic** | `/primer`, `/help`, `/task-next` | Single-agent, quick execution |
| **Intermediate** | `/smart-commit`, `/review-general`, `/azure-deploy` | Multiple steps, some orchestration |
| **Advanced** | `/parallel-research`, `/hackathon-prp` | Multi-agent, long-running |

---

## 🎯 Quick Reference Cards

### Essential Commands Card

```
┌──────────────────────────────────────┐
│     ESSENTIAL COMMANDS               │
├──────────────────────────────────────┤
│ /primer          Init context        │
│ /task-next       Next task           │
│ /smart-commit    Smart commit        │
│ /test-run        Run tests           │
│ /help            Get help            │
└──────────────────────────────────────┘
```

### Azure Commands Card

```
┌──────────────────────────────────────┐
│     AZURE COMMANDS                   │
├──────────────────────────────────────┤
│ /azure-status    Check status        │
│ /azure-deploy    Deploy resources    │
│ /azure-logs      View logs           │
│ /bicep-validate  Validate templates  │
└──────────────────────────────────────┘
```

### Git Commands Card

```
┌──────────────────────────────────────┐
│     GIT COMMANDS                     │
├──────────────────────────────────────┤
│ /smart-commit      Smart commit      │
│ /create-pr         Create PR         │
│ /conflict-resolver Resolve conflicts │
│ /new-dev-branch    New branch        │
└──────────────────────────────────────┘
```

---

## 📈 Command Usage Analytics

### Recommended Workflows

**Daily Development**:
```bash
# Morning startup
/primer

# Task planning
/task-next

# Development cycle
/test-run
/smart-commit

# End of day
/kb-extract-patterns
```

**Azure Deployment**:
```bash
# Pre-deployment
/bicep-validate
/test-run

# Deployment
/azure-deploy staging

# Verification
/azure-status
/azure-logs
```

**Code Review**:
```bash
# Before PR
/review-staged
/test-run
/security-scan

# Create PR
/create-pr
```

---

## ✅ Commands Documentation Checklist

- [x] Overview and introduction
- [x] Quick start guide
- [x] Command categories (7 categories)
- [x] Command organization
- [x] Usage patterns
- [x] Permission model
- [x] Creating custom commands overview
- [x] Best practices
- [x] Troubleshooting
- [x] Related documentation
- [x] Command catalog quick reference
- [x] Quick reference cards
- [x] Command usage analytics

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: DevEx Team
**Status**: Active

### Change Log

- **2025-01-15**: Initial commands documentation
  - Created comprehensive command hub
  - Documented all command categories
  - Added quick reference cards
  - Included usage patterns and best practices

---

**Navigate**: [← Back to Main](../README.md) | [Core Essentials →](./core-essentials.md) | [Architecture →](../architecture/README.md)

---

*Built with ❤️ for developers who love powerful command workflows*
