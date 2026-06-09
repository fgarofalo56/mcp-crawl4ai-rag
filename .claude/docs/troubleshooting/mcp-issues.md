# MCP Server Troubleshooting Guide

## Overview

This comprehensive guide addresses issues specific to MCP (Model Context Protocol) servers in the Claude Code Context Engineering system, covering all 9 MCP servers and their common problems.

## Connection Failures

### Problem
MCP servers fail to establish connection or disconnect unexpectedly.

### Symptoms
- "Connection refused" errors
- "Unable to connect to MCP server" messages
- Intermittent disconnections
- Server unreachable

### Server-Specific Solutions

#### Filesystem MCP

```bash
# Check if server is running
ps aux | grep mcp-server-filesystem

# Start server manually
node ~/.claude/mcp-servers/filesystem/dist/index.js

# Test connection
/test-mcp filesystem

# Common fix
cd ~/.claude/mcp-servers/filesystem
npm install
npm run build
```

**Configuration Check:**
```json
{
  "filesystem": {
    "command": "node",
    "args": ["~/.claude/mcp-servers/filesystem/dist/index.js"],
    "env": {
      "ALLOWED_PATHS": "/home/user/projects,/tmp"
    }
  }
}
```

#### GitHub MCP

```bash
# Verify GitHub token
echo $GITHUB_TOKEN

# Test GitHub API access
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Debug connection
MCP_DEBUG=true node ~/.claude/mcp-servers/github/index.js

# Common fix - Update token
export GITHUB_TOKEN="ghp_your_new_token_here"
```

**Troubleshooting Steps:**
1. Regenerate GitHub token with correct scopes
2. Check network firewall rules
3. Verify API rate limits

#### Playwright MCP

```bash
# Install browsers
npx playwright install

# Test browser launch
npx playwright test --headed

# Fix permissions
chmod +x ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome

# Debug mode
DEBUG=pw:api node ~/.claude/mcp-servers/playwright/index.js
```

**Common Issues:**
- Missing browser binaries
- Display server issues (Linux)
- Insufficient memory

#### Sequential Thinking MCP

```bash
# Check Python version (needs 3.8+)
python3 --version

# Verify installation
pip show sequential-thinking-mcp

# Reinstall if needed
pip install --upgrade sequential-thinking-mcp

# Test directly
python -m sequential_thinking_mcp.server
```

#### Postgres MCP

```bash
# Test database connection
psql -h localhost -U username -d database -c "SELECT 1"

# Check PostgreSQL service
systemctl status postgresql

# Verify connection string
echo $DATABASE_URL

# Test MCP connection
/test-mcp postgres --connection-string "postgresql://user:pass@localhost/db"
```

**Connection String Format:**
```
postgresql://username:password@host:port/database?sslmode=require
```

#### Brave Search MCP

```bash
# Verify API key
curl -H "X-Subscription-Token: $BRAVE_API_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"

# Check rate limits
/check-mcp-limits brave-search

# Debug search
MCP_LOG_LEVEL=debug node ~/.claude/mcp-servers/brave-search/index.js
```

#### EXA MCP

```bash
# Test EXA API
curl -H "Authorization: Bearer $EXA_API_KEY" \
  https://api.exa.ai/search

# Verify server
/verify-mcp exa

# Check configuration
cat ~/.claude/mcp-servers/exa/config.json
```

#### Memory MCP

```bash
# Check Redis connection (if used)
redis-cli ping

# Verify memory storage
ls -la ~/.claude/mcp-servers/memory/data/

# Test memory operations
/test-mcp memory --operation store --key test --value data
```

#### Puppeteer MCP

```bash
# Similar to Playwright, check Chrome
google-chrome --version

# Test Puppeteer
node -e "const p = require('puppeteer'); p.launch().then(b => b.close())"

# Fix Chrome sandbox issues
echo "export CHROME_DEVEL_SANDBOX=/usr/local/sbin/chrome-devel-sandbox" >> ~/.bashrc
```

### General Connection Solutions

#### Solution 1: Network Diagnostics

```bash
# Check port availability
netstat -tuln | grep <mcp-port>

# Test localhost connectivity
ping localhost
telnet localhost <port>

# Check firewall rules
sudo iptables -L -n | grep <port>
# or on Mac
sudo pfctl -s rules | grep <port>

# Windows firewall
netsh advfirewall firewall show rule name=all | findstr <port>
```

#### Solution 2: Process Management

```bash
# Kill stuck processes
pkill -f mcp-server

# Start all MCP servers
/start-all-mcps

# Restart specific server
/restart-mcp filesystem

# Check server status
/status-mcp --all
```

#### Solution 3: Connection Pool Reset

```python
# reset_connections.py
import subprocess
import time

def reset_mcp_connections():
    """Reset all MCP server connections"""

    servers = [
        'filesystem', 'github', 'playwright',
        'sequential-thinking', 'postgres', 'brave-search',
        'exa', 'memory', 'puppeteer'
    ]

    for server in servers:
        print(f"Resetting {server}...")

        # Stop server
        subprocess.run(['pkill', '-f', f'mcp-server-{server}'])
        time.sleep(2)

        # Start server
        subprocess.run(['/start-mcp', server])
        time.sleep(3)

        # Test connection
        result = subprocess.run(
            ['/test-mcp', server],
            capture_output=True,
            text=True
        )

        if 'success' in result.stdout.lower():
            print(f"✅ {server} connected successfully")
        else:
            print(f"❌ {server} connection failed")

reset_mcp_connections()
```

## Authentication Errors

### Problem
Authentication failures when connecting to MCP servers.

### Symptoms
- "401 Unauthorized" errors
- "Invalid credentials" messages
- Token expiration issues
- API key rejections

### Solutions by Server

#### GitHub MCP Authentication

```bash
# Generate new token
# Go to GitHub Settings > Developer settings > Personal access tokens

# Required scopes:
# - repo (full control)
# - read:org
# - read:user

# Set token
export GITHUB_TOKEN="ghp_your_token_here"

# Add to .env
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env

# Test authentication
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

#### Postgres MCP Authentication

```sql
-- Check user permissions
\du

-- Grant necessary permissions
GRANT CONNECT ON DATABASE mydb TO myuser;
GRANT USAGE ON SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;

-- Test connection
\c mydb myuser
```

#### Brave Search API Authentication

```bash
# Get API key from https://api.search.brave.com/app/keys

# Set API key
export BRAVE_API_KEY="BSA_your_key_here"

# Test authentication
curl -H "X-Subscription-Token: $BRAVE_API_KEY" \
  "https://api.search.brave.com/res/v1/web/search?q=test"

# Check rate limits
curl -H "X-Subscription-Token: $BRAVE_API_KEY" \
  "https://api.search.brave.com/res/v1/account/usage"
```

### General Authentication Solutions

#### Solution 1: Credential Management

```python
# manage_credentials.py
import os
import json
import keyring
from cryptography.fernet import Fernet

class CredentialManager:
    """Secure credential management for MCP servers"""

    def __init__(self):
        self.key = self.get_or_create_key()
        self.cipher = Fernet(self.key)

    def get_or_create_key(self):
        """Get or create encryption key"""
        key = keyring.get_password("claude-mcp", "encryption-key")
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password("claude-mcp", "encryption-key", key)
        return key.encode()

    def store_credential(self, service, credential):
        """Store encrypted credential"""
        encrypted = self.cipher.encrypt(credential.encode())
        keyring.set_password("claude-mcp", service, encrypted.decode())

    def get_credential(self, service):
        """Retrieve and decrypt credential"""
        encrypted = keyring.get_password("claude-mcp", service)
        if encrypted:
            return self.cipher.decrypt(encrypted.encode()).decode()
        return None

    def setup_all_credentials(self):
        """Interactive setup for all MCP credentials"""
        services = {
            'github': 'GitHub Personal Access Token',
            'postgres': 'PostgreSQL Connection String',
            'brave': 'Brave Search API Key',
            'exa': 'EXA API Key'
        }

        for service, description in services.items():
            current = self.get_credential(service)
            if current:
                print(f"✅ {description} already configured")
            else:
                value = input(f"Enter {description}: ")
                if value:
                    self.store_credential(service, value)
                    print(f"✅ {description} stored securely")

# Usage
manager = CredentialManager()
manager.setup_all_credentials()
```

#### Solution 2: Token Refresh

```bash
# Auto-refresh script
#!/bin/bash
# refresh_tokens.sh

# GitHub token refresh (using GitHub CLI)
gh auth refresh

# Update environment
export GITHUB_TOKEN=$(gh auth token)

# Reload MCP configurations
/reload-mcp-config

# Test all authentications
/test-mcp-auth --all
```

## Timeout Issues

### Problem
MCP server operations timeout or take too long to respond.

### Symptoms
- "Operation timed out" errors
- Slow response times
- Hanging operations
- Connection drops

### Solutions

#### Solution 1: Adjust Timeout Settings

```json
// .claude/mcp-config.json
{
  "defaults": {
    "timeout": 30000,  // 30 seconds
    "retries": 3,
    "retryDelay": 1000
  },
  "servers": {
    "playwright": {
      "timeout": 60000,  // 1 minute for browser operations
      "options": {
        "headless": true,
        "slowMo": 0
      }
    },
    "postgres": {
      "timeout": 15000,
      "connectionTimeout": 5000,
      "statementTimeout": 10000
    },
    "github": {
      "timeout": 20000,
      "rateLimit": {
        "maxRequests": 5000,
        "perHour": true
      }
    }
  }
}
```

#### Solution 2: Optimize Queries

```python
# optimize_mcp_operations.py

class MCPOptimizer:
    """Optimize MCP server operations"""

    def optimize_playwright(self):
        """Optimize Playwright operations"""
        return {
            'headless': True,
            'viewport': {'width': 1280, 'height': 720},
            'userAgent': 'Mozilla/5.0 (optimized)',
            'ignoreHTTPSErrors': True,
            'args': [
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        }

    def optimize_postgres_query(self, query):
        """Optimize PostgreSQL queries"""
        # Add query timeout
        optimized = f"SET statement_timeout = '10s'; {query}"

        # Add LIMIT if SELECT without LIMIT
        if 'SELECT' in query.upper() and 'LIMIT' not in query.upper():
            optimized += ' LIMIT 1000'

        return optimized

    def batch_github_requests(self, requests):
        """Batch GitHub API requests"""
        # Use GraphQL for multiple queries
        graphql_query = """
        query BatchRequest {
          %s
        }
        """ % '\n'.join(requests)

        return graphql_query
```

#### Solution 3: Connection Pooling

```javascript
// connection_pool.js
class MCPConnectionPool {
    constructor(serverType, options = {}) {
        this.serverType = serverType;
        this.pool = [];
        this.maxConnections = options.maxConnections || 5;
        this.timeout = options.timeout || 30000;
    }

    async getConnection() {
        // Reuse existing connection
        const available = this.pool.find(conn => !conn.inUse);
        if (available) {
            available.inUse = true;
            return available;
        }

        // Create new connection if under limit
        if (this.pool.length < this.maxConnections) {
            const conn = await this.createConnection();
            this.pool.push(conn);
            return conn;
        }

        // Wait for available connection
        return this.waitForConnection();
    }

    async createConnection() {
        const conn = {
            id: Date.now(),
            server: this.serverType,
            inUse: true,
            created: new Date(),
            lastUsed: new Date()
        };

        // Server-specific initialization
        switch(this.serverType) {
            case 'postgres':
                conn.client = await this.createPostgresClient();
                break;
            case 'playwright':
                conn.browser = await this.createPlaywrightBrowser();
                break;
        }

        return conn;
    }

    async waitForConnection() {
        const start = Date.now();
        while (Date.now() - start < this.timeout) {
            const available = this.pool.find(conn => !conn.inUse);
            if (available) {
                available.inUse = true;
                return available;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        throw new Error('Connection pool timeout');
    }

    releaseConnection(conn) {
        conn.inUse = false;
        conn.lastUsed = new Date();
    }
}
```

## Performance Problems

### Problem
MCP servers exhibit poor performance or resource consumption.

### Symptoms
- High CPU usage
- Memory leaks
- Slow operations
- System lag

### Server-Specific Performance Issues

#### Playwright/Puppeteer Performance

```javascript
// playwright_performance.js
const optimizedConfig = {
    // Reduce resource usage
    launchOptions: {
        headless: true,
        args: [
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials'
        ]
    },

    // Context options
    contextOptions: {
        viewport: { width: 1280, height: 720 },
        deviceScaleFactor: 1,
        hasTouch: false,
        javascriptEnabled: true,
        ignoreHTTPSErrors: true
    },

    // Resource blocking
    routePatterns: [
        { pattern: /\.(png|jpg|jpeg|gif|webp|svg)$/i, action: 'abort' },
        { pattern: /\.(css|font|woff|woff2)$/i, action: 'abort' },
        { pattern: /google-analytics\.com/i, action: 'abort' }
    ]
};

// Apply optimizations
async function optimizeBrowser(browser) {
    const context = await browser.newContext(optimizedConfig.contextOptions);
    const page = await context.newPage();

    // Block unnecessary resources
    await page.route('**/*', route => {
        const url = route.request().url();
        for (const pattern of optimizedConfig.routePatterns) {
            if (pattern.pattern.test(url)) {
                return route.abort();
            }
        }
        return route.continue();
    });

    return page;
}
```

#### PostgreSQL Performance

```sql
-- Performance tuning queries
-- Check slow queries
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- Connection pool settings
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

#### Memory MCP Performance

```python
# memory_optimization.py
import gc
import psutil
import resource

class MemoryOptimizer:
    """Optimize memory usage for MCP servers"""

    def __init__(self):
        self.initial_memory = self.get_memory_usage()
        self.set_memory_limits()

    def set_memory_limits(self):
        """Set memory limits for the process"""
        # Set soft and hard limits (1GB)
        resource.setrlimit(
            resource.RLIMIT_AS,
            (1024 * 1024 * 1024, 1024 * 1024 * 1024)
        )

    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB

    def cleanup(self):
        """Force garbage collection"""
        gc.collect()
        gc.collect()  # Run twice for thorough cleanup

    def monitor_memory(self, threshold_mb=500):
        """Monitor and clean if threshold exceeded"""
        current = self.get_memory_usage()
        if current > threshold_mb:
            print(f"Memory usage high: {current:.2f}MB")
            self.cleanup()
            new = self.get_memory_usage()
            print(f"After cleanup: {new:.2f}MB")
            return True
        return False

# Usage
optimizer = MemoryOptimizer()
# Run periodically
optimizer.monitor_memory()
```

### General Performance Solutions

#### Solution 1: Resource Monitoring

```bash
#!/bin/bash
# monitor_mcp_resources.sh

monitor_server() {
    local server=$1
    local pid=$(pgrep -f "mcp-server-$server")

    if [ -z "$pid" ]; then
        echo "Server $server not running"
        return
    fi

    echo "Monitoring $server (PID: $pid)"
    echo "------------------------"

    # CPU and Memory
    ps -p $pid -o %cpu,%mem,vsz,rss,comm

    # Open files
    lsof -p $pid | wc -l

    # Network connections
    netstat -np 2>/dev/null | grep $pid | wc -l

    echo ""
}

# Monitor all servers
for server in filesystem github playwright postgres; do
    monitor_server $server
done

# System resources
echo "System Resources"
echo "------------------------"
free -h
df -h
uptime
```

#### Solution 2: Caching Strategy

```python
# caching_strategy.py
from functools import lru_cache
import hashlib
import json
import redis
import time

class MCPCache:
    """Intelligent caching for MCP operations"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.ttl = 3600  # 1 hour default

    def cache_key(self, server, operation, params):
        """Generate cache key"""
        data = f"{server}:{operation}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    def get(self, server, operation, params):
        """Get cached result"""
        key = self.cache_key(server, operation, params)
        result = self.redis_client.get(key)
        if result:
            return json.loads(result)
        return None

    def set(self, server, operation, params, result):
        """Cache result"""
        key = self.cache_key(server, operation, params)
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(result)
        )

    def invalidate(self, server=None):
        """Invalidate cache"""
        if server:
            pattern = f"{server}:*"
        else:
            pattern = "*"

        for key in self.redis_client.scan_iter(pattern):
            self.redis_client.delete(key)

    @lru_cache(maxsize=100)
    def should_cache(self, server, operation):
        """Determine if operation should be cached"""
        # Don't cache write operations
        no_cache = ['create', 'update', 'delete', 'write']
        if any(nc in operation.lower() for nc in no_cache):
            return False

        # Server-specific rules
        cache_rules = {
            'filesystem': ['read', 'list', 'stat'],
            'github': ['get_repo', 'list_repos', 'get_user'],
            'postgres': ['select', 'count'],
            'playwright': []  # Don't cache browser operations
        }

        if server in cache_rules:
            return any(rule in operation.lower()
                      for rule in cache_rules[server])

        return True
```

## Server-Specific Troubleshooting

### Filesystem MCP

**Common Issues:**
1. Permission denied on file operations
2. Path not allowed
3. Symlink resolution failures

**Solutions:**
```bash
# Fix permissions
chmod -R 755 ~/projects

# Update allowed paths
export MCP_FS_ALLOWED_PATHS="/home/user/projects,/tmp,/var/data"

# Enable symlink following
export MCP_FS_FOLLOW_SYMLINKS=true
```

### GitHub MCP

**Common Issues:**
1. Rate limit exceeded
2. Repository access denied
3. Large file timeouts

**Solutions:**
```python
# github_troubleshoot.py
import time
from github import Github

def handle_rate_limit(func):
    """Decorator to handle GitHub rate limits"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if 'rate limit' in str(e).lower():
                # Wait for rate limit reset
                g = Github(auth=kwargs.get('token'))
                reset_time = g.get_rate_limit().core.reset
                wait_time = (reset_time - datetime.now()).seconds
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                return func(*args, **kwargs)
            raise
    return wrapper
```

### Playwright MCP

**Common Issues:**
1. Browser crashes
2. Element not found
3. Navigation timeouts

**Solutions:**
```javascript
// playwright_fixes.js
async function robustClick(page, selector, options = {}) {
    const defaults = {
        timeout: 30000,
        retries: 3,
        delay: 1000
    };
    options = { ...defaults, ...options };

    for (let i = 0; i < options.retries; i++) {
        try {
            await page.waitForSelector(selector, {
                timeout: options.timeout,
                state: 'visible'
            });
            await page.click(selector);
            return;
        } catch (error) {
            console.log(`Attempt ${i + 1} failed: ${error.message}`);
            if (i < options.retries - 1) {
                await page.waitForTimeout(options.delay);
            } else {
                throw error;
            }
        }
    }
}
```

### Sequential Thinking MCP

**Common Issues:**
1. Token limit exceeded
2. Circular reasoning
3. Memory overflow

**Solutions:**
```python
# sequential_thinking_fixes.py
class ThinkingOptimizer:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
        self.thought_history = []

    def compress_context(self, thoughts):
        """Compress thoughts to fit token limit"""
        # Summarize older thoughts
        if len(thoughts) > 10:
            summary = self.summarize_thoughts(thoughts[:-5])
            return [summary] + thoughts[-5:]
        return thoughts

    def detect_loops(self, new_thought):
        """Detect circular reasoning"""
        for old_thought in self.thought_history[-5:]:
            similarity = self.calculate_similarity(new_thought, old_thought)
            if similarity > 0.9:
                return True
        return False

    def reset_if_needed(self):
        """Reset thinking context if needed"""
        if len(self.thought_history) > 50:
            self.thought_history = self.thought_history[-10:]
```

## Diagnostics and Testing

### Comprehensive MCP Diagnostics

```bash
#!/bin/bash
# diagnose_mcp.sh

echo "MCP Server Diagnostics"
echo "====================="

# Function to test MCP server
test_mcp_server() {
    local server=$1
    echo ""
    echo "Testing $server..."
    echo "-----------------"

    # Check if process is running
    if pgrep -f "mcp-server-$server" > /dev/null; then
        echo "✅ Process running"
    else
        echo "❌ Process not found"
        return 1
    fi

    # Test connection
    if /test-mcp $server 2>/dev/null | grep -q "success"; then
        echo "✅ Connection successful"
    else
        echo "❌ Connection failed"
    fi

    # Check logs
    log_file="$HOME/.claude/logs/mcp-$server.log"
    if [ -f "$log_file" ]; then
        errors=$(grep -c ERROR "$log_file" 2>/dev/null)
        echo "⚠️  Errors in log: $errors"
        if [ $errors -gt 0 ]; then
            echo "Recent errors:"
            tail -n 5 "$log_file" | grep ERROR
        fi
    fi

    # Server-specific tests
    case $server in
        filesystem)
            echo "Testing file operations..."
            /test-mcp filesystem --operation read --path /tmp/test
            ;;
        github)
            echo "Testing GitHub API..."
            /test-mcp github --operation get-user
            ;;
        postgres)
            echo "Testing database connection..."
            /test-mcp postgres --query "SELECT 1"
            ;;
        playwright)
            echo "Testing browser launch..."
            /test-mcp playwright --operation launch
            ;;
    esac
}

# Test all servers
servers=(filesystem github playwright sequential-thinking postgres brave-search exa memory puppeteer)

for server in "${servers[@]}"; do
    test_mcp_server "$server"
done

echo ""
echo "Summary"
echo "-------"
echo "Run '/fix-mcp-issues' to attempt automatic fixes"
```

### Automated Fix Script

```python
# fix_mcp_issues.py
#!/usr/bin/env python3

import subprocess
import os
import sys
import time

class MCPFixer:
    """Automated MCP issue resolver"""

    def __init__(self):
        self.servers = [
            'filesystem', 'github', 'playwright',
            'sequential-thinking', 'postgres', 'brave-search',
            'exa', 'memory', 'puppeteer'
        ]
        self.fixed = []
        self.failed = []

    def fix_all(self):
        """Attempt to fix all MCP issues"""
        print("Starting MCP automatic repair...")
        print("=" * 50)

        for server in self.servers:
            if self.fix_server(server):
                self.fixed.append(server)
            else:
                self.failed.append(server)

        self.print_summary()

    def fix_server(self, server):
        """Fix specific server issues"""
        print(f"\nFixing {server}...")

        # Stop server
        self.stop_server(server)
        time.sleep(2)

        # Clear cache/locks
        self.clear_server_cache(server)

        # Fix permissions
        self.fix_permissions(server)

        # Reinstall if needed
        if not self.verify_installation(server):
            self.reinstall_server(server)

        # Start server
        self.start_server(server)
        time.sleep(3)

        # Test connection
        return self.test_connection(server)

    def stop_server(self, server):
        """Stop MCP server process"""
        subprocess.run(['pkill', '-f', f'mcp-server-{server}'],
                      capture_output=True)

    def start_server(self, server):
        """Start MCP server"""
        subprocess.run(['/start-mcp', server],
                      capture_output=True)

    def clear_server_cache(self, server):
        """Clear server cache and locks"""
        cache_dir = f"~/.claude/cache/{server}"
        lock_file = f"~/.claude/locks/{server}.lock"

        os.system(f"rm -rf {cache_dir}")
        os.system(f"rm -f {lock_file}")

    def fix_permissions(self, server):
        """Fix file permissions"""
        server_dir = f"~/.claude/mcp-servers/{server}"
        os.system(f"chmod -R 755 {server_dir}")

    def verify_installation(self, server):
        """Verify server installation"""
        server_dir = os.path.expanduser(f"~/.claude/mcp-servers/{server}")
        return os.path.exists(server_dir)

    def reinstall_server(self, server):
        """Reinstall MCP server"""
        print(f"  Reinstalling {server}...")
        subprocess.run(['/install-mcp', server],
                      capture_output=True)

    def test_connection(self, server):
        """Test server connection"""
        result = subprocess.run(['/test-mcp', server],
                              capture_output=True,
                              text=True)
        return 'success' in result.stdout.lower()

    def print_summary(self):
        """Print fix summary"""
        print("\n" + "=" * 50)
        print("MCP Fix Summary")
        print("=" * 50)

        if self.fixed:
            print(f"✅ Fixed: {', '.join(self.fixed)}")

        if self.failed:
            print(f"❌ Failed: {', '.join(self.failed)}")
            print("\nFor failed servers, try:")
            print("1. Check logs: /show-logs mcp-<server>")
            print("2. Reinstall: /reinstall-mcp <server>")
            print("3. Check credentials: /check-mcp-auth <server>")

if __name__ == "__main__":
    fixer = MCPFixer()
    fixer.fix_all()
```

## Prevention and Best Practices

### MCP Health Monitoring

```yaml
# mcp-monitoring.yaml
monitoring:
  interval: 60  # seconds
  alerts:
    enabled: true
    channels: [email, slack]

  checks:
    - type: connection
      servers: all
      timeout: 5000
      alert_on_failure: true

    - type: performance
      metric: response_time
      threshold: 1000  # ms
      alert_on_exceed: true

    - type: resource
      metric: memory_usage
      threshold: 512  # MB
      alert_on_exceed: true

    - type: error_rate
      threshold: 0.05  # 5%
      window: 300  # 5 minutes
      alert_on_exceed: true

  auto_recovery:
    enabled: true
    actions:
      connection_failure: restart
      high_memory: restart
      high_error_rate: reset
```

### MCP Backup and Recovery

```bash
#!/bin/bash
# backup_mcp.sh

# Backup MCP configurations
backup_dir="$HOME/.claude/backups/mcp-$(date +%Y%m%d)"
mkdir -p "$backup_dir"

# Backup configurations
cp -r ~/.claude/mcp-servers "$backup_dir/"
cp ~/.claude/settings.json "$backup_dir/"
cp ~/.env "$backup_dir/.env.backup"

# Backup credentials (encrypted)
gpg --encrypt --recipient your-email@example.com \
    ~/.claude/credentials.json > "$backup_dir/credentials.gpg"

echo "Backup created: $backup_dir"

# Restore function
restore_mcp() {
    local backup_date=$1
    local backup_dir="$HOME/.claude/backups/mcp-$backup_date"

    if [ ! -d "$backup_dir" ]; then
        echo "Backup not found: $backup_dir"
        return 1
    fi

    # Stop all MCP servers
    /stop-all-mcps

    # Restore configurations
    cp -r "$backup_dir/mcp-servers" ~/.claude/
    cp "$backup_dir/settings.json" ~/.claude/
    cp "$backup_dir/.env.backup" ~/.env

    # Restore credentials
    gpg --decrypt "$backup_dir/credentials.gpg" > ~/.claude/credentials.json

    # Restart servers
    /start-all-mcps

    echo "Restored from: $backup_dir"
}
```

## Summary

MCP server issues typically involve:

1. **Connection Problems** - Network, firewall, or process issues
2. **Authentication Failures** - Invalid or expired credentials
3. **Timeouts** - Slow operations or network latency
4. **Performance Issues** - Resource consumption or inefficient operations
5. **Server-Specific Problems** - Unique to each MCP implementation

Key troubleshooting steps:
1. Check server status and logs
2. Verify credentials and permissions
3. Test connectivity and operations
4. Monitor resource usage
5. Apply server-specific fixes

Always maintain backups and implement monitoring to prevent and quickly resolve MCP issues.
