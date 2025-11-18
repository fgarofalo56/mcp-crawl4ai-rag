# Azure Cost Estimate Command

Estimate costs for current architecture and provide optimization recommendations.

## Usage
```
/azure-cost-estimate [--timeframe=monthly|yearly] [--include-projections] [--optimize]
```

## Description
Analyzes current Azure resource usage and provides detailed cost estimates, projections, and optimization recommendations.

## Implementation
1. **Resource Inventory**: Catalog all Azure resources and their configurations
2. **Usage Analysis**: Analyze current usage patterns and trends
3. **Cost Calculation**: Calculate costs based on current usage and pricing
4. **Projection Modeling**: Project future costs based on growth trends
5. **Optimization Analysis**: Identify cost optimization opportunities
6. **Recommendations**: Provide actionable cost reduction strategies

## Output Format
```
💰 Azure Cost Analysis & Optimization
=====================================

📊 Current Cost Breakdown:

## Monthly Costs (Current):
- Azure OpenAI: ${openai_cost} ({percentage}% of total)
- Compute Resources: ${compute_cost} ({percentage}% of total)
- Storage: ${storage_cost} ({percentage}% of total)
- Networking: ${networking_cost} ({percentage}% of total)
- Monitoring: ${monitoring_cost} ({percentage}% of total)
- **Total Monthly**: ${total_monthly}

## Annual Projection:
- Current Annual Rate: ${annual_current}
- With Growth Projections: ${annual_projected}
- Potential Savings: ${annual_savings}

⚡ Azure OpenAI Costs:

## Token Usage Costs:
- GPT-4o Input: {input_tokens:,} tokens × ${input_rate} = ${input_cost}
- GPT-4o Output: {output_tokens:,} tokens × ${output_rate} = ${output_cost}
- Embeddings: {embedding_tokens:,} tokens × ${embedding_rate} = ${embedding_cost}

## Model Hosting:
- Provisioned Throughput: {ptu_units} PTUs × ${ptu_rate} = ${ptu_cost}
- Standard Deployment: ${standard_deployment_cost}

💾 Storage & Compute Costs:

## Storage Breakdown:
- Hot Blob Storage: {hot_gb} GB × ${hot_rate} = ${hot_cost}
- Cool Blob Storage: {cool_gb} GB × ${cool_rate} = ${cool_cost}
- Transactions: {transactions:,} × ${transaction_rate} = ${transaction_cost}

## Compute Resources:
- App Service Plans: ${app_service_cost}
- Container Instances: ${container_cost}
- Function Apps: ${function_cost}

🌐 Networking & Security:

## Networking Costs:
- Data Transfer: {transfer_gb} GB × ${transfer_rate} = ${transfer_cost}
- Private Endpoints: {endpoint_count} × ${endpoint_rate} = ${endpoint_cost}
- Load Balancers: ${lb_cost}

## Security Services:
- Key Vault Operations: {kv_operations:,} × ${kv_rate} = ${kv_cost}
- Monitoring & Logs: ${monitoring_cost}

📈 Cost Projections:

## Growth-Based Projections:
- 30-day projection: ${thirty_day_cost}
- 90-day projection: ${ninety_day_cost}
- 12-month projection: ${twelve_month_cost}

## Usage Growth Assumptions:
- Token usage growth: {token_growth}% per month
- Storage growth: {storage_growth}% per month
- User growth: {user_growth}% per month

💡 Cost Optimization Opportunities:

## Immediate Savings (${immediate_savings}/month):
1. **Reserved Instances**: Save ${reserved_savings}/month
   - App Service Reserved Plans: ${app_service_savings}
   - Storage Reserved Capacity: ${storage_savings}

2. **Right-sizing**: Save ${rightsizing_savings}/month
   - Oversized compute instances: {oversized_count}
   - Underutilized resources: {underutilized_count}

3. **Storage Optimization**: Save ${storage_opt_savings}/month
   - Move to cool storage: {cool_candidates} GB
   - Archive old data: {archive_candidates} GB
   - Compress blob data: {compression_savings}%

## Medium-term Optimizations (${medium_term_savings}/month):
1. **Azure OpenAI Optimization**: Save ${openai_opt_savings}/month
   - Switch to PTU for high usage: ${ptu_savings}
   - Optimize prompt efficiency: ${prompt_opt_savings}
   - Implement caching: ${caching_savings}

2. **Networking Optimization**: Save ${network_opt_savings}/month
   - Reduce data transfer: ${transfer_savings}
   - Optimize endpoint usage: ${endpoint_savings}

🎯 Optimization Recommendations:

## Priority 1 (High Impact, Low Effort):
- {high_impact_recommendation_1}
- {high_impact_recommendation_2}
- {high_impact_recommendation_3}

## Priority 2 (Medium Impact, Medium Effort):
- {medium_impact_recommendation_1}
- {medium_impact_recommendation_2}

## Priority 3 (Long-term Strategic):
- {strategic_recommendation_1}
- {strategic_recommendation_2}

📊 Cost Optimization Summary:
- Current Monthly Cost: ${current_cost}
- Optimized Monthly Cost: ${optimized_cost}
- Monthly Savings: ${monthly_savings} ({savings_percentage}%)
- Annual Savings: ${annual_savings}
- ROI Timeline: {roi_months} months

🔔 Cost Monitoring Setup:
- Budget Alerts: ${budget_amount} monthly
- Anomaly Detection: Enabled
- Cost Allocation Tags: {tag_coverage}% coverage
- Automated Optimization: {automation_status}

🎯 Next Actions:
1. {action_1}
2. {action_2}
3. {action_3}
```

## Timeframe Options
- `monthly`: Monthly cost analysis (default)
- `yearly`: Annual cost analysis with seasonal considerations

## Parameters
- `--include-projections`: Include growth-based cost projections
- `--optimize`: Include detailed optimization recommendations

## Cost Categories Analyzed
- **Azure OpenAI**: Token usage, model hosting, PTU costs
- **Compute**: App Services, Container Instances, Function Apps
- **Storage**: Blob storage tiers, transactions, bandwidth
- **Networking**: Data transfer, private endpoints, load balancers
- **Security**: Key Vault, monitoring, audit logs
- **Database**: SQL Database, Cosmos DB, backup costs

## MCP Servers Used
- **Azure Resource Graph MCP**: Resource usage and configuration analysis
- **Azure-mcp MCP**: Cost data and pricing information
- **Microsoft Docs MCP**: Pricing documentation and optimization guides
- **Analysis Tool**: Cost calculations, projections, and optimization modeling
