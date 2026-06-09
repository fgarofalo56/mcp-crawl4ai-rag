# ✅ Testing & QA Commands

> **Testing, quality assurance, and code review commands**

Testing and QA commands help ensure code quality through automated testing, code reviews, and quality gates.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/test-generate](#test-generate---generate-tests)
  - [/test-run](#test-run---run-test-suite)
  - [/coverage-check](#coverage-check---check-test-coverage)
  - [/review-staged](#review-staged---review-staged-changes)
  - [/review-general](#review-general---comprehensive-code-review)
  - [/lint-fix](#lint-fix---run-linters-and-fix)
- [Workflow Patterns](#-workflow-patterns)

---

## 📋 Command Reference

### /test-generate - Generate Tests

**Purpose**: Generates unit tests for code.

**Execution Time**: 1-3 minutes

**Resources**: Medium

#### What It Does

1. **Analyzes Code**
   - Identifies functions/classes
   - Determines test cases needed
   - Notes edge cases

2. **Generates Tests**
   - Creates test files
   - Writes test functions
   - Includes fixtures
   - Adds assertions

3. **Validates Tests**
   - Runs generated tests
   - Checks coverage
   - Fixes failures

#### Usage Examples

```bash
# Generate tests for file
/test-generate src/services/user_service.py

# Generate tests for function
/test-generate get_user_by_email

# Generate with specific framework
/test-generate --framework pytest src/api/auth.py

# Generate integration tests
/test-generate --type integration src/api/
```

---

### /test-run - Run Test Suite

**Purpose**: Runs project test suite.

**Execution Time**: 30 seconds - 5 minutes

**Resources**: Medium

#### Usage Examples

```bash
# Run all tests
/test-run

# Run specific test file
/test-run tests/test_user_service.py

# Run with coverage
/test-run --coverage

# Run only failed tests
/test-run --failed

# Run in watch mode
/test-run --watch
```

---

### /coverage-check - Check Test Coverage

**Purpose**: Analyzes test coverage and identifies gaps.

**Execution Time**: 30-60 seconds

**Resources**: Low-Medium

#### Usage Examples

```bash
# Check overall coverage
/coverage-check

# Check specific module
/coverage-check src/api

# Show uncovered lines
/coverage-check --show-uncovered

# Generate HTML report
/coverage-check --html
```

---

### /review-staged - Review Staged Changes

**Purpose**: Reviews staged changes before commit.

**Execution Time**: 1-3 minutes

**Resources**: Medium

#### What It Does

1. **Analyzes Staged Changes**
   - Gets git diff
   - Identifies modified functions
   - Notes new code

2. **Reviews Quality**
   - Code patterns
   - Best practices
   - Security issues
   - Performance concerns

3. **Checks Tests**
   - Test coverage for changes
   - New tests needed
   - Edge cases covered

4. **Provides Feedback**
   - Issues found
   - Suggestions
   - Approval status

#### Usage Examples

```bash
# Review staged changes
/review-staged

# Review with specific focus
/review-staged --focus security

# Review Python/Pydantic patterns
/review-staged --patterns python

# Quick review
/review-staged --quick
```

---

### /review-general - Comprehensive Code Review

**Purpose**: Comprehensive code review covering quality, patterns, security, and testing.

**Execution Time**: 2-5 minutes

**Resources**: Medium

#### Usage Examples

```bash
# Review entire codebase
/review-general

# Review specific directory
/review-general src/api

# Focus on specific aspects
/review-general --focus architecture

# Generate report
/review-general --report review-$(date +%Y%m%d).md
```

---

### /lint-fix - Run Linters and Fix

**Purpose**: Runs linters and auto-fixes issues.

**Execution Time**: 30-90 seconds

**Resources**: Low

#### Usage Examples

```bash
# Lint and fix all
/lint-fix

# Lint specific files
/lint-fix src/api/*.py

# Check only (no fix)
/lint-fix --check

# Specific linter
/lint-fix --linter ruff
```

---

## 🔄 Workflow Patterns

### Test-Driven Development (TDD)

```bash
# 1. Generate test stubs
/test-generate new_feature

# 2. Run tests (should fail)
/test-run --failed

# 3. Implement feature
# ... code ...

# 4. Run tests again
/test-run

# 5. Check coverage
/coverage-check
```

### Pre-Commit Review

```bash
# 1. Review staged changes
/review-staged

# 2. Run tests
/test-run

# 3. Check coverage
/coverage-check

# 4. Lint and fix
/lint-fix

# 5. Commit
/smart-commit
```

---

**Navigate**: [← Development Support](./development-support.md) | [Commands Home](./README.md) | [Git Operations →](./git-operations.md)

---

*Quality is not an act, it is a habit*
