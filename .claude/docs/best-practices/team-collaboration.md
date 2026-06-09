# Team Collaboration

Best practices for using Claude Code in team environments.

## Overview

This guide covers team setup, shared configurations, knowledge sharing strategies, collaborative workflows, documentation practices, and team metrics.

## Team Setup

### Initial Team Onboarding

**Step 1: Install Claude Code**
```bash
# Each team member installs Claude Code
npm install -g @anthropic/claude-code

# Verify installation
claude --version
```

**Step 2: Clone Repository**
```bash
git clone https://github.com/your-org/your-project.git
cd your-project
```

**Step 3: Configure Shared Settings**
```bash
# Shared settings are in version control
ls .claude/settings.shared.json

# Create personal settings
cp .claude/settings.example.json .claude/settings.local.json

# Edit personal preferences
# .claude/settings.local.json extends settings.shared.json
```

**Step 4: Set Up Environment**
```bash
# Copy environment template
cp .env.example .env

# Fill in personal credentials
# Edit .env

# Install dependencies
npm install

# Run tests to verify setup
npm test
```

**Step 5: Review Team Documentation**
```bash
# Read team guidelines
cat docs/TEAM_GUIDELINES.md

# Review coding standards
cat docs/CODING_STANDARDS.md

# Check architecture docs
cat docs/ARCHITECTURE.md
```

### Shared Configuration

**settings.shared.json** (committed to git):
```json
{
  "version": "1.0",
  "teamName": "Product Engineering",
  "permissions": {
    "bash": {
      "allow": [
        "npm test",
        "npm run build",
        "npm run lint",
        "git status",
        "git diff*",
        "git log*"
      ],
      "ask": [
        "git push*",
        "npm publish",
        "npm install*"
      ],
      "deny": [
        "rm -rf node_modules",
        "git push --force*",
        "npm uninstall express"
      ]
    },
    "tools": {
      "Read": "allow",
      "Edit": "allow",
      "Write": "ask",
      "Bash": "allow"
    }
  },
  "qualityGates": {
    "testCoverageThreshold": 80,
    "codeQualityScore": 8,
    "requireTests": true,
    "requireDocs": false,
    "securityScan": true,
    "validationChecklist": [
      "All tests pass",
      "No linting errors",
      "Code reviewed",
      "Documentation updated"
    ]
  },
  "outputStyle": "concise",
  "mcpServers": {
    "microsoft-docs-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/mcp-server"],
      "enabled": true
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"],
      "enabled": true
    }
  },
  "hooks": {
    "preCommit": [
      "npm run lint",
      "npm test"
    ]
  }
}
```

**.gitignore:**
```
# Personal settings
.claude/settings.local.json
.claude/logs/
.claude/cache/

# Environment
.env

# Dependencies
node_modules/

# Build
dist/
build/
```

### Team Roles and Permissions

**Define role-based settings:**

**Junior Developer:**
```json
{
  "extends": "./settings.shared.json",
  "outputStyle": "explanatory",
  "permissions": {
    "bash": {
      "ask": ["git push*", "npm install*", "npm publish"]
    }
  }
}
```

**Senior Developer:**
```json
{
  "extends": "./settings.shared.json",
  "outputStyle": "concise",
  "permissions": {
    "bash": {
      "allow": ["git push origin feature-*"],
      "ask": ["git push origin main", "npm publish"]
    }
  }
}
```

**Tech Lead:**
```json
{
  "extends": "./settings.shared.json",
  "outputStyle": "concise",
  "permissions": {
    "bash": {
      "allow": ["git push*", "npm install*"]
    }
  },
  "qualityGates": {
    "testCoverageThreshold": 90
  }
}
```

## Shared Commands and Agents

### Custom Commands Library

**.claude/commands/team-commit.md:**
```markdown
# Team Commit

Create a commit following team standards:

1. Run all quality checks:
   - npm run lint
   - npm run type-check
   - npm test

2. Review changes:
   - git diff

3. Create commit with conventional commit format:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation
   - test: Tests
   - refactor: Code refactoring
   - style: Code style
   - chore: Maintenance

4. Include ticket number if applicable:
   - [PROJ-123] feat: Add user authentication
```

**.claude/commands/code-review.md:**
```markdown
# Code Review

Perform comprehensive code review:

1. Run quality checks:
   - npm test
   - npm run lint
   - npm run type-check

2. Review for:
   - Code quality and readability
   - Security vulnerabilities
   - Performance issues
   - Test coverage
   - Documentation completeness

3. Generate review summary with:
   - Strengths
   - Issues (critical, major, minor)
   - Suggestions
   - Overall recommendation (approve, request changes, reject)
```

**.claude/commands/new-feature.md:**
```markdown
# New Feature

Create a new feature following team architecture:

1. Create feature directory structure:
   - src/features/[feature-name]/
   - src/features/[feature-name]/components/
   - src/features/[feature-name]/hooks/
   - src/features/[feature-name]/utils/
   - src/features/[feature-name]/types/

2. Create files:
   - index.ts (public API)
   - [Feature].tsx (main component)
   - [Feature].test.tsx (tests)
   - README.md (documentation)

3. Add to main exports

4. Create tests

5. Update documentation
```

**.claude/commands/sprint-start.md:**
```markdown
# Sprint Start

Set up for new sprint:

1. Pull latest from main:
   - git checkout main
   - git pull origin main

2. Create sprint branch:
   - git checkout -b sprint-[number]-[name]

3. Review sprint goals:
   - Read docs/sprints/sprint-[number].md

4. Break down stories into tasks

5. Create task checklist

6. Set up quality gates for sprint
```

### Shared Agents

**.claude/agents/architect.md:**
```markdown
# System Architect

You are a senior software architect reviewing system design.

Focus areas:
- System architecture and design patterns
- Scalability and performance
- Security architecture
- Technology choices and trade-offs
- Integration points
- Data flow and storage

Provide:
- Architectural recommendations
- Diagrams (text-based)
- Trade-off analysis
- Implementation guidance
```

**.claude/agents/security-reviewer.md:**
```markdown
# Security Reviewer

You are a security expert reviewing code for vulnerabilities.

Focus areas:
- Authentication and authorization
- Input validation
- SQL injection prevention
- XSS prevention
- CSRF protection
- Secrets management
- API security

Provide:
- Security vulnerabilities found
- Severity ratings (critical, high, medium, low)
- Remediation steps
- Best practices
```

**.claude/agents/performance-optimizer.md:**
```markdown
# Performance Optimizer

You are a performance expert optimizing code.

Focus areas:
- Database query optimization
- Caching strategies
- API performance
- Bundle size optimization
- Memory usage
- Network requests

Provide:
- Performance issues identified
- Optimization recommendations
- Before/after comparisons
- Implementation steps
```

## Knowledge Sharing

### Documentation Practices

**Team Wiki Structure:**
```
docs/
├── architecture/
│   ├── overview.md
│   ├── diagrams/
│   ├── adr/              # Architecture Decision Records
│   └── patterns.md
├── onboarding/
│   ├── getting-started.md
│   ├── development-setup.md
│   └── team-guidelines.md
├── guides/
│   ├── coding-standards.md
│   ├── testing-guide.md
│   ├── deployment-guide.md
│   └── troubleshooting.md
├── features/
│   ├── authentication.md
│   ├── payments.md
│   └── notifications.md
└── api/
    ├── rest-api.md
    └── graphql-api.md
```

**Architecture Decision Records (ADR):**
```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status
Accepted

## Context
We need a reliable, scalable database for storing application data.

## Decision
Use PostgreSQL as our primary database.

## Rationale
- ACID compliance for data integrity
- Excellent JSON support for flexible schemas
- Strong performance characteristics
- Rich ecosystem and tooling
- Team expertise

## Consequences

### Positive
- Data consistency guaranteed
- Flexible querying with SQL and JSON
- Mature tooling and libraries
- Good performance for our use cases

### Negative
- Requires careful scaling planning
- More complex than managed NoSQL options
- Requires PostgreSQL expertise

## Alternatives Considered
- MongoDB: Easier horizontal scaling but eventual consistency
- MySQL: Similar to PostgreSQL but weaker JSON support
- DynamoDB: Managed but vendor lock-in

## Implementation Notes
- Use connection pooling
- Implement proper indexing strategy
- Set up monitoring and alerts
- Plan for read replicas as we scale

## Date
2025-10-01

## Authors
- Tech Lead
- Senior Engineer
```

### Weekly Knowledge Sharing

**Friday Demo Session:**
```markdown
# Weekly Demo - October 9, 2025

## What We Built This Week

### Feature: User Profile Management
- Presenter: Alice
- Duration: 10 min
- Demo: Live demo of profile editing
- Technical highlights:
  - Optimistic updates for better UX
  - Image upload with compression
  - Form validation with Zod

### Bug Fix: Payment Processing Race Condition
- Presenter: Bob
- Duration: 5 min
- Explanation of the issue and solution
- Learning: Always use database transactions for multi-step operations

### Tool: Custom Claude Agent for API Documentation
- Presenter: Carol
- Duration: 5 min
- Demo: Automated API doc generation
- Team can reuse this agent

## Learnings
- Form libraries comparison (React Hook Form vs Formik)
- Database transaction best practices
- Claude Code agent development tips

## Next Week
- Sprint 16 kickoff
- Focus: Notification system
```

### Code Review Sessions

**Collaborative Review Process:**
```markdown
# Code Review Guidelines

## Before Requesting Review

1. Self-review your code
2. Run all tests and quality checks
3. Update documentation
4. Create detailed PR description

## PR Template

```
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows team style guide
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance considered

## Related Issues
Closes #123

## Screenshots (if applicable)
```

## Reviewing PRs

### Automated Checks
- All tests must pass
- Linting must pass
- Coverage must meet threshold
- Security scan must pass

### Human Review
1. Code quality and readability
2. Architectural fit
3. Security considerations
4. Performance implications
5. Test adequacy
6. Documentation completeness

### Review Feedback Format

**Positive feedback:**
```
✅ Great use of the builder pattern here
```

**Suggestions:**
```
💡 Consider extracting this into a utility function for reusability
```

**Required changes:**
```
🔴 This creates a SQL injection vulnerability. Use parameterized queries.
```

**Questions:**
```
❓ Why did we choose this approach over [alternative]?
```

## Using Claude for Reviews

```bash
# Review entire PR
"Review PR #123 for:
1. Code quality
2. Security issues
3. Performance concerns
4. Test coverage
5. Documentation"

# Focus on specific aspects
"Review this authentication code for security vulnerabilities"

# Generate review summary
"Create a review summary with strengths, issues, and recommendations"
```
```

### Pair Programming

**Driver-Navigator Pattern:**
```markdown
# Pair Programming Session

## Setup (5 min)
- Share screen
- Set up task
- Agree on approach

## Development (45 min)
- Navigator: Guide direction and strategy
- Driver: Write code
- Switch every 15-20 minutes

## Review (10 min)
- Review what was built
- Discuss learnings
- Plan next steps

## Best Practices
- Keep sessions to 1-2 hours max
- Take breaks
- Both should contribute ideas
- Focus on one task at a time
- Document decisions
```

**Using Claude in Pair Programming:**
```bash
# Navigator uses Claude for research
"What's the best practice for handling file uploads?"

# Driver uses Claude for implementation
"Implement file upload with validation and virus scanning"

# Both review with Claude
"Review this upload implementation for security issues"
```

## Metrics and Reporting

### Team Metrics

**Track Key Metrics:**
```json
{
  "metrics": {
    "codeQuality": {
      "testCoverage": 85,
      "lintScore": 95,
      "codeQualityScore": 8.5,
      "securityScore": 9.2
    },
    "productivity": {
      "storiesCompleted": 12,
      "bugsFixed": 8,
      "deploymentFrequency": "daily",
      "leadTime": "2 days",
      "cycleTime": "1.5 days"
    },
    "quality": {
      "bugEscapeRate": 0.05,
      "productionIncidents": 0,
      "meanTimeToRecover": "15 min"
    }
  }
}
```

**Weekly Team Report:**
```markdown
# Weekly Team Report - Week of October 7, 2025

## Velocity
- Story points completed: 32
- Stories completed: 8
- Bugs fixed: 5

## Quality
- Test coverage: 85% (target: 80%)
- Code quality score: 8.5/10
- Security vulnerabilities: 0 critical, 1 medium (fixed)
- Production incidents: 0

## Deployments
- Deployments this week: 5
- Success rate: 100%
- Average deployment time: 12 min
- Rollbacks: 0

## Technical Debt
- Debt items added: 2
- Debt items resolved: 3
- Current debt score: 6.5/10 (improving)

## Achievements
- ✅ Completed payment processing feature
- ✅ Improved API response time by 30%
- ✅ Migrated to new authentication system

## Challenges
- Database connection pool tuning needed
- Test suite getting slow (30 min)

## Action Items
- Optimize slow tests
- Review database connection settings
- Plan technical debt sprint
```

### Individual Metrics

**Developer Dashboard:**
```markdown
# Developer Metrics - Alice

## This Sprint
- Stories completed: 3 (12 points)
- PRs created: 5
- PRs reviewed: 8
- Code quality score: 9.2/10
- Test coverage: 92%

## Code Review
- Average review time: 2 hours
- Approval rate: 95%
- Issues found: 12 (8 minor, 3 major, 1 critical)

## Contributions
- Lines of code: +1,200 / -800 (net: +400)
- Files changed: 35
- Commits: 24

## Learning
- New skills: GraphQL subscriptions, Redis caching
- Certifications: None this sprint
- Knowledge sharing: 1 demo presentation
```

### Automated Reporting

**GitHub Actions Workflow:**
```yaml
name: Weekly Team Report

on:
  schedule:
    - cron: '0 9 * * FRI'  # Every Friday at 9 AM

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate metrics
        run: |
          npm run metrics:generate

      - name: Create report
        run: |
          npm run report:weekly

      - name: Post to Slack
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: 'team-reports'
          slack-message: |
            Weekly Team Report is ready!
            View at: ${{ github.server_url }}/${{ github.repository }}/blob/main/reports/weekly-report.md
```

## Team Templates

### Feature Template

**.claude/templates/feature.md:**
```markdown
# Feature: {{feature_name}}

## Overview
Brief description of the feature

## Requirements
- User story: As a {{user}}, I want {{goal}} so that {{benefit}}
- Acceptance criteria:
  - [ ] Criterion 1
  - [ ] Criterion 2
  - [ ] Criterion 3

## Technical Design
### Architecture
- Components involved:
- Data flow:
- External dependencies:

### Database Changes
- New tables/collections:
- Schema changes:
- Migrations needed:

### API Changes
- New endpoints:
- Modified endpoints:
- Breaking changes:

## Implementation Plan
1. Step 1
2. Step 2
3. Step 3

## Testing Strategy
- Unit tests:
- Integration tests:
- E2E tests:
- Manual testing:

## Documentation
- API docs to update:
- User docs to create:
- Architecture docs to update:

## Deployment
- Feature flags needed:
- Configuration changes:
- Migration steps:
- Rollback plan:

## Timeline
- Estimated effort: X days
- Target completion: YYYY-MM-DD
```

### Bug Report Template

**.github/ISSUE_TEMPLATE/bug_report.md:**
```markdown
---
name: Bug Report
about: Report a bug
title: '[BUG] '
labels: bug
assignees: ''
---

## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Browser/Node version:
- OS:
- Environment (dev/staging/prod):

## Screenshots
If applicable

## Logs
```
Paste relevant logs here
```

## Possible Solution
If you have ideas

## Additional Context
Any other relevant information
```

## Conflict Resolution

### Merge Conflicts

**Handling Conflicts:**
```bash
# Pull latest changes
git checkout main
git pull origin main

# Rebase your branch
git checkout feature-branch
git rebase main

# If conflicts occur
git status  # See conflicted files

# Use Claude to help resolve
"Help me resolve this merge conflict in user.service.ts:
<<<<<<< HEAD
[current code]
=======
[incoming code]
>>>>>>> main"

# After resolving
git add .
git rebase --continue

# Push
git push origin feature-branch --force-with-lease
```

### Code Style Disagreements

**Team Decision Process:**
1. Discuss in team meeting
2. Present pros/cons
3. Vote if needed
4. Document decision in style guide
5. Update linting rules
6. Apply consistently

## Remote Team Collaboration

### Async Communication

**Use Claude for Documentation:**
```bash
# Document your work for the team
"Create a summary of today's work on the payment feature:
- What was implemented
- Decisions made
- Blockers encountered
- Next steps"

# Review others' work
"Read alice-daily-update.md and create questions for clarification"
```

### Time Zone Coordination

**Overlap Hours:**
```markdown
# Team Overlap Hours

## Team Members
- Alice (San Francisco): 9 AM - 5 PM PST
- Bob (New York): 12 PM - 8 PM EST
- Carol (London): 9 AM - 5 PM GMT
- Dave (Tokyo): 10 AM - 6 PM JST

## Core Hours (all online)
- 8 AM - 9 AM PST / 11 AM - 12 PM EST / 4 PM - 5 PM GMT

## Async-First Practices
- Document decisions in writing
- Use async video updates for complex topics
- Respond within 24 hours
- Schedule meetings in advance
- Record all meetings
```

## Best Practices Summary

### Team Configuration
✅ Share common settings via version control
✅ Allow personal customization
✅ Document team standards
✅ Version control custom commands/agents

### Knowledge Sharing
✅ Weekly demos and retrospectives
✅ Comprehensive documentation
✅ Architecture decision records
✅ Regular pair programming

### Code Review
✅ Automated quality checks
✅ Timely reviews (within 24 hours)
✅ Constructive feedback
✅ Use Claude to assist reviews

### Metrics
✅ Track team and individual metrics
✅ Focus on outcomes, not just output
✅ Regular retrospectives
✅ Continuous improvement

### Communication
✅ Async-first for distributed teams
✅ Clear documentation
✅ Regular sync points
✅ Transparent decision-making

## Next Steps

- [Context Management](./context-management.md) - Optimize context usage
- [Workflow Patterns](./workflow-patterns.md) - Development workflows
- [Code Quality](./code-quality.md) - Quality guidelines
- [Settings Configuration](../settings/README.md) - Configure Claude Code
