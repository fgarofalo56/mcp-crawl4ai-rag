# Test Full Stack Command

Comprehensive testing across all layers with MCP validation and quality assurance.

## Usage

/test-full-stack [--type=all|unit|integration|e2e|security|performance] [--coverage-threshold=80]

## Description

Executes comprehensive testing across all application layers, validates results using MCP servers, and provides detailed quality assessment.

## Implementation

1. **Test Discovery**: Find and categorize all test suites
2. **Environment Preparation**: Setup test environments and dependencies
3. **Multi-Layer Testing**: Execute unit, integration, and e2e tests
4. **UI Testing**: Use Playwright MCP for comprehensive UI validation
5. **Security Testing**: Validate security aspects
6. **Performance Testing**: Measure performance metrics
7. **Results Validation**: Cross-validate results with MCP servers

## Output Format

🧪 Full Stack Test Results
📊 Test Execution Summary:

Total Tests: {count}
Passed: {count} ({percentage}%)
Failed: {count} ({percentage}%)
Skipped: {count} ({percentage}%)
Duration: {duration}

🔬 Test Coverage Analysis:

Overall Coverage: {percentage}%
Unit Test Coverage: {percentage}%
Integration Coverage: {percentage}%
E2E Coverage: {percentage}%
Threshold: {threshold}% ({passed/failed})

🏗️ Layer-by-Layer Results:
Unit Tests (Domain Layer):

Tests: {count}
Coverage: {percentage}%
Status: {passed/failed}
Critical Failures: {count}

Integration Tests (Infrastructure):

Tests: {count}
Coverage: {percentage}%
Status: {passed/failed}
External Dependencies: {status}

API Tests (Service Layer):

Tests: {count}
Coverage: {percentage}%
Status: {passed/failed}
Endpoint Coverage: {percentage}%

E2E Tests (Presentation Layer):

Tests: {count}
Coverage: {percentage}%
Status: {passed/failed}
User Journey Coverage: {percentage}%

🔒 Security Test Results:

Vulnerability Scans: {status}
Authentication Tests: {status}
Authorization Tests: {status}
Input Validation: {status}

⚡ Performance Test Results:

Load Test: {status}
Stress Test: {status}
Response Time: {average}ms
Throughput: {requests_per_second}

🌐 UI Test Results (Playwright):

Cross-browser Tests: {status}
Responsive Design: {status}
Accessibility: {status}
Visual Regression: {status}

❌ Failed Tests Analysis:
{detailed_failure_analysis}
💡 Recommendations:
{improvement_recommendations}
📈 Quality Gates:

Code Coverage: {passed/failed}
Performance Benchmarks: {passed/failed}
Security Scan: {passed/failed}
All Tests Passing: {passed/failed}

🎯 Next Actions:
{prioritized_action_items}

## Test Types

- `--type=all`: Full comprehensive testing (default)
- `--type=unit`: Unit tests only
- `--type=integration`: Integration tests only
- `--type=e2e`: End-to-end tests only
- `--type=security`: Security-focused tests
- `--type=performance`: Performance tests only

## MCP Servers Used

- **Playwright MCP**: UI testing, cross-browser validation
- **Analysis Tool**: Test metrics calculation and coverage analysis
- **Serena MCP**: Code coverage analysis
- **Azure-mcp MCP**: Azure service integration testing
- **AI-Server-Sequential-thinking**: Test failure analysis
