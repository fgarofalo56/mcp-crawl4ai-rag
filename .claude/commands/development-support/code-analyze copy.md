# Code Analyze Command

Comprehensive code analysis using semantic analysis, best practices validation, and pattern recognition.

## Usage

/code-analyze [file_path] [--scope=file|directory|project] [--focus=quality|security|performance|all]

## Description

Performs deep code analysis using AI-powered tools to identify issues, suggest improvements, and validate against best practices.

## Implementation

1. **Semantic Analysis**: Use Serena MCP for intelligent code understanding
2. **Pattern Recognition**: Identify code patterns and anti-patterns
3. **Quality Assessment**: Check code quality metrics and standards
4. **Security Scan**: Identify potential security vulnerabilities
5. **Performance Analysis**: Identify performance bottlenecks
6. **Best Practices**: Validate against Azure and general best practices

## Output Format

🔍 Code Analysis Report
📁 Analysis Scope:

Target: {file_path_or_scope}
Lines Analyzed: {count}
Files Processed: {count}
Analysis Duration: {seconds}s

🎯 Overall Assessment:

Code Quality Score: {score}/100
Security Rating: {A-F}
Performance Rating: {A-F}
Maintainability Index: {score}

⚠️ Critical Issues ({count}):
{list_of_critical_issues}
🟡 Warnings ({count}):
{list_of_warnings}
💡 Improvements ({count}):
{list_of_improvement_suggestions}
🏗️ Architecture Analysis:

Clean Architecture Compliance: {percentage}%
SOLID Principles: {compliance_status}
Design Patterns Used: {pattern_list}
Coupling Analysis: {loose/tight}

🔒 Security Assessment:

Potential Vulnerabilities: {count}
Input Validation: {status}
Authentication Patterns: {status}
Secrets Management: {status}

⚡ Performance Analysis:

Algorithmic Complexity: {analysis}
Memory Usage Patterns: {analysis}
I/O Operations: {analysis}
Optimization Opportunities: {count}

📊 Code Metrics:

Cyclomatic Complexity: {average}
Code Duplication: {percentage}%
Test Coverage: {percentage}%
Documentation Coverage: {percentage}%

🎯 Recommended Actions:

{priority_1_action}
{priority_2_action}
{priority_3_action}

💾 Analysis Stored:

Knowledge Base: ✅ Patterns and solutions stored
Project Memory: ✅ Analysis results saved

## Focus Options

- `--focus=quality`: Code quality and maintainability
- `--focus=security`: Security vulnerabilities and best practices
- `--focus=performance`: Performance optimization opportunities
- `--focus=all`: Comprehensive analysis (default)

## MCP Servers Used

- **Serena MCP**: Semantic code analysis and intelligent suggestions
- **AI-Server-Sequential-thinking**: Complex analysis reasoning
- **Microsoft Docs MCP**: Best practices validation
- **Crawl4ai-rag**: Pattern comparison and storage
- **Analysis Tool**: Metrics calculation and scoring
