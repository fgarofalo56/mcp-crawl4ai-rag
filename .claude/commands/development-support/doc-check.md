# Documentation Check Command

Validate documentation against style guide and completeness standards.

## Usage
```
/doc-check [path] [--fix-auto] [--report-format=summary|detailed|json]
```

## Description
Validates all documentation against the markdown style guide, checks for completeness, and suggests improvements.

## Implementation
1. **Style Guide Validation**: Check against `docs/guides/MARKDOWN_STYLE_GUIDE.md`
2. **Structure Validation**: Verify directory structure compliance
3. **Content Analysis**: Check for completeness and clarity
4. **Link Validation**: Verify all internal and external links
5. **Markup Validation**: Run markdownlint and custom validators
6. **Auto-Fix**: Apply automatic fixes where possible

## Output Format
```
📖 Documentation Validation Report
===================================

📊 Validation Summary:
- Files Checked: {count}
- Style Guide Compliance: {percentage}%
- Structure Compliance: {percentage}%
- Link Validity: {percentage}%
- Overall Score: {score}/100

✅ Compliant Files ({count}):
{list_of_compliant_files}

⚠️ Issues Found ({count}):

## Style Guide Violations:
{numbered_list_of_style_violations}

## Structure Issues:
{numbered_list_of_structure_issues}

## Content Issues:
{numbered_list_of_content_issues}

## Broken Links ({count}):
{list_of_broken_links}

🔧 Auto-Fixable Issues ({count}):
{list_of_auto_fixable_issues}

📋 Missing Documentation:
- API Endpoints: {missing_count}
- Configuration Options: {missing_count}
- Error Handling: {missing_count}
- Deployment Steps: {missing_count}

💡 Improvement Suggestions:
{numbered_list_of_suggestions}

🎯 Priority Fixes:
1. {priority_1}
2. {priority_2}
3. {priority_3}

📈 Progress Tracking:
- Last Check: {timestamp}
- Issues Fixed Since Last Check: {count}
- New Issues: {count}
- Improvement Trend: {improving/declining/stable}
```

## Options
- `--fix-auto`: Automatically apply fixable issues
- `--report-format=summary`: Brief summary (default)
- `--report-format=detailed`: Full detailed report
- `--report-format=json`: JSON format for CI/CD integration

## Validation Rules
- Markdown syntax and formatting
- Header hierarchy and structure
- Code block syntax highlighting
- Table formatting
- Link validity and anchors
- Image alt text and sizing
- Directory structure compliance
- README file presence and completeness

## MCP Servers Used
- **Filesystem MCP**: File structure analysis
- **Microsoft Docs MCP**: Documentation best practices
- **Brave Search MCP**: External link validation
- **Analysis Tool**: Compliance scoring and statistics
