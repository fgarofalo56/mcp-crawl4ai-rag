# Troubleshoot Command

Multi-MCP troubleshooting workflow for comprehensive problem diagnosis and resolution.

## Usage
```
/troubleshoot <problem_description> [--severity=low|medium|high|critical] [--category=code|infrastructure|performance|security]
```

## Description
Comprehensive troubleshooting workflow that leverages multiple MCP servers for problem diagnosis, solution research, and resolution implementation.

## Implementation
1. **Problem Analysis**: Use sequential thinking to break down the issue
2. **Information Gathering**: Collect relevant logs, configurations, and context
3. **Multi-Source Research**: Query multiple MCP servers for solutions
4. **Pattern Matching**: Search knowledge base for similar issues
5. **Solution Synthesis**: Combine findings into actionable solutions
6. **Implementation Guidance**: Provide step-by-step resolution steps
7. **Prevention Strategies**: Recommend preventive measures
8. **Knowledge Storage**: Store solution for future reference

## Output Format
```
🔧 Troubleshooting Analysis
===========================

🚨 Problem Summary:
- Issue: {problem_description}
- Severity: {severity_level}
- Category: {category}
- First Reported: {timestamp}
- Affected Components: {component_list}

🔍 Diagnostic Analysis:

## System Information:
- Environment: {environment}
- Version: {application_version}
- Dependencies: {dependency_versions}
- Configuration: {config_status}

## Error Analysis:
- Error Type: {error_classification}
- Error Code: {error_code}
- Stack Trace: {relevant_stack_trace}
- Frequency: {occurrence_frequency}

## Impact Assessment:
- Affected Users: {user_count}
- Affected Features: {feature_list}
- Performance Impact: {performance_metrics}
- Business Impact: {business_impact_level}

📚 Research Findings:

## Microsoft Documentation:
{microsoft_docs_findings}

## Community Solutions:
{community_solutions_summary}

## Knowledge Base Matches:
{similar_issues_from_kb}

## Code Analysis:
{serena_code_analysis}

## Azure Service Status:
{azure_service_health}

💡 Root Cause Analysis:
{sequential_thinking_analysis}

🛠️ Solution Options:

### Option 1: Quick Fix ({estimated_time})
{quick_fix_steps}

### Option 2: Comprehensive Solution ({estimated_time})
{comprehensive_solution_steps}

### Option 3: Architectural Change ({estimated_time})
{architectural_solution_steps}

🎯 Recommended Solution:
{recommended_solution_with_reasoning}

📋 Implementation Steps:
1. {step_1_with_details}
2. {step_2_with_details}
3. {step_3_with_details}
4. {validation_steps}

⚠️ Risk Assessment:
- Implementation Risk: {risk_level}
- Rollback Plan: {rollback_steps}
- Testing Requirements: {testing_needed}
- Dependencies: {dependency_considerations}

🔮 Prevention Strategies:
{prevention_recommendations}

📊 Success Metrics:
- Resolution Indicators: {success_indicators}
- Performance Benchmarks: {performance_targets}
- Monitoring Alerts: {recommended_alerts}

🧠 Knowledge Base Update:
- Problem Pattern: ✅ Stored
- Solution Steps: ✅ Documented
- Prevention Measures: ✅ Added
- Related Issues: ✅ Cross-referenced

🔄 Follow-up Actions:
{follow_up_recommendations}

📈 Learning Opportunities:
{process_improvements}
```

## Severity Levels
- `critical`: System down, major functionality broken
- `high`: Significant feature impairment, performance degradation
- `medium`: Minor feature issues, workarounds available (default)
- `low`: Cosmetic issues, nice-to-have improvements

## Category Focus
- `code`: Application code issues
- `infrastructure`: Infrastructure and deployment issues
- `performance`: Performance and optimization issues
- `security`: Security vulnerabilities and concerns

## MCP Servers Used
- **AI-Server-Sequential-thinking**: Root cause analysis and logical reasoning
- **Microsoft Docs MCP**: Official troubleshooting documentation
- **Brave Search MCP**: Community solutions and recent fixes
- **Serena MCP**: Code analysis and bug detection
- **Azure-mcp MCP**: Azure service diagnostics
- **Crawl4ai-rag**: Similar issue pattern matching
- **Analysis Tool**: Impact analysis and metrics calculation
