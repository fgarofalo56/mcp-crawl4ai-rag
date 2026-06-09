# Memory Store Command

Store important findings and patterns in the project knowledge base for future reference.

## Usage
```
/memory-store <category> [--title="Custom Title"] [--tags="tag1,tag2"]
```

## Description
Captures and stores current work context, findings, solutions, and patterns in the knowledge base for future reference and team knowledge sharing.

## Categories
- `solution`: Problem-solution pairs
- `pattern`: Reusable code/architecture patterns
- `config`: Configuration examples and settings
- `troubleshooting`: Issue resolution steps
- `decision`: Architecture decision records
- `research`: Research findings and conclusions
- `integration`: Integration examples and gotchas

## Implementation
1. **Context Capture**: Gather current work context and findings
2. **Information Structure**: Organize information for future retrieval
3. **Knowledge Base Storage**: Store in Crawl4ai-rag with metadata
4. **Project Tracking**: Update project memory files
5. **Cross-Reference Creation**: Link to related memories and tasks
6. **Future Search Optimization**: Add searchable keywords and tags

## Output Format
```
🧠 Memory Stored Successfully
=============================

📝 Memory Details:
- ID: {unique_id}
- Category: {category}
- Title: {title}
- Created: {timestamp}
- Tags: {tags}
- Related Tasks: {task_ids}

💾 Storage Locations:
- Knowledge Base: ✅ Stored in Crawl4ai-rag
- Project Tracking: ✅ Added to project_tracking/memory/
- Cross-References: ✅ Linked to {count} related items

🔍 Searchable Keywords:
{extracted_keywords}

🔗 Related Memories:
{list_of_related_memories}

💡 Quick Access:
Use `/memory-search {keywords}` to find this memory later

📊 Memory Statistics:
- Total Memories: {count}
- Category Count: {count}
- Most Used Tags: {top_tags}
```

## Examples
```bash
# Store a troubleshooting solution
/memory-store troubleshooting --title="Azure OpenAI 429 Rate Limit Fix" --tags="azure,openai,rate-limit"

# Store an architecture decision
/memory-store decision --title="Chose Semantic Kernel over AutoGen" --tags="architecture,ai,framework"

# Store a useful code pattern
/memory-store pattern --title="Azure Auth with Managed Identity" --tags="azure,authentication,pattern"
```

## MCP Servers Used
- **Crawl4ai-rag**: Primary knowledge storage
- **Filesystem MCP**: Project tracking file management
- **AI-Server-Sequential-thinking**: Content organization and keyword extraction
- **Analysis Tool**: Memory statistics and relationship analysis
