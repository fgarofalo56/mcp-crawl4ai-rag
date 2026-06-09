# Sprint Status Command

Show current sprint progress with comprehensive MCP validation and task overview.

## Usage
```
/sprint-status [sprint_number]
```

## Description
Provides a comprehensive overview of the current sprint including task progress, blockers, and validation status across all MCP servers.

## Implementation
1. **Task Analysis**: Review all tasks in `project_tracking/sprints/current/`
2. **MCP Validation**: Check status using all available MCP servers
3. **Progress Calculation**: Calculate completion percentages and velocity
4. **Blocker Identification**: Identify and categorize current blockers
5. **Quality Metrics**: Show testing coverage and documentation status

## Output Format
```
📊 Sprint {number} Status Report
================================

📈 Progress Overview:
- Total Tasks: {count}
- Completed: {count} ({percentage}%)
- In Progress: {count}
- Blocked: {count}
- Remaining: {count}

🎯 Current Sprint Goal: {goal_description}

⏰ Timeline:
- Sprint Start: {date}
- Sprint End: {date}
- Days Remaining: {count}
- Velocity: {points_per_day}

🚧 Active Blockers:
{list_of_blockers_with_owners}

✅ Quality Metrics:
- Test Coverage: {percentage}%
- Documentation: {status}
- Code Review Status: {status}
- Azure Compliance: {status}

🔍 MCP Server Status:
- Microsoft Docs: {status}
- Context7: {status}
- Azure-mcp: {status}
- Crawl4ai-rag: {status}
- All others...

📋 Next Priority Tasks:
{top_3_priority_tasks}
```

## MCP Servers Used
- **Project Tracking**: Task status analysis
- **Microsoft Docs MCP**: Azure compliance validation
- **Context7 MCP**: Dependency version checking
- **Crawl4ai-rag**: Knowledge base status
- **Analysis Tool**: Progress calculations
