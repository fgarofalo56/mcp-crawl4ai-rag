# 🚀 Implementation Guide - Claude Code Primer Setup

## Overview

This guide walks you through implementing the optimized Claude Code primer in your development workflow. Follow these steps for individual or team deployment.

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Individual Setup](#individual-setup)
3. [Team Deployment](#team-deployment)
4. [Project-Specific Configuration](#project-specific-configuration)
5. [Testing & Validation](#testing-validation)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Customization](#advanced-customization)

---

## Quick Start

### For Immediate Use (Individual Developer)

1. **Download the primer file**
   ```bash
   # Already done - file is at C:\tmp\claude-code-primer-optimized.md
   ```

2. **Open Claude Code in your project**
   ```bash
   cd your-project-directory
   claude
   ```

3. **Load and execute the primer**
   ```
   @C:\tmp\claude-code-primer-optimized.md

   Please execute this primer command to initialize project context.
   ```

4. **Start coding!**
   Claude now has comprehensive project context.

---

## Individual Setup

### Option 1: Global Command (Recommended)

Make the primer available in **all** your Claude Code sessions:

#### Windows
```bash
# Create global commands directory if it doesn't exist
mkdir %USERPROFILE%\.claude\commands

# Copy the primer
copy C:\tmp\claude-code-primer-optimized.md %USERPROFILE%\.claude\commands\primer.md

# Also copy the quick version
copy C:\tmp\primer-quick.md %USERPROFILE%\.claude\commands\quickprimer.md
```

#### macOS/Linux
```bash
# Create global commands directory
mkdir -p ~/.claude/commands

# Copy the primer
cp C:\tmp\claude-code-primer-optimized.md ~/.claude/commands/primer.md

# Also copy the quick version
cp C:\tmp\primer-quick.md ~/.claude/commands/quickprimer.md
```

**Usage**: Type `/primer` or `/quickprimer` in any Claude Code session

### Option 2: Project-Specific Command

Add the primer to a specific project:

```bash
# Navigate to your project
cd your-project-directory

# Create project commands directory
mkdir -p .claude/commands

# Copy the primer
cp C:\tmp\claude-code-primer-optimized.md .claude/commands/primer.md
```

**Usage**: Type `/primer` only when in this project

### Option 3: Bookmark/Alias

Create a shell alias for quick access:

#### Windows (PowerShell)
```powershell
# Add to your PowerShell profile
Add-Content $PROFILE "`nfunction Invoke-ClaudePrimer { claude '@C:\tmp\claude-code-primer-optimized.md Please execute this primer' }"
```

#### macOS/Linux (Bash/Zsh)
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias claude-prime="claude \"@/path/to/primer.md Please execute this primer\""' >> ~/.bashrc
source ~/.bashrc
```

**Usage**: Run `Invoke-ClaudePrimer` (Windows) or `claude-prime` (Unix)

---

## Team Deployment

### Step 1: Prepare Team Version

```bash
# Copy team template to project
cd your-project-directory
mkdir -p .claude/commands
cp C:\tmp\primer-team.md .claude/commands/primer.md
```

### Step 2: Customize for Your Project

Edit `.claude/commands/primer.md`:

```markdown
## Team Configuration

**Project Name**: YourProjectName
**Team Standards**: See docs/STANDARDS.md
**Code Style**: ESLint + Prettier (see .eslintrc.js)

## Additional Team Sections

### Our Tech Stack
- Frontend: React 18, TypeScript, Tailwind CSS
- Backend: Node.js, Express, PostgreSQL
- Infrastructure: Azure, Docker, GitHub Actions

### Our Conventions
- Branch naming: feature/JIRA-123-description
- Commit format: Conventional Commits
- PR requirements: 2 approvals, CI passing

### Team Contacts
- Tech Lead: @techLead
- DevOps: @devOpsTeam
- Architecture: @architects
```

### Step 3: Add to Version Control

```bash
git add .claude/commands/primer.md
git commit -m "Add Claude Code team primer command"
git push
```

### Step 4: Document in README

Add to your project's README.md:

```markdown
## Development Setup with Claude Code

### Quick Start
1. Install Claude Code: https://docs.claude.com/
2. Clone this repository
3. Run Claude Code in the project directory: `claude`
4. Initialize context: `/primer`
5. Start coding!

### Available Commands
- `/primer` - Full project initialization (10-15 min)
- `/quickprimer` - Fast assessment (5 min)
- See `.claude/commands/` for all available commands
```

### Step 5: Team Training

Schedule a 30-minute session to:
- Demonstrate primer usage
- Show context management (`/clear`, `/compact`, `/context`)
- Review output format and expectations
- Answer questions

---

## Project-Specific Configuration

### Creating Custom Primers

For specialized projects, create custom variants:

#### Example: Frontend-Focused Primer

```bash
# Create specialized command
cat > .claude/commands/frontend-primer.md << 'EOF'
# Frontend Project Primer

## Focus Areas
1. Component architecture
2. State management patterns
3. Styling approach (CSS/Tailwind/CSS-in-JS)
4. Build configuration
5. Testing strategy (Jest, React Testing Library)

## Specific Files to Analyze
- src/components/
- src/hooks/
- src/context/
- public/
- vite.config.js or webpack.config.js

## Frontend-Specific Questions
- What component library is used?
- How is global state managed?
- What's the routing strategy?
- How are API calls structured?
- What's the responsive design approach?
EOF
```

#### Example: Backend/API Primer

```bash
cat > .claude/commands/api-primer.md << 'EOF'
# API Project Primer

## Focus Areas
1. API structure and routing
2. Database schema and migrations
3. Authentication/authorization
4. Middleware and error handling
5. API documentation

## Specific Files to Analyze
- routes/ or controllers/
- models/ or database/
- middleware/
- migrations/
- API documentation (Swagger/OpenAPI)

## API-Specific Questions
- What framework is used? (Express, FastAPI, etc.)
- How is the database accessed? (ORM, query builder, raw SQL)
- What authentication strategy is implemented?
- How are API versions managed?
- What rate limiting is in place?
EOF
```

### Integrating with CLAUDE.md

Add primer guidance to your project's CLAUDE.md:

```markdown
# Project: YourProjectName

## Getting Started with Claude Code

When starting work on this project, run `/primer` to initialize context.

The primer will:
- Analyze project structure
- Review our coding standards
- Check current tasks in /project_tracking
- Identify areas needing attention

## After Primer Completion

You'll have context about:
- Our architecture decisions
- Current sprint work
- Testing requirements
- Deployment procedures

## Context Management

- Use `/clear` when switching between major features
- Use `/compact` during long sessions
- Monitor with `/context` to stay under 70% usage
- Leverage subagents for complex tasks

## Our Standards

[Your existing CLAUDE.md content...]
```

---

## Testing & Validation

### Test Checklist

Before rolling out to your team, validate the primer:

#### ✅ Basic Functionality
```bash
# Test in a sample project
cd sample-project
claude

# Run primer
/primer

# Verify output includes:
# - Project structure analysis
# - Dependencies identified
# - Test coverage reported
# - Next steps provided
```

#### ✅ Context Management
```
# After primer completes, check context
/context

# Verify context usage is < 50%
```

#### ✅ Error Handling
```
# Test with missing files
# Test with inaccessible MCP servers
# Test with large files

# Verify graceful degradation
```

#### ✅ Output Quality
```
# Review the summary output
# Check for:
# - Clear formatting
# - Actionable recommendations
# - Accurate information
# - Professional presentation
```

### Validation Script

Create a test script:

```bash
#!/bin/bash
# test-primer.sh

echo "Testing Claude Code Primer..."

# Test 1: Command exists
if claude --help | grep -q "primer"; then
    echo "✅ Primer command found"
else
    echo "❌ Primer command not found"
    exit 1
fi

# Test 2: Can execute without errors
claude --non-interactive "/primer" > primer-output.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Primer executed successfully"
else
    echo "❌ Primer execution failed"
    exit 1
fi

# Test 3: Output contains expected sections
if grep -q "Project Structure" primer-output.txt && \
   grep -q "Dependencies Overview" primer-output.txt; then
    echo "✅ Output contains expected sections"
else
    echo "❌ Output missing expected sections"
    exit 1
fi

echo "All tests passed! ✅"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Command Not Found
```
Error: /primer command not recognized
```

**Solution**:
```bash
# Check if file exists
ls ~/.claude/commands/primer.md  # or project/.claude/commands/primer.md

# Check file permissions
chmod 644 ~/.claude/commands/primer.md

# Restart Claude Code
```

#### Issue 2: Context Overload
```
Error: Context limit reached during primer execution
```

**Solution**:
```bash
# Use the quick primer instead
/quickprimer

# Or run phases separately
# Phase 1 only:
@primer.md Execute Phase 1 only (Project Discovery)
/clear
# Phase 2 only:
@primer.md Execute Phase 2 only (MCP Server Integration)
```

#### Issue 3: Serena Not Accessible
```
Error: Serena MCP server not responding
```

**Solution**:
```bash
# Check MCP server status
claude --list-mcp-servers

# Restart MCP servers
claude --restart-mcp

# Continue primer without Serena
# Primer will fallback to direct file reading
```

#### Issue 4: Large Files Blocking
```
Primer waiting for permission to read large files
```

**Solution**:
```
# Run with auto-approve (use caution)
claude --dangerously-skip-permissions

# Or manually approve during execution
# Press 'y' when prompted
```

#### Issue 5: Outdated Cache
```
Primer showing outdated project information
```

**Solution**:
```bash
# Clear Claude's cache
claude --clear-cache

# Re-run primer
/primer
```

### Getting Help

If issues persist:

1. **Check Claude Code Documentation**
   - https://docs.claude.com/

2. **Review MCP Server Logs**
   ```bash
   claude --show-logs
   ```

3. **Community Support**
   - GitHub Issues: https://github.com/anthropics/claude-code
   - Discord: https://discord.gg/anthropic

4. **Contact Support**
   - support@anthropic.com

---

## Advanced Customization

### Creating Subagent-Enhanced Primers

For complex projects, create specialized subagents:

```bash
# Create subagent for code review
cat > .claude/agents/reviewer.md << 'EOF'
# Code Reviewer Agent

## Purpose
Specialized in code quality analysis and review.

## Capabilities
- Security vulnerability detection
- Performance analysis
- Best practices compliance
- Test coverage assessment

## Usage
Call me during primer Phase 6 for detailed code quality analysis.
EOF

# Create subagent for documentation
cat > .claude/agents/docs-writer.md << 'EOF'
# Documentation Writer Agent

## Purpose
Specialized in technical documentation and API docs.

## Capabilities
- API documentation generation
- README maintenance
- Architecture decision records (ADRs)
- Tutorial creation

## Usage
Call me during primer Phase 6 to assess documentation quality.
EOF
```

Update primer to use subagents:

```markdown
## Phase 6: Analysis & Recommendations

### 6.3 Code Quality Deep Dive
I'll delegate to @reviewer subagent for detailed analysis:
- Security audit
- Performance profiling
- Best practices review

### 6.2 Documentation Assessment
I'll delegate to @docs-writer subagent for:
- API documentation completeness
- README quality
- Missing guides
```

### Integration with CI/CD

Run primer automatically in CI:

```yaml
# .github/workflows/claude-primer.yml
name: Claude Code Primer Check

on:
  pull_request:
    branches: [main, develop]

jobs:
  primer-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Claude Code Primer
        run: |
          claude --non-interactive --headless \
            -p "Run /primer and output results as JSON" \
            --output-format stream-json > primer-results.json

      - name: Check for Critical Issues
        run: |
          if grep -q "Security vulnerabilities: HIGH" primer-results.json; then
            echo "❌ Critical security issues found"
            exit 1
          fi

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: primer-analysis
          path: primer-results.json
```

### Custom Metrics Dashboard

Track primer results over time:

```python
# scripts/track-primer-metrics.py
import json
import datetime

def extract_metrics(primer_output):
    """Extract key metrics from primer output"""
    return {
        'timestamp': datetime.datetime.now().isoformat(),
        'test_coverage': extract_coverage(primer_output),
        'security_issues': count_security_issues(primer_output),
        'tech_debt_score': calculate_debt_score(primer_output),
        'documentation_completeness': assess_docs(primer_output)
    }

def save_metrics(metrics):
    """Save to metrics database or file"""
    with open('primer-metrics.jsonl', 'a') as f:
        f.write(json.dumps(metrics) + '\n')

# Usage in CI/CD
if __name__ == '__main__':
    with open('primer-results.json') as f:
        output = json.load(f)
    metrics = extract_metrics(output)
    save_metrics(metrics)
```

---

## Maintenance & Updates

### Keeping Primers Current

Schedule regular reviews:

```bash
# Add to calendar: Monthly primer review
# 1. Review primer output quality
# 2. Update for new technologies
# 3. Incorporate team feedback
# 4. Optimize for new Claude Code features
```

### Version Control

Track primer versions:

```bash
# Tag primer versions
git tag -a primer-v1.0 -m "Initial optimized primer"
git push origin primer-v1.0

# Create changelog
cat > .claude/CHANGELOG.md << 'EOF'
# Primer Command Changelog

## v1.0 (2025-01-15)
- Initial optimized primer release
- 7-phase structure
- Context management integration
- Team collaboration features
EOF
```

### Feedback Loop

Collect team feedback:

```markdown
# .claude/FEEDBACK.md

## Primer Feedback

### What's Working Well
- [Team member comments]

### Areas for Improvement
- [Suggestions]

### Feature Requests
- [New capabilities needed]

### Bugs/Issues
- [Problems encountered]
```

---

## Success Metrics

Track these KPIs to measure primer effectiveness:

### Quantitative
- **Time to productivity**: How fast can new devs start contributing?
- **Context efficiency**: Average context usage after primer
- **Error reduction**: Fewer initialization failures
- **Test coverage**: Improvement in coverage over time

### Qualitative
- **Developer satisfaction**: Survey team members
- **Code quality**: Fewer bugs in first PRs
- **Documentation quality**: Better-maintained docs
- **Team alignment**: Consistent understanding of codebase

---

## Next Steps

### Week 1
- [ ] Test primer on sample project
- [ ] Customize for your primary project
- [ ] Add to version control

### Week 2
- [ ] Deploy to team (pilot with 2-3 developers)
- [ ] Gather initial feedback
- [ ] Make adjustments

### Month 1
- [ ] Full team rollout
- [ ] Create project-specific variants
- [ ] Integrate with CI/CD

### Ongoing
- [ ] Monthly primer reviews
- [ ] Update based on feedback
- [ ] Track and report metrics
- [ ] Share learnings with team

---

## Resources

### Documentation
- **Claude Code Docs**: https://docs.claude.com/
- **MCP Servers**: https://docs.claude.com/mcp
- **Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices

### Community
- **GitHub**: https://github.com/anthropics/claude-code
- **Discord**: https://discord.gg/anthropic
- **Examples**: https://github.com/hesreallyhim/awesome-claude-code

### Support
- **Email**: support@anthropic.com
- **Documentation**: https://docs.claude.com/support

---

**Ready to implement? Start with the Quick Start section above!**

Questions? Reach out to your team lead or Claude Code community.
