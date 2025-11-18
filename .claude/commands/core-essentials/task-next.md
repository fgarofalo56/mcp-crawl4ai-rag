# Task Next Command

Get the next highest priority task with comprehensive research preparation.

## Usage
```
/task-next [filter_by_label]
```

## Description
Identifies and prepares the next highest priority task, including all necessary research, context, and validation setup.

## Implementation
1. **Priority Analysis**: Find highest `task_order` task with status "todo"
2. **Context Gathering**: Collect related tasks, dependencies, and history
3. **Research Preparation**: Pre-load relevant documentation and examples
4. **MCP Setup**: Prepare all relevant MCP servers for the task type
5. **Knowledge Base Search**: Find related past work and patterns

## Output Format
```
🎯 Next Priority Task
====================

📝 Task Details:
- ID: {task_id}
- Title: {task_title}
- Priority: {task_order}
- Estimated Time: {hours}
- Labels: {labels}
- Assigned Sprint: {sprint}

📋 Description:
{task_description}

✅ Acceptance Criteria:
{acceptance_criteria_list}

🔗 Dependencies:
{dependency_tasks}

📚 Pre-Research Completed:
- Microsoft Docs: {relevant_docs}
- Context7: {sdk_versions}
- Knowledge Base: {related_patterns}
- Code Examples: {example_links}

🛠️ Recommended Approach:
{suggested_implementation_steps}

🔍 MCP Servers Ready:
{list_of_prepared_mcp_servers}

⚠️ Potential Risks:
{identified_risks}

🎯 Ready to start? Type 'yes' to begin implementation.
```

## MCP Servers Used
- **Filesystem MCP**: Task file analysis
- **Microsoft Docs MCP**: Relevant documentation lookup
- **Context7 MCP**: SDK version preparation
- **Crawl4ai-rag**: Pattern and example search
- **AI-Server-Sequential-thinking**: Implementation strategy
