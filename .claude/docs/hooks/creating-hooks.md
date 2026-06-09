# 🛠️ Creating Custom Hooks

> **Step-by-step guide for building your own Claude Code hooks**

This document provides comprehensive instructions for creating custom hooks in JavaScript, Python, and Shell, with templates, testing techniques, and best practices.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Hook File Structure](#-hook-file-structure)
- [Hook API](#-hook-api)
- [JavaScript Hooks](#-javascript-hooks)
- [Python Hooks](#-python-hooks)
- [Shell Hooks](#-shell-hooks)
- [Configuration Integration](#-configuration-integration)
- [Testing Hooks](#-testing-hooks)
- [Debugging Techniques](#-debugging-techniques)
- [Best Practices](#-best-practices)
- [Security Considerations](#-security-considerations)
- [Complete Examples](#-complete-examples)

---

## 🎯 Overview

### What You'll Learn

This guide covers:
- Hook file structure and requirements
- Context API and utilities
- Creating hooks in multiple languages
- Configuration and testing
- Debugging and troubleshooting
- Security best practices

### Prerequisites

Before creating hooks, you should understand:
- Basic programming (JavaScript, Python, or Shell)
- Git operations (for Git hooks)
- JSON configuration
- Async/await patterns (for JavaScript)

### Quick Start

**1. Create hook file**:
```bash
# Create hooks directory
mkdir -p .claude/hooks

# Create your hook
touch .claude/hooks/my-hook.js
```

**2. Write hook logic**:
```javascript
module.exports = async function(context) {
  context.log('Hello from my hook!');
  return { success: true };
};
```

**3. Configure hook**:
```json
{
  "hooks": {
    "session-start": {
      "enabled": true,
      "file": ".claude/hooks/my-hook.js"
    }
  }
}
```

**4. Test hook**:
```bash
claude test-hook session-start
```

---

## 📄 Hook File Structure

### Basic Structure

All hooks follow this pattern:

```
1. Import dependencies (if needed)
2. Define main hook function
3. Perform operations using context
4. Return result object
5. Export hook function
```

### Minimal Hook

**JavaScript**:
```javascript
module.exports = async function(context) {
  return { success: true };
};
```

**Python**:
```python
async def hook(context):
    return {"success": True}
```

**Shell**:
```bash
#!/bin/bash
echo "Hook executed"
exit 0  # 0 = success, non-zero = failure
```

### Complete Hook Template

**JavaScript**:
```javascript
// .claude/hooks/template.js
/**
 * Hook Description
 *
 * Purpose: What does this hook do?
 * Triggers: When is it called?
 * Dependencies: What does it require?
 */

module.exports = async function(context) {
  try {
    // Log start
    context.log('🚀 Starting hook...');

    // Perform operations
    const result = await performOperation(context);

    // Log success
    context.log('✅ Hook completed');

    // Return success
    return {
      success: true,
      data: result
    };

  } catch (error) {
    // Log error
    context.error(`❌ Hook failed: ${error.message}`);

    // Return failure
    return {
      success: false,
      error: error.message
    };
  }
};

async function performOperation(context) {
  // Your logic here
  return {};
}
```

### Return Object Structure

Hooks must return an object with these properties:

```typescript
interface HookResult {
  success: boolean;           // Required: Did hook succeed?
  error?: string;             // Optional: Error message if failed
  message?: string;           // Optional: Additional info
  data?: any;                 // Optional: Result data
  skipped?: boolean;          // Optional: Was hook skipped?
  warning?: string;           // Optional: Warning message
  [key: string]: any;         // Optional: Custom properties
}
```

**Examples**:
```javascript
// Success
return { success: true };

// Success with data
return {
  success: true,
  data: { filesProcessed: 10 }
};

// Skipped
return {
  success: true,
  skipped: true,
  message: 'No files to process'
};

// Failure
return {
  success: false,
  error: 'Validation failed',
  details: errorDetails
};

// Warning
return {
  success: true,
  warning: 'Some checks failed but not blocking'
};
```

---

## 🔧 Hook API

### Context Object

The `context` object provides utilities for hook operations:

#### File Operations

```javascript
// Read file
const content = await context.read('path/to/file.txt');

// Write file
await context.write('path/to/file.txt', 'content');

// Check if file exists
const exists = await context.exists('path/to/file.txt');

// Delete file
await context.delete('path/to/file.txt');

// List directory
const files = await context.list('path/to/dir');

// Resolve absolute path
const absPath = context.resolvePath('relative/path');
```

#### Command Execution

```javascript
// Execute command
const result = await context.exec('npm test');
// result = { success: true/false, stdout: '...', stderr: '...' }

// Execute silently (no output)
const result = await context.execSilent('git status');

// Execute with options
const result = await context.exec('npm install', {
  timeout: 60000,
  cwd: '/custom/dir',
  env: { NODE_ENV: 'production' }
});
```

#### Memory/Knowledge Operations

```javascript
// Load memory
const memory = await context.loadMemory();

// Save memory
await context.saveMemory({ key: 'value' });

// Search knowledge base
const results = await context.searchKnowledge('query string');

// Add to knowledge base
await context.addKnowledge({
  type: 'pattern',
  content: 'Code pattern...'
});
```

#### Logging

```javascript
// Info log
context.log('Information message');

// Warning
context.warn('⚠️  Warning message');

// Error
context.error('❌ Error message');

// Debug (only shown in debug mode)
context.debug('Debug info');
```

#### MCP Integration

```javascript
// Call MCP server
const result = await context.callMCP('server-name', 'tool-name', {
  arg1: 'value1',
  arg2: 'value2'
});
```

#### Utilities

```javascript
// Glob pattern matching
const files = await context.glob('src/**/*.js');

// Grep (search in files)
const results = await context.grep('pattern', {
  path: 'src/',
  type: 'js'
});

// Hash content
const hash = context.hash('content to hash');

// Get timestamp
const timestamp = context.timestamp();
// Returns ISO 8601 string
```

#### Properties

```javascript
// Project information
context.projectRoot      // '/path/to/project'
context.projectName      // 'my-project'
context.gitBranch        // 'main'
context.gitCommit        // 'abc123'

// Environment variables
context.env.NODE_ENV     // 'development'
context.env.API_KEY      // 'secret'

// Hook configuration
context.config.timeout   // 30000
context.config.priority  // 100

// Event data
context.event.type       // 'session-start'
context.event.timestamp  // '2025-01-15T10:00:00Z'
context.event.data       // Event-specific data
```

---

## 📦 JavaScript Hooks

### Basic JavaScript Hook

```javascript
// .claude/hooks/example.js
module.exports = async function(context) {
  context.log('Running example hook');

  // Check if package.json exists
  if (!await context.exists('package.json')) {
    context.warn('No package.json found');
    return { success: true, skipped: true };
  }

  // Read and parse package.json
  const packageJson = JSON.parse(
    await context.read('package.json')
  );

  context.log(`Project: ${packageJson.name}`);

  return {
    success: true,
    project: packageJson.name
  };
};
```

### Advanced JavaScript Hook

```javascript
// .claude/hooks/advanced-example.js
const path = require('path');

module.exports = async function(context) {
  context.log('🔍 Running advanced validation...');

  const results = {
    filesChecked: 0,
    issues: []
  };

  // Get all JavaScript files
  const jsFiles = await context.glob('src/**/*.js');
  results.filesChecked = jsFiles.length;

  context.log(`  Checking ${jsFiles.length} files...`);

  // Check each file
  for (const file of jsFiles) {
    const issues = await checkFile(context, file);
    if (issues.length > 0) {
      results.issues.push({ file, issues });
    }
  }

  // Report results
  if (results.issues.length > 0) {
    context.warn(`⚠️  Found issues in ${results.issues.length} files`);

    results.issues.forEach(({ file, issues }) => {
      context.warn(`  ${file}:`);
      issues.forEach(issue => {
        context.warn(`    - ${issue}`);
      });
    });

    return {
      success: false,
      error: 'Validation issues found',
      results
    };
  }

  context.log('✅ All files valid');

  return {
    success: true,
    results
  };
};

async function checkFile(context, file) {
  const issues = [];
  const content = await context.read(file);

  // Check for console.log
  if (content.includes('console.log')) {
    issues.push('Contains console.log');
  }

  // Check for TODO comments
  if (content.includes('// TODO')) {
    issues.push('Contains TODO comments');
  }

  // Check file size
  if (content.length > 10000) {
    issues.push('File exceeds 10KB');
  }

  return issues;
}
```

### JavaScript Hook with External Dependencies

```javascript
// .claude/hooks/with-dependencies.js
// Note: Install dependencies in .claude/hooks/package.json

const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async function(context) {
  context.log('Fetching external data...');

  try {
    const response = await axios.get('https://api.example.com/data', {
      timeout: 5000
    });

    const data = response.data;

    context.log(`✅ Fetched ${data.items.length} items`);

    return {
      success: true,
      data: data.items
    };

  } catch (error) {
    context.error(`❌ Failed to fetch: ${error.message}`);

    return {
      success: false,
      error: error.message
    };
  }
};
```

---

## 🐍 Python Hooks

### Basic Python Hook

```python
# .claude/hooks/example.py
import json
import os

async def hook(context):
    """Example Python hook"""
    context.log("Running Python hook")

    # Check if file exists
    if not await context.exists("package.json"):
        context.warn("No package.json found")
        return {"success": True, "skipped": True}

    # Read file
    content = await context.read("package.json")
    data = json.loads(content)

    context.log(f"Project: {data['name']}")

    return {
        "success": True,
        "project": data["name"]
    }
```

### Advanced Python Hook

```python
# .claude/hooks/advanced-example.py
import re
import json
from typing import List, Dict, Any

async def hook(context) -> Dict[str, Any]:
    """Advanced validation hook"""
    context.log("🔍 Running Python validation...")

    results = {
        "files_checked": 0,
        "issues": []
    }

    # Get Python files
    py_files = await context.glob("src/**/*.py")
    results["files_checked"] = len(py_files)

    context.log(f"  Checking {len(py_files)} files...")

    # Check each file
    for file in py_files:
        issues = await check_file(context, file)
        if issues:
            results["issues"].append({
                "file": file,
                "issues": issues
            })

    # Report results
    if results["issues"]:
        context.warn(f"⚠️  Found issues in {len(results['issues'])} files")

        for item in results["issues"]:
            context.warn(f"  {item['file']}:")
            for issue in item["issues"]:
                context.warn(f"    - {issue}")

        return {
            "success": False,
            "error": "Validation issues found",
            "results": results
        }

    context.log("✅ All files valid")

    return {
        "success": True,
        "results": results
    }

async def check_file(context, file: str) -> List[str]:
    """Check a single file for issues"""
    issues = []
    content = await context.read(file)

    # Check for print statements
    if "print(" in content:
        issues.append("Contains print statements")

    # Check for TODO comments
    if "# TODO" in content:
        issues.append("Contains TODO comments")

    # Check for proper docstrings
    if "def " in content:
        if not re.search(r'def \w+.*:\n\s+"""', content):
            issues.append("Missing docstrings")

    return issues
```

### Python Hook with External Libraries

```python
# .claude/hooks/with-libraries.py
import aiohttp
import asyncio
from typing import Dict, Any

async def hook(context) -> Dict[str, Any]:
    """Hook with external API call"""
    context.log("Fetching external data...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.example.com/data',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                data = await response.json()

        context.log(f"✅ Fetched {len(data['items'])} items")

        return {
            "success": True,
            "data": data["items"]
        }

    except asyncio.TimeoutError:
        context.error("❌ Request timeout")
        return {
            "success": False,
            "error": "Request timeout"
        }

    except Exception as e:
        context.error(f"❌ Failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 🐚 Shell Hooks

### Basic Shell Hook

```bash
#!/bin/bash
# .claude/hooks/example.sh

echo "🚀 Running shell hook..."

# Check if file exists
if [ ! -f "package.json" ]; then
  echo "⚠️  No package.json found"
  exit 0  # Success but skipped
fi

# Read project name
PROJECT_NAME=$(jq -r '.name' package.json)
echo "Project: $PROJECT_NAME"

echo "✅ Hook completed"
exit 0
```

### Advanced Shell Hook

```bash
#!/bin/bash
# .claude/hooks/advanced-example.sh

set -e  # Exit on error

echo "🔍 Running shell validation..."

ISSUES_FOUND=0

# Find all JavaScript files
JS_FILES=$(find src -name "*.js" -type f)
FILE_COUNT=$(echo "$JS_FILES" | wc -l)

echo "  Checking $FILE_COUNT files..."

# Check each file
for file in $JS_FILES; do
  ISSUES=()

  # Check for console.log
  if grep -q "console.log" "$file"; then
    ISSUES+=("Contains console.log")
  fi

  # Check for TODO
  if grep -q "// TODO" "$file"; then
    ISSUES+=("Contains TODO")
  fi

  # Check file size
  SIZE=$(wc -c < "$file")
  if [ "$SIZE" -gt 10000 ]; then
    ISSUES+=("File exceeds 10KB")
  fi

  # Report issues
  if [ ${#ISSUES[@]} -gt 0 ]; then
    echo "⚠️  Issues in $file:"
    for issue in "${ISSUES[@]}"; do
      echo "    - $issue"
    done
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
  fi
done

# Report results
if [ $ISSUES_FOUND -gt 0 ]; then
  echo "❌ Found issues in $ISSUES_FOUND files"
  exit 1
fi

echo "✅ All files valid"
exit 0
```

### Shell Hook with Functions

```bash
#!/bin/bash
# .claude/hooks/with-functions.sh

# Function definitions
check_dependencies() {
  echo "Checking dependencies..."

  local missing=0

  for cmd in node npm git; do
    if ! command -v $cmd &> /dev/null; then
      echo "  ❌ $cmd not found"
      missing=$((missing + 1))
    else
      echo "  ✅ $cmd found"
    fi
  done

  return $missing
}

check_environment() {
  echo "Checking environment..."

  if [ -z "$NODE_ENV" ]; then
    echo "  ⚠️  NODE_ENV not set"
    return 1
  fi

  echo "  ✅ NODE_ENV=$NODE_ENV"
  return 0
}

# Main execution
echo "🚀 Running environment check..."

if ! check_dependencies; then
  echo "❌ Missing dependencies"
  exit 1
fi

if ! check_environment; then
  echo "⚠️  Environment issues (not blocking)"
fi

echo "✅ Check completed"
exit 0
```

---

## ⚙️ Configuration Integration

### Hook Configuration Schema

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
      "priority": 100,
      "environment": {
        "KEY": "value"
      },
      "conditions": {
        "files": ["*.js"],
        "branches": ["main"],
        "skipIf": "env.SKIP_HOOKS === 'true'"
      }
    }
  }
}
```

### Conditional Execution

**Only on specific files**:
```json
{
  "hooks": {
    "lint-js": {
      "enabled": true,
      "file": ".claude/hooks/lint.js",
      "conditions": {
        "files": ["*.js", "*.ts"]
      }
    }
  }
}
```

**Only on specific branches**:
```json
{
  "hooks": {
    "deploy-check": {
      "enabled": true,
      "file": ".claude/hooks/deploy.js",
      "conditions": {
        "branches": ["main", "production"]
      }
    }
  }
}
```

**Skip based on environment**:
```json
{
  "hooks": {
    "heavy-validation": {
      "enabled": true,
      "file": ".claude/hooks/validate.js",
      "conditions": {
        "skipIf": "process.env.CI !== 'true'"
      }
    }
  }
}
```

### Environment Variables

```json
{
  "hooks": {
    "api-check": {
      "enabled": true,
      "file": ".claude/hooks/api-check.js",
      "environment": {
        "API_URL": "https://api.example.com",
        "API_TIMEOUT": "5000",
        "DEBUG": "false"
      }
    }
  }
}
```

**Accessing in hook**:
```javascript
module.exports = async function(context) {
  const apiUrl = context.env.API_URL;
  const timeout = parseInt(context.env.API_TIMEOUT);
  const debug = context.env.DEBUG === 'true';

  // Use environment variables
};
```

---

## 🧪 Testing Hooks

### Manual Testing

**Test hook directly**:
```bash
# JavaScript
node .claude/hooks/my-hook.js

# Python
python .claude/hooks/my-hook.py

# Shell
bash .claude/hooks/my-hook.sh
```

**Test via Claude Code**:
```bash
# Test specific hook
claude test-hook session-start

# Test with mock data
claude test-hook pre-commit --mock-files="src/index.js,src/utils.js"

# Test with debug output
CLAUDE_DEBUG_HOOKS=true claude test-hook my-hook
```

### Automated Testing

**JavaScript (Jest)**:
```javascript
// .claude/hooks/__tests__/my-hook.test.js
const hook = require('../my-hook');

describe('my-hook', () => {
  let mockContext;

  beforeEach(() => {
    mockContext = {
      log: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
      read: jest.fn(),
      write: jest.fn(),
      exists: jest.fn(),
      exec: jest.fn(),
      projectRoot: '/test/project',
      env: {}
    };
  });

  test('should return success when package.json exists', async () => {
    mockContext.exists.mockResolvedValue(true);
    mockContext.read.mockResolvedValue('{"name":"test"}');

    const result = await hook(mockContext);

    expect(result.success).toBe(true);
    expect(result.project).toBe('test');
  });

  test('should skip when package.json missing', async () => {
    mockContext.exists.mockResolvedValue(false);

    const result = await hook(mockContext);

    expect(result.success).toBe(true);
    expect(result.skipped).toBe(true);
  });
});
```

**Python (pytest)**:
```python
# .claude/hooks/test_my_hook.py
import pytest
from unittest.mock import AsyncMock, Mock
from my_hook import hook

@pytest.mark.asyncio
async def test_hook_success():
    """Test hook succeeds when package.json exists"""
    mock_context = Mock()
    mock_context.log = Mock()
    mock_context.exists = AsyncMock(return_value=True)
    mock_context.read = AsyncMock(return_value='{"name":"test"}')

    result = await hook(mock_context)

    assert result["success"] == True
    assert result["project"] == "test"

@pytest.mark.asyncio
async def test_hook_skipped():
    """Test hook skips when package.json missing"""
    mock_context = Mock()
    mock_context.warn = Mock()
    mock_context.exists = AsyncMock(return_value=False)

    result = await hook(mock_context)

    assert result["success"] == True
    assert result["skipped"] == True
```

**Shell (bats)**:
```bash
# .claude/hooks/test_my_hook.bats
#!/usr/bin/env bats

setup() {
  export TEST_DIR="$BATS_TEST_DIRNAME/fixtures"
}

@test "hook succeeds when package.json exists" {
  cd "$TEST_DIR"
  run bash ../ my-hook.sh

  [ "$status" -eq 0 ]
  [[ "$output" =~ "✅ Hook completed" ]]
}

@test "hook skips when package.json missing" {
  run bash ../my-hook.sh

  [ "$status" -eq 0 ]
  [[ "$output" =~ "⚠️  No package.json found" ]]
}
```

### Integration Testing

**Test entire workflow**:
```bash
#!/bin/bash
# test-workflow.sh

echo "Testing Git workflow..."

# Setup test repo
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"
git init

# Copy hooks
cp -r .claude .

# Configure hooks
claude configure-hooks

# Test pre-commit
echo "console.log('test');" > test.js
git add test.js

echo "Running pre-commit..."
if git commit -m "test"; then
  echo "❌ Pre-commit should have failed"
  exit 1
fi

echo "✅ Pre-commit correctly blocked commit"

# Cleanup
cd -
rm -rf "$TEST_DIR"
```

---

## 🐛 Debugging Techniques

### Logging

**Add detailed logging**:
```javascript
module.exports = async function(context) {
  context.debug('Starting hook');
  context.debug(`Project root: ${context.projectRoot}`);
  context.debug(`Event: ${JSON.stringify(context.event)}`);

  const result = await operation(context);

  context.debug(`Result: ${JSON.stringify(result)}`);

  return { success: true };
};
```

**Enable debug output**:
```bash
CLAUDE_DEBUG_HOOKS=true claude test-hook my-hook
```

### Error Handling

**Comprehensive error handling**:
```javascript
module.exports = async function(context) {
  try {
    const result = await riskyOperation(context);
    return { success: true, data: result };

  } catch (error) {
    context.error(`Error: ${error.message}`);
    context.error(`Stack: ${error.stack}`);

    // Dump context for debugging
    context.debug('Context dump:', {
      projectRoot: context.projectRoot,
      event: context.event,
      env: context.env
    });

    return {
      success: false,
      error: error.message,
      stack: error.stack
    };
  }
};
```

### Timing Analysis

**Measure performance**:
```javascript
module.exports = async function(context) {
  const times = {};

  const start = Date.now();

  times.operation1 = await timeOperation(async () => {
    await operation1(context);
  });

  times.operation2 = await timeOperation(async () => {
    await operation2(context);
  });

  times.total = Date.now() - start;

  context.log(`Timing: ${JSON.stringify(times, null, 2)}`);

  return { success: true, timing: times };
};

async function timeOperation(fn) {
  const start = Date.now();
  await fn();
  return Date.now() - start;
}
```

### Dry Run Mode

**Add dry-run support**:
```javascript
module.exports = async function(context) {
  const dryRun = context.env.DRY_RUN === 'true';

  if (dryRun) {
    context.log('🏃 DRY RUN MODE');
  }

  // Read operations (always safe)
  const data = await context.read('file.txt');

  // Write operations (skip in dry-run)
  if (!dryRun) {
    await context.write('output.txt', data);
  } else {
    context.log('Would write to output.txt');
  }

  return { success: true, dryRun };
};
```

**Run in dry-run mode**:
```bash
DRY_RUN=true claude test-hook my-hook
```

---

## 💡 Best Practices

### General

✅ **DO**:
- Keep hooks fast (<5 seconds typical)
- Return meaningful result objects
- Handle all errors gracefully
- Log progress clearly
- Make hooks idempotent
- Test thoroughly
- Document purpose and usage

❌ **DON'T**:
- Block on slow operations
- Make assumptions about environment
- Modify files unexpectedly
- Fail silently
- Skip error handling
- Hardcode values
- Ignore edge cases

### Performance

✅ **DO**:
```javascript
// Run operations in parallel
const [lint, test, typecheck] = await Promise.all([
  runLint(context),
  runTests(context),
  runTypeCheck(context)
]);
```

❌ **DON'T**:
```javascript
// Sequential (slow)
const lint = await runLint(context);
const test = await runTests(context);
const typecheck = await runTypeCheck(context);
```

### Error Handling

✅ **DO**:
```javascript
try {
  await operation(context);
  return { success: true };
} catch (error) {
  context.error(`Failed: ${error.message}`);
  return {
    success: false,
    error: error.message,
    suggestion: 'Check logs for details'
  };
}
```

❌ **DON'T**:
```javascript
// No error handling
const result = await operation(context);
return { success: true };
```

---

## 🔒 Security Considerations

### Input Validation

```javascript
module.exports = async function(context) {
  // Validate file paths
  const file = context.event.file;

  if (!file || file.includes('..')) {
    return {
      success: false,
      error: 'Invalid file path'
    };
  }

  // Resolve to absolute path
  const absPath = context.resolvePath(file);

  // Ensure within project
  if (!absPath.startsWith(context.projectRoot)) {
    return {
      success: false,
      error: 'Path outside project'
    };
  }

  return { success: true };
};
```

### Command Injection Prevention

```javascript
// ❌ UNSAFE
await context.exec(`grep ${userInput} file.txt`);

// ✅ SAFE
await context.grep(userInput, { path: 'file.txt' });

// ✅ SAFE (escaped)
const escaped = userInput.replace(/[;|&$`]/g, '\\$&');
await context.exec(`grep "${escaped}" file.txt`);
```

### Secret Management

```javascript
// ❌ UNSAFE
const apiKey = 'hardcoded-secret-key';

// ✅ SAFE
const apiKey = context.env.API_KEY;

if (!apiKey) {
  return {
    success: false,
    error: 'API_KEY not configured'
  };
}
```

### Permission Checks

```javascript
module.exports = async function(context) {
  // Check if hook has necessary permissions
  const canWrite = context.config.permissions?.write || [];

  const targetFile = 'important-file.txt';

  if (!canWrite.includes(targetFile)) {
    return {
      success: false,
      error: 'No write permission for file'
    };
  }

  await context.write(targetFile, 'data');

  return { success: true };
};
```

---

## 🌟 Complete Examples

### Example 1: File Validator

```javascript
// .claude/hooks/file-validator.js
/**
 * Validates files before commit
 * - Checks file size
 * - Validates naming conventions
 * - Ensures proper extensions
 */

module.exports = async function(context) {
  context.log('📋 Validating files...');

  // Get staged files
  const staged = await context.exec(
    'git diff --cached --name-only'
  );

  const files = staged.stdout.split('\n').filter(f => f.trim());

  if (files.length === 0) {
    return { success: true, skipped: true };
  }

  const issues = [];

  for (const file of files) {
    // Check file size
    if (await context.exists(file)) {
      const content = await context.read(file);

      if (content.length > 1024 * 1024) {  // 1MB
        issues.push({
          file,
          issue: 'File exceeds 1MB'
        });
      }
    }

    // Check naming convention (kebab-case)
    const basename = file.split('/').pop();
    if (!/^[a-z0-9-]+\.[a-z]+$/.test(basename)) {
      issues.push({
        file,
        issue: 'Should use kebab-case naming'
      });
    }

    // Check allowed extensions
    const allowedExts = ['.js', '.ts', '.json', '.md', '.yml'];
    const ext = basename.substring(basename.lastIndexOf('.'));

    if (!allowedExts.includes(ext)) {
      issues.push({
        file,
        issue: `Extension ${ext} not allowed`
      });
    }
  }

  if (issues.length > 0) {
    context.error('❌ File validation failed:');
    issues.forEach(({ file, issue }) => {
      context.error(`  ${file}: ${issue}`);
    });

    return {
      success: false,
      error: 'Validation failed',
      issues
    };
  }

  context.log(`✅ ${files.length} files validated`);

  return {
    success: true,
    filesValidated: files.length
  };
};
```

### Example 2: Dependency Checker

```python
# .claude/hooks/dependency-checker.py
"""
Checks for outdated dependencies and security issues
"""

import json
import subprocess
from typing import Dict, Any, List

async def hook(context) -> Dict[str, Any]:
    """Check dependencies"""
    context.log("📦 Checking dependencies...")

    if not await context.exists("package.json"):
        return {"success": True, "skipped": True}

    results = {
        "outdated": [],
        "vulnerabilities": []
    }

    # Check outdated packages
    outdated = await check_outdated(context)
    results["outdated"] = outdated

    # Check vulnerabilities
    vulnerabilities = await check_vulnerabilities(context)
    results["vulnerabilities"] = vulnerabilities

    # Report
    if outdated:
        context.warn(f"⚠️  {len(outdated)} outdated packages")
        for pkg in outdated[:5]:  # Show first 5
            context.warn(f"  {pkg['name']}: {pkg['current']} → {pkg['latest']}")

    if vulnerabilities:
        context.error(f"❌ {len(vulnerabilities)} vulnerabilities")
        for vuln in vulnerabilities[:5]:
            context.error(f"  {vuln['name']}: {vuln['severity']}")

        return {
            "success": False,
            "error": "Security vulnerabilities found",
            "results": results
        }

    context.log("✅ Dependencies up to date")

    return {"success": True, "results": results}

async def check_outdated(context) -> List[Dict]:
    """Check for outdated packages"""
    result = await context.exec("npm outdated --json")

    if result["stdout"]:
        try:
            data = json.loads(result["stdout"])
            return [
                {
                    "name": name,
                    "current": info["current"],
                    "latest": info["latest"]
                }
                for name, info in data.items()
            ]
        except json.JSONDecodeError:
            pass

    return []

async def check_vulnerabilities(context) -> List[Dict]:
    """Check for security vulnerabilities"""
    result = await context.exec("npm audit --json")

    if result["stdout"]:
        try:
            data = json.loads(result["stdout"])
            vulnerabilities = data.get("vulnerabilities", {})

            return [
                {
                    "name": name,
                    "severity": info["severity"]
                }
                for name, info in vulnerabilities.items()
            ]
        except json.JSONDecodeError:
            pass

    return []
```

### Example 3: Commit Message Validator

```bash
#!/bin/bash
# .claude/hooks/commit-msg-validator.sh

# Validates commit messages follow conventional commits

set -e

echo "📝 Validating commit message..."

# Get commit message
COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Check format: type(scope): subject
PATTERN="^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .{1,50}"

if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
  echo "❌ Invalid commit message format"
  echo ""
  echo "Expected format:"
  echo "  type(scope): subject"
  echo ""
  echo "Types: feat, fix, docs, style, refactor, perf, test, chore"
  echo ""
  echo "Example:"
  echo "  feat(auth): add login functionality"
  echo ""
  exit 1
fi

# Check subject length
SUBJECT=$(echo "$COMMIT_MSG" | head -n1)
SUBJECT_LENGTH=${#SUBJECT}

if [ $SUBJECT_LENGTH -gt 72 ]; then
  echo "⚠️  Warning: Subject exceeds 72 characters ($SUBJECT_LENGTH)"
fi

echo "✅ Commit message valid"
exit 0
```

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: DevEx Team
**Status**: Active

---

**Navigate**: [← Back to Hooks](./README.md) | [Hook Architecture →](./hook-architecture.md) | [Hook Examples →](./hook-examples.md)

---

*Built with ❤️ for developers who love building automation*
