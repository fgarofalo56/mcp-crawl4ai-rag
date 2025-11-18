# 🛠️ Development Support Commands

> **General development support and productivity commands**

Development support commands help with debugging, refactoring, code understanding, and general development tasks.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/debug-rca](#debug-rca---root-cause-analysis)
  - [/refactor-simple](#refactor-simple---quick-refactoring)
  - [/code-explain](#code-explain---explain-code)
  - [/dependencies-check](#dependencies-check---check-dependencies)
  - [/security-scan](#security-scan---security-analysis)
  - [/performance-profile](#performance-profile---performance-analysis)
- [Workflow Patterns](#-workflow-patterns)

---

## 📋 Command Reference

### /debug-rca - Root Cause Analysis

**Purpose**: Systematic debugging and root cause analysis.

**Execution Time**: 2-5 minutes

**Resources**: Medium

#### What It Does

1. **Gathers Context**
   - Error messages
   - Stack traces
   - Recent changes
   - Environment info

2. **Analyzes Issue**
   - Identifies root cause
   - Traces execution path
   - Checks related code

3. **Suggests Fixes**
   - Immediate fixes
   - Long-term solutions
   - Prevention strategies

4. **Documents Finding**
   - RCA report
   - Fix verification
   - Adds to KB

#### Usage Examples

```bash
# Analyze current error
/debug-rca

# Analyze specific error
/debug-rca "ValueError: invalid literal for int()"

# Analyze from logs
/debug-rca --logs error.log

# Focus on specific file
/debug-rca --file src/api/users.py
```

---

### /refactor-simple - Quick Refactoring

**Purpose**: Quick refactoring analysis for Python code.

**Execution Time**: 1-3 minutes

**Resources**: Medium

#### Usage Examples

```bash
# Refactor current file
/refactor-simple

# Refactor specific file
/refactor-simple src/services/user_service.py

# Focus on complexity
/refactor-simple --focus complexity

# Generate refactoring tasks
/refactor-simple --create-tasks
```

---

### /code-explain - Explain Code

**Purpose**: Explains complex code sections.

**Execution Time**: 30-90 seconds

**Resources**: Low

#### Usage Examples

```bash
# Explain selected code
/code-explain

# Explain function
/code-explain get_user_by_email

# Explain with examples
/code-explain --with-examples async_context_manager
```

---

### /dependencies-check - Check Dependencies

**Purpose**: Analyzes and validates project dependencies.

**Execution Time**: 30-60 seconds

**Resources**: Low

#### Usage Examples

```bash
# Check all dependencies
/dependencies-check

# Check for updates
/dependencies-check --check-updates

# Security vulnerabilities
/dependencies-check --security

# Analyze dependency tree
/dependencies-check --tree
```

---

### /security-scan - Security Analysis

**Purpose**: Scans code for security issues.

**Execution Time**: 1-3 minutes

**Resources**: Medium

#### Usage Examples

```bash
# Scan entire codebase
/security-scan

# Scan specific area
/security-scan src/api

# Focus on specific issues
/security-scan --focus auth

# Generate report
/security-scan --report
```

---

### /performance-profile - Performance Analysis

**Purpose**: Analyzes code for performance bottlenecks.

**Execution Time**: 2-5 minutes

**Resources**: Medium

#### Usage Examples

```bash
# Profile current code
/performance-profile

# Profile specific function
/performance-profile process_large_dataset

# With benchmarks
/performance-profile --benchmark

# Suggest optimizations
/performance-profile --optimize
```

---

**Navigate**: [← Azure Development](./azure-development.md) | [Commands Home](./README.md) | [Testing & QA →](./testing-qa.md)

---

*Develop smarter, not harder*
