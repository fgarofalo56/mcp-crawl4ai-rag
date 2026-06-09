# Knowledge Base Update Memory Command

Update project memory with current findings and work references.

## Usage
```
/kb-update-memory [--scope=current-task|sprint|project] [--include-context]
```

## Description
Updates the project memory system with current work context, findings, decisions, and patterns for future reference and team knowledge sharing.

## Implementation
1. **Context Capture**: Capture current work session context
2. **Memory Analysis**: Analyze what should be stored for future reference
3. **Pattern Extraction**: Identify reusable patterns and solutions
4. **Decision Recording**: Document key decisions and rationale
5. **Cross-Reference Update**: Link to related work and dependencies
6. **Team Knowledge**: Prepare information for team sharing

## Output Format
```
🧠 Project Memory Updated
=========================

📊 Update Summary:
- Scope: {scope}
- Context Captured: {context_items} items
- New Patterns: {pattern_count}
- Decisions Recorded: {decision_count}
- Cross-References: {reference_count}

💾 Memory Categories Updated:

## Technical Decisions:
- {decision_1}
- {decision_2}
- {decision_3}

## Code Patterns:
- {pattern_1}
- {pattern_2}
- {pattern_3}

## Integration Examples:
- {integration_1}
- {integration_2}

## Troubleshooting Solutions:
- {solution_1}
- {solution_2}

🔗 Cross-References Added:
- Related Tasks: {task_links}
- Related Sprints: {sprint_links}
- Related Patterns: {pattern_links}
- Related Decisions: {decision_links}

📚 Knowledge Base Integration:
- New Entries: {new_entries}
- Updated Entries: {updated_entries}
- Enhanced Search Terms: {search_terms}

🎯 Team Benefits:
- Onboarding Context: ✅ Available
- Decision History: ✅ Documented
- Pattern Library: ✅ Enhanced
- Troubleshooting Guide: ✅ Updated

📊 Memory Statistics:
- Total Memory Entries: {total_count}
- Recent Activity: {activity_level}
- Most Referenced: {most_referenced}
- Knowledge Growth: {growth_trend}

💡 Recommendations:
- Share findings with team
- Review decision impacts in next retrospective
- Consider pattern promotion to shared library
- Document lessons learned

🔍 Quick Access:
- Search memory: `/memory-search {keywords}`
- Browse patterns: `/pattern-browse`
- Review decisions: `/decision-history`
```

## Scope Options
- `--scope=current-task`: Current task context only
- `--scope=sprint`: Current sprint context (default)
- `--scope=project`: Full project context

## Parameters
- `--include-context`: Include full conversation context in memory

## Memory Categories
- **Technical Decisions**: Architecture and implementation choices
- **Code Patterns**: Reusable code solutions and approaches
- **Integration Examples**: Working integration configurations
- **Troubleshooting Solutions**: Problem-solution pairs
- **Configuration Examples**: Working configuration setups
- **Performance Insights**: Performance optimization discoveries
- **Security Considerations**: Security-related learnings

## MCP Servers Used
- **Crawl4ai-rag**: Knowledge base storage and enhancement
- **Filesystem MCP**: Project memory file management
- **AI-Server-Sequential-thinking**: Context analysis and pattern recognition
- **Analysis Tool**: Memory statistics and relationship analysis
