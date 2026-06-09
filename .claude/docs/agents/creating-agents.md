# 🛠️ Creating Custom Agents

> **Step-by-step guide for building your own specialized Claude Code agents**

This comprehensive guide teaches you how to create custom agents tailored to your specific needs, from simple single-purpose agents to complex multi-tool specialists.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Agent File Structure](#-agent-file-structure)
- [YAML Frontmatter Specification](#-yaml-frontmatter-specification)
- [System Prompt Writing](#-system-prompt-writing)
- [Tool Permission Configuration](#-tool-permission-configuration)
- [Testing Your Agent](#-testing-your-agent)
- [Debugging Techniques](#-debugging-techniques)
- [Agent Templates](#-agent-templates)
- [Common Patterns](#-common-patterns)
- [Anti-Patterns to Avoid](#-anti-patterns-to-avoid)
- [Publishing and Sharing](#-publishing-and-sharing)
- [Related Documentation](#-related-documentation)

---

## 🎯 Overview

Creating a custom agent involves:

1. **Define Purpose** - What specialized task will it perform?
2. **Create Agent File** - Markdown file with YAML frontmatter
3. **Write System Prompt** - Instructions that define agent behavior
4. **Configure Tools** - Grant only necessary tool permissions
5. **Test Thoroughly** - Validate agent behavior
6. **Iterate and Refine** - Improve based on results

### When to Create a Custom Agent

✅ **Create an agent when**:
- Task requires specialized expertise
- Repeated workflow needs automation
- Tool isolation improves security
- Specific output format needed
- Domain-specific knowledge required

❌ **Don't create an agent when**:
- One-off task (use main session)
- General-purpose task (use existing agent)
- Simple command would suffice
- No specialized expertise needed

---

## 📄 Agent File Structure

### Basic Structure

```markdown
---
name: my-agent
description: Brief description of what the agent does
tools: Read, Write, Edit
model: sonnet
---

You are a [role] specializing in [expertise area].

## Focus Areas

- Area 1
- Area 2
- Area 3

## Approach

1. Step 1
2. Step 2
3. Step 3

## Output

- Output format 1
- Output format 2
- Output format 3

[Additional sections as needed]
```

### File Location

**Project-Specific**:
```bash
.claude/agents/my-agent.md
```

**Global** (available in all projects):
```bash
~/.claude/agents/my-agent.md
```

### Naming Conventions

**File Name**: `agent-name.md`
- Lowercase
- Hyphens for spaces
- Descriptive and clear
- Matches `name` in frontmatter

**Examples**:
- ✅ `python-expert.md`
- ✅ `database-optimizer.md`
- ✅ `security-scanner.md`
- ❌ `agent1.md` (not descriptive)
- ❌ `Python_Expert.md` (wrong format)
- ❌ `myagent.md` (hard to read)

---

## ⚙️ YAML Frontmatter Specification

### Required Fields

#### `name`
**Type**: `string`
**Required**: Yes
**Description**: Agent identifier, must match filename

```yaml
name: python-expert
```

**Rules**:
- Lowercase
- Hyphens only
- No spaces or special characters
- Must match filename (without .md)

#### `description`
**Type**: `string`
**Required**: Yes
**Description**: Brief summary of agent purpose

```yaml
description: "Python development expert specializing in clean code and best practices"
```

**Best Practices**:
- Keep under 150 characters
- Be specific about expertise
- Mention key capabilities
- Use action verbs

#### `tools`
**Type**: `string` (comma-separated) or `array`
**Required**: Yes (can be empty for read-only)
**Description**: List of permitted tools

```yaml
# String format
tools: Read, Write, Edit, Bash

# Array format (alternative)
tools:
  - Read
  - Write
  - Edit
  - Bash
```

**Available Tools**:
- `Read` - Read files
- `Write` - Write files
- `Edit` - Edit files in-place
- `MultiEdit` - Edit multiple files
- `Bash` - Execute bash commands
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `ls` - List directories
- `TodoWrite` - Update todo lists
- `WebSearch` - Web search (if configured)
- `WebFetch` - Fetch web pages (if configured)

### Optional Fields

#### `model`
**Type**: `string`
**Default**: System default
**Options**: `haiku`, `sonnet`, `opus`
**Description**: Specific Claude model to use

```yaml
model: opus
```

**When to specify**:
- `haiku` - Fast, simple tasks (e.g., formatting)
- `sonnet` - Balanced (most agents) - DEFAULT
- `opus` - Complex reasoning (e.g., architecture)

#### `deny`
**Type**: `string` or `array`
**Description**: Explicitly denied tools

```yaml
deny: Bash, TodoWrite
```

#### `ask`
**Type**: `string` or `array`
**Description**: Tools requiring user approval

```yaml
ask: Bash, MultiEdit
```

### Complete Example

```yaml
---
name: security-auditor
description: "Security expert analyzing code for vulnerabilities, best practices, and compliance issues. Provides detailed security reports with remediation steps."
tools: Read, Grep, Glob
deny: Write, Edit, Bash
model: opus
---
```

---

## ✍️ System Prompt Writing

### Anatomy of a Great System Prompt

#### 1. Role Definition

**Bad**:
```markdown
You help with Python code.
```

**Good**:
```markdown
You are a Python development expert specializing in clean, performant, and idiomatic Python code following PEP 8 and modern Python best practices.
```

**Best**:
```markdown
You are a senior Python developer with 10+ years of experience specializing in:
- Clean, idiomatic Python following PEP 8 and PEP 20 (Zen of Python)
- Performance optimization and profiling
- Design patterns and SOLID principles
- Comprehensive testing with pytest
- Type hints and static analysis with mypy

Your goal is to write Python code that is not just functional, but maintainable, testable, and exemplary.
```

#### 2. Focus Areas

Define specific areas of expertise:

```markdown
## Focus Areas

### Code Quality
- PEP 8 compliance and pythonic idioms
- Type hints for all public interfaces
- Comprehensive docstrings (Google style)

### Performance
- Profiling with cProfile and line_profiler
- Memory optimization with tracemalloc
- Algorithm complexity analysis

### Testing
- Unit tests with pytest and fixtures
- Test coverage above 90%
- Mocking external dependencies
- Property-based testing with hypothesis

### Architecture
- SOLID principles
- Design patterns (when appropriate)
- Dependency injection
- Clear separation of concerns
```

#### 3. Approach/Methodology

Define how the agent should work:

```markdown
## Approach

1. **Analyze First**: Understand the code's purpose and context before refactoring
2. **Incremental Changes**: Make small, testable improvements
3. **Test-Driven**: Write or update tests before modifying code
4. **Measure Performance**: Profile before and after optimization
5. **Document Decisions**: Explain non-obvious choices in comments
```

#### 4. Output Specifications

Define expected output format:

```markdown
## Output Format

### Code
- Complete, runnable Python files
- Type hints for all functions
- Docstrings for all public APIs
- Inline comments for complex logic

### Tests
- Pytest test files with descriptive names
- Fixtures for common test data
- Both positive and negative test cases
- Coverage report showing >90%

### Documentation
- Updated README if public API changed
- CHANGELOG entry for significant changes
- Performance benchmarks if optimization made

### Analysis
- Code quality metrics (if issues found)
- Performance profiling results (if relevant)
- Suggestions for further improvement
```

#### 5. Constraints and Guidelines

Define boundaries and rules:

```markdown
## Constraints

- Python 3.9+ only (use modern features)
- No external dependencies without justification
- All code must pass `ruff check .` and `mypy .`
- Maintain or improve test coverage
- No breaking changes to public APIs without explicit approval
```

#### 6. Examples (Optional)

Show the agent what good looks like:

```markdown
## Examples

### Input: Legacy code
```python
def calc(x, y, op):
    if op == 'add':
        return x + y
    elif op == 'sub':
        return x - y
    # ... more operations
```

### Output: Modern, typed Python
```python
from enum import Enum
from typing import Protocol

class Operation(Enum):
    """Supported mathematical operations."""
    ADD = "add"
    SUBTRACT = "sub"

def calculate(x: float, y: float, operation: Operation) -> float:
    """Perform mathematical operation on two numbers.

    Args:
        x: First operand
        y: Second operand
        operation: Operation to perform

    Returns:
        Result of the operation

    Raises:
        ValueError: If operation is not supported

    Examples:
        >>> calculate(5, 3, Operation.ADD)
        8.0
        >>> calculate(10, 4, Operation.SUBTRACT)
        6.0
    """
    operations = {
        Operation.ADD: lambda: x + y,
        Operation.SUBTRACT: lambda: x - y,
    }

    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")

    return operations[operation]()
```
```

### System Prompt Best Practices

✅ **DO**:
- Be specific and detailed
- Use clear, concise language
- Provide examples of desired output
- Define success criteria
- Include quality standards
- Mention common pitfalls to avoid
- Use structured sections (##, ###)
- Define output format explicitly

❌ **DON'T**:
- Be vague or ambiguous
- Use contradictory instructions
- Make prompt too long (>10,000 chars)
- Include project-specific details
- Assume knowledge of internal systems
- Mix multiple unrelated responsibilities
- Skip the "why" behind approaches

### System Prompt Templates

#### Minimal Template
```markdown
You are a [ROLE] specializing in [EXPERTISE].

## Focus Areas
- [Area 1]
- [Area 2]

## Output
- [Output type 1]
- [Output type 2]
```

#### Standard Template
```markdown
You are a [ROLE] specializing in [EXPERTISE].

## Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]

## Focus Areas
- [Area 1]
- [Area 2]
- [Area 3]

## Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output Format
- [Format specification]
- [Quality criteria]

## Key Principles
- [Principle 1]
- [Principle 2]
```

#### Comprehensive Template
```markdown
You are a [ROLE] specializing in [EXPERTISE]. Your expertise includes [SPECIFIC SKILLS].

## Core Responsibilities

### [Category 1]
- [Specific task]
- [Specific task]

### [Category 2]
- [Specific task]
- [Specific task]

## Focus Areas

### [Focus Area 1]
[Detailed description]

### [Focus Area 2]
[Detailed description]

## Approach

1. **[Phase 1]**: [Description]
2. **[Phase 2]**: [Description]
3. **[Phase 3]**: [Description]

## Output Specifications

### [Output Type 1]
- [Specification]
- [Quality criteria]

### [Output Type 2]
- [Specification]
- [Quality criteria]

## Quality Standards
- [Standard 1]
- [Standard 2]

## Key Principles
- [Principle 1 with explanation]
- [Principle 2 with explanation]

## Examples

### Example 1: [Scenario]
**Input**: [Input example]
**Output**: [Expected output]

### Example 2: [Scenario]
**Input**: [Input example]
**Output**: [Expected output]
```

---

## 🔐 Tool Permission Configuration

### Tool Permission Levels

#### Level 1: Read-Only (Safest)
```yaml
tools: Read, Grep, Glob
```

**Use for**:
- Analysis agents
- Review agents
- Research agents
- Auditing agents

**Example**: Security auditor, code reviewer

#### Level 2: Read + Write (Common)
```yaml
tools: Read, Write, Edit
```

**Use for**:
- Documentation agents
- Code generation agents
- Refactoring agents

**Example**: Documentation manager, Python expert

#### Level 3: Read + Write + Bash (Powerful)
```yaml
tools: Read, Write, Edit, Bash
```

**Use for**:
- Testing agents
- Build agents
- Deployment agents

**Example**: Validation gates, data engineer

⚠️ **Warning**: Bash access is powerful and potentially dangerous. Use with caution.

### Tool Selection Guidelines

**Read** - Always safe:
```yaml
tools: Read
```
- No modification possible
- Perfect for analysis

**Write** - Controlled creation:
```yaml
tools: Read, Write
```
- Can create new files
- Cannot modify existing files without Read

**Edit** - In-place modification:
```yaml
tools: Read, Edit
```
- Can modify existing files
- More surgical than Write

**MultiEdit** - Batch modifications:
```yaml
tools: Read, MultiEdit
```
- Edit multiple files at once
- Efficient for refactoring

**Bash** - Execution capability:
```yaml
tools: Bash, Read
```
- Run commands
- Build projects
- Execute tests
- ⚠️ DANGEROUS if misused

**Grep** - Content search:
```yaml
tools: Read, Grep
```
- Fast content searching
- Pattern matching
- Perfect for analysis

**Glob** - File discovery:
```yaml
tools: Read, Glob
```
- Find files by pattern
- Navigate project structure

### Permission Patterns

#### Pattern 1: Analyzer
```yaml
name: code-analyzer
tools: Read, Grep, Glob
```
**Purpose**: Read and analyze, no modifications

#### Pattern 2: Generator
```yaml
name: code-generator
tools: Read, Write
```
**Purpose**: Create new files based on analysis

#### Pattern 3: Refactorer
```yaml
name: code-refactorer
tools: Read, Edit, MultiEdit
```
**Purpose**: Modify existing code

#### Pattern 4: Validator
```yaml
name: test-validator
tools: Read, Bash, Edit
```
**Purpose**: Run tests and fix issues

#### Pattern 5: Builder
```yaml
name: project-builder
tools: Read, Write, Bash
```
**Purpose**: Generate and build projects

### Security Considerations

#### Principle of Least Privilege

✅ **Good**:
```yaml
name: readme-updater
tools: Read, Edit
# Only can read files and edit README
```

❌ **Bad**:
```yaml
name: readme-updater
tools: Read, Write, Edit, Bash, MultiEdit
# Way more permissions than needed
```

#### Ask for Dangerous Operations

```yaml
name: deployment-agent
tools: Read, Write
ask: Bash
# Bash requires user approval
```

#### Explicit Denials

```yaml
name: documentation-agent
tools: Read, Write, Edit
deny: Bash, MultiEdit
# Explicitly prevent code execution
```

---

## 🧪 Testing Your Agent

### Testing Checklist

- [ ] Agent file parses correctly
- [ ] Frontmatter YAML is valid
- [ ] Agent name matches filename
- [ ] Description is clear and accurate
- [ ] Tool permissions are minimal
- [ ] System prompt is well-structured
- [ ] Agent produces expected output
- [ ] Edge cases handled gracefully
- [ ] Error messages are helpful
- [ ] Performance is acceptable

### Manual Testing

#### 1. Syntax Validation

```bash
# Check YAML syntax
head -20 .claude/agents/my-agent.md

# Verify agent is discoverable
ls .claude/agents/my-agent.md
```

#### 2. Simple Invocation

```
"Use my-agent to [simple task]"
```

Example:
```
"Use python-expert agent to explain this function:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"
```

#### 3. Tool Permission Test

```
"Use my-agent to read file.txt"  # Should work if Read permission
"Use my-agent to delete file.txt"  # Should fail if no Bash
```

#### 4. Output Format Test

Check if agent follows output specifications:
```
"Use my-agent to [task]"

# Verify output contains:
# - Expected sections
# - Proper formatting
# - Complete information
```

#### 5. Edge Case Testing

```
# Empty input
"Use my-agent to process: ''"

# Invalid input
"Use my-agent to process: [nonsense]"

# Large input
"Use my-agent to process: [very long text]"

# Boundary conditions
"Use my-agent to process: [edge case]"
```

### Automated Testing

Create a test file:

```python
# tests/test_agents.py
import subprocess
import json

def test_agent_syntax():
    """Verify agent file has valid YAML frontmatter."""
    with open('.claude/agents/my-agent.md') as f:
        content = f.read()

    assert content.startswith('---')
    assert '\n---\n' in content

def test_agent_invocation():
    """Test agent can be invoked."""
    result = invoke_agent('my-agent', 'Test task')
    assert result.success
    assert result.output

def test_agent_tools():
    """Verify agent respects tool permissions."""
    # Agent with only Read permission
    result = invoke_agent('read-only-agent', 'Write to file.txt')
    assert result.error
    assert 'permission denied' in result.error.lower()
```

### Performance Testing

```python
import time

def test_agent_performance():
    """Verify agent completes in reasonable time."""
    start = time.time()
    result = invoke_agent('my-agent', 'Standard task')
    duration = time.time() - start

    assert duration < 60  # Should complete in under 60 seconds
    assert result.tokens < 10000  # Should use reasonable tokens
```

---

## 🐛 Debugging Techniques

### Common Issues and Solutions

#### Issue 1: Agent Not Found

**Symptom**:
```
Error: Agent 'my-agent' not found
```

**Debug Steps**:
```bash
# 1. Check file exists
ls .claude/agents/my-agent.md

# 2. Check filename matches agent name
cat .claude/agents/my-agent.md | head -5
# Should show: name: my-agent

# 3. Check file location
pwd
# Should be in project root or ~/.claude/agents/
```

**Solution**:
- Ensure filename matches `name` field
- Check file is in correct directory
- Verify no typos in name

#### Issue 2: Invalid YAML Frontmatter

**Symptom**:
```
Error: Failed to parse agent definition
```

**Debug Steps**:
```bash
# Extract frontmatter
sed -n '/^---$/,/^---$/p' .claude/agents/my-agent.md

# Validate YAML online
# Copy frontmatter to yamllint.com
```

**Common YAML Errors**:
```yaml
# ❌ Wrong: Missing quotes around description with special chars
description: Agent that does "cool" things

# ✅ Right: Quotes around entire string
description: "Agent that does \"cool\" things"

# ❌ Wrong: Inconsistent indentation
tools:
 - Read
  - Write

# ✅ Right: Consistent indentation
tools:
  - Read
  - Write
```

#### Issue 3: Permission Denied

**Symptom**:
```
Error: Agent denied access to tool 'Bash'
```

**Debug Steps**:
```bash
# Check agent tools
grep "^tools:" .claude/agents/my-agent.md

# Check if Bash is listed
# If not, add it to tools array
```

**Solution**:
```yaml
# Add missing tool
tools: Read, Write, Bash
```

#### Issue 4: Agent Produces Wrong Output

**Symptom**:
- Output doesn't match expectations
- Missing sections
- Wrong format

**Debug Steps**:
1. **Review System Prompt**:
   ```bash
   cat .claude/agents/my-agent.md
   # Read prompt carefully for ambiguities
   ```

2. **Test with Simple Input**:
   ```
   "Use my-agent with this simple test: [minimal example]"
   ```

3. **Check for Contradictions**:
   - Does prompt say both "be brief" and "be comprehensive"?
   - Are output format requirements clear?

**Solution**:
- Clarify system prompt
- Add specific output format section
- Include example outputs

#### Issue 5: Agent Too Slow

**Symptom**:
- Agent takes >120 seconds
- Times out

**Debug Steps**:
1. **Check Tool Usage**:
   - Is agent reading too many files?
   - Too many Bash executions?

2. **Review Prompt Length**:
   ```bash
   wc -c .claude/agents/my-agent.md
   # Should be < 50,000 chars
   ```

3. **Check Model**:
   ```yaml
   # Is agent using opus when haiku would work?
   model: haiku  # Faster
   ```

**Solutions**:
- Simplify system prompt
- Use faster model
- Limit tool usage
- Break into smaller agents

### Debugging Tools

#### Enable Verbose Logging

```bash
# Set debug environment variable
export CLAUDE_DEBUG=1

# Run with verbose output
claude-code --debug
```

#### Agent Trace

```python
# Add to agent testing
def trace_agent_execution(agent_name, task):
    print(f"[TRACE] Invoking agent: {agent_name}")
    print(f"[TRACE] Task: {task}")

    result = invoke_agent(agent_name, task)

    print(f"[TRACE] Success: {result.success}")
    print(f"[TRACE] Duration: {result.duration}s")
    print(f"[TRACE] Tokens: {result.tokens}")
    print(f"[TRACE] Tools used: {result.tools_used}")

    return result
```

#### Agent Comparison

```python
# Compare two agent versions
def compare_agents(agent1, agent2, task):
    result1 = invoke_agent(agent1, task)
    result2 = invoke_agent(agent2, task)

    print(f"Agent 1: {result1.duration}s, {result1.tokens} tokens")
    print(f"Agent 2: {result2.duration}s, {result2.tokens} tokens")

    print("\nOutput comparison:")
    print(f"Length: {len(result1.output)} vs {len(result2.output)}")
    print(f"Quality: {rate_quality(result1)} vs {rate_quality(result2)}")
```

---

## 📦 Agent Templates

### Template 1: Code Quality Agent

```markdown
---
name: code-quality-checker
description: "Analyzes code quality, identifies issues, and suggests improvements based on best practices and coding standards."
tools: Read, Grep, Glob
model: sonnet
---

You are a code quality expert specializing in identifying code smells, anti-patterns, and opportunities for improvement.

## Core Responsibilities

1. **Static Analysis**: Analyze code structure and patterns
2. **Best Practices**: Check adherence to language-specific best practices
3. **Maintainability**: Assess code maintainability and readability
4. **Recommendations**: Provide actionable improvement suggestions

## Focus Areas

### Code Smells
- Long methods (>50 lines)
- God objects (>500 lines)
- Duplicated code
- Magic numbers
- Deep nesting (>3 levels)

### Design Patterns
- SOLID principles violations
- Missing abstractions
- Tight coupling
- Poor separation of concerns

### Documentation
- Missing docstrings
- Unclear variable names
- Inadequate comments for complex logic

## Analysis Process

1. **Scan Codebase**: Identify files to analyze
2. **Detect Issues**: Find code smells and anti-patterns
3. **Prioritize**: Rank issues by severity
4. **Recommend**: Provide specific, actionable fixes
5. **Estimate**: Give effort estimate for fixes

## Output Format

### Summary
- Total files analyzed
- Issues found (by severity)
- Overall code quality score (0-100)

### Detailed Issues

For each issue:
```markdown
#### Issue: [Issue Name]
**Severity**: High/Medium/Low
**File**: path/to/file.py:line_number
**Description**: What's wrong
**Impact**: Why it matters
**Recommendation**: How to fix
**Effort**: Estimated time to fix
```

### Quick Wins
List of easy improvements with high impact

## Quality Metrics

- Code quality score: Weighted average of:
  - Complexity (30%)
  - Maintainability (25%)
  - Documentation (20%)
  - Best practices adherence (25%)

## Key Principles

- Focus on maintainability over perfection
- Prioritize high-impact issues
- Provide constructive, actionable feedback
- Consider context and constraints
```

### Template 2: Documentation Generator

```markdown
---
name: doc-generator
description: "Generates comprehensive documentation from code, including API docs, README sections, and inline documentation."
tools: Read, Write, Grep, Glob
model: sonnet
---

You are a technical documentation specialist who generates clear, comprehensive documentation from source code.

## Core Responsibilities

1. **Code Analysis**: Understand code structure and purpose
2. **Documentation Generation**: Create appropriate documentation
3. **Format Consistency**: Ensure consistent documentation style
4. **Example Creation**: Provide usage examples

## Documentation Types

### API Documentation
- Function signatures with parameter descriptions
- Return values and types
- Usage examples
- Error conditions

### Module Documentation
- Module purpose and overview
- Exported functions/classes
- Dependencies
- Usage patterns

### README Sections
- Installation instructions
- Quick start guide
- Usage examples
- Configuration options

## Generation Process

1. **Discover**: Find all documentable elements
2. **Extract**: Get function signatures, types, etc.
3. **Infer**: Understand purpose from code
4. **Generate**: Create documentation
5. **Examples**: Add usage examples
6. **Validate**: Check completeness

## Output Format

### For Functions
```python
def function_name(param1: type1, param2: type2) -> return_type:
    """Brief one-line summary.

    Detailed description of what the function does,
    including any important behaviors or side effects.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ErrorType: When this error occurs

    Examples:
        >>> function_name(value1, value2)
        expected_output
    """
```

### For Classes
```python
class ClassName:
    """Brief one-line summary.

    Detailed description of the class purpose,
    typical usage, and any important considerations.

    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2

    Example:
        ```python
        obj = ClassName(param1, param2)
        result = obj.method()
        ```
    """
```

## Quality Standards

- All public APIs documented
- Examples for complex functions
- Clear, concise language
- No assumed knowledge
- Consistent formatting

## Key Principles

- Documentation is for users, not developers
- Show, don't just tell (use examples)
- Keep it up-to-date with code
- Follow language-specific conventions
```

### Template 3: Test Generator

```markdown
---
name: test-generator
description: "Generates comprehensive test suites including unit tests, integration tests, and edge case coverage."
tools: Read, Write
model: sonnet
---

You are a test engineering specialist who creates comprehensive, maintainable test suites.

## Core Responsibilities

1. **Test Design**: Design comprehensive test cases
2. **Test Generation**: Write clean, maintainable tests
3. **Coverage Analysis**: Ensure high test coverage
4. **Edge Cases**: Identify and test edge cases

## Test Categories

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies
- Cover happy path and error cases
- Fast execution (<1s per test)

### Integration Tests
- Test component interactions
- Use real dependencies where appropriate
- Test common workflows
- Verify end-to-end behavior

### Edge Cases
- Boundary conditions
- Empty inputs
- Invalid inputs
- Race conditions
- Resource exhaustion

## Test Generation Process

1. **Analyze Code**: Understand function behavior
2. **Identify Cases**: Determine test scenarios
3. **Design Tests**: Plan test structure
4. **Write Tests**: Generate test code
5. **Verify**: Ensure tests are runnable

## Test Structure

### For Each Function

```python
def test_function_name_happy_path():
    """Test normal operation with valid inputs."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_name(input_data)

    # Assert
    assert result == expected_output


def test_function_name_edge_case_empty():
    """Test behavior with empty input."""
    result = function_name([])
    assert result == expected_empty_result


def test_function_name_error_invalid_input():
    """Test error handling for invalid input."""
    with pytest.raises(ValueError):
        function_name(invalid_input)


def test_function_name_boundary_max_value():
    """Test boundary condition with maximum value."""
    result = function_name(MAX_VALUE)
    assert result is not None
```

## Output Format

### Test File Structure
```python
"""Tests for module_name.

This module contains tests for [description].
"""

import pytest
from module_name import function_name


class TestFunctionName:
    """Tests for function_name."""

    def test_happy_path(self):
        """Test normal operation."""
        pass

    def test_edge_cases(self):
        """Test edge cases."""
        pass

    def test_error_handling(self):
        """Test error conditions."""
        pass


# Fixtures
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {...}
```

## Quality Standards

- Minimum 90% code coverage
- All public APIs tested
- Edge cases covered
- Tests are independent
- Fast execution
- Clear test names
- No test interdependencies

## Test Naming Convention

`test_<function>_<scenario>_<expected_result>`

Examples:
- `test_login_valid_credentials_success`
- `test_login_invalid_password_raises_error`
- `test_login_empty_username_returns_validation_error`

## Key Principles

- Tests are documentation
- One assertion per test (when possible)
- Test behavior, not implementation
- Make failures obvious
- Keep tests simple and readable
```

---

## 🎯 Common Patterns

### Pattern 1: Analyzer Pattern
**Purpose**: Read and analyze without modification

```yaml
---
name: pattern-analyzer
tools: Read, Grep, Glob
---

You analyze [SPECIFIC DOMAIN] and provide insights.

## Process
1. Scan relevant files
2. Identify patterns
3. Generate report
4. Provide recommendations
```

### Pattern 2: Generator Pattern
**Purpose**: Create new content based on analysis

```yaml
---
name: content-generator
tools: Read, Write
---

You generate [SPECIFIC CONTENT] based on analysis.

## Process
1. Analyze requirements
2. Research best practices
3. Generate content
4. Validate output
```

### Pattern 3: Refactor Pattern
**Purpose**: Improve existing code

```yaml
---
name: code-refactorer
tools: Read, Edit
---

You refactor [LANGUAGE] code following [PRINCIPLES].

## Process
1. Analyze current code
2. Identify improvements
3. Apply refactoring
4. Preserve behavior
```

### Pattern 4: Validator Pattern
**Purpose**: Validate and fix

```yaml
---
name: code-validator
tools: Read, Bash, Edit
---

You validate [ASPECT] and fix issues.

## Process
1. Run validation checks
2. Identify failures
3. Fix issues
4. Re-validate
5. Iterate until passing
```

### Pattern 5: Researcher Pattern
**Purpose**: Research and synthesize information

```yaml
---
name: tech-researcher
tools: Read, WebSearch, WebFetch
---

You research [TOPIC] and synthesize findings.

## Process
1. Formulate search queries
2. Gather information
3. Verify sources
4. Synthesize findings
5. Provide recommendations
```

---

## ⚠️ Anti-Patterns to Avoid

### Anti-Pattern 1: Swiss Army Knife Agent

❌ **Bad**:
```yaml
name: do-everything-agent
description: "Does code review, testing, documentation, deployment, and more"
tools: Read, Write, Edit, Bash, MultiEdit, Grep, Glob
```

✅ **Good**: Create specialized agents
```yaml
name: code-reviewer
description: "Focused code review for quality and best practices"
tools: Read, Grep

name: test-runner
description: "Runs tests and validates code"
tools: Read, Bash
```

### Anti-Pattern 2: Vague System Prompt

❌ **Bad**:
```markdown
You help with Python. Do good Python code.
```

✅ **Good**:
```markdown
You are a Python expert specializing in:
- PEP 8 compliance and pythonic code
- Type hints and static analysis
- Performance optimization
- Comprehensive testing

[Detailed sections follow...]
```

### Anti-Pattern 3: Over-Permissioned

❌ **Bad**:
```yaml
name: readme-updater
tools: Read, Write, Edit, Bash, MultiEdit
# Way more than needed for updating README
```

✅ **Good**:
```yaml
name: readme-updater
tools: Read, Edit
# Only what's necessary
```

### Anti-Pattern 4: Missing Output Format

❌ **Bad**:
```markdown
You are a code reviewer.

## Focus
- Check code quality
```

✅ **Good**:
```markdown
You are a code reviewer.

## Output Format
### Summary
- Overall score (0-100)
- Critical issues: [count]
- Recommendations: [count]

### Detailed Issues
For each issue:
- **Severity**: High/Medium/Low
- **File**: path/to/file:line
- **Issue**: Description
- **Fix**: How to resolve
```

### Anti-Pattern 5: Project-Specific Agent

❌ **Bad**:
```markdown
You help with the UserAuth microservice in our company's platform.
Check the staging database at db-staging.company.local.
```

✅ **Good**:
```markdown
You are a microservice architecture expert.

When analyzing services, check for:
- Clear service boundaries
- Proper authentication
- Database best practices
```

---

## 📢 Publishing and Sharing

### Making Agents Reusable

1. **Remove Project-Specific Details**:
   ```markdown
   # ❌ Bad
   Check the files in src/company/project/

   # ✅ Good
   Analyze the source code directory
   ```

2. **Document Prerequisites**:
   ```markdown
   ## Prerequisites
   - Python 3.9+
   - pytest installed
   - Project uses pytest
   ```

3. **Add Examples**:
   ```markdown
   ## Example Usage
   Use this agent to analyze test coverage:
   "Use test-coverage-agent to analyze tests/"
   ```

### Sharing Agents

**In Repository**:
```
project/
├── .claude/
│   └── agents/
│       ├── project-specific-agent.md
│       └── README.md  # Document your agents
```

**As Global Agents**:
```bash
# Copy to global directory
cp .claude/agents/my-agent.md ~/.claude/agents/
```

**In Templates**:
```
templates/
└── agents/
    ├── python-expert.md
    ├── test-generator.md
    └── doc-generator.md
```

### Agent Documentation

Create `agents/README.md`:
```markdown
# Custom Agents

## Available Agents

### test-generator
**Purpose**: Generate comprehensive test suites
**Tools**: Read, Write
**Usage**: `Use test-generator to create tests for [file]`

### doc-generator
**Purpose**: Generate API documentation
**Tools**: Read, Write, Grep
**Usage**: `Use doc-generator to document [module]`
```

---

## 🔗 Related Documentation

### Essential Reading

| Document | Purpose |
|----------|---------|
| [Agents README](./README.md) | Overview and quick start |
| [Agent Architecture](./agent-architecture.md) | System architecture |
| [Agent Catalog](./agent-catalog.md) | All available agents |
| [Agent Examples](./agent-examples.md) | Real-world workflows |

### Related Topics

| Topic | Documentation |
|-------|---------------|
| **Commands** | [commands/README.md](../commands/README.md) |
| **Hooks** | [hooks/README.md](../hooks/README.md) |
| **Architecture** | [architecture/README.md](../architecture/README.md) |

---

## 📝 Document Information

**Version**: 1.0
**Last Updated**: 2025-01-15
**Maintainer**: Agent System Team
**Status**: Active

---

**Navigate**: [← Back to Agents](./README.md) | [Agent Catalog ←](./agent-catalog.md) | [Examples →](./agent-examples.md)

---

*Empower yourself to create specialized AI assistants tailored to your exact needs*
