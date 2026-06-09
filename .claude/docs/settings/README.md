# Settings & Configuration

Complete guide to configuring Claude Code for your development workflow.

## Overview

Claude Code uses a flexible configuration system based on `settings.local.json` files. These settings control permissions, MCP server integrations, output styles, quality gates, and more.

## Configuration Hierarchy

Settings are applied in the following order (later settings override earlier ones):

1. **Global defaults** - Built into Claude Code
2. **Global user settings** - `~/.claude/settings.json`
3. **Project settings** - `.claude/settings.local.json`
4. **Session overrides** - Commands like `/output` or `/context`

## Quick Start

### Basic Project Setup

Create `.claude/settings.local.json` in your project root:

```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": ["npm test", "npm run build"],
      "deny": ["rm -rf"],
      "ask": ["npm publish"]
    },
    "tools": {
      "Read": "allow",
      "Write": "ask",
      "Edit": "allow",
      "Bash": "allow"
    }
  },
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "enabled": true
    }
  },
  "outputStyle": "explanatory",
  "qualityGates": {
    "testCoverageThreshold": 80,
    "requireTests": true
  }
}
```

### Essential Settings

**Permissions** - Control what Claude Code can do:
```json
{
  "permissions": {
    "bash": {
      "allow": ["git status", "npm test"],
      "deny": ["rm -rf *"],
      "ask": ["git push", "npm publish"]
    }
  }
}
```

**MCP Servers** - Enable external tool integrations:
```json
{
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true
    }
  }
}
```

**Output Style** - Control response verbosity:
```json
{
  "outputStyle": "concise"
}
```

## Configuration File Structure

### Complete Schema

```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": ["string[]"],
      "deny": ["string[]"],
      "ask": ["string[]"]
    },
    "tools": {
      "Read": "allow | ask | deny",
      "Write": "allow | ask | deny",
      "Edit": "allow | ask | deny",
      "Bash": "allow | ask | deny",
      "Glob": "allow | ask | deny",
      "Grep": "allow | ask | deny",
      "TodoWrite": "allow | ask | deny",
      "WebFetch": "allow | ask | deny",
      "WebSearch": "allow | ask | deny"
    },
    "mcpServers": {
      "<server-name>": "allow | ask | deny"
    }
  },
  "mcpServers": {
    "<server-name>": {
      "command": "string",
      "args": ["string[]"],
      "env": {
        "KEY": "value"
      },
      "enabled": true | false,
      "healthCheck": {
        "enabled": true | false,
        "interval": 60000,
        "timeout": 5000
      }
    }
  },
  "outputStyle": "explanatory | concise | terse | detailed",
  "qualityGates": {
    "testCoverageThreshold": 80,
    "codeQualityScore": 8,
    "requireTests": true,
    "requireDocs": false,
    "securityScan": true,
    "validationChecklist": ["string[]"]
  },
  "hooks": {
    "preCommit": ["string[]"],
    "postCommit": ["string[]"],
    "preTest": ["string[]"],
    "postTest": ["string[]"]
  },
  "logging": {
    "level": "info | debug | warn | error",
    "outputPath": "string",
    "includeTimestamps": true
  },
  "performance": {
    "maxConcurrentTasks": 5,
    "cacheDuration": 900000,
    "enableParallelExecution": true
  }
}
```

## Quick Configuration Examples

### Python Project

```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": [
        "python -m pytest*",
        "python -m pip install*",
        "python -m venv*",
        "black .",
        "ruff check*",
        "mypy*"
      ],
      "ask": ["pip install*", "python setup.py*"]
    }
  },
  "qualityGates": {
    "testCoverageThreshold": 85,
    "requireTests": true,
    "validationChecklist": [
      "All tests pass",
      "Type hints added",
      "Black formatting applied",
      "Ruff linting passes"
    ]
  }
}
```

### TypeScript/Node Project

```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": [
        "npm test",
        "npm run build",
        "npm run lint",
        "npm run type-check",
        "npx tsc*"
      ],
      "ask": ["npm publish", "npm install*"]
    }
  },
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "enabled": true
    }
  },
  "qualityGates": {
    "testCoverageThreshold": 80,
    "requireTests": true,
    "validationChecklist": [
      "All tests pass",
      "TypeScript compilation successful",
      "ESLint passes",
      "Build succeeds"
    ]
  }
}
```

### Azure Development

```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": [
        "az login",
        "az account show",
        "az group list",
        "terraform plan",
        "terraform validate"
      ],
      "ask": [
        "az deployment*",
        "terraform apply",
        "az resource delete*"
      ],
      "deny": ["az account delete*"]
    }
  },
  "mcpServers": {
    "azure-mcp": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server"],
      "enabled": true,
      "env": {
        "AZURE_TENANT_ID": "${AZURE_TENANT_ID}",
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}"
      }
    },
    "azure-resource-graph": {
      "command": "npx",
      "args": ["-y", "@azure/resource-graph-mcp"],
      "enabled": true
    },
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true
    }
  }
}
```

### Web Scraping Project

```json
{
  "version": "1.0",
  "permissions": {
    "tools": {
      "WebFetch": "allow",
      "WebSearch": "allow"
    }
  },
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "enabled": true
    },
    "crawl4ai-rag": {
      "command": "python",
      "args": ["-m", "crawl4ai_rag.mcp"],
      "enabled": true
    }
  }
}
```

### Team Development

```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": [
        "git status",
        "git diff*",
        "git log*",
        "npm test",
        "npm run build"
      ],
      "ask": [
        "git push*",
        "git merge*",
        "npm publish"
      ]
    }
  },
  "outputStyle": "concise",
  "qualityGates": {
    "testCoverageThreshold": 80,
    "requireTests": true,
    "requireDocs": true,
    "validationChecklist": [
      "All tests pass",
      "Code reviewed",
      "Documentation updated",
      "Security scan passed"
    ]
  },
  "hooks": {
    "preCommit": [
      "npm run lint",
      "npm test"
    ]
  }
}
```

## Environment Variables

Use environment variables for sensitive data:

```json
{
  "mcpServers": {
    "custom-api": {
      "command": "node",
      "args": ["server.js"],
      "env": {
        "API_KEY": "${API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}",
        "ENV": "production"
      }
    }
  }
}
```

Set environment variables:

**Windows:**
```bash
set API_KEY=your-key-here
set DATABASE_URL=postgres://localhost/db
```

**macOS/Linux:**
```bash
export API_KEY=your-key-here
export DATABASE_URL=postgres://localhost/db
```

**.env file (recommended):**
```bash
API_KEY=your-key-here
DATABASE_URL=postgres://localhost/db
```

## Common Patterns

### Development vs Production

Use different settings files:

**.claude/settings.dev.json:**
```json
{
  "outputStyle": "explanatory",
  "logging": {
    "level": "debug"
  }
}
```

**.claude/settings.prod.json:**
```json
{
  "outputStyle": "terse",
  "logging": {
    "level": "error"
  }
}
```

Switch with:
```bash
cp .claude/settings.dev.json .claude/settings.local.json
```

### Shared Team Settings

**settings.shared.json** (committed to git):
```json
{
  "version": "1.0",
  "qualityGates": {
    "testCoverageThreshold": 80,
    "requireTests": true
  },
  "hooks": {
    "preCommit": ["npm test"]
  }
}
```

**settings.local.json** (personal, gitignored):
```json
{
  "extends": "./settings.shared.json",
  "outputStyle": "concise",
  "mcpServers": {
    "custom-server": {
      "enabled": true
    }
  }
}
```

### Multi-Environment Setup

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
      }
    },
    "staging": {
      "mcpServers": {
        "azure-mcp": {
          "env": {
            "AZURE_SUBSCRIPTION_ID": "${STAGING_SUBSCRIPTION_ID}"
          }
        }
      }
    },
    "production": {
      "mcpServers": {
        "azure-mcp": {
          "env": {
            "AZURE_SUBSCRIPTION_ID": "${PROD_SUBSCRIPTION_ID}"
          }
        }
      }
    }
  },
  "activeEnvironment": "development"
}
```

## Validation

Validate your configuration:

```bash
# Check syntax
claude config validate

# Show effective configuration
claude config show

# Test MCP server connections
claude config test-mcp

# Verify permissions
claude config check-permissions
```

## Common Issues

### Issue: Settings Not Applied

**Check:**
1. File location: `.claude/settings.local.json` in project root
2. JSON syntax: Use a validator like `jsonlint`
3. Schema version: Ensure `"version": "1.0"`
4. Reload: Restart Claude Code session

### Issue: MCP Server Not Connecting

**Check:**
1. Server installed: `npx -y <server-package>`
2. Command path correct
3. Environment variables set
4. Health check enabled and passing

### Issue: Permission Denied

**Check:**
1. Tool permission in `permissions.tools`
2. Bash command in `permissions.bash.allow`
3. MCP server permission in `permissions.mcpServers`

## Performance Tips

### Optimize MCP Server Loading

```json
{
  "mcpServers": {
    "rarely-used-server": {
      "enabled": false,
      "lazyLoad": true
    }
  }
}
```

### Cache Configuration

```json
{
  "performance": {
    "cacheDuration": 900000,
    "maxCacheSize": "100MB"
  }
}
```

### Parallel Execution

```json
{
  "performance": {
    "maxConcurrentTasks": 5,
    "enableParallelExecution": true
  }
}
```

## Security Best Practices

### 1. Never Commit Secrets

```json
{
  "mcpServers": {
    "api-server": {
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

Add to `.gitignore`:
```
.env
.claude/settings.local.json
```

### 2. Use Principle of Least Privilege

```json
{
  "permissions": {
    "bash": {
      "allow": ["npm test"],
      "deny": ["rm -rf", "sudo*"]
    }
  }
}
```

### 3. Audit Bash Commands

```json
{
  "permissions": {
    "bash": {
      "ask": ["git push*", "npm publish"]
    }
  },
  "logging": {
    "auditBashCommands": true
  }
}
```

### 4. Validate MCP Server Sources

Only use trusted MCP servers:
```json
{
  "mcpServers": {
    "untrusted-server": {
      "enabled": false
    }
  }
}
```

## Documentation Structure

This settings documentation is organized into the following guides:

### [Permissions Guide](./permissions.md)
- Bash command permissions
- Tool permissions
- MCP server permissions
- Security considerations
- Wildcard patterns
- Examples

### [MCP Servers Guide](./mcp-servers.md)
- Installing MCP servers
- Configuring each server
- Health checks
- Troubleshooting
- Performance tuning
- Custom servers

### [Output Styles Guide](./output-styles.md)
- Available styles
- When to use each
- Custom formatting
- Examples
- Configuration

### [Quality Gates Guide](./quality-gates.md)
- Test coverage thresholds
- Code quality requirements
- Security scanning
- Validation checklists
- CI/CD integration

### [Advanced Configuration Guide](./advanced-config.md)
- Team configurations
- Custom MCP servers
- Hook system
- Logging and monitoring
- Performance optimization
- Multi-project setup

## Next Steps

1. **Start with basics**: Create `.claude/settings.local.json` with essential permissions
2. **Add MCP servers**: Enable servers for your tech stack
3. **Configure quality gates**: Set testing and quality requirements
4. **Customize output**: Choose your preferred verbosity level
5. **Optimize**: Fine-tune performance and logging settings

## Additional Resources

- [Permissions Documentation](./permissions.md) - Detailed permission system guide
- [MCP Servers Documentation](./mcp-servers.md) - All available MCP servers
- [Quality Gates Documentation](./quality-gates.md) - Quality requirements setup
- [Advanced Configuration](./advanced-config.md) - Advanced features and patterns
- [Best Practices](../best-practices/README.md) - Development workflows and guidelines

## Getting Help

If you need assistance:

1. Check the relevant documentation section
2. Validate configuration: `claude config validate`
3. View effective settings: `claude config show`
4. Test connections: `claude config test-mcp`
5. Review logs in `.claude/logs/`

## Configuration Templates

Quick-start templates for common scenarios:

**Python Data Science:**
```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": ["python -m pytest*", "jupyter*", "python *.py"]
    }
  },
  "mcpServers": {
    "analysis-tool": {
      "command": "npx",
      "args": ["-y", "@analysis/mcp-server"],
      "enabled": true
    }
  }
}
```

**React/Next.js:**
```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": ["npm test", "npm run dev", "npm run build"]
    }
  },
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "enabled": true
    }
  }
}
```

**DevOps/Infrastructure:**
```json
{
  "version": "1.0",
  "permissions": {
    "bash": {
      "allow": ["terraform plan", "az account show"],
      "ask": ["terraform apply", "az deployment*"]
    }
  },
  "mcpServers": {
    "azure-mcp": {"enabled": true},
    "azure-resource-graph": {"enabled": true}
  }
}
```

## Version History

- **1.0** - Initial settings schema
  - Basic permissions system
  - MCP server configuration
  - Output styles
  - Quality gates

## Contributing

To improve this documentation:

1. Test configurations thoroughly
2. Document edge cases
3. Add real-world examples
4. Update troubleshooting sections
5. Keep examples current with latest versions
