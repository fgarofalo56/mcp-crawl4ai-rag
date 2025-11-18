# Context Management

Master context window optimization for efficient, long-running development sessions.

## Overview

Claude Code uses a context window to maintain conversation history, code references, and working memory. Effective context management ensures optimal performance, better responses, and longer productive sessions.

## Understanding Context

### What's in Context?

**1. Conversation History**
- Your messages
- Claude's responses
- Command outputs
- Error messages

**2. File Contents**
- Files read with Read tool
- Code snippets shown
- Documentation referenced

**3. MCP Server Responses**
- API results
- Database queries
- External tool outputs

**4. System Context**
- Project structure
- Configuration
- Command history

### Context Window Size

- **Total capacity:** ~200,000 tokens
- **Optimal usage:** 60-80% (120,000-160,000 tokens)
- **Warning threshold:** 85% (170,000 tokens)
- **Critical threshold:** 95% (190,000 tokens)

## Monitoring Context

### Check Context Usage

```bash
/context
```

**Example output:**
```
Context Usage: 125,000 / 200,000 tokens (62.5%)
Status: Healthy

Breakdown:
- Conversation: 45,000 tokens (36%)
- Files: 60,000 tokens (48%)
- MCP Responses: 15,000 tokens (12%)
- System: 5,000 tokens (4%)

Recommendations:
- Continue current session
- Consider /compact at 80%
```

### Watch for Warning Signs

**Performance degradation:**
- Slower responses
- Incomplete answers
- Lost context from earlier in conversation

**High context usage:**
- Over 80% capacity
- Large file reads
- Extensive MCP server usage

## Context Management Commands

### /clear

**Purpose:** Start fresh conversation, keep settings

**When to use:**
- Context >90% full
- Switching to completely different task
- Context feels "muddled"
- Need clean slate

**What it preserves:**
- Project configuration
- MCP server connections
- Custom commands
- File system state

**What it clears:**
- Conversation history
- File contents in memory
- Previous outputs

**Example:**
```bash
/clear

# Start new task
"Implement payment processing feature"
```

### /compact

**Purpose:** Compress conversation history, keep essential context

**When to use:**
- Context 75-85% full
- Want to continue current task
- Need to preserve context
- Multiple related tasks

**What it preserves:**
- Essential conversation points
- Key code references
- Important decisions
- Current task context

**What it compresses:**
- Verbose responses
- Redundant information
- Old tangents
- Resolved issues

**Example:**
```bash
/compact

# Continue current work
"Now add validation to the payment form"
```

### /context reset

**Purpose:** Clear context and reset to defaults

**When to use:**
- Major context issues
- Starting completely new project
- Debugging context problems

**Example:**
```bash
/context reset

# Confirm when prompted
yes
```

## Context Optimization Strategies

### 1. Use Concise Output Style

**High context usage:**
```json
{
  "outputStyle": "explanatory"  // Uses 500-1000 tokens per response
}
```

**Optimized:**
```json
{
  "outputStyle": "concise"      // Uses 200-400 tokens per response
}
```

**Dynamic adjustment:**
```bash
# Start explanatory for learning
/output explanatory

# Switch to concise when context fills
/output concise

# Use terse for critical context conservation
/output terse
```

### 2. Read Files Strategically

**Inefficient:**
```
"Read all Python files in the project"
# Loads entire codebase into context
```

**Efficient:**
```
"Find files related to user authentication"
# Search first, read only relevant files

"Read src/auth/login.py"
# Read specific files needed
```

### 3. Use Grep Before Read

**Pattern:**
```bash
# Step 1: Search for relevant code
"Find all functions that handle payments"

# Step 2: Read only relevant files
"Read the PaymentProcessor class"

# Step 3: Make changes
"Add retry logic to processPayment"
```

### 4. Batch Related Operations

**Inefficient:**
```
"Create user model"
# Wait for response
"Now create user controller"
# Wait for response
"Now create user routes"
# Wait for response
```

**Efficient:**
```
"Create user model, controller, routes, and tests for user management"
# One comprehensive request
```

### 5. Use Subagents

**Purpose:** Isolate tasks in separate contexts

**When to use:**
- Independent parallel tasks
- Exploratory analysis
- Code reviews
- Documentation generation

**Example:**
```bash
# Main session: Continue feature work
"Add payment processing"

# Subagent 1: Code review
/agent reviewer "Review the authentication code"

# Subagent 2: Documentation
/agent documenter "Generate API docs for payment endpoints"
```

### 6. Progressive Disclosure

**Pattern:**
```bash
# Start high-level
"Show me the architecture of the auth system"

# Then specific
"How does JWT token validation work?"

# Then detailed
"Show me the validateToken function implementation"
```

### 7. Reference by Name

**Inefficient:**
```
"Here's the entire UserController.ts file [paste 500 lines]
Can you add a new method?"
```

**Efficient:**
```
"Add a deleteUser method to UserController.ts"
# Claude reads the file as needed
```

## Long Session Strategies

### Multi-Day Project Pattern

**Day 1: Setup and Architecture**
```bash
# Start fresh
/clear

# Set context
"I'm building a blog platform with Next.js, TypeScript, and PostgreSQL"

# High-level planning
"Design the database schema and API structure"

# At end of day (context: 65%)
# Leave session open or document decisions
```

**Day 2: Implementation**
```bash
# Continue from yesterday (context: 65%)
"Implement the post creation endpoint based on yesterday's design"

# If context >85%
/compact

# Continue working
```

**Day 3: Testing and Refinement**
```bash
# If context high from previous days
/clear

# Set context efficiently
"Working on blog platform. I've implemented post creation, now need to add tests"

# Continue
```

### Sprint Workflow

**Sprint Start (Monday):**
```bash
/clear

# Set sprint context
"Sprint goal: Implement user profile features
Stories: Profile view, edit, avatar upload"

# Plan
"Break down these stories into tasks"
```

**Mid-Sprint (Wednesday, context: 75%):**
```bash
/compact

# Continue
"Profile view and edit complete. Now implementing avatar upload"
```

**Sprint End (Friday):**
```bash
# Review and document
"Create sprint summary: what was completed, issues encountered, next steps"
```

## Context Window Exhaustion

### Symptoms

1. **Truncated responses**
   - Responses cut off mid-sentence
   - Incomplete code blocks

2. **Lost context**
   - Forgetting earlier conversation
   - Re-asking for information provided

3. **Performance issues**
   - Very slow responses
   - Timeouts

### Recovery Strategies

**Immediate Fix:**
```bash
/compact
```

**If that doesn't help:**
```bash
/clear

# Provide concise summary
"Working on user authentication. Implemented login/logout.
Now need password reset feature."
```

**For complex projects:**
```bash
# Create context document
"Generate a concise summary of our work so far"

# Save the summary
# Start fresh
/clear

# Restore context
"Here's where we left off: [paste summary]"
```

## Subagent Usage

### When to Use Subagents

**✅ Good use cases:**
- Independent code reviews
- Parallel feature development
- Documentation generation
- Exploratory analysis
- Security audits

**❌ Poor use cases:**
- Tasks that need main conversation context
- Quick single operations
- Highly interdependent changes

### Subagent Patterns

**Pattern 1: Parallel Development**
```bash
# Main: Core feature
"Implement payment processing"

# Subagent 1: Tests
/agent tester "Write integration tests for payment processing"

# Subagent 2: Docs
/agent docs "Document payment API endpoints"
```

**Pattern 2: Code Review**
```bash
# Main: Continue development
"Add email notifications"

# Subagent: Review completed code
/agent reviewer "Review the payment processing implementation for security and performance"
```

**Pattern 3: Research**
```bash
# Main: Implementation work
"Working on authentication"

# Subagent: Research
/agent researcher "Research best practices for OAuth2 implementation"
```

### Managing Subagent Results

**Bring results back to main session:**
```bash
# After subagent completes
"The code review found 3 issues. Let's address them:
1. [issue 1]
2. [issue 2]
3. [issue 3]"
```

## Context-Aware Request Patterns

### High Context Situation (>80%)

**Use references:**
```bash
"Add error handling to the processPayment function"
# Not: "Here's the function: [paste code]"
```

**Use terse style:**
```bash
/output terse
"Add logging to all API endpoints"
```

**Batch operations:**
```bash
"Fix all linting errors and update tests"
# Not separate requests for each
```

### Low Context Situation (<50%)

**Can be more verbose:**
```bash
/output explanatory
"Explain how the authentication flow works"
```

**Can explore:**
```bash
"What's the best approach for implementing caching?"
```

**Can request detailed analysis:**
```bash
"Review the entire API layer for security issues"
```

## Context Budgeting

### Allocate Context by Task Type

**Feature Development (target: 60-70%)**
- Conversation: 30%
- Code files: 50%
- Tool outputs: 20%

**Debugging (target: 50-60%)**
- Conversation: 40%
- Error logs: 30%
- Code files: 30%

**Code Review (target: 70-80%)**
- Conversation: 20%
- Code files: 60%
- Analysis results: 20%

**Architecture Planning (target: 40-50%)**
- Conversation: 60%
- Documentation: 30%
- Code samples: 10%

## Best Practices Summary

### Do's

✅ Monitor context regularly with `/context`
✅ Use `/compact` at 75-80% capacity
✅ Use `/clear` for new major tasks
✅ Choose appropriate output style
✅ Read files strategically
✅ Use Grep before Read
✅ Batch related operations
✅ Use subagents for independent tasks
✅ Reference files by name, not content

### Don'ts

❌ Let context reach 95%+
❌ Paste large code blocks unnecessarily
❌ Read entire codebase into context
❌ Use verbose output when context high
❌ Ignore context warnings
❌ Continue when performance degrades
❌ Use subagents for dependent tasks

## Troubleshooting

### Problem: Context Filling Too Quickly

**Solutions:**
1. Switch to concise/terse output
2. Stop reading unnecessary files
3. Use Grep instead of Read
4. Use `/compact` more frequently

### Problem: Lost Important Context

**Solutions:**
1. Document key decisions in files
2. Create context summaries
3. Use project CLAUDE.md for persistent context
4. Commit work frequently

### Problem: Can't Continue After /clear

**Solution:**
Create a context restoration file:

```markdown
# Project Context

## Current State
- Implemented user auth (login, logout, JWT)
- Created user and post database models
- Built API endpoints for CRUD operations

## Active Task
Adding password reset feature

## Key Decisions
- Using JWT for auth (not sessions)
- PostgreSQL database
- Express.js API
- React frontend

## Next Steps
1. Create password reset endpoint
2. Add email service
3. Create reset flow UI
```

After `/clear`:
```bash
"Read docs/context.md"
# Continue working
```

### Problem: Subagent Results Too Large

**Solution:**
```bash
# Instead of copying entire result
"The review identified: [summarize key points only]"
```

## Advanced Techniques

### Context Checkpointing

**Save important state:**
```bash
# At key milestones
"Generate a summary of what we've built and key decisions made"

# Save to file
# Can restore later if needed
```

### Context Templates

**Create templates for common scenarios:**

**Feature Development Template:**
```markdown
# Feature: [Name]

## Goal
[What we're building]

## Approach
[Key decisions]

## Status
[What's done, what's next]
```

**Bug Fix Template:**
```markdown
# Bug: [Description]

## Symptoms
[What's wrong]

## Root Cause
[Why it's happening]

## Fix
[How we're fixing it]
```

## Metrics and Monitoring

### Track Context Efficiency

**Measure:**
- Average context usage per session
- Time to context exhaustion
- `/compact` vs `/clear` frequency
- Session duration

**Optimize:**
- Identify context-heavy operations
- Adjust output styles
- Refine file reading patterns
- Improve batching

## Next Steps

- [Workflow Patterns](./workflow-patterns.md) - Efficient development workflows
- [Code Quality](./code-quality.md) - Quality guidelines
- [Team Collaboration](./team-collaboration.md) - Team practices
- [Output Styles](../settings/output-styles.md) - Configure verbosity
