# Research Deep Command

Comprehensive research using all relevant MCP servers for thorough topic analysis.

## Usage
```
/research-deep <topic> [--scope=basic|comprehensive|expert]
```

## Description
Conducts thorough research on any topic using multiple MCP servers, validates information across sources, and stores findings in the knowledge base.

## Implementation
1. **Topic Analysis**: Break down research topic into components
2. **Multi-Source Research**: Query all relevant MCP servers
3. **Information Synthesis**: Combine and validate findings
4. **Knowledge Storage**: Store results in Crawl4ai-rag
5. **Source Verification**: Cross-reference information quality
6. **Gap Identification**: Identify areas needing additional research

## Output Format
```
🔬 Deep Research: {topic}
==========================

📊 Research Summary:
- Sources Consulted: {count}
- Confidence Level: {high/medium/low}
- Last Updated: {timestamp}
- Verification Status: {verified/partial/needs_review}

📚 Key Findings:

## Microsoft Documentation:
{official_microsoft_findings}

## Latest SDK Information:
{context7_findings}

## Community Best Practices:
{web_search_findings}

## Code Examples & Patterns:
{crawl4ai_findings}

## Azure-Specific Considerations:
{azure_mcp_findings}

🔗 Source References:
{numbered_list_of_sources}

⚠️ Important Considerations:
{warnings_limitations_gotchas}

💡 Recommended Implementation:
{step_by_step_recommendations}

🎯 Next Actions:
{suggested_next_steps}

📝 Knowledge Base Updated:
- Added {count} new entries
- Updated {count} existing entries
- Created {count} new patterns
```

## Parameters
- `--scope=basic`: Essential information only
- `--scope=comprehensive`: Detailed analysis (default)
- `--scope=expert`: Deep technical details and edge cases

## MCP Servers Used
- **Microsoft Docs MCP**: Official documentation
- **Context7 MCP**: SDK and library information
- **Brave Search MCP**: Community practices and recent updates
- **Azure-mcp MCP**: Azure-specific tools and services
- **Crawl4ai-rag**: Pattern storage and retrieval
- **AI-Server-Sequential-thinking**: Information synthesis
