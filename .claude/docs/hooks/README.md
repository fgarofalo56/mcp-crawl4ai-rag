# 🪝 Hooks Documentation

> **Complete event-driven automation reference for Claude Code**

This directory contains comprehensive documentation for the Claude Code hooks system. Hooks enable automatic, event-driven automation that responds to session lifecycle events, Git operations, and custom triggers.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Hook Categories](#-hook-categories)
- [When to Use Hooks](#-when-to-use-hooks)
- [Hook Execution Flow](#-hook-execution-flow)
- [Documentation Structure](#-documentation-structure)
- [Configuration](#-configuration)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)
- [Related Documentation](#-related-documentation)

---

## 🎯 Overview

### What are Hooks?

Hooks are event-driven automation scripts that execute automatically in response to specific triggers. They enable:

- **Session Management** - Initialize and cleanup session state
- **Git Integration** - Validate, enhance, and automate Git workflows
- **Knowledge Management** - Automatically capture and update learnings
- **Quality Assurance** - Enforce standards and run validations
- **Workflow Automation** - Custom automations without manual intervention

### Hook Philosophy

```
Event Trigger → Hook Execution → Automated Action
     │                │                  │
     │                │                  └→ Update Knowledge Base
     │                └→ Validate Code → Pass/Fail
     └→ session-start → Load Context → Ready to Work
```

**Key Principles**:
- ✅ **Automatic** - No manual intervention required
- ✅ **Reliable** - Should not fail unexpectedly
- ✅ **Fast** - Complete within seconds
- ✅ **Transparent** - Clear output and logging
- ✅ **Configurable** - Easy to enable/disable

### Hook vs Command vs Agent

| Aspect | Hook | Command | Agent |
|--------|------|---------|-------|
| **Trigger** | Automatic (events) | Manual (user invocation) | Manual (via commands) |
| **When** | Session start, pre-commit, etc. | User decides | Command orchestrates |
| **Purpose** | Automation, validation | Workflow orchestration | Specialized tasks |
| **Execution** | Event-driven | User-driven | Command-driven |
| **Examples** | session-start, pre-commit | /primer, /task-next | validation-gates, research |

---

## 🚀 Quick Start

### Installing Hooks

**1. Create hooks directory**:
```bash
mkdir -p .claude/hooks/
```

**2. Add hook script**:
```bash
# Copy example hook
cp examples/hooks/session-start.js .claude/hooks/

# Or create your own
touch .claude/hooks/my-hook.js
```

**3. Configure in settings.local.json**:
```json
{
  "hooks": {
    "session-start": {
      "enabled": true,
      "file": ".claude/hooks/session-start.js",
      "timeout": 30000
    }
  }
}
```

### Your First Hook

**Simple session-start hook**:

```javascript
// .claude/hooks/session-start.js
module.exports = async function(context) {
  console.log('🎉 Session started!');

  // Check project structure
  const hasPackageJson = await context.fileExists('package.json');
  if (!hasPackageJson) {
    console.warn('⚠️  No package.json found');
  }

  // Load project memory
  const memory = await context.loadMemory();
  console.log(`📚 Loaded ${memory.length} memories`);

  return { success: true };
};
```

**Testing the hook**:
```bash
# Start new session - hook will run automatically
claude
```

### Essential First Hooks

```bash
# Session initialization
session-start → Load context, check health

# Git validation
pre-commit → Lint, test, validate

# Knowledge capture
post-commit → Extract patterns, update KB

# Session cleanup
session-end → Save state, generate summary
```

---

## 📋 Hook Categories

### 1. Session Lifecycle Hooks

**Trigger**: Session start/end events

**Examples**:
- `session-start` - Initialize session, load context
- `session-end` - Save state, generate summary

**Use cases**:
- Load project context
- Check MCP server health
- Validate environment
- Save session memory

**Documentation**: [session-hooks.md](./session-hooks.md)

---

### 2. Git Integration Hooks

**Trigger**: Git operations (commit, push)

**Examples**:
- `pre-commit` - Validate before commit
- `post-commit` - Extract patterns after commit
- `pre-push` - Final validation before push

**Use cases**:
- Code quality checks
- Test execution
- Pattern extraction
- Changelog updates

**Documentation**: [git-hooks.md](./git-hooks.md)

---

### 3. Custom Hooks

**Trigger**: Custom events

**Examples**:
- `file-change` - React to file modifications
- `test-complete` - After test execution
- `deploy-start` - Before deployment

**Use cases**:
- Custom validations
- Workflow automation
- Integration triggers
- Monitoring and alerts

**Documentation**: [creating-hooks.md](./creating-hooks.md)

---

## 🤔 When to Use Hooks

### Use Hooks When:

✅ **Automatic Execution Needed**
```
Event: User starts session
Hook: Load project context automatically
```

✅ **Validation Gates Required**
```
Event: User attempts commit
Hook: Run tests, block if failing
```

✅ **Knowledge Capture Desired**
```
Event: Successful commit
Hook: Extract patterns, update KB
```

✅ **Consistency Enforcement**
```
Event: Pre-push
Hook: Validate code standards
```

### Use Commands Instead When:

❌ **User Decision Required**
```
Better: /deploy command with user approval
Not: deploy-auto hook
```

❌ **Interactive Workflow**
```
Better: /research-topic with parameters
Not: auto-research hook
```

❌ **Rare Operations**
```
Better: /architecture-review when needed
Not: architecture-review hook on every change
```

### Use Agents Instead When:

❌ **Complex AI Processing**
```
Better: validation-gates agent via command
Not: Heavy AI processing in hook
```

❌ **Long-Running Tasks**
```
Better: research agent with progress
Not: Slow hook blocking workflow
```

### Decision Matrix

```
┌─────────────────────────────────────────┐
│        AUTOMATION DECISION TREE         │
├─────────────────────────────────────────┤
│                                         │
│  Needs to be automatic? ──NO──→ COMMAND│
│         │                               │
│        YES                              │
│         │                               │
│  Blocks operation? ──NO──→ POST-HOOK   │
│         │                               │
│        YES                              │
│         │                               │
│  Fast (<5s)? ──NO──→ ASYNC COMMAND     │
│         │                               │
│        YES                              │
│         │                               │
│      PRE-HOOK                           │
└─────────────────────────────────────────┘
```

---

## 🔄 Hook Execution Flow

### Lifecycle Overview

```
┌──────────────────────────────────────────┐
│         USER ACTION / EVENT              │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      CHECK IF HOOK CONFIGURED            │
│  (settings.local.json → hooks section)   │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│        HOOK ENABLED?                     │
│  ┌─NO──→ Skip hook, continue             │
│  └─YES──→ Continue                       │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      LOAD HOOK SCRIPT                    │
│  (JavaScript, Python, or Shell)          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      EXECUTE HOOK                        │
│  - Create context object                 │
│  - Set timeout timer                     │
│  - Run hook function                     │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      HOOK RETURNS RESULT                 │
│  { success: true/false, message: "..." } │
└──────────────┬───────────────────────────┘
               │
          ┌────┴────┐
          │         │
          ▼         ▼
    ┌─────────┐ ┌──────────┐
    │ SUCCESS │ │   FAIL   │
    └────┬────┘ └────┬─────┘
         │           │
         │           └──→ Block operation (pre-hooks)
         │               Log error (post-hooks)
         │
         └──→ Continue operation
```

### Execution Phases

**Phase 1: Discovery**
- Claude Code checks for hook configuration
- Validates hook file exists
- Checks if hook is enabled

**Phase 2: Preparation**
- Load hook script
- Create context object with utilities
- Set timeout limits

**Phase 3: Execution**
- Run hook function with context
- Monitor execution time
- Capture output and errors

**Phase 4: Result Processing**
- Parse return value
- For pre-hooks: Block or continue operation
- For post-hooks: Log results
- Update metrics

**Phase 5: Cleanup**
- Clear timeout
- Release resources
- Log completion

### Timing Diagram

```
Session Start Example:

T+0ms:   User starts Claude Code
T+100ms: session-start event triggered
T+150ms: Load session-start hook
T+200ms: Execute hook
T+250ms:   └─→ Check MCP servers
T+500ms:   └─→ Load project memory
T+750ms:   └─→ Validate environment
T+800ms: Hook completes (success)
T+850ms: Session ready
```

---

## 📚 Documentation Structure

### Complete Hook Documentation

```
hooks/
├── README.md                    ← You are here (1500 lines)
├── hook-architecture.md         ← Architecture & lifecycle (2000 lines)
├── session-hooks.md             ← Session lifecycle hooks (1500 lines)
├── git-hooks.md                 ← Git integration hooks (2000 lines)
├── creating-hooks.md            ← Build custom hooks (1500 lines)
└── hook-examples.md             ← Real-world examples (1500 lines)
```

### Documentation Guide

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **README.md** | Overview, quick start | First time, reference |
| **hook-architecture.md** | Deep technical details | Building complex hooks |
| **session-hooks.md** | Session management | Session automation |
| **git-hooks.md** | Git integration | Git workflow automation |
| **creating-hooks.md** | Hook development | Creating new hooks |
| **hook-examples.md** | Real examples | Learning by example |

### Learning Path

**Beginner** (1 hour):
1. Read this README
2. Try session-start example
3. Review session-hooks.md

**Intermediate** (2 hours):
1. Study hook-architecture.md
2. Implement pre-commit hook
3. Review git-hooks.md

**Advanced** (4 hours):
1. Read creating-hooks.md
2. Build custom hook
3. Study hook-examples.md

---

## ⚙️ Configuration

### Hook Configuration Structure

```json
{
  "hooks": {
    "hook-name": {
      "enabled": true,
      "file": ".claude/hooks/hook-name.js",
      "timeout": 30000,
      "async": false,
      "retries": 0,
      "continueOnError": false,
      "environment": {
        "KEY": "value"
      }
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | false | Enable/disable hook |
| `file` | string | required | Path to hook script |
| `timeout` | number | 30000 | Timeout in milliseconds |
| `async` | boolean | false | Run asynchronously |
| `retries` | number | 0 | Retry count on failure |
| `continueOnError` | boolean | false | Continue on error (post-hooks) |
| `environment` | object | {} | Environment variables |

### Example Configurations

**Minimal Configuration**:
```json
{
  "hooks": {
    "session-start": {
      "enabled": true,
      "file": ".claude/hooks/session-start.js"
    }
  }
}
```

**Full Configuration**:
```json
{
  "hooks": {
    "pre-commit": {
      "enabled": true,
      "file": ".claude/hooks/pre-commit.js",
      "timeout": 60000,
      "async": false,
      "retries": 1,
      "continueOnError": false,
      "environment": {
        "NODE_ENV": "test",
        "LINT_FIX": "true"
      }
    },
    "post-commit": {
      "enabled": true,
      "file": ".claude/hooks/post-commit.js",
      "timeout": 30000,
      "async": true,
      "continueOnError": true
    }
  }
}
```

**Conditional Enabling**:
```json
{
  "hooks": {
    "pre-commit": {
      "enabled": "${CI:false}",
      "file": ".claude/hooks/pre-commit.js"
    }
  }
}
```

### Global vs Local Hooks

**Local Hooks** (`.claude/hooks/`):
- Project-specific
- Version controlled
- Team-shared

**Global Hooks** (`~/.claude/hooks/`):
- Personal automation
- Not shared with team
- Lower priority

**Priority Order**:
1. Local project hooks (`.claude/hooks/`)
2. Global user hooks (`~/.claude/hooks/`)

---

## 💡 Best Practices

### Hook Design

✅ **DO**:
- Keep hooks fast (<5 seconds)
- Return meaningful results
- Handle errors gracefully
- Log progress clearly
- Make hooks idempotent
- Test thoroughly

❌ **DON'T**:
- Block for long operations
- Make external API calls without timeout
- Modify files unexpectedly
- Fail silently
- Assume dependencies exist
- Skip error handling

### Error Handling

✅ **DO**:
```javascript
try {
  const result = await riskyOperation();
  return { success: true, data: result };
} catch (error) {
  console.error('❌ Operation failed:', error.message);
  return {
    success: false,
    error: error.message,
    suggestion: 'Check network connection'
  };
}
```

❌ **DON'T**:
```javascript
// No error handling
const result = await riskyOperation();
return { success: true };
```

### Performance

✅ **DO**:
- Cache expensive operations
- Use async when appropriate
- Set reasonable timeouts
- Skip unnecessary work

❌ **DON'T**:
- Synchronously read large files
- Make unbounded loops
- Run expensive computations
- Block main thread unnecessarily

### Security

✅ **DO**:
- Validate all inputs
- Use environment variables for secrets
- Check file permissions
- Sanitize paths

❌ **DON'T**:
- Hardcode credentials
- Trust user input
- Execute arbitrary code
- Modify system files

### Testing

✅ **DO**:
```bash
# Test hook directly
node .claude/hooks/my-hook.js

# Test with context
claude test-hook session-start

# Validate configuration
claude validate-hooks
```

❌ **DON'T**:
- Deploy untested hooks
- Skip error scenarios
- Assume environment

---

## 🐛 Troubleshooting

### Common Issues

**Hook Not Executing**:

```bash
# Check configuration
cat .claude/settings.local.json | grep -A5 "hooks"

# Verify hook file exists
ls -la .claude/hooks/

# Check if enabled
# In settings.local.json: "enabled": true

# Check Claude Code logs
claude --debug
```

**Hook Timeout**:

```javascript
// Increase timeout in settings
{
  "hooks": {
    "my-hook": {
      "timeout": 60000  // 60 seconds
    }
  }
}

// Or make hook faster
// - Cache results
// - Skip unnecessary work
// - Use async operations
```

**Hook Failing**:

```bash
# Test hook in isolation
node .claude/hooks/my-hook.js

# Check dependencies
npm list

# Verify permissions
ls -la .claude/hooks/

# Check error logs
claude logs --hooks
```

**Hook Blocking Workflow**:

```json
// Make post-hook non-blocking
{
  "hooks": {
    "post-commit": {
      "async": true,
      "continueOnError": true
    }
  }
}
```

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export CLAUDE_DEBUG_HOOKS=true

# Run with debug flag
claude --debug-hooks

# View detailed logs
claude logs --level=debug
```

### Validation Commands

```bash
# Validate all hooks
claude validate-hooks

# Test specific hook
claude test-hook session-start

# Check hook syntax
claude check-hook-syntax .claude/hooks/my-hook.js

# List available hooks
claude list-hooks
```

### Getting Help

1. **Check Documentation**:
   - This README for overview
   - [hook-architecture.md](./hook-architecture.md) for technical details
   - [creating-hooks.md](./creating-hooks.md) for development guide

2. **Review Examples**:
   ```bash
   # View example hooks
   ls examples/hooks/

   # Read hook examples
   code hooks/hook-examples.md
   ```

3. **Test Incrementally**:
   ```bash
   # Start with simple hook
   # Add complexity gradually
   # Test each addition
   ```

4. **Use Debug Tools**:
   ```bash
   # Enable debug mode
   claude --debug-hooks

   # Check logs
   claude logs --hooks
   ```

---

## 🔗 Related Documentation

### Essential Reading

| Document | Purpose | Priority |
|----------|---------|----------|
| [Hook Architecture](./hook-architecture.md) | Technical deep dive | HIGH |
| [Session Hooks](./session-hooks.md) | Session management | HIGH |
| [Git Hooks](./git-hooks.md) | Git integration | HIGH |
| [Creating Hooks](./creating-hooks.md) | Build custom hooks | MEDIUM |
| [Hook Examples](./hook-examples.md) | Real-world examples | MEDIUM |

### Architecture Documentation

| Document | Purpose |
|----------|---------|
| [System Design](../architecture/system-design.md) | Overall architecture |
| [Data Flow](../architecture/data-flow.md) | How hooks fit in flow |
| [MCP Integration](../architecture/mcp-integration.md) | Using MCP in hooks |

### Related Components

| Component | Documentation |
|-----------|---------------|
| **Commands** | [commands/README.md](../commands/README.md) |
| **Agents** | [agents/README.md](../agents/README.md) |
| **Settings** | [settings/README.md](../settings/README.md) |

---

## 📊 Hook Catalog Quick Reference

### Session Hooks

| Hook | Trigger | Purpose | Blocking |
|------|---------|---------|----------|
| `session-start` | Session begins | Initialize context | No |
| `session-end` | Session ends | Save state | No |

### Git Hooks

| Hook | Trigger | Purpose | Blocking |
|------|---------|---------|----------|
| `pre-commit` | Before commit | Validate changes | Yes |
| `post-commit` | After commit | Extract patterns | No |
| `pre-push` | Before push | Final validation | Yes |

### Custom Hooks

| Hook | Trigger | Purpose | Blocking |
|------|---------|---------|----------|
| `file-change` | File modified | React to changes | No |
| `test-complete` | Tests finish | Process results | No |
| `deploy-start` | Before deploy | Validate deployment | Yes |

---

## 🎯 Quick Reference Cards

### Hook Types Card

```
┌──────────────────────────────────────┐
│     HOOK TYPES                       │
├──────────────────────────────────────┤
│ PRE-HOOKS     Block operations       │
│               Fast validation        │
│               Gate keeping           │
│                                      │
│ POST-HOOKS    Non-blocking          │
│               Async processing       │
│               Knowledge capture      │
│                                      │
│ ASYNC-HOOKS   Background tasks      │
│               Long running           │
│               Fire and forget        │
└──────────────────────────────────────┘
```

### Hook Context Card

```
┌──────────────────────────────────────┐
│     HOOK CONTEXT API                 │
├──────────────────────────────────────┤
│ context.read(path)                   │
│ context.write(path, content)         │
│ context.exists(path)                 │
│ context.exec(command)                │
│ context.loadMemory()                 │
│ context.saveMemory(data)             │
│ context.log(message)                 │
│ context.env                          │
└──────────────────────────────────────┘
```

### Performance Guidelines Card

```
┌──────────────────────────────────────┐
│     HOOK PERFORMANCE                 │
├──────────────────────────────────────┤
│ Target: < 5 seconds                  │
│ Timeout: 30 seconds default          │
│ Async: For slow operations           │
│ Cache: Expensive computations        │
│ Skip: Unnecessary work               │
└──────────────────────────────────────┘
```

---

## 📈 Hook Usage Patterns

### Common Patterns

**Session Initialization**:
```javascript
// session-start hook
module.exports = async (context) => {
  // 1. Check MCP servers
  await context.checkMCPHealth();

  // 2. Load project memory
  const memory = await context.loadMemory();

  // 3. Validate environment
  await context.validateEnvironment();

  // 4. Display welcome message
  context.log('✅ Session initialized');

  return { success: true };
};
```

**Git Validation**:
```javascript
// pre-commit hook
module.exports = async (context) => {
  // 1. Lint staged files
  const lintResult = await context.exec('npm run lint:staged');
  if (!lintResult.success) {
    return { success: false, error: 'Linting failed' };
  }

  // 2. Run tests
  const testResult = await context.exec('npm test');
  if (!testResult.success) {
    return { success: false, error: 'Tests failed' };
  }

  return { success: true };
};
```

**Knowledge Capture**:
```javascript
// post-commit hook
module.exports = async (context) => {
  // 1. Get commit info
  const commit = await context.getLastCommit();

  // 2. Extract patterns
  const patterns = await context.extractPatterns(commit.files);

  // 3. Update knowledge base
  await context.updateKnowledgeBase(patterns);

  // 4. Don't block on errors
  return { success: true };
};
```

---

## ✅ Hooks Documentation Checklist

- [x] Overview and introduction
- [x] Quick start guide
- [x] Hook categories (3 categories)
- [x] When to use hooks (vs commands/agents)
- [x] Hook execution flow diagram
- [x] Documentation structure
- [x] Configuration reference
- [x] Best practices
- [x] Troubleshooting guide
- [x] Related documentation
- [x] Hook catalog reference
- [x] Quick reference cards
- [x] Usage patterns

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: DevEx Team
**Status**: Active

### Change Log

- **2025-01-15**: Initial hooks documentation
  - Created comprehensive hooks hub
  - Documented all hook types
  - Added execution flow diagrams
  - Included usage patterns and best practices

---

**Navigate**: [← Back to Main](../README.md) | [Hook Architecture →](./hook-architecture.md) | [Session Hooks →](./session-hooks.md) | [Git Hooks →](./git-hooks.md)

---

*Built with ❤️ for developers who love automated workflows*
