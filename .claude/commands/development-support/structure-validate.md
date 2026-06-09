# Structure Validate Command

Validate project directory structure against clean architecture standards.

## Usage
```
/structure-validate [--fix-violations] [--report-level=summary|detailed|architectural]
```

## Description
Validates the project directory structure against the universal clean architecture template and identifies violations or improvements.

## Implementation
1. **Structure Mapping**: Map current structure to clean architecture template
2. **Violation Detection**: Identify files in incorrect locations
3. **Layer Analysis**: Validate architectural layer separation
4. **Dependency Validation**: Check for circular or improper dependencies
5. **Naming Convention**: Validate naming conventions and patterns
6. **Improvement Suggestions**: Recommend structure optimizations

## Output Format
```
🏗️ Directory Structure Validation
==================================

📊 Structure Compliance:
- Overall Compliance: {percentage}%
- Clean Architecture Score: {score}/100
- Directory Organization: {percentage}%
- File Placement Accuracy: {percentage}%

✅ Compliant Areas:
{list_of_compliant_areas}

❌ Structure Violations ({count}):

## Misplaced Files:
{file_path} → Should be in: {correct_path}
{file_path} → Should be in: {correct_path}

## Missing Directories:
{list_of_missing_required_directories}

## Architectural Violations:
{list_of_layer_violations}

## Naming Convention Issues:
{list_of_naming_issues}

🏛️ Layer Analysis:

### Domain Layer:
- Files: {count}
- External Dependencies: {count} ⚠️
- Purity Score: {percentage}%

### Infrastructure Layer:
- Files: {count}
- External Integrations: {count}
- Organization Score: {percentage}%

### Services Layer:
- Files: {count}
- Orchestration Patterns: {detected_patterns}
- Complexity Score: {percentage}%

### Presentation Layer:
- Files: {count}
- Interface Types: {list_types}
- Separation Score: {percentage}%

📁 Directory Health:
- Empty Directories: {count}
- Oversized Directories: {count}
- Deeply Nested Paths: {count}
- Recommended Splits: {count}

🔗 Dependency Analysis:
- Circular Dependencies: {count} ❌
- Improper Layer Dependencies: {count} ⚠️
- Clean Dependencies: {count} ✅

🛠️ Auto-Fixable Issues ({count}):
{list_of_auto_fixes}

💡 Recommended Improvements:
1. {improvement_1}
2. {improvement_2}
3. {improvement_3}

📋 Action Plan:
{step_by_step_action_plan}

🎯 Target Structure Preview:
{ascii_tree_of_recommended_structure}
```

## Report Levels
- `--report-level=summary`: High-level compliance overview
- `--report-level=detailed`: File-by-file analysis (default)
- `--report-level=architectural`: Deep architectural analysis

## Validation Criteria
- Clean architecture layer separation
- File placement according to responsibility
- Naming convention compliance
- Directory organization efficiency
- Dependency flow validation
- Test directory separation
- Configuration file placement

## MCP Servers Used
- **Filesystem MCP**: Directory structure analysis
- **Serena MCP**: Code dependency analysis
- **Analysis Tool**: Compliance scoring and metrics
- **AI-Server-Sequential-thinking**: Architectural reasoning
