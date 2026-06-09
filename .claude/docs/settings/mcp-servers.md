# MCP Servers Configuration

Complete guide to installing, configuring, and managing MCP (Model Context Protocol) servers in Claude Code.

## Overview

MCP servers extend Claude Code's capabilities with specialized tools and integrations. They run as separate processes and communicate via the Model Context Protocol, providing access to external services, databases, APIs, and specialized functionality.

## Available MCP Servers

### 1. microsoft-docs-mcp
Search and fetch official Microsoft documentation

### 2. context7
Advanced context management and code analysis

### 3. azure-mcp
Azure resource management and deployment

### 4. crawl4ai-rag
Web crawling and RAG (Retrieval-Augmented Generation)

### 5. serena
AI-powered code analysis and suggestions

### 6. playwright
Browser automation and testing

### 7. azure-resource-graph
Query Azure resources with KQL

### 8. ai-server-sequential-thinking
Sequential reasoning and problem-solving

### 9. analysis-tool
Data analysis and visualization

## Installation

### Prerequisites

**Node.js and npm:**
```bash
# Check installation
node --version
npm --version

# Install if needed
# Download from https://nodejs.org/
```

**Python (for Python-based servers):**
```bash
# Check installation
python --version
pip --version

# Install if needed
# Download from https://www.python.org/
```

### Installing MCP Servers

MCP servers can be installed globally or run on-demand with `npx`:

**Global installation (recommended for frequent use):**
```bash
npm install -g @microsoft/mcp-server
npm install -g @playwright/mcp-server
npm install -g @azure/mcp-server
```

**On-demand with npx (no installation needed):**
```json
{
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"]
    }
  }
}
```

**Python-based servers:**
```bash
pip install crawl4ai-rag
pip install analysis-tool
```

## Basic Configuration

Add MCP servers to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "string",
      "args": ["string[]"],
      "env": {"KEY": "value"},
      "enabled": true | false
    }
  }
}
```

## Server Configurations

### Microsoft Docs MCP

Search and fetch Microsoft documentation including Azure, .NET, Microsoft 365, and more.

**Installation:**
```bash
npm install -g @microsoft/mcp-server
```

**Configuration:**
```json
{
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true,
      "healthCheck": {
        "enabled": true,
        "interval": 60000,
        "timeout": 5000
      }
    }
  }
}
```

**Available Tools:**
- `microsoft_docs_search` - Search Microsoft documentation
- `microsoft_code_sample_search` - Find code examples
- `microsoft_docs_fetch` - Fetch complete documentation pages

**Usage Example:**
```typescript
// Claude Code will automatically use this server when you ask:
"Show me how to create an Azure Function in Python"
"Find documentation on Azure Key Vault"
"Get code examples for Azure Cosmos DB"
```

**Environment Variables:**
None required - works out of the box.

**Troubleshooting:**
```bash
# Test manually
npx -y @microsoft/mcp-server

# Check connectivity
claude config test-mcp microsoft-docs-mcp

# View logs
cat .claude/logs/mcp-microsoft-docs.log
```

### Context7

Advanced context management and code analysis.

**Installation:**
```bash
npm install -g @context7/mcp-server
```

**Configuration:**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"],
      "enabled": true,
      "env": {
        "CONTEXT7_MAX_CONTEXT": "100000",
        "CONTEXT7_CACHE_DIR": ".claude/cache/context7"
      }
    }
  }
}
```

**Available Tools:**
- Context analysis and optimization
- Intelligent code summarization
- Dependency graph generation
- Smart context window management

**Usage Example:**
```typescript
// Automatically activated for:
"Analyze the entire codebase architecture"
"Show dependencies between modules"
"Summarize this large file"
```

**Environment Variables:**
- `CONTEXT7_MAX_CONTEXT` - Maximum context size (default: 100000)
- `CONTEXT7_CACHE_DIR` - Cache directory path
- `CONTEXT7_API_KEY` - Optional API key for enhanced features

**Performance Tuning:**
```json
{
  "mcpServers": {
    "context7": {
      "env": {
        "CONTEXT7_MAX_CONTEXT": "200000",
        "CONTEXT7_ENABLE_CACHE": "true",
        "CONTEXT7_PARALLEL_ANALYSIS": "4"
      }
    }
  }
}
```

### Azure MCP

Manage Azure resources, deployments, and configurations.

**Installation:**
```bash
npm install -g @azure/mcp-server
```

**Configuration:**
```json
{
  "mcpServers": {
    "azure-mcp": {
      "command": "npx",
      "args": ["-y", "@azure/mcp-server"],
      "enabled": true,
      "env": {
        "AZURE_TENANT_ID": "${AZURE_TENANT_ID}",
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}",
        "AZURE_CLIENT_ID": "${AZURE_CLIENT_ID}",
        "AZURE_CLIENT_SECRET": "${AZURE_CLIENT_SECRET}"
      }
    }
  },
  "permissions": {
    "mcpServers": {
      "azure-mcp": "ask"
    }
  }
}
```

**Available Tools:**
- `list-tenants` - List all Azure tenants
- `select-tenant` - Select tenant and subscription
- `list-resource-groups` - List resource groups
- `get-resource-details` - Get detailed resource information
- `create-resource-group` - Create new resource group
- `list-role-assignments` - List RBAC assignments
- `get-role-definitions` - Get role definitions
- `get-user-permissions` - Get detailed user permissions
- `run-azure-code` - Execute Azure SDK code

**Usage Example:**
```typescript
// List all resource groups
"Show me all Azure resource groups"

// Get resource details
"Get details for the storage account named 'mystorageacct'"

// Create resources
"Create a resource group named 'rg-dev-eastus' in East US"

// Check permissions
"What permissions do I have on this subscription?"
```

**Authentication:**

**Option 1: Environment Variables (recommended)**
```bash
# Windows
set AZURE_TENANT_ID=your-tenant-id
set AZURE_SUBSCRIPTION_ID=your-subscription-id
set AZURE_CLIENT_ID=your-client-id
set AZURE_CLIENT_SECRET=your-client-secret

# macOS/Linux
export AZURE_TENANT_ID=your-tenant-id
export AZURE_SUBSCRIPTION_ID=your-subscription-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
```

**Option 2: Azure CLI**
```bash
az login
az account show
```

**Troubleshooting:**
```bash
# Test authentication
az account show

# Verify server
claude config test-mcp azure-mcp

# Check logs
cat .claude/logs/mcp-azure.log
```

### Crawl4AI RAG

Web crawling with RAG capabilities for intelligent content extraction.

**Installation:**
```bash
pip install crawl4ai-rag
```

**Configuration:**
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "command": "python",
      "args": ["-m", "crawl4ai_rag.mcp"],
      "enabled": true,
      "env": {
        "CRAWL4AI_MAX_DEPTH": "3",
        "CRAWL4AI_CACHE_DIR": ".claude/cache/crawl4ai",
        "CRAWL4AI_USER_AGENT": "ClaudeDev/1.0"
      }
    }
  },
  "permissions": {
    "mcpServers": {
      "crawl4ai-rag": "ask"
    }
  }
}
```

**Available Tools:**
- Intelligent web crawling
- Content extraction
- RAG-based Q&A on crawled content
- Site mapping and analysis

**Usage Example:**
```typescript
"Crawl the React documentation and summarize hooks"
"Extract all code examples from this blog post"
"What does this website say about authentication?"
```

**Environment Variables:**
- `CRAWL4AI_MAX_DEPTH` - Maximum crawl depth (default: 3)
- `CRAWL4AI_CACHE_DIR` - Cache directory
- `CRAWL4AI_USER_AGENT` - Custom user agent
- `CRAWL4AI_RATE_LIMIT` - Requests per second (default: 1)

**Advanced Configuration:**
```json
{
  "mcpServers": {
    "crawl4ai-rag": {
      "env": {
        "CRAWL4AI_MAX_DEPTH": "5",
        "CRAWL4AI_FOLLOW_LINKS": "true",
        "CRAWL4AI_EXTRACT_IMAGES": "true",
        "CRAWL4AI_EXTRACT_TABLES": "true",
        "CRAWL4AI_RESPECT_ROBOTS_TXT": "true"
      }
    }
  }
}
```

### Serena

AI-powered code analysis and intelligent suggestions.

**Installation:**
```bash
npm install -g @serena/mcp-server
```

**Configuration:**
```json
{
  "mcpServers": {
    "serena": {
      "command": "npx",
      "args": ["-y", "@serena/mcp-server"],
      "enabled": true,
      "env": {
        "SERENA_API_KEY": "${SERENA_API_KEY}",
        "SERENA_MODEL": "gpt-4"
      }
    }
  }
}
```

**Available Tools:**
- Code quality analysis
- Security vulnerability detection
- Performance optimization suggestions
- Best practices recommendations

**Usage Example:**
```typescript
"Analyze this code for security issues"
"Suggest performance improvements"
"Review this function for best practices"
```

**Environment Variables:**
- `SERENA_API_KEY` - API key (required)
- `SERENA_MODEL` - AI model to use
- `SERENA_MAX_TOKENS` - Maximum tokens per request

### Playwright

Browser automation and end-to-end testing.

**Installation:**
```bash
npm install -g @playwright/mcp-server
playwright install
```

**Configuration:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "enabled": true,
      "env": {
        "PLAYWRIGHT_BROWSER": "chromium",
        "PLAYWRIGHT_HEADLESS": "true"
      }
    }
  }
}
```

**Available Tools:**
- `browser_navigate` - Navigate to URLs
- `browser_click` - Click elements
- `browser_type` - Type text
- `browser_snapshot` - Capture page state
- `browser_take_screenshot` - Take screenshots
- `browser_evaluate` - Execute JavaScript
- `browser_fill_form` - Fill forms
- `browser_wait_for` - Wait for conditions
- And many more...

**Usage Example:**
```typescript
"Navigate to example.com and take a screenshot"
"Fill out the login form and submit"
"Test the checkout flow on my app"
"Verify the navigation menu works"
```

**Environment Variables:**
- `PLAYWRIGHT_BROWSER` - Browser to use (chromium, firefox, webkit)
- `PLAYWRIGHT_HEADLESS` - Run headless (true/false)
- `PLAYWRIGHT_SLOW_MO` - Slow down operations (milliseconds)

**Headless vs Headed:**
```json
{
  "mcpServers": {
    "playwright": {
      "env": {
        "PLAYWRIGHT_HEADLESS": "false",  // Show browser
        "PLAYWRIGHT_SLOW_MO": "100"       // Slow down for visibility
      }
    }
  }
}
```

**Troubleshooting:**
```bash
# Install browsers
playwright install

# Test installation
npx playwright test --help

# Check browser binaries
playwright install --help
```

### Azure Resource Graph

Query Azure resources using KQL (Kusto Query Language).

**Installation:**
```bash
npm install -g @azure/resource-graph-mcp
```

**Configuration:**
```json
{
  "mcpServers": {
    "azure-resource-graph": {
      "command": "npx",
      "args": ["-y", "@azure/resource-graph-mcp"],
      "enabled": true,
      "env": {
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}"
      }
    }
  }
}
```

**Available Tools:**
- `query-resources` - Execute KQL queries against Azure resources

**Usage Example:**
```typescript
"Find all virtual machines in East US"
"List storage accounts with public access"
"Show resources tagged with environment=production"
"Find resources without tags"
```

**KQL Query Examples:**
```kql
// All VMs
Resources
| where type == "microsoft.compute/virtualmachines"

// Resources by location
Resources
| where location == "eastus"
| project name, type, resourceGroup

// Tagged resources
Resources
| where tags.environment == "production"

// Resource counts by type
Resources
| summarize count() by type
| order by count_ desc
```

**Authentication:**
Uses same credentials as azure-mcp (Azure CLI or environment variables).

### AI Server Sequential Thinking

Advanced sequential reasoning and problem-solving.

**Installation:**
```bash
npm install -g @ai-server/sequential-thinking
```

**Configuration:**
```json
{
  "mcpServers": {
    "ai-server-sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@ai-server/sequential-thinking"],
      "enabled": true,
      "env": {
        "THINKING_MAX_STEPS": "50",
        "THINKING_MODEL": "claude-3-5-sonnet"
      }
    }
  }
}
```

**Available Tools:**
- `sequentialthinking` - Multi-step reasoning with chain of thought

**Usage Example:**
```typescript
"Solve this complex algorithm problem step by step"
"Design a system architecture with detailed reasoning"
"Debug this issue using systematic analysis"
```

**Environment Variables:**
- `THINKING_MAX_STEPS` - Maximum reasoning steps
- `THINKING_MODEL` - AI model for reasoning
- `THINKING_ENABLE_BRANCHING` - Enable thought branching

**Advanced Configuration:**
```json
{
  "mcpServers": {
    "ai-server-sequential-thinking": {
      "env": {
        "THINKING_MAX_STEPS": "100",
        "THINKING_ENABLE_BRANCHING": "true",
        "THINKING_ENABLE_REVISION": "true",
        "THINKING_MIN_CONFIDENCE": "0.8"
      }
    }
  }
}
```

### Analysis Tool

Data analysis, visualization, and statistical operations.

**Installation:**
```bash
pip install analysis-tool
```

**Configuration:**
```json
{
  "mcpServers": {
    "analysis-tool": {
      "command": "python",
      "args": ["-m", "analysis_tool.mcp"],
      "enabled": true,
      "env": {
        "ANALYSIS_BACKEND": "pandas",
        "ANALYSIS_PLOT_BACKEND": "matplotlib"
      }
    }
  }
}
```

**Available Tools:**
- Data loading and transformation
- Statistical analysis
- Data visualization
- Pattern detection

**Usage Example:**
```typescript
"Analyze this CSV file and show summary statistics"
"Create a visualization of sales trends"
"Detect outliers in this dataset"
"Perform correlation analysis"
```

**Environment Variables:**
- `ANALYSIS_BACKEND` - pandas, polars, dask
- `ANALYSIS_PLOT_BACKEND` - matplotlib, plotly, seaborn
- `ANALYSIS_MAX_ROWS` - Maximum rows to process

## Health Checks

Enable health checks to monitor MCP server status:

```json
{
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true,
      "healthCheck": {
        "enabled": true,
        "interval": 60000,        // Check every 60 seconds
        "timeout": 5000,          // 5 second timeout
        "retries": 3,             // Retry 3 times before failing
        "onFailure": "restart"    // restart, disable, or alert
      }
    }
  }
}
```

**Health Check Actions:**
- `restart` - Restart the server automatically
- `disable` - Disable the server
- `alert` - Log error and continue

**Custom Health Checks:**
```json
{
  "mcpServers": {
    "custom-server": {
      "healthCheck": {
        "enabled": true,
        "command": "curl http://localhost:3000/health",
        "expectedOutput": "OK",
        "interval": 30000
      }
    }
  }
}
```

## Performance Tuning

### Lazy Loading

Load servers only when needed:

```json
{
  "mcpServers": {
    "rarely-used-server": {
      "command": "npx",
      "args": ["-y", "@rarely/used-server"],
      "enabled": false,
      "lazyLoad": true,
      "activationPatterns": [
        "use rarely used feature",
        "activate special tool"
      ]
    }
  }
}
```

### Connection Pooling

Reuse server connections:

```json
{
  "mcpServers": {
    "database-server": {
      "command": "node",
      "args": ["db-server.js"],
      "pool": {
        "min": 2,
        "max": 10,
        "idleTimeout": 30000
      }
    }
  }
}
```

### Caching

Enable response caching:

```json
{
  "mcpServers": {
    "microsoft-docs-mcp": {
      "cache": {
        "enabled": true,
        "ttl": 900000,           // 15 minutes
        "maxSize": "100MB",
        "storage": "disk"         // memory or disk
      }
    }
  }
}
```

## Multi-Server Configurations

### Complete Azure Stack

```json
{
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true
    },
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
    }
  },
  "permissions": {
    "mcpServers": {
      "microsoft-docs-mcp": "allow",
      "azure-mcp": "ask",
      "azure-resource-graph": "allow"
    }
  }
}
```

### Web Development Stack

```json
{
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

### Data Science Stack

```json
{
  "mcpServers": {
    "analysis-tool": {
      "command": "python",
      "args": ["-m", "analysis_tool.mcp"],
      "enabled": true
    },
    "ai-server-sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@ai-server/sequential-thinking"],
      "enabled": true
    }
  }
}
```

## Troubleshooting

### Server Won't Start

**Check installation:**
```bash
# Node-based servers
npx -y @microsoft/mcp-server --version

# Python-based servers
python -m crawl4ai_rag.mcp --version
```

**Check configuration:**
```bash
claude config validate
claude config show
```

**Check logs:**
```bash
cat .claude/logs/mcp-<server-name>.log
```

### Connection Timeouts

Increase timeout:
```json
{
  "mcpServers": {
    "slow-server": {
      "timeout": 30000,
      "healthCheck": {
        "timeout": 10000
      }
    }
  }
}
```

### Authentication Errors

**Verify credentials:**
```bash
# Azure
az account show

# Check environment variables
echo $AZURE_TENANT_ID
echo $AZURE_SUBSCRIPTION_ID
```

**Update configuration:**
```json
{
  "mcpServers": {
    "azure-mcp": {
      "env": {
        "AZURE_TENANT_ID": "correct-tenant-id",
        "AZURE_SUBSCRIPTION_ID": "correct-subscription-id"
      }
    }
  }
}
```

### Memory Issues

Limit resource usage:
```json
{
  "mcpServers": {
    "resource-intensive-server": {
      "resources": {
        "maxMemory": "512MB",
        "maxCpu": "50%"
      }
    }
  }
}
```

### Port Conflicts

Change port:
```json
{
  "mcpServers": {
    "custom-server": {
      "env": {
        "PORT": "3001"
      }
    }
  }
}
```

## Custom MCP Servers

Create your own MCP server:

**server.js:**
```javascript
const { MCPServer } = require('@modelcontextprotocol/sdk');

const server = new MCPServer({
  name: 'custom-server',
  version: '1.0.0'
});

server.registerTool({
  name: 'custom_tool',
  description: 'Does something custom',
  inputSchema: {
    type: 'object',
    properties: {
      input: { type: 'string' }
    }
  },
  handler: async (input) => {
    return { result: `Processed: ${input}` };
  }
});

server.start();
```

**Configuration:**
```json
{
  "mcpServers": {
    "custom-server": {
      "command": "node",
      "args": ["path/to/server.js"],
      "enabled": true
    }
  }
}
```

## Best Practices

### 1. Enable Only Needed Servers
Reduce startup time and resource usage:
```json
{
  "mcpServers": {
    "frequently-used": {
      "enabled": true
    },
    "rarely-used": {
      "enabled": false,
      "lazyLoad": true
    }
  }
}
```

### 2. Use Health Checks
Monitor server health:
```json
{
  "healthCheck": {
    "enabled": true,
    "interval": 60000,
    "onFailure": "restart"
  }
}
```

### 3. Secure Credentials
Use environment variables:
```json
{
  "env": {
    "API_KEY": "${API_KEY}"
  }
}
```

### 4. Configure Timeouts
Prevent hanging:
```json
{
  "timeout": 30000,
  "healthCheck": {
    "timeout": 5000
  }
}
```

### 5. Enable Caching
Improve performance:
```json
{
  "cache": {
    "enabled": true,
    "ttl": 900000
  }
}
```

### 6. Monitor Logs
Regular log review:
```bash
tail -f .claude/logs/mcp-*.log
```

### 7. Version Pin
Pin server versions for stability:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server@1.2.3"]
    }
  }
}
```

## Next Steps

- [Permissions Configuration](./permissions.md) - Control server access
- [Quality Gates](./quality-gates.md) - Set quality requirements
- [Advanced Configuration](./advanced-config.md) - Advanced features
- [Best Practices](../best-practices/README.md) - Development workflows
