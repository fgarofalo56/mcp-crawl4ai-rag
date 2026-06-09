# Workflow Patterns

Proven development workflow patterns for maximum productivity with Claude Code.

## Overview

This guide provides battle-tested workflow patterns for common development scenarios. Each pattern includes step-by-step instructions, configuration recommendations, and real-world examples.

## Daily Development Workflow

### Morning Routine

**1. Start Fresh Session**
```bash
# Clear previous session if needed
/clear

# Check configuration
claude config show

# Set today's focus
"Today I'm working on [feature/bug/refactor]"
```

**2. Review Recent Changes**
```bash
git status
git log --since="yesterday"
git diff main...feature-branch
```

**3. Set Context**
```bash
# Load relevant documentation
"Read docs/feature-spec.md"

# Review related code
"Show me the current implementation of [feature]"
```

**4. Plan the Day**
```bash
# Create task list
"Break down today's work into specific tasks"

# Optional: Use TodoWrite for tracking
/todo
```

### Active Development

**1. Feature Implementation Pattern**
```bash
# Step 1: Understand requirement
"Explain how [feature] should work based on the spec"

# Step 2: Design approach
"What's the best way to implement this given our architecture?"

# Step 3: Implement
"Create [component/module] with [requirements]"

# Step 4: Test
"Add unit tests for [component]"

# Step 5: Integration
"Integrate [component] with existing code"

# Step 6: Verify
npm test
npm run build
```

**2. Iterative Development Loop**
```bash
# Implement feature
"Add user profile update endpoint"

# Test
npm test

# Fix issues
"Fix the validation error in updateProfile"

# Re-test
npm test

# Commit when passing
git add .
git commit -m "feat: Add user profile update endpoint"
```

**3. Context Management During Development**
```bash
# Check context every hour
/context

# Compact when reaching 75%
/compact

# Continue working
```

### End of Day

**1. Review Progress**
```bash
# Check what was accomplished
git log --since="today"
git status

# Update task list
"Mark completed tasks as done"
```

**2. Commit Work**
```bash
# Ensure everything is committed
"Review uncommitted changes and create appropriate commits"

git status
git add .
git commit -m "feat: Implement user profile features"
```

**3. Document Blockers/Notes**
```bash
# If work incomplete
"Create a summary of today's progress and any blockers for tomorrow"

# Save to file
# docs/daily-notes/2025-10-09.md
```

**4. Push Changes**
```bash
git push origin feature-branch
```

## Sprint Workflows

### Sprint Start

**Day 1: Planning & Setup**
```bash
# Start fresh
/clear

# Review sprint goals
"Read docs/sprint-planning/sprint-15.md"

# Break down stories
"Break down these user stories into technical tasks:
1. [Story 1]
2. [Story 2]
3. [Story 3]"

# Create task tracking
"Create a checklist for all sprint tasks"

# Set up quality gates
# Update .claude/settings.local.json if needed
```

**Architecture Review**
```bash
# Review system architecture
"Show current architecture diagram"

# Plan changes
"How should we modify the architecture to support [new features]?"

# Document decisions
"Document architectural decisions in docs/architecture/adr/"
```

**Initial Setup**
```bash
# Create feature branch
git checkout -b sprint-15-user-profiles

# Create directory structure
"Create directory structure for new features"

# Set up tests
"Create test file structure"
```

### Sprint Mid-Point

**Day 3-4: Review & Adjust**
```bash
# Check progress
/context

# Review completed work
git log --since="3 days ago"

# Assess remaining work
"Review sprint checklist and estimate remaining effort"

# Adjust if needed
"Identify which tasks are at risk of not completing"
```

**Quality Check**
```bash
# Run all tests
npm test -- --coverage

# Check quality gates
npm run lint
npm run type-check

# Review technical debt
"Identify any technical debt created and plan to address it"
```

### Sprint End

**Day 5: Completion & Review**
```bash
# Final testing
npm test -- --coverage
npm run build
npm run test:e2e

# Code review
"Review all changes for code quality and best practices"

# Documentation
"Update all relevant documentation"

# Create PR
/pr

# Sprint retrospective notes
"Generate sprint summary:
- Features completed
- Challenges faced
- Lessons learned
- Process improvements"
```

## Feature Development Patterns

### Small Feature (1-2 days)

**Pattern: Single-Session Development**
```bash
# Day 1: Design & Implement
/clear

# Understand requirement
"Read feature spec: docs/features/email-notifications.md"

# Design
"Design the email notification system"

# Implement
"Create EmailService class with send, queue, and retry methods"

# Test
"Add unit tests for EmailService"

# Integrate
"Integrate EmailService into UserController"

# Verify
npm test

# Commit
git add .
git commit -m "feat: Add email notification system"

# PR
/pr
```

### Medium Feature (3-5 days)

**Pattern: Multi-Session with Checkpoints**
```bash
# Day 1: Foundation
/clear
"Implementing payment processing feature"

# Create core structure
"Create Payment model, PaymentService, and PaymentController"

# Checkpoint: Commit
git commit -m "feat: Add payment processing foundation"

# Day 2: Business Logic
# Continue same session or /compact if context high
"Add payment processing logic with Stripe integration"

# Checkpoint
git commit -m "feat: Implement Stripe payment processing"

# Day 3: Error Handling & Edge Cases
"Add error handling and retry logic"
git commit -m "feat: Add payment error handling"

# Day 4: Testing
"Add comprehensive tests including edge cases"
git commit -m "test: Add payment processing tests"

# Day 5: Integration & Documentation
"Integrate with checkout flow and update docs"
git commit -m "feat: Integrate payments with checkout"
/pr
```

### Large Feature (1-2 weeks)

**Pattern: Modular Development with Subagents**
```bash
# Week 1, Day 1: Architecture
/clear
"Designing multi-tenant architecture"

# High-level design
"Create architecture document for multi-tenancy"

# Break into modules
"Break down multi-tenancy into independent modules:
1. Tenant management
2. Data isolation
3. Authentication updates
4. API changes"

# Assign modules
# Main session: Core tenant management
"Implement tenant management module"

# Subagent 1: Data isolation
/agent isolation "Design and implement data isolation layer"

# Subagent 2: Documentation
/agent docs "Create multi-tenancy documentation"

# Week 1, Days 2-5: Implement modules
# Continue modular development

# Week 2: Integration & Testing
/clear
"Integrating multi-tenancy modules"

# Integration
"Integrate all multi-tenancy components"

# Testing
"Create integration tests for multi-tenancy"

# Documentation
"Update all docs for multi-tenancy support"

# Review
"Comprehensive review of multi-tenancy implementation"

# PR
/pr
```

## Bug Fixing Workflows

### Simple Bug Fix

**Pattern: Quick Fix**
```bash
# Reproduce
"The login button doesn't work on mobile"

# Locate
"Find the login button component"

# Understand
"Show me the LoginButton implementation"

# Fix
"Fix the onClick handler to work on mobile"

# Test
npm test
npm run test:mobile

# Commit
git commit -m "fix: Login button click handler on mobile"
```

### Complex Bug Fix

**Pattern: Systematic Debugging**
```bash
# Step 1: Gather information
/clear
"Debugging: User data not saving correctly"

# Step 2: Reproduce
"Create a test that reproduces the bug"

# Step 3: Locate
"Where in the code does user data get saved?"

# Step 4: Analyze
"Show me the saveUser function and trace through the logic"

# Step 5: Identify root cause
"The issue is in the validation logic. Here's why..."

# Step 6: Fix
"Fix the validation in saveUser function"

# Step 7: Verify fix
"Run the reproduction test to verify it's fixed"

# Step 8: Prevent regression
"Add tests to prevent this bug from happening again"

# Step 9: Document
"Add comment explaining the fix"

# Commit
git commit -m "fix: User data validation causing save failures

Root cause: Validation was too strict for optional fields
Solution: Allow null/undefined for optional fields
Regression prevention: Added test for optional field handling"
```

### Production Bug (Urgent)

**Pattern: Fast Track**
```bash
# Immediate context
/clear
"URGENT: Production bug - payments failing"

# Gather error info
"Review error logs from production"

# Locate issue
"Find payment processing code"

# Hotfix
"Create minimal fix for payment processing bug"

# Test thoroughly
npm test
npm run test:payments

# Commit to hotfix branch
git checkout -b hotfix/payment-processing
git commit -m "hotfix: Fix payment processing error"

# Deploy
"Create deployment instructions"

# Follow-up
"Create ticket for proper fix and tests"
```

## Refactoring Patterns

### Small Refactoring

**Pattern: Extract and Simplify**
```bash
# Identify need
"This function is too complex"

# Plan refactoring
"How should we refactor getUserData function?"

# Execute
"Extract helper functions from getUserData"

# Verify
npm test  # All tests should still pass

# Commit
git commit -m "refactor: Extract helpers from getUserData"
```

### Large Refactoring

**Pattern: Incremental with Feature Flags**
```bash
# Week 1: Plan
/clear
"Planning refactor of authentication system"

# Analyze current state
"Analyze current authentication implementation"

# Design new approach
"Design improved authentication architecture"

# Create migration plan
"Create step-by-step migration plan"

# Week 2-3: Incremental implementation
# Day 1: Add new implementation alongside old
"Implement new authentication system with feature flag"

# Day 2-3: Migrate features one by one
"Migrate login to new auth system"
git commit -m "refactor: Migrate login to new auth system"

"Migrate logout to new auth system"
git commit -m "refactor: Migrate logout to new auth system"

# Day 4-5: Testing
"Add comprehensive tests for new auth system"

# Week 4: Complete migration
"Enable new auth system by default"
"Remove old auth system code"
git commit -m "refactor: Complete auth system migration"
```

## Testing Workflows

### Test-Driven Development (TDD)

**Pattern: Red-Green-Refactor**
```bash
# Red: Write failing test
"Write a test for the calculateDiscount function that doesn't exist yet"

npm test  # Should fail

# Green: Make it pass
"Implement calculateDiscount to make the test pass"

npm test  # Should pass

# Refactor: Improve
"Refactor calculateDiscount for better readability"

npm test  # Should still pass

# Commit
git commit -m "feat: Add calculateDiscount function (TDD)"
```

### Testing Existing Code

**Pattern: Comprehensive Coverage**
```bash
# Analyze coverage
npm test -- --coverage

# Identify gaps
"Show me which functions in UserService lack tests"

# Add tests systematically
"Add tests for getUserById function"
"Add tests for updateUser function"
"Add tests for deleteUser function"

# Verify coverage
npm test -- --coverage

# Commit
git commit -m "test: Add comprehensive UserService tests"
```

### Integration Testing

**Pattern: End-to-End Scenarios**
```bash
# Plan scenarios
"List the key user scenarios for the checkout process"

# Implement tests
"Create integration test for complete checkout flow:
1. Add to cart
2. Apply discount
3. Enter payment
4. Confirm order"

# Run tests
npm run test:integration

# Fix issues
"Fix the discount calculation issue in checkout"

# Re-run
npm run test:integration
```

## Code Review Workflows

### Self Review

**Pattern: Before Creating PR**
```bash
# Review your changes
git diff main...feature-branch

# Use Claude to review
"Review these changes for:
1. Code quality
2. Security issues
3. Performance concerns
4. Test coverage
5. Documentation"

# Address findings
"Fix the security issue in password handling"
"Add missing tests for edge cases"
"Update documentation"

# Create PR
/pr
```

### Reviewing Others' Code

**Pattern: Comprehensive Review**
```bash
# Load PR context
/clear
"Reviewing PR #123: Add user profile features"

# Fetch changes
git fetch origin
git checkout pr-123

# Understand changes
"Summarize the changes in this PR"

# Review systematically
"Review for code quality"
"Review for security"
"Review for performance"
"Check test coverage"

# Run tests
npm test
npm run build

# Provide feedback
"Generate code review feedback highlighting:
- Good practices used
- Issues to address
- Suggestions for improvement"
```

## Deployment Workflows

### Pre-Deployment

**Pattern: Deployment Checklist**
```bash
# Run full test suite
npm test -- --coverage
npm run test:integration
npm run test:e2e

# Quality checks
npm run lint
npm run type-check

# Security scan
npm audit
npm run security-scan

# Build
npm run build

# Check build size
npm run analyze-bundle

# Review changes
git log production..main

# Create deployment notes
"Generate deployment notes:
- Features being deployed
- Bug fixes
- Breaking changes
- Migration steps
- Rollback plan"
```

### Post-Deployment

**Pattern: Verification**
```bash
# Monitor logs
"Check production logs for errors"

# Smoke tests
npm run smoke-test:production

# Verify features
"Manually verify key features in production"

# Monitor metrics
"Check performance metrics"

# Document
"Document deployment completion and any issues"
```

## Emergency Workflows

### Production Incident

**Pattern: Incident Response**
```bash
# Immediate assessment
/clear
"INCIDENT: [Description]"

# Gather information
"Analyze error logs"
"Check system metrics"
"Review recent deployments"

# Identify cause
"Root cause: [cause]"

# Quick mitigation
"Create rollback plan" OR "Create hotfix"

# Execute fix
git checkout -b hotfix/incident-fix
# Implement fix
git commit -m "hotfix: Fix production incident"

# Deploy
# Follow emergency deployment process

# Post-incident
"Create incident report:
- Timeline
- Root cause
- Resolution
- Prevention steps"
```

## Collaboration Workflows

### Pair Programming

**Pattern: Driver-Navigator**
```bash
# Navigator: Guide the session
"We're implementing user authentication. Start with the User model"

# Driver: Execute
"Create User model with email, password, and profile fields"

# Iterate
Navigator: "Add password hashing"
Driver: "Add bcrypt hashing to User model"

# Switch roles periodically
```

### Mob Programming

**Pattern: Rotate Driver**
```bash
# Mob: Discuss approach
"Let's discuss how to implement caching"

# Driver 1: Start implementation (15 min)
"Create cache service with Redis"

# Driver 2: Continue (15 min)
"Add cache methods: get, set, delete"

# Driver 3: Testing (15 min)
"Add tests for cache service"

# Rotate and continue
```

## Productivity Tips

### Batch Operations

**Instead of:**
```bash
"Create User model"
# Wait
"Create Post model"
# Wait
"Create Comment model"
```

**Do:**
```bash
"Create User, Post, and Comment models with relationships"
```

### Use Templates

**Create custom commands:**
```bash
# .claude/commands/new-feature.md
Create new feature with:
1. Model
2. Service
3. Controller
4. Routes
5. Tests
6. Documentation

# Use it
/new-feature "user-profiles"
```

### Leverage MCP Servers

```bash
# Use microsoft-docs-mcp
"Show me Azure Function best practices"

# Use playwright
"Test the login flow automatically"

# Use azure-mcp
"List all production resources"
```

## Next Steps

- [Context Management](./context-management.md) - Optimize context usage
- [Code Quality](./code-quality.md) - Quality guidelines
- [Team Collaboration](./team-collaboration.md) - Team practices
- [Settings Configuration](../settings/README.md) - Configure Claude Code
