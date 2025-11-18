# Sprint Start Command

Comprehensive sprint initialization with full MCP research, planning, and team preparation.

## Usage
```
/sprint-start <sprint_number> [--duration=1w|2w|3w|4w] [--team-size=number] [--focus=feature|bugfix|research|mixed]
```

## Description
Initializes a new sprint with comprehensive research, planning, capacity analysis, and team preparation using all available MCP servers.

## Implementation
1. **Sprint Planning**: Analyze backlog and capacity
2. **Research Phase**: Conduct upfront research on all planned work
3. **Dependency Analysis**: Identify and resolve dependencies
4. **Capacity Planning**: Validate team capacity and velocity
5. **Risk Assessment**: Identify potential blockers and risks
6. **Knowledge Preparation**: Pre-load relevant patterns and solutions
7. **Environment Setup**: Validate all development environments
8. **Documentation Setup**: Prepare documentation templates and standards

## Output Format
```
🚀 Sprint {number} Initialization
=================================

📅 Sprint Details:
- Sprint Number: {sprint_number}
- Duration: {duration}
- Start Date: {start_date}
- End Date: {end_date}
- Working Days: {working_days}
- Team Size: {team_size}

🎯 Sprint Goal:
{sprint_goal_description}

📊 Capacity Planning:
- Total Capacity: {total_story_points}
- Committed Points: {committed_points}
- Buffer Capacity: {buffer_percentage}%
- Velocity Trend: {velocity_trend}
- Confidence Level: {confidence_percentage}%

📋 Sprint Backlog ({task_count} tasks):

## High Priority (P1):
{high_priority_tasks}

## Medium Priority (P2):
{medium_priority_tasks}

## Low Priority (P3):
{low_priority_tasks}

🔍 Pre-Sprint Research Completed:

## Technology Research:
- Microsoft Docs: ✅ {docs_reviewed} articles reviewed
- SDK Versions: ✅ All dependencies validated
- Best Practices: ✅ {practices_count} practices documented
- Azure Services: ✅ Service status and limits confirmed

## Knowledge Base Preparation:
- Relevant Patterns: ✅ {patterns_count} patterns loaded
- Code Examples: ✅ {examples_count} examples prepared
- Troubleshooting Guides: ✅ {guides_count} guides ready
- Decision History: ✅ Previous decisions reviewed

🔗 Dependency Analysis:
- External Dependencies: {external_deps_count}
- Team Dependencies: {team_deps_count}
- Technical Dependencies: {tech_deps_count}
- Blocking Issues: {blocker_count} ⚠️

⚠️ Risk Assessment:

## High Risk Items:
{high_risk_items}

## Medium Risk Items:
{medium_risk_items}

## Mitigation Strategies:
{mitigation_plans}

🛠️ Environment Validation:
- Development Environment: ✅ All team members ready
- Testing Environment: ✅ Environments validated
- Azure Resources: ✅ All services operational
- CI/CD Pipeline: ✅ Pipeline tested and ready
- Documentation Tools: ✅ All tools accessible

📚 Team Preparation:

## Knowledge Sharing Sessions:
{scheduled_knowledge_sessions}

## Code Review Assignments:
{review_assignments}

## Pair Programming Pairs:
{pairing_schedule}

## Daily Standup Schedule:
{standup_schedule}

📈 Success Metrics:
- Sprint Goal Achievement: Target 100%
- Velocity: Target {target_velocity} points
- Quality: Target {quality_score}/100
- Team Satisfaction: Target {satisfaction_score}/10

🎯 Sprint Ceremonies:
- Daily Standups: {standup_time} daily
- Sprint Review: {review_date}
- Sprint Retrospective: {retro_date}
- Backlog Refinement: {refinement_schedule}

🔧 Development Standards:
- Code Review: Mandatory for all changes
- Testing: TDD approach required
- Documentation: Update with all changes
- Azure Best Practices: Mandatory compliance

🧠 Knowledge Management:
- Sprint Memory: ✅ Sprint context stored
- Pattern Library: ✅ Relevant patterns ready
- Troubleshooting: ✅ Common solutions prepared
- Team Learnings: ✅ Previous sprint insights applied

💡 Innovation Opportunities:
{innovation_suggestions}

🔄 Continuous Improvement:
{process_improvements_planned}

✅ Sprint Readiness Checklist:
- [ ] All tasks estimated and assigned
- [ ] Dependencies identified and managed
- [ ] Risks assessed and mitigated
- [ ] Environments validated
- [ ] Team prepared and aligned
- [ ] Knowledge base updated
- [ ] Success metrics defined

🎯 Ready to Begin!
Sprint {number} is fully prepared and ready for execution.

Next: Begin daily development with `/task-next`
```

## Duration Options
- `1w`: 1-week sprint
- `2w`: 2-week sprint (default)
- `3w`: 3-week sprint
- `4w`: 4-week sprint

## Focus Areas
- `feature`: New feature development
- `bugfix`: Bug fixing and stability
- `research`: Research and experimentation
- `mixed`: Balanced approach (default)

## MCP Servers Used
- **All Available MCP Servers**: Comprehensive sprint preparation
- **Microsoft Docs MCP**: Technology and best practices research
- **Context7 MCP**: SDK and dependency validation
- **Azure-mcp MCP**: Azure services and resource validation
- **Crawl4ai-rag**: Pattern and solution preparation
- **AI-Server-Sequential-thinking**: Capacity planning and risk analysis
- **Analysis Tool**: Velocity and metrics calculation
