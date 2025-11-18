# 🔧 Creating Custom Commands

> **Complete guide to building your own slash commands**

Learn how to create powerful custom slash commands that automate your unique workflows and integrate with Claude Code's capabilities.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Command Structure](#-command-structure)
- [Frontmatter Reference](#-frontmatter-reference)
- [Writing Instructions](#-writing-instructions)
- [Advanced Features](#-advanced-features)
- [Real-World Examples](#-real-world-examples)
- [Testing Commands](#-testing-commands)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

Custom slash commands are markdown files that define automated workflows for Claude Code. They enable you to:

- **Automate Repetitive Tasks** - Turn multi-step workflows into single commands
- **Standardize Processes** - Ensure consistent execution across team
- **Compose Tools** - Combine built-in tools, agents, and MCP servers
- **Share Workflows** - Distribute commands via git
- **Build Custom Automation** - Create project-specific workflows

### Command Capabilities

A custom command can:
- ✅ Use any built-in tools (Read, Write, Edit, Bash, etc.)
- ✅ Invoke specialized agents (Task tool)
- ✅ Call MCP servers (requires-mcp)
- ✅ Accept user arguments
- ✅ Execute conditional logic
- ✅ Compose other commands
- ✅ Generate structured output

---

## 🚀 Quick Start

### 1. Create Your First Command

```bash
# Create commands directory
mkdir -p .claude/commands/

# Create command file
cat > .claude/commands/my-first-command.md << 'EOF'
---
description: My first custom command
allowed-tools: Read, Write, Bash
---

# My First Command

This is a simple command that greets the user.

## Steps

1. Read the project README
2. Count the number of lines
3. Print a greeting with the line count

## Implementation

Use the Read tool to read README.md.
Use Bash to count lines: `wc -l README.md`
Print: "Hello! Your README has X lines."
EOF
```

### 2. Test Your Command

```bash
# Invoke the command
/my-first-command
```

### 3. Expected Output

```
✅ Executed: my-first-command

📖 Reading README.md...
📊 Counting lines...

Hello! Your README has 87 lines.
```

---

## 📋 Command Structure

### Complete Command Template

```markdown
---
# Required
description: Brief description of what this command does

# Optional
allowed-tools: Read, Write, Edit, Bash, Task, Grep, Glob
requires-mcp: microsoft-docs, serena, azure-mcp
argument-hint: [optional-arguments]
category: custom
author: your-name
version: 1.0.0
---

# Command Name

Brief overview of the command's purpose.

## Purpose

Detailed explanation of:
- What problem this solves
- When to use this command
- Expected outcomes

## Prerequisites (if any)

- Required tools
- Required MCP servers
- Required permissions
- Environment setup

## Steps

1. **Step 1 Name**
   - Substep details
   - What happens here

2. **Step 2 Name**
   - Substep details
   - What happens here

3. **Step 3 Name**
   - Substep details
   - What happens here

## Arguments

If the command accepts arguments via $ARGUMENTS:

- `argument1` - Description
- `argument2` - Description (optional)

## Examples

```bash
# Example 1
/command-name arg1 arg2

# Example 2
/command-name "argument with spaces"
```

## Expected Output

Describe what the user should expect to see.

## Error Handling

How errors are handled and what to do if something fails.

## Related Commands

- `/related-command-1`
- `/related-command-2`
```

---

## 🏷️ Frontmatter Reference

### Required Fields

```yaml
---
description: Brief, clear description (shown in command list)
---
```

### Optional Fields

```yaml
---
description: Command description

# Tools the command will use
allowed-tools: Read, Write, Edit, Bash, Task, Grep, Glob

# MCP servers required
requires-mcp: microsoft-docs, serena, azure-mcp

# Hint shown to user about arguments
argument-hint: [file-path] [options]

# Category for organization
category: custom

# Author information
author: your-name@example.com

# Version for tracking changes
version: 1.0.0

# Experimental/beta flag
experimental: true
---
```

### Tool Permissions

Available tools:
- `Read` - Read files
- `Write` - Write new files
- `Edit` - Edit existing files
- `Bash` - Execute bash commands
- `Task` - Invoke specialized agents
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web

---

## ✍️ Writing Instructions

### Clear, Actionable Steps

✅ **Good Example**:
```markdown
## Steps

1. **Analyze Current Code**
   - Use Grep to find all TODO comments
   - Parse each TODO for priority indicators
   - Group by file and priority

2. **Generate Task List**
   - Create markdown task list
   - Include file locations
   - Add priority labels
   - Sort by priority

3. **Output Results**
   - Write to TODO.md
   - Print summary to console
   - Add to knowledge base
```

❌ **Bad Example**:
```markdown
## Steps

1. Look at the code
2. Find the TODOs
3. Make a list
```

### Using Arguments

Access user input via `$ARGUMENTS`:

```markdown
---
description: Search codebase for pattern
argument-hint: "search pattern"
---

# Search Command

## Steps

1. **Parse Arguments**
   - Extract search pattern from $ARGUMENTS
   - If empty, prompt user for pattern

2. **Search Codebase**
   - Use Grep with pattern: $ARGUMENTS
   - Search in src/ directory
   - Filter results

3. **Present Results**
   - Show matching files
   - Display match count
   - Suggest next actions
```

### Conditional Logic

```markdown
## Steps

1. **Check Prerequisites**
   - If .env file exists, proceed
   - Otherwise, create .env from .env.example
   - Validate required variables

2. **Deploy Based on Environment**
   - If $ARGUMENTS contains "production":
     * Run additional validation
     * Require confirmation
     * Use production config
   - Otherwise:
     * Use development config
     * Skip confirmation
```

---

## 🚀 Advanced Features

### Invoking Agents

Use the Task tool to invoke specialized agents:

```markdown
---
description: Research and implement feature
allowed-tools: Task, Read, Write, Edit
requires-mcp: microsoft-docs
---

# Research-Implement Command

## Steps

1. **Research Phase** (Use Task agent)
   - Launch research agent with search-specialist type
   - Provide topic: $ARGUMENTS
   - Agent should:
     * Search microsoft-docs for best practices
     * Find code examples
     * Identify common patterns
     * Return comprehensive summary

2. **Implementation Phase** (Use Task agent)
   - Launch python-pro agent
   - Provide research findings
   - Agent should:
     * Implement feature
     * Follow best practices from research
     * Add tests
     * Update documentation

3. **Validation Phase** (Use Task agent)
   - Launch validation-gates agent
   - Run test suite
   - Verify implementation
   - Report results
```

### Using MCP Servers

```markdown
---
description: Search Azure documentation and implement
requires-mcp: microsoft-docs, azure-mcp
allowed-tools: Read, Write, Task
---

# Azure Feature Implementation

## Steps

1. **Search Documentation** (MCP: microsoft-docs)
   - Use microsoft_docs_search with query from $ARGUMENTS
   - Retrieve relevant documentation
   - Extract key concepts and code examples

2. **Check Azure Resources** (MCP: azure-mcp)
   - Use azure-mcp to check current resources
   - Verify prerequisites exist
   - Check permissions

3. **Implement Feature**
   - Use Task agent with azure-focused prompt
   - Provide documentation and resource info
   - Generate implementation code

4. **Deploy to Azure** (MCP: azure-mcp)
   - Use azure-mcp to deploy
   - Monitor deployment
   - Verify success
```

### Parallel Agent Execution

```markdown
---
description: Parallel research and analysis
allowed-tools: Task
---

# Parallel Research Command

## Steps

1. **Launch Parallel Agents**

   Launch 4 agents concurrently:

   **Agent 1: Documentation Research**
   - Search official docs
   - Extract best practices

   **Agent 2: Code Pattern Search**
   - Search codebase for patterns
   - Identify existing implementations

   **Agent 3: Security Analysis**
   - Research security implications
   - Find common vulnerabilities

   **Agent 4: Performance Research**
   - Research performance patterns
   - Find optimization techniques

2. **Synthesize Results**
   - Wait for all agents to complete
   - Combine findings
   - Remove duplicates
   - Create comprehensive report

3. **Output Report**
   - Write to docs/research/
   - Add to knowledge base
   - Print summary
```

### Error Handling

```markdown
## Steps

1. **Validate Prerequisites**
   - Check if Azure CLI is installed
   - If not:
     * Print installation instructions
     * Exit with error message
   - Check if logged in to Azure
   - If not:
     * Print: "Run: az login"
     * Exit

2. **Deploy with Error Handling**
   - Attempt deployment
   - If deployment fails:
     * Capture error message
     * Check common failure causes
     * Provide specific remediation
     * Save error to logs/
   - If successful:
     * Print success message
     * Show deployment URL
```

---

## 💼 Real-World Examples

### Example 1: Daily Standup Generator

```markdown
---
description: Generate daily standup summary
allowed-tools: Bash, Read, Write
---

# Daily Standup Generator

## Purpose

Generates a summary of work done yesterday and plans for today.

## Steps

1. **Get Yesterday's Work**
   - Use Bash: `git log --since="yesterday" --author="$(git config user.email)" --oneline`
   - Parse commits
   - Group by type (feat, fix, docs, etc.)

2. **Get Today's Plan**
   - Read TODO.md if exists
   - Check for in-progress tasks
   - Review open pull requests

3. **Generate Summary**
   - Format as standup template
   - Include:
     * Yesterday: [commits]
     * Today: [planned tasks]
     * Blockers: [any blockers noted]

4. **Output**
   - Print to console
   - Optionally save to standup-notes/YYYY-MM-DD.md
```

### Example 2: API Endpoint Generator

```markdown
---
description: Generate FastAPI endpoint with tests
allowed-tools: Task, Read, Write, Edit
requires-mcp: microsoft-docs
---

# Generate API Endpoint

## Arguments

- Endpoint path (e.g., "/users/{id}")
- HTTP method (GET, POST, PUT, DELETE)

## Steps

1. **Research Patterns** (Agent)
   - Search for FastAPI best practices
   - Find similar endpoints in codebase
   - Identify patterns to follow

2. **Generate Endpoint Code**
   - Parse $ARGUMENTS for path and method
   - Create endpoint function
   - Add Pydantic models
   - Add error handling
   - Follow project patterns

3. **Generate Tests**
   - Create test file
   - Add test cases:
     * Happy path
     * Error cases
     * Edge cases
     * Auth checks

4. **Update Documentation**
   - Add endpoint to API docs
   - Include request/response examples
   - Note authentication requirements

5. **Validate**
   - Run tests
   - Check coverage
   - Run linter
```

### Example 3: Code Review Automation

```markdown
---
description: Automated code review with checklist
allowed-tools: Bash, Read, Grep, Task
---

# Automated Code Review

## Steps

1. **Get Changed Files**
   - Use Bash: `git diff --name-only main...HEAD`
   - Filter for source files only
   - Skip test files for now

2. **Review Each File** (Agent per file)
   - Launch review agent for each file
   - Agent checks:
     * Code quality
     * Security issues
     * Performance concerns
     * Best practices
     * Documentation
   - Collect issues

3. **Check Test Coverage**
   - For each changed file
   - Check if tests were added/updated
   - Verify test coverage >80%
   - Flag if coverage decreased

4. **Generate Review Report**
   - Group issues by severity
   - Include file:line references
   - Provide fix suggestions
   - Calculate approval score

5. **Output Report**
   - Print summary
   - Write detailed report to code-review.md
   - Exit with status (pass/fail)
```

---

## 🧪 Testing Commands

### Manual Testing

```bash
# 1. Test basic execution
/my-command

# 2. Test with arguments
/my-command arg1 arg2

# 3. Test error cases
/my-command invalid-input

# 4. Test with empty arguments
/my-command

# 5. Verify output
ls expected-output-file.md
```

### Testing Checklist

- [ ] Command appears in `/help`
- [ ] Description is clear
- [ ] Arguments are parsed correctly
- [ ] Required tools are available
- [ ] MCP servers are responding
- [ ] Error handling works
- [ ] Output is as expected
- [ ] Edge cases handled
- [ ] Performance acceptable

### Debug Mode

Add debug output to your commands:

```markdown
## Steps

1. **Debug: Print Arguments**
   - Print: "DEBUG: Arguments = $ARGUMENTS"
   - Print: "DEBUG: Argument count = [count]"

2. **Debug: Print State**
   - Print current directory
   - Print git status
   - Print relevant environment variables

3. **Proceed with Main Logic**
   - ... rest of command ...
```

---

## 💡 Best Practices

### Command Design

✅ **DO**:
- **Single Responsibility** - One command, one purpose
- **Clear Naming** - Descriptive, verb-based names
- **Good Documentation** - Explain what, why, when
- **Example Usage** - Show concrete examples
- **Error Handling** - Graceful failure with helpful messages
- **Idempotent** - Safe to run multiple times
- **Validate Input** - Check arguments and prerequisites

❌ **DON'T**:
- Create overly complex commands
- Mix unrelated functionality
- Skip error handling
- Hardcode values
- Ignore security implications
- Skip documentation
- Make destructive commands without safeguards

### Performance

✅ **DO**:
- Use parallel agents when possible
- Cache expensive operations
- Limit file reads
- Use specific Grep/Glob patterns
- Set reasonable timeouts

❌ **DON'T**:
- Read entire large files unnecessarily
- Search entire disk without filters
- Create infinite loops
- Forget to limit agent execution time

### Security

✅ **DO**:
- Validate all input
- Use permission model
- Sanitize file paths
- Require confirmation for dangerous operations
- Log sensitive operations
- Use environment variables for secrets

❌ **DON'T**:
- Execute arbitrary code from input
- Expose secrets in output
- Skip permission checks
- Ignore path traversal risks
- Trust user input blindly

---

## 🐛 Troubleshooting

### Common Issues

**Command Not Found**:
```bash
# Check file location
ls .claude/commands/my-command.md
ls ~/.claude/commands/my-command.md

# Check file name (must be .md)
# Check for typos in command name
```

**Frontmatter Parse Error**:
```yaml
# Bad (not valid YAML)
---
description: My command's description
allowed-tools: Read Write
---

# Good
---
description: "My command's description"
allowed-tools: Read, Write
---
```

**Tool Permission Denied**:
```json
// Add to .claude/settings.local.json
{
  "permissions": {
    "allow": [
      "Bash(your-command:*)"
    ]
  }
}
```

**MCP Server Not Available**:
```bash
# Check MCP health
/mcp-health-check

# Verify requires-mcp matches server name
# Check server is configured in settings
```

**Agent Invocation Fails**:
```markdown
# Ensure Task tool is in allowed-tools
allowed-tools: Task, Read, Write

# Verify agent type exists
# Check agent has necessary permissions
```

### Debug Techniques

1. **Add Verbose Output**
   ```markdown
   - Print: "Starting step 1..."
   - Print: "Arguments: $ARGUMENTS"
   - Print: "Current directory: $(pwd)"
   ```

2. **Test Components Separately**
   ```bash
   # Test Grep pattern
   grep "pattern" file.txt

   # Test Bash command
   bash -c "your command"
   ```

3. **Check Permissions**
   ```bash
   # View current permissions
   cat .claude/settings.local.json
   ```

4. **Validate YAML**
   ```bash
   # Use online YAML validator
   # Or: python -c "import yaml; yaml.safe_load(open('file.md').read().split('---')[1])"
   ```

---

## 📚 Additional Resources

### Example Commands

Browse real-world examples:
```bash
# View example commands
ls claude_examples/slash-commands/

# Categories
ls claude_examples/slash-commands/code-quality/
ls claude_examples/slash-commands/development/
ls claude_examples/slash-commands/git-operations/
```

### Command Templates

Quick-start templates:
- **Basic Command**: Simple tool usage
- **Research Command**: MCP + agents
- **Multi-Agent**: Parallel execution
- **Deployment Command**: Azure integration
- **Review Command**: Code analysis

### Official Documentation

- [Claude Code Commands Docs](https://docs.claude.com/claude-code/commands)
- [Tool Reference](https://docs.claude.com/claude-code/tools)
- [Agent System](https://docs.claude.com/claude-code/agents)
- [MCP Protocol](https://modelcontextprotocol.io)

---

## ✅ Command Creation Checklist

Before deploying your command:

- [ ] Clear, descriptive name
- [ ] Complete frontmatter
- [ ] Detailed documentation
- [ ] Step-by-step instructions
- [ ] Argument handling
- [ ] Error handling
- [ ] Example usage
- [ ] Prerequisites documented
- [ ] Tools listed in allowed-tools
- [ ] MCP servers listed in requires-mcp
- [ ] Permissions configured
- [ ] Tested with valid input
- [ ] Tested with invalid input
- [ ] Tested with edge cases
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] Documentation complete

---

**Navigate**: [← Advanced Workflows](./advanced-workflows.md) | [Commands Home](./README.md) | [Architecture →](../architecture/README.md)

---

*Build the commands you wish existed*
