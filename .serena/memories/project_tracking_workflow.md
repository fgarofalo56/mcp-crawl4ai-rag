# Project Tracking Workflow

## Overview

The MCP-Crawl4AI-RAG project uses a comprehensive tracking system that prevents task loss and ensures nothing falls through the cracks.

## Three-Layer Tracking System

### 1. Sprint-Level Tracking (`project_tracking/sprints/current/`)
- **Purpose**: Track current sprint goals, tasks, and progress
- **File**: `sprint-current.md` - Active sprint with all tasks
- **Update Frequency**: Daily progress logs
- **Owner**: Development team

**What It Tracks**:
- Sprint goals and objectives
- All active tasks (P0, P1, P2, P3)
- Dependencies and blockers
- Daily progress updates
- Sprint metrics

### 2. Task-Level Tracking (`project_tracking/sprints/current/task-*.md`)
- **Purpose**: Detailed task specifications and implementation plans
- **Naming**: `task-{number}-{brief-description}.md`
- **Update Frequency**: As work progresses
- **Owner**: Task assignee

**What It Tracks**:
- Acceptance criteria
- Implementation plan (step-by-step)
- Testing requirements
- Documentation needs
- Progress notes

### 3. Serena Memory (`.serena/memories/`)
- **Purpose**: Persistent knowledge across sessions
- **Update Frequency**: At major milestones
- **Owner**: All contributors

**What It Stores**:
- Project overview and context
- Common patterns and solutions
- Troubleshooting guides
- Task completion checklists

## Workflow for Starting New Work

### Step 1: Check Current Sprint
```bash
# View current sprint status
cat project_tracking/sprints/current/sprint-current.md | grep -A 10 "Sprint Backlog"
```

### Step 2: Select Next Task
- Check sprint-current.md for highest priority `todo` task
- Review task dependencies
- Check if task file exists

### Step 3: Create Task File (if needed)
Use one of the custom slash commands:
- `/task-create-tool` - For new MCP tools
- `/task-create-refactor` - For code refactoring
- `/task-create-test` - For testing tasks
- `/task-create-rag-improvement` - For RAG enhancements

### Step 4: Work on Task
1. Update task status to `in_progress`
2. Use TodoWrite tool for session tracking
3. Follow implementation plan in task file
4. Update progress notes in task file

### Step 5: Complete Task
1. Verify all acceptance criteria met
2. Run tests and ensure passing
3. Update documentation
4. Update task status to `completed`
5. Update sprint-current.md with completion
6. Commit changes with reference to task number

## Workflow for Sprint Planning

### Starting a New Sprint
1. Archive completed sprint to `project_tracking/sprints/completed/`
2. Copy template from `project_tracking/templates/sprint-template.md`
3. Review `docs/PROJECT_STATUS.md` for current work
4. Create sprint file in `project_tracking/sprints/current/`
5. Break down goals into tasks
6. Create task files for P0 and P1 tasks

### During Sprint
1. Daily progress log updates in sprint file
2. Task status updates as work progresses
3. Add new tasks to backlog as discovered
4. Update blocker list if issues arise

### Ending a Sprint
1. Complete sprint review section
2. Document lessons learned
3. Calculate metrics
4. Move sprint file to `completed/`
5. Plan next sprint

## Decision Tracking

### When to Create an ADR (Architecture Decision Record)
- Choosing between multiple implementation approaches
- Adding/removing major dependencies
- Changing core architecture patterns
- Deprecating features

### Creating an ADR
1. Use template: `project_tracking/templates/decision-template.md`
2. Save to: `project_tracking/decisions/ADR-{number}-{title}.md`
3. Number sequentially (ADR-001, ADR-002, etc.)
4. Reference in task files and commit messages

## Task Statuses

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `todo` | Not started, ready to begin | Assign and start |
| `in_progress` | Currently being worked on | Continue work, update progress |
| `blocked` | Cannot proceed due to blocker | Resolve blocker, update status |
| `completed` | All acceptance criteria met | Archive, update metrics |

## Task Priorities

| Priority | Meaning | Timeline |
|----------|---------|----------|
| P0 | Critical - Must complete this sprint | This week |
| P1 | High - Should complete this sprint | This sprint |
| P2 | Medium - Nice to have | Next sprint if not done |
| P3 | Low - If time permits | Backlog |

## File Organization

```
project_tracking/
├── sprints/
│   ├── current/
│   │   ├── sprint-current.md           # Active sprint
│   │   ├── task-001-description.md     # Task files
│   │   ├── task-002-description.md
│   │   └── ...
│   └── completed/
│       ├── sprint-01-code-quality.md   # Archived sprints
│       └── ...
├── backlog/
│   ├── feature-ideas.md                # Future features
│   ├── technical-debt.md               # Known debt
│   └── improvements.md                 # Enhancements
├── decisions/
│   ├── ADR-001-rag-strategy.md         # Decision records
│   ├── ADR-002-testing-approach.md
│   └── ...
└── templates/
    ├── task-template.md                # Task template
    ├── sprint-template.md              # Sprint template
    └── decision-template.md            # ADR template
```

## Integration with Tools

### TodoWrite Tool (Session-based)
- Use for tracking multi-step work within a session
- Doesn't persist across sessions
- Good for breaking down task implementation
- Updates automatically during conversation

### Serena Memories (Persistent)
- Use for long-term knowledge storage
- Write important patterns, decisions, solutions
- Read at start of new sessions for context
- Commands: `/memory-store`, `/memory-search`

### PROJECT_STATUS.md (Team visibility)
- High-level sprint goals and metrics
- Current sprint overview
- Recent completions
- Success criteria

## Best Practices

### Do's ✅
- Update sprint file daily with progress
- Create task files before starting P0/P1 work
- Document blockers immediately
- Reference task numbers in commits (e.g., "feat: implement X (task-001)")
- Archive completed sprints
- Create ADRs for significant decisions

### Don'ts ❌
- Don't skip task file creation for complex work
- Don't leave tasks in `in_progress` indefinitely
- Don't forget to update dependencies
- Don't mix sprint planning with execution
- Don't create tasks that are too large (> XL)

## Quick Reference Commands

```bash
# View current sprint
cat project_tracking/sprints/current/sprint-current.md

# List all current tasks
ls project_tracking/sprints/current/task-*.md

# Search for specific task
grep -r "keyword" project_tracking/sprints/current/

# View task completion checklist
cat .serena/memories/task_completion_checklist.md

# Create new sprint (using template)
cp project_tracking/templates/sprint-template.md project_tracking/sprints/current/sprint-X.md

# Archive completed sprint
mv project_tracking/sprints/current/sprint-X.md project_tracking/sprints/completed/
```

## When Things Go Wrong

### Lost Context Between Sessions
1. Read `project_tracking/sprints/current/sprint-current.md`
2. Check your last `in_progress` task
3. Review Serena memories: `/memory-search {topic}`
4. Check recent commits: `git log --oneline -10`

### Forgot What You Were Working On
1. Check TodoWrite from last session (lost if session ended)
2. Read sprint progress log for yesterday
3. Check task file progress notes
4. Look at git diff: `git diff`

### Task Seems Blocked
1. Update task status to `blocked`
2. Document blocker in task file and sprint file
3. Add mitigation plan
4. Work on different task while blocked
5. Check blocker resolution daily

## Metrics Tracking

### Sprint Metrics
- Tasks completed vs. committed
- Average task completion time
- Number of blockers
- Test coverage improvement
- Code quality improvements

### Quality Metrics
- Test coverage percentage
- Lines of code per function (target < 150)
- Linting errors (target: 0)
- CI/CD pass rate (target: 100%)

---

**Last Updated**: 2025-10-14
**Version**: 1.0
**Maintained By**: Development Team
