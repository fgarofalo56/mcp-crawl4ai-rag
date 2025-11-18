# Task Complete Command

Mark task as complete with full MCP checklist validation.

## Usage
```
/task-complete <task_id> [--skip-validation] [--add-learnings]
```

## Description
Marks a task as complete after running through the comprehensive quality assurance checklist and MCP validation.

## Implementation
1. **Quality Assurance**: Run full QA checklist validation
2. **MCP Validation**: Validate using all relevant MCP servers
3. **Testing Verification**: Ensure all tests pass
4. **Documentation Check**: Verify documentation is updated
5. **Knowledge Storage**: Store learnings and patterns
6. **Task Status Update**: Update task status and close related items

## Output Format
```
✅ Task Completion Validation
=============================

📝 Task Details:
- Task ID: {task_id}
- Title: {task_title}
- Completion Date: {timestamp}
- Time Spent: {actual_hours} hours
- Original Estimate: {estimated_hours} hours

🔍 Quality Assurance Checklist:

## Research & Documentation Validation:
- [✅] Microsoft Docs MCP: Azure best practices verified
- [✅] Context7 MCP: Latest SDK versions confirmed
- [✅] Brave Search MCP: Security advisories checked
- [✅] Crawl4ai-rag: Research findings added to knowledge base

## Azure & Infrastructure Validation:
- [✅] Azure-mcp MCP: Azure tools and services validated
- [✅] Azure Resource Graph MCP: Resource dependencies verified
- [✅] Supabase MCP: Database/auth/storage validated

## AI-Powered Analysis:
- [✅] AI-Server-Sequential-thinking: Complex logic validated
- [✅] Serena MCP: Code analysis and suggestions applied
- [✅] Analysis Tool: Comprehensive validation completed

## Testing & Quality:
- [✅] Playwright MCP: UI testing completed
- [✅] All tests pass: {unit_count} unit, {integration_count} integration
- [✅] No regression: Full regression suite passed
- [✅] Code quality: Meets standards ({score}/100)

## Knowledge Management:
- [✅] Knowledge base updated: {kb_entries} entries added
- [✅] Project tracking updated: Status and learnings documented
- [✅] Memory system updated: Patterns and solutions stored
- [✅] Documentation: All changes documented

✅ Final Validation Results:
- Task meets acceptance criteria: ✅
- All MCP validations passed: ✅
- Knowledge base enriched: ✅
- Ready for deployment: ✅

📚 Learnings Captured:
- Technical insights: {insights_count}
- Code patterns: {patterns_count}
- Troubleshooting solutions: {solutions_count}
- Best practices: {practices_count}

🎯 Task Status Updated:
- Previous Status: doing
- New Status: done
- Next Actions: {next_actions}

📊 Sprint Impact:
- Sprint progress: {new_percentage}%
- Velocity update: {velocity_impact}
- Team capacity: {remaining_capacity}%
```

## Parameters
- `--skip-validation`: Skip MCP validation (not recommended)
- `--add-learnings`: Force capture additional learnings

## MCP Servers Used
- **All Available MCP Servers**: Full validation suite
- **Crawl4ai-rag**: Knowledge storage and patterns
- **Analysis Tool**: Quality metrics and calculations
- **AI-Server-Sequential-thinking**: Completion analysis
