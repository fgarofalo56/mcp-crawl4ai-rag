# Project Tracking & Work Outputs

This directory contains sprint/task management files AND all work outputs generated during development activities.

## Directory Structure

```
project_tracking/
├── sprints/                 # Sprint planning and tracking
│   ├── current/            # Active sprint files
│   └── archive/            # Completed sprints (if needed)
│
├── templates/              # Templates for tasks, sprints, decisions
│   ├── task-template.md
│   ├── sprint-template.md
│   └── decision-template.md
│
├── decisions/              # Architecture Decision Records (ADRs)
│   └── *.md               # Individual ADR files
│
├── reports/                # AI-generated reports and analyses
│   ├── *_REPORT.md        # Development reports
│   ├── *_ANALYSIS.md      # Code/architecture analyses
│   ├── *_VALIDATION.md    # Validation and verification reports
│   └── *_REVIEW.md        # Review reports
│
├── summaries/              # Work summaries and completion reports
│   ├── *_SUMMARY.md       # Refactoring summaries
│   ├── *_COMPLETE.md      # Completion reports
│   └── *_UPDATE.md        # Update summaries
│
├── action-plans/           # Implementation and action plans
│   ├── *_PLAN.md          # Implementation plans
│   └── *_ACTION*.md       # Action plans
│
└── reviews/                # Code reviews and audits
    ├── *_CODE_REVIEW*.md  # Code review reports
    └── *_AUDIT*.md        # Audit reports
```

## Purpose

### **Why this directory exists:**
1. **Keep codebase clean**: Work outputs don't clutter the root directory
2. **Organize by type**: Easy to find reports, summaries, or plans
3. **Preserve work history**: All work artifacts are tracked and searchable
4. **Separate concerns**: Project documentation (docs/) vs. work artifacts (here)

### **What goes here:**
- ✅ Sprint planning and tracking documents
- ✅ Task tracking files
- ✅ Architecture decision records
- ✅ **ALL AI-generated work outputs**:
  - Reports (validation, analysis, review)
  - Summaries (refactoring, implementation, updates)
  - Action plans (implementation plans, roadmaps)
  - Code reviews and audits

### **What does NOT go here:**
- ❌ Project documentation → `docs/`
- ❌ User guides → `docs/guides/`
- ❌ API references → `docs/`
- ❌ Architecture docs → `docs/ARCHITECTURE.md`

## File Naming Conventions

### Reports
- Pattern: `{TOPIC}_{TYPE}_REPORT.md`
- Examples: `DOCUMENTATION_VALIDATION_REPORT.md`, `ARCHITECTURE_REVIEW_REPORT.md`

### Summaries
- Pattern: `{TOPIC}_{ACTION}_SUMMARY.md` or `{TOPIC}_COMPLETE.md`
- Examples: `REFACTORING_SUMMARY.md`, `DOCUMENTATION_UPDATE_SUMMARY.md`

### Action Plans
- Pattern: `{TOPIC}_ACTION_PLAN.md` or `{TOPIC}_IMPLEMENTATION_PLAN.md`
- Examples: `IMPLEMENTATION_ACTION_PLAN.md`, `REFACTORING_ROADMAP.md`

### Reviews
- Pattern: `{TOPIC}_REVIEW.md` or `{TOPIC}_AUDIT.md`
- Examples: `CODE_REVIEW_SUMMARY.md`, `SECURITY_AUDIT.md`

## Usage Guidelines

### For AI Assistants
1. **Always** save work outputs to appropriate subdirectory
2. **Never** create work output files in root or docs/
3. **Use** descriptive names following conventions above
4. **Organize** by type (reports/, summaries/, action-plans/, reviews/)

### For Developers
1. Check this directory for recent work artifacts
2. Use templates/ for consistent task/sprint/decision formatting
3. Archive old sprints to keep current/ clean
4. Reference work outputs in commits/PRs for context

## Integration with Workflow

This directory works with:
- `.serena/memories/` - Persistent AI context (workflows, conventions)
- `docs/` - Project documentation (separate from work outputs)
- `docs/PROJECT_MANAGEMENT.md` - Sprint and task management guide

---

**Last Updated**: 2025-10-28
**Maintainer**: Project team
