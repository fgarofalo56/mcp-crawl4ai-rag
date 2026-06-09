# 📋 Project Management Guide

> **🏠 [Home](../README.md)** | **📖 [Documentation](README.md)** | **Project Management**

---

**Version**: 1.0
**Last Updated**: 2025-10-14

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Project Tracking System](#project-tracking-system)
4. [Workflows](#workflows)
5. [Tools & Commands](#tools--commands)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The MCP-Crawl4AI-RAG project uses a comprehensive tracking system that prevents task loss and ensures nothing falls through the cracks. The system integrates three layers:

1. **Sprint-Level Tracking**: High-level goals and progress (`project_tracking/sprints/`)
2. **Task-Level Tracking**: Detailed task specifications (`project_tracking/sprints/current/task-*.md`)
3. **Persistent Memory**: Long-term knowledge storage (`.serena/memories/`)

### Why This System?

- ✅ **Nothing Gets Lost**: All work is tracked in files, git history, and Serena memories
- ✅ **Context Preserved**: New sessions start with full context
- ✅ **Team Visibility**: Clear sprint goals and progress tracking
- ✅ **Easy Navigation**: Find any task or decision quickly

---

## Quick Start

### View Current Sprint
```bash
cat project_tracking/sprints/current/sprint-current.md
```

### List All Tasks
```bash
python scripts/task_helper.py list
```

### Create New Task
```bash
python scripts/task_helper.py create --name "Task name" --priority P1 --type feature
```

### Update Task Status
```bash
python scripts/task_helper.py update --id 001 --status in_progress
```

### Check Sprint Status
```bash
python scripts/sprint_helper.py status
```

---

## Project Tracking System

### Directory Structure

```
project_tracking/
├── sprints/
│   ├── current/
│   │   ├── sprint-current.md           # Active sprint
│   │   ├── task-001-description.md     # Individual tasks
│   │   ├── task-002-description.md
│   │   └── ...
│   └── completed/
│       └── sprint-01-code-quality.md   # Archived sprints
├── backlog/
│   ├── feature-ideas.md                # Future features
│   ├── technical-debt.md               # Known debt
│   └── improvements.md                 # Enhancements
├── decisions/
│   ├── ADR-001-rag-strategy.md         # Decision records
│   └── ...
└── templates/
    ├── task-template.md                # Task template
    ├── sprint-template.md              # Sprint template
    └── decision-template.md            # ADR template
```

### Sprint File (`sprint-current.md`)

**Contains**:
- Sprint goals and objectives
- All tasks (P0, P1, P2, P3)
- Dependencies and blockers
- Daily progress log
- Sprint metrics

**Update Frequency**: Daily

### Task Files (`task-*.md`)

**Contains**:
- Detailed task description
- Acceptance criteria
- Implementation plan
- Testing requirements
- Documentation needs
- Progress notes

**Update Frequency**: As work progresses

### Serena Memories (`.serena/memories/`)

**Contains**:
- Project overview and context
- Common patterns and solutions
- Troubleshooting guides
- Task completion checklists
- Current project state

**Update Frequency**: At major milestones

---

## Workflows

### 1. Starting New Work

```
1. Check current sprint: cat project_tracking/sprints/current/sprint-current.md
2. Find next priority task (highest P0, then P1)
3. Create or open task file
4. Update task status to in_progress
5. Work on implementation
6. Update progress notes in task file
7. Mark task as completed when done
```

### 2. Creating a New Task

#### Option A: Using Helper Script
```bash
python scripts/task_helper.py create \
  --name "Implement feature X" \
  --priority P1 \
  --type feature \
  --effort M \
  --description "Add functionality for X"
```

#### Option B: Using Slash Commands
```bash
# For MCP tools
/task-create-tool {tool_name}

# For refactoring
/task-create-refactor {function_name}

# For testing
/task-create-test {test_area}

# For RAG improvements
/task-create-rag-improvement {improvement_area}
```

#### Option C: Manual Creation
```bash
cp project_tracking/templates/task-template.md \
   project_tracking/sprints/current/task-001-my-task.md
# Then edit the file
```

### 3. Sprint Planning

#### Starting a New Sprint
```bash
# Archive current sprint
python scripts/sprint_helper.py archive

# Start new sprint
python scripts/sprint_helper.py start \
  --number 2 \
  --goal "Improve performance" \
  --theme "optimization" \
  --duration 2
```

#### During Sprint
- Update daily progress log in sprint file
- Update task statuses as work progresses
- Add new tasks as discovered
- Update blocker list if issues arise

#### Ending Sprint
```bash
# Mark as completed
python scripts/sprint_helper.py complete

# Archive
python scripts/sprint_helper.py archive
```

### 4. Making Decisions

When you need to make a significant architectural or technical decision:

```bash
# 1. Create ADR file
cp project_tracking/templates/decision-template.md \
   project_tracking/decisions/ADR-{number}-{title}.md

# 2. Fill in:
#    - Context and problem
#    - Options considered
#    - Decision and rationale
#    - Consequences

# 3. Reference in commits and task files
```

---

## Tools & Commands

### Helper Scripts

#### `scripts/task_helper.py`

**Create Task**:
```bash
python scripts/task_helper.py create \
  --name "Task name" \
  --priority P0|P1|P2|P3 \
  --type feature|bugfix|refactor|test|docs|research \
  --effort XS|S|M|L|XL \
  --description "Description"
```

**List Tasks**:
```bash
# All tasks
python scripts/task_helper.py list

# Filter by status
python scripts/task_helper.py list --status todo
python scripts/task_helper.py list --status in_progress
python scripts/task_helper.py list --status completed
```

**Update Task Status**:
```bash
python scripts/task_helper.py update --id 001 --status in_progress
python scripts/task_helper.py update --id 001 --status completed
```

**Show Task Details**:
```bash
python scripts/task_helper.py show --id 001
```

#### `scripts/sprint_helper.py`

**Start Sprint**:
```bash
python scripts/sprint_helper.py start \
  --number 2 \
  --goal "Sprint goal" \
  --theme "theme-name" \
  --duration 2
```

**Show Status**:
```bash
python scripts/sprint_helper.py status
```

**Complete Sprint**:
```bash
python scripts/sprint_helper.py complete
```

**Archive Sprint**:
```bash
python scripts/sprint_helper.py archive
```

### Custom Slash Commands

Located in `.claude/commands/mcp-development/`:

- `/task-create-tool` - Create new MCP tool task
- `/task-create-refactor` - Create refactoring task
- `/task-create-test` - Create testing task
- `/task-create-rag-improvement` - Create RAG enhancement task

### Serena Memory Commands

- `/memory-store` - Store important context
- `/memory-search {keyword}` - Search stored memories
- `/kb-update-memory` - Update project knowledge base

---

## Best Practices

### Do's ✅

1. **Update Daily**: Update sprint file daily with progress
2. **Task Files for Complex Work**: Create task files for P0/P1 work
3. **Document Blockers**: Update blocker list immediately when stuck
4. **Reference Tasks in Commits**: Include task ID in commit messages
5. **Archive Completed Sprints**: Keep history organized
6. **Create ADRs**: Document significant decisions

### Don'ts ❌

1. **Don't Skip Task Files**: For complex work, always create detailed task files
2. **Don't Leave Tasks Orphaned**: Update status, don't abandon tasks
3. **Don't Forget Dependencies**: Document task dependencies
4. **Don't Mix Sprints**: Keep sprint focus clear
5. **Don't Create Huge Tasks**: Break down tasks larger than XL

### Task Sizing Guidelines

| Size | Time | Use For |
|------|------|---------|
| XS | 1-2 hours | Small fixes, documentation updates |
| S | 2-4 hours | Simple features, minor refactoring |
| M | 4-8 hours | Medium features, moderate refactoring |
| L | 1-2 days | Large features, major refactoring |
| XL | 2-5 days | Very large features, system redesign |

If a task is larger than XL, break it into smaller tasks.

---

## Troubleshooting

### Lost Context Between Sessions

**Problem**: You don't remember what you were working on.

**Solution**:
```bash
# 1. Check current sprint
cat project_tracking/sprints/current/sprint-current.md | grep "in_progress"

# 2. View recent progress
git log --oneline -10

# 3. Check Serena memories
# Use /memory-search command

# 4. View task files
python scripts/task_helper.py list --status in_progress
```

### Task Seems Blocked

**Problem**: You're stuck and can't proceed.

**Solution**:
1. Update task status to `blocked`
2. Document blocker in task file
3. Add to sprint blocker list
4. Add mitigation plan
5. Work on different task while resolving blocker

```bash
python scripts/task_helper.py update --id 001 --status blocked
```

### Can't Find a Task

**Problem**: You know a task exists but can't find it.

**Solution**:
```bash
# List all tasks
python scripts/task_helper.py list

# Search task files
grep -r "keyword" project_tracking/sprints/current/

# Check archived sprints
grep -r "keyword" project_tracking/sprints/completed/
```

### Sprint Taking Too Long

**Problem**: Sprint is behind schedule.

**Solution**:
1. Review sprint metrics in sprint file
2. Identify blockers
3. Re-prioritize remaining tasks
4. Move P2/P3 tasks to backlog
5. Focus on P0/P1 only
6. Consider extending sprint or reducing scope

---

## Integration with Existing Tools

### Git Workflow
- Reference task IDs in commit messages: `feat: implement X (task-001)`
- Update task status after commits
- Push regularly to preserve work

### CI/CD Pipeline
- Tests run automatically on push
- Update task file with test results
- Mark tests as passing in acceptance criteria

### Documentation
- Update `docs/PROJECT_STATUS.md` at sprint milestones
- Keep `README.md` current with features
- Reference decisions in `docs/ARCHITECTURE.md`

---

## Examples

### Example: Complete Task Workflow

```bash
# 1. List tasks to find next priority
python scripts/task_helper.py list --status todo

# 2. Start working on task 001
python scripts/task_helper.py update --id 001 --status in_progress

# 3. Work on the task...
# Follow implementation plan in task file
# Update progress notes

# 4. Complete task
python scripts/task_helper.py update --id 001 --status completed

# 5. Commit changes
git add .
git commit -m "feat: implement feature X (task-001)"
git push
```

### Example: Sprint Workflow

```bash
# Week 1: Start Sprint
python scripts/sprint_helper.py start \
  --number 1 \
  --goal "Improve code quality" \
  --duration 2

# Week 1-2: Daily Updates
# Update sprint-current.md daily progress log
# Update task statuses as work progresses

# Week 2: Mid-Sprint Check
python scripts/sprint_helper.py status

# Week 3: End Sprint
python scripts/sprint_helper.py complete
python scripts/sprint_helper.py archive
```

---

## Quick Reference

### File Locations
- Current sprint: `project_tracking/sprints/current/sprint-current.md`
- Tasks: `project_tracking/sprints/current/task-*.md`
- Backlog: `project_tracking/backlog/`
- Decisions: `project_tracking/decisions/ADR-*.md`
- Serena memories: `.serena/memories/`

### Task Statuses
- `todo` - Not started
- `in_progress` - Currently working
- `blocked` - Cannot proceed
- `completed` - Finished

### Priorities
- `P0` - Critical, must do this week
- `P1` - High, should do this sprint
- `P2` - Medium, next sprint if not done
- `P3` - Low, backlog

---

**Need help?** Check `.serena/memories/project_tracking_workflow.md` for detailed workflow documentation.

**Last Updated**: 2025-10-14
**Maintained By**: Development Team
