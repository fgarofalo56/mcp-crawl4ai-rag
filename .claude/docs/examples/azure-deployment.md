# Azure Deployment Examples

## Complete Azure Deployment Walkthrough

This comprehensive guide demonstrates end-to-end Azure deployment using the Claude Code Context Engineering system, from initial setup through production deployment with full CI/CD integration.

## Table of Contents

1. [Prerequisites and Setup](#prerequisites-and-setup)
2. [Simple Function Deployment](#simple-function)
3. [Web Application Deployment](#web-application)
4. [Microservices Deployment](#microservices)
5. [Enterprise Deployment](#enterprise)
6. [CI/CD Integration](#cicd-integration)
7. [Monitoring and Validation](#monitoring)
8. [Complete Working Example](#complete-example)

## Prerequisites and Setup

### Required Tools

```bash
# Check Azure CLI installation
az --version
# Expected: Azure CLI 2.50.0 or higher

# Check Docker installation (for container deployments)
docker --version
# Expected: Docker 20.10.0 or higher

# Check Node.js (for Function Apps)
node --version
# Expected: Node.js 16.0.0 or higher

# Check Python (for Python functions)
python --version
# Expected: Python 3.8 or higher
```

### Azure Account Setup

```bash
# Login to Azure
az login

# Set default subscription
az account set --subscription "Your-Subscription-Name"

# Verify subscription
az account show
```

### MCP Configuration

```json
{
  "mcpServers": {
    "azure-mcp": {
      "command": "node",
      "args": ["path/to/azure-mcp/dist/index.js"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "your-subscription-id",
        "AZURE_TENANT_ID": "your-tenant-id"
      }
    }
  }
}
```

## Simple Function

### Hello World Azure Function

#### Step 1: Initialize Project

```bash
# Create function app project
/azure-init --type function --runtime python --name hello-function

# Expected output:
# ✓ Creating Azure Function project...
# ✓ Project structure created
# ✓ Requirements.txt generated
# ✓ Host.json configured
# ✓ Local.settings.json created
```

#### Step 2: Create Function

```python
# function_app.py
import azure.functions as func
import json

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="hello")
def main(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name', 'World')

    return func.HttpResponse(
        json.dumps({
            "message": f"Hello, {name}!",
            "timestamp": func.datetime.now().isoformat()
        }),
        status_code=200,
        mimetype="application/json"
    )
```

#### Step 3: Test Locally

```bash
# Start function locally
func start

# Test the function
curl http://localhost:7071/api/hello?name=Azure

# Expected response:
# {
#   "message": "Hello, Azure!",
#   "timestamp": "2024-01-15T10:30:00Z"
# }
```

#### Step 4: Deploy to Azure

```bash
# Create resources and deploy
/azure-deploy function hello-function \
  --resource-group my-functions-rg \
  --location eastus \
  --storage my-func-storage

# Expected output:
# ✓ Creating resource group...
# ✓ Creating storage account...
# ✓ Creating function app...
# ✓ Deploying function code...
# ✓ Function deployed successfully!
#
# URL: https://hello-function.azurewebsites.net/api/hello
```

## Web Application

### Full Stack Web Application Deployment

#### Step 1: Application Structure

```bash
# Initialize web application
/azure-web-init --stack python --frontend react

# Project structure:
# my-web-app/
# ├── backend/
# │   ├── app.py
# │   ├── requirements.txt
# │   └── config/
# ├── frontend/
# │   ├── src/
# │   ├── package.json
# │   └── build/
# └── azure/
#     ├── deploy.yaml
#     └── infrastructure/
```

#### Step 2: Backend API

```python
# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Azure App Configuration
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['STORAGE_CONNECTION'] = os.environ.get('STORAGE_CONNECTION')

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })

@app.route('/api/data')
def get_data():
    # Fetch from Azure SQL
    return jsonify({
        'items': fetch_from_database()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Upload to Azure Blob Storage
    file = request.files['file']
    url = upload_to_blob_storage(file)
    return jsonify({'url': url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

#### Step 3: Frontend Application

```javascript
// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [data, setData] = useState([]);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    // Check API health
    axios.get(`${API_URL}/api/health`)
      .then(res => setHealth(res.data))
      .catch(err => console.error(err));

    // Fetch data
    axios.get(`${API_URL}/api/data`)
      .then(res => setData(res.data.items))
      .catch(err => console.error(err));
  }, []);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_URL}/api/upload`, formData);
    return response.data.url;
  };

  return (
    <div className="App">
      <h1>Azure Web Application</h1>
      {health && (
        <div>Status: {health.status} | Environment: {health.environment}</div>
      )}
      <DataList items={data} />
      <FileUploader onUpload={handleUpload} />
    </div>
  );
}
```

#### Step 4: Infrastructure as Code

```yaml
# azure/deploy.yaml
name: Azure Web App Deployment

resources:
  - type: Microsoft.Web/serverfarms
    name: my-app-plan
    location: eastus
    sku:
      name: B2
      tier: Basic
    properties:
      reserved: true  # Linux

  - type: Microsoft.Web/sites
    name: my-backend-app
    location: eastus
    properties:
      serverFarmId: my-app-plan
      siteConfig:
        linuxFxVersion: PYTHON|3.9
        appSettings:
          - name: ENVIRONMENT
            value: production
          - name: DATABASE_URI
            value: "@Microsoft.KeyVault(SecretUri=...)"

  - type: Microsoft.Storage/storageAccounts
    name: myappstorage
    location: eastus
    sku:
      name: Standard_LRS
    properties:
      supportsHttpsTrafficOnly: true
      allowBlobPublicAccess: false

  - type: Microsoft.Sql/servers
    name: my-sql-server
    location: eastus
    properties:
      administratorLogin: admin
      administratorLoginPassword: "@Microsoft.KeyVault(SecretUri=...)"
```

#### Step 5: Deploy Everything

```bash
# Deploy infrastructure
/azure-deploy infrastructure \
  --template azure/deploy.yaml \
  --resource-group my-web-app-rg

# Deploy backend
/azure-deploy webapp backend \
  --app-name my-backend-app \
  --source ./backend

# Deploy frontend to Static Web Apps
/azure-deploy static-web-app \
  --name my-frontend \
  --source ./frontend/build \
  --api-url https://my-backend-app.azurewebsites.net

# Expected output:
# ✓ Infrastructure deployed
# ✓ Backend API deployed: https://my-backend-app.azurewebsites.net
# ✓ Frontend deployed: https://my-frontend.azurestaticapps.net
# ✓ All services connected and running
```

## Microservices

### Kubernetes Microservices Deployment

#### Step 1: Service Architecture

```yaml
# services/architecture.yaml
services:
  - name: auth-service
    port: 3000
    replicas: 2
    image: myregistry.azurecr.io/auth:latest

  - name: api-gateway
    port: 8080
    replicas: 3
    image: myregistry.azurecr.io/gateway:latest

  - name: product-service
    port: 5000
    replicas: 2
    image: myregistry.azurecr.io/products:latest

  - name: order-service
    port: 5001
    replicas: 2
    image: myregistry.azurecr.io/orders:latest
```

#### Step 2: Create AKS Cluster

```bash
# Create AKS cluster
/azure-aks create \
  --name my-aks-cluster \
  --resource-group my-k8s-rg \
  --node-count 3 \
  --node-size Standard_DS2_v2 \
  --enable-monitoring \
  --enable-autoscaling

# Get credentials
az aks get-credentials \
  --resource-group my-k8s-rg \
  --name my-aks-cluster

# Verify cluster
kubectl get nodes

# Expected output:
# NAME                       STATUS   ROLES   AGE   VERSION
# aks-nodepool1-12345678-0   Ready    agent   5m    v1.27.1
# aks-nodepool1-12345678-1   Ready    agent   5m    v1.27.1
# aks-nodepool1-12345678-2   Ready    agent   5m    v1.27.1
```

#### Step 3: Deploy Services

```bash
# Deploy all microservices
/azure-k8s-deploy \
  --manifest services/k8s-manifests/ \
  --namespace production

# Apply ingress controller
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
spec:
  rules:
  - host: api.myapp.com
    http:
      paths:
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: auth-service
            port:
              number: 3000
      - path: /products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 5000
EOF

# Verify deployment
kubectl get pods -n production
kubectl get services -n production
kubectl get ingress -n production
```

#### Step 4: Setup Service Mesh

```bash
# Install Istio for service mesh
/azure-service-mesh install istio \
  --namespace istio-system

# Enable sidecar injection
kubectl label namespace production istio-injection=enabled

# Apply traffic management
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-service
spec:
  http:
  - match:
    - headers:
        version:
          exact: v2
    route:
    - destination:
        host: product-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: product-service
        subset: v1
      weight: 90
    - destination:
        host: product-service
        subset: v2
      weight: 10
EOF
```

## Enterprise

### Enterprise-Grade Deployment with High Availability

#### Step 1: Multi-Region Setup

```bash
# Deploy to multiple regions
/azure-enterprise-deploy \
  --regions eastus,westus,westeurope \
  --resource-group enterprise-app-rg \
  --high-availability true \
  --disaster-recovery true

# Infrastructure created:
# ✓ 3 App Service Plans (1 per region)
# ✓ 3 Web Apps (1 per region)
# ✓ Azure Front Door for global load balancing
# ✓ Azure SQL with geo-replication
# ✓ Azure Redis Cache for session management
# ✓ Application Insights for monitoring
# ✓ Key Vault for secrets
# ✓ Azure AD B2C for authentication
```

#### Step 2: Database Configuration

```sql
-- Setup geo-replicated database
CREATE DATABASE EnterpriseDB
  WITH
  ( SERVICE_OBJECTIVE = 'P2',
    MAXSIZE = 100 GB,
    EDITION = 'Premium' );

-- Enable automatic tuning
ALTER DATABASE EnterpriseDB
  SET AUTOMATIC_TUNING (FORCE_LAST_GOOD_PLAN = ON);

-- Create read replicas
CREATE DATABASE EnterpriseDB_ReadReplica
  AS COPY OF EnterpriseDB;
```

```bash
# Configure failover groups
az sql failover-group create \
  --resource-group enterprise-app-rg \
  --server primary-sql-server \
  --partner-server secondary-sql-server \
  --name enterprise-failover-group \
  --databases EnterpriseDB
```

#### Step 3: Security Configuration

```bash
# Enable Azure AD authentication
/azure-security configure \
  --enable-aad true \
  --enable-mfa true \
  --enable-conditional-access true

# Configure network security
az network nsg create \
  --resource-group enterprise-app-rg \
  --name enterprise-nsg

# Add security rules
az network nsg rule create \
  --resource-group enterprise-app-rg \
  --nsg-name enterprise-nsg \
  --name AllowHTTPS \
  --priority 100 \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp

# Enable DDoS protection
az network ddos-protection create \
  --resource-group enterprise-app-rg \
  --name enterprise-ddos \
  --vnets enterprise-vnet
```

#### Step 4: Monitoring and Alerting

```bash
# Setup Application Insights
/azure-monitoring setup \
  --app-insights enterprise-ai \
  --log-analytics enterprise-logs \
  --alerts true

# Configure alerts
az monitor metrics alert create \
  --name high-response-time \
  --resource-group enterprise-app-rg \
  --scopes /subscriptions/xxx/resourceGroups/xxx \
  --condition "avg ResponseTime > 2000" \
  --description "Alert when response time exceeds 2 seconds"

# Setup auto-scaling
az monitor autoscale create \
  --resource-group enterprise-app-rg \
  --name enterprise-autoscale \
  --min-count 2 \
  --max-count 10 \
  --count 3
```

## CICD Integration

### GitHub Actions Integration

#### Workflow Configuration

```yaml
# .github/workflows/azure-deploy.yml
name: Azure Deployment Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  AZURE_WEBAPP_NAME: my-app
  AZURE_RESOURCE_GROUP: production-rg
  NODE_VERSION: '18.x'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install dependencies
        run: |
          npm ci
          npm run build

      - name: Run tests
        run: |
          npm test
          npm run test:e2e

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-artifacts
          path: dist/

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: ${{ steps.deploy.outputs.webapp-url }}

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to staging slot
        id: deploy
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          slot-name: staging
          package: .

      - name: Run smoke tests
        run: |
          curl -f ${{ steps.deploy.outputs.webapp-url }}/health

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: ${{ steps.deploy.outputs.webapp-url }}

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-artifacts

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to production
        id: deploy
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          package: .

      - name: Verify deployment
        run: |
          /azure-verify-deployment \
            --app ${{ env.AZURE_WEBAPP_NAME }} \
            --tests production-tests.yaml
```

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  azureSubscription: 'Production-Subscription'
  resourceGroup: 'production-rg'
  webAppName: 'my-enterprise-app'

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '18.x'

          - script: |
              npm ci
              npm run build
              npm test
            displayName: 'Build and Test'

          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: 'dist'
              artifactName: 'drop'

  - stage: DeployStaging
    dependsOn: Build
    condition: eq(variables['Build.SourceBranch'], 'refs/heads/develop')
    jobs:
      - deployment: DeployToStaging
        environment: 'staging'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: $(azureSubscription)
                    appName: $(webAppName)
                    slotName: 'staging'
                    package: '$(Pipeline.Workspace)/drop'

  - stage: DeployProduction
    dependsOn: Build
    condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')
    jobs:
      - deployment: DeployToProduction
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: $(azureSubscription)
                    appName: $(webAppName)
                    package: '$(Pipeline.Workspace)/drop'

                - task: AzureCLI@2
                  inputs:
                    azureSubscription: $(azureSubscription)
                    scriptType: 'bash'
                    scriptLocation: 'inlineScript'
                    inlineScript: |
                      az webapp restart --name $(webAppName) --resource-group $(resourceGroup)
```

## Monitoring

### Comprehensive Monitoring Setup

#### Application Performance Monitoring

```bash
# Setup Application Insights
/azure-monitor configure \
  --type application-insights \
  --name prod-app-insights \
  --sampling-rate 100 \
  --enable-profiler true \
  --enable-snapshot-debugger true

# Configure custom metrics
az monitor app-insights metrics create \
  --app prod-app-insights \
  --resource-group production-rg \
  --metric-name "OrderProcessingTime" \
  --aggregation Average
```

#### Log Analytics Configuration

```kql
// Custom query for performance analysis
let timeRange = 24h;
requests
| where timestamp > ago(timeRange)
| summarize
    RequestCount = count(),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95),
    P99Duration = percentile(duration, 99)
    by bin(timestamp, 5m), name
| render timechart
```

#### Dashboard Creation

```json
{
  "name": "Production Dashboard",
  "widgets": [
    {
      "type": "metric",
      "title": "Response Time",
      "query": "avg(requests.duration)"
    },
    {
      "type": "chart",
      "title": "Request Rate",
      "query": "requests | summarize count() by bin(timestamp, 1m)"
    },
    {
      "type": "map",
      "title": "Geographic Distribution",
      "query": "requests | summarize count() by client_CountryOrRegion"
    }
  ]
}
```

## Complete Example

### End-to-End E-Commerce Platform Deployment

This complete example demonstrates deploying a full e-commerce platform with:
- Microservices architecture
- Multi-region deployment
- Complete CI/CD pipeline
- Monitoring and alerting
- Auto-scaling and high availability

#### Step 1: Project Initialization

```bash
# Initialize the complete project
/azure-ecommerce-init \
  --name "GlobalStore" \
  --architecture microservices \
  --regions "eastus,westeurope,southeastasia"

# Project structure created:
# GlobalStore/
# ├── services/
# │   ├── auth-service/
# │   ├── catalog-service/
# │   ├── order-service/
# │   ├── payment-service/
# │   └── shipping-service/
# ├── infrastructure/
# │   ├── terraform/
# │   ├── kubernetes/
# │   └── scripts/
# ├── .github/workflows/
# └── monitoring/
```

#### Step 2: Infrastructure Provisioning

```bash
# Run the complete infrastructure setup
/azure-infrastructure provision \
  --config infrastructure/production.yaml \
  --environment production

# Resources created:
# ✓ 3 AKS Clusters (one per region)
# ✓ Azure Cosmos DB (globally distributed)
# ✓ Azure Service Bus (for messaging)
# ✓ Azure Redis Cache (for caching)
# ✓ Azure Front Door (global load balancer)
# ✓ Azure Container Registry
# ✓ Azure Key Vault (for secrets)
# ✓ Application Gateway (with WAF)
# ✓ Log Analytics Workspace
# ✓ Application Insights
```

#### Step 3: Build and Deploy Services

```bash
# Build all microservices
for service in auth catalog order payment shipping; do
  echo "Building $service-service..."
  cd services/$service-service
  docker build -t globalstore.azurecr.io/$service:latest .
  docker push globalstore.azurecr.io/$service:latest
  cd ../..
done

# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Verify all services are running
kubectl get pods --all-namespaces
kubectl get services --all-namespaces
kubectl get ingress --all-namespaces

# Expected output:
# NAMESPACE     NAME                    READY   STATUS
# production    auth-service-xxx        2/2     Running
# production    catalog-service-xxx     2/2     Running
# production    order-service-xxx       2/2     Running
# production    payment-service-xxx     2/2     Running
# production    shipping-service-xxx    2/2     Running
```

#### Step 4: Configure Traffic Management

```bash
# Setup Azure Front Door
az network front-door create \
  --resource-group globalstore-rg \
  --name globalstore-fd \
  --backend-pools @fd-backend-pools.json \
  --routing-rules @fd-routing-rules.json

# Configure health probes
az network front-door probe create \
  --resource-group globalstore-rg \
  --front-door-name globalstore-fd \
  --name health-probe \
  --path /health \
  --interval 30
```

#### Step 5: Setup Monitoring

```bash
# Deploy monitoring stack
/azure-monitoring deploy-stack \
  --grafana true \
  --prometheus true \
  --alerts production-alerts.yaml

# Configure alerts
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group globalstore-rg \
  --condition "count failures > 100" \
  --window-size 5m \
  --severity 2

# Setup dashboards
/azure-dashboard create \
  --template monitoring/dashboards/production.json \
  --name "Production Overview"
```

#### Step 6: CI/CD Pipeline Execution

```bash
# Trigger the deployment pipeline
git add .
git commit -m "Deploy GlobalStore to production"
git push origin main

# Monitor pipeline execution
gh run watch

# Pipeline stages:
# 1. ✓ Code checkout
# 2. ✓ Build services (5 parallel jobs)
# 3. ✓ Run tests (unit, integration, e2e)
# 4. ✓ Security scanning
# 5. ✓ Push to registry
# 6. ✓ Deploy to staging
# 7. ✓ Run smoke tests
# 8. ✓ Deploy to production (blue-green)
# 9. ✓ Verify deployment
# 10. ✓ Update monitoring
```

#### Step 7: Validation

```bash
# Run comprehensive validation
/azure-validate-deployment \
  --app globalstore \
  --checks all

# Validation results:
# ✓ All services healthy
# ✓ Database connections verified
# ✓ Message bus operational
# ✓ Cache responding
# ✓ CDN configured correctly
# ✓ SSL certificates valid
# ✓ Auto-scaling configured
# ✓ Backup configured
# ✓ Monitoring active
# ✓ Alerts configured

# Performance test
/azure-load-test \
  --url https://globalstore.com \
  --users 1000 \
  --duration 10m

# Results:
# Average response time: 145ms
# P95 response time: 320ms
# P99 response time: 580ms
# Error rate: 0.01%
# Throughput: 5,000 req/s
```

#### Complete Working Commands Summary

```bash
# Full deployment sequence
/azure-ecommerce-init --name "GlobalStore"
/azure-infrastructure provision --environment production
/azure-build-services --all
/azure-deploy-services --target production
/azure-configure-networking --type front-door
/azure-monitoring deploy-stack
/azure-validate-deployment --app globalstore

# Access URLs:
# Production: https://globalstore.com
# Staging: https://staging.globalstore.com
# Monitoring: https://monitoring.globalstore.com
# API Docs: https://api.globalstore.com/docs
```

## Best Practices

### Security Best Practices

1. **Use Managed Identities**
```bash
az webapp identity assign \
  --resource-group my-rg \
  --name my-app
```

2. **Store Secrets in Key Vault**
```bash
az keyvault secret set \
  --vault-name my-vault \
  --name "DatabasePassword" \
  --value "SecurePassword123!"
```

3. **Enable HTTPS Only**
```bash
az webapp update \
  --resource-group my-rg \
  --name my-app \
  --https-only true
```

### Performance Best Practices

1. **Enable Caching**
```bash
az redis create \
  --resource-group my-rg \
  --name my-cache \
  --sku Premium \
  --vm-size P1
```

2. **Use CDN for Static Content**
```bash
az cdn profile create \
  --resource-group my-rg \
  --name my-cdn
```

3. **Configure Auto-scaling**
```bash
az monitor autoscale create \
  --resource-group my-rg \
  --name my-autoscale \
  --min-count 2 \
  --max-count 10
```

### Cost Optimization

1. **Use Reserved Instances**
2. **Implement proper tagging**
3. **Setup cost alerts**
4. **Use Azure Advisor recommendations**

## Troubleshooting Common Issues

### Deployment Failures

```bash
# Check deployment logs
az webapp log tail \
  --resource-group my-rg \
  --name my-app

# Check deployment history
az webapp deployment list \
  --resource-group my-rg \
  --name my-app
```

### Connection Issues

```bash
# Test connectivity
az webapp ssh \
  --resource-group my-rg \
  --name my-app

# Check network configuration
az network nsg rule list \
  --resource-group my-rg \
  --nsg-name my-nsg
```

### Performance Issues

```bash
# Check metrics
az monitor metrics list \
  --resource my-app \
  --metric-names "CpuPercentage,MemoryPercentage"

# Review Application Insights
az monitor app-insights query \
  --app my-insights \
  --query "requests | where duration > 1000"
```

## Summary

This comprehensive Azure deployment guide has covered:

1. **Basic Deployments**: Simple function apps and web applications
2. **Advanced Architectures**: Microservices with Kubernetes
3. **Enterprise Solutions**: Multi-region, highly available systems
4. **CI/CD Integration**: GitHub Actions and Azure DevOps
5. **Monitoring**: Complete observability stack
6. **Best Practices**: Security, performance, and cost optimization

Each example provides:
- Complete, working code
- Step-by-step commands
- Expected outputs
- Validation steps
- Troubleshooting guidance

Use these examples as templates for your own Azure deployments, modifying them to meet your specific requirements. The Claude Code Context Engineering system streamlines the entire deployment process, from initial setup through production monitoring.
