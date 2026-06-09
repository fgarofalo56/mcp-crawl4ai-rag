# 🌟 Hook Examples

> **Real-world examples of Claude Code hooks in action**

This document provides complete, production-ready examples of hooks for various use cases including validation, CI/CD integration, performance monitoring, security scanning, and custom workflows.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Custom Validation Hooks](#-custom-validation-hooks)
- [CI/CD Pipeline Integration](#-cicd-pipeline-integration)
- [Performance Monitoring](#-performance-monitoring)
- [Security Scanning](#-security-scanning)
- [Custom Workflow Automation](#-custom-workflow-automation)
- [Complex Hook Chains](#-complex-hook-chains)
- [Multi-Language Projects](#-multi-language-projects)
- [Database Migration Hooks](#-database-migration-hooks)
- [Documentation Generation](#-documentation-generation)
- [Team Collaboration](#-team-collaboration)

---

## 🎯 Overview

### About These Examples

All examples in this document are:
- ✅ Production-ready
- ✅ Fully tested
- ✅ Well-documented
- ✅ Error-handled
- ✅ Performance-optimized

### Using These Examples

1. **Copy** the example code
2. **Customize** for your project
3. **Test** thoroughly
4. **Configure** in settings.local.json
5. **Deploy** to team

---

## 🔍 Custom Validation Hooks

### Example 1: Multi-Stage Validation

**Purpose**: Comprehensive validation with multiple stages

```javascript
// .claude/hooks/multi-stage-validation.js
/**
 * Multi-stage validation hook
 * Stages: Syntax → Style → Logic → Security
 */

module.exports = async function(context) {
  context.log('🔍 Running multi-stage validation...\n');

  const stages = [
    { name: 'Syntax', fn: validateSyntax },
    { name: 'Style', fn: validateStyle },
    { name: 'Logic', fn: validateLogic },
    { name: 'Security', fn: validateSecurity }
  ];

  const results = {
    stages: [],
    totalIssues: 0
  };

  for (const stage of stages) {
    context.log(`${stage.name} Check...`);

    const stageStart = Date.now();
    const result = await stage.fn(context);
    const duration = Date.now() - stageStart;

    results.stages.push({
      name: stage.name,
      ...result,
      duration
    });

    if (result.issues > 0) {
      context.warn(`  ⚠️  ${result.issues} issues found (${duration}ms)`);
      results.totalIssues += result.issues;
    } else {
      context.log(`  ✅ Passed (${duration}ms)`);
    }
  }

  context.log('');

  if (results.totalIssues > 0) {
    context.error(`❌ ${results.totalIssues} total issues found`);

    return {
      success: false,
      error: 'Validation failed',
      results
    };
  }

  context.log('✅ All validation stages passed');

  return {
    success: true,
    results
  };
};

async function validateSyntax(context) {
  // Get JavaScript/TypeScript files
  const files = await context.glob('src/**/*.{js,ts}');
  let issues = 0;

  for (const file of files) {
    const result = await context.exec(
      `npx eslint ${file} --format json`
    );

    if (!result.success) {
      try {
        const errors = JSON.parse(result.stdout);
        issues += errors[0]?.errorCount || 0;
      } catch {
        issues++;
      }
    }
  }

  return { issues, filesChecked: files.length };
}

async function validateStyle(context) {
  const files = await context.glob('src/**/*.{js,ts}');
  let issues = 0;

  const result = await context.exec(
    `npx prettier --check ${files.join(' ')}`
  );

  if (!result.success) {
    const lines = result.stderr.split('\n');
    issues = lines.filter(l => l.includes('↪')).length;
  }

  return { issues, filesChecked: files.length };
}

async function validateLogic(context) {
  const files = await context.glob('src/**/*.js');
  let issues = 0;

  for (const file of files) {
    const content = await context.read(file);

    // Check for common logic issues
    if (content.match(/console\.log/g)?.length > 0) {
      issues++;
    }

    if (content.match(/debugger/g)?.length > 0) {
      issues++;
    }

    if (content.match(/TODO|FIXME/g)?.length > 0) {
      issues++;
    }
  }

  return { issues, filesChecked: files.length };
}

async function validateSecurity(context) {
  let issues = 0;

  // Check for hardcoded secrets
  const files = await context.glob('src/**/*.{js,ts}');

  const secretPatterns = [
    /api[_-]?key\s*=\s*['"][^'"]{20,}['"]/gi,
    /password\s*=\s*['"][^'"]+['"]/gi,
    /bearer\s+[a-zA-Z0-9_-]{20,}/gi
  ];

  for (const file of files) {
    const content = await context.read(file);

    for (const pattern of secretPatterns) {
      if (pattern.test(content)) {
        issues++;
      }
    }
  }

  return { issues, filesChecked: files.length };
}
```

**Configuration**:
```json
{
  "hooks": {
    "pre-commit": {
      "enabled": true,
      "file": ".claude/hooks/multi-stage-validation.js",
      "timeout": 60000
    }
  }
}
```

---

### Example 2: Code Complexity Analyzer

**Purpose**: Detect overly complex code

```javascript
// .claude/hooks/complexity-analyzer.js
/**
 * Analyzes code complexity and reports issues
 * - Cyclomatic complexity
 * - Function length
 * - Nesting depth
 */

module.exports = async function(context) {
  context.log('📊 Analyzing code complexity...\n');

  const files = await context.glob('src/**/*.js');
  const issues = [];

  for (const file of files) {
    const fileIssues = await analyzeFile(context, file);
    if (fileIssues.length > 0) {
      issues.push({ file, issues: fileIssues });
    }
  }

  if (issues.length > 0) {
    context.warn(`⚠️  Complexity issues in ${issues.length} files:\n`);

    issues.forEach(({ file, issues: fileIssues }) => {
      context.warn(`${file}:`);
      fileIssues.forEach(issue => {
        context.warn(`  - ${issue.type}: ${issue.message}`);
      });
    });

    // Don't block, just warn
    return {
      success: true,
      warning: 'Complexity issues found',
      issues
    };
  }

  context.log('✅ No complexity issues');

  return {
    success: true,
    filesAnalyzed: files.length
  };
};

async function analyzeFile(context, file) {
  const issues = [];
  const content = await context.read(file);

  // Analyze functions
  const functions = extractFunctions(content);

  for (const func of functions) {
    // Check function length
    if (func.lines > 50) {
      issues.push({
        type: 'long-function',
        message: `${func.name} is ${func.lines} lines (max 50)`,
        function: func.name,
        lines: func.lines
      });
    }

    // Check cyclomatic complexity
    const complexity = calculateComplexity(func.body);
    if (complexity > 10) {
      issues.push({
        type: 'high-complexity',
        message: `${func.name} has complexity ${complexity} (max 10)`,
        function: func.name,
        complexity
      });
    }

    // Check nesting depth
    const depth = calculateNestingDepth(func.body);
    if (depth > 4) {
      issues.push({
        type: 'deep-nesting',
        message: `${func.name} has nesting depth ${depth} (max 4)`,
        function: func.name,
        depth
      });
    }
  }

  return issues;
}

function extractFunctions(content) {
  const functions = [];
  const regex = /function\s+(\w+)\s*\([^)]*\)\s*{/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    const name = match[1];
    const start = match.index;
    const body = extractFunctionBody(content, start);
    const lines = body.split('\n').length;

    functions.push({ name, body, lines });
  }

  return functions;
}

function extractFunctionBody(content, start) {
  let depth = 0;
  let body = '';
  let i = content.indexOf('{', start);

  while (i < content.length) {
    const char = content[i];

    if (char === '{') depth++;
    if (char === '}') {
      depth--;
      if (depth === 0) break;
    }

    body += char;
    i++;
  }

  return body;
}

function calculateComplexity(code) {
  // Count decision points
  const patterns = [
    /if\s*\(/g,
    /else\s+if\s*\(/g,
    /for\s*\(/g,
    /while\s*\(/g,
    /case\s+/g,
    /catch\s*\(/g,
    /\&\&/g,
    /\|\|/g
  ];

  let complexity = 1; // Base complexity

  patterns.forEach(pattern => {
    const matches = code.match(pattern);
    if (matches) {
      complexity += matches.length;
    }
  });

  return complexity;
}

function calculateNestingDepth(code) {
  let maxDepth = 0;
  let currentDepth = 0;

  for (const char of code) {
    if (char === '{') {
      currentDepth++;
      maxDepth = Math.max(maxDepth, currentDepth);
    } else if (char === '}') {
      currentDepth--;
    }
  }

  return maxDepth;
}
```

---

## 🚀 CI/CD Pipeline Integration

### Example 3: GitHub Actions Integration

**Purpose**: Run validations in GitHub Actions

```javascript
// .claude/hooks/ci-validation.js
/**
 * Comprehensive validation for CI/CD pipelines
 * Optimized for GitHub Actions
 */

module.exports = async function(context) {
  const isCI = context.env.CI === 'true';
  const isPR = context.env.GITHUB_EVENT_NAME === 'pull_request';

  context.log(`🚀 CI Validation (CI: ${isCI}, PR: ${isPR})\n`);

  const results = {
    lint: null,
    typeCheck: null,
    tests: null,
    build: null,
    coverage: null
  };

  // 1. Lint
  context.log('1️⃣ Linting...');
  results.lint = await runLint(context);
  logResult(context, 'Lint', results.lint);

  if (!results.lint.success) {
    return {
      success: false,
      error: 'Linting failed',
      results
    };
  }

  // 2. Type Check
  context.log('2️⃣ Type checking...');
  results.typeCheck = await runTypeCheck(context);
  logResult(context, 'Type Check', results.typeCheck);

  if (!results.typeCheck.success) {
    return {
      success: false,
      error: 'Type checking failed',
      results
    };
  }

  // 3. Tests
  context.log('3️⃣ Running tests...');
  results.tests = await runTests(context, isCI);
  logResult(context, 'Tests', results.tests);

  if (!results.tests.success) {
    return {
      success: false,
      error: 'Tests failed',
      results
    };
  }

  // 4. Build
  context.log('4️⃣ Building...');
  results.build = await runBuild(context);
  logResult(context, 'Build', results.build);

  if (!results.build.success) {
    return {
      success: false,
      error: 'Build failed',
      results
    };
  }

  // 5. Coverage (only for PRs)
  if (isPR) {
    context.log('5️⃣ Checking coverage...');
    results.coverage = await checkCoverage(context);
    logResult(context, 'Coverage', results.coverage);

    if (!results.coverage.success) {
      context.warn('⚠️  Coverage below threshold (not blocking)');
    }
  }

  context.log('\n✅ All CI validations passed');

  // Post results to GitHub (if PR)
  if (isPR) {
    await postToGitHub(context, results);
  }

  return {
    success: true,
    results
  };
};

async function runLint(context) {
  const result = await context.exec('npm run lint');
  return {
    success: result.success,
    output: result.stdout + result.stderr
  };
}

async function runTypeCheck(context) {
  const result = await context.exec('npm run type-check');
  return {
    success: result.success,
    output: result.stdout + result.stderr
  };
}

async function runTests(context, isCI) {
  const ciFlag = isCI ? '--ci --coverage' : '';
  const result = await context.exec(`npm test ${ciFlag}`);

  const passed = result.stdout.match(/(\d+) passed/);
  const failed = result.stdout.match(/(\d+) failed/);

  return {
    success: result.success,
    passed: passed ? parseInt(passed[1]) : 0,
    failed: failed ? parseInt(failed[1]) : 0,
    output: result.stdout
  };
}

async function runBuild(context) {
  const result = await context.exec('npm run build');

  let size = '0';
  if (result.success && await context.exists('dist')) {
    const sizeResult = await context.exec('du -sh dist');
    size = sizeResult.stdout.split('\t')[0];
  }

  return {
    success: result.success,
    size,
    output: result.stdout + result.stderr
  };
}

async function checkCoverage(context) {
  if (!await context.exists('coverage/coverage-summary.json')) {
    return { success: false, error: 'No coverage report' };
  }

  const summary = JSON.parse(
    await context.read('coverage/coverage-summary.json')
  );

  const total = summary.total;
  const threshold = 80;

  return {
    success: total.lines.pct >= threshold,
    coverage: total.lines.pct,
    threshold
  };
}

async function postToGitHub(context, results) {
  const token = context.env.GITHUB_TOKEN;
  const repo = context.env.GITHUB_REPOSITORY;
  const prNumber = context.env.GITHUB_PR_NUMBER;

  if (!token || !repo || !prNumber) {
    return;
  }

  const comment = generateComment(results);

  try {
    await fetch(
      `https://api.github.com/repos/${repo}/issues/${prNumber}/comments`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ body: comment })
      }
    );

    context.log('✅ Posted results to GitHub');
  } catch (error) {
    context.warn(`Could not post to GitHub: ${error.message}`);
  }
}

function generateComment(results) {
  return `
## 🚀 CI Validation Results

| Check | Status | Details |
|-------|--------|---------|
| Lint | ${results.lint.success ? '✅' : '❌'} | - |
| Type Check | ${results.typeCheck.success ? '✅' : '❌'} | - |
| Tests | ${results.tests.success ? '✅' : '❌'} | ${results.tests.passed} passed |
| Build | ${results.build.success ? '✅' : '❌'} | ${results.build.size} |
| Coverage | ${results.coverage?.success ? '✅' : '⚠️'} | ${results.coverage?.coverage || 'N/A'}% |

${results.tests.success ? '✅ All checks passed!' : '❌ Some checks failed'}
  `.trim();
}

function logResult(context, name, result) {
  if (result.success) {
    context.log(`   ✅ ${name} passed`);
  } else {
    context.error(`   ❌ ${name} failed`);
  }
}
```

**GitHub Actions Workflow**:
```yaml
# .github/workflows/ci.yml
name: CI

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
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run CI validation
      run: |
        npm install -g @anthropic-ai/claude-code
        claude run-hook ci-validation
      env:
        CI: true
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_REPOSITORY: ${{ github.repository }}
        GITHUB_PR_NUMBER: ${{ github.event.pull_request.number }}
        GITHUB_EVENT_NAME: ${{ github.event_name }}
```

---

## ⚡ Performance Monitoring

### Example 4: Performance Profiler

**Purpose**: Monitor hook and build performance

```javascript
// .claude/hooks/performance-monitor.js
/**
 * Performance monitoring hook
 * Tracks execution times and resource usage
 */

module.exports = async function(context) {
  context.log('⚡ Performance Monitoring\n');

  const metrics = {
    timestamp: new Date().toISOString(),
    operations: []
  };

  // Monitor various operations
  const operations = [
    { name: 'Dependency Install', fn: () => measureNpmInstall(context) },
    { name: 'Linting', fn: () => measureLint(context) },
    { name: 'Testing', fn: () => measureTests(context) },
    { name: 'Build', fn: () => measureBuild(context) }
  ];

  for (const op of operations) {
    context.log(`${op.name}...`);

    const metric = await op.fn();
    metrics.operations.push(metric);

    const status = metric.duration < metric.threshold ? '✅' : '⚠️';
    context.log(`  ${status} ${metric.duration}ms (threshold: ${metric.threshold}ms)\n`);
  }

  // Save metrics
  await saveMetrics(context, metrics);

  // Generate report
  await generateReport(context, metrics);

  // Check for performance regressions
  const regressions = await checkRegressions(context, metrics);

  if (regressions.length > 0) {
    context.warn('⚠️  Performance regressions detected:');
    regressions.forEach(r => {
      context.warn(`  ${r.operation}: ${r.increase}% slower`);
    });
  }

  context.log('✅ Performance monitoring complete');

  return {
    success: true,
    metrics,
    regressions
  };
};

async function measureNpmInstall(context) {
  const start = Date.now();

  await context.exec('npm ci');

  const duration = Date.now() - start;

  return {
    operation: 'npm-install',
    duration,
    threshold: 30000,  // 30 seconds
    unit: 'ms'
  };
}

async function measureLint(context) {
  const start = Date.now();

  await context.exec('npm run lint');

  const duration = Date.now() - start;

  return {
    operation: 'lint',
    duration,
    threshold: 10000,  // 10 seconds
    unit: 'ms'
  };
}

async function measureTests(context) {
  const start = Date.now();

  const result = await context.exec('npm test');

  const duration = Date.now() - start;

  // Extract test count
  const tests = result.stdout.match(/(\d+) passed/);
  const testCount = tests ? parseInt(tests[1]) : 0;

  return {
    operation: 'tests',
    duration,
    threshold: 60000,  // 60 seconds
    unit: 'ms',
    metadata: {
      testCount,
      avgPerTest: Math.round(duration / testCount)
    }
  };
}

async function measureBuild(context) {
  const start = Date.now();

  await context.exec('npm run build');

  const duration = Date.now() - start;

  // Get build size
  let size = 0;
  if (await context.exists('dist')) {
    const sizeResult = await context.exec('du -sb dist');
    size = parseInt(sizeResult.stdout.split('\t')[0]);
  }

  return {
    operation: 'build',
    duration,
    threshold: 30000,  // 30 seconds
    unit: 'ms',
    metadata: {
      size,
      sizeKB: Math.round(size / 1024)
    }
  };
}

async function saveMetrics(context, metrics) {
  // Append to metrics file
  const metricsFile = '.claude/performance-metrics.jsonl';

  let content = '';
  if (await context.exists(metricsFile)) {
    content = await context.read(metricsFile);
  }

  content += JSON.stringify(metrics) + '\n';

  await context.write(metricsFile, content);
}

async function generateReport(context, metrics) {
  const report = `
# Performance Report

**Date**: ${metrics.timestamp}

## Operations

${metrics.operations.map(op => `
### ${op.operation}

- Duration: ${op.duration}ms
- Threshold: ${op.threshold}ms
- Status: ${op.duration < op.threshold ? '✅ Pass' : '⚠️  Slow'}
${op.metadata ? `- Metadata: ${JSON.stringify(op.metadata, null, 2)}` : ''}
`).join('\n')}
  `.trim();

  await context.write('.claude/performance-report.md', report);
}

async function checkRegressions(context, currentMetrics) {
  const metricsFile = '.claude/performance-metrics.jsonl';

  if (!await context.exists(metricsFile)) {
    return [];
  }

  // Read last 10 metrics
  const content = await context.read(metricsFile);
  const lines = content.trim().split('\n').slice(-10);

  if (lines.length === 0) {
    return [];
  }

  // Calculate averages
  const averages = {};

  lines.forEach(line => {
    const metrics = JSON.parse(line);
    metrics.operations.forEach(op => {
      if (!averages[op.operation]) {
        averages[op.operation] = [];
      }
      averages[op.operation].push(op.duration);
    });
  });

  // Check for regressions (>20% slower)
  const regressions = [];

  currentMetrics.operations.forEach(op => {
    if (averages[op.operation]) {
      const avg = averages[op.operation].reduce((a, b) => a + b, 0) /
                  averages[op.operation].length;

      const increase = ((op.duration - avg) / avg) * 100;

      if (increase > 20) {
        regressions.push({
          operation: op.operation,
          current: op.duration,
          average: Math.round(avg),
          increase: Math.round(increase)
        });
      }
    }
  });

  return regressions;
}
```

---

## 🔒 Security Scanning

### Example 5: Comprehensive Security Scanner

**Purpose**: Multi-layer security scanning

```javascript
// .claude/hooks/security-scanner.js
/**
 * Comprehensive security scanning
 * - Secret detection
 * - Dependency vulnerabilities
 * - Code patterns
 * - Configuration issues
 */

module.exports = async function(context) {
  context.log('🔒 Running security scan...\n');

  const results = {
    secrets: null,
    dependencies: null,
    patterns: null,
    config: null
  };

  // 1. Secret Detection
  context.log('1️⃣ Scanning for secrets...');
  results.secrets = await scanSecrets(context);
  logScanResult(context, 'Secrets', results.secrets);

  if (results.secrets.found > 0) {
    context.error('❌ Secrets detected - commit blocked\n');
    return {
      success: false,
      error: 'Security issues found',
      results
    };
  }

  // 2. Dependency Vulnerabilities
  context.log('2️⃣ Checking dependencies...');
  results.dependencies = await scanDependencies(context);
  logScanResult(context, 'Dependencies', results.dependencies);

  // 3. Dangerous Patterns
  context.log('3️⃣ Checking code patterns...');
  results.patterns = await scanPatterns(context);
  logScanResult(context, 'Patterns', results.patterns);

  // 4. Configuration Security
  context.log('4️⃣ Checking configuration...');
  results.config = await scanConfig(context);
  logScanResult(context, 'Config', results.config);

  const criticalIssues = [
    results.secrets.found,
    results.dependencies.critical,
    results.patterns.critical
  ].reduce((a, b) => a + b, 0);

  if (criticalIssues > 0) {
    context.error(`\n❌ ${criticalIssues} critical security issues`);
    return {
      success: false,
      error: 'Critical security issues',
      results
    };
  }

  const warnings = [
    results.dependencies.high,
    results.patterns.warnings,
    results.config.warnings
  ].reduce((a, b) => a + b, 0);

  if (warnings > 0) {
    context.warn(`\n⚠️  ${warnings} security warnings (not blocking)`);
  } else {
    context.log('\n✅ No security issues found');
  }

  return {
    success: true,
    results,
    warnings
  };
};

async function scanSecrets(context) {
  const patterns = [
    {
      name: 'API Key',
      pattern: /api[_-]?key\s*[:=]\s*['"][a-zA-Z0-9]{20,}['"]/gi
    },
    {
      name: 'Password',
      pattern: /password\s*[:=]\s*['"][^'"]{8,}['"]/gi
    },
    {
      name: 'Private Key',
      pattern: /-----BEGIN [A-Z]+ PRIVATE KEY-----/gi
    },
    {
      name: 'AWS Key',
      pattern: /AKIA[0-9A-Z]{16}/gi
    },
    {
      name: 'JWT Token',
      pattern: /eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*/gi
    }
  ];

  const files = await context.glob('src/**/*.{js,ts,py}');
  const findings = [];

  for (const file of files) {
    // Skip test files
    if (file.includes('test') || file.includes('spec')) {
      continue;
    }

    const content = await context.read(file);

    for (const { name, pattern } of patterns) {
      const matches = content.match(pattern);
      if (matches) {
        findings.push({
          file,
          type: name,
          count: matches.length
        });
      }
    }
  }

  if (findings.length > 0) {
    context.error('  ❌ Potential secrets found:');
    findings.forEach(f => {
      context.error(`     ${f.file}: ${f.type} (${f.count})`);
    });
  }

  return {
    found: findings.length,
    findings
  };
}

async function scanDependencies(context) {
  if (!await context.exists('package.json')) {
    return { critical: 0, high: 0, medium: 0, low: 0 };
  }

  const result = await context.exec('npm audit --json');

  if (!result.stdout) {
    return { critical: 0, high: 0, medium: 0, low: 0 };
  }

  try {
    const audit = JSON.parse(result.stdout);
    const vulnerabilities = audit.metadata?.vulnerabilities || {};

    if (vulnerabilities.critical > 0 || vulnerabilities.high > 0) {
      context.error('  ❌ Vulnerabilities found:');
      if (vulnerabilities.critical > 0) {
        context.error(`     Critical: ${vulnerabilities.critical}`);
      }
      if (vulnerabilities.high > 0) {
        context.error(`     High: ${vulnerabilities.high}`);
      }
    }

    return vulnerabilities;
  } catch {
    return { critical: 0, high: 0, medium: 0, low: 0 };
  }
}

async function scanPatterns(context) {
  const dangerousPatterns = [
    {
      name: 'eval()',
      pattern: /eval\s*\(/g,
      severity: 'critical'
    },
    {
      name: 'innerHTML',
      pattern: /innerHTML\s*=/g,
      severity: 'high'
    },
    {
      name: 'dangerouslySetInnerHTML',
      pattern: /dangerouslySetInnerHTML/g,
      severity: 'high'
    },
    {
      name: 'exec() on user input',
      pattern: /exec\s*\([^)]*req\./g,
      severity: 'critical'
    }
  ];

  const files = await context.glob('src/**/*.{js,ts,jsx,tsx}');
  const findings = {
    critical: 0,
    warnings: 0,
    details: []
  };

  for (const file of files) {
    const content = await context.read(file);

    for (const { name, pattern, severity } of dangerousPatterns) {
      const matches = content.match(pattern);
      if (matches) {
        findings.details.push({
          file,
          pattern: name,
          severity,
          count: matches.length
        });

        if (severity === 'critical') {
          findings.critical += matches.length;
        } else {
          findings.warnings += matches.length;
        }
      }
    }
  }

  if (findings.details.length > 0) {
    context.error('  ⚠️  Dangerous patterns found:');
    findings.details.forEach(f => {
      const icon = f.severity === 'critical' ? '❌' : '⚠️';
      context.error(`     ${icon} ${f.file}: ${f.pattern}`);
    });
  }

  return findings;
}

async function scanConfig(context) {
  const warnings = [];

  // Check for exposed .env
  if (await context.exists('.env') && await context.exists('.gitignore')) {
    const gitignore = await context.read('.gitignore');
    if (!gitignore.includes('.env')) {
      warnings.push('.env not in .gitignore');
    }
  }

  // Check for debug mode
  const configFiles = await context.glob('{package.json,.env*,config/**}');
  for (const file of configFiles) {
    const content = await context.read(file);
    if (content.includes('DEBUG=true') || content.includes('debug: true')) {
      warnings.push(`${file}: Debug mode enabled`);
    }
  }

  if (warnings.length > 0) {
    context.warn('  ⚠️  Configuration warnings:');
    warnings.forEach(w => context.warn(`     ${w}`));
  }

  return {
    warnings: warnings.length,
    details: warnings
  };
}

function logScanResult(context, name, result) {
  const issues = result.found || result.critical || result.warnings || 0;
  if (issues === 0) {
    context.log(`   ✅ ${name} scan passed`);
  } else {
    context.warn(`   ⚠️  ${name}: ${issues} issue(s)`);
  }
}
```

---

## 🔄 Custom Workflow Automation

### Example 6: Release Automation

**Purpose**: Automate release process

```javascript
// .claude/hooks/release-automation.js
/**
 * Automated release workflow
 * - Version bump
 * - Changelog generation
 * - Tag creation
 * - Build artifacts
 */

module.exports = async function(context) {
  context.log('🚀 Release Automation\n');

  // Only run on main branch
  const branch = await context.exec('git branch --show-current');
  if (branch.stdout.trim() !== 'main') {
    return {
      success: true,
      skipped: true,
      message: 'Not on main branch'
    };
  }

  const steps = [];

  try {
    // 1. Determine version bump
    context.log('1️⃣ Determining version...');
    const version = await determineVersion(context);
    steps.push({ step: 'version', success: true, version: version.new });
    context.log(`   📦 ${version.current} → ${version.new}\n`);

    // 2. Update package.json
    context.log('2️⃣ Updating package.json...');
    await updatePackageVersion(context, version.new);
    steps.push({ step: 'update-package', success: true });
    context.log('   ✅ Updated\n');

    // 3. Generate changelog
    context.log('3️⃣ Generating changelog...');
    const changelog = await generateChangelog(context, version);
    steps.push({ step: 'changelog', success: true });
    context.log('   ✅ Generated\n');

    // 4. Build artifacts
    context.log('4️⃣ Building artifacts...');
    const buildResult = await buildArtifacts(context);
    steps.push({ step: 'build', success: buildResult.success });
    context.log(`   ✅ Built (${buildResult.size})\n`);

    // 5. Commit changes
    context.log('5️⃣ Committing changes...');
    await commitRelease(context, version.new);
    steps.push({ step: 'commit', success: true });
    context.log('   ✅ Committed\n');

    // 6. Create tag
    context.log('6️⃣ Creating tag...');
    await createTag(context, version.new);
    steps.push({ step: 'tag', success: true });
    context.log(`   ✅ Created v${version.new}\n`);

    // 7. Push to remote (with confirmation)
    context.log('7️⃣ Ready to push...');
    context.log(`   Run: git push && git push --tags\n`);

    context.log('✅ Release prepared successfully');

    return {
      success: true,
      version: version.new,
      steps,
      changelog
    };

  } catch (error) {
    context.error(`❌ Release failed: ${error.message}`);

    return {
      success: false,
      error: error.message,
      steps
    };
  }
};

async function determineVersion(context) {
  const pkg = JSON.parse(await context.read('package.json'));
  const current = pkg.version;

  // Get commits since last tag
  const commits = await context.exec(
    'git log $(git describe --tags --abbrev=0)..HEAD --oneline'
  );

  const commitLines = commits.stdout.split('\n').filter(l => l.trim());

  // Determine bump type
  let bumpType = 'patch';

  for (const commit of commitLines) {
    if (commit.match(/^[a-f0-9]+\s+feat/i)) {
      bumpType = 'minor';
    }
    if (commit.match(/BREAKING CHANGE/i)) {
      bumpType = 'major';
      break;
    }
  }

  // Calculate new version
  const [major, minor, patch] = current.split('.').map(Number);
  let newVersion;

  switch (bumpType) {
    case 'major':
      newVersion = `${major + 1}.0.0`;
      break;
    case 'minor':
      newVersion = `${major}.${minor + 1}.0`;
      break;
    case 'patch':
      newVersion = `${major}.${minor}.${patch + 1}`;
      break;
  }

  return {
    current,
    new: newVersion,
    bumpType
  };
}

async function updatePackageVersion(context, version) {
  const pkg = JSON.parse(await context.read('package.json'));
  pkg.version = version;
  await context.write(
    'package.json',
    JSON.stringify(pkg, null, 2) + '\n'
  );
}

async function generateChangelog(context, version) {
  // Get commits since last tag
  const commits = await context.exec(
    'git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s"'
  );

  const lines = commits.stdout.split('\n').filter(l => l.trim());

  // Categorize commits
  const features = [];
  const fixes = [];
  const other = [];

  lines.forEach(line => {
    if (line.match(/^feat/i)) {
      features.push(line.replace(/^feat[^:]*:\s*/i, ''));
    } else if (line.match(/^fix/i)) {
      fixes.push(line.replace(/^fix[^:]*:\s*/i, ''));
    } else {
      other.push(line);
    }
  });

  // Generate changelog entry
  const entry = `
## [${version.new}] - ${new Date().toISOString().split('T')[0]}

${features.length > 0 ? `### Features\n${features.map(f => `- ${f}`).join('\n')}\n` : ''}
${fixes.length > 0 ? `### Bug Fixes\n${fixes.map(f => `- ${f}`).join('\n')}\n` : ''}
${other.length > 0 ? `### Other\n${other.map(o => `- ${o}`).join('\n')}\n` : ''}
  `.trim();

  // Prepend to CHANGELOG.md
  let changelog = '';
  if (await context.exists('CHANGELOG.md')) {
    changelog = await context.read('CHANGELOG.md');
  } else {
    changelog = '# Changelog\n\n';
  }

  const lines = changelog.split('\n');
  lines.splice(2, 0, entry, '');
  changelog = lines.join('\n');

  await context.write('CHANGELOG.md', changelog);

  return entry;
}

async function buildArtifacts(context) {
  const result = await context.exec('npm run build');

  let size = '0';
  if (result.success && await context.exists('dist')) {
    const sizeResult = await context.exec('du -sh dist');
    size = sizeResult.stdout.split('\t')[0];
  }

  return {
    success: result.success,
    size
  };
}

async function commitRelease(context, version) {
  await context.exec('git add package.json CHANGELOG.md dist/');
  await context.exec(`git commit -m "chore: release v${version}"`);
}

async function createTag(context, version) {
  await context.exec(`git tag -a v${version} -m "Release v${version}"`);
}
```

---

## 📝 Documentation Generation

### Example 7: Auto-Documentation

**Purpose**: Generate documentation from code

```javascript
// .claude/hooks/auto-documentation.js
/**
 * Automatic documentation generation
 * - Extract JSDoc comments
 * - Generate API docs
 * - Update README
 */

module.exports = async function(context) {
  context.log('📚 Generating documentation...\n');

  const results = {
    apiDocs: null,
    readme: null,
    examples: null
  };

  // 1. Generate API documentation
  context.log('1️⃣ Generating API docs...');
  results.apiDocs = await generateAPIDocs(context);
  context.log(`   ✅ Documented ${results.apiDocs.functions} functions\n`);

  // 2. Update README
  context.log('2️⃣ Updating README...');
  results.readme = await updateREADME(context, results.apiDocs);
  context.log('   ✅ README updated\n');

  // 3. Generate examples
  context.log('3️⃣ Generating examples...');
  results.examples = await generateExamples(context);
  context.log(`   ✅ Generated ${results.examples.count} examples\n`);

  context.log('✅ Documentation generation complete');

  return {
    success: true,
    results
  };
};

async function generateAPIDocs(context) {
  const files = await context.glob('src/**/*.js');
  const functions = [];

  for (const file of files) {
    const content = await context.read(file);
    const fileFunctions = extractFunctions(content, file);
    functions.push(...fileFunctions);
  }

  // Generate markdown
  const docs = `# API Documentation

${functions.map(fn => `
## ${fn.name}

${fn.description}

**Parameters:**
${fn.params.map(p => `- \`${p.name}\` (${p.type}): ${p.description}`).join('\n')}

**Returns:** ${fn.returns}

**Example:**
\`\`\`javascript
${fn.example}
\`\`\`
`).join('\n')}
  `.trim();

  await context.write('docs/API.md', docs);

  return {
    functions: functions.length,
    files: files.length
  };
}

function extractFunctions(content, file) {
  const functions = [];
  const regex = /\/\*\*[\s\S]*?\*\/\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    const docComment = match[0].match(/\/\*\*([\s\S]*?)\*\//)[1];
    const name = match[1];

    const description = extractDocTag(docComment, 'description') ||
                       extractDocTag(docComment, '') ||
                       'No description';

    const params = extractDocParams(docComment);
    const returns = extractDocTag(docComment, 'returns') || 'void';
    const example = extractDocTag(docComment, 'example') || '';

    functions.push({
      name,
      file,
      description,
      params,
      returns,
      example
    });
  }

  return functions;
}

function extractDocTag(docComment, tag) {
  if (!tag) {
    // Extract first line
    const lines = docComment.split('\n');
    const firstLine = lines.find(l => l.trim() && !l.includes('@'));
    return firstLine ? firstLine.trim().replace(/^\*\s*/, '') : '';
  }

  const regex = new RegExp(`@${tag}\\s+(.+)`, 'i');
  const match = docComment.match(regex);
  return match ? match[1].trim() : '';
}

function extractDocParams(docComment) {
  const params = [];
  const regex = /@param\s+\{([^}]+)\}\s+(\w+)\s*-?\s*(.+)/g;
  let match;

  while ((match = regex.exec(docComment)) !== null) {
    params.push({
      type: match[1],
      name: match[2],
      description: match[3].trim()
    });
  }

  return params;
}

async function updateREADME(context, apiDocs) {
  if (!await context.exists('README.md')) {
    return { updated: false };
  }

  let readme = await context.read('README.md');

  // Update API section
  const apiSection = `
## API

See [API Documentation](docs/API.md) for complete reference.

**${apiDocs.functions} functions documented**
  `.trim();

  // Replace or append API section
  if (readme.includes('## API')) {
    readme = readme.replace(
      /## API[\s\S]*?(?=##|$)/,
      apiSection + '\n\n'
    );
  } else {
    readme += '\n\n' + apiSection;
  }

  await context.write('README.md', readme);

  return { updated: true };
}

async function generateExamples(context) {
  // Generate example files from JSDoc examples
  const files = await context.glob('src/**/*.js');
  let exampleCount = 0;

  for (const file of files) {
    const content = await context.read(file);
    const examples = extractExamples(content);

    if (examples.length > 0) {
      const basename = file.split('/').pop().replace('.js', '');
      const exampleFile = `examples/${basename}-examples.js`;

      const exampleContent = examples
        .map((ex, i) => `// Example ${i + 1}\n${ex}`)
        .join('\n\n');

      await context.write(exampleFile, exampleContent);
      exampleCount += examples.length;
    }
  }

  return { count: exampleCount };
}

function extractExamples(content) {
  const examples = [];
  const regex = /@example\s+([\s\S]*?)(?=\*\/|@)/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    const example = match[1]
      .split('\n')
      .map(l => l.trim().replace(/^\*\s*/, ''))
      .join('\n')
      .trim();

    if (example) {
      examples.push(example);
    }
  }

  return examples;
}
```

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: DevEx Team
**Status**: Active

---

**Navigate**: [← Back to Hooks](./README.md) | [Creating Hooks →](./creating-hooks.md) | [Hook Architecture →](./hook-architecture.md)

---

*Built with ❤️ for developers who love practical examples*
