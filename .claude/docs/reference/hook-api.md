# Claude Code Hook API Specification

## Overview

The Hook API provides a flexible, multi-language mechanism for extending and customizing Claude Code's behavior through carefully designed extension points.

## Hook Types and Locations

### Hook Storage Locations

| Language | Directory | File Extension |
|----------|-----------|----------------|
| JavaScript | `.claude/hooks/js/` | `.js` |
| Python | `.claude/hooks/python/` | `.py` |
| Shell | `.claude/hooks/shell/` | `.sh` |

## JavaScript Hooks

### Interface Definition

```javascript
module.exports = {
  name: 'descriptive-hook-name',
  description: 'Purpose of the hook',
  category: 'system|development|integration',
  version: '1.0.0',

  // Primary execution method
  execute: async (context) => {
    // Hook implementation
    return {
      success: true,
      data: {},
      logs: []
    };
  },

  // Optional lifecycle methods
  beforeExecute: (context) => {},
  afterExecute: (context) => {},

  // Configuration and constraints
  permissions: {
    requiredTools: ['Bash', 'Grep'],
    restrictedActions: []
  }
}
```

### Context Object Structure

```javascript
{
  input: {}, // Original input data
  tools: [], // Available tools
  environment: {
    platform: 'win32',
    version: '3.5.0',
    timestamp: '2025-10-09T12:00:00Z'
  },
  state: {}, // Mutable state container
  metadata: {} // Additional context information
}
```

## Python Hooks

### Interface Definition

```python
def execute(context):
    """
    Primary hook execution method

    Args:
        context (dict): Execution context

    Returns:
        dict: Execution results
    """
    return {
        'success': True,
        'data': {},
        'logs': []
    }

# Optional lifecycle methods
def before_execute(context):
    pass

def after_execute(context):
    pass

# Metadata
__hook_name__ = 'descriptive-hook-name'
__description__ = 'Purpose of the hook'
__category__ = 'system|development|integration'
__version__ = '1.0.0'
```

## Shell Hooks

### Interface Definition

```bash
#!/bin/bash

# Hook Metadata
# HOOK_NAME=descriptive-hook-name
# HOOK_DESCRIPTION=Purpose of the hook
# HOOK_CATEGORY=system|development|integration
# HOOK_VERSION=1.0.0

function execute() {
    local context="$1"

    # Hook implementation
    return 0
}

function before_execute() {
    local context="$1"
    # Pre-execution logic
}

function after_execute() {
    local context="$1"
    # Post-execution logic
}
```

## Hook Execution Lifecycle

1. **Initialization**
   - Load hook configuration
   - Validate permissions
   - Prepare execution context

2. **Pre-Execution**
   - Run `beforeExecute` method
   - Perform initial setup
   - Validate input

3. **Main Execution**
   - Call primary `execute` method
   - Process input
   - Interact with tools
   - Generate output

4. **Post-Execution**
   - Run `afterExecute` method
   - Log results
   - Clean up resources

5. **Finalization**
   - Return execution results
   - Handle errors
   - Update system state

## Permissions and Security

### Permission Levels

| Level | Description | Restrictions |
|-------|-------------|--------------|
| `system` | Full system access | Highest privilege |
| `restricted` | Limited tool access | Controlled execution |
| `read-only` | View-only operations | No modifications |

### Security Constraints

- Mandatory input validation
- Principle of least privilege
- Sandboxed execution environment
- Comprehensive logging
- Error isolation

## Hook Configuration

```yaml
hooks:
  - name: infrastructure-analyzer
    language: javascript
    permissions: read-only
    tools:
      - azure-resource-graph
    constraints:
      max-execution-time: 60s
      memory-limit: 512MB
```

## Error Handling

### Error Types

| Code | Category | Description |
|------|----------|-------------|
| `100` | Configuration | Hook setup failure |
| `200` | Execution | Runtime error |
| `300` | Permission | Access denied |
| `400` | Resource | External dependency issue |

## Performance Characteristics

### Execution Overhead

| Hook Type | Initialization | Execution | Memory Usage |
|-----------|----------------|-----------|--------------|
| JavaScript | Low | Fast | Medium |
| Python | Medium | Moderate | High |
| Shell | Minimal | Fastest | Low |

## Monitoring and Observability

- Detailed execution logs
- Performance metrics
- Error tracking
- Resource utilization

## Best Practices

1. Keep hooks focused and modular
2. Minimize external dependencies
3. Handle errors gracefully
4. Use strong typing
5. Implement comprehensive logging
6. Follow language-specific idioms

## Versioning and Compatibility

- Semantic versioning
- Backward compatibility guarantees
- Deprecation notices
- Feature flags

## Community and Contributions

- Hook submission guidelines
- Peer review process
- Performance benchmark requirements

## Version History

- 1.0.0: Initial comprehensive specification
- 0.9.0: Pre-release draft
