# Hook Troubleshooting Guide

## Overview

This guide addresses common issues with hooks in the Claude Code Context Engineering system, covering execution failures, configuration problems, and performance issues.

## Hook Execution Failures

### Problem
Hooks fail to execute or produce errors during execution.

### Symptoms
- Hook scripts not running
- Error messages during hook execution
- Partial execution or unexpected termination
- Silent failures with no output

### Root Causes

1. **Script Errors** - Syntax or runtime errors in hook code
2. **Permission Issues** - Insufficient execution permissions
3. **Missing Dependencies** - Required tools or libraries not available
4. **Path Problems** - Incorrect working directory or file paths
5. **Environment Issues** - Missing environment variables

### Solutions

#### Solution 1: Debug Hook Execution

```bash
# Enable hook debugging
export HOOK_DEBUG=true

# Test specific hook
/test-hook pre-command

# View hook execution log
/hook-log --last 10

# Trace hook execution
/trace-hook pre-command --verbose
```

**Debug Script:**
```bash
#!/bin/bash
# debug_hook.sh - Add to beginning of hook scripts

set -x  # Enable debug output
set -e  # Exit on error
set -u  # Error on undefined variables
set -o pipefail  # Pipe failures cause exit

# Log execution details
echo "Hook executing at: $(date)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Environment: ${NODE_ENV:-not set}"
echo "Arguments: $@"

# Trap errors
trap 'echo "Error on line $LINENO"' ERR
```

#### Solution 2: Fix Common Script Errors

```python
# hook_validator.py
import subprocess
import os
import sys
import ast

class HookValidator:
    """Validate and fix hook scripts"""

    def validate_bash_hook(self, script_path):
        """Validate bash script syntax"""
        result = subprocess.run(
            ['bash', '-n', script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Syntax error in {script_path}:")
            print(result.stderr)
            return False

        print(f"✅ {script_path} syntax valid")
        return True

    def validate_python_hook(self, script_path):
        """Validate Python script syntax"""
        try:
            with open(script_path, 'r') as f:
                ast.parse(f.read())
            print(f"✅ {script_path} syntax valid")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error in {script_path}:")
            print(f"  Line {e.lineno}: {e.msg}")
            return False

    def validate_node_hook(self, script_path):
        """Validate Node.js script syntax"""
        result = subprocess.run(
            ['node', '--check', script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Syntax error in {script_path}:")
            print(result.stderr)
            return False

        print(f"✅ {script_path} syntax valid")
        return True

    def fix_common_issues(self, script_path):
        """Fix common hook script issues"""
        with open(script_path, 'r') as f:
            content = f.read()

        fixes_applied = []

        # Add shebang if missing (bash)
        if script_path.endswith('.sh') and not content.startswith('#!'):
            content = '#!/bin/bash\n' + content
            fixes_applied.append("Added shebang")

        # Fix line endings
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            fixes_applied.append("Fixed line endings")

        # Ensure final newline
        if not content.endswith('\n'):
            content += '\n'
            fixes_applied.append("Added final newline")

        if fixes_applied:
            with open(script_path, 'w') as f:
                f.write(content)
            print(f"Applied fixes to {script_path}: {', '.join(fixes_applied)}")

        return len(fixes_applied) > 0

# Usage
validator = HookValidator()
hooks_dir = '.claude/hooks'

for hook_file in os.listdir(hooks_dir):
    hook_path = os.path.join(hooks_dir, hook_file)

    if hook_file.endswith('.sh'):
        validator.validate_bash_hook(hook_path)
    elif hook_file.endswith('.py'):
        validator.validate_python_hook(hook_path)
    elif hook_file.endswith('.js'):
        validator.validate_node_hook(hook_path)

    validator.fix_common_issues(hook_path)
```

#### Solution 3: Fix Permission Issues

```bash
# Fix hook permissions
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py

# Fix directory permissions
chmod 755 .claude/hooks

# Check effective permissions
ls -la .claude/hooks/

# Test execution permission
.claude/hooks/pre-command.sh test

# Fix SELinux context (if applicable)
restorecon -R .claude/hooks/
```

#### Solution 4: Resolve Dependency Issues

```bash
#!/bin/bash
# check_hook_dependencies.sh

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Missing: $1"
        return 1
    else
        echo "✅ Found: $1 ($(command -v $1))"
        return 0
    fi
}

echo "Checking hook dependencies..."
echo "============================"

# Common dependencies
dependencies=(
    "bash"
    "python3"
    "node"
    "git"
    "jq"
    "curl"
    "grep"
    "sed"
    "awk"
)

missing=0
for dep in "${dependencies[@]}"; do
    if ! check_command "$dep"; then
        ((missing++))
    fi
done

if [ $missing -gt 0 ]; then
    echo ""
    echo "Install missing dependencies:"
    echo "  Ubuntu/Debian: apt-get install <package>"
    echo "  macOS: brew install <package>"
    echo "  Windows: choco install <package>"
    exit 1
else
    echo ""
    echo "All dependencies satisfied!"
fi
```

## Timeout Issues

### Problem
Hooks timeout during execution or take too long to complete.

### Symptoms
- "Hook execution timeout" errors
- Hooks terminated before completion
- Slow hook execution
- System hangs during hook execution

### Solutions

#### Solution 1: Configure Timeout Settings

```yaml
# .claude/hooks/config.yaml
hooks:
  global:
    timeout: 30000  # 30 seconds default
    kill_timeout: 35000  # Force kill after 35 seconds

  specific:
    pre-command:
      timeout: 10000  # Quick validation

    post-command:
      timeout: 60000  # Longer for cleanup

    pre-deploy:
      timeout: 300000  # 5 minutes for deployment prep

    test-suite:
      timeout: 600000  # 10 minutes for full tests
```

#### Solution 2: Optimize Hook Performance

```python
# optimize_hooks.py
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError

class HookOptimizer:
    """Optimize hook execution performance"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def run_hook_with_timeout(self, hook_path, timeout=30):
        """Run hook with timeout and monitoring"""
        start_time = time.time()

        try:
            # Run hook in thread pool to avoid blocking
            future = self.executor.submit(self.execute_hook, hook_path)

            # Wait with timeout
            result = await asyncio.wait_for(
                asyncio.wrap_future(future),
                timeout=timeout
            )

            execution_time = time.time() - start_time
            print(f"✅ Hook completed in {execution_time:.2f}s")

            return result

        except asyncio.TimeoutError:
            print(f"❌ Hook timeout after {timeout}s")
            # Attempt graceful shutdown
            self.graceful_shutdown(hook_path)
            raise

        except Exception as e:
            print(f"❌ Hook failed: {e}")
            raise

    def execute_hook(self, hook_path):
        """Execute hook script"""
        import subprocess

        result = subprocess.run(
            [hook_path],
            capture_output=True,
            text=True,
            timeout=None  # Managed by asyncio
        )

        if result.returncode != 0:
            raise Exception(f"Hook failed: {result.stderr}")

        return result.stdout

    def graceful_shutdown(self, hook_path):
        """Attempt graceful shutdown of hanging hook"""
        import signal
        import psutil

        # Find processes spawned by hook
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if hook_path in ' '.join(proc.info['cmdline'] or []):
                    print(f"Terminating process {proc.info['pid']}")
                    proc.send_signal(signal.SIGTERM)
                    proc.wait(timeout=5)
            except:
                pass

# Usage
async def main():
    optimizer = HookOptimizer()
    await optimizer.run_hook_with_timeout(
        '.claude/hooks/pre-command.sh',
        timeout=10
    )

asyncio.run(main())
```

#### Solution 3: Parallel Hook Execution

```javascript
// parallel_hooks.js
const { spawn } = require('child_process');
const path = require('path');

class ParallelHookRunner {
    constructor() {
        this.maxParallel = 4;
        this.timeout = 30000;
    }

    async runHooks(hookType) {
        const hooks = this.getHooks(hookType);

        if (hooks.length === 0) {
            console.log(`No ${hookType} hooks found`);
            return;
        }

        console.log(`Running ${hooks.length} ${hookType} hooks in parallel...`);

        // Group hooks by dependency
        const independent = hooks.filter(h => !h.depends);
        const dependent = hooks.filter(h => h.depends);

        // Run independent hooks in parallel
        const results = await this.runParallel(independent);

        // Run dependent hooks sequentially
        for (const hook of dependent) {
            await this.runSingle(hook);
        }

        return results;
    }

    async runParallel(hooks) {
        const promises = hooks.map(hook =>
            this.runSingle(hook)
        );

        return Promise.all(promises);
    }

    async runSingle(hook) {
        return new Promise((resolve, reject) => {
            const child = spawn(hook.path, hook.args || []);
            const timeout = setTimeout(() => {
                child.kill('SIGTERM');
                reject(new Error(`Hook timeout: ${hook.name}`));
            }, hook.timeout || this.timeout);

            let output = '';
            child.stdout.on('data', (data) => {
                output += data;
            });

            child.on('close', (code) => {
                clearTimeout(timeout);
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`Hook failed: ${hook.name} (exit ${code})`));
                }
            });
        });
    }

    getHooks(hookType) {
        // Load hooks from configuration
        const hooksDir = path.join('.claude', 'hooks');
        const fs = require('fs');

        return fs.readdirSync(hooksDir)
            .filter(file => file.startsWith(hookType))
            .map(file => ({
                name: file,
                path: path.join(hooksDir, file),
                timeout: this.timeout
            }));
    }
}

// Usage
const runner = new ParallelHookRunner();
runner.runHooks('pre-command')
    .then(() => console.log('Hooks completed'))
    .catch(err => console.error('Hook execution failed:', err));
```

## Configuration Errors

### Problem
Hook configuration is incorrect or invalid.

### Symptoms
- Hooks not recognized
- Wrong trigger conditions
- Missing hook definitions
- Configuration parse errors

### Solutions

#### Solution 1: Validate Hook Configuration

```yaml
# .claude/hooks/hooks.yaml - Correct configuration
version: "1.0"

hooks:
  # Command hooks
  pre-command:
    enabled: true
    scripts:
      - path: ./validate-command.sh
        timeout: 5000
        required: true
      - path: ./log-command.py
        timeout: 2000
        required: false

  post-command:
    enabled: true
    scripts:
      - path: ./cleanup.sh
        timeout: 10000
        on_error: continue

  # File hooks
  pre-save:
    enabled: true
    patterns:
      - "*.py"
      - "*.js"
    scripts:
      - path: ./format-code.sh
      - path: ./lint-code.sh

  post-save:
    enabled: true
    scripts:
      - path: ./update-index.py
      - path: ./git-add.sh

  # Deployment hooks
  pre-deploy:
    enabled: true
    environments:
      - staging
      - production
    scripts:
      - path: ./run-tests.sh
        required: true
        stop_on_failure: true
      - path: ./build-assets.sh
      - path: ./validate-config.py

  # Error hooks
  on-error:
    enabled: true
    scripts:
      - path: ./capture-error.sh
      - path: ./notify-team.py

# Hook conditions
conditions:
  business_hours:
    days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
    hours: "09:00-17:00"
    timezone: "America/New_York"

  critical_operations:
    commands:
      - deploy
      - migrate
      - delete
    require_confirmation: true
```

#### Solution 2: Fix Configuration Parsing

```python
# fix_hook_config.py
import yaml
import json
import os
from typing import Dict, List

class HookConfigFixer:
    """Fix and validate hook configuration"""

    def __init__(self, config_path='.claude/hooks/hooks.yaml'):
        self.config_path = config_path
        self.valid_hook_types = [
            'pre-command', 'post-command',
            'pre-save', 'post-save',
            'pre-deploy', 'post-deploy',
            'on-error', 'on-success'
        ]

    def load_config(self) -> Dict:
        """Load and parse configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ YAML parsing error: {e}")
            return self.fix_yaml_errors()
        except FileNotFoundError:
            print("❌ Configuration file not found")
            return self.create_default_config()

    def fix_yaml_errors(self) -> Dict:
        """Attempt to fix common YAML errors"""
        with open(self.config_path, 'r') as f:
            content = f.read()

        # Fix common issues
        # Remove tabs
        content = content.replace('\t', '  ')

        # Fix incorrect indentation
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            # Ensure consistent indentation
            if line.strip() and not line.startswith('#'):
                indent = len(line) - len(line.lstrip())
                if indent % 2 != 0:
                    line = ' ' + line
            fixed_lines.append(line)

        fixed_content = '\n'.join(fixed_lines)

        try:
            return yaml.safe_load(fixed_content)
        except:
            return self.create_default_config()

    def create_default_config(self) -> Dict:
        """Create default hook configuration"""
        default = {
            'version': '1.0',
            'hooks': {
                'pre-command': {
                    'enabled': True,
                    'scripts': []
                },
                'post-command': {
                    'enabled': True,
                    'scripts': []
                }
            }
        }

        # Save default configuration
        with open(self.config_path, 'w') as f:
            yaml.dump(default, f, default_flow_style=False)

        print("✅ Created default hook configuration")
        return default

    def validate_config(self, config: Dict) -> List[str]:
        """Validate hook configuration"""
        errors = []

        # Check version
        if 'version' not in config:
            errors.append("Missing 'version' field")

        # Check hooks section
        if 'hooks' not in config:
            errors.append("Missing 'hooks' section")
        else:
            for hook_type, hook_config in config['hooks'].items():
                if hook_type not in self.valid_hook_types:
                    errors.append(f"Unknown hook type: {hook_type}")

                if 'scripts' in hook_config:
                    for script in hook_config['scripts']:
                        if 'path' not in script:
                            errors.append(f"Missing 'path' in {hook_type} script")
                        elif not os.path.exists(script['path']):
                            errors.append(f"Script not found: {script['path']}")

        return errors

    def fix_and_validate(self):
        """Load, fix, and validate configuration"""
        config = self.load_config()
        errors = self.validate_config(config)

        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"  - {error}")

            # Attempt auto-fix
            self.auto_fix_errors(config, errors)
        else:
            print("✅ Hook configuration is valid")

        return config

    def auto_fix_errors(self, config: Dict, errors: List[str]):
        """Attempt to automatically fix errors"""
        fixes_applied = []

        for error in errors:
            if "Missing 'version'" in error:
                config['version'] = '1.0'
                fixes_applied.append("Added version field")

            elif "Script not found" in error:
                # Create missing script with template
                script_path = error.split(': ')[1]
                self.create_hook_template(script_path)
                fixes_applied.append(f"Created template: {script_path}")

        if fixes_applied:
            # Save fixed configuration
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            print(f"✅ Applied {len(fixes_applied)} fixes:")
            for fix in fixes_applied:
                print(f"  - {fix}")

    def create_hook_template(self, script_path: str):
        """Create hook script template"""
        os.makedirs(os.path.dirname(script_path), exist_ok=True)

        if script_path.endswith('.sh'):
            template = '''#!/bin/bash
# Hook script: {name}
set -e

echo "Hook executing: $(basename $0)"
# Add your hook logic here

exit 0
'''.format(name=os.path.basename(script_path))

        elif script_path.endswith('.py'):
            template = '''#!/usr/bin/env python3
# Hook script: {name}
import sys
import os

def main():
    """Main hook logic"""
    print(f"Hook executing: {{os.path.basename(__file__)}}")
    # Add your hook logic here
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''.format(name=os.path.basename(script_path))

        else:
            template = '#!/bin/sh\n# Hook script\nexit 0\n'

        with open(script_path, 'w') as f:
            f.write(template)

        os.chmod(script_path, 0o755)
        print(f"✅ Created hook template: {script_path}")

# Usage
fixer = HookConfigFixer()
config = fixer.fix_and_validate()
```

## Hook Not Triggering

### Problem
Hooks are configured but not triggering when expected.

### Symptoms
- Hooks not running on events
- Missing hook execution logs
- Events processed without hooks
- Conditional hooks not firing

### Solutions

#### Solution 1: Debug Hook Triggers

```bash
# Enable hook trigger debugging
export HOOK_TRIGGER_DEBUG=true

# Monitor hook triggers in real-time
/monitor-hooks --live

# Check hook trigger history
/hook-history --last 20

# Test specific trigger
/trigger-hook pre-command --test
```

#### Solution 2: Fix Trigger Conditions

```javascript
// hook_trigger_manager.js
class HookTriggerManager {
    constructor() {
        this.hooks = this.loadHooks();
        this.enabled = true;
        this.debug = process.env.HOOK_TRIGGER_DEBUG === 'true';
    }

    shouldTrigger(hookType, context = {}) {
        if (!this.enabled) {
            this.log(`Hooks disabled globally`);
            return false;
        }

        const hook = this.hooks[hookType];
        if (!hook) {
            this.log(`No hook configured for: ${hookType}`);
            return false;
        }

        if (!hook.enabled) {
            this.log(`Hook disabled: ${hookType}`);
            return false;
        }

        // Check conditions
        if (hook.conditions) {
            return this.evaluateConditions(hook.conditions, context);
        }

        return true;
    }

    evaluateConditions(conditions, context) {
        // Check file patterns
        if (conditions.patterns && context.file) {
            const matches = conditions.patterns.some(pattern =>
                this.matchPattern(context.file, pattern)
            );
            if (!matches) {
                this.log(`File doesn't match patterns: ${context.file}`);
                return false;
            }
        }

        // Check environment
        if (conditions.environments && context.environment) {
            if (!conditions.environments.includes(context.environment)) {
                this.log(`Environment not matched: ${context.environment}`);
                return false;
            }
        }

        // Check time-based conditions
        if (conditions.schedule) {
            if (!this.isScheduledTime(conditions.schedule)) {
                this.log(`Not scheduled time`);
                return false;
            }
        }

        // Check command whitelist/blacklist
        if (conditions.commands) {
            if (conditions.commands.whitelist &&
                !conditions.commands.whitelist.includes(context.command)) {
                this.log(`Command not in whitelist: ${context.command}`);
                return false;
            }

            if (conditions.commands.blacklist &&
                conditions.commands.blacklist.includes(context.command)) {
                this.log(`Command in blacklist: ${context.command}`);
                return false;
            }
        }

        return true;
    }

    matchPattern(file, pattern) {
        // Convert glob pattern to regex
        const regex = pattern
            .replace(/\./g, '\\.')
            .replace(/\*/g, '.*')
            .replace(/\?/g, '.');
        return new RegExp(`^${regex}$`).test(file);
    }

    isScheduledTime(schedule) {
        const now = new Date();
        const hour = now.getHours();
        const day = now.getDay();

        if (schedule.hours) {
            const [startHour, endHour] = schedule.hours.split('-').map(Number);
            if (hour < startHour || hour > endHour) {
                return false;
            }
        }

        if (schedule.days) {
            const dayMap = {
                'Sun': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3,
                'Thu': 4, 'Fri': 5, 'Sat': 6
            };
            const allowedDays = schedule.days.map(d => dayMap[d]);
            if (!allowedDays.includes(day)) {
                return false;
            }
        }

        return true;
    }

    async trigger(hookType, context = {}) {
        if (!this.shouldTrigger(hookType, context)) {
            return { triggered: false };
        }

        this.log(`Triggering hook: ${hookType}`);

        const hook = this.hooks[hookType];
        const results = [];

        for (const script of hook.scripts) {
            try {
                const result = await this.executeScript(script, context);
                results.push({
                    script: script.path,
                    success: true,
                    output: result
                });
            } catch (error) {
                results.push({
                    script: script.path,
                    success: false,
                    error: error.message
                });

                if (script.required) {
                    throw new Error(`Required hook failed: ${script.path}`);
                }
            }
        }

        return { triggered: true, results };
    }

    log(message) {
        if (this.debug) {
            console.log(`[HookTrigger] ${message}`);
        }
    }
}

// Usage
const manager = new HookTriggerManager();

// Test trigger conditions
const context = {
    command: 'deploy',
    environment: 'production',
    file: 'main.py'
};

if (manager.shouldTrigger('pre-deploy', context)) {
    manager.trigger('pre-deploy', context)
        .then(result => console.log('Hook result:', result))
        .catch(err => console.error('Hook failed:', err));
}
```

## Performance Issues

### Problem
Hooks cause performance degradation or system slowdown.

### Symptoms
- Slow command execution
- High CPU/memory usage during hooks
- System lag when hooks run
- Queue buildup

### Solutions

#### Solution 1: Profile Hook Performance

```python
# profile_hooks.py
import time
import psutil
import cProfile
import pstats
import io
from contextlib import contextmanager

class HookProfiler:
    """Profile hook performance"""

    def __init__(self):
        self.profiles = {}
        self.metrics = {}

    @contextmanager
    def profile_hook(self, hook_name):
        """Profile hook execution"""
        # Start profiling
        profiler = cProfile.Profile()
        process = psutil.Process()

        start_time = time.time()
        start_cpu = process.cpu_percent()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB

        profiler.enable()

        yield

        # Stop profiling
        profiler.disable()

        end_time = time.time()
        end_cpu = process.cpu_percent()
        end_memory = process.memory_info().rss / 1024 / 1024

        # Calculate metrics
        self.metrics[hook_name] = {
            'duration': end_time - start_time,
            'cpu_usage': end_cpu - start_cpu,
            'memory_delta': end_memory - start_memory
        }

        # Store profile
        self.profiles[hook_name] = profiler

        # Print summary
        self.print_summary(hook_name)

    def print_summary(self, hook_name):
        """Print performance summary"""
        metrics = self.metrics[hook_name]

        print(f"\nPerformance Profile: {hook_name}")
        print("=" * 50)
        print(f"Duration: {metrics['duration']:.3f}s")
        print(f"CPU Usage: {metrics['cpu_usage']:.1f}%")
        print(f"Memory Delta: {metrics['memory_delta']:.2f}MB")

        # Print top functions
        if hook_name in self.profiles:
            s = io.StringIO()
            ps = pstats.Stats(
                self.profiles[hook_name],
                stream=s
            ).sort_stats('cumulative')
            ps.print_stats(10)

            print("\nTop 10 Functions by Time:")
            print(s.getvalue())

    def analyze_bottlenecks(self):
        """Analyze performance bottlenecks"""
        bottlenecks = []

        for hook, metrics in self.metrics.items():
            issues = []

            if metrics['duration'] > 5:
                issues.append(f"Slow execution: {metrics['duration']:.1f}s")

            if metrics['cpu_usage'] > 50:
                issues.append(f"High CPU: {metrics['cpu_usage']:.1f}%")

            if metrics['memory_delta'] > 100:
                issues.append(f"Memory leak: {metrics['memory_delta']:.1f}MB")

            if issues:
                bottlenecks.append({
                    'hook': hook,
                    'issues': issues
                })

        return bottlenecks

# Usage
profiler = HookProfiler()

# Profile a hook
with profiler.profile_hook('pre-command'):
    # Hook execution
    import subprocess
    subprocess.run(['.claude/hooks/pre-command.sh'])

# Analyze bottlenecks
bottlenecks = profiler.analyze_bottlenecks()
for bottleneck in bottlenecks:
    print(f"⚠️ {bottleneck['hook']}: {', '.join(bottleneck['issues'])}")
```

#### Solution 2: Optimize Hook Scripts

```bash
#!/bin/bash
# optimized_hook.sh - Optimized hook template

# Use efficient commands
# BAD: cat file | grep pattern
# GOOD: grep pattern file

# Cache expensive operations
CACHE_FILE="/tmp/hook_cache_$$"
if [ -f "$CACHE_FILE" ] && [ $(( $(date +%s) - $(stat -c %Y "$CACHE_FILE") )) -lt 300 ]; then
    # Use cache if less than 5 minutes old
    result=$(cat "$CACHE_FILE")
else
    # Perform expensive operation
    result=$(expensive_operation)
    echo "$result" > "$CACHE_FILE"
fi

# Use parallel processing
process_files() {
    local file=$1
    # Process file
    echo "Processing $file"
}

export -f process_files

# Process files in parallel
find . -name "*.py" | parallel -j 4 process_files

# Avoid unnecessary work
if [ "$SKIP_VALIDATION" = "true" ]; then
    exit 0
fi

# Use early exit
if ! command -v required_command &> /dev/null; then
    exit 0  # Exit gracefully if not applicable
fi

# Batch operations
files_to_process=""
for file in *.txt; do
    files_to_process="$files_to_process $file"
done

# Process all at once instead of one by one
if [ -n "$files_to_process" ]; then
    process_batch $files_to_process
fi
```

## Recovery Procedures

### Hook System Recovery

```bash
#!/bin/bash
# recover_hooks.sh

echo "Hook System Recovery"
echo "===================="

# Stop all running hooks
echo "Stopping running hooks..."
pkill -f ".claude/hooks"

# Clear hook locks
echo "Clearing hook locks..."
rm -f .claude/hooks/.lock*

# Reset hook state
echo "Resetting hook state..."
rm -f .claude/hooks/.state
echo '{"last_run": null, "errors": 0}' > .claude/hooks/.state

# Validate all hooks
echo "Validating hooks..."
for hook in .claude/hooks/*.sh; do
    if bash -n "$hook" 2>/dev/null; then
        echo "✅ Valid: $(basename $hook)"
    else
        echo "❌ Invalid: $(basename $hook)"
        mv "$hook" "$hook.disabled"
    fi
done

# Rebuild hook index
echo "Rebuilding hook index..."
/rebuild-hook-index

# Test core hooks
echo "Testing core hooks..."
/test-hook pre-command --quiet
/test-hook post-command --quiet

echo ""
echo "Recovery complete!"
echo "Run '/hook-status' to verify"
```

### Hook Rollback

```python
# rollback_hooks.py
import os
import shutil
import json
from datetime import datetime

class HookRollback:
    """Rollback hook changes"""

    def __init__(self):
        self.backup_dir = '.claude/hooks/.backups'
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_current(self):
        """Backup current hooks"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, timestamp)

        shutil.copytree('.claude/hooks', backup_path,
                       ignore=shutil.ignore_patterns('.backups'))

        print(f"✅ Backed up to: {backup_path}")
        return backup_path

    def list_backups(self):
        """List available backups"""
        backups = []
        for backup in os.listdir(self.backup_dir):
            path = os.path.join(self.backup_dir, backup)
            if os.path.isdir(path):
                backups.append({
                    'timestamp': backup,
                    'path': path,
                    'size': sum(os.path.getsize(os.path.join(dirpath, f))
                               for dirpath, _, files in os.walk(path)
                               for f in files)
                })

        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

    def rollback_to(self, timestamp):
        """Rollback to specific backup"""
        backup_path = os.path.join(self.backup_dir, timestamp)

        if not os.path.exists(backup_path):
            raise ValueError(f"Backup not found: {timestamp}")

        # Backup current before rollback
        self.backup_current()

        # Clear current hooks (except backups)
        for item in os.listdir('.claude/hooks'):
            if item != '.backups':
                path = os.path.join('.claude/hooks', item)
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

        # Restore from backup
        for item in os.listdir(backup_path):
            src = os.path.join(backup_path, item)
            dst = os.path.join('.claude/hooks', item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst)

        print(f"✅ Rolled back to: {timestamp}")

# Usage
rollback = HookRollback()

# Backup before changes
rollback.backup_current()

# List backups
backups = rollback.list_backups()
for backup in backups[:5]:
    print(f"{backup['timestamp']} - {backup['size']} bytes")

# Rollback if needed
# rollback.rollback_to('20240115_143000')
```

## Best Practices

### Hook Development Guidelines

```markdown
# Hook Development Best Practices

## 1. Structure
- Keep hooks small and focused
- One responsibility per hook
- Use functions for reusability
- Follow naming conventions

## 2. Error Handling
- Always check return codes
- Provide meaningful error messages
- Use proper exit codes
- Log errors appropriately

## 3. Performance
- Avoid blocking operations
- Use timeouts for external calls
- Cache expensive computations
- Clean up resources

## 4. Security
- Validate all inputs
- Don't store secrets in hooks
- Use proper permissions
- Avoid command injection

## 5. Testing
- Test hooks in isolation
- Use test mode flags
- Validate with different inputs
- Check edge cases

## 6. Documentation
- Comment complex logic
- Document dependencies
- Provide usage examples
- Maintain changelog
```

### Hook Template

```bash
#!/bin/bash
# hook_template.sh - Production-ready hook template

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Configuration
readonly SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
readonly LOG_FILE="${SCRIPT_DIR}/.logs/${SCRIPT_NAME}.log"
readonly TIMEOUT=${HOOK_TIMEOUT:-30}

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    log "ERROR: $*" >&2
    exit 1
}

# Cleanup function
cleanup() {
    local exit_code=$?
    # Cleanup operations
    rm -f /tmp/hook_temp_*

    if [ $exit_code -ne 0 ]; then
        log "Hook failed with exit code: $exit_code"
    fi

    exit $exit_code
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Validate environment
validate_environment() {
    # Check required commands
    for cmd in git jq curl; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command not found: $cmd"
        fi
    done

    # Check required environment variables
    if [ -z "${CLAUDE_HOME:-}" ]; then
        error "CLAUDE_HOME not set"
    fi
}

# Main hook logic
main() {
    log "Starting hook: $SCRIPT_NAME"

    # Validate environment
    validate_environment

    # Hook implementation
    # TODO: Add your hook logic here

    log "Hook completed successfully"
}

# Run with timeout
if command -v timeout &> /dev/null; then
    timeout "$TIMEOUT" bash -c "$(declare -f main); main $*"
else
    main "$@"
fi
```

## Summary

Hook issues typically involve:

1. **Execution Failures** - Script errors, permissions, dependencies
2. **Timeout Problems** - Slow execution, hanging scripts
3. **Configuration Errors** - Invalid syntax, missing definitions
4. **Trigger Issues** - Conditions not met, disabled hooks
5. **Performance Problems** - Resource usage, bottlenecks

Key troubleshooting steps:
1. Enable debug mode for detailed logs
2. Validate hook scripts and configuration
3. Check permissions and dependencies
4. Profile performance bottlenecks
5. Implement proper error handling

Always test hooks thoroughly and maintain backups before making changes.
