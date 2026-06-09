# 🏗️ Hook Architecture

> **Deep technical documentation for Claude Code hooks system**

This document provides comprehensive technical details about the hooks architecture, including execution lifecycle, event system, configuration, error handling, and performance considerations.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Hook System Architecture](#-hook-system-architecture)
- [Execution Lifecycle](#-execution-lifecycle)
- [Event System](#-event-system)
- [Hook Configuration](#-hook-configuration)
- [Context API](#-context-api)
- [Error Handling](#-error-handling)
- [Performance Considerations](#-performance-considerations)
- [Hook Chaining](#-hook-chaining)
- [Parallel vs Sequential Execution](#-parallel-vs-sequential-execution)
- [Hook Discovery](#-hook-discovery)
- [Security Model](#-security-model)
- [Testing Framework](#-testing-framework)
- [Advanced Patterns](#-advanced-patterns)

---

## 🎯 Overview

### Architecture Goals

The hooks system is designed to provide:

1. **Reliability** - Hooks must not break core workflows
2. **Performance** - Fast execution (<5 seconds typical)
3. **Flexibility** - Support multiple languages and patterns
4. **Safety** - Fail-safe defaults and error isolation
5. **Extensibility** - Easy to add new hook types
6. **Debuggability** - Clear logging and error messages

### Design Principles

**Principle 1: Fail-Safe Defaults**
```
Hook failure → Log error → Continue (post-hooks)
Hook failure → Log error → Block (pre-hooks)
Missing hook → Skip silently
```

**Principle 2: Explicit Configuration**
```
All hooks must be explicitly enabled
No auto-discovery without configuration
Clear timeout and retry policies
```

**Principle 3: Context Isolation**
```
Each hook gets isolated context
No shared state between hooks
Clean environment per execution
```

**Principle 4: Observable Execution**
```
Every hook logs start/end
Metrics collected for performance
Errors captured with stack traces
```

---

## 🏛️ Hook System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────┐
│                  CLAUDE CODE CORE                      │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │           EVENT BUS                          │    │
│  │  - Session events                            │    │
│  │  - Git events                                │    │
│  │  - Custom events                             │    │
│  └──────────┬───────────────────────────────────┘    │
│             │                                         │
│             ▼                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │       HOOK MANAGER                           │    │
│  │  - Hook discovery                            │    │
│  │  - Configuration loading                     │    │
│  │  - Execution orchestration                   │    │
│  │  - Error handling                            │    │
│  └──────────┬───────────────────────────────────┘    │
│             │                                         │
│             ▼                                         │
│  ┌──────────────────────────────────────────────┐    │
│  │       HOOK EXECUTOR                          │    │
│  │  - Script loading                            │    │
│  │  - Context creation                          │    │
│  │  - Timeout management                        │    │
│  │  - Result processing                         │    │
│  └──────────┬───────────────────────────────────┘    │
└─────────────┼────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   HOOK SCRIPTS      │
    │  - JavaScript       │
    │  - Python           │
    │  - Shell            │
    └─────────────────────┘
```

### Component Responsibilities

**Event Bus**:
- Emit events for hook triggers
- Maintain event queue
- Handle event subscription
- Support custom events

**Hook Manager**:
- Discover available hooks
- Load configuration
- Determine which hooks to run
- Orchestrate execution
- Aggregate results

**Hook Executor**:
- Load and validate hook scripts
- Create execution context
- Set timeout timers
- Execute hook code
- Capture results and errors
- Clean up resources

**Hook Scripts**:
- User-defined automation logic
- Receive context object
- Return result object
- Handle specific event types

---

## 🔄 Execution Lifecycle

### Complete Lifecycle Diagram

```
┌─────────────────────────────────────────────────────┐
│                    EVENT OCCURS                     │
│     (session-start, pre-commit, etc.)               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              HOOK MANAGER NOTIFIED                  │
│  - Event type identified                            │
│  - Timestamp recorded                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         LOAD HOOK CONFIGURATION                     │
│  - Read settings.local.json                         │
│  - Find hooks for event type                        │
│  - Check if enabled                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ├──[No hooks]──→ Continue
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         VALIDATE HOOK FILES                         │
│  - Check file exists                                │
│  - Verify permissions                               │
│  - Validate syntax (optional)                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ├──[Invalid]──→ Log error → Continue/Block
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         LOAD HOOK SCRIPT                            │
│  - Determine language (JS/Python/Shell)             │
│  - Load interpreter                                 │
│  - Import/require hook module                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ├──[Load error]──→ Log error → Continue/Block
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         CREATE EXECUTION CONTEXT                    │
│  - Build context object                             │
│  - Attach utilities (read, write, exec, etc.)       │
│  - Set environment variables                        │
│  - Prepare workspace                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         START TIMEOUT TIMER                         │
│  - Default: 30 seconds                              │
│  - Configurable per hook                            │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         EXECUTE HOOK FUNCTION                       │
│  - Call hook with context                           │
│  - Monitor execution                                │
│  - Capture output                                   │
└──────────────────┬──────────────────────────────────┘
                   │
            ┌──────┴──────┐
            │             │
            ▼             ▼
    ┌───────────┐  ┌──────────┐
    │ COMPLETES │  │ TIMEOUT  │
    │ IN TIME   │  │ EXCEEDED │
    └─────┬─────┘  └────┬─────┘
          │             │
          │             └──→ Kill process
          │                  Return timeout error
          ▼
┌─────────────────────────────────────────────────────┐
│         PROCESS HOOK RESULT                         │
│  - Parse return value                               │
│  - Validate result structure                        │
│  - Extract success/error/message                    │
└──────────────────┬──────────────────────────────────┘
                   │
            ┌──────┴──────┐
            │             │
            ▼             ▼
    ┌────────────┐  ┌──────────┐
    │  SUCCESS   │  │  FAILURE │
    └──────┬─────┘  └────┬─────┘
           │             │
           │             ▼
           │    ┌────────────────────┐
           │    │  LOG ERROR         │
           │    │  - Stack trace     │
           │    │  - Context dump    │
           │    │  - Suggestions     │
           │    └────────┬───────────┘
           │             │
           │      ┌──────┴───────┐
           │      │              │
           │      ▼              ▼
           │  ┌─────────┐  ┌──────────┐
           │  │PRE-HOOK │  │POST-HOOK │
           │  │  BLOCK  │  │ CONTINUE │
           │  └────┬────┘  └────┬─────┘
           │       │            │
           ▼       ▼            ▼
┌─────────────────────────────────────────────────────┐
│         CLEANUP                                     │
│  - Clear timeout                                    │
│  - Release resources                                │
│  - Update metrics                                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         RETURN CONTROL                              │
│  - Continue operation (success/post-hook)           │
│  - Block operation (pre-hook failure)               │
└─────────────────────────────────────────────────────┘
```

### Lifecycle Phases

**Phase 1: Event Detection** (1-5ms)
- Event occurs in system
- Event bus receives notification
- Event type and metadata captured

**Phase 2: Hook Discovery** (5-10ms)
- Load settings.local.json
- Find hooks for event type
- Check enabled status
- Validate configuration

**Phase 3: Preparation** (10-50ms)
- Validate hook files exist
- Check file permissions
- Load hook scripts
- Parse and validate syntax

**Phase 4: Context Creation** (50-100ms)
- Build context object
- Attach utility functions
- Set environment variables
- Initialize workspace

**Phase 5: Execution** (100ms-30s)
- Start timeout timer
- Call hook function
- Monitor execution
- Capture output

**Phase 6: Result Processing** (10-50ms)
- Parse return value
- Validate result structure
- Log success/errors
- Determine next action

**Phase 7: Cleanup** (5-20ms)
- Clear timeout timer
- Release resources
- Update metrics
- Free memory

---

## 🎪 Event System

### Event Types

**Session Events**:
```javascript
{
  type: 'session-start',
  timestamp: '2025-01-15T10:30:00Z',
  sessionId: 'abc123',
  project: '/path/to/project'
}

{
  type: 'session-end',
  timestamp: '2025-01-15T12:30:00Z',
  sessionId: 'abc123',
  duration: 7200000  // ms
}
```

**Git Events**:
```javascript
{
  type: 'pre-commit',
  timestamp: '2025-01-15T11:00:00Z',
  files: ['src/index.js', 'src/utils.js'],
  stagedChanges: 150
}

{
  type: 'post-commit',
  timestamp: '2025-01-15T11:00:30Z',
  commitHash: 'abc123def',
  message: 'Add new feature',
  files: ['src/index.js']
}

{
  type: 'pre-push',
  timestamp: '2025-01-15T11:05:00Z',
  branch: 'main',
  commits: ['abc123', 'def456'],
  remote: 'origin'
}
```

**Custom Events**:
```javascript
{
  type: 'file-change',
  timestamp: '2025-01-15T11:15:00Z',
  file: 'src/config.json',
  changeType: 'modified'
}

{
  type: 'test-complete',
  timestamp: '2025-01-15T11:20:00Z',
  passed: 45,
  failed: 2,
  duration: 5000  // ms
}
```

### Event Bus Implementation

```javascript
class EventBus {
  constructor() {
    this.listeners = new Map();
    this.eventQueue = [];
  }

  // Register hook for event
  on(eventType, hookConfig) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(hookConfig);
  }

  // Emit event
  async emit(eventType, eventData) {
    const hooks = this.listeners.get(eventType) || [];

    // Execute all hooks for this event
    for (const hook of hooks) {
      if (hook.enabled) {
        await this.executeHook(hook, eventData);
      }
    }
  }

  // Execute single hook
  async executeHook(hook, eventData) {
    const executor = new HookExecutor(hook);
    const result = await executor.execute(eventData);
    return result;
  }
}
```

### Event Propagation

```
Event Triggered
      │
      ▼
Event Bus Receives Event
      │
      ├──→ Hook 1 (if enabled)
      │       │
      │       └──→ Success/Failure
      │
      ├──→ Hook 2 (if enabled)
      │       │
      │       └──→ Success/Failure
      │
      └──→ Hook N (if enabled)
              │
              └──→ Success/Failure
```

**Sequential Execution** (default):
```javascript
for (const hook of hooks) {
  await executeHook(hook);  // Wait for each
}
```

**Parallel Execution** (optional):
```javascript
await Promise.all(
  hooks.map(hook => executeHook(hook))
);
```

---

## ⚙️ Hook Configuration

### Configuration Schema

```typescript
interface HookConfig {
  enabled: boolean;              // Enable/disable hook
  file: string;                  // Path to hook script
  timeout?: number;              // Timeout in ms (default: 30000)
  async?: boolean;               // Run asynchronously (default: false)
  retries?: number;              // Retry count on failure (default: 0)
  continueOnError?: boolean;     // Continue on error (default: false)
  environment?: Record<string, string>;  // Environment variables
  priority?: number;             // Execution priority (default: 0)
  conditions?: HookConditions;   // Conditional execution
}

interface HookConditions {
  files?: string[];              // Only run for these files
  branches?: string[];           // Only run on these branches
  environment?: string;          // Only run in this environment
  skipIf?: string;               // Skip if condition true
}
```

### Configuration Loading

```javascript
class ConfigLoader {
  loadHookConfig(hookName) {
    // 1. Load base configuration
    const baseConfig = this.loadSettingsFile('.claude/settings.local.json');

    // 2. Load environment overrides
    const envConfig = this.loadEnvironmentConfig();

    // 3. Merge configurations
    const config = this.mergeConfigs(baseConfig, envConfig);

    // 4. Validate configuration
    this.validateConfig(config);

    // 5. Return hook-specific config
    return config.hooks[hookName];
  }

  validateConfig(config) {
    // Check required fields
    if (!config.file) {
      throw new Error('Hook file path required');
    }

    // Validate timeout
    if (config.timeout && config.timeout < 0) {
      throw new Error('Timeout must be positive');
    }

    // Validate retries
    if (config.retries && config.retries < 0) {
      throw new Error('Retries must be non-negative');
    }
  }
}
```

### Configuration Inheritance

```
Global Config (~/.claude/settings.json)
      │
      ├──→ Merged with
      │
      ▼
Project Config (.claude/settings.local.json)
      │
      ├──→ Merged with
      │
      ▼
Environment Variables (CLAUDE_HOOK_*)
      │
      ▼
Final Configuration
```

### Advanced Configuration Examples

**Conditional Execution**:
```json
{
  "hooks": {
    "pre-commit": {
      "enabled": true,
      "file": ".claude/hooks/pre-commit.js",
      "conditions": {
        "files": ["*.js", "*.ts"],
        "skipIf": "process.env.SKIP_HOOKS === 'true'"
      }
    }
  }
}
```

**Priority-Based Execution**:
```json
{
  "hooks": {
    "session-start-1": {
      "enabled": true,
      "file": ".claude/hooks/mcp-health.js",
      "priority": 100
    },
    "session-start-2": {
      "enabled": true,
      "file": ".claude/hooks/load-context.js",
      "priority": 50
    }
  }
}
```

**Retry Logic**:
```json
{
  "hooks": {
    "pre-push": {
      "enabled": true,
      "file": ".claude/hooks/pre-push.js",
      "retries": 2,
      "timeout": 60000
    }
  }
}
```

---

## 🔧 Context API

### Context Object Structure

```typescript
interface HookContext {
  // File operations
  read(path: string): Promise<string>;
  write(path: string, content: string): Promise<void>;
  exists(path: string): Promise<boolean>;
  delete(path: string): Promise<void>;
  list(dir: string): Promise<string[]>;

  // Command execution
  exec(command: string, options?: ExecOptions): Promise<ExecResult>;
  execSilent(command: string): Promise<ExecResult>;

  // Project information
  projectRoot: string;
  projectName: string;
  gitBranch?: string;
  gitCommit?: string;

  // Memory/Knowledge
  loadMemory(): Promise<any>;
  saveMemory(data: any): Promise<void>;
  searchKnowledge(query: string): Promise<any[]>;
  addKnowledge(entry: any): Promise<void>;

  // Logging
  log(message: string): void;
  warn(message: string): void;
  error(message: string): void;
  debug(message: string): void;

  // Environment
  env: Record<string, string>;
  config: HookConfig;

  // Event data
  event: EventData;

  // MCP integration
  callMCP(server: string, tool: string, args: any): Promise<any>;

  // Utilities
  glob(pattern: string): Promise<string[]>;
  grep(pattern: string, options?: GrepOptions): Promise<string[]>;
  hash(content: string): string;
  timestamp(): string;
}
```

### Context Implementation

```javascript
class HookContext {
  constructor(config, event) {
    this.config = config;
    this.event = event;
    this.env = { ...process.env, ...config.environment };
    this.projectRoot = process.cwd();
  }

  // File operations
  async read(path) {
    const fs = require('fs').promises;
    const fullPath = this.resolvePath(path);
    return await fs.readFile(fullPath, 'utf8');
  }

  async write(path, content) {
    const fs = require('fs').promises;
    const fullPath = this.resolvePath(path);
    await fs.writeFile(fullPath, content, 'utf8');
  }

  async exists(path) {
    const fs = require('fs').promises;
    const fullPath = this.resolvePath(path);
    try {
      await fs.access(fullPath);
      return true;
    } catch {
      return false;
    }
  }

  // Command execution
  async exec(command, options = {}) {
    const { exec } = require('child_process');
    const { promisify } = require('util');
    const execAsync = promisify(exec);

    try {
      const result = await execAsync(command, {
        cwd: this.projectRoot,
        env: this.env,
        timeout: options.timeout || 30000
      });

      return {
        success: true,
        stdout: result.stdout,
        stderr: result.stderr
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stdout: error.stdout,
        stderr: error.stderr
      };
    }
  }

  // Memory operations
  async loadMemory() {
    const memoryPath = `${this.projectRoot}/.claude/memory.json`;
    if (await this.exists(memoryPath)) {
      const content = await this.read(memoryPath);
      return JSON.parse(content);
    }
    return {};
  }

  async saveMemory(data) {
    const memoryPath = `${this.projectRoot}/.claude/memory.json`;
    await this.write(memoryPath, JSON.stringify(data, null, 2));
  }

  // Logging
  log(message) {
    console.log(`[${this.config.name}] ${message}`);
  }

  warn(message) {
    console.warn(`[${this.config.name}] ⚠️  ${message}`);
  }

  error(message) {
    console.error(`[${this.config.name}] ❌ ${message}`);
  }

  // Utilities
  resolvePath(path) {
    const pathModule = require('path');
    if (pathModule.isAbsolute(path)) {
      return path;
    }
    return pathModule.join(this.projectRoot, path);
  }

  async glob(pattern) {
    const glob = require('glob');
    const { promisify } = require('util');
    const globAsync = promisify(glob);
    return await globAsync(pattern, { cwd: this.projectRoot });
  }
}
```

### Context Usage Examples

**Reading Files**:
```javascript
module.exports = async (context) => {
  // Read package.json
  const packageJson = await context.read('package.json');
  const pkg = JSON.parse(packageJson);

  // Check dependencies
  const deps = Object.keys(pkg.dependencies || {});
  context.log(`Found ${deps.length} dependencies`);

  return { success: true };
};
```

**Executing Commands**:
```javascript
module.exports = async (context) => {
  // Run tests
  const result = await context.exec('npm test');

  if (!result.success) {
    context.error('Tests failed');
    return { success: false, error: result.stderr };
  }

  context.log('✅ All tests passed');
  return { success: true };
};
```

**Working with Memory**:
```javascript
module.exports = async (context) => {
  // Load existing memory
  const memory = await context.loadMemory();

  // Update session count
  memory.sessionCount = (memory.sessionCount || 0) + 1;
  memory.lastSession = context.timestamp();

  // Save updated memory
  await context.saveMemory(memory);

  return { success: true };
};
```

---

## 🚨 Error Handling

### Error Types

**1. Configuration Errors**:
```javascript
{
  type: 'ConfigError',
  message: 'Hook file not found',
  hookName: 'pre-commit',
  file: '.claude/hooks/pre-commit.js',
  suggestion: 'Check file path in settings.local.json'
}
```

**2. Execution Errors**:
```javascript
{
  type: 'ExecutionError',
  message: 'Hook function threw exception',
  hookName: 'pre-commit',
  error: 'Cannot read property "length" of undefined',
  stack: '...',
  suggestion: 'Check hook implementation'
}
```

**3. Timeout Errors**:
```javascript
{
  type: 'TimeoutError',
  message: 'Hook execution exceeded timeout',
  hookName: 'pre-push',
  timeout: 30000,
  suggestion: 'Increase timeout or optimize hook'
}
```

**4. Validation Errors**:
```javascript
{
  type: 'ValidationError',
  message: 'Hook returned invalid result',
  hookName: 'post-commit',
  result: null,
  expected: '{ success: boolean }',
  suggestion: 'Return valid result object'
}
```

### Error Handling Strategy

```javascript
class HookExecutor {
  async execute(context) {
    try {
      // Set timeout
      const timeoutPromise = this.createTimeout();
      const hookPromise = this.runHook(context);

      // Race between hook and timeout
      const result = await Promise.race([hookPromise, timeoutPromise]);

      // Validate result
      this.validateResult(result);

      return result;

    } catch (error) {
      return this.handleError(error);
    } finally {
      this.cleanup();
    }
  }

  handleError(error) {
    // Log error with context
    this.logError(error);

    // Create error result
    const errorResult = {
      success: false,
      error: error.message,
      type: error.constructor.name,
      stack: error.stack,
      suggestion: this.getSuggestion(error)
    };

    // Decide whether to block operation
    if (this.isPreHook() && !this.config.continueOnError) {
      throw errorResult;  // Block operation
    }

    return errorResult;  // Continue with error logged
  }

  getSuggestion(error) {
    if (error instanceof TimeoutError) {
      return 'Increase timeout or optimize hook performance';
    }
    if (error instanceof ConfigError) {
      return 'Check settings.local.json configuration';
    }
    if (error instanceof ExecutionError) {
      return 'Check hook implementation and logs';
    }
    return 'Check hook logs for details';
  }
}
```

### Retry Logic

```javascript
class HookExecutor {
  async executeWithRetries(context) {
    const maxRetries = this.config.retries || 0;
    let attempt = 0;
    let lastError;

    while (attempt <= maxRetries) {
      try {
        this.log(`Attempt ${attempt + 1}/${maxRetries + 1}`);
        return await this.execute(context);

      } catch (error) {
        lastError = error;
        attempt++;

        if (attempt <= maxRetries) {
          // Wait before retry (exponential backoff)
          const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
          await this.sleep(delay);
        }
      }
    }

    // All retries failed
    throw lastError;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### Error Recovery

**Graceful Degradation**:
```javascript
module.exports = async (context) => {
  try {
    // Try primary operation
    const result = await primaryOperation();
    return { success: true, data: result };

  } catch (error) {
    context.warn('Primary operation failed, trying fallback');

    try {
      // Try fallback operation
      const fallbackResult = await fallbackOperation();
      return { success: true, data: fallbackResult, fallback: true };

    } catch (fallbackError) {
      // Both failed
      context.error('All operations failed');
      return {
        success: false,
        error: fallbackError.message
      };
    }
  }
};
```

---

## ⚡ Performance Considerations

### Performance Goals

| Metric | Target | Maximum |
|--------|--------|---------|
| Hook discovery | <10ms | 50ms |
| Context creation | <100ms | 500ms |
| Hook execution | <5s | 30s |
| Total overhead | <10% | 20% |

### Performance Optimization

**1. Lazy Loading**:
```javascript
class HookManager {
  constructor() {
    this.hooks = new Map();
    this.loaded = new Set();
  }

  async loadHook(name) {
    // Only load if not already loaded
    if (!this.loaded.has(name)) {
      const script = await this.loadScript(name);
      this.hooks.set(name, script);
      this.loaded.add(name);
    }
    return this.hooks.get(name);
  }
}
```

**2. Caching**:
```javascript
module.exports = async (context) => {
  // Cache expensive computation
  const cacheKey = 'expensive-result';
  const cached = await context.loadMemory(cacheKey);

  if (cached && !isCacheExpired(cached)) {
    context.log('Using cached result');
    return { success: true, data: cached.data };
  }

  // Compute if not cached
  const result = await expensiveComputation();

  // Cache for next time
  await context.saveMemory(cacheKey, {
    data: result,
    timestamp: Date.now()
  });

  return { success: true, data: result };
};
```

**3. Async Operations**:
```javascript
module.exports = async (context) => {
  // Run operations in parallel
  const [lintResult, testResult, typeResult] = await Promise.all([
    context.exec('npm run lint'),
    context.exec('npm test'),
    context.exec('npm run type-check')
  ]);

  // All complete at same time
  const allPassed = lintResult.success &&
                    testResult.success &&
                    typeResult.success;

  return { success: allPassed };
};
```

**4. Early Exit**:
```javascript
module.exports = async (context) => {
  // Check fast condition first
  const hasChanges = await context.exec('git diff --cached --quiet');
  if (hasChanges.success) {
    // No changes, skip hook
    return { success: true, skipped: true };
  }

  // Only run expensive operations if needed
  return await runExpensiveValidation(context);
};
```

### Timeout Management

```javascript
class HookExecutor {
  createTimeout() {
    const timeout = this.config.timeout || 30000;

    return new Promise((_, reject) => {
      this.timeoutId = setTimeout(() => {
        reject(new TimeoutError(
          `Hook exceeded timeout of ${timeout}ms`
        ));
      }, timeout);
    });
  }

  clearTimeout() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }
}
```

### Performance Monitoring

```javascript
class PerformanceMonitor {
  startHook(hookName) {
    this.start = performance.now();
    this.hookName = hookName;
  }

  endHook() {
    const duration = performance.now() - this.start;

    // Log if slow
    if (duration > 5000) {
      console.warn(`⚠️  Hook ${this.hookName} took ${duration}ms`);
    }

    // Record metric
    this.recordMetric(this.hookName, duration);
  }

  recordMetric(hookName, duration) {
    // Store in metrics database
    // Or send to monitoring service
  }
}
```

---

## 🔗 Hook Chaining

### Chaining Patterns

**Sequential Chaining**:
```javascript
// Hook 1: Validate
module.exports = async (context) => {
  const valid = await validate(context);
  if (!valid) {
    return { success: false, error: 'Validation failed' };
  }

  // Signal to next hook
  await context.saveMemory('validation-passed', true);
  return { success: true };
};

// Hook 2: Process (depends on Hook 1)
module.exports = async (context) => {
  const validationPassed = await context.loadMemory('validation-passed');
  if (!validationPassed) {
    return { success: false, error: 'Validation did not pass' };
  }

  return await process(context);
};
```

**Conditional Chaining**:
```javascript
module.exports = async (context) => {
  const result = await operation(context);

  if (result.needsFollowup) {
    // Trigger another hook
    await context.emit('custom:followup', result);
  }

  return { success: true };
};
```

**Data Pipeline**:
```javascript
// Hook 1: Extract
module.exports = async (context) => {
  const data = await extract(context);
  await context.saveMemory('extracted-data', data);
  return { success: true };
};

// Hook 2: Transform (uses Hook 1 data)
module.exports = async (context) => {
  const data = await context.loadMemory('extracted-data');
  const transformed = await transform(data);
  await context.saveMemory('transformed-data', transformed);
  return { success: true };
};

// Hook 3: Load (uses Hook 2 data)
module.exports = async (context) => {
  const data = await context.loadMemory('transformed-data');
  await load(data);
  return { success: true };
};
```

---

## 🔀 Parallel vs Sequential Execution

### Sequential Execution (Default)

```javascript
// Hooks run one after another
for (const hook of hooks) {
  const result = await executeHook(hook);
  if (!result.success && hook.blocking) {
    break;  // Stop on failure
  }
}
```

**Use sequential when**:
- Hooks depend on each other
- Order matters
- Need to stop on first failure

### Parallel Execution

```json
{
  "hooks": {
    "session-start": {
      "enabled": true,
      "parallel": ["mcp-check", "env-validate", "load-context"]
    }
  }
}
```

```javascript
// Hooks run simultaneously
const results = await Promise.all(
  hooks.map(hook => executeHook(hook))
);

// Check if all succeeded
const allSuccess = results.every(r => r.success);
```

**Use parallel when**:
- Hooks are independent
- Want fastest total execution
- Can handle multiple failures

### Hybrid Approach

```javascript
// Sequential phases, parallel within phase
const phase1 = await Promise.all([
  executeHook('lint'),
  executeHook('type-check')
]);

if (phase1.every(r => r.success)) {
  const phase2 = await Promise.all([
    executeHook('unit-tests'),
    executeHook('integration-tests')
  ]);
}
```

---

## 🔍 Hook Discovery

### Discovery Process

```javascript
class HookDiscovery {
  async discoverHooks() {
    const hooks = [];

    // 1. Check project hooks
    const projectHooks = await this.scanDirectory('.claude/hooks');
    hooks.push(...projectHooks);

    // 2. Check global hooks
    const globalHooks = await this.scanDirectory('~/.claude/hooks');
    hooks.push(...globalHooks);

    // 3. Filter by configuration
    return this.filterByConfig(hooks);
  }

  async scanDirectory(dir) {
    const fs = require('fs').promises;
    const files = await fs.readdir(dir);

    return files
      .filter(f => this.isHookFile(f))
      .map(f => this.createHookConfig(dir, f));
  }

  isHookFile(filename) {
    return filename.match(/\.(js|py|sh)$/);
  }
}
```

### Discovery Priority

```
1. Explicit configuration in settings.local.json
2. Project hooks directory (.claude/hooks/)
3. Global hooks directory (~/.claude/hooks/)
4. Built-in hooks
```

---

## 🔒 Security Model

### Security Principles

1. **Least Privilege** - Hooks only get necessary permissions
2. **Sandboxing** - Isolated execution environment
3. **Validation** - Input and output validation
4. **Audit Trail** - Log all hook executions

### Permission Model

```json
{
  "hooks": {
    "pre-commit": {
      "permissions": {
        "read": ["src/**", "tests/**"],
        "write": [".claude/memory.json"],
        "exec": ["npm:*", "git:status"],
        "network": false
      }
    }
  }
}
```

### Security Checks

```javascript
class SecurityValidator {
  validateHookAccess(hook, operation, target) {
    const permissions = hook.config.permissions;

    switch(operation) {
      case 'read':
        return this.checkPattern(target, permissions.read);
      case 'write':
        return this.checkPattern(target, permissions.write);
      case 'exec':
        return this.checkCommand(target, permissions.exec);
      case 'network':
        return permissions.network === true;
    }

    return false;
  }

  checkPattern(path, patterns) {
    return patterns.some(pattern =>
      minimatch(path, pattern)
    );
  }
}
```

---

## 🧪 Testing Framework

### Hook Testing

```javascript
// test-hook.js
const { HookTester } = require('@claude/hook-testing');

describe('session-start hook', () => {
  let tester;

  beforeEach(() => {
    tester = new HookTester('session-start');
  });

  test('should load project memory', async () => {
    const result = await tester.execute();

    expect(result.success).toBe(true);
    expect(result.memoryLoaded).toBe(true);
  });

  test('should handle missing memory file', async () => {
    tester.mockFileSystem({ '.claude/memory.json': null });

    const result = await tester.execute();

    expect(result.success).toBe(true);
    expect(result.memoryCreated).toBe(true);
  });
});
```

### Integration Testing

```bash
# Test all hooks
claude test-hooks

# Test specific hook
claude test-hook session-start

# Test hook with mock data
claude test-hook pre-commit --mock-files="src/index.js,src/utils.js"
```

---

## 🎨 Advanced Patterns

### Async Background Hooks

```javascript
module.exports = async (context) => {
  // Immediately return success
  context.log('Starting background task...');

  // Start background work
  setImmediate(async () => {
    await longRunningTask(context);
    context.log('Background task complete');
  });

  return { success: true, async: true };
};
```

### Debounced Hooks

```javascript
const debounce = require('lodash.debounce');

const debouncedHook = debounce(async (context) => {
  // Only runs after 1s of inactivity
  await actualWork(context);
}, 1000);

module.exports = async (context) => {
  debouncedHook(context);
  return { success: true, debounced: true };
};
```

### Conditional Hooks

```javascript
module.exports = async (context) => {
  // Only run on main branch
  const branch = await context.exec('git branch --show-current');
  if (branch.stdout.trim() !== 'main') {
    return { success: true, skipped: true };
  }

  // Only run if specific files changed
  const changedFiles = await context.exec('git diff --name-only --cached');
  const hasRelevantChanges = changedFiles.stdout.includes('src/');

  if (!hasRelevantChanges) {
    return { success: true, skipped: true };
  }

  return await actualValidation(context);
};
```

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: Architecture Team
**Status**: Active

---

**Navigate**: [← Back to Hooks](./README.md) | [Session Hooks →](./session-hooks.md) | [Git Hooks →](./git-hooks.md) | [Creating Hooks →](./creating-hooks.md)

---

*Built with ❤️ for developers who love robust automation*
