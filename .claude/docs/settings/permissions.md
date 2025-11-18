# Permissions System

Complete guide to configuring permissions in Claude Code to control security and automation.

## Overview

The permissions system controls what Claude Code can do in your environment. It uses a three-tier system: **allow**, **ask**, and **deny** for granular control over tools, bash commands, and MCP servers.

## Permission Levels

### Allow
- Action proceeds automatically
- No user confirmation required
- Use for safe, repeatable operations

### Ask
- Action requires user confirmation
- Shows proposed action before execution
- Use for impactful or irreversible operations

### Deny
- Action is blocked completely
- User cannot override without changing settings
- Use for dangerous or prohibited operations

## Permissions Schema

```json
{
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
      "WebSearch": "allow | ask | deny",
      "NotebookEdit": "allow | ask | deny",
      "SlashCommand": "allow | ask | deny"
    },
    "mcpServers": {
      "<server-name>": "allow | ask | deny"
    }
  }
}
```

## Bash Command Permissions

### Basic Configuration

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "git status",
        "git diff",
        "npm test",
        "python -m pytest"
      ],
      "ask": [
        "git push",
        "npm publish",
        "pip install"
      ],
      "deny": [
        "rm -rf /",
        "sudo rm",
        "format c:"
      ]
    }
  }
}
```

### Wildcard Patterns

Use wildcards for flexible matching:

**Asterisk (*) - Matches any characters:**
```json
{
  "bash": {
    "allow": [
      "npm run *",           // Any npm script
      "git log*",            // git log with any args
      "python *.py"          // Run any Python file
    ]
  }
}
```

**Question mark (?) - Matches single character:**
```json
{
  "bash": {
    "allow": [
      "test?.py",            // test1.py, test2.py, etc.
      "node src/app?.js"     // app1.js, app2.js, etc.
    ]
  }
}
```

**Character ranges [...]:**
```json
{
  "bash": {
    "allow": [
      "git checkout feature-[0-9]*",  // feature-1, feature-23, etc.
      "npm run test-[a-z]*"           // test-a, test-unit, etc.
    ]
  }
}
```

### Command Categories

**Git Operations:**
```json
{
  "bash": {
    "allow": [
      "git status",
      "git diff*",
      "git log*",
      "git branch*",
      "git show*",
      "git fetch*"
    ],
    "ask": [
      "git push*",
      "git pull*",
      "git merge*",
      "git rebase*",
      "git commit*"
    ],
    "deny": [
      "git push --force*",
      "git reset --hard*",
      "git clean -fd*"
    ]
  }
}
```

**Package Management:**
```json
{
  "bash": {
    "allow": [
      "npm install --dry-run*",
      "npm list*",
      "npm outdated*",
      "pip list*",
      "pip show*"
    ],
    "ask": [
      "npm install*",
      "npm uninstall*",
      "pip install*",
      "pip uninstall*"
    ],
    "deny": [
      "npm install -g*",      // Global installs
      "pip install --user*"   // User-wide installs
    ]
  }
}
```

**Testing:**
```json
{
  "bash": {
    "allow": [
      "npm test*",
      "npm run test*",
      "pytest*",
      "python -m pytest*",
      "jest*",
      "mocha*",
      "cargo test*"
    ]
  }
}
```

**Building:**
```json
{
  "bash": {
    "allow": [
      "npm run build*",
      "npm run compile*",
      "python setup.py build",
      "cargo build*",
      "mvn compile*",
      "gradle build*"
    ]
  }
}
```

**Linting & Formatting:**
```json
{
  "bash": {
    "allow": [
      "npm run lint*",
      "eslint*",
      "black .",
      "black src/",
      "ruff check*",
      "prettier*",
      "rustfmt*"
    ]
  }
}
```

**Type Checking:**
```json
{
  "bash": {
    "allow": [
      "npm run type-check*",
      "tsc --noEmit*",
      "mypy*",
      "pyright*"
    ]
  }
}
```

**Docker:**
```json
{
  "bash": {
    "allow": [
      "docker ps*",
      "docker images*",
      "docker logs*",
      "docker inspect*"
    ],
    "ask": [
      "docker build*",
      "docker run*",
      "docker stop*",
      "docker rm*"
    ],
    "deny": [
      "docker system prune -a*",
      "docker rm -f $(docker ps -aq)"
    ]
  }
}
```

**Cloud CLI:**
```json
{
  "bash": {
    "allow": [
      "az account show",
      "az account list",
      "az group list*",
      "az resource list*",
      "kubectl get*",
      "kubectl describe*"
    ],
    "ask": [
      "az deployment*",
      "az group create*",
      "kubectl apply*",
      "kubectl delete*"
    ],
    "deny": [
      "az account delete*",
      "az group delete*",
      "kubectl delete namespace*"
    ]
  }
}
```

### Pattern Matching Rules

Commands are matched in order:

1. **Exact match** - Literal string comparison
2. **Deny rules** - Checked first for safety
3. **Allow rules** - Checked next
4. **Ask rules** - Checked last
5. **Default** - If no match, default to "ask"

```json
{
  "bash": {
    "deny": ["git push --force*"],        // Checked first
    "allow": ["git status"],              // Then allow
    "ask": ["git push*"]                  // Then ask
  }
}
```

**Example matching:**
- `git push --force origin main` → **Denied** (matches deny rule)
- `git status` → **Allowed** (matches allow rule)
- `git push origin main` → **Ask** (matches ask rule)
- `git log` → **Ask** (no match, default behavior)

### Security Patterns

**Block destructive operations:**
```json
{
  "bash": {
    "deny": [
      "rm -rf /*",
      "rm -rf *",
      "sudo rm*",
      "dd if=*",
      "mkfs*",
      "format*",
      "> /dev/sda*",
      "chmod 777 *",
      "chmod -R 777*"
    ]
  }
}
```

**Block privilege escalation:**
```json
{
  "bash": {
    "deny": [
      "sudo*",
      "su*",
      "doas*"
    ]
  }
}
```

**Block system modifications:**
```json
{
  "bash": {
    "deny": [
      "systemctl*",
      "service*",
      "reboot",
      "shutdown*",
      "halt",
      "init*"
    ]
  }
}
```

**Block network exposure:**
```json
{
  "bash": {
    "deny": [
      "chmod 777*",
      "chmod 666*",
      "iptables -F*",
      "ufw disable*"
    ]
  }
}
```

## Tool Permissions

### Available Tools

**File Operations:**
- **Read** - Read file contents
- **Write** - Create or overwrite files
- **Edit** - Modify existing files
- **Glob** - Search for files by pattern
- **Grep** - Search file contents

**Execution:**
- **Bash** - Execute shell commands

**Workflow:**
- **TodoWrite** - Manage task lists
- **SlashCommand** - Execute custom commands

**Web:**
- **WebFetch** - Fetch web pages
- **WebSearch** - Search the web

**Notebooks:**
- **NotebookEdit** - Modify Jupyter notebooks

### Configuration Examples

**Read-only mode:**
```json
{
  "permissions": {
    "tools": {
      "Read": "allow",
      "Glob": "allow",
      "Grep": "allow",
      "Write": "deny",
      "Edit": "deny",
      "Bash": "deny"
    }
  }
}
```

**Safe development:**
```json
{
  "permissions": {
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Glob": "allow",
      "Grep": "allow",
      "Write": "ask",
      "Bash": "allow",
      "TodoWrite": "allow"
    }
  }
}
```

**Web research:**
```json
{
  "permissions": {
    "tools": {
      "Read": "allow",
      "WebFetch": "allow",
      "WebSearch": "allow",
      "Write": "ask"
    }
  }
}
```

**Jupyter notebooks:**
```json
{
  "permissions": {
    "tools": {
      "Read": "allow",
      "NotebookEdit": "allow",
      "Edit": "allow",
      "Bash": "allow"
    }
  }
}
```

### Tool Permission Behavior

**Read Permission:**
```json
{
  "tools": {
    "Read": "allow"    // Can read any file
  }
}
```
- Allows reading files in the project
- No user confirmation needed
- Safe for most scenarios

**Write Permission:**
```json
{
  "tools": {
    "Write": "ask"     // Confirms before creating files
  }
}
```
- Controls file creation
- Overwrites existing files if allowed
- Set to "ask" to prevent accidental overwrites

**Edit Permission:**
```json
{
  "tools": {
    "Edit": "allow"    // Can modify existing files
  }
}
```
- Modifies existing files only
- Cannot create new files
- Safer than Write for most operations

**Bash Permission:**
```json
{
  "tools": {
    "Bash": "allow"    // Can execute bash commands
  }
}
```
- Controls all bash command execution
- Individual commands still checked against bash permissions
- Set to "deny" to block all command execution

## MCP Server Permissions

### Basic Configuration

```json
{
  "permissions": {
    "mcpServers": {
      "playwright": "allow",
      "azure-mcp": "ask",
      "untrusted-server": "deny"
    }
  }
}
```

### Common Configurations

**Development tools (trusted):**
```json
{
  "permissions": {
    "mcpServers": {
      "microsoft-docs-mcp": "allow",
      "playwright": "allow",
      "analysis-tool": "allow",
      "ai-server-sequential-thinking": "allow"
    }
  }
}
```

**Cloud operations (require confirmation):**
```json
{
  "permissions": {
    "mcpServers": {
      "azure-mcp": "ask",
      "azure-resource-graph": "ask"
    }
  }
}
```

**External services (ask):**
```json
{
  "permissions": {
    "mcpServers": {
      "crawl4ai-rag": "ask",
      "custom-api-server": "ask"
    }
  }
}
```

### Server-Specific Permissions

Some MCP servers have their own permission systems:

**Azure MCP:**
```json
{
  "mcpServers": {
    "azure-mcp": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server"],
      "permissions": {
        "read": "allow",
        "write": "ask",
        "delete": "deny"
      }
    }
  }
}
```

**Playwright:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "permissions": {
        "navigate": "allow",
        "screenshot": "allow",
        "execute": "ask"
      }
    }
  }
}
```

## Permission Inheritance

### Global Settings

Create global defaults in `~/.claude/settings.json`:

```json
{
  "permissions": {
    "bash": {
      "deny": [
        "rm -rf /*",
        "sudo*"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow"
    }
  }
}
```

### Project Overrides

Override in `.claude/settings.local.json`:

```json
{
  "extends": "~/.claude/settings.json",
  "permissions": {
    "bash": {
      "allow": [
        "npm test",
        "npm run build"
      ]
    }
  }
}
```

**Merge behavior:**
- Deny rules: Combined (project + global)
- Allow rules: Project overrides global
- Ask rules: Project overrides global

## Real-World Examples

### Example 1: Python Data Science Project

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "python -m pytest*",
        "python *.py",
        "jupyter notebook*",
        "jupyter lab*",
        "black .",
        "black src/",
        "ruff check*",
        "mypy*"
      ],
      "ask": [
        "pip install*",
        "conda install*"
      ],
      "deny": [
        "rm -rf data/",
        "rm *.csv",
        "rm *.parquet"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask",
      "NotebookEdit": "allow",
      "Bash": "allow"
    },
    "mcpServers": {
      "analysis-tool": "allow"
    }
  }
}
```

### Example 2: TypeScript API Project

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "npm test*",
        "npm run test*",
        "npm run build*",
        "npm run lint*",
        "npm run type-check*",
        "npx tsc*",
        "docker ps*",
        "docker logs*"
      ],
      "ask": [
        "npm install*",
        "npm publish*",
        "docker build*",
        "docker run*"
      ],
      "deny": [
        "rm -rf node_modules",
        "rm package-lock.json",
        "npm uninstall express"  // Critical dependency
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask",
      "Bash": "allow",
      "TodoWrite": "allow"
    }
  }
}
```

### Example 3: Azure Infrastructure Project

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "az account show",
        "az account list",
        "az group list*",
        "az resource list*",
        "terraform plan*",
        "terraform validate*",
        "terraform fmt*"
      ],
      "ask": [
        "az deployment group create*",
        "az deployment sub create*",
        "terraform apply*"
      ],
      "deny": [
        "az account delete*",
        "az group delete*",
        "az resource delete*",
        "terraform destroy*"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask",
      "Bash": "allow"
    },
    "mcpServers": {
      "azure-mcp": "ask",
      "azure-resource-graph": "allow",
      "microsoft-docs-mcp": "allow"
    }
  }
}
```

### Example 4: React Frontend Project

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "npm test*",
        "npm run test*",
        "npm run build*",
        "npm run lint*",
        "npm run dev*",
        "npm run start*",
        "npx playwright test*"
      ],
      "ask": [
        "npm install*",
        "npm publish*",
        "npm run deploy*"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask",
      "Bash": "allow",
      "WebFetch": "allow"
    },
    "mcpServers": {
      "playwright": "allow"
    }
  }
}
```

### Example 5: Machine Learning Project

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "python train.py --dry-run*",
        "python eval.py*",
        "tensorboard*",
        "jupyter*",
        "python -m pytest*"
      ],
      "ask": [
        "python train.py*",           // Expensive operations
        "python fine_tune.py*",
        "pip install*"
      ],
      "deny": [
        "rm -rf models/",
        "rm -rf checkpoints/",
        "rm *.pt",
        "rm *.ckpt"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask",
      "NotebookEdit": "allow",
      "Bash": "allow"
    }
  }
}
```

## Security Considerations

### Principle of Least Privilege

Start restrictive and expand as needed:

```json
{
  "permissions": {
    "bash": {
      "allow": [
        // Only essential commands
        "git status",
        "npm test"
      ],
      "ask": [
        // Everything else
        "*"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "ask",
      "Write": "ask",
      "Bash": "allow"
    }
  }
}
```

### Protect Sensitive Data

```json
{
  "permissions": {
    "bash": {
      "deny": [
        "cat .env*",
        "cat *secret*",
        "cat *password*",
        "cat *credential*",
        "echo $AWS_SECRET*",
        "echo $API_KEY*"
      ]
    }
  }
}
```

### Audit Logging

Enable logging for security audits:

```json
{
  "permissions": {
    "bash": {
      "ask": [
        "git push*",
        "npm publish*"
      ]
    }
  },
  "logging": {
    "auditBashCommands": true,
    "auditFileWrites": true,
    "outputPath": ".claude/logs/audit.log"
  }
}
```

### Team Permissions

For shared projects:

```json
{
  "permissions": {
    "bash": {
      "allow": [
        "git status",
        "git diff*",
        "npm test",
        "npm run build"
      ],
      "ask": [
        "git push*",
        "git merge*",
        "npm publish"
      ],
      "deny": [
        "git push --force*",
        "rm -rf node_modules"
      ]
    }
  }
}
```

### Environment-Specific Permissions

**Development:**
```json
{
  "permissions": {
    "bash": {
      "allow": ["*"],
      "deny": ["rm -rf /*", "sudo*"]
    }
  }
}
```

**Staging:**
```json
{
  "permissions": {
    "bash": {
      "allow": ["git status", "npm test"],
      "ask": ["*"]
    }
  }
}
```

**Production:**
```json
{
  "permissions": {
    "bash": {
      "allow": ["git status"],
      "ask": ["git log*", "npm test"],
      "deny": ["*"]
    }
  }
}
```

## Testing Permissions

### Validate Configuration

```bash
# Check syntax
claude config validate

# Show effective permissions
claude config show

# Test specific command
claude test-permission "git push origin main"
```

### Permission Test Cases

Create test scenarios:

```json
{
  "permissions": {
    "bash": {
      "allow": ["npm test*"],
      "ask": ["git push*"],
      "deny": ["rm -rf*"]
    }
  }
}
```

Test:
```bash
# Should succeed
claude exec "npm test"

# Should prompt
claude exec "git push origin main"

# Should fail
claude exec "rm -rf node_modules"
```

## Troubleshooting

### Permission Denied Errors

**Check configuration:**
```bash
claude config show | grep -A 10 "permissions"
```

**Add missing permission:**
```json
{
  "permissions": {
    "bash": {
      "allow": ["your-command-here"]
    }
  }
}
```

**Reload configuration:**
```bash
claude config reload
```

### Wildcard Not Matching

**Use more specific patterns:**
```json
{
  "bash": {
    "allow": [
      "npm run test:*",      // Instead of "npm run test*"
      "python -m pytest*"    // Include full command
    ]
  }
}
```

### Permission Conflicts

Order matters - deny takes precedence:

```json
{
  "bash": {
    "deny": ["git push --force*"],   // Checked first
    "allow": ["git push*"]           // Won't match force push
  }
}
```

## Best Practices

### 1. Start Restrictive
Begin with minimal permissions and expand as needed.

### 2. Use Wildcards Carefully
Overly broad wildcards can allow unintended commands.

### 3. Document Custom Permissions
Add comments explaining why specific permissions are needed.

### 4. Regular Audits
Review and update permissions periodically.

### 5. Environment-Specific Configs
Use different settings for dev, staging, and production.

### 6. Test Before Deployment
Validate permissions in safe environments first.

### 7. Version Control
Commit shared settings, gitignore local overrides.

### 8. Security Review
Have security team review permission configurations.

## Next Steps

- [MCP Servers Configuration](./mcp-servers.md) - Configure external integrations
- [Quality Gates](./quality-gates.md) - Set quality requirements
- [Advanced Configuration](./advanced-config.md) - Advanced features
- [Best Practices](../best-practices/README.md) - Development workflows
