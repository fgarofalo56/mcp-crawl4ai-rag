# Claude Code Command API Specification

## Overview

The Command API defines a powerful, flexible mechanism for creating structured, reproducible commands within the Claude Code ecosystem.

## File Structure

### Location
Commands are stored in `.claude/commands/` directory with `.md` extension.

### Filename Convention
`{command-name}.md`
- Lowercase
- Hyphen-separated
- Descriptive and concise

## Frontmatter Specification

### Required Fields

```yaml
description: "Concise, action-oriented description of the command's purpose"
```

### Optional Fields

```yaml
allowed-tools:
  - tool1
  - tool2

requires-mcp: true/false

argument-hint: "[optional argument description]"

category:
  - utility
  - development
  - integration

author: "Your Name"
version: "1.0.0"
experimental: false
```

## Command Body Structure

### Markdown Syntax

1. **Header**: Brief command overview
2. **Description**: Detailed explanation
3. **Parameters**: Input specifications
4. **Examples**: Usage demonstrations
5. **Return Values**: Expected outputs

### Special Variables

- `$ARGUMENTS`: Dynamic argument parsing
- `$CONTEXT`: Current execution context
- `$MCP_SERVERS`: Available MCP servers

## Parameter Syntax

### Basic Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text input | `"hello world"` |
| `number` | Numeric value | `42` |
| `boolean` | True/False | `true` |
| `array` | List of items | `["item1", "item2"]` |
| `object` | Key-value pairs | `{"key": "value"}` |

### Parameter Constraints

```yaml
parameters:
  name:
    type: string
    required: true
    min-length: 2
    max-length: 50
    pattern: "^[a-zA-Z0-9_-]+$"
```

## Invocation Mechanisms

### Direct Execution

```bash
/command-name [arguments]
```

### Programmatic Invocation

```javascript
await invokeCommand('command-name', {
  arguments: { ... },
  context: { ... }
})
```

## Error Handling

### Error Types

| Code | Description | Handling |
|------|-------------|----------|
| `100` | Invalid Arguments | Reject execution |
| `200` | Permissions Error | Access denied |
| `300` | MCP Server Unavailable | Fallback/Retry |

## Advanced Features

### Conditional Execution

```yaml
conditions:
  - mcp-server-available
  - user-has-permission
```

### Hooks and Middleware

- Pre-execution validation
- Post-execution logging
- Context transformation

## Security Considerations

- Argument sanitization
- Permission verification
- Least-privilege principle

## Example Command Definition

```markdown
# Copy Template Command

## Description
Copies a predefined project template to a target directory.

## Parameters
- `template`: Name of the template to copy
- `target`: Destination directory path

## Example

```bash
/copy-template prp-base-python /path/to/new/project
```

## Return Values
- `success`: Boolean indicating operation result
- `path`: Full path of created project
- `errors`: Any encountered issues
```

## Versioning and Compatibility

- Semantic versioning
- Backward compatibility guarantees
- Deprecation notices

## Best Practices

1. Keep commands focused
2. Use clear, descriptive names
3. Validate all inputs
4. Provide comprehensive documentation
5. Handle errors gracefully

## Testing and Validation

- Unit tests for each command
- Integration tests
- Edge case coverage

## Experimental Commands

- Clearly marked
- Subject to change
- Opt-in usage

## Community and Contributions

- Pull request guidelines
- Command submission process
- Review criteria

## Legal and Licensing

Standard Anthropic open-source licensing applies.

## Version History

- 1.0.0: Initial comprehensive specification
- 0.9.0: Pre-release draft
