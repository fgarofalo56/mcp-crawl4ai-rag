# Security Scan Command

Security validation using multiple MCP servers and vulnerability assessment.

## Usage
```
/security-scan [--scope=code|infrastructure|all] [--severity=low|medium|high|critical] [--fix-issues]
```

## Description
Comprehensive security analysis across code, infrastructure, and configurations using multiple security validation tools.

## Implementation
1. **Code Security Analysis**: Scan code for vulnerabilities and security anti-patterns
2. **Infrastructure Security**: Validate Azure resource security configurations
3. **Authentication Review**: Check authentication and authorization implementations
4. **Data Protection**: Validate encryption and data handling practices
5. **Network Security**: Review network configurations and access controls
6. **Compliance Check**: Verify compliance with security standards

## Output Format
```
🔒 Security Scan Results
========================

📊 Scan Summary:
- Scope: {scope}
- Vulnerabilities Found: {vulnerability_count}
- Critical Issues: {critical_count}
- High Severity: {high_count}
- Medium Severity: {medium_count}
- Low Severity: {low_count}
- Scan Duration: {duration}

🚨 Critical Vulnerabilities ({critical_count}):
{list_of_critical_vulnerabilities}

⚠️ High Severity Issues ({high_count}):
{list_of_high_severity_issues}

🟡 Medium Severity Issues ({medium_count}):
{list_of_medium_severity_issues}

🔍 Code Security Analysis:

## Authentication & Authorization:
- Hard-coded Credentials: {found_count} ❌
- JWT Token Handling: {validation_status}
- Session Management: {session_security_status}
- Access Control Implementation: {access_control_status}

## Input Validation & Sanitization:
- SQL Injection Prevention: {sql_injection_status}
- XSS Protection: {xss_protection_status}
- Input Validation Coverage: {input_validation_percentage}%
- Output Encoding: {output_encoding_status}

## Data Protection:
- Sensitive Data Exposure: {exposure_risk_level}
- Encryption at Rest: {encryption_rest_status}
- Encryption in Transit: {encryption_transit_status}
- PII Handling: {pii_handling_status}

🏗️ Infrastructure Security:

## Azure Resource Security:
- Private Endpoints: {private_endpoint_coverage}% coverage
- Network Security Groups: {nsg_status}
- RBAC Configuration: {rbac_compliance}%
- Resource Access Policies: {access_policy_status}

## Key Management:
- Azure Key Vault Usage: {keyvault_usage_status}
- Certificate Management: {cert_mgmt_status}
- Secret Rotation: {secret_rotation_status}
- Access Key Security: {access_key_status}

## Network Security:
- TLS/SSL Configuration: {tls_ssl_status}
- Firewall Rules: {firewall_status}
- VNet Configuration: {vnet_security_status}
- Public IP Exposure: {public_ip_risk}

📋 Compliance Assessment:

## Security Standards:
- OWASP Top 10: {owasp_compliance}% compliant
- NIST Cybersecurity Framework: {nist_compliance}%
- ISO 27001: {iso_compliance}%
- SOC 2: {soc2_compliance}%

## Azure Security Benchmark:
- Identity and Access Management: {iam_score}/100
- Network Security: {network_score}/100
- Data Protection: {data_protection_score}/100
- Asset Management: {asset_mgmt_score}/100

🛠️ Auto-Fixable Issues ({auto_fix_count}):
{list_of_auto_fixable_issues}

💡 Remediation Recommendations:

## Immediate Actions (Critical/High):
1. {immediate_action_1}
2. {immediate_action_2}
3. {immediate_action_3}

## Short-term Improvements (Medium):
1. {short_term_1}
2. {short_term_2}

## Long-term Enhancements (Low):
1. {long_term_1}
2. {long_term_2}

📊 Security Metrics:
- Overall Security Score: {security_score}/100
- Risk Level: {risk_level}
- Improvement from Last Scan: {improvement_percentage}%
- Time to Address Critical Issues: {critical_fix_time}

🎯 Security Roadmap:
{prioritized_security_improvement_plan}

🔔 Monitoring Recommendations:
- Security Alert Setup: {alert_recommendations}
- Continuous Monitoring: {monitoring_recommendations}
- Automated Security Scanning: {automation_recommendations}
```

## Scope Options
- `--scope=code`: Application code security only
- `--scope=infrastructure`: Azure infrastructure security only
- `--scope=all`: Comprehensive security scan (default)

## Severity Filters
- `--severity=critical`: Critical vulnerabilities only
- `--severity=high`: High and critical vulnerabilities
- `--severity=medium`: Medium, high, and critical vulnerabilities
- `--severity=low`: All vulnerabilities (default)

## Security Categories
- **Authentication & Authorization**: Identity and access management
- **Input Validation**: Injection attack prevention
- **Data Protection**: Encryption and data handling
- **Network Security**: Network configurations and access controls
- **Infrastructure Security**: Azure resource security
- **Compliance**: Security standards and regulatory compliance

## MCP Servers Used
- **Serena MCP**: Code security analysis and vulnerability detection
- **Azure-mcp MCP**: Azure infrastructure security validation
- **Microsoft Docs MCP**: Security best practices and compliance standards
- **Analysis Tool**: Security metrics calculation and risk assessment
- **Crawl4ai-rag**: Security knowledge base and threat intelligence
