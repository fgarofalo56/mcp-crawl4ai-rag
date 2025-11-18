# 🔀 Git Integration Hooks

> **Complete guide to Git workflow automation with Claude Code hooks**

This document covers Git integration hooks that automate validation, testing, pattern extraction, and quality checks throughout the Git workflow.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Pre-Commit Hooks](#-pre-commit-hooks)
- [Post-Commit Hooks](#-post-commit-hooks)
- [Pre-Push Hooks](#-pre-push-hooks)
- [Git Hook Integration](#-git-hook-integration)
- [CI/CD Integration](#-cicd-integration)
- [Configuration Examples](#-configuration-examples)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)
- [Real-World Examples](#-real-world-examples)

---

## 🎯 Overview

### What are Git Hooks?

Git hooks are automation scripts triggered by Git operations:

**pre-commit**: Before commit is created
- Lint code
- Run tests
- Validate formatting
- Security scans
- Block commit on failure

**post-commit**: After commit succeeds
- Extract patterns
- Update knowledge base
- Generate changelog
- Notify team
- Non-blocking

**pre-push**: Before push to remote
- Run full test suite
- Integration tests
- Deployment validation
- Final quality gate
- Block push on failure

### Git Workflow with Hooks

```
┌─────────────────────────────────────────┐
│  Developer makes changes                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  git add .                              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  git commit                             │
│       │                                 │
│       ▼                                 │
│  ┌──────────────┐                      │
│  │  pre-commit  │  ← Validation        │
│  └──────┬───────┘                      │
│         │                               │
│    ┌────┴────┐                         │
│    │         │                          │
│    ▼         ▼                          │
│  PASS      FAIL → Commit blocked       │
│    │                                    │
│    └──→ Commit created                 │
│           │                             │
│           ▼                             │
│      ┌──────────────┐                  │
│      │ post-commit  │ ← Extract        │
│      └──────────────┘                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  git push                               │
│       │                                 │
│       ▼                                 │
│  ┌──────────────┐                      │
│  │  pre-push    │  ← Final validation  │
│  └──────┬───────┘                      │
│         │                               │
│    ┌────┴────┐                         │
│    │         │                          │
│    ▼         ▼                          │
│  PASS      FAIL → Push blocked         │
│    │                                    │
│    └──→ Push to remote                 │
└─────────────────────────────────────────┘
```

---

## 🚫 Pre-Commit Hooks

### Purpose

Pre-commit hooks prevent bad code from being committed by:
- Running linters and formatters
- Executing quick tests
- Validating code standards
- Checking for security issues
- Ensuring documentation
- Blocking commits that fail checks

### Common pre-commit Hooks

#### 1. Linting and Formatting

**Purpose**: Ensure code quality and consistent style

```javascript
// .claude/hooks/pre-commit-lint.js
module.exports = async function(context) {
  context.log('🔍 Running linters...');

  // Get staged files
  const stagedFiles = await context.exec(
    'git diff --cached --name-only --diff-filter=ACMR'
  );

  const files = stagedFiles.stdout
    .split('\n')
    .filter(f => f.trim() && (f.endsWith('.js') || f.endsWith('.ts')));

  if (files.length === 0) {
    context.log('  ⏭️  No JavaScript/TypeScript files to lint');
    return { success: true, skipped: true };
  }

  context.log(`  Processing ${files.length} files...`);

  // Run ESLint
  const lintResult = await context.exec(
    `npx eslint ${files.join(' ')} --max-warnings 0`
  );

  if (!lintResult.success) {
    context.error('❌ Linting failed:');
    context.error(lintResult.stdout);
    context.error('\n💡 Fix errors or run: npm run lint:fix\n');

    return {
      success: false,
      error: 'Linting failed',
      details: lintResult.stdout
    };
  }

  // Run Prettier
  const prettierResult = await context.exec(
    `npx prettier --check ${files.join(' ')}`
  );

  if (!prettierResult.success) {
    context.error('❌ Formatting check failed');
    context.error('\n💡 Fix formatting: npm run format\n');

    return {
      success: false,
      error: 'Formatting check failed'
    };
  }

  context.log('✅ All files pass linting and formatting');

  return {
    success: true,
    filesChecked: files.length
  };
};
```

#### 2. Testing

**Purpose**: Run quick tests before commit

```javascript
// .claude/hooks/pre-commit-test.js
module.exports = async function(context) {
  context.log('🧪 Running tests...');

  // Only run tests if source files changed
  const stagedFiles = await context.exec(
    'git diff --cached --name-only'
  );

  const hasSourceChanges = stagedFiles.stdout
    .split('\n')
    .some(f => f.startsWith('src/') || f.startsWith('lib/'));

  if (!hasSourceChanges) {
    context.log('  ⏭️  No source changes, skipping tests');
    return { success: true, skipped: true };
  }

  // Run unit tests
  context.log('  Running unit tests...');
  const testResult = await context.exec(
    'npm test -- --selectProjects=unit --bail'
  );

  if (!testResult.success) {
    context.error('❌ Tests failed:');
    context.error(testResult.stdout);
    context.error('\n💡 Fix failing tests before committing\n');

    return {
      success: false,
      error: 'Tests failed',
      output: testResult.stdout
    };
  }

  // Parse test results
  const testOutput = testResult.stdout;
  const passedMatch = testOutput.match(/(\d+) passed/);
  const passed = passedMatch ? parseInt(passedMatch[1]) : 0;

  context.log(`✅ All ${passed} tests passed`);

  return {
    success: true,
    testsPassed: passed
  };
};
```

#### 3. Security Scanning

**Purpose**: Check for security vulnerabilities

```javascript
// .claude/hooks/pre-commit-security.js
module.exports = async function(context) {
  context.log('🔒 Running security checks...');

  const issues = [];

  // Check for hardcoded secrets
  context.log('  Checking for secrets...');
  const secretPatterns = [
    /api[_-]?key\s*=\s*['"][^'"]+['"]/gi,
    /password\s*=\s*['"][^'"]+['"]/gi,
    /secret\s*=\s*['"][^'"]+['"]/gi,
    /token\s*=\s*['"][^'"]+['"]/gi
  ];

  const stagedFiles = await context.exec(
    'git diff --cached --name-only --diff-filter=ACMR'
  );

  const files = stagedFiles.stdout.split('\n').filter(f => f.trim());

  for (const file of files) {
    if (file.includes('test') || file.includes('.md')) {
      continue; // Skip test files and docs
    }

    try {
      const content = await context.read(file);

      for (const pattern of secretPatterns) {
        const matches = content.match(pattern);
        if (matches) {
          issues.push({
            file,
            type: 'potential-secret',
            matches: matches.length
          });
        }
      }
    } catch (error) {
      // File might be deleted or binary
    }
  }

  if (issues.length > 0) {
    context.error('❌ Potential secrets detected:');
    issues.forEach(issue => {
      context.error(`   ${issue.file}: ${issue.matches} potential secret(s)`);
    });
    context.error('\n💡 Use environment variables for secrets\n');

    return {
      success: false,
      error: 'Security issues detected',
      issues
    };
  }

  // Check npm audit
  if (await context.exists('package.json')) {
    context.log('  Running npm audit...');
    const auditResult = await context.exec('npm audit --audit-level=high');

    if (!auditResult.success) {
      context.warn('⚠️  Vulnerabilities found (not blocking)');
      context.warn('   Run: npm audit fix');
      // Don't block on vulnerabilities, just warn
    }
  }

  context.log('✅ No security issues detected');

  return { success: true };
};
```

#### 4. Code Quality Check

**Purpose**: Validate code complexity and standards

```javascript
// .claude/hooks/pre-commit-quality.js
module.exports = async function(context) {
  context.log('📊 Checking code quality...');

  // Get staged JavaScript/TypeScript files
  const stagedFiles = await context.exec(
    'git diff --cached --name-only --diff-filter=ACMR'
  );

  const files = stagedFiles.stdout
    .split('\n')
    .filter(f => f.match(/\.(js|ts)$/));

  if (files.length === 0) {
    return { success: true, skipped: true };
  }

  const issues = [];

  for (const file of files) {
    try {
      const content = await context.read(file);

      // Check file size
      if (content.length > 10000) {
        issues.push({
          file,
          type: 'large-file',
          message: 'File exceeds 10KB, consider splitting'
        });
      }

      // Check function length
      const functions = content.match(/function\s+\w+\s*\([^)]*\)\s*{/g) || [];
      for (const func of functions) {
        const funcContent = extractFunctionBody(content, func);
        if (funcContent.split('\n').length > 50) {
          issues.push({
            file,
            type: 'long-function',
            message: 'Function exceeds 50 lines'
          });
        }
      }

      // Check for TODO/FIXME
      const todos = content.match(/\/\/\s*(TODO|FIXME):/gi) || [];
      if (todos.length > 0) {
        issues.push({
          file,
          type: 'todo',
          message: `${todos.length} TODO/FIXME comment(s)`,
          severity: 'info'
        });
      }
    } catch (error) {
      // Skip files that can't be read
    }
  }

  // Report issues
  const errors = issues.filter(i => i.severity !== 'info');
  const warnings = issues.filter(i => i.severity === 'info');

  if (errors.length > 0) {
    context.error('❌ Code quality issues:');
    errors.forEach(issue => {
      context.error(`   ${issue.file}: ${issue.message}`);
    });
    return { success: false, error: 'Quality issues detected', issues };
  }

  if (warnings.length > 0) {
    context.warn('⚠️  Code quality warnings:');
    warnings.forEach(issue => {
      context.warn(`   ${issue.file}: ${issue.message}`);
    });
  }

  context.log('✅ Code quality checks passed');

  return { success: true, filesChecked: files.length };
};

function extractFunctionBody(content, funcSignature) {
  const start = content.indexOf(funcSignature);
  let braceCount = 0;
  let i = start;
  let body = '';

  while (i < content.length) {
    const char = content[i];
    if (char === '{') braceCount++;
    if (char === '}') {
      braceCount--;
      if (braceCount === 0) break;
    }
    if (braceCount > 0) body += char;
    i++;
  }

  return body;
}
```

---

## ✅ Post-Commit Hooks

### Purpose

Post-commit hooks enhance the Git workflow by:
- Extracting code patterns
- Updating knowledge base
- Generating changelogs
- Notifying team members
- Running async tasks
- Never blocking workflow

### Common post-commit Hooks

#### 1. Pattern Extraction

**Purpose**: Extract patterns from committed code

```javascript
// .claude/hooks/post-commit-patterns.js
module.exports = async function(context) {
  context.log('🔍 Extracting patterns from commit...');

  // Get files from last commit
  const commitFiles = await context.exec(
    'git diff-tree --no-commit-id --name-only -r HEAD'
  );

  const files = commitFiles.stdout
    .split('\n')
    .filter(f => f.match(/\.(js|ts|py|java)$/));

  if (files.length === 0) {
    context.log('  ⏭️  No code files in commit');
    return { success: true, skipped: true };
  }

  context.log(`  Analyzing ${files.length} files...`);

  const patterns = {
    imports: [],
    functions: [],
    classes: [],
    exports: []
  };

  for (const file of files) {
    try {
      const content = await context.read(file);

      // Extract imports
      const imports = content.match(/^import .+ from .+$/gm) || [];
      patterns.imports.push(...imports.map(i => ({ file, pattern: i })));

      // Extract function definitions
      const functions = content.match(/^(?:export )?(?:async )?function \w+/gm) || [];
      patterns.functions.push(...functions.map(f => ({ file, pattern: f })));

      // Extract class definitions
      const classes = content.match(/^(?:export )?class \w+/gm) || [];
      patterns.classes.push(...classes.map(c => ({ file, pattern: c })));

      // Extract exports
      const exports = content.match(/^export \{[^}]+\}/gm) || [];
      patterns.exports.push(...exports.map(e => ({ file, pattern: e })));

    } catch (error) {
      context.warn(`  Could not read ${file}`);
    }
  }

  const totalPatterns =
    patterns.imports.length +
    patterns.functions.length +
    patterns.classes.length +
    patterns.exports.length;

  if (totalPatterns > 0) {
    // Save patterns to knowledge base (async)
    savePatternsToKB(context, patterns).catch(err => {
      context.warn(`Could not save patterns: ${err.message}`);
    });

    context.log(`✅ Extracted ${totalPatterns} patterns`);
  }

  return {
    success: true,
    patternsExtracted: totalPatterns,
    patterns
  };
};

async function savePatternsToKB(context, patterns) {
  try {
    await context.callMCP('kb', 'add-patterns', {
      patterns,
      timestamp: new Date().toISOString(),
      commit: await getCommitHash(context)
    });
  } catch (error) {
    throw new Error(`KB update failed: ${error.message}`);
  }
}

async function getCommitHash(context) {
  const result = await context.exec('git rev-parse --short HEAD');
  return result.stdout.trim();
}
```

#### 2. Knowledge Base Update

**Purpose**: Update KB with commit information

```javascript
// .claude/hooks/post-commit-kb.js
module.exports = async function(context) {
  context.log('🧠 Updating knowledge base...');

  // Get commit info
  const commitHash = await context.exec('git rev-parse --short HEAD');
  const commitMessage = await context.exec('git log -1 --pretty=%B');
  const commitFiles = await context.exec(
    'git diff-tree --no-commit-id --name-only -r HEAD'
  );

  const commit = {
    hash: commitHash.stdout.trim(),
    message: commitMessage.stdout.trim(),
    files: commitFiles.stdout.split('\n').filter(f => f.trim()),
    timestamp: new Date().toISOString()
  };

  context.log(`  Commit: ${commit.hash}`);
  context.log(`  Files: ${commit.files.length}`);

  // Extract learnings from commit message
  const learnings = extractLearnings(commit.message);

  if (learnings.length > 0) {
    context.log(`  Found ${learnings.length} learnings`);

    try {
      await context.callMCP('kb', 'add-commit', {
        commit,
        learnings
      });

      context.log('✅ Knowledge base updated');
    } catch (error) {
      context.warn(`⚠️  KB update failed: ${error.message}`);
    }
  }

  return {
    success: true,
    commit,
    learnings: learnings.length
  };
};

function extractLearnings(message) {
  const learnings = [];

  // Look for learning patterns
  const patterns = [
    /learned:?\s*(.+)/gi,
    /discovered:?\s*(.+)/gi,
    /found that:?\s*(.+)/gi,
    /note:?\s*(.+)/gi
  ];

  for (const pattern of patterns) {
    const matches = message.matchAll(pattern);
    for (const match of matches) {
      learnings.push(match[1].trim());
    }
  }

  return learnings;
}
```

#### 3. Changelog Update

**Purpose**: Automatically update CHANGELOG.md

```javascript
// .claude/hooks/post-commit-changelog.js
module.exports = async function(context) {
  context.log('📝 Updating changelog...');

  // Only update on main/master branch
  const branch = await context.exec('git branch --show-current');
  if (!['main', 'master'].includes(branch.stdout.trim())) {
    context.log('  ⏭️  Not on main branch, skipping');
    return { success: true, skipped: true };
  }

  // Get commit info
  const commitHash = await context.exec('git rev-parse --short HEAD');
  const commitMessage = await context.exec('git log -1 --pretty=%B');
  const commitAuthor = await context.exec('git log -1 --pretty=%an');
  const commitDate = await context.exec('git log -1 --pretty=%ad --date=short');

  const entry = {
    hash: commitHash.stdout.trim(),
    message: commitMessage.stdout.trim(),
    author: commitAuthor.stdout.trim(),
    date: commitDate.stdout.trim()
  };

  // Parse commit type (conventional commits)
  const typeMatch = entry.message.match(/^(\w+)(\(.+\))?:/);
  const type = typeMatch ? typeMatch[1] : 'other';

  // Categorize commit
  const category = categorizeCommit(type);

  if (category === 'skip') {
    context.log('  ⏭️  Commit type does not need changelog entry');
    return { success: true, skipped: true };
  }

  // Update CHANGELOG.md
  if (await context.exists('CHANGELOG.md')) {
    try {
      const changelog = await context.read('CHANGELOG.md');
      const updatedChangelog = addChangelogEntry(changelog, entry, category);
      await context.write('CHANGELOG.md', updatedChangelog);

      context.log('✅ Changelog updated');
    } catch (error) {
      context.warn(`⚠️  Could not update changelog: ${error.message}`);
    }
  }

  return { success: true, entry };
};

function categorizeCommit(type) {
  const categories = {
    feat: 'Features',
    fix: 'Bug Fixes',
    docs: 'Documentation',
    style: 'skip',
    refactor: 'Refactoring',
    perf: 'Performance',
    test: 'skip',
    chore: 'skip'
  };

  return categories[type] || 'Other';
}

function addChangelogEntry(changelog, entry, category) {
  const lines = changelog.split('\n');

  // Find or create "Unreleased" section
  let unreleasedIndex = lines.findIndex(l => l.includes('## [Unreleased]'));

  if (unreleasedIndex === -1) {
    // Add unreleased section after title
    unreleasedIndex = 2;
    lines.splice(unreleasedIndex, 0, '', '## [Unreleased]', '');
  }

  // Find or create category section
  let categoryIndex = -1;
  for (let i = unreleasedIndex; i < lines.length; i++) {
    if (lines[i].startsWith('## ') && !lines[i].includes('Unreleased')) {
      break; // Reached next release section
    }
    if (lines[i].startsWith(`### ${category}`)) {
      categoryIndex = i;
      break;
    }
  }

  if (categoryIndex === -1) {
    // Add category section
    categoryIndex = unreleasedIndex + 2;
    lines.splice(categoryIndex, 0, `### ${category}`, '');
  }

  // Add entry
  const entryLine = `- ${entry.message} (${entry.hash})`;
  lines.splice(categoryIndex + 1, 0, entryLine);

  return lines.join('\n');
}
```

#### 4. Team Notification

**Purpose**: Notify team of commits (optional)

```javascript
// .claude/hooks/post-commit-notify.js
module.exports = async function(context) {
  // Only notify if configured
  if (!context.env.SLACK_WEBHOOK) {
    return { success: true, skipped: true };
  }

  context.log('📢 Sending team notification...');

  const commitHash = await context.exec('git rev-parse --short HEAD');
  const commitMessage = await context.exec('git log -1 --pretty=%B');
  const commitAuthor = await context.exec('git log -1 --pretty=%an');

  const notification = {
    text: `New commit by ${commitAuthor.stdout.trim()}`,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*${commitMessage.stdout.trim()}*\n\`${commitHash.stdout.trim()}\``
        }
      }
    ]
  };

  try {
    const response = await fetch(context.env.SLACK_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(notification)
    });

    if (response.ok) {
      context.log('✅ Team notified');
    } else {
      context.warn('⚠️  Notification failed');
    }
  } catch (error) {
    context.warn(`⚠️  Could not send notification: ${error.message}`);
  }

  return { success: true };
};
```

---

## 🚀 Pre-Push Hooks

### Purpose

Pre-push hooks provide final validation before code reaches remote:
- Run full test suite
- Integration tests
- Build verification
- Deployment checks
- Final quality gate
- Block push on critical failures

### Common pre-push Hooks

#### 1. Comprehensive Validation

**Purpose**: Run all validation checks

```javascript
// .claude/hooks/pre-push-validate.js
module.exports = async function(context) {
  context.log('🔍 Running comprehensive validation...\n');

  const results = {
    lint: null,
    typeCheck: null,
    unitTests: null,
    integrationTests: null
  };

  // 1. Lint
  context.log('1️⃣ Linting...');
  results.lint = await runLint(context);
  if (!results.lint.success) {
    context.error('❌ Linting failed\n');
    return { success: false, results };
  }
  context.log('   ✅ Linting passed\n');

  // 2. Type check
  context.log('2️⃣ Type checking...');
  results.typeCheck = await runTypeCheck(context);
  if (!results.typeCheck.success) {
    context.error('❌ Type checking failed\n');
    return { success: false, results };
  }
  context.log('   ✅ Type checking passed\n');

  // 3. Unit tests
  context.log('3️⃣ Unit tests...');
  results.unitTests = await runUnitTests(context);
  if (!results.unitTests.success) {
    context.error('❌ Unit tests failed\n');
    return { success: false, results };
  }
  context.log(`   ✅ ${results.unitTests.passed} tests passed\n`);

  // 4. Integration tests
  context.log('4️⃣ Integration tests...');
  results.integrationTests = await runIntegrationTests(context);
  if (!results.integrationTests.success) {
    context.error('❌ Integration tests failed\n');
    return { success: false, results };
  }
  context.log(`   ✅ ${results.integrationTests.passed} tests passed\n`);

  context.log('✅ All validation passed - ready to push!\n');

  return { success: true, results };
};

async function runLint(context) {
  const result = await context.exec('npm run lint');
  return { success: result.success };
}

async function runTypeCheck(context) {
  const result = await context.exec('npm run type-check');
  return { success: result.success };
}

async function runUnitTests(context) {
  const result = await context.exec('npm test -- --selectProjects=unit');
  const passed = result.stdout.match(/(\d+) passed/);
  return {
    success: result.success,
    passed: passed ? parseInt(passed[1]) : 0
  };
}

async function runIntegrationTests(context) {
  const result = await context.exec('npm test -- --selectProjects=integration');
  const passed = result.stdout.match(/(\d+) passed/);
  return {
    success: result.success,
    passed: passed ? parseInt(passed[1]) : 0
  };
}
```

#### 2. Build Verification

**Purpose**: Ensure code builds successfully

```javascript
// .claude/hooks/pre-push-build.js
module.exports = async function(context) {
  context.log('🏗️  Verifying build...');

  // Clean previous build
  if (await context.exists('dist')) {
    await context.exec('rm -rf dist');
  }

  // Run build
  const buildResult = await context.exec('npm run build');

  if (!buildResult.success) {
    context.error('❌ Build failed:');
    context.error(buildResult.stderr);
    context.error('\n💡 Fix build errors before pushing\n');

    return {
      success: false,
      error: 'Build failed',
      output: buildResult.stderr
    };
  }

  // Verify build output
  if (!await context.exists('dist')) {
    context.error('❌ Build output missing');
    return {
      success: false,
      error: 'Build output not found'
    };
  }

  // Check build size
  const sizeResult = await context.exec('du -sh dist');
  const size = sizeResult.stdout.trim().split('\t')[0];

  context.log(`✅ Build successful (${size})`);

  return {
    success: true,
    size
  };
};
```

#### 3. Deployment Check

**Purpose**: Validate deployment readiness

```javascript
// .claude/hooks/pre-push-deploy.js
module.exports = async function(context) {
  context.log('🚀 Checking deployment readiness...');

  const checks = [];

  // Check environment variables
  const requiredEnvVars = ['API_URL', 'API_KEY'];
  for (const envVar of requiredEnvVars) {
    if (context.env[envVar]) {
      checks.push({ name: envVar, status: 'pass' });
    } else {
      checks.push({ name: envVar, status: 'fail', error: 'Not set' });
    }
  }

  // Check configuration files
  const requiredFiles = ['.env.production', 'docker-compose.yml'];
  for (const file of requiredFiles) {
    if (await context.exists(file)) {
      checks.push({ name: file, status: 'pass' });
    } else {
      checks.push({ name: file, status: 'warn', error: 'Missing' });
    }
  }

  // Check dependencies
  if (await context.exists('package.json')) {
    const pkg = JSON.parse(await context.read('package.json'));
    if (pkg.engines && pkg.engines.node) {
      checks.push({ name: 'Node version specified', status: 'pass' });
    } else {
      checks.push({
        name: 'Node version',
        status: 'warn',
        error: 'Not specified in package.json'
      });
    }
  }

  // Report results
  const failures = checks.filter(c => c.status === 'fail');
  const warnings = checks.filter(c => c.status === 'warn');

  if (failures.length > 0) {
    context.error('❌ Deployment checks failed:');
    failures.forEach(c => {
      context.error(`   ${c.name}: ${c.error}`);
    });
    return { success: false, checks };
  }

  if (warnings.length > 0) {
    context.warn('⚠️  Deployment warnings:');
    warnings.forEach(c => {
      context.warn(`   ${c.name}: ${c.error}`);
    });
  }

  context.log('✅ Deployment checks passed');

  return { success: true, checks };
};
```

---

## 🔗 Git Hook Integration

### Linking Claude Hooks to Git

**Setup script** (`.claude/hooks/setup-git-hooks.sh`):

```bash
#!/bin/bash
# Setup Git hooks to call Claude Code hooks

HOOKS_DIR=".git/hooks"
CLAUDE_HOOKS_DIR=".claude/hooks"

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Call Claude Code pre-commit hooks

echo "Running Claude Code pre-commit hooks..."
claude run-hook pre-commit

if [ $? -ne 0 ]; then
  echo "❌ Pre-commit hooks failed"
  exit 1
fi

exit 0
EOF

# Post-commit hook
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# Call Claude Code post-commit hooks

echo "Running Claude Code post-commit hooks..."
claude run-hook post-commit

# Don't block on post-commit failures
exit 0
EOF

# Pre-push hook
cat > "$HOOKS_DIR/pre-push" << 'EOF'
#!/bin/bash
# Call Claude Code pre-push hooks

echo "Running Claude Code pre-push hooks..."
claude run-hook pre-push

if [ $? -ne 0 ]; then
  echo "❌ Pre-push hooks failed"
  exit 1
fi

exit 0
EOF

# Make hooks executable
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/post-commit"
chmod +x "$HOOKS_DIR/pre-push"

echo "✅ Git hooks configured"
```

**Run setup**:
```bash
bash .claude/hooks/setup-git-hooks.sh
```

### Bypassing Hooks

```bash
# Skip pre-commit hooks
git commit --no-verify

# Skip pre-push hooks
git push --no-verify

# Skip all hooks (use carefully!)
git -c core.hooksPath=/dev/null commit
```

---

## 🔄 CI/CD Integration

### GitHub Actions Integration

```yaml
# .github/workflows/validate.yml
name: Validate

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Install Claude Code
      run: npm install -g @anthropic-ai/claude-code

    - name: Run pre-push validation
      run: claude run-hook pre-push

    - name: Run build
      run: npm run build

    - name: Run tests
      run: npm test
```

### GitLab CI Integration

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - build
  - test

validate:
  stage: validate
  script:
    - npm ci
    - npm install -g @anthropic-ai/claude-code
    - claude run-hook pre-push

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  script:
    - npm test
```

---

## ⚙️ Configuration Examples

### Minimal Configuration

```json
{
  "hooks": {
    "pre-commit": {
      "enabled": true,
      "file": ".claude/hooks/pre-commit-lint.js"
    },
    "post-commit": {
      "enabled": true,
      "file": ".claude/hooks/post-commit-kb.js",
      "async": true
    }
  }
}
```

### Comprehensive Configuration

```json
{
  "hooks": {
    "pre-commit-lint": {
      "enabled": true,
      "file": ".claude/hooks/pre-commit-lint.js",
      "timeout": 30000,
      "priority": 100
    },
    "pre-commit-test": {
      "enabled": true,
      "file": ".claude/hooks/pre-commit-test.js",
      "timeout": 60000,
      "priority": 90
    },
    "pre-commit-security": {
      "enabled": true,
      "file": ".claude/hooks/pre-commit-security.js",
      "timeout": 30000,
      "priority": 80
    },
    "post-commit-patterns": {
      "enabled": true,
      "file": ".claude/hooks/post-commit-patterns.js",
      "async": true,
      "continueOnError": true,
      "priority": 100
    },
    "post-commit-kb": {
      "enabled": true,
      "file": ".claude/hooks/post-commit-kb.js",
      "async": true,
      "continueOnError": true,
      "priority": 90
    },
    "post-commit-changelog": {
      "enabled": "${UPDATE_CHANGELOG:true}",
      "file": ".claude/hooks/post-commit-changelog.js",
      "async": true,
      "priority": 80
    },
    "pre-push-validate": {
      "enabled": true,
      "file": ".claude/hooks/pre-push-validate.js",
      "timeout": 300000,
      "priority": 100
    },
    "pre-push-build": {
      "enabled": true,
      "file": ".claude/hooks/pre-push-build.js",
      "timeout": 120000,
      "priority": 90
    }
  }
}
```

---

## 💡 Best Practices

### Pre-Commit Hooks

✅ **DO**:
- Keep fast (<30 seconds)
- Only check staged files
- Provide clear error messages
- Suggest fixes
- Allow bypass when needed
- Run incrementally

❌ **DON'T**:
- Run full test suite
- Make network calls
- Modify files without warning
- Block on warnings
- Skip error reporting

### Post-Commit Hooks

✅ **DO**:
- Run asynchronously
- Continue on errors
- Log all actions
- Extract useful patterns
- Update documentation
- Be idempotent

❌ **DON'T**:
- Block commit completion
- Fail loudly
- Require user input
- Make destructive changes
- Assume network access

### Pre-Push Hooks

✅ **DO**:
- Run comprehensive tests
- Validate builds
- Check deployment readiness
- Allow longer timeouts
- Provide detailed feedback
- Cache when possible

❌ **DON'T**:
- Skip critical checks
- Ignore test failures
- Make assumptions
- Deploy automatically
- Modify repository

---

## 🐛 Troubleshooting

### Hook Not Running

```bash
# Check Git hooks directory
ls -la .git/hooks/

# Verify Claude Code hooks
ls -la .claude/hooks/

# Check configuration
cat .claude/settings.local.json | grep -A5 "hooks"

# Test hook manually
claude run-hook pre-commit
```

### Hook Failing

```bash
# Run with debug mode
CLAUDE_DEBUG_HOOKS=true git commit

# Test hook in isolation
node .claude/hooks/pre-commit-lint.js

# Check logs
claude logs --hooks
```

### Slow Hooks

```javascript
// Add timing
module.exports = async function(context) {
  const start = Date.now();

  await operation(context);

  const duration = Date.now() - start;
  context.log(`Took ${duration}ms`);

  return { success: true };
};
```

---

## 🌟 Real-World Examples

See [hook-examples.md](./hook-examples.md) for complete working examples of:
- Multi-language linting
- Comprehensive testing
- Security scanning
- Pattern extraction
- CI/CD integration
- Custom workflows

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: DevEx Team
**Status**: Active

---

**Navigate**: [← Back to Hooks](./README.md) | [Session Hooks →](./session-hooks.md) | [Creating Hooks →](./creating-hooks.md) | [Hook Examples →](./hook-examples.md)

---

*Built with ❤️ for developers who love automated Git workflows*
