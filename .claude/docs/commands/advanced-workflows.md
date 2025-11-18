# 🚀 Advanced Workflows Commands

> **Complex multi-agent workflow commands for rapid development**

Advanced workflow commands orchestrate multiple specialized agents for complex tasks, rapid prototyping, and comprehensive analysis.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Command Reference](#-command-reference)
  - [/hackathon-prp](#hackathon-prp---rapid-prototyping)
  - [/parallel-prp-creation](#parallel-prp-creation---multiple-prp-variations)
  - [/research-validate-implement](#research-validate-implement---full-development-cycle)
  - [/onboarding-generate](#onboarding-generate---generate-onboarding-docs)
  - [/architecture-review](#architecture-review---architecture-analysis)
- [Understanding Multi-Agent Workflows](#-understanding-multi-agent-workflows)
- [Resource Management](#-resource-management)
- [Best Practices](#-best-practices)

---

## 🎯 Overview

Advanced workflows combine multiple specialized agents running in parallel to accomplish complex tasks quickly. These commands are designed for:

- **Rapid Prototyping** - Build production-ready prototypes in 30-60 minutes
- **Comprehensive Research** - Multiple concurrent research agents
- **Complex Analysis** - Architecture, security, and performance review
- **Documentation Generation** - Complete documentation suites
- **Parallel Exploration** - Explore multiple approaches simultaneously

### Key Characteristics

- ⚡ **High Concurrency** - 15-25 parallel agents
- 🎯 **Specialized Agents** - Each agent has specific expertise
- 🔄 **Coordinated Execution** - Agents share findings and coordinate
- 📊 **Comprehensive Output** - Detailed reports and deliverables
- ⏱️ **Time-Intensive** - 30-60 minute execution times

---

## 📋 Command Reference

### /hackathon-prp - Rapid Prototyping

**Purpose**: Deploys 25 parallel agents for rapid prototype implementation with production-ready code.

**Category**: Advanced Workflows (Experimental)

**Execution Time**: 30-60 minutes

**Resources**: VERY HIGH (25 parallel agents)

**Cost**: High (significant API usage)

#### What It Does

1. **Planning Phase** (5 agents, 5 minutes)
   - Requirements analysis
   - Technical feasibility
   - Architecture design
   - Resource planning
   - Risk assessment

2. **Research Phase** (8 agents, 10 minutes)
   - Technology research
   - Best practices
   - Security patterns
   - Performance optimization
   - Integration patterns

3. **Implementation Phase** (8 agents, 30 minutes)
   - Frontend development
   - Backend development
   - Database schema
   - API design
   - Infrastructure code

4. **Quality Phase** (4 agents, 10 minutes)
   - Test generation
   - Security review
   - Performance testing
   - Documentation

#### Usage Examples

```bash
# Basic usage
/hackathon-prp "Build a real-time chat application with WebSocket support"

# With specific requirements
/hackathon-prp "Create a multi-tenant SaaS application with:
- User authentication (OAuth2)
- Subscription management
- Usage tracking
- Admin dashboard
- RESTful API"

# With technology stack
/hackathon-prp "Build inventory management system" --stack "FastAPI,PostgreSQL,React"
```

#### Expected Output

```
🚀 Hackathon PRP: Real-time Chat Application

⚙️ Launching 25 Agents...

📋 Planning Phase (5 agents):
  ✅ Agent 1: Requirements Analysis
  ✅ Agent 2: Technical Feasibility
  ✅ Agent 3: Architecture Design
  ✅ Agent 4: Resource Planning
  ✅ Agent 5: Risk Assessment

🔍 Research Phase (8 agents):
  ✅ Agent 6: WebSocket Patterns
  ✅ Agent 7: Authentication Best Practices
  ✅ Agent 8: Message Queuing
  ✅ Agent 9: Database Design
  ✅ Agent 10: Frontend Architecture
  ✅ Agent 11: Security Patterns
  ✅ Agent 12: Performance Optimization
  ✅ Agent 13: Deployment Strategies

💻 Implementation Phase (8 agents):
  ✅ Agent 14: WebSocket Server (FastAPI)
  ✅ Agent 15: Message Storage (PostgreSQL)
  ✅ Agent 16: Authentication Service
  ✅ Agent 17: Frontend Components (React)
  ✅ Agent 18: Real-time State Management
  ✅ Agent 19: API Gateway
  ✅ Agent 20: Infrastructure (Bicep)
  ✅ Agent 21: Docker Configuration

✅ Quality Phase (4 agents):
  ✅ Agent 22: Test Suite Generation
  ✅ Agent 23: Security Review
  ✅ Agent 24: Performance Testing
  ✅ Agent 25: Documentation

⏱️ Total Time: 47 minutes

📦 Deliverables:
  ✅ Complete codebase (2,847 lines)
  ✅ Test suite (95% coverage)
  ✅ Infrastructure code (Bicep)
  ✅ Documentation (README, API docs)
  ✅ Deployment guide
  ✅ Security review report

🎯 Success Criteria Met: 23/25 (92%)

⚠️ Known Limitations:
  - Horizontal scaling needs manual configuration
  - Rate limiting implementation basic

💡 Next Steps:
  1. Review generated code
  2. Run test suite: /test-run
  3. Deploy to dev: /azure-deploy dev
  4. Review security report
```

#### Best Practices

✅ **DO**:
- Provide clear, detailed requirements
- Specify technology preferences
- Review all generated code
- Run tests before deployment
- Review security findings

❌ **DON'T**:
- Use for production without review
- Skip security review
- Ignore known limitations
- Deploy without testing
- Expect perfection (iterate!)

---

### /parallel-prp-creation - Multiple PRP Variations

**Purpose**: Creates 2-5 parallel PRP variations focusing on different aspects.

**Execution Time**: 15-30 minutes

**Resources**: HIGH (2-5 parallel agent groups)

#### What It Does

Creates multiple Product Requirement Prompts (PRPs) in parallel, each optimized for different priorities:

1. **Performance-Optimized PRP**
   - Focus on speed and scalability
   - Caching strategies
   - Async operations
   - Database optimization

2. **Security-Focused PRP**
   - Security-first design
   - Authentication/authorization
   - Data encryption
   - Audit logging

3. **Maintainability PRP**
   - Clean code practices
   - Extensive documentation
   - Test coverage
   - Modular design

4. **Feature-Rich PRP** (optional)
   - Maximum functionality
   - Advanced features
   - Integration capabilities

5. **Minimal MVP PRP** (optional)
   - Fastest time to market
   - Core features only
   - Simplest implementation

#### Usage Examples

```bash
# Create 3 PRP variations (default)
/parallel-prp-creation "User authentication system"

# Create 5 variations
/parallel-prp-creation "E-commerce platform" --count 5

# Specific focus areas
/parallel-prp-creation "API Gateway" --focus "performance,security,scalability"
```

---

### /research-validate-implement - Full Development Cycle

**Purpose**: Complete development cycle from research through implementation with validation.

**Execution Time**: 15-30 minutes

**Resources**: HIGH (sequential multi-agent)

#### What It Does

1. **Research Phase** (5 minutes)
   - Background research
   - Best practices
   - Existing patterns
   - Technology selection

2. **Planning Phase** (5 minutes)
   - Architecture design
   - Implementation plan
   - Test strategy
   - Risk assessment

3. **Implementation Phase** (15 minutes)
   - Code generation
   - Configuration
   - Infrastructure
   - Integration

4. **Validation Phase** (5 minutes)
   - Test execution
   - Security scan
   - Performance check
   - Quality gates

#### Usage Examples

```bash
# Complete cycle
/research-validate-implement "Add OAuth2 authentication"

# With specific requirements
/research-validate-implement "Implement caching layer" --requirements "Redis, 99.9% uptime, <10ms latency"
```

---

### /onboarding-generate - Generate Onboarding Docs

**Purpose**: Generates comprehensive onboarding documentation.

**Execution Time**: 5-10 minutes

**Resources**: MEDIUM (documentation agents)

#### What It Does

Generates complete onboarding package:

1. **ONBOARDING.md**
   - Project overview
   - Getting started
   - Development workflow
   - Common tasks

2. **QUICKSTART.md**
   - 5-minute setup guide
   - Prerequisites
   - Step-by-step instructions
   - Verification steps

3. **CONTRIBUTING.md**
   - Contribution guidelines
   - Code standards
   - PR process
   - Testing requirements

4. **README Enhancements**
   - Architecture overview
   - Setup instructions
   - Usage examples

#### Usage Examples

```bash
# Generate all onboarding docs
/onboarding-generate

# Focus on specific docs
/onboarding-generate --docs "onboarding,quickstart"

# For specific audience
/onboarding-generate --audience "junior developers"
```

---

### /architecture-review - Architecture Analysis

**Purpose**: Comprehensive architecture review and analysis.

**Execution Time**: 10-20 minutes

**Resources**: HIGH (multiple review agents)

#### What It Does

1. **Structure Analysis**
   - Directory organization
   - Module dependencies
   - Layer separation
   - Code organization

2. **Pattern Detection**
   - Design patterns
   - Anti-patterns
   - Architectural patterns
   - Best practices

3. **Quality Assessment**
   - SOLID principles
   - Coupling/cohesion
   - Testability
   - Maintainability

4. **Recommendations**
   - Improvement areas
   - Refactoring suggestions
   - Technical debt items
   - Architecture evolution

#### Usage Examples

```bash
# Full architecture review
/architecture-review

# Focus on specific area
/architecture-review --focus api

# With specific concerns
/architecture-review --concerns "scalability,security"
```

---

## 🎯 Understanding Multi-Agent Workflows

### How Parallel Agents Work

```
Main Command
    ├─→ Agent Group 1 (Planning)
    │   ├─→ Agent 1: Requirements
    │   ├─→ Agent 2: Technical
    │   └─→ Agent 3: Architecture
    │
    ├─→ Agent Group 2 (Research) [Parallel]
    │   ├─→ Agent 4: Docs
    │   ├─→ Agent 5: Patterns
    │   └─→ Agent 6: Best Practices
    │
    └─→ Agent Group 3 (Implementation) [Parallel]
        ├─→ Agent 7: Frontend
        ├─→ Agent 8: Backend
        └─→ Agent 9: Infra

Results Synthesis → Final Output
```

### Agent Coordination

- **Shared Context** - Agents share findings
- **Sequential Phases** - Phases run in order
- **Parallel Within Phase** - Agents within phase run concurrently
- **Result Aggregation** - Results synthesized at end

---

## 💰 Resource Management

### Cost Considerations

| Command | Agents | Time | Relative Cost |
|---------|--------|------|---------------|
| `/hackathon-prp` | 25 | 30-60 min | Very High ($$$$) |
| `/parallel-prp-creation` | 2-5 groups | 15-30 min | High ($$$) |
| `/research-validate-implement` | 8-12 | 15-30 min | High ($$$) |
| `/onboarding-generate` | 3-5 | 5-10 min | Medium ($$) |
| `/architecture-review` | 5-8 | 10-20 min | Medium ($$) |

### When to Use Advanced Commands

✅ **Good Use Cases**:
- Hackathons or rapid prototyping needs
- Exploring multiple approaches
- Comprehensive analysis required
- Documentation generation
- Learning new technologies

❌ **Not Recommended**:
- Simple, straightforward tasks
- Well-defined single tasks
- Production code (without review)
- Frequent daily use
- Cost-sensitive projects

---

## 💡 Best Practices

### Before Running Advanced Commands

1. **Clear Requirements**
   - Write detailed requirements
   - Specify constraints
   - Define success criteria

2. **Resource Planning**
   - Ensure sufficient API quota
   - Plan for execution time
   - Have review time allocated

3. **Environment Preparation**
   - Clean working directory
   - Latest code pulled
   - Tests passing

### During Execution

1. **Monitor Progress**
   - Watch agent outputs
   - Note any warnings
   - Track completion

2. **Be Available**
   - May need to answer questions
   - Review intermediate outputs
   - Make decisions

### After Completion

1. **Thorough Review**
   - Review all generated code
   - Run all tests
   - Check security findings
   - Validate implementation

2. **Iterate**
   - Refine as needed
   - Fix issues found
   - Add to knowledge base

3. **Document**
   - Capture learnings
   - Update project docs
   - Share with team

---

**Navigate**: [← Git Operations](./git-operations.md) | [Commands Home](./README.md) | [Creating Custom Commands →](./creating-custom-commands.md)

---

*Move fast and build things*
