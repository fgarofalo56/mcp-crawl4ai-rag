# CI/CD Integration Examples

## Complete CI/CD Pipeline Integration

This guide demonstrates comprehensive CI/CD integration using the Claude Code Context Engineering system, covering GitHub Actions, Azure Pipelines, quality gates, and automated deployment strategies.

## Table of Contents

1. [GitHub Actions Integration](#github-actions)
2. [Azure Pipelines Integration](#azure-pipelines)
3. [Quality Gates](#quality-gates)
4. [Automated Validation](#automated-validation)
5. [Hook Integration](#hook-integration)
6. [Multi-Environment Deployment](#multi-environment)
7. [Complete Pipeline Configuration](#complete-pipeline)

## GitHub Actions

### Complete GitHub Actions Workflow

#### Step 1: Basic Workflow Setup

```yaml
# .github/workflows/main.yml
name: Complete CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
          - development
          - staging
          - production

env:
  NODE_VERSION: '18.x'
  PYTHON_VERSION: '3.10'
  DOTNET_VERSION: '6.0.x'

jobs:
  setup:
    name: Setup and Cache Dependencies
    runs-on: ubuntu-latest
    outputs:
      cache-key: ${{ steps.cache.outputs.cache-key }}

    steps:
      - uses: actions/checkout@v3

      - name: Generate cache key
        id: cache
        run: |
          echo "cache-key=${{ runner.os }}-${{ hashFiles('**/package-lock.json', '**/requirements.txt') }}" >> $GITHUB_OUTPUT

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ steps.cache.outputs.cache-key }}
          restore-keys: |
            ${{ runner.os }}-dependencies-

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt
```

#### Step 2: Code Quality Checks

```yaml
  code-quality:
    name: Code Quality Analysis
    needs: setup
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Restore cache
        uses: actions/cache@v3
        with:
          path: |
            ~/.npm
            ~/.cache/pip
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}

      - name: Run ESLint
        run: |
          npm run lint:js
          npm run lint:css

      - name: Run Prettier
        run: npm run format:check

      - name: Run Python linting
        run: |
          pip install flake8 black mypy
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          black --check .
          mypy .

      - name: Security scanning with Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/python
            p/javascript
            p/typescript
            p/react

      - name: License checking
        run: |
          npm install -g license-checker
          license-checker --onlyAllow 'MIT;Apache-2.0;BSD;ISC'

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

#### Step 3: Testing Pipeline

```yaml
  unit-tests:
    name: Unit Tests
    needs: code-quality
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-suite: [frontend, backend, api]

    steps:
      - uses: actions/checkout@v3

      - name: Restore cache
        uses: actions/cache@v3
        with:
          path: |
            node_modules
            .venv
          key: ${{ needs.setup.outputs.cache-key }}

      - name: Run ${{ matrix.test-suite }} tests
        run: |
          if [ "${{ matrix.test-suite }}" = "frontend" ]; then
            npm run test:unit -- --coverage
          elif [ "${{ matrix.test-suite }}" = "backend" ]; then
            pytest tests/unit --cov=src --cov-report=xml
          elif [ "${{ matrix.test-suite }}" = "api" ]; then
            npm run test:api
          fi

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: ${{ matrix.test-suite }}
          name: ${{ matrix.test-suite }}-coverage

  integration-tests:
    name: Integration Tests
    needs: unit-tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Setup test environment
        run: |
          cp .env.test .env
          npm run db:migrate
          npm run db:seed

      - name: Run integration tests
        run: |
          npm run test:integration
          pytest tests/integration

      - name: Test API endpoints
        run: |
          npm run test:e2e:api

  e2e-tests:
    name: E2E Tests
    needs: integration-tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Playwright
        run: |
          npm install -D @playwright/test
          npx playwright install --with-deps

      - name: Start application
        run: |
          npm run build
          npm run start &
          npx wait-on http://localhost:3000

      - name: Run E2E tests
        run: |
          npx playwright test --project=chromium

      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-results
          path: |
            playwright-report/
            test-results/
```

#### Step 4: Build and Package

```yaml
  build:
    name: Build Application
    needs: [unit-tests, integration-tests]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        platform: [linux, windows, darwin]
        arch: [amd64, arm64]

    steps:
      - uses: actions/checkout@v3

      - name: Setup build environment
        run: |
          npm ci
          pip install -r requirements.txt

      - name: Build for ${{ matrix.platform }}-${{ matrix.arch }}
        run: |
          npm run build:${{ matrix.platform }}:${{ matrix.arch }}

      - name: Create Docker image
        if: matrix.platform == 'linux'
        run: |
          docker build \
            --platform ${{ matrix.platform }}/${{ matrix.arch }} \
            -t ${{ github.repository }}:${{ github.sha }}-${{ matrix.platform }}-${{ matrix.arch }} \
            .

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push ${{ github.repository }}:${{ github.sha }}-${{ matrix.platform }}-${{ matrix.arch }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-${{ matrix.platform }}-${{ matrix.arch }}
          path: dist/
```

## Azure Pipelines

### Complete Azure DevOps Pipeline

#### Step 1: Multi-Stage Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
      - 'release/*'

pr:
  branches:
    include:
      - main

variables:
  - group: production-variables
  - name: buildConfiguration
    value: 'Release'
  - name: vmImageName
    value: 'ubuntu-latest'

stages:
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: BuildJob
        displayName: 'Build Application'
        pool:
          vmImage: $(vmImageName)

        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '18.x'
            displayName: 'Install Node.js'

          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.10'
            displayName: 'Use Python 3.10'

          - task: Cache@2
            inputs:
              key: 'npm | "$(Agent.OS)" | package-lock.json'
              restoreKeys: |
                npm | "$(Agent.OS)"
              path: $(Pipeline.Workspace)/.npm
            displayName: Cache npm

          - script: |
              npm ci
              npm run build
            displayName: 'Install and Build'

          - task: ArchiveFiles@2
            inputs:
              rootFolderOrFile: '$(System.DefaultWorkingDirectory)/dist'
              includeRootFolder: false
              archiveType: 'zip'
              archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
              replaceExistingArchive: true

          - publish: $(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip
            artifact: drop

      - job: TestJob
        displayName: 'Run Tests'
        dependsOn: BuildJob
        pool:
          vmImage: $(vmImageName)

        steps:
          - script: |
              npm test -- --coverage
              npm run test:integration
            displayName: 'Run Tests'

          - task: PublishTestResults@2
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/test-results.xml'
              failTaskOnFailedTests: true

          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: 'Cobertura'
              summaryFileLocation: '$(System.DefaultWorkingDirectory)/coverage/cobertura-coverage.xml'

  - stage: SecurityScan
    displayName: 'Security Scanning'
    dependsOn: Build
    jobs:
      - job: SecurityAnalysis
        displayName: 'Security Analysis'
        pool:
          vmImage: $(vmImageName)

        steps:
          - task: CredScan@3
            displayName: 'Run CredScan'

          - task: SdtReport@2
            displayName: 'Create Security Report'
            inputs:
              GdnExportAllTools: true

          - task: PublishSecurityAnalysisLogs@3
            displayName: 'Publish Security Logs'
            inputs:
              ArtifactName: 'CodeAnalysisLogs'
              ArtifactType: 'Container'

  - stage: DeployDev
    displayName: 'Deploy to Development'
    dependsOn: SecurityScan
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
    jobs:
      - deployment: DeploymentJob
        displayName: 'Deploy to Dev Environment'
        pool:
          vmImage: $(vmImageName)
        environment: 'development'
        strategy:
          runOnce:
            deploy:
              steps:
                - download: current
                  artifact: drop

                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'Dev-Subscription'
                    appName: 'app-dev'
                    package: '$(Pipeline.Workspace)/drop/*.zip'
                    deploymentMethod: 'auto'

  - stage: DeployStaging
    displayName: 'Deploy to Staging'
    dependsOn: SecurityScan
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeploymentJob
        displayName: 'Deploy to Staging'
        pool:
          vmImage: $(vmImageName)
        environment: 'staging'
        strategy:
          runOnce:
            deploy:
              steps:
                - download: current
                  artifact: drop

                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'Staging-Subscription'
                    appName: 'app-staging'
                    package: '$(Pipeline.Workspace)/drop/*.zip'
                    slotName: 'staging'

                - task: AzureCLI@2
                  inputs:
                    azureSubscription: 'Staging-Subscription'
                    scriptType: 'bash'
                    scriptLocation: 'inlineScript'
                    inlineScript: |
                      az webapp deployment slot swap \
                        --resource-group rg-staging \
                        --name app-staging \
                        --slot staging \
                        --target-slot production

  - stage: DeployProduction
    displayName: 'Deploy to Production'
    dependsOn: DeployStaging
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeploymentJob
        displayName: 'Deploy to Production'
        pool:
          vmImage: $(vmImageName)
        environment: 'production'
        strategy:
          canary:
            increments: [10, 25, 50, 100]
            deploy:
              steps:
                - download: current
                  artifact: drop

                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'Production-Subscription'
                    appName: 'app-production'
                    package: '$(Pipeline.Workspace)/drop/*.zip'
                    deploymentMethod: 'canary'
```

#### Step 2: Template-Based Pipelines

```yaml
# templates/build-template.yml
parameters:
  - name: buildConfiguration
    type: string
    default: 'Release'
  - name: platform
    type: string
    default: 'Any CPU'

steps:
  - task: DotNetCoreCLI@2
    displayName: 'Restore packages'
    inputs:
      command: 'restore'
      projects: '**/*.csproj'

  - task: DotNetCoreCLI@2
    displayName: 'Build solution'
    inputs:
      command: 'build'
      projects: '**/*.csproj'
      arguments: '--configuration ${{ parameters.buildConfiguration }}'

  - task: DotNetCoreCLI@2
    displayName: 'Run tests'
    inputs:
      command: 'test'
      projects: '**/*Tests.csproj'
      arguments: '--configuration ${{ parameters.buildConfiguration }} --collect:"XPlat Code Coverage"'

  - task: PublishCodeCoverageResults@1
    displayName: 'Publish code coverage'
    inputs:
      codeCoverageTool: 'Cobertura'
      summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'

# main-pipeline.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        steps:
          - template: templates/build-template.yml
            parameters:
              buildConfiguration: 'Release'
              platform: 'x64'
```

## Quality Gates

### Comprehensive Quality Gate Implementation

#### Step 1: Quality Gate Configuration

```yaml
# quality-gates/config.yml
quality_gates:
  code_coverage:
    threshold: 80
    enforcement: strict
    exclude_patterns:
      - '**/tests/**'
      - '**/migrations/**'
      - '**/config/**'

  security:
    critical_vulnerabilities: 0
    high_vulnerabilities: 3
    scan_tools:
      - semgrep
      - trivy
      - snyk

  performance:
    page_load_time: 2000  # ms
    api_response_time: 500  # ms
    bundle_size: 500000  # bytes

  code_quality:
    complexity_threshold: 10
    duplication_threshold: 5  # percent
    maintainability_index: 70

  tests:
    unit_test_pass_rate: 100
    integration_test_pass_rate: 95
    e2e_test_pass_rate: 90
```

#### Step 2: Quality Gate Enforcement

```python
# scripts/quality_gate_check.py
import json
import sys
import subprocess
from typing import Dict, Any

class QualityGateChecker:
    """Check quality gates for CI/CD pipeline"""

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.results = {}
        self.passed = True

    def check_code_coverage(self) -> bool:
        """Check code coverage meets threshold"""
        # Parse coverage report
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)

        total_coverage = coverage_data['total']['percentage']
        threshold = self.config['code_coverage']['threshold']

        passed = total_coverage >= threshold

        self.results['code_coverage'] = {
            'passed': passed,
            'actual': total_coverage,
            'threshold': threshold,
            'details': coverage_data['files']
        }

        return passed

    def check_security(self) -> bool:
        """Check security vulnerabilities"""
        # Run security scan
        result = subprocess.run(
            ['trivy', 'fs', '.', '--format', 'json'],
            capture_output=True,
            text=True
        )

        vulnerabilities = json.loads(result.stdout)

        critical = sum(1 for v in vulnerabilities if v['severity'] == 'CRITICAL')
        high = sum(1 for v in vulnerabilities if v['severity'] == 'HIGH')

        passed = (
            critical <= self.config['security']['critical_vulnerabilities'] and
            high <= self.config['security']['high_vulnerabilities']
        )

        self.results['security'] = {
            'passed': passed,
            'critical': critical,
            'high': high,
            'vulnerabilities': vulnerabilities
        }

        return passed

    def check_performance(self) -> bool:
        """Check performance metrics"""
        # Run performance tests
        with open('performance-results.json', 'r') as f:
            perf_data = json.load(f)

        metrics_passed = all([
            perf_data['page_load_time'] <= self.config['performance']['page_load_time'],
            perf_data['api_response_time'] <= self.config['performance']['api_response_time'],
            perf_data['bundle_size'] <= self.config['performance']['bundle_size']
        ])

        self.results['performance'] = {
            'passed': metrics_passed,
            'metrics': perf_data,
            'thresholds': self.config['performance']
        }

        return metrics_passed

    def check_code_quality(self) -> bool:
        """Check code quality metrics"""
        # Run code quality analysis
        result = subprocess.run(
            ['npm', 'run', 'analyze:quality'],
            capture_output=True,
            text=True
        )

        quality_data = json.loads(result.stdout)

        passed = all([
            quality_data['complexity'] <= self.config['code_quality']['complexity_threshold'],
            quality_data['duplication'] <= self.config['code_quality']['duplication_threshold'],
            quality_data['maintainability'] >= self.config['code_quality']['maintainability_index']
        ])

        self.results['code_quality'] = {
            'passed': passed,
            'metrics': quality_data,
            'thresholds': self.config['code_quality']
        }

        return passed

    def check_all_gates(self) -> bool:
        """Check all quality gates"""
        checks = [
            self.check_code_coverage(),
            self.check_security(),
            self.check_performance(),
            self.check_code_quality()
        ]

        self.passed = all(checks)
        return self.passed

    def generate_report(self) -> str:
        """Generate quality gate report"""
        report = []
        report.append("=" * 50)
        report.append("QUALITY GATE REPORT")
        report.append("=" * 50)

        for gate, result in self.results.items():
            status = "✓ PASSED" if result['passed'] else "✗ FAILED"
            report.append(f"\n{gate.upper()}: {status}")

            if gate == 'code_coverage':
                report.append(f"  Coverage: {result['actual']}% (threshold: {result['threshold']}%)")

            elif gate == 'security':
                report.append(f"  Critical: {result['critical']} | High: {result['high']}")

            elif gate == 'performance':
                for metric, value in result['metrics'].items():
                    threshold = result['thresholds'][metric]
                    report.append(f"  {metric}: {value} (threshold: {threshold})")

        report.append("\n" + "=" * 50)
        report.append(f"OVERALL: {'✓ PASSED' if self.passed else '✗ FAILED'}")

        return "\n".join(report)

if __name__ == "__main__":
    checker = QualityGateChecker('quality-gates/config.json')

    if checker.check_all_gates():
        print(checker.generate_report())
        sys.exit(0)
    else:
        print(checker.generate_report())
        print("\n❌ Quality gates failed. Please fix the issues above.")
        sys.exit(1)
```

## Automated Validation

### Comprehensive Validation Pipeline

#### Step 1: Pre-Commit Validation

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.42.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]

  - repo: local
    hooks:
      - id: run-tests
        name: Run unit tests
        entry: npm test
        language: system
        pass_filenames: false
        stages: [commit]

      - id: check-dependencies
        name: Check dependencies
        entry: npm audit
        language: system
        pass_filenames: false
```

#### Step 2: Validation Scripts

```bash
#!/bin/bash
# scripts/validate-deployment.sh

set -e

echo "🔍 Starting deployment validation..."

# Function to check endpoint health
check_health() {
    local url=$1
    local expected_status=${2:-200}

    echo "Checking $url..."
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status" -eq "$expected_status" ]; then
        echo "✓ $url is healthy (status: $status)"
        return 0
    else
        echo "✗ $url is unhealthy (status: $status, expected: $expected_status)"
        return 1
    fi
}

# Function to run smoke tests
run_smoke_tests() {
    echo "Running smoke tests..."

    # Test critical endpoints
    check_health "$APP_URL/health"
    check_health "$APP_URL/api/status"
    check_health "$APP_URL/login" 200

    # Test database connectivity
    echo "Testing database connection..."
    curl -s "$APP_URL/api/db-check" | grep -q "connected"

    # Test external services
    echo "Testing external service connections..."
    curl -s "$APP_URL/api/external-services" | jq -e '.all_connected == true'

    echo "✓ All smoke tests passed"
}

# Function to validate configuration
validate_configuration() {
    echo "Validating configuration..."

    # Check environment variables
    required_vars=("DATABASE_URL" "REDIS_URL" "API_KEY" "JWT_SECRET")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "✗ Missing required environment variable: $var"
            exit 1
        fi
    done

    # Validate SSL certificates
    echo "Checking SSL certificate..."
    openssl s_client -connect "$APP_HOST:443" -servername "$APP_HOST" < /dev/null 2>/dev/null | \
        openssl x509 -noout -checkend 86400

    echo "✓ Configuration validated"
}

# Function to check metrics
check_metrics() {
    echo "Checking application metrics..."

    # Query Prometheus metrics
    metrics=$(curl -s "$METRICS_URL/api/v1/query?query=up")

    # Check if app is reporting metrics
    if echo "$metrics" | jq -e '.data.result[0].value[1] == "1"' > /dev/null; then
        echo "✓ Application metrics are being collected"
    else
        echo "✗ Application metrics not available"
        return 1
    fi

    # Check error rate
    error_rate=$(curl -s "$METRICS_URL/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])")
    if [ $(echo "$error_rate" | jq '.data.result[0].value[1]') -lt 0.01 ]; then
        echo "✓ Error rate is acceptable"
    else
        echo "⚠ High error rate detected"
    fi
}

# Main validation flow
main() {
    echo "Environment: $ENVIRONMENT"
    echo "Application URL: $APP_URL"
    echo "----------------------------------------"

    validate_configuration
    run_smoke_tests
    check_metrics

    echo "----------------------------------------"
    echo "✅ Deployment validation completed successfully!"
}

# Run validation
main
```

## Hook Integration

### Git Hooks and Pipeline Hooks

#### Step 1: Pre-Push Hook

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "Running pre-push validation..."

# Run tests
npm test || {
    echo "❌ Tests failed. Push aborted."
    exit 1
}

# Check code quality
npm run lint || {
    echo "❌ Linting failed. Push aborted."
    exit 1
}

# Check for sensitive data
git secrets --scan || {
    echo "❌ Sensitive data detected. Push aborted."
    exit 1
}

# Check commit messages
commits=$(git log origin/main..HEAD --oneline)
while IFS= read -r commit; do
    if ! echo "$commit" | grep -qE '^[a-f0-9]+ (feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'; then
        echo "❌ Invalid commit message format: $commit"
        echo "Use conventional commits: type(scope): description"
        exit 1
    fi
done <<< "$commits"

echo "✅ Pre-push validation passed!"
```

#### Step 2: Webhook Integration

```python
# webhooks/pipeline_hooks.py
from flask import Flask, request, jsonify
import hmac
import hashlib
import subprocess
import json

app = Flask(__name__)

class PipelineWebhooks:
    """Handle CI/CD pipeline webhooks"""

    def __init__(self):
        self.secret = os.environ.get('WEBHOOK_SECRET')

    def verify_signature(self, payload, signature):
        """Verify webhook signature"""
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    @app.route('/webhook/github', methods=['POST'])
    def github_webhook(self):
        """Handle GitHub webhooks"""

        # Verify signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not self.verify_signature(request.data, signature):
            return jsonify({'error': 'Invalid signature'}), 401

        event = request.headers.get('X-GitHub-Event')
        payload = request.json

        if event == 'push':
            return self.handle_push(payload)
        elif event == 'pull_request':
            return self.handle_pr(payload)
        elif event == 'deployment':
            return self.handle_deployment(payload)

        return jsonify({'status': 'ignored'}), 200

    def handle_push(self, payload):
        """Handle push events"""
        branch = payload['ref'].split('/')[-1]

        if branch == 'main':
            # Trigger production deployment
            subprocess.run(['./scripts/deploy.sh', 'production'])
        elif branch == 'develop':
            # Trigger staging deployment
            subprocess.run(['./scripts/deploy.sh', 'staging'])

        return jsonify({'status': 'deployment triggered'}), 200

    def handle_pr(self, payload):
        """Handle pull request events"""
        action = payload['action']
        pr_number = payload['number']

        if action == 'opened' or action == 'synchronize':
            # Run PR validation
            result = subprocess.run(
                ['./scripts/validate-pr.sh', str(pr_number)],
                capture_output=True,
                text=True
            )

            # Post result as comment
            self.post_pr_comment(pr_number, result.stdout)

        return jsonify({'status': 'pr validated'}), 200

    def handle_deployment(self, payload):
        """Handle deployment events"""
        environment = payload['environment']
        status = payload['deployment_status']['state']

        if status == 'success':
            # Run post-deployment validation
            subprocess.run(['./scripts/validate-deployment.sh', environment])

            # Send notifications
            self.send_deployment_notification(environment, 'success')

        elif status == 'failure':
            # Trigger rollback
            subprocess.run(['./scripts/rollback.sh', environment])

            # Send alert
            self.send_deployment_notification(environment, 'failure')

        return jsonify({'status': 'deployment handled'}), 200
```

## Multi Environment

### Multi-Environment Deployment Strategy

#### Step 1: Environment Configuration

```yaml
# environments/config.yml
environments:
  development:
    url: https://dev.example.com
    branch: develop
    auto_deploy: true
    approval_required: false
    variables:
      NODE_ENV: development
      DATABASE_URL: ${DEV_DATABASE_URL}
      LOG_LEVEL: debug
    health_check:
      endpoint: /health
      timeout: 30
      retries: 5

  staging:
    url: https://staging.example.com
    branch: main
    auto_deploy: true
    approval_required: false
    variables:
      NODE_ENV: staging
      DATABASE_URL: ${STAGING_DATABASE_URL}
      LOG_LEVEL: info
    health_check:
      endpoint: /health
      timeout: 60
      retries: 10
    smoke_tests:
      - test: api_availability
      - test: database_connectivity
      - test: cache_connectivity

  production:
    url: https://example.com
    branch: main
    auto_deploy: false
    approval_required: true
    variables:
      NODE_ENV: production
      DATABASE_URL: ${PROD_DATABASE_URL}
      LOG_LEVEL: warn
    deployment_strategy: blue_green
    rollback_on_failure: true
    health_check:
      endpoint: /health
      timeout: 120
      retries: 20
    smoke_tests:
      - test: full_suite
    monitoring:
      alerts: true
      dashboard: https://monitoring.example.com
```

#### Step 2: Deployment Strategies

```python
# deployment/strategies.py
from abc import ABC, abstractmethod
import time
import requests

class DeploymentStrategy(ABC):
    """Base deployment strategy"""

    @abstractmethod
    async def deploy(self, app, version, environment):
        pass

class BlueGreenDeployment(DeploymentStrategy):
    """Blue-green deployment strategy"""

    async def deploy(self, app, version, environment):
        print(f"Starting blue-green deployment to {environment}")

        # Deploy to inactive environment
        inactive = self.get_inactive_environment(app)
        await self.deploy_to_environment(app, version, inactive)

        # Run health checks
        if not await self.health_check(inactive):
            raise Exception(f"Health check failed for {inactive}")

        # Run smoke tests
        if not await self.smoke_tests(inactive):
            raise Exception(f"Smoke tests failed for {inactive}")

        # Switch traffic
        await self.switch_traffic(app, inactive)

        # Monitor for issues
        if not await self.monitor_deployment(app, duration=300):
            print("Issues detected, rolling back...")
            await self.rollback(app)
            raise Exception("Deployment failed, rolled back")

        # Cleanup old environment
        await self.cleanup_old_environment(app)

        print(f"Blue-green deployment completed successfully")

class CanaryDeployment(DeploymentStrategy):
    """Canary deployment strategy"""

    async def deploy(self, app, version, environment):
        print(f"Starting canary deployment to {environment}")

        stages = [10, 25, 50, 100]  # Traffic percentages

        for percentage in stages:
            print(f"Routing {percentage}% traffic to new version")

            # Update traffic split
            await self.update_traffic_split(app, version, percentage)

            # Monitor metrics
            await self.monitor_metrics(app, duration=300)

            # Check error rate
            error_rate = await self.get_error_rate(app)
            if error_rate > 0.01:  # 1% threshold
                print(f"High error rate detected: {error_rate}")
                await self.rollback(app)
                raise Exception("Canary deployment failed")

            print(f"{percentage}% traffic validated successfully")

        print("Canary deployment completed successfully")

class RollingDeployment(DeploymentStrategy):
    """Rolling deployment strategy"""

    async def deploy(self, app, version, environment):
        print(f"Starting rolling deployment to {environment}")

        instances = await self.get_instances(app)
        batch_size = max(1, len(instances) // 4)  # 25% at a time

        for i in range(0, len(instances), batch_size):
            batch = instances[i:i + batch_size]

            # Deploy to batch
            for instance in batch:
                await self.deploy_to_instance(instance, version)

            # Wait for health
            await self.wait_for_health(batch)

            # Validate batch
            if not await self.validate_batch(batch):
                print("Batch validation failed, rolling back...")
                await self.rollback_batch(batch)
                raise Exception("Rolling deployment failed")

            print(f"Batch {i // batch_size + 1} deployed successfully")

        print("Rolling deployment completed successfully")
```

## Complete Pipeline

### Production-Ready CI/CD Pipeline

#### Step 1: Complete Pipeline Configuration

```yaml
# .github/workflows/production-pipeline.yml
name: Production CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [created]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ====================
  # CONTINUOUS INTEGRATION
  # ====================

  analyze:
    name: Code Analysis
    runs-on: ubuntu-latest
    permissions:
      security-events: write

    steps:
      - uses: actions/checkout@v3

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python

      - name: Autobuild
        uses: github/codeql-action/autobuild@v2

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  test:
    name: Test Suite
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-type: [unit, integration, e2e, performance]

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Setup Environment
        uses: ./.github/actions/setup-environment

      - name: Run ${{ matrix.test-type }} Tests
        run: |
          npm run test:${{ matrix.test-type }} -- --coverage

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: ${{ matrix.test-type }}

  build:
    name: Build and Push
    needs: [analyze, test]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    outputs:
      version: ${{ steps.meta.outputs.version }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ====================
  # CONTINUOUS DEPLOYMENT
  # ====================

  deploy-staging:
    name: Deploy to Staging
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/app \
            app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.build.outputs.version }} \
            --namespace=staging

      - name: Wait for Deployment
        run: |
          kubectl rollout status deployment/app --namespace=staging

      - name: Run Smoke Tests
        run: |
          npm run test:smoke -- --url=https://staging.example.com

  deploy-production:
    name: Deploy to Production
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    environment:
      name: production
      url: https://example.com

    steps:
      - uses: actions/checkout@v3

      - name: Blue-Green Deployment
        run: |
          ./scripts/blue-green-deploy.sh \
            --image=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.build.outputs.version }} \
            --environment=production

      - name: Validate Deployment
        run: |
          ./scripts/validate-deployment.sh production

      - name: Update DNS
        run: |
          ./scripts/update-dns.sh production

  rollback:
    name: Rollback if Failed
    needs: deploy-production
    runs-on: ubuntu-latest
    if: failure()

    steps:
      - name: Rollback Deployment
        run: |
          kubectl rollout undo deployment/app --namespace=production

      - name: Notify Team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment failed and was rolled back'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  # ====================
  # POST-DEPLOYMENT
  # ====================

  monitor:
    name: Post-Deployment Monitoring
    needs: deploy-production
    runs-on: ubuntu-latest
    if: success()

    steps:
      - name: Monitor Application Health
        run: |
          for i in {1..20}; do
            if curl -f https://example.com/health; then
              echo "Health check $i passed"
            else
              echo "Health check $i failed"
              exit 1
            fi
            sleep 30
          done

      - name: Check Error Rates
        run: |
          ./scripts/check-metrics.sh \
            --metric=error_rate \
            --threshold=0.01 \
            --duration=10m

      - name: Performance Validation
        run: |
          npm run test:performance -- --url=https://example.com
```

#### Step 2: Pipeline Utilities

```bash
#!/bin/bash
# scripts/pipeline-utils.sh

# Utility functions for CI/CD pipeline

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for deployment
wait_for_deployment() {
    local namespace=$1
    local deployment=$2
    local timeout=${3:-300}

    log_info "Waiting for deployment $deployment in namespace $namespace..."

    if kubectl rollout status deployment/$deployment \
        --namespace=$namespace \
        --timeout=${timeout}s; then
        log_info "Deployment $deployment is ready"
        return 0
    else
        log_error "Deployment $deployment failed or timed out"
        return 1
    fi
}

# Check service health
check_service_health() {
    local url=$1
    local retries=${2:-10}
    local delay=${3:-30}

    log_info "Checking service health at $url..."

    for i in $(seq 1 $retries); do
        if curl -f -s -o /dev/null "$url/health"; then
            log_info "Service is healthy (attempt $i/$retries)"
            return 0
        else
            log_warn "Service not ready yet (attempt $i/$retries)"
            sleep $delay
        fi
    done

    log_error "Service health check failed after $retries attempts"
    return 1
}

# Run smoke tests
run_smoke_tests() {
    local environment=$1
    local test_suite=${2:-basic}

    log_info "Running smoke tests for $environment environment..."

    case $test_suite in
        basic)
            npm run test:smoke:basic -- --env=$environment
            ;;
        full)
            npm run test:smoke:full -- --env=$environment
            ;;
        *)
            log_error "Unknown test suite: $test_suite"
            return 1
            ;;
    esac
}

# Send notification
send_notification() {
    local channel=$1
    local message=$2
    local status=${3:-info}

    case $channel in
        slack)
            curl -X POST $SLACK_WEBHOOK_URL \
                -H 'Content-Type: application/json' \
                -d "{\"text\": \"[$status] $message\"}"
            ;;
        email)
            echo "$message" | mail -s "[$status] Deployment Notification" $TEAM_EMAIL
            ;;
        *)
            log_warn "Unknown notification channel: $channel"
            ;;
    esac
}

# Export functions for use in other scripts
export -f log_info log_warn log_error
export -f wait_for_deployment check_service_health
export -f run_smoke_tests send_notification
```

## Summary

This comprehensive CI/CD integration guide demonstrates:

1. **GitHub Actions**: Complete workflow configuration
2. **Azure Pipelines**: Multi-stage pipeline setup
3. **Quality Gates**: Automated quality checks
4. **Validation**: Comprehensive validation strategies
5. **Hook Integration**: Git and webhook hooks
6. **Multi-Environment**: Environment-specific deployments
7. **Complete Pipeline**: Production-ready implementation

The CI/CD system provides:
- Automated testing and validation
- Quality gate enforcement
- Multi-environment deployments
- Rollback capabilities
- Monitoring and notifications
- Security scanning
- Performance validation

Use these examples to build robust CI/CD pipelines with the Claude Code Context Engineering system.
