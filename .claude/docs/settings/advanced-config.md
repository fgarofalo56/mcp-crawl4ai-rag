# Advanced Configuration

Advanced settings for team collaboration, custom integrations, performance optimization, and complex workflows.

## Overview

This guide covers advanced configuration topics including team setups, custom MCP server integration, hook systems, logging, monitoring, performance tuning, and multi-project configurations.

## Team Configuration

### Shared Team Settings

**settings.shared.json** (committed to git):
```json
{
  "version": "1.0",
  "teamName": "Product Engineering",
  "permissions": {
    "bash": {
      "allow": [
        "npm test",
        "npm run build",
        "git status",
        "git diff*"
      ],
      "ask": [
        "git push*",
        "npm publish"
      ],
      "deny": [
        "rm -rf node_modules",
        "git push --force*"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask"
    }
  },
  "qualityGates": {
    "testCoverageThreshold": 80,
    "requireTests": true,
    "validationChecklist": [
      "All tests pass",
      "Code reviewed",
      "Documentation updated"
    ]
  },
  "outputStyle": "concise",
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true
    }
  }
}
```

**settings.local.json** (personal, gitignored):
```json
{
  "extends": "./settings.shared.json",
  "outputStyle": "terse",
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["~/my-tools/custom-server.js"],
      "enabled": true
    }
  }
}
```

**.gitignore:**
```
.claude/settings.local.json
.claude/logs/
.claude/cache/
.env
```

### Team Roles

Configure role-based settings:

```json
{
  "roles": {
    "developer": {
      "permissions": {
        "bash": {
          "allow": ["npm test", "npm run build"]
        }
      },
      "qualityGates": {
        "testCoverageThreshold": 80
      }
    },
    "senior-developer": {
      "extends": "developer",
      "permissions": {
        "bash": {
          "ask": ["npm publish"]
        }
      }
    },
    "tech-lead": {
      "extends": "senior-developer",
      "permissions": {
        "bash": {
          "allow": ["git push*"]
        }
      },
      "qualityGates": {
        "testCoverageThreshold": 90
      }
    }
  },
  "activeRole": "developer"
}
```

### Command Library

Share custom commands across team:

**.claude/commands/team-commit.md:**
```markdown
# Team Commit Command

Commit with team standards:
1. Run all tests
2. Run linting
3. Check coverage meets threshold
4. Create conventional commit message
5. Push to remote
```

**.claude/commands/code-review.md:**
```markdown
# Code Review Command

Perform comprehensive code review:
1. Check code quality score
2. Verify test coverage
3. Run security scan
4. Check for common anti-patterns
5. Verify documentation
6. Generate review summary
```

### Agent Library

Share custom agents:

**.claude/agents/architecture-reviewer.md:**
```markdown
# Architecture Reviewer

You are an expert software architect reviewing system design.

Focus on:
- System design patterns
- Scalability concerns
- Security architecture
- Performance bottlenecks
- Technology choices

Provide detailed recommendations.
```

## Custom MCP Server Integration

### Creating Custom MCP Server

**custom-server.js:**
```javascript
const { MCPServer } = require('@modelcontextprotocol/sdk');

class CustomServer extends MCPServer {
  constructor() {
    super({
      name: 'custom-server',
      version: '1.0.0',
      description: 'Custom MCP server for team tools'
    });

    this.registerTools();
  }

  registerTools() {
    // Register custom tool
    this.registerTool({
      name: 'analyze_codebase',
      description: 'Analyze entire codebase for patterns',
      inputSchema: {
        type: 'object',
        properties: {
          path: {
            type: 'string',
            description: 'Path to analyze'
          },
          pattern: {
            type: 'string',
            description: 'Pattern to search for'
          }
        },
        required: ['path']
      },
      handler: async (input) => {
        // Custom analysis logic
        return {
          results: await this.analyzeCode(input.path, input.pattern)
        };
      }
    });

    // Register resource provider
    this.registerResource({
      uri: 'custom://team-standards',
      name: 'Team Coding Standards',
      description: 'Team coding standards and best practices',
      mimeType: 'text/markdown',
      handler: async () => {
        return {
          content: await this.loadTeamStandards()
        };
      }
    });
  }

  async analyzeCode(path, pattern) {
    // Implementation
  }

  async loadTeamStandards() {
    // Implementation
  }
}

const server = new CustomServer();
server.start();
```

**Configuration:**
```json
{
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["tools/custom-server.js"],
      "enabled": true,
      "env": {
        "TEAM_STANDARDS_PATH": "${TEAM_STANDARDS_PATH}"
      },
      "healthCheck": {
        "enabled": true,
        "interval": 60000
      }
    }
  }
}
```

### MCP Server with Database

**database-server.js:**
```javascript
const { MCPServer } = require('@modelcontextprotocol/sdk');
const { Pool } = require('pg');

class DatabaseServer extends MCPServer {
  constructor() {
    super({
      name: 'database-server',
      version: '1.0.0'
    });

    this.pool = new Pool({
      host: process.env.DB_HOST,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD
    });

    this.registerTools();
  }

  registerTools() {
    this.registerTool({
      name: 'query_database',
      description: 'Execute SQL query',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string' },
          params: { type: 'array' }
        },
        required: ['query']
      },
      handler: async (input) => {
        const result = await this.pool.query(input.query, input.params);
        return { rows: result.rows };
      }
    });
  }
}
```

**Configuration:**
```json
{
  "mcpServers": {
    "database-server": {
      "command": "node",
      "args": ["tools/database-server.js"],
      "env": {
        "DB_HOST": "${DB_HOST}",
        "DB_NAME": "${DB_NAME}",
        "DB_USER": "${DB_USER}",
        "DB_PASSWORD": "${DB_PASSWORD}"
      },
      "pool": {
        "min": 2,
        "max": 10,
        "idleTimeout": 30000
      }
    }
  }
}
```

## Hook System

### Available Hooks

Configure hooks for automated workflows:

```json
{
  "hooks": {
    "preCommit": ["npm run lint", "npm test"],
    "postCommit": ["npm run update-changelog"],
    "preTest": ["npm run clean"],
    "postTest": ["npm run coverage-report"],
    "preBuild": ["npm run clean"],
    "postBuild": ["npm run analyze-bundle"],
    "preDeployment": ["npm run test:e2e"],
    "postDeployment": ["npm run smoke-test"]
  }
}
```

### Conditional Hooks

Run hooks based on conditions:

```json
{
  "hooks": {
    "preCommit": [
      {
        "command": "npm test",
        "when": {
          "filesChanged": ["src/**/*.ts"]
        }
      },
      {
        "command": "npm run lint:css",
        "when": {
          "filesChanged": ["**/*.css", "**/*.scss"]
        }
      }
    ]
  }
}
```

### Parallel Hooks

Run hooks in parallel:

```json
{
  "hooks": {
    "preCommit": {
      "parallel": true,
      "hooks": [
        "npm run lint",
        "npm run type-check",
        "npm run test:unit"
      ]
    }
  }
}
```

### Hook Timeout

Configure timeouts:

```json
{
  "hooks": {
    "preCommit": [
      {
        "command": "npm test",
        "timeout": 30000,
        "retries": 2
      }
    ]
  }
}
```

### Custom Hook Scripts

**scripts/pre-commit.sh:**
```bash
#!/bin/bash

# Run linting
echo "Running linter..."
npm run lint || exit 1

# Run tests
echo "Running tests..."
npm test || exit 1

# Check coverage
echo "Checking coverage..."
npm run coverage-check || exit 1

echo "Pre-commit checks passed!"
```

**Configuration:**
```json
{
  "hooks": {
    "preCommit": ["bash scripts/pre-commit.sh"]
  }
}
```

## Logging and Monitoring

### Comprehensive Logging

```json
{
  "logging": {
    "level": "debug",
    "outputPath": ".claude/logs",
    "includeTimestamps": true,
    "rotateDaily": true,
    "maxFileSize": "10MB",
    "maxFiles": 7,
    "separate": {
      "errors": ".claude/logs/errors.log",
      "bash": ".claude/logs/bash.log",
      "mcp": ".claude/logs/mcp.log",
      "performance": ".claude/logs/performance.log"
    },
    "format": {
      "type": "json",
      "pretty": false
    }
  }
}
```

### Audit Logging

```json
{
  "logging": {
    "audit": {
      "enabled": true,
      "outputPath": ".claude/logs/audit.log",
      "events": [
        "bash-command",
        "file-write",
        "file-delete",
        "git-push",
        "deployment"
      ],
      "includeContext": true,
      "retention": "90 days"
    }
  }
}
```

### Performance Monitoring

```json
{
  "monitoring": {
    "performance": {
      "enabled": true,
      "metrics": [
        "response-time",
        "mcp-server-latency",
        "bash-execution-time",
        "context-window-usage"
      ],
      "outputPath": ".claude/metrics",
      "aggregation": {
        "interval": "1 hour",
        "retention": "30 days"
      }
    }
  }
}
```

### Error Tracking

```json
{
  "logging": {
    "errorTracking": {
      "enabled": true,
      "service": "sentry",
      "dsn": "${SENTRY_DSN}",
      "environment": "production",
      "sampleRate": 1.0,
      "includeStackTrace": true
    }
  }
}
```

### Alerting

```json
{
  "monitoring": {
    "alerts": {
      "enabled": true,
      "channels": {
        "slack": {
          "webhookUrl": "${SLACK_WEBHOOK}",
          "channel": "#dev-alerts"
        },
        "email": {
          "recipients": ["team@example.com"],
          "smtp": {
            "host": "${SMTP_HOST}",
            "port": 587,
            "auth": {
              "user": "${SMTP_USER}",
              "pass": "${SMTP_PASSWORD}"
            }
          }
        }
      },
      "rules": [
        {
          "name": "High error rate",
          "condition": "errorRate > 10",
          "severity": "high",
          "channels": ["slack", "email"]
        },
        {
          "name": "MCP server down",
          "condition": "mcpServerHealth == false",
          "severity": "critical",
          "channels": ["slack", "email"]
        }
      ]
    }
  }
}
```

## Performance Optimization

### Caching Configuration

```json
{
  "performance": {
    "cache": {
      "enabled": true,
      "storage": "disk",
      "path": ".claude/cache",
      "ttl": {
        "default": 900000,
        "mcpResponses": 1800000,
        "fileReads": 300000,
        "webFetch": 3600000
      },
      "maxSize": "500MB",
      "compression": true,
      "evictionPolicy": "lru"
    }
  }
}
```

### Parallel Execution

```json
{
  "performance": {
    "parallelExecution": {
      "enabled": true,
      "maxConcurrentTasks": 5,
      "maxConcurrentBashCommands": 3,
      "maxConcurrentMCPCalls": 10
    }
  }
}
```

### Resource Limits

```json
{
  "performance": {
    "limits": {
      "maxMemory": "2GB",
      "maxContextSize": 200000,
      "maxFileSize": "10MB",
      "maxConcurrentSessions": 5,
      "timeout": {
        "bash": 120000,
        "mcp": 30000,
        "fileOperation": 10000
      }
    }
  }
}
```

### Optimization Strategies

```json
{
  "performance": {
    "optimizations": {
      "lazyLoadMCPServers": true,
      "preloadFrequentFiles": [
        "package.json",
        "tsconfig.json",
        ".env.example"
      ],
      "indexCodebase": {
        "enabled": true,
        "interval": "1 hour",
        "exclude": ["node_modules", ".git"]
      },
      "compressLogs": true,
      "batchFileReads": true
    }
  }
}
```

## Multi-Project Setup

### Workspace Configuration

**.claude/workspace.json:**
```json
{
  "version": "1.0",
  "workspace": {
    "name": "Monorepo",
    "projects": [
      {
        "name": "frontend",
        "path": "packages/frontend",
        "settingsPath": "packages/frontend/.claude/settings.local.json"
      },
      {
        "name": "backend",
        "path": "packages/backend",
        "settingsPath": "packages/backend/.claude/settings.local.json"
      },
      {
        "name": "shared",
        "path": "packages/shared",
        "settingsPath": "packages/shared/.claude/settings.local.json"
      }
    ],
    "sharedSettings": ".claude/settings.shared.json"
  }
}
```

### Project-Specific Settings

**packages/frontend/.claude/settings.local.json:**
```json
{
  "extends": "../../.claude/settings.shared.json",
  "permissions": {
    "bash": {
      "allow": [
        "npm test",
        "npm run build",
        "npm run dev"
      ]
    }
  },
  "mcpServers": {
    "playwright": {
      "enabled": true
    }
  }
}
```

**packages/backend/.claude/settings.local.json:**
```json
{
  "extends": "../../.claude/settings.shared.json",
  "permissions": {
    "bash": {
      "allow": [
        "npm test",
        "npm run build",
        "docker-compose up -d"
      ]
    }
  },
  "mcpServers": {
    "database-server": {
      "enabled": true
    },
    "azure-mcp": {
      "enabled": true
    }
  }
}
```

### Cross-Project Commands

**.claude/commands/build-all.md:**
```markdown
# Build All Projects

Build all projects in workspace:
1. Build shared package
2. Build backend
3. Build frontend
4. Run integration tests
```

## Environment Management

### Multi-Environment Configuration

```json
{
  "environments": {
    "development": {
      "mcpServers": {
        "azure-mcp": {
          "env": {
            "AZURE_SUBSCRIPTION_ID": "${DEV_SUBSCRIPTION_ID}"
          }
        }
      },
      "logging": {
        "level": "debug"
      },
      "qualityGates": {
        "testCoverageThreshold": 70
      }
    },
    "staging": {
      "mcpServers": {
        "azure-mcp": {
          "env": {
            "AZURE_SUBSCRIPTION_ID": "${STAGING_SUBSCRIPTION_ID}"
          }
        }
      },
      "logging": {
        "level": "info"
      },
      "qualityGates": {
        "testCoverageThreshold": 80
      }
    },
    "production": {
      "mcpServers": {
        "azure-mcp": {
          "env": {
            "AZURE_SUBSCRIPTION_ID": "${PROD_SUBSCRIPTION_ID}"
          }
        }
      },
      "logging": {
        "level": "warn"
      },
      "qualityGates": {
        "testCoverageThreshold": 90,
        "requireCodeReview": true
      }
    }
  },
  "activeEnvironment": "development"
}
```

### Environment Switching

```bash
# Switch environment
claude env use staging

# View current environment
claude env current

# List available environments
claude env list
```

## Secret Management

### Environment Variables

**.env.example:**
```bash
# Azure
AZURE_TENANT_ID=
AZURE_SUBSCRIPTION_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# Database
DB_HOST=localhost
DB_NAME=myapp
DB_USER=
DB_PASSWORD=

# External Services
API_KEY=
SENTRY_DSN=
SLACK_WEBHOOK=
```

### Secret Providers

```json
{
  "secrets": {
    "provider": "azure-keyvault",
    "config": {
      "vaultUrl": "${KEYVAULT_URL}",
      "tenantId": "${AZURE_TENANT_ID}",
      "clientId": "${AZURE_CLIENT_ID}",
      "clientSecret": "${AZURE_CLIENT_SECRET}"
    },
    "mapping": {
      "API_KEY": "api-key-secret",
      "DB_PASSWORD": "database-password"
    }
  }
}
```

**Alternative providers:**
```json
{
  "secrets": {
    "provider": "aws-secrets-manager",
    "region": "us-east-1"
  }
}
```

## Advanced Integrations

### Slack Integration

```json
{
  "integrations": {
    "slack": {
      "enabled": true,
      "webhookUrl": "${SLACK_WEBHOOK}",
      "notifications": {
        "onCommit": {
          "channel": "#dev-commits",
          "format": "{{author}} committed: {{message}}"
        },
        "onDeployment": {
          "channel": "#deployments",
          "format": "Deployed {{version}} to {{environment}}"
        },
        "onError": {
          "channel": "#dev-alerts",
          "format": "Error: {{error}}"
        }
      }
    }
  }
}
```

### Jira Integration

```json
{
  "integrations": {
    "jira": {
      "enabled": true,
      "host": "${JIRA_HOST}",
      "email": "${JIRA_EMAIL}",
      "apiToken": "${JIRA_API_TOKEN}",
      "project": "PROJ",
      "autoCreateIssues": false,
      "autoLinkCommits": true,
      "transitions": {
        "onCommit": "In Progress",
        "onPR": "In Review",
        "onMerge": "Done"
      }
    }
  }
}
```

### Analytics Integration

```json
{
  "integrations": {
    "analytics": {
      "enabled": true,
      "provider": "mixpanel",
      "apiKey": "${MIXPANEL_API_KEY}",
      "events": [
        "command-executed",
        "file-created",
        "test-run",
        "deployment"
      ],
      "includeMetadata": true
    }
  }
}
```

## Best Practices

### 1. Version Control
Commit shared settings, gitignore local settings.

### 2. Environment Variables
Use environment variables for secrets, never commit them.

### 3. Team Standards
Document and share team configuration standards.

### 4. Regular Reviews
Review and update configurations regularly.

### 5. Monitoring
Enable logging and monitoring in production.

### 6. Performance
Optimize cache settings and parallel execution.

### 7. Security
Use secret managers, audit logging, and role-based access.

### 8. Documentation
Document custom configurations and integrations.

### 9. Testing
Test configurations in safe environments first.

### 10. Backup
Backup important configurations and logs.

## Troubleshooting

### Configuration Not Loading

**Check file location:**
```bash
ls -la .claude/settings.local.json
```

**Validate JSON:**
```bash
claude config validate
```

**Check extends path:**
```json
{
  "extends": "./settings.shared.json"  // Relative to .claude/
}
```

### Hook Not Running

**Check hook configuration:**
```bash
claude config show | grep -A 10 "hooks"
```

**Test hook manually:**
```bash
npm run lint
```

**Check permissions:**
```bash
chmod +x scripts/pre-commit.sh
```

### Performance Issues

**Check cache size:**
```bash
du -sh .claude/cache
```

**Clear cache:**
```bash
claude cache clear
```

**Reduce parallel tasks:**
```json
{
  "performance": {
    "maxConcurrentTasks": 3
  }
}
```

## Next Steps

- [Permissions Configuration](./permissions.md) - Control security
- [MCP Servers](./mcp-servers.md) - External integrations
- [Quality Gates](./quality-gates.md) - Quality requirements
- [Best Practices](../best-practices/README.md) - Development workflows
