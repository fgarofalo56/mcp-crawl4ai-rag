# Common Issues and Solutions

## Overview

This guide covers the most frequently encountered issues with the Claude Code Context Engineering system and provides detailed solutions for each.

## Command Not Found

### Problem
Commands are not recognized or return "command not found" errors.

### Symptoms
- `/command-name` returns "Command not found"
- Custom commands don't work
- Built-in commands missing

### Causes
1. Command not properly registered
2. Incorrect file permissions
3. Syntax errors in command files
4. Missing dependencies
5. Configuration issues

### Solutions

#### Solution 1: Verify Command Installation

```bash
# List all available commands
/list-commands

# Check if specific command exists
/check-command task-next

# Verify command directory
ls -la .claude/commands/
```

#### Solution 2: Fix Command Registration

```bash
# Re-register commands
/reload-commands

# Register specific command
/register-command task-next

# Rebuild command index
/rebuild-command-index
```

#### Solution 3: Check Command File

```markdown
<!-- .claude/commands/task-next.md -->
# Command must start with proper header
/task-next

## Description
Task management command

## Usage
/task-next "task description"

## Implementation
<!-- Command logic here -->
```

#### Solution 4: Fix Permissions

```bash
# Fix command directory permissions
chmod 755 .claude/commands/

# Fix individual command files
chmod 644 .claude/commands/*.md

# Fix execution permissions for scripts
chmod +x .claude/commands/scripts/*.sh
```

#### Solution 5: Debug Command Loading

```python
# debug_commands.py
import os
import json

def check_commands():
    """Verify command configuration"""
    commands_dir = '.claude/commands'

    if not os.path.exists(commands_dir):
        print("❌ Commands directory missing")
        return False

    for file in os.listdir(commands_dir):
        if file.endswith('.md'):
            filepath = os.path.join(commands_dir, file)
            with open(filepath, 'r') as f:
                content = f.read()
                # Check for command marker
                if not content.startswith('/'):
                    print(f"⚠️ {file}: Missing command marker")
                else:
                    print(f"✅ {file}: Valid command file")

    return True

check_commands()
```

### Prevention
- Use command templates
- Validate commands after creation
- Regular command audits
- Version control for commands

## Permission Denied

### Problem
Operations fail due to insufficient permissions.

### Symptoms
- "Permission denied" errors
- Cannot create/modify files
- Cannot execute commands
- Access restrictions

### Solutions

#### Solution 1: File Permissions

```bash
# Check current permissions
ls -la

# Fix file permissions
find .claude -type f -exec chmod 644 {} \;

# Fix directory permissions
find .claude -type d -exec chmod 755 {} \;

# Fix script permissions
find .claude -name "*.sh" -exec chmod +x {} \;
```

#### Solution 2: User Permissions

```bash
# Check current user
whoami

# Check file ownership
ls -la .claude/

# Change ownership if needed
sudo chown -R $(whoami):$(whoami) .claude/

# Add user to necessary groups
sudo usermod -aG docker $(whoami)  # For Docker operations
```

#### Solution 3: Windows-Specific

```powershell
# Run as Administrator
# Right-click PowerShell -> Run as Administrator

# Check permissions
icacls .claude

# Grant full control
icacls .claude /grant "%USERNAME%":F /T

# Take ownership
takeown /f .claude /r
```

#### Solution 4: macOS-Specific

```bash
# Reset permissions
sudo chmod -R 755 .claude/

# Clear extended attributes
xattr -rc .claude/

# Fix quarantine flag
xattr -d com.apple.quarantine .claude/commands/*
```

### Prevention
- Set proper umask
- Use consistent ownership
- Document permission requirements
- Regular permission audits

## Configuration Problems

### Problem
System configuration is incorrect or corrupted.

### Symptoms
- Settings not applied
- Features not working
- Unexpected behavior
- Configuration errors

### Solutions

#### Solution 1: Validate Configuration

```json
// .claude/settings.json
{
  "version": "1.0.0",
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["mcp-server-filesystem/index.js"],
      "enabled": true
    }
  },
  "commands": {
    "directory": ".claude/commands",
    "enabled": true
  },
  "hooks": {
    "directory": ".claude/hooks",
    "enabled": true
  },
  "context": {
    "maxSize": 100000,
    "compactionThreshold": 0.8
  }
}
```

#### Solution 2: Reset Configuration

```bash
# Backup current config
cp .claude/settings.json .claude/settings.backup.json

# Reset to defaults
/reset-config

# Or manually create minimal config
cat > .claude/settings.json << 'EOF'
{
  "version": "1.0.0",
  "mcpServers": {},
  "commands": {
    "directory": ".claude/commands",
    "enabled": true
  }
}
EOF
```

#### Solution 3: Fix JSON Syntax

```python
# validate_config.py
import json

def validate_config():
    """Validate and fix configuration"""
    try:
        with open('.claude/settings.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration is valid JSON")

        # Check required fields
        required = ['version', 'commands']
        for field in required:
            if field not in config:
                print(f"⚠️ Missing required field: {field}")
                config[field] = get_default(field)

        # Save fixed config
        with open('.claude/settings.json', 'w') as f:
            json.dump(config, f, indent=2)

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        print("Creating new configuration...")
        create_default_config()

def get_default(field):
    defaults = {
        'version': '1.0.0',
        'commands': {'directory': '.claude/commands', 'enabled': True}
    }
    return defaults.get(field, {})

validate_config()
```

### Prevention
- Regular config backups
- Use config validation
- Version control configs
- Document all changes

## Environment Setup

### Problem
Environment variables or dependencies not properly configured.

### Symptoms
- Missing environment variables
- Import errors
- Dependency conflicts
- Path issues

### Solutions

#### Solution 1: Environment Variables

```bash
# Check current environment
env | grep CLAUDE

# Set required variables
export CLAUDE_HOME="$HOME/.claude"
export CLAUDE_CONFIG="$CLAUDE_HOME/settings.json"
export PATH="$CLAUDE_HOME/bin:$PATH"

# Make permanent (bash)
echo 'export CLAUDE_HOME="$HOME/.claude"' >> ~/.bashrc
echo 'export PATH="$CLAUDE_HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Make permanent (zsh)
echo 'export CLAUDE_HOME="$HOME/.claude"' >> ~/.zshrc
source ~/.zshrc
```

#### Solution 2: Python Dependencies

```bash
# Check Python version
python --version  # Should be 3.8+

# Create virtual environment
python -m venv .claude/venv

# Activate virtual environment
source .claude/venv/bin/activate  # Linux/Mac
# or
.claude\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installations
pip list
```

#### Solution 3: Node.js Dependencies

```bash
# Check Node version
node --version  # Should be 16+

# Install dependencies
cd .claude
npm install

# Fix dependency issues
npm audit fix

# Clear cache if needed
npm cache clean --force
```

#### Solution 4: System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    nodejs \
    npm \
    git \
    curl \
    build-essential

# macOS
brew update
brew install \
    python3 \
    node \
    git

# Windows (using Chocolatey)
choco install -y \
    python3 \
    nodejs \
    git
```

### Prevention
- Use dependency managers
- Document requirements
- Version lock dependencies
- Regular dependency updates

## Command Execution

### Problem
Commands execute but fail or produce unexpected results.

### Symptoms
- Commands timeout
- Partial execution
- Wrong output
- Silent failures

### Solutions

#### Solution 1: Debug Command Execution

```bash
# Enable debug mode
/debug on

# Trace command execution
/trace task-next

# Check command logs
/logs --command task-next --last 10
```

#### Solution 2: Fix Timeout Issues

```yaml
# .claude/commands/config.yaml
commands:
  task-next:
    timeout: 300  # 5 minutes
    retries: 3
    retry_delay: 5

  research-topic:
    timeout: 600  # 10 minutes
    async: true
```

#### Solution 3: Handle Errors Properly

```python
# command_wrapper.py
import asyncio
import traceback

async def execute_command(command, args):
    """Execute command with proper error handling"""
    try:
        # Set timeout
        result = await asyncio.wait_for(
            run_command(command, args),
            timeout=300
        )
        return result

    except asyncio.TimeoutError:
        print(f"Command '{command}' timed out")
        return None

    except Exception as e:
        print(f"Command '{command}' failed: {e}")
        traceback.print_exc()
        return None

async def run_command(command, args):
    """Actual command execution"""
    # Command implementation
    pass
```

### Prevention
- Add timeout configurations
- Implement retry logic
- Comprehensive error handling
- Command validation

## Custom Commands

### Problem
Custom commands not working as expected.

### Symptoms
- Custom commands not recognized
- Incorrect behavior
- Parameter issues
- Output problems

### Solutions

#### Solution 1: Command Structure

```markdown
<!-- .claude/commands/my-command.md -->
# Command name (must match filename)
/my-command

## Description
Brief description of what the command does

## Usage
```
/my-command <required-param> [optional-param]
```

## Parameters
- `required-param`: Description
- `optional-param`: Description (optional)

## Examples
```
/my-command "value1"
/my-command "value1" "value2"
```

## Implementation
<!-- Actual command logic -->
```

#### Solution 2: Parameter Parsing

```python
# parse_params.py
import re
import shlex

def parse_command(input_string):
    """Parse command and parameters"""
    # Extract command name
    match = re.match(r'^/(\S+)\s*(.*)', input_string)
    if not match:
        return None, []

    command = match.group(1)
    params_str = match.group(2)

    # Parse parameters (handles quotes)
    try:
        params = shlex.split(params_str)
    except ValueError as e:
        print(f"Parameter parsing error: {e}")
        params = params_str.split()

    return command, params

# Test
command, params = parse_command('/my-command "param 1" param2')
print(f"Command: {command}")
print(f"Parameters: {params}")
```

#### Solution 3: Command Validation

```python
# validate_command.py
class CommandValidator:
    """Validate custom commands"""

    def validate(self, command_file):
        """Validate command file"""
        errors = []

        with open(command_file, 'r') as f:
            content = f.read()

        # Check for command marker
        if not re.search(r'^/\w+', content, re.MULTILINE):
            errors.append("Missing command marker (/command-name)")

        # Check for required sections
        required_sections = ['## Description', '## Usage']
        for section in required_sections:
            if section not in content:
                errors.append(f"Missing section: {section}")

        # Check for implementation
        if '## Implementation' not in content:
            errors.append("Missing implementation section")

        return len(errors) == 0, errors

# Usage
validator = CommandValidator()
valid, errors = validator.validate('.claude/commands/my-command.md')
if not valid:
    print("Command validation failed:")
    for error in errors:
        print(f"  - {error}")
```

### Prevention
- Use command templates
- Validate before deployment
- Test thoroughly
- Document parameters clearly

## Installation Issues

### Problem
System installation or component setup fails.

### Symptoms
- Installation errors
- Missing components
- Incomplete setup
- Version conflicts

### Solutions

#### Solution 1: Clean Installation

```bash
# Remove existing installation
rm -rf .claude/
rm -rf node_modules/
rm -rf .venv/

# Fresh installation
git clone https://github.com/claude-code/context-engineering.git
cd context-engineering
./install.sh

# Or manual installation
mkdir -p .claude/{commands,hooks,context}
npm install
pip install -r requirements.txt
```

#### Solution 2: Version Compatibility

```bash
# Check versions
python --version  # >= 3.8
node --version    # >= 16.0
npm --version     # >= 8.0

# Update if needed
# Python
python -m pip install --upgrade pip

# Node.js (using nvm)
nvm install 18
nvm use 18

# npm
npm install -g npm@latest
```

#### Solution 3: Dependency Resolution

```bash
# Python dependencies
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

# If conflicts occur
pip install -r requirements.txt --force-reinstall

# Node dependencies
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Prevention
- Document version requirements
- Use virtual environments
- Lock dependency versions
- Regular compatibility testing

## Recovery Procedures

### Emergency Recovery

```bash
# Create recovery point
/create-recovery-point

# List recovery points
/list-recovery-points

# Restore from recovery point
/restore-recovery-point --id recovery-2024-01-15

# Export current state
/export-state --file state-backup.json

# Import state
/import-state state-backup.json
```

### Data Recovery

```bash
# Recover deleted commands
/recover-commands --from-backup

# Restore configuration
/restore-config --date yesterday

# Rebuild indices
/rebuild-all-indices

# Verify integrity
/verify-integrity --repair
```

### System Reset

```bash
# Soft reset (preserves data)
/reset --soft

# Hard reset (clean slate)
/reset --hard --confirm

# Factory reset
/factory-reset --preserve-config
```

## Prevention Strategies

### Best Practices

1. **Regular Backups**
   ```bash
   # Automated backups
   /enable-auto-backup --interval daily
   ```

2. **Version Control**
   ```bash
   git init .claude
   git add .
   git commit -m "Configuration backup"
   ```

3. **Health Monitoring**
   ```bash
   # Setup monitoring
   /setup-monitor --component all
   ```

4. **Testing**
   ```bash
   # Test configuration
   /test-config

   # Test commands
   /test-commands --all
   ```

## Summary

Common issues typically fall into these categories:
1. **Configuration** - JSON syntax, missing fields
2. **Permissions** - File/directory access rights
3. **Dependencies** - Missing or incompatible versions
4. **Environment** - Variables and paths
5. **Commands** - Structure and registration

Most issues can be resolved by:
- Checking logs and error messages
- Validating configuration
- Fixing permissions
- Updating dependencies
- Restarting the system

Always backup before making changes and document successful solutions for future reference.
