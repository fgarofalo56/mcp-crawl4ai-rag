# 🎯 Session Lifecycle Hooks

> **Complete guide to session-start and session-end hooks**

This document covers session lifecycle hooks that manage Claude Code session initialization, context loading, cleanup, and state management.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Session Start Hooks](#-session-start-hooks)
- [Session End Hooks](#-session-end-hooks)
- [Common Patterns](#-common-patterns)
- [Configuration Examples](#-configuration-examples)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)
- [Real-World Examples](#-real-world-examples)

---

## 🎯 Overview

### What are Session Hooks?

Session hooks manage the lifecycle of Claude Code sessions:

**session-start**: Triggered when Claude Code starts
- Load project context
- Check environment health
- Initialize services
- Load persistent memory
- Set up session state

**session-end**: Triggered when Claude Code exits
- Save session state
- Generate work summary
- Update knowledge base
- Clean up resources
- Archive session data

### Session Lifecycle

```
User Starts Claude Code
      │
      ▼
┌─────────────────────┐
│  session-start      │
│  - Health checks    │
│  - Load context     │
│  - Initialize state │
└─────────┬───────────┘
          │
          ▼
    Work Session
    (commands, agents, etc.)
          │
          ▼
User Exits Claude Code
      │
      ▼
┌─────────────────────┐
│  session-end        │
│  - Save state       │
│  - Generate summary │
│  - Update KB        │
└─────────────────────┘
```

---

## 🚀 Session Start Hooks

### Purpose

Session-start hooks prepare the environment for productive work by:
- Validating system health
- Loading project context
- Checking dependencies
- Initializing services
- Restoring previous state

### Common session-start Hooks

#### 1. MCP Health Check

**Purpose**: Ensure all MCP servers are responsive

```javascript
// .claude/hooks/mcp-health-check.js
module.exports = async function(context) {
  context.log('🏥 Checking MCP server health...');

  const servers = [
    'microsoft-docs',
    'serena',
    'playwright',
    'azure-mcp',
    'memory',
    'filesearch',
    'kb',
    'gitingest',
    'linear'
  ];

  const results = await Promise.all(
    servers.map(async (server) => {
      try {
        const result = await context.callMCP(server, 'health', {});
        return { server, status: 'healthy', ...result };
      } catch (error) {
        return { server, status: 'unhealthy', error: error.message };
      }
    })
  );

  // Log results
  const healthy = results.filter(r => r.status === 'healthy');
  const unhealthy = results.filter(r => r.status === 'unhealthy');

  context.log(`✅ ${healthy.length}/${servers.length} MCP servers healthy`);

  if (unhealthy.length > 0) {
    context.warn('⚠️  Unhealthy MCP servers:');
    unhealthy.forEach(r => {
      context.warn(`   - ${r.server}: ${r.error}`);
    });
  }

  return {
    success: unhealthy.length === 0,
    healthy: healthy.map(r => r.server),
    unhealthy: unhealthy.map(r => r.server)
  };
};
```

**Configuration**:
```json
{
  "hooks": {
    "session-start-mcp": {
      "enabled": true,
      "file": ".claude/hooks/mcp-health-check.js",
      "timeout": 10000,
      "continueOnError": true
    }
  }
}
```

#### 2. Environment Validator

**Purpose**: Validate development environment setup

```javascript
// .claude/hooks/environment-validator.js
module.exports = async function(context) {
  context.log('🔍 Validating environment...');

  const checks = [];

  // Check Node.js
  try {
    const nodeVersion = await context.exec('node --version');
    checks.push({
      name: 'Node.js',
      status: 'pass',
      version: nodeVersion.stdout.trim()
    });
  } catch (error) {
    checks.push({
      name: 'Node.js',
      status: 'fail',
      error: 'Node.js not found'
    });
  }

  // Check npm
  try {
    const npmVersion = await context.exec('npm --version');
    checks.push({
      name: 'npm',
      status: 'pass',
      version: npmVersion.stdout.trim()
    });
  } catch (error) {
    checks.push({
      name: 'npm',
      status: 'fail',
      error: 'npm not found'
    });
  }

  // Check git
  try {
    const gitVersion = await context.exec('git --version');
    checks.push({
      name: 'git',
      status: 'pass',
      version: gitVersion.stdout.trim()
    });
  } catch (error) {
    checks.push({
      name: 'git',
      status: 'fail',
      error: 'git not found'
    });
  }

  // Check project dependencies
  if (await context.exists('package.json')) {
    if (await context.exists('node_modules')) {
      checks.push({
        name: 'Dependencies',
        status: 'pass',
        message: 'node_modules exists'
      });
    } else {
      checks.push({
        name: 'Dependencies',
        status: 'warn',
        message: 'Run npm install'
      });
    }
  }

  // Check .env file
  if (await context.exists('.env')) {
    checks.push({
      name: 'Environment',
      status: 'pass',
      message: '.env file found'
    });
  } else {
    checks.push({
      name: 'Environment',
      status: 'warn',
      message: '.env file missing'
    });
  }

  // Log results
  const passed = checks.filter(c => c.status === 'pass');
  const failed = checks.filter(c => c.status === 'fail');
  const warnings = checks.filter(c => c.status === 'warn');

  context.log(`✅ ${passed.length} checks passed`);

  if (warnings.length > 0) {
    context.warn(`⚠️  ${warnings.length} warnings:`);
    warnings.forEach(c => {
      context.warn(`   - ${c.name}: ${c.message}`);
    });
  }

  if (failed.length > 0) {
    context.error(`❌ ${failed.length} checks failed:`);
    failed.forEach(c => {
      context.error(`   - ${c.name}: ${c.error}`);
    });
  }

  return {
    success: failed.length === 0,
    checks,
    passed: passed.length,
    failed: failed.length,
    warnings: warnings.length
  };
};
```

#### 3. Session Context Loader

**Purpose**: Load project context and memory

```javascript
// .claude/hooks/session-context-loader.js
module.exports = async function(context) {
  context.log('📚 Loading session context...');

  const sessionData = {};

  // Load project memory
  try {
    const memory = await context.loadMemory();
    sessionData.memory = memory;
    context.log(`  Loaded ${Object.keys(memory).length} memory entries`);
  } catch (error) {
    context.warn('  No existing memory found');
    sessionData.memory = {};
  }

  // Get project info
  if (await context.exists('package.json')) {
    const packageJson = JSON.parse(
      await context.read('package.json')
    );
    sessionData.projectName = packageJson.name;
    sessionData.projectVersion = packageJson.version;
    context.log(`  Project: ${packageJson.name} v${packageJson.version}`);
  }

  // Get git info
  try {
    const branch = await context.exec('git branch --show-current');
    const commit = await context.exec('git rev-parse --short HEAD');

    sessionData.git = {
      branch: branch.stdout.trim(),
      commit: commit.stdout.trim()
    };

    context.log(`  Git: ${sessionData.git.branch} @ ${sessionData.git.commit}`);
  } catch (error) {
    context.warn('  Not a git repository');
  }

  // Load knowledge base stats
  try {
    const kbStats = await context.callMCP('kb', 'stats', {});
    sessionData.knowledgeBase = kbStats;
    context.log(`  Knowledge Base: ${kbStats.entries} entries`);
  } catch (error) {
    context.warn('  Knowledge Base unavailable');
  }

  // Update session count
  const sessionCount = (sessionData.memory.sessionCount || 0) + 1;
  sessionData.memory.sessionCount = sessionCount;
  sessionData.memory.lastSession = new Date().toISOString();

  await context.saveMemory(sessionData.memory);

  context.log(`✅ Session #${sessionCount} initialized`);

  return {
    success: true,
    sessionData
  };
};
```

#### 4. Primer Auto-Run

**Purpose**: Automatically run /primer command

```javascript
// .claude/hooks/primer-auto.js
module.exports = async function(context) {
  // Check if auto-primer is enabled
  const memory = await context.loadMemory();

  if (memory.autoPrimer === false) {
    context.log('⏭️  Auto-primer disabled');
    return { success: true, skipped: true };
  }

  context.log('🎯 Running auto-primer...');

  try {
    // Run primer command
    const result = await context.exec('claude-primer');

    if (result.success) {
      context.log('✅ Primer completed');
      return { success: true };
    } else {
      context.warn('⚠️  Primer failed');
      return { success: false, error: result.stderr };
    }
  } catch (error) {
    context.warn(`⚠️  Primer error: ${error.message}`);
    return { success: false, error: error.message };
  }
};
```

---

## 🛑 Session End Hooks

### Purpose

Session-end hooks capture session outcomes and prepare for next session:
- Save work state
- Generate summaries
- Update knowledge base
- Archive session data
- Clean up temporary files

### Common session-end Hooks

#### 1. Memory Store

**Purpose**: Save session state and learnings

```javascript
// .claude/hooks/memory-store.js
module.exports = async function(context) {
  context.log('💾 Saving session memory...');

  const memory = await context.loadMemory();

  // Update session info
  memory.lastSessionEnd = new Date().toISOString();
  memory.totalSessions = (memory.totalSessions || 0) + 1;

  // Capture session metrics
  const sessionMetrics = {
    duration: context.event.duration,
    commandsExecuted: context.event.commandsExecuted || 0,
    filesModified: context.event.filesModified || 0,
    timestamp: new Date().toISOString()
  };

  if (!memory.sessionHistory) {
    memory.sessionHistory = [];
  }

  memory.sessionHistory.push(sessionMetrics);

  // Keep only last 10 sessions
  if (memory.sessionHistory.length > 10) {
    memory.sessionHistory = memory.sessionHistory.slice(-10);
  }

  await context.saveMemory(memory);

  context.log('✅ Memory saved');

  return {
    success: true,
    sessionsSaved: memory.sessionHistory.length
  };
};
```

#### 2. Work Summary Generator

**Purpose**: Generate summary of session work

```javascript
// .claude/hooks/work-summary.js
module.exports = async function(context) {
  context.log('📝 Generating work summary...');

  const summary = {
    timestamp: new Date().toISOString(),
    duration: context.event.duration,
    changes: {}
  };

  // Get git changes
  try {
    const status = await context.exec('git status --short');
    const lines = status.stdout.split('\n').filter(l => l.trim());

    summary.changes = {
      modified: lines.filter(l => l.startsWith(' M')).length,
      added: lines.filter(l => l.startsWith('A ')).length,
      deleted: lines.filter(l => l.startsWith(' D')).length,
      untracked: lines.filter(l => l.startsWith('??')).length
    };
  } catch (error) {
    context.warn('Could not get git status');
  }

  // Get commits made this session
  try {
    const commits = await context.exec(
      `git log --since="${context.event.startTime}" --oneline`
    );
    summary.commits = commits.stdout.split('\n').filter(l => l.trim()).length;
  } catch (error) {
    summary.commits = 0;
  }

  // Generate summary text
  const summaryText = `
Session Summary
===============
Duration: ${Math.round(summary.duration / 1000 / 60)} minutes
Commits: ${summary.commits}
Files Modified: ${summary.changes.modified || 0}
Files Added: ${summary.changes.added || 0}
Files Deleted: ${summary.changes.deleted || 0}
Untracked: ${summary.changes.untracked || 0}
  `.trim();

  context.log('\n' + summaryText);

  // Save summary to file
  const summaryPath = '.claude/session-summary.txt';
  await context.write(summaryPath, summaryText);

  return {
    success: true,
    summary
  };
};
```

#### 3. Knowledge Base Update

**Purpose**: Extract patterns and update KB

```javascript
// .claude/hooks/kb-update.js
module.exports = async function(context) {
  context.log('🧠 Updating knowledge base...');

  // Get files modified this session
  const modifiedFiles = context.event.filesModified || [];

  if (modifiedFiles.length === 0) {
    context.log('  No files to process');
    return { success: true, skipped: true };
  }

  context.log(`  Processing ${modifiedFiles.length} files...`);

  const patterns = [];

  for (const file of modifiedFiles) {
    try {
      // Extract patterns from file
      const content = await context.read(file);
      const filePatterns = await extractPatterns(content, file);
      patterns.push(...filePatterns);
    } catch (error) {
      context.warn(`  Could not process ${file}`);
    }
  }

  if (patterns.length > 0) {
    // Add to knowledge base
    try {
      await context.callMCP('kb', 'add-batch', { patterns });
      context.log(`✅ Added ${patterns.length} patterns to KB`);
    } catch (error) {
      context.warn('  Could not update KB');
    }
  }

  return {
    success: true,
    patternsExtracted: patterns.length
  };
};

function extractPatterns(content, file) {
  const patterns = [];

  // Extract imports
  const imports = content.match(/^import .+ from .+$/gm) || [];
  if (imports.length > 0) {
    patterns.push({
      type: 'import',
      file,
      patterns: imports
    });
  }

  // Extract function definitions
  const functions = content.match(/^(async )?function \w+/gm) || [];
  if (functions.length > 0) {
    patterns.push({
      type: 'function',
      file,
      patterns: functions
    });
  }

  // Extract classes
  const classes = content.match(/^class \w+/gm) || [];
  if (classes.length > 0) {
    patterns.push({
      type: 'class',
      file,
      patterns: classes
    });
  }

  return patterns;
}
```

#### 4. Context Save

**Purpose**: Save project context for next session

```javascript
// .claude/hooks/context-save.js
module.exports = async function(context) {
  context.log('💼 Saving context for next session...');

  const contextData = {
    timestamp: new Date().toISOString(),
    project: {},
    state: {}
  };

  // Save project state
  if (await context.exists('package.json')) {
    const pkg = JSON.parse(await context.read('package.json'));
    contextData.project = {
      name: pkg.name,
      version: pkg.version,
      dependencies: Object.keys(pkg.dependencies || {})
    };
  }

  // Save git state
  try {
    const branch = await context.exec('git branch --show-current');
    const status = await context.exec('git status --short');

    contextData.git = {
      branch: branch.stdout.trim(),
      hasChanges: status.stdout.trim().length > 0
    };
  } catch (error) {
    // Not a git repo
  }

  // Save current directory
  contextData.state.workingDirectory = context.projectRoot;

  // Save to context file
  const contextPath = '.claude/context.json';
  await context.write(
    contextPath,
    JSON.stringify(contextData, null, 2)
  );

  context.log('✅ Context saved');

  return { success: true };
};
```

---

## 🎨 Common Patterns

### Multi-Step Initialization

```javascript
// session-start with multiple steps
module.exports = async function(context) {
  context.log('🚀 Initializing session...');

  // Step 1: Health checks
  context.log('1️⃣ Health checks...');
  const healthResult = await performHealthChecks(context);
  if (!healthResult.success) {
    return healthResult;
  }

  // Step 2: Load context
  context.log('2️⃣ Loading context...');
  const contextResult = await loadContext(context);

  // Step 3: Initialize services
  context.log('3️⃣ Initializing services...');
  const servicesResult = await initializeServices(context);

  context.log('✅ Session ready!');

  return { success: true };
};
```

### Conditional Execution

```javascript
// Only run in certain environments
module.exports = async function(context) {
  const env = context.env.NODE_ENV;

  if (env === 'production') {
    context.log('⏭️  Skipping in production');
    return { success: true, skipped: true };
  }

  return await performDevChecks(context);
};
```

### Error Recovery

```javascript
// Graceful degradation
module.exports = async function(context) {
  try {
    return await primaryOperation(context);
  } catch (error) {
    context.warn('Primary operation failed, trying fallback');

    try {
      return await fallbackOperation(context);
    } catch (fallbackError) {
      // Both failed, but don't block session
      context.error('All operations failed');
      return {
        success: true,  // Don't block session start
        warning: 'Some features may be unavailable'
      };
    }
  }
};
```

---

## ⚙️ Configuration Examples

### Minimal Configuration

```json
{
  "hooks": {
    "session-start": {
      "enabled": true,
      "file": ".claude/hooks/session-start.js"
    },
    "session-end": {
      "enabled": true,
      "file": ".claude/hooks/session-end.js"
    }
  }
}
```

### Comprehensive Configuration

```json
{
  "hooks": {
    "session-start-health": {
      "enabled": true,
      "file": ".claude/hooks/mcp-health-check.js",
      "timeout": 10000,
      "continueOnError": true,
      "priority": 100
    },
    "session-start-env": {
      "enabled": true,
      "file": ".claude/hooks/environment-validator.js",
      "timeout": 5000,
      "continueOnError": true,
      "priority": 90
    },
    "session-start-context": {
      "enabled": true,
      "file": ".claude/hooks/session-context-loader.js",
      "timeout": 10000,
      "priority": 80
    },
    "session-start-primer": {
      "enabled": "${AUTO_PRIMER:false}",
      "file": ".claude/hooks/primer-auto.js",
      "timeout": 30000,
      "continueOnError": true,
      "priority": 70
    },
    "session-end-memory": {
      "enabled": true,
      "file": ".claude/hooks/memory-store.js",
      "timeout": 5000,
      "async": true,
      "priority": 100
    },
    "session-end-summary": {
      "enabled": true,
      "file": ".claude/hooks/work-summary.js",
      "timeout": 10000,
      "async": true,
      "priority": 90
    },
    "session-end-kb": {
      "enabled": true,
      "file": ".claude/hooks/kb-update.js",
      "timeout": 30000,
      "async": true,
      "continueOnError": true,
      "priority": 80
    },
    "session-end-context": {
      "enabled": true,
      "file": ".claude/hooks/context-save.js",
      "timeout": 5000,
      "priority": 70
    }
  }
}
```

---

## 💡 Best Practices

### Session Start Hooks

✅ **DO**:
- Keep fast (<10 seconds total)
- Continue on errors (don't block session)
- Log progress clearly
- Load context incrementally
- Cache expensive operations
- Validate before proceeding

❌ **DON'T**:
- Block session start on non-critical checks
- Make external API calls without timeout
- Perform expensive computations
- Require user interaction
- Assume dependencies exist
- Fail silently

### Session End Hooks

✅ **DO**:
- Run asynchronously when possible
- Save important state
- Generate useful summaries
- Clean up temporary files
- Update knowledge base
- Handle errors gracefully

❌ **DON'T**:
- Block session end
- Lose unsaved data
- Skip error handling
- Make long network calls
- Require user input
- Forget to cleanup

### Performance

✅ **DO**:
```javascript
// Run checks in parallel
const [health, env, context] = await Promise.all([
  checkHealth(context),
  validateEnv(context),
  loadContext(context)
]);
```

❌ **DON'T**:
```javascript
// Run checks sequentially (slow)
const health = await checkHealth(context);
const env = await validateEnv(context);
const context = await loadContext(context);
```

---

## 🐛 Troubleshooting

### Session Start Issues

**Hook Not Running**:
```bash
# Check configuration
cat .claude/settings.local.json | grep -A5 "session-start"

# Verify file exists
ls -la .claude/hooks/session-start.js

# Check if enabled
# "enabled": true in config
```

**Slow Session Start**:
```javascript
// Add timing logs
module.exports = async function(context) {
  const start = Date.now();

  await operation1(context);
  context.log(`Operation 1: ${Date.now() - start}ms`);

  await operation2(context);
  context.log(`Operation 2: ${Date.now() - start}ms`);
};
```

**Hook Failing**:
```bash
# Test hook directly
node .claude/hooks/session-start.js

# Enable debug logging
export CLAUDE_DEBUG_HOOKS=true
claude
```

### Session End Issues

**Data Not Saved**:
```javascript
// Ensure synchronous save for critical data
module.exports = async function(context) {
  await context.saveMemory(data);  // Wait for save
  return { success: true };
};
```

**Hook Timeout**:
```json
{
  "hooks": {
    "session-end": {
      "timeout": 60000  // Increase timeout
    }
  }
}
```

---

## 🌟 Real-World Examples

### Complete Session Start Hook

```javascript
// .claude/hooks/session-start-complete.js
module.exports = async function(context) {
  context.log('🚀 Initializing Claude Code session...\n');

  const results = {
    health: null,
    environment: null,
    context: null
  };

  // 1. MCP Health Check
  context.log('1️⃣ Checking MCP servers...');
  try {
    results.health = await checkMCPHealth(context);
    context.log(`   ✅ ${results.health.healthy} servers healthy\n`);
  } catch (error) {
    context.warn('   ⚠️  Health check failed\n');
  }

  // 2. Environment Validation
  context.log('2️⃣ Validating environment...');
  try {
    results.environment = await validateEnvironment(context);
    context.log(`   ✅ ${results.environment.passed} checks passed\n`);
  } catch (error) {
    context.warn('   ⚠️  Environment validation failed\n');
  }

  // 3. Load Context
  context.log('3️⃣ Loading project context...');
  try {
    results.context = await loadProjectContext(context);
    context.log(`   ✅ Context loaded\n`);
  } catch (error) {
    context.warn('   ⚠️  Context loading failed\n');
  }

  // 4. Display Welcome
  displayWelcome(context, results);

  return { success: true, results };
};

async function checkMCPHealth(context) {
  const servers = ['microsoft-docs', 'serena', 'kb'];
  const results = await Promise.all(
    servers.map(async (s) => {
      try {
        await context.callMCP(s, 'health', {});
        return { server: s, status: 'healthy' };
      } catch {
        return { server: s, status: 'unhealthy' };
      }
    })
  );

  return {
    healthy: results.filter(r => r.status === 'healthy').length,
    total: servers.length,
    results
  };
}

async function validateEnvironment(context) {
  const checks = [
    { name: 'Node.js', cmd: 'node --version' },
    { name: 'npm', cmd: 'npm --version' },
    { name: 'git', cmd: 'git --version' }
  ];

  const results = await Promise.all(
    checks.map(async (check) => {
      try {
        await context.exec(check.cmd);
        return { ...check, status: 'pass' };
      } catch {
        return { ...check, status: 'fail' };
      }
    })
  );

  return {
    passed: results.filter(r => r.status === 'pass').length,
    total: checks.length,
    results
  };
}

async function loadProjectContext(context) {
  const memory = await context.loadMemory();
  const sessionCount = (memory.sessionCount || 0) + 1;

  memory.sessionCount = sessionCount;
  memory.lastSession = new Date().toISOString();

  await context.saveMemory(memory);

  return { sessionCount, memory };
}

function displayWelcome(context, results) {
  const sessionNum = results.context?.sessionCount || 1;

  context.log('═══════════════════════════════════════════');
  context.log('  🎉 Claude Code Ready!');
  context.log(`  📊 Session #${sessionNum}`);
  context.log('═══════════════════════════════════════════\n');

  context.log('Available commands:');
  context.log('  /primer - Load project context');
  context.log('  /task-next - Get next task');
  context.log('  /help - Show all commands\n');
}
```

### Complete Session End Hook

```javascript
// .claude/hooks/session-end-complete.js
module.exports = async function(context) {
  context.log('\n💤 Ending session...\n');

  // 1. Generate summary
  context.log('1️⃣ Generating work summary...');
  const summary = await generateSummary(context);
  context.log(summary.text);

  // 2. Save memory
  context.log('2️⃣ Saving memory...');
  await saveSessionMemory(context, summary);
  context.log('   ✅ Memory saved\n');

  // 3. Update KB (async)
  context.log('3️⃣ Updating knowledge base...');
  updateKnowledgeBase(context).catch(err => {
    context.warn(`   ⚠️  KB update failed: ${err.message}`);
  });

  context.log('👋 Goodbye!\n');

  return { success: true };
};

async function generateSummary(context) {
  const duration = context.event.duration || 0;
  const minutes = Math.round(duration / 1000 / 60);

  let commits = 0;
  let filesChanged = 0;

  try {
    const commitLog = await context.exec(
      `git log --since="${context.event.startTime}" --oneline`
    );
    commits = commitLog.stdout.split('\n').filter(l => l.trim()).length;

    const status = await context.exec('git status --short');
    filesChanged = status.stdout.split('\n').filter(l => l.trim()).length;
  } catch (error) {
    // Not a git repo or no changes
  }

  const text = `
   ╔══════════════════════════════════╗
   ║      Session Summary            ║
   ╠══════════════════════════════════╣
   ║ Duration: ${minutes} minutes
   ║ Commits:  ${commits}
   ║ Changes:  ${filesChanged} files
   ╚══════════════════════════════════╝
  `.trim();

  return { duration, commits, filesChanged, text };
}

async function saveSessionMemory(context, summary) {
  const memory = await context.loadMemory();

  if (!memory.sessions) {
    memory.sessions = [];
  }

  memory.sessions.push({
    timestamp: new Date().toISOString(),
    duration: summary.duration,
    commits: summary.commits,
    filesChanged: summary.filesChanged
  });

  // Keep last 10 sessions
  if (memory.sessions.length > 10) {
    memory.sessions = memory.sessions.slice(-10);
  }

  await context.saveMemory(memory);
}

async function updateKnowledgeBase(context) {
  // This runs async, doesn't block session end
  await new Promise(resolve => setTimeout(resolve, 100));
  // ... KB update logic
}
```

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: DevEx Team
**Status**: Active

---

**Navigate**: [← Back to Hooks](./README.md) | [Hook Architecture →](./hook-architecture.md) | [Git Hooks →](./git-hooks.md) | [Creating Hooks →](./creating-hooks.md)

---

*Built with ❤️ for developers who love seamless session management*
