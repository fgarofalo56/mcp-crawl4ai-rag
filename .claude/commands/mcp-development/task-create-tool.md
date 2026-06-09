# Create MCP Tool Task

Create a new task for developing an MCP tool with all necessary research and setup.

## Usage
```
/task-create-tool <tool_name> [--priority=P0|P1|P2|P3] [--effort=XS|S|M|L|XL]
```

## Description
Creates a comprehensive task file for developing a new MCP tool, including research, implementation plan, testing strategy, and documentation requirements.

## Implementation

1. **Create task file** in `project_tracking/sprints/current/`
2. **Research tool requirements** using available MCP servers
3. **Analyze similar tools** for patterns
4. **Plan implementation** with file changes
5. **Define testing strategy**
6. **Identify documentation needs**

## Task File Structure

```markdown
# Task: Implement {tool_name} MCP Tool

**Status**: todo
**Priority**: {priority}
**Estimated Effort**: {effort}
**Task Type**: feature
**Sprint**: Current
**Created**: {date}
**Labels**: mcp-tool, new-feature

## Description

Implement a new MCP tool called `{tool_name}` that provides {functionality}.

## Acceptance Criteria

- [ ] Tool exposed via @mcp.tool() decorator
- [ ] Input validation implemented
- [ ] Error handling with standardized responses
- [ ] Tool appears in Claude Desktop/clients
- [ ] Documentation added to API_REFERENCE.md
- [ ] Tests written and passing

## Research & Context

### Similar Tools
[Analysis of similar existing tools in the codebase]

### Dependencies
- Supabase/Neo4j/OpenAI requirements
- External service dependencies

### Technical Approach
[Recommended implementation approach]

## Implementation Plan

### Step 1: Tool Definition
**Files to modify**:
- `src/crawl4ai_mcp.py` - Add @mcp.tool() function

**Implementation**:
```python
@mcp.tool()
async def {tool_name}(
    ctx: Context,
    param1: str,
    param2: int = 10
) -> str:
    """Tool description.

    Args:
        ctx: MCP context
        param1: Description
        param2: Description (default: 10)

    Returns:
        JSON response with results
    """
    try:
        # Validate inputs
        validated = validate_mcp_tool_input(
            param1=param1,
            param2=param2
        )

        # Implementation logic here
        result = await process(validated)

        return create_success_response(result)

    except ValidationError as e:
        return create_error_response(str(e), error_type="validation_error")
    except Exception as e:
        logger.error(f"Tool error: {e}", exc_info=True)
        return create_error_response(str(e), error_type="tool_error")
```

### Step 2: Input Validation
**Files to modify**:
- `src/validators.py` - Add validation logic if needed

### Step 3: Core Logic
**Files to modify**:
- `src/utils.py` or create new utility file
- Integration with Supabase/Neo4j/OpenAI as needed

### Step 4: Testing
**Files to create**:
- `tests/test_{tool_name}.py` - Unit tests

## Testing Requirements

### Unit Tests
- [ ] Test successful execution
- [ ] Test input validation (invalid inputs)
- [ ] Test error handling
- [ ] Test edge cases

### Integration Tests
- [ ] Test tool via MCP client
- [ ] Test with real services (Supabase/Neo4j)
- [ ] Test error scenarios

### Manual Testing Checklist
- [ ] Tool visible in Claude Desktop
- [ ] Parameters work correctly
- [ ] Error messages helpful
- [ ] Response format correct

## Documentation Updates

- [ ] Add tool to `docs/API_REFERENCE.md`
- [ ] Add example usage to README.md
- [ ] Update tool count in README
- [ ] Add docstring with examples
- [ ] Update CHANGELOG.md

## Definition of Done

- [ ] Tool implemented and working
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] No linting errors
- [ ] Tool tested in Claude Desktop
```

## Example Usage

```bash
/task-create-tool parse_code_repository --priority=P1 --effort=L
```

Creates task for a new `parse_code_repository` tool with high priority and large effort estimate.

## Output

Task file created at: `project_tracking/sprints/current/task-{number}-{tool_name}.md`

Updates sprint file with new task reference.
