# Regression Check Command

Check for regressions using Serena code analysis and comprehensive testing.

## Usage
```
/regression-check [--baseline=commit|tag|branch] [--scope=code|functionality|performance|all]
```

## Description
Comprehensive regression analysis comparing current code state against a baseline, identifying potential regressions in functionality, performance, and code quality.

## Implementation
1. **Baseline Comparison**: Compare current state against specified baseline
2. **Code Analysis**: Use Serena MCP for semantic code comparison
3. **Functional Testing**: Execute regression test suite
4. **Performance Comparison**: Compare performance metrics against baseline
5. **Quality Analysis**: Assess code quality changes
6. **Risk Assessment**: Identify regression risks and impacts

## Output Format
```
🔄 Regression Analysis Report
=============================

📊 Analysis Summary:
- Baseline: {baseline_reference}
- Current State: {current_commit}
- Files Changed: {changed_files_count}
- Test Cases: {test_cases_executed}
- Analysis Duration: {duration}

📈 Code Change Analysis:

## Changed Components:
- Domain Layer: {domain_changes} files
- Infrastructure Layer: {infra_changes} files
- Services Layer: {services_changes} files
- Presentation Layer: {presentation_changes} files
- Tests: {test_changes} files

## Change Impact:
- Critical Components: {critical_changes} ⚠️
- High-Risk Areas: {high_risk_changes}
- Low-Risk Changes: {low_risk_changes}
- New Features: {new_features_count}

🧪 Functional Regression Tests:

## Test Results Comparison:
- Baseline Tests: {baseline_tests_passed}/{baseline_tests_total} passed
- Current Tests: {current_tests_passed}/{current_tests_total} passed
- New Failures: {new_failures} ❌
- Fixed Issues: {fixed_issues} ✅
- New Tests: {new_tests_added}

## Failed Test Analysis:
{detailed_test_failure_analysis}

## Critical Functionality:
- Authentication: {auth_status}
- Core Business Logic: {core_logic_status}
- Data Processing: {data_processing_status}
- External Integrations: {integration_status}

⚡ Performance Regression Analysis:

## Response Time Comparison:
- Baseline Avg: {baseline_response_time}ms
- Current Avg: {current_response_time}ms
- Change: {response_time_change}ms ({change_percentage}%)

## Throughput Analysis:
- Baseline RPS: {baseline_rps}
- Current RPS: {current_rps}
- Change: {rps_change} ({rps_change_percentage}%)

## Resource Usage:
- Memory Usage Change: {memory_change}%
- CPU Usage Change: {cpu_change}%
- Database Query Performance: {db_performance_change}%

🔍 Code Quality Analysis:

## Quality Metrics Comparison:
- Code Quality Score: {baseline_quality} → {current_quality}
- Test Coverage: {baseline_coverage}% → {current_coverage}%
- Complexity Score: {baseline_complexity} → {current_complexity}
- Technical Debt: {baseline_debt} → {current_debt}

## Semantic Analysis (Serena):
- Breaking Changes: {breaking_changes_count}
- API Compatibility: {api_compatibility_status}
- Interface Changes: {interface_changes_count}
- Deprecated Usage: {deprecated_usage_count}

🚨 Regression Risk Assessment:

## High-Risk Regressions ({high_risk_count}):
{high_risk_regression_list}

## Medium-Risk Changes ({medium_risk_count}):
{medium_risk_change_list}

## Low-Risk Changes ({low_risk_count}):
{low_risk_change_summary}

🔒 Security Regression Analysis:
- New Security Issues: {new_security_issues}
- Fixed Security Issues: {fixed_security_issues}
- Security Score Change: {security_score_change}
- Authentication Impact: {auth_security_impact}

📊 Integration Impact:

## External Service Integration:
- Azure OpenAI: {azure_openai_impact}
- Database Connections: {database_impact}
- Third-party APIs: {api_integration_impact}
- File Storage: {storage_impact}

## Dependency Analysis:
- New Dependencies: {new_dependencies}
- Updated Dependencies: {updated_dependencies}
- Removed Dependencies: {removed_dependencies}
- Version Conflicts: {version_conflicts}

💡 Recommendations:

## Immediate Actions:
1. {immediate_action_1}
2. {immediate_action_2}
3. {immediate_action_3}

## Risk Mitigation:
1. {risk_mitigation_1}
2. {risk_mitigation_2}

## Testing Recommendations:
1. {testing_recommendation_1}
2. {testing_recommendation_2}

🎯 Deployment Readiness:
- Overall Risk Level: {overall_risk_level}
- Deployment Recommendation: {deployment_recommendation}
- Required Testing: {required_testing}
- Rollback Plan: {rollback_readiness}

📈 Change Summary:
- Total Lines Changed: {lines_changed}
- Files Modified: {files_modified}
- Functions Added: {functions_added}
- Functions Modified: {functions_modified}
- Functions Removed: {functions_removed}

🔄 Continuous Integration Impact:
- Build Status: {build_status}
- Test Suite Duration: {test_duration_change}
- Pipeline Success Rate: {pipeline_success_rate}
```

## Baseline Options
- `--baseline=HEAD~1`: Compare against previous commit (default)
- `--baseline=main`: Compare against main branch
- `--baseline=v1.0.0`: Compare against specific tag
- `--baseline=feature/branch`: Compare against specific branch

## Scope Options
- `--scope=code`: Code-only regression analysis
- `--scope=functionality`: Functional regression testing only
- `--scope=performance`: Performance regression only
- `--scope=all`: Comprehensive regression analysis (default)

## Regression Categories
- **Functional Regressions**: Broken existing functionality
- **Performance Regressions**: Degraded performance metrics
- **Security Regressions**: Introduced security vulnerabilities
- **API Regressions**: Breaking changes to interfaces
- **Integration Regressions**: External service integration issues

## MCP Servers Used
- **Serena MCP**: Semantic code analysis and change impact assessment
- **Playwright MCP**: UI regression testing and visual comparison
- **Analysis Tool**: Performance metrics comparison and statistical analysis
- **Azure-mcp MCP**: Azure service integration regression testing
- **AI-Server-Sequential-thinking**: Risk assessment and impact analysis
