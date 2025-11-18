# Azure Setup Command

Setup Azure resources with best practices validation and automated configuration.

## Usage
```
/azure-setup [--environment=dev|staging|prod] [--region=eastus|westus|northeurope] [--create-resources]
```

## Description
Sets up Azure resources following best practices, validates configuration, and ensures proper security and monitoring.

## Implementation
1. **Environment Planning**: Plan resource architecture based on environment
2. **Resource Creation**: Create Azure resources with proper configuration
3. **Security Configuration**: Apply security best practices
4. **Monitoring Setup**: Configure monitoring and alerting
5. **Cost Optimization**: Apply cost optimization strategies
6. **Documentation**: Document all created resources and configurations

## Output Format
```
🏗️ Azure Environment Setup
===========================

📋 Setup Configuration:
- Environment: {environment}
- Region: {region}
- Subscription: {subscription_name}
- Resource Group: {resource_group_name}

🔧 Resources Created/Validated:

## Core Services:
- ✅ Resource Group: {rg_name} ({region})
- ✅ Azure OpenAI: {openai_name} ({sku})
- ✅ AI Foundry Project: {project_name}
- ✅ Key Vault: {keyvault_name}
- ✅ Storage Account: {storage_name}

## Networking:
- ✅ Virtual Network: {vnet_name}
- ✅ Private Endpoints: {endpoint_count} created
- ✅ Network Security Groups: Configured
- ✅ DNS Zones: Private zones configured

## Security Configuration:
- ✅ Service Principal: Created and configured
- ✅ RBAC Roles: Assigned with least privilege
- ✅ Key Vault Policies: Configured
- ✅ Private Endpoints: All services secured
- ✅ Audit Logging: Enabled

## Monitoring & Observability:
- ✅ Log Analytics: Workspace created
- ✅ Application Insights: Configured
- ✅ Azure Monitor: Alerts configured
- ✅ Cost Alerts: Budget alerts set

💰 Cost Configuration:
- Monthly Budget: ${budget_amount}
- Cost Alerts: At 50%, 80%, 100%
- Optimization: Auto-shutdown enabled
- Resource Tags: Cost center tracking

🔐 Security Summary:
- All resources use managed identities
- Private endpoints for all services
- Network isolation implemented
- Audit logging enabled
- Compliance: SOC 2, ISO 27001 ready

📊 Configuration Details:
- OpenAI Models: {deployed_models}
- Storage: {storage_type} with {redundancy}
- Networking: Private access only
- Backup: Enabled with {retention} days
- DR: Cross-region replication enabled

🔑 Access Configuration:
- Service Principal ID: {sp_id}
- Key Vault URL: {kv_url}
- OpenAI Endpoint: {openai_endpoint}
- Storage Connection: Via managed identity

📝 Environment Variables:
{environment_variables_template}

🎯 Next Steps:
1. Update application configuration
2. Deploy application code
3. Run connectivity tests
4. Configure CI/CD pipeline
5. Set up monitoring dashboards

📚 Documentation Generated:
- Architecture diagram: ✅
- Security configuration: ✅
- Cost analysis report: ✅
- Troubleshooting guide: ✅
- Deployment checklist: ✅
```

## Environment Types
- `dev`: Development environment with minimal resources
- `staging`: Staging environment with production-like setup
- `prod`: Production environment with high availability (default)

## Region Options
- `eastus`: East US (default)
- `westus`: West US
- `northeurope`: North Europe
- `southeastasia`: Southeast Asia

## MCP Servers Used
- **Azure-mcp MCP**: Resource creation and configuration
- **Azure Resource Graph MCP**: Resource validation and monitoring
- **Microsoft Docs MCP**: Best practices implementation
- **Analysis Tool**: Cost calculations and optimization
- **Crawl4ai-rag**: Store configuration patterns and templates
