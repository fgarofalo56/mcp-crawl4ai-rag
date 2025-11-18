# Azure Validate Command

Comprehensive Azure configuration and best practices validation.

## Usage
```
/azure-validate [--component=all|auth|resources|security|costs]
```

## Description
Validates Azure configuration, resources, security settings, and best practices compliance using multiple Azure-focused MCP servers.

## Implementation
1. **Authentication Check**: Verify Azure credentials and permissions
2. **Resource Analysis**: Review current Azure resources and configuration
3. **Security Validation**: Check security settings and compliance
4. **Cost Analysis**: Estimate and validate current/projected costs
5. **Best Practices**: Compare against Microsoft recommendations
6. **Documentation Review**: Ensure all configurations are documented

## Output Format
```
🔵 Azure Configuration Validation
=================================

🔐 Authentication Status:
- Service Principal: {status}
- Permissions: {validated_permissions}
- Key Vault Access: {status}
- Token Expiration: {date}

🏗️ Resource Analysis:
- Resource Group: {name} ({region})
- OpenAI Service: {status} ({sku})
- AI Project: {status}
- Storage Accounts: {count}
- Networking: {vnet_status}

💰 Cost Analysis:
- Current Month Spend: ${amount}
- Projected Month: ${amount}
- Budget Status: {within/over/approaching}
- Cost Optimization Opportunities: {suggestions}

🔒 Security Validation:
- Private Endpoints: {status}
- Network Security Groups: {status}
- RBAC Configuration: {status}
- Audit Logging: {status}
- Compliance Score: {percentage}%

✅ Best Practices Compliance:
- Naming Conventions: {status}
- Resource Tagging: {status}
- Backup Configuration: {status}
- Disaster Recovery: {status}
- Monitoring Setup: {status}

⚠️ Issues Found:
{numbered_list_of_issues}

💡 Recommendations:
{numbered_list_of_recommendations}

🎯 Action Items:
{prioritized_action_items}
```

## Parameters
- `--component=all`: Full validation (default)
- `--component=auth`: Authentication only
- `--component=resources`: Resource configuration only
- `--component=security`: Security settings only
- `--component=costs`: Cost analysis only

## MCP Servers Used
- **Azure-mcp MCP**: Azure tools and services validation
- **Azure Resource Graph MCP**: Resource analysis and querying
- **Microsoft Docs MCP**: Best practices verification
- **Analysis Tool**: Cost calculations and compliance scoring
