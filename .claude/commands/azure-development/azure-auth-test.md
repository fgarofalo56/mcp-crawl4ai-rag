# Azure Authentication Test Command

Test Azure authentication across all services and validate permissions.

## Usage
```
/azure-auth-test [--service=all|openai|storage|keyvault|ai-project] [--fix-issues]
```

## Description
Comprehensive testing of Azure authentication across all integrated services, validates permissions, and provides troubleshooting guidance.

## Implementation
1. **Credential Validation**: Test all Azure credential types
2. **Service Connectivity**: Test connection to each Azure service
3. **Permission Verification**: Validate required permissions
4. **Token Health**: Check token expiration and refresh
5. **Troubleshooting**: Identify and suggest fixes for issues
6. **Documentation**: Update authentication documentation

## Output Format
```
🔐 Azure Authentication Test Results
====================================

📊 Test Summary:
- Services Tested: {service_count}
- Authentication Methods: {auth_methods}
- Overall Status: {pass/fail/warnings}
- Test Duration: {duration}s

🔑 Credential Validation:

## Service Principal:
- Client ID: {masked_client_id}
- Tenant ID: {tenant_id}
- Secret Status: ✅ Valid (expires: {expiration_date})
- Token Generation: ✅ Successful

## Managed Identity:
- System Assigned: {status}
- User Assigned: {status}
- Azure Metadata Service: {status}

🌐 Service Connectivity Tests:

## Azure OpenAI Service:
- Endpoint: {endpoint_url}
- Authentication: ✅ Successful
- Permissions: ✅ Cognitive Services User
- Model Access: ✅ {model_count} models available
- Rate Limits: {current_usage}/{limit}

## Key Vault:
- Vault URL: {keyvault_url}
- Authentication: ✅ Successful
- Permissions: ✅ Get, List secrets
- Certificate Access: {cert_status}
- Secret Retrieval: ✅ Test successful

## Storage Account:
- Account Name: {storage_account}
- Authentication: ✅ Successful
- Permissions: ✅ Storage Blob Data Contributor
- Container Access: ✅ Read/Write confirmed
- Connection String: ✅ Valid

## AI Foundry Project:
- Project Endpoint: {ai_project_endpoint}
- Authentication: ✅ Successful
- Permissions: ✅ AI Developer
- Agent Service: ✅ Available
- Model Deployments: {deployment_count} active

## Azure Resource Graph:
- Query Access: ✅ Successful
- Permissions: ✅ Reader
- Resource Discovery: ✅ {resource_count} resources found
- Subscription Access: ✅ Confirmed

🔍 Permission Analysis:
- Required Permissions: {required_count}
- Granted Permissions: {granted_count}
- Missing Permissions: {missing_count}
- Excessive Permissions: {excessive_count}

⚠️ Issues Detected ({issue_count}):
{list_of_authentication_issues}

🛠️ Troubleshooting Guidance:
{step_by_step_troubleshooting}

💡 Optimization Recommendations:
{security_and_performance_recommendations}

📊 Authentication Metrics:
- Token Refresh Rate: {refresh_frequency}
- Average Response Time: {avg_response_time}ms
- Error Rate: {error_percentage}%
- Success Rate: {success_percentage}%

🔄 Auto-Fix Results (if --fix-issues used):
{list_of_attempted_fixes}

🎯 Action Items:
{prioritized_action_items}

✅ Authentication Health Score: {score}/100
```

## Service Options
- `all`: Test all Azure services (default)
- `openai`: Azure OpenAI only
- `storage`: Storage Account only
- `keyvault`: Key Vault only
- `ai-project`: AI Foundry Project only

## Parameters
- `--fix-issues`: Attempt automatic fixes for common issues

## Common issues Detected
- Expired service principal secrets
- Missing RBAC permissions
- Network connectivity issues
- Token refresh failures
- Service endpoint configuration errors

## MCP Servers Used
- **Azure-mcp MCP**: Service connectivity testing
- **Azure Resource Graph MCP**: Permission validation
- **Microsoft Docs MCP**: Authentication best practices
- **Analysis Tool**: Performance metrics and health scoring
