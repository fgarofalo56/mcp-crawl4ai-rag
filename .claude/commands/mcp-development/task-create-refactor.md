# Create Code Refactoring Task

Create a task for refactoring large functions or improving code quality.

## Usage
```
/task-create-refactor <function_name> [--target-lines=100] [--priority=P1]
```

## Description
Creates a structured task for refactoring a specific function, including analysis of current state, proposed changes, and validation strategy.

## Implementation

1. **Analyze function** using code analysis tools
2. **Identify extraction opportunities** for helper functions
3. **Plan refactoring steps** with backward compatibility
4. **Define success metrics** (line count, complexity)
5. **Create test plan** to ensure no breaking changes

## Task File Structure

```markdown
# Task: Refactor {function_name}

**Status**: todo
**Priority**: {priority}
**Estimated Effort**: M
**Task Type**: refactor
**Sprint**: Current
**Created**: {date}
**Labels**: refactoring, code-quality

## Description

Refactor the `{function_name}` function to improve maintainability and reduce complexity.

**Current State**:
- Lines: {current_lines}
- Complexity: {complexity_score}
- Location: `{file_path}:{line_number}`

**Target State**:
- Lines: < {target_lines}
- Complexity: Reduced by extracting helper functions
- Maintainability: Improved

## Acceptance Criteria

- [ ] Function reduced to < {target_lines} lines
- [ ] No breaking changes to API
- [ ] All existing tests still pass
- [ ] New tests added for extracted functions
- [ ] Type hints on all extracted functions
- [ ] Docstrings for all extracted functions
- [ ] No increase in overall module size

## Current Function Analysis

### Function Signature
```python
{function_signature}
```

### Current Responsibilities
1. Responsibility 1
2. Responsibility 2
3. Responsibility 3 (should be extracted)
4. Responsibility 4 (should be extracted)

### Code Smells Identified
- [ ] Too many responsibilities
- [ ] Deep nesting
- [ ] Repeated code patterns
- [ ] Long parameter list
- [ ] Complex conditionals

## Refactoring Plan

### Step 1: Extract {helper_function_1}
**Lines to extract**: {start}-{end}
**New function signature**:
```python
def {helper_function_name}(param1: Type1, param2: Type2) -> ReturnType:
    """Description of what this helper does.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description of return value
    """
    # Extracted logic here
```

**Rationale**: This logic is self-contained and reusable

### Step 2: Extract {helper_function_2}
**Lines to extract**: {start}-{end}
**New function signature**:
```python
def {helper_function_name}(param1: Type1) -> ReturnType:
    """Description."""
    # Extracted logic here
```

**Rationale**: Separates concern X from main function

### Step 3: Simplify Main Function
**After extraction, main function should**:
1. Validate inputs
2. Call helper_function_1
3. Call helper_function_2
4. Return formatted result

**Expected line count**: ~{expected_lines} lines

## Testing Strategy

### Regression Testing
- [ ] Run existing test suite
- [ ] Verify all tests pass
- [ ] Check test coverage maintained

### New Tests for Extracted Functions
```python
# tests/test_{module_name}.py

class Test{HelperFunction1}:
    async def test_normal_case(self):
        result = {helper_function_1}(param1, param2)
        assert result == expected

    async def test_edge_case(self):
        result = {helper_function_1}(edge_case_input)
        assert result == expected

    async def test_error_case(self):
        with pytest.raises(ExpectedError):
            {helper_function_1}(invalid_input)
```

### Integration Testing
- [ ] Test refactored function with real MCP client
- [ ] Verify behavior unchanged
- [ ] Check performance not degraded

## Backward Compatibility

### API Contract
- [ ] Function signature unchanged
- [ ] Return type unchanged
- [ ] Behavior identical for all inputs
- [ ] Error handling unchanged

### Migration Notes
No migration needed - internal refactoring only.

## Performance Considerations

### Expected Impact
- Performance: No change or slight improvement
- Memory: No significant change
- Maintainability: Significant improvement

### Measurements
- [ ] Benchmark before refactoring
- [ ] Benchmark after refactoring
- [ ] Compare results

## Documentation Updates

- [ ] Update inline comments
- [ ] Update function docstrings
- [ ] Add docstrings to extracted functions
- [ ] Update module documentation if needed

## Definition of Done

- [ ] Function < {target_lines} lines
- [ ] All tests passing
- [ ] New tests for extracted functions
- [ ] Code reviewed and approved
- [ ] No linting/type errors
- [ ] Performance benchmarked
- [ ] Documentation updated

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Comprehensive regression testing |
| Performance degradation | Benchmark before/after |
| Increased complexity | Careful extraction with clear responsibilities |
```

## Example Usage

```bash
/task-create-refactor parse_github_repositories_batch --target-lines=150 --priority=P0
```

Creates a task for refactoring the `parse_github_repositories_batch` function (currently 274 lines) to under 150 lines.

## Output

Task file created with detailed refactoring plan based on current function analysis.
