# ☁️ Azure Development Commands

> **Azure-specific development and deployment workflows**

Azure development commands streamline cloud development workflows, from infrastructure provisioning to deployment and monitoring.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/azure-init](#azure-init---initialize-azure-resources)
  - [/azure-deploy](#azure-deploy---deploy-to-azure)
  - [/azure-status](#azure-status---check-deployment-status)
  - [/bicep-validate](#bicep-validate---validate-bicep-templates)
  - [/azure-logs](#azure-logs---view-azure-logs)
  - [/azure-cost](#azure-cost---check-azure-costs)
- [Prerequisites](#-prerequisites)
- [Workflow Patterns](#-workflow-patterns)
- [Best Practices](#-best-practices)

---

## 🎯 Overview

Azure commands integrate with:
- **Azure CLI** - Infrastructure management
- **Bicep** - Infrastructure as Code
- **Azure MCP** - Cloud resource interaction
- **Container Apps** - Application deployment
- **Azure Monitor** - Logging and diagnostics

### Supported Azure Services

- ✅ Azure Container Apps
- ✅ Azure Container Registry
- ✅ Azure PostgreSQL Flexible Server
- ✅ Azure Redis Cache
- ✅ Azure Key Vault
- ✅ Azure Monitor
- ✅ Azure Virtual Networks

---

## 📋 Command Reference

### /azure-init - Initialize Azure Resources

**Purpose**: Initializes Azure infrastructure using Bicep templates.

**Execution Time**: 5-15 minutes

**Resources**: High (Azure deployment)

#### What It Does

1. **Validates Prerequisites**
   - Azure CLI installed
   - Logged in to Azure
   - Subscription selected
   - Required permissions

2. **Creates Resource Group**
   - Names based on environment
   - Tags with metadata
   - Sets location

3. **Deploys Infrastructure**
   - Runs Bicep deployment
   - Creates all resources
   - Configures networking
   - Sets up security

4. **Outputs Connection Info**
   - Connection strings
   - Endpoints
   - Resource IDs
   - Next steps

#### Usage Examples

```bash
# Initialize dev environment
/azure-init dev

# Initialize production
/azure-init production --location eastus2

# Initialize with specific subscription
/azure-init staging --subscription "My Subscription"
```

#### Expected Output

```
☁️ Azure Initialization: development

✅ Prerequisites:
  ✅ Azure CLI v2.54.0
  ✅ Logged in as user@example.com
  ✅ Subscription: My Dev Subscription
  ✅ Bicep v0.24.24

🏗️ Creating Infrastructure:
  ✅ Resource Group: rg-myapp-dev-eastus2
  ⏳ Container Registry: crmyappdev
  ⏳ PostgreSQL Server: psql-myapp-dev
  ⏳ Redis Cache: redis-myapp-dev
  ⏳ Container App Environment: cae-myapp-dev

⏱️ Estimated time: 10-12 minutes

[After completion]

✅ Deployment Complete!

📋 Resources Created:
  - Resource Group: rg-myapp-dev-eastus2
  - Container Registry: crmyappdev.azurecr.io
  - PostgreSQL: psql-myapp-dev.postgres.database.azure.com
  - Redis: redis-myapp-dev.redis.cache.windows.net
  - Container Env: cae-myapp-dev

🔑 Connection Info:
  Saved to: .env.development

🚀 Next Steps:
  1. Run: /azure-deploy dev
  2. Check status: /azure-status dev
```

---

### /azure-deploy - Deploy to Azure

**Purpose**: Deploys application to Azure Container Apps.

**Execution Time**: 3-8 minutes

**Resources**: High

#### Usage Examples

```bash
# Deploy to development
/azure-deploy dev

# Deploy to production with approval
/azure-deploy production

# Deploy specific version
/azure-deploy staging --version v1.2.3

# Deploy with specific image
/azure-deploy dev --image myapp:feature-xyz
```

---

### /azure-status - Check Deployment Status

**Purpose**: Checks status of Azure resources and deployments.

**Execution Time**: 5-15 seconds

**Resources**: Low

#### Usage Examples

```bash
# Check all resources
/azure-status

# Check specific environment
/azure-status production

# Detailed health check
/azure-status dev --detailed
```

#### Expected Output

```
☁️ Azure Status: development

📊 Resource Health:
  ✅ Container App: myapp-dev (Running)
     - Replicas: 2/2 healthy
     - CPU: 45% average
     - Memory: 512 MB / 1 GB
     - Requests: 1,234 (last hour)

  ✅ PostgreSQL: psql-myapp-dev (Available)
     - Status: Ready
     - Storage: 15% used
     - Connections: 12/100

  ✅ Redis: redis-myapp-dev (Healthy)
     - Status: Running
     - Memory: 128 MB / 1 GB
     - Connections: 8

🌐 Endpoints:
  - App: https://myapp-dev.eastus2.azurecontainerapps.io
  - Health: https://myapp-dev.../health (200 OK)

📅 Last Deployment:
  - Time: 2 hours ago
  - Version: v1.2.0
  - Status: Successful

💰 Estimated Monthly Cost: $127.50
```

---

### /bicep-validate - Validate Bicep Templates

**Purpose**: Validates Bicep infrastructure templates.

**Execution Time**: 10-30 seconds

**Resources**: Low

#### Usage Examples

```bash
# Validate all templates
/bicep-validate

# Validate specific file
/bicep-validate infrastructure/main.bicep

# Validate with parameters
/bicep-validate infrastructure/main.bicep --params dev
```

---

### /azure-logs - View Azure Logs

**Purpose**: Retrieves and displays Azure application logs.

**Execution Time**: 5-30 seconds

**Resources**: Low

#### Usage Examples

```bash
# View recent logs
/azure-logs

# View logs for specific environment
/azure-logs production

# Filter by level
/azure-logs dev --level error

# Tail logs (live)
/azure-logs dev --tail

# Time range
/azure-logs production --since 1h
```

---

### /azure-cost - Check Azure Costs

**Purpose**: Displays Azure cost analysis.

**Execution Time**: 10-20 seconds

**Resources**: Low

#### Usage Examples

```bash
# Current month costs
/azure-cost

# Specific environment
/azure-cost production

# Forecast next month
/azure-cost --forecast

# Cost breakdown
/azure-cost --detailed
```

---

## ✅ Prerequisites

### Required Tools

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Bicep
az bicep install

# Verify versions
az --version
az bicep version
```

### Azure Configuration

```bash
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set subscription
az account set --subscription "My Subscription"

# Verify
az account show
```

### Required Permissions

- **Contributor** role on subscription or resource group
- **User Access Administrator** for role assignments
- **Network Contributor** for VNet operations

---

## 🔄 Workflow Patterns

### Initial Setup Workflow

```bash
# 1. Initialize infrastructure
/azure-init dev

# 2. Validate templates
/bicep-validate

# 3. Deploy application
/azure-deploy dev

# 4. Check status
/azure-status dev

# 5. View logs
/azure-logs dev
```

### Continuous Deployment Workflow

```bash
# 1. Run tests locally
/test-run

# 2. Deploy to staging
/azure-deploy staging

# 3. Check status
/azure-status staging

# 4. Run smoke tests
/test-smoke staging

# 5. Deploy to production (if staging OK)
/azure-deploy production
```

---

**Navigate**: [← Knowledge Management](./knowledge-management.md) | [Commands Home](./README.md) | [Development Support →](./development-support.md)

---

*Cloud-native development made simple*
