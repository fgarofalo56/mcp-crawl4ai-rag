# Standards Review Command

Review code against Azure best practices and development standards.

## Usage
```
/standards-review [--scope=code|docs|config|all] [--framework=azure-ai|semantic-kernel|autogen]
```

## Description
Comprehensive review of code, documentation, and configuration against Azure best practices and project standards.

## Implementation
1. **Azure Standards Check**: Validate against Azure development best practices
2. **Framework Compliance**: Check framework-specific standards
3. **Code Quality Review**: Assess code quality and patterns
4. **Security Standards**: Validate security implementations
5. **Documentation Standards**: Check documentation completeness
6. **Configuration Review**: Validate configuration standards

## Output Format
```
📋 Standards Compliance Review
==============================

🎯 Review Scope:
- Framework: {framework_name}
- Components Reviewed: {component_count}
- Standards Applied: {standards_count}
- Review Duration: {duration}

📊 Overall Compliance:
- Azure Best Practices: {percentage}% compliant
- Framework Standards: {percentage}% compliant
- Security Standards: {percentage}% compliant
- Documentation Standards: {percentage}% compliant
- Overall Score: {score}/100

🔵 Azure Best Practices Review:

## Authentication & Security:
- ✅ Uses DefaultAzureCredential pattern
- ✅ Managed Identity implementation
- ⚠️ Key Vault integration: {status}
- ✅ Private endpoints configured
- ✅ RBAC permissions: Least privilege applied

## Resource Configuration:
- ✅ Proper resource naming conventions
- ✅ Resource tagging strategy implemented
- ✅ Cost optimization applied
- ⚠️ Monitoring setup: {completeness}%
- ✅ Backup and DR configured

## AI/ML Best Practices:
- ✅ Azure OpenAI integration patterns
- ✅ Token usage optimization
- ✅ Rate limit handling
- ⚠️ Content filtering: {status}
- ✅ Error handling and retry logic

🔧 Framework-Specific Standards:

## {Framework Name} Compliance:
- API Usage: {compliance_status}
- Pattern Implementation: {pattern_score}/100
- Performance Optimization: {perf_score}/100
- Error Handling: {error_handling_score}/100

🔒 Security Standards Review:

## Code Security:
- Input Validation: {validation_status}
- Output Sanitization: {sanitization_status}
- Secret Management: {secret_mgmt_status}
- Authentication Flow: {auth_flow_status}

## Infrastructure Security:
- Network Security: {network_security_status}
- Data Encryption: {encryption_status}
- Access Control: {access_control_status}
- Audit Logging: {audit_logging_status}

📚 Documentation Standards:

## Code Documentation:
- Inline Comments: {comment_coverage}%
- API Documentation: {api_doc_status}
- Architecture Documentation: {arch_doc_status}
- Troubleshooting Guides: {troubleshoot_status}

## Project Documentation:
- README Quality: {readme_score}/100
- Setup Instructions: {setup_completeness}%
- Configuration Guide: {config_guide_status}
- Deployment Guide: {deploy_guide_status}

⚠️ Standards Violations ({violation_count}):

## High Priority:
{high_priority_violations}

## Medium Priority:
{medium_priority_violations}

## Low Priority:
{low_priority_violations}

💡 Improvement Recommendations:

## Immediate Actions:
1. {immediate_action_1}
2. {immediate_action_2}
3. {immediate_action_3}

## Short-term Improvements:
1. {short_term_1}
2. {short_term_2}

## Long-term Enhancements:
1. {long_term_1}
2. {long_term_2}

📈 Standards Compliance Trend:
- Previous Review Score: {previous_score}/100
- Current Review Score: {current_score}/100
- Improvement: {improvement_trend}
- Time to Full Compliance: {estimated_time}

🎯 Action Plan:
{detailed_action_plan_with_priorities}

✅ Compliance Checklist:
{checklist_of_standards_to_address}
```

## Scope Options
- `--scope=code`: Code quality and patterns only
- `--scope=docs`: Documentation standards only
- `--scope=config`: Configuration and infrastructure only
- `--scope=all`: Comprehensive review (default)

## Framework Options
- `--framework=azure-ai`: Azure AI Agent Service standards
- `--framework=semantic-kernel`: Semantic Kernel best practices
- `--framework=autogen`: AutoGen framework standards

## Standards Categories
- **Azure Best Practices**: Official Microsoft recommendations
- **Security Standards**: Security implementation patterns
- **Performance Standards**: Performance optimization guidelines
- **Code Quality Standards**: Clean code and architecture principles
- **Documentation Standards**: Project documentation requirements

## MCP Servers Used
- **Microsoft Docs MCP**: Azure best practices and official standards
- **Serena MCP**: Code quality analysis and pattern detection
- **Azure-mcp MCP**: Azure-specific configuration validation
- **Analysis Tool**: Compliance scoring and trend analysis
- **Crawl4ai-rag**: Best practices knowledge base
