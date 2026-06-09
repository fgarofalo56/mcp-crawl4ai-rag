# Azure Quota Check Command

Check Azure quotas and limits using Resource Graph and provide capacity planning.

## Usage
```
/azure-quota-check [--service=all|openai|compute|storage|networking] [--region=current|all]
```

## Description
Checks current Azure resource usage against quotas and limits, provides capacity planning recommendations, and identifies potential bottlenecks.

## Implementation
1. **Current Usage Analysis**: Query current resource usage across services
2. **Quota Retrieval**: Get quota limits for all relevant services
3. **Capacity Planning**: Calculate remaining capacity and growth projections
4. **Bottleneck Identification**: Identify services approaching limits
5. **Recommendations**: Suggest quota increases or optimizations
6. **Alerting Setup**: Configure monitoring for quota thresholds

## Output Format
```
📊 Azure Quota and Capacity Analysis
====================================

🔍 Analysis Scope:
- Services Checked: {service_count}
- Regions Analyzed: {region_list}
- Subscription: {subscription_name}
- Analysis Date: {timestamp}

⚡ Azure OpenAI Service:

## Token Limits:
- Tokens per Minute (TPM): {current_tpm}/{limit_tpm} ({percentage}% used)
- Requests per Minute: {current_rpm}/{limit_rpm} ({percentage}% used)
- Daily Token Limit: {current_daily}/{limit_daily} ({percentage}% used)

## Model Deployments:
- GPT-4o: {deployments}/{limit} deployments
- GPT-4o-mini: {deployments}/{limit} deployments
- Text Embeddings: {deployments}/{limit} deployments
- Available Capacity: {available_capacity} TPM

## Regional Availability:
- East US: {availability_status}
- West US: {availability_status}
- Europe: {availability_status}

💾 Storage Services:

## Storage Accounts:
- Current Accounts: {current}/{limit} per region
- Total Storage Used: {used_tb} TB / {limit_tb} TB
- IOPS Usage: {current_iops}/{limit_iops}

## Blob Storage:
- Hot Tier Usage: {hot_usage} GB
- Cool Tier Usage: {cool_usage} GB
- Archive Tier Usage: {archive_usage} GB

🖥️ Compute Resources:

## Virtual Machines:
- vCPU Usage: {vcpu_used}/{vcpu_limit} ({percentage}% used)
- Memory Usage: {memory_used} GB/{memory_limit} GB
- Premium SSD: {ssd_used} GB/{ssd_limit} GB

## Container Instances:
- Current Instances: {instances}/{limit}
- CPU Allocation: {cpu_allocated}/{cpu_limit}
- Memory Allocation: {memory_allocated} GB/{memory_limit} GB

🌐 Networking:

## Virtual Networks:
- VNets per Region: {vnets}/{limit}
- Subnets per VNet: {avg_subnets}/{limit}
- Private Endpoints: {endpoints}/{limit}

## Load Balancers:
- Standard Load Balancers: {lb_count}/{limit}
- Application Gateways: {appgw_count}/{limit}

⚠️ Quota Warnings ({warning_count}):
{list_of_services_approaching_limits}

🚨 Critical Alerts ({critical_count}):
{list_of_services_at_or_over_limits}

📈 Capacity Projections:

## Based on Current Growth:
- 30-day projection: {thirty_day_projection}
- 90-day projection: {ninety_day_projection}
- Estimated time to quota limit: {time_to_limit}

## Recommended Actions:
1. {recommendation_1}
2. {recommendation_2}
3. {recommendation_3}

💡 Optimization Opportunities:
- Unused Resources: ${monthly_savings} potential savings
- Right-sizing: {rightsizing_recommendations}
- Reserved Capacity: {reservation_recommendations}

🔔 Monitoring Setup:
- Quota Alert Thresholds: 80%, 90%, 95%
- Automated Scaling: {autoscaling_status}
- Budget Alerts: Configured for quota increases

📋 Quota Increase Requests:
{list_of_recommended_quota_increases}

📊 Summary Dashboard:
- Overall Quota Health: {health_score}/100
- Services at Risk: {at_risk_count}
- Growth Sustainability: {sustainability_months} months
- Cost Impact: ${estimated_monthly_cost}
```

## Service Options
- `all`: Check all service quotas (default)
- `openai`: Azure OpenAI quotas only
- `compute`: Compute resource quotas
- `storage`: Storage service quotas
- `networking`: Network resource quotas

## Region Options
- `current`: Current deployment regions only (default)
- `all`: All available regions

## Quota Categories
- **Azure OpenAI**: TPM, RPM, model deployments, daily limits
- **Compute**: vCPUs, memory, storage, VM instances
- **Storage**: Storage accounts, capacity, IOPS, bandwidth
- **Networking**: VNets, subnets, load balancers, private endpoints
- **Database**: SQL databases, Cosmos DB RUs, connections
- **Security**: Key Vault operations, certificates, secrets

## MCP Servers Used
- **Azure Resource Graph MCP**: Resource usage queries and quota analysis
- **Azure-mcp MCP**: Service-specific quota information
- **Microsoft Docs MCP**: Quota documentation and best practices
- **Analysis Tool**: Capacity planning calculations and projections
