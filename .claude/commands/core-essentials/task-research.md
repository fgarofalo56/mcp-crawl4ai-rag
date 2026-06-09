# Task Research Command

Deep research for specific task using all relevant MCP servers.

## Usage
```
/task-research <task_id> [--depth=surface|deep|expert] [--store-findings]
```

## Description
Conducts comprehensive research for a specific task, gathering all relevant information and preparing for implementation.

## Implementation
1. **Task Analysis**: Analyze task requirements and scope
2. **Research Strategy**: Determine research approach based on task type
3. **Multi-MCP Research**: Query relevant MCP servers
4. **Context Integration**: Integrate with existing project context
5. **Implementation Planning**: Create research-informed implementation plan
6. **Knowledge Storage**: Store findings for team access

## Output Format
```
🔬 Task Research: {task_title}
===============================

📋 Task Context:
- Task ID: {task_id}
- Priority: {priority}
- Sprint: {sprint}
- Estimated Effort: {hours} hours
- Dependencies: {dependencies}

🎯 Research Scope:
- Depth Level: {depth}
- Focus Areas: {focus_areas}
- Technology Stack: {tech_stack}
- Integration Points: {integrations}

📚 Research Findings:

## Microsoft Documentation Research:
{microsoft_docs_findings}

## SDK and Library Research:
{context7_findings}

## Community Best Practices:
{community_research}

## Azure-Specific Research:
{azure_research}

## Existing Pattern Analysis:
{pattern_analysis}

## Code Examples Found:
{code_examples}

🏗️ Implementation Strategy:

## Recommended Approach:
{recommended_approach}

## Architecture Considerations:
{architecture_notes}

## Security Considerations:
{security_notes}

## Performance Considerations:
{performance_notes}

## Testing Strategy:
{testing_approach}

⚠️ Risks and Considerations:
{identified_risks}

💡 Alternative Approaches:
{alternative_options}

🛠️ Required Tools and Resources:
{tools_and_resources}

📖 Reference Documentation:
{reference_links}

🎯 Implementation Plan:
1. {step_1}
2. {step_2}
3. {step_3}
...

📊 Research Quality Metrics:
- Sources Consulted: {source_count}
- Confidence Level: {confidence}%
- Completeness: {completeness}%
- Validation Status: {validation_status}

💾 Knowledge Base Integration:
- New entries created: {new_entries}
- Existing entries updated: {updated_entries}
- Cross-references added: {cross_refs}

🎯 Ready for Implementation:
Research complete. Use `/task-next` to begin implementation.
```

## Depth Levels
- `--depth=surface`: Basic research for straightforward tasks
- `--depth=deep`: Comprehensive research (default)
- `--depth=expert`: Deep technical research for complex tasks

## MCP Servers Used
- **Microsoft Docs MCP**: Official documentation and best practices
- **Context7 MCP**: SDK versions and API documentation
- **Brave Search MCP**: Community solutions and recent developments
- **Azure-mcp MCP**: Azure-specific tools and configurations
- **Crawl4ai-rag**: Existing patterns and solutions
- **Serena MCP**: Code analysis and examples
- **AI-Server-Sequential-thinking**: Implementation planning
