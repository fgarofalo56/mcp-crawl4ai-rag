# Quality Gates

Configure automated quality checks and requirements to ensure code meets standards before completion.

## Overview

Quality gates are automated checkpoints that validate code quality, test coverage, security, and compliance before tasks are marked complete. They help maintain consistent standards and catch issues early in development.

## Basic Configuration

Add quality gates to `.claude/settings.local.json`:

```json
{
  "qualityGates": {
    "testCoverageThreshold": 80,
    "codeQualityScore": 8,
    "requireTests": true,
    "requireDocs": false,
    "securityScan": true,
    "validationChecklist": [
      "All tests pass",
      "No linting errors",
      "Documentation updated"
    ]
  }
}
```

## Quality Gate Types

### Test Coverage

Require minimum test coverage percentage:

```json
{
  "qualityGates": {
    "testCoverageThreshold": 80,
    "testCoverageType": "line",      // line, branch, function, statement
    "testCoverageExclusions": [
      "**/*.test.ts",
      "**/test/**",
      "**/__mocks__/**"
    ]
  }
}
```

**Validation command:**
```bash
npm test -- --coverage
pytest --cov=src --cov-report=term --cov-fail-under=80
```

**Example configuration by project type:**

**JavaScript/TypeScript:**
```json
{
  "qualityGates": {
    "testCoverageThreshold": 80,
    "coverageCommand": "npm test -- --coverage",
    "coverageReportPath": "coverage/coverage-summary.json"
  }
}
```

**Python:**
```json
{
  "qualityGates": {
    "testCoverageThreshold": 85,
    "coverageCommand": "pytest --cov=src --cov-report=json",
    "coverageReportPath": "coverage.json"
  }
}
```

**Go:**
```json
{
  "qualityGates": {
    "testCoverageThreshold": 75,
    "coverageCommand": "go test ./... -coverprofile=coverage.out",
    "coverageReportPath": "coverage.out"
  }
}
```

### Code Quality Score

Require minimum code quality score (1-10 scale):

```json
{
  "qualityGates": {
    "codeQualityScore": 8,
    "qualityMetrics": [
      "complexity",
      "maintainability",
      "duplication",
      "documentation"
    ],
    "complexityThreshold": 10,
    "duplicationThreshold": 3
  }
}
```

**Validation tools:**
- **JavaScript/TypeScript:** ESLint, SonarQube
- **Python:** Pylint, Radon, SonarQube
- **Go:** golangci-lint
- **Java:** SonarQube, Checkstyle

**Example ESLint integration:**
```json
{
  "qualityGates": {
    "codeQualityScore": 8,
    "lintCommand": "npm run lint",
    "lintErrorThreshold": 0,
    "lintWarningThreshold": 5
  }
}
```

### Required Tests

Enforce test creation for new code:

```json
{
  "qualityGates": {
    "requireTests": true,
    "testPatterns": {
      "src/**/*.ts": "src/**/*.test.ts",
      "src/**/*.py": "tests/**/test_*.py"
    },
    "minimumTestsPerFile": 3
  }
}
```

**Test types to require:**
```json
{
  "qualityGates": {
    "requireTests": {
      "unit": true,
      "integration": true,
      "e2e": false
    }
  }
}
```

### Documentation Requirements

Require documentation for new features:

```json
{
  "qualityGates": {
    "requireDocs": true,
    "docPatterns": {
      "newFeatures": "docs/features/*.md",
      "apiChanges": "docs/api/*.md",
      "publicFunctions": "inline"
    },
    "docCoverageThreshold": 90
  }
}
```

**Documentation validation:**
```json
{
  "qualityGates": {
    "requireDocs": true,
    "docValidation": {
      "checkExamples": true,
      "checkLinks": true,
      "checkSpelling": true,
      "requireCodeExamples": true
    }
  }
}
```

### Security Scanning

Require security scans to pass:

```json
{
  "qualityGates": {
    "securityScan": true,
    "securityTools": [
      "npm audit",
      "snyk test",
      "bandit"
    ],
    "securityThresholds": {
      "critical": 0,
      "high": 0,
      "medium": 5,
      "low": 20
    }
  }
}
```

**Tool-specific configurations:**

**npm audit:**
```json
{
  "qualityGates": {
    "securityScan": {
      "command": "npm audit --audit-level=moderate",
      "failOnVulnerabilities": true
    }
  }
}
```

**Snyk:**
```json
{
  "qualityGates": {
    "securityScan": {
      "command": "snyk test --severity-threshold=high",
      "failOnVulnerabilities": true
    }
  }
}
```

**Python Bandit:**
```json
{
  "qualityGates": {
    "securityScan": {
      "command": "bandit -r src/ -ll",
      "failOnVulnerabilities": true
    }
  }
}
```

### Validation Checklist

Custom checklist items that must be completed:

```json
{
  "qualityGates": {
    "validationChecklist": [
      "All tests pass",
      "No linting errors",
      "Code reviewed",
      "Documentation updated",
      "Breaking changes documented",
      "Migration guide created (if needed)",
      "Performance benchmarks run",
      "Security review completed"
    ]
  }
}
```

**Interactive checklist:**
```json
{
  "qualityGates": {
    "validationChecklist": [
      {
        "item": "All tests pass",
        "automated": true,
        "command": "npm test"
      },
      {
        "item": "Code reviewed",
        "automated": false,
        "requiredFor": "production"
      },
      {
        "item": "Performance benchmarks run",
        "automated": true,
        "command": "npm run benchmark",
        "requiredFor": "performance-critical"
      }
    ]
  }
}
```

## Comprehensive Examples

### Python Data Science Project

```json
{
  "qualityGates": {
    "testCoverageThreshold": 85,
    "coverageCommand": "pytest --cov=src --cov-report=term --cov-report=json",
    "requireTests": {
      "unit": true,
      "integration": true
    },
    "codeQualityScore": 8,
    "lintCommand": "ruff check src/ && black --check src/ && mypy src/",
    "validationChecklist": [
      "All tests pass",
      "Type hints complete",
      "Black formatting applied",
      "Ruff linting passes",
      "Jupyter notebooks validated",
      "Data validation tests included"
    ],
    "customValidation": {
      "dataValidation": {
        "command": "python scripts/validate_data_schema.py",
        "required": true
      },
      "notebookTests": {
        "command": "pytest --nbmake notebooks/",
        "required": true
      }
    }
  }
}
```

### TypeScript API Project

```json
{
  "qualityGates": {
    "testCoverageThreshold": 80,
    "coverageCommand": "npm test -- --coverage",
    "requireTests": {
      "unit": true,
      "integration": true,
      "e2e": true
    },
    "codeQualityScore": 8,
    "lintCommand": "npm run lint && npm run type-check",
    "securityScan": {
      "command": "npm audit --audit-level=moderate && snyk test",
      "failOnVulnerabilities": true
    },
    "validationChecklist": [
      "All tests pass",
      "TypeScript compilation successful",
      "ESLint passes",
      "API documentation updated",
      "OpenAPI spec validated",
      "Database migrations created",
      "Environment variables documented"
    ],
    "performanceGates": {
      "responseTime": {
        "p95": 200,
        "p99": 500
      },
      "throughput": {
        "min": 1000
      }
    }
  }
}
```

### React Frontend Project

```json
{
  "qualityGates": {
    "testCoverageThreshold": 75,
    "coverageCommand": "npm test -- --coverage",
    "requireTests": {
      "unit": true,
      "integration": true,
      "e2e": false
    },
    "codeQualityScore": 8,
    "lintCommand": "npm run lint",
    "validationChecklist": [
      "All tests pass",
      "Component tests included",
      "Accessibility checks pass",
      "Bundle size under limit",
      "No console errors/warnings",
      "Storybook updated"
    ],
    "accessibilityGates": {
      "command": "npm run test:a11y",
      "wcagLevel": "AA",
      "failOnViolations": true
    },
    "bundleSize": {
      "maxSize": "500KB",
      "maxChunkSize": "200KB"
    }
  }
}
```

### Azure Infrastructure Project

```json
{
  "qualityGates": {
    "validationChecklist": [
      "Terraform plan successful",
      "Terraform validate passes",
      "Security scan completed",
      "Cost estimation reviewed",
      "RBAC permissions verified",
      "Naming conventions followed",
      "Tags applied correctly",
      "Backup strategy documented"
    ],
    "securityScan": {
      "command": "tfsec . && checkov -d .",
      "failOnVulnerabilities": true
    },
    "customValidation": {
      "terraformValidate": {
        "command": "terraform validate",
        "required": true
      },
      "terraformPlan": {
        "command": "terraform plan -detailed-exitcode",
        "required": true
      },
      "costEstimation": {
        "command": "infracost breakdown --path .",
        "required": true,
        "maxMonthlyCost": 1000
      }
    }
  }
}
```

## Pre-Commit Integration

Run quality gates before commits:

```json
{
  "qualityGates": {
    "preCommitHooks": {
      "enabled": true,
      "hooks": [
        {
          "name": "lint",
          "command": "npm run lint",
          "failOnError": true
        },
        {
          "name": "test",
          "command": "npm test",
          "failOnError": true
        },
        {
          "name": "type-check",
          "command": "npm run type-check",
          "failOnError": true
        }
      ]
    }
  },
  "hooks": {
    "preCommit": [
      "npm run lint",
      "npm test"
    ]
  }
}
```

**Install pre-commit hooks:**
```bash
# Using husky
npm install --save-dev husky
npx husky install
npx husky add .husky/pre-commit "npm run lint && npm test"

# Using pre-commit (Python)
pip install pre-commit
pre-commit install
```

## CI/CD Integration

Configure gates for continuous integration:

```json
{
  "qualityGates": {
    "ci": {
      "required": true,
      "stages": [
        {
          "name": "build",
          "command": "npm run build",
          "failOnError": true
        },
        {
          "name": "test",
          "command": "npm test -- --coverage",
          "failOnError": true,
          "coverageThreshold": 80
        },
        {
          "name": "lint",
          "command": "npm run lint",
          "failOnError": true
        },
        {
          "name": "security",
          "command": "npm audit",
          "failOnError": true
        }
      ]
    }
  }
}
```

**GitHub Actions integration:**
```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Run quality gates
        run: npm run quality-gates
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Custom Quality Gates

Define custom validation logic:

```json
{
  "qualityGates": {
    "customGates": [
      {
        "name": "api-compatibility",
        "command": "npm run check-api-compatibility",
        "failOnError": true,
        "description": "Ensure API changes are backward compatible"
      },
      {
        "name": "performance-regression",
        "command": "npm run benchmark -- --compare",
        "failOnError": true,
        "threshold": {
          "maxRegression": 10
        }
      },
      {
        "name": "database-migrations",
        "command": "npm run check-migrations",
        "failOnError": true,
        "requiredFor": ["database-changes"]
      }
    ]
  }
}
```

## Environment-Specific Gates

Different requirements for different environments:

```json
{
  "qualityGates": {
    "development": {
      "testCoverageThreshold": 70,
      "requireDocs": false,
      "securityScan": false
    },
    "staging": {
      "testCoverageThreshold": 80,
      "requireDocs": true,
      "securityScan": true
    },
    "production": {
      "testCoverageThreshold": 90,
      "requireDocs": true,
      "securityScan": true,
      "requireCodeReview": true,
      "requireApprovals": 2
    }
  },
  "activeEnvironment": "development"
}
```

## Quality Gate Reporting

Generate quality reports:

```json
{
  "qualityGates": {
    "reporting": {
      "enabled": true,
      "format": "html",
      "outputPath": "reports/quality-gates.html",
      "includeMetrics": [
        "coverage",
        "complexity",
        "duplication",
        "security",
        "performance"
      ],
      "notifications": {
        "onFailure": {
          "email": ["team@example.com"],
          "slack": "#dev-alerts"
        }
      }
    }
  }
}
```

## Gate Exemptions

Allow exemptions with justification:

```json
{
  "qualityGates": {
    "exemptions": {
      "allowExemptions": true,
      "requireJustification": true,
      "requireApproval": true,
      "approvers": ["tech-lead", "security-team"],
      "exemptionLog": ".claude/exemptions.json"
    }
  }
}
```

**Request exemption:**
```json
{
  "gate": "testCoverage",
  "justification": "Legacy code being refactored incrementally",
  "approvedBy": "tech-lead",
  "expiresAt": "2025-12-31"
}
```

## Progressive Quality Gates

Gradually increase requirements:

```json
{
  "qualityGates": {
    "progressive": {
      "enabled": true,
      "milestones": [
        {
          "date": "2025-01-01",
          "testCoverageThreshold": 60
        },
        {
          "date": "2025-04-01",
          "testCoverageThreshold": 70
        },
        {
          "date": "2025-07-01",
          "testCoverageThreshold": 80
        }
      ]
    }
  }
}
```

## Quality Metrics Dashboard

Track quality metrics over time:

```json
{
  "qualityGates": {
    "metrics": {
      "enabled": true,
      "storage": "metrics.db",
      "retention": "90 days",
      "track": [
        "coverage",
        "quality-score",
        "security-vulnerabilities",
        "build-time",
        "test-time"
      ],
      "dashboard": {
        "enabled": true,
        "port": 3000
      }
    }
  }
}
```

## Troubleshooting

### Gate Failing Unexpectedly

**Check gate configuration:**
```bash
claude config show | grep -A 20 "qualityGates"
```

**Run gate manually:**
```bash
npm test -- --coverage
npm run lint
npm audit
```

**View detailed logs:**
```bash
cat .claude/logs/quality-gates.log
```

### Coverage Not Meeting Threshold

**Identify uncovered code:**
```bash
npm test -- --coverage --verbose
```

**Exclude non-critical files:**
```json
{
  "qualityGates": {
    "testCoverageExclusions": [
      "**/*.test.ts",
      "**/mocks/**",
      "**/fixtures/**"
    ]
  }
}
```

### Security Scan Too Strict

**Adjust thresholds:**
```json
{
  "qualityGates": {
    "securityThresholds": {
      "critical": 0,
      "high": 1,
      "medium": 10
    }
  }
}
```

**Suppress false positives:**
```json
{
  "qualityGates": {
    "securityScan": {
      "suppressions": [
        "CVE-2024-12345"
      ]
    }
  }
}
```

## Best Practices

### 1. Start Lenient, Tighten Gradually
Begin with achievable thresholds and increase over time.

### 2. Automate Everything Possible
Use automated checks instead of manual checklists.

### 3. Make Gates Fast
Slow gates discourage development velocity.

### 4. Provide Clear Feedback
Gates should explain what failed and how to fix it.

### 5. Environment-Specific Requirements
Different standards for dev, staging, production.

### 6. Track Metrics Over Time
Monitor quality trends, not just point-in-time checks.

### 7. Allow Reasonable Exemptions
Not all code needs 100% coverage.

### 8. Integrate with CI/CD
Run gates automatically on every commit/PR.

### 9. Team Agreement
Quality gates should be team decisions, not mandates.

### 10. Review and Adjust
Regularly review gate effectiveness and adjust.

## Example Complete Configuration

```json
{
  "qualityGates": {
    "testCoverageThreshold": 80,
    "coverageCommand": "npm test -- --coverage",
    "testCoverageExclusions": [
      "**/*.test.ts",
      "**/test/**"
    ],
    "codeQualityScore": 8,
    "lintCommand": "npm run lint",
    "requireTests": {
      "unit": true,
      "integration": true
    },
    "requireDocs": true,
    "securityScan": {
      "command": "npm audit --audit-level=moderate",
      "failOnVulnerabilities": true,
      "thresholds": {
        "critical": 0,
        "high": 0,
        "medium": 5
      }
    },
    "validationChecklist": [
      "All tests pass",
      "No linting errors",
      "TypeScript compilation successful",
      "Documentation updated",
      "Breaking changes documented"
    ],
    "preCommitHooks": {
      "enabled": true,
      "hooks": [
        {"name": "lint", "command": "npm run lint"},
        {"name": "test", "command": "npm test"}
      ]
    },
    "ci": {
      "required": true,
      "stages": [
        {"name": "build", "command": "npm run build"},
        {"name": "test", "command": "npm test"},
        {"name": "security", "command": "npm audit"}
      ]
    },
    "reporting": {
      "enabled": true,
      "format": "html",
      "outputPath": "reports/quality.html"
    }
  }
}
```

## Next Steps

- [Permissions Configuration](./permissions.md) - Control what Claude Code can do
- [MCP Servers](./mcp-servers.md) - Configure external integrations
- [Advanced Configuration](./advanced-config.md) - Advanced features
- [Best Practices](../best-practices/README.md) - Development workflows
