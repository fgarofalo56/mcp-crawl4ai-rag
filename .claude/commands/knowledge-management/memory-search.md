# Memory Search Command

Search past work and references in the knowledge base and project memory.

## Usage
```
/memory-search <keywords> [--category=all|solution|pattern|config|troubleshooting|decision|research|integration] [--limit=10]
```

## Description
Searches through the project knowledge base and memory system to find relevant past work, solutions, and patterns.

## Implementation
1. **Query Processing**: Parse search keywords and categories
2. **Knowledge Base Search**: Search Crawl4ai-rag with semantic matching
3. **Project Memory Search**: Search project tracking memory files
4. **Relevance Ranking**: Rank results by relevance and recency
5. **Context Enhancement**: Provide related memories and cross-references
6. **Quick Access**: Provide direct links to detailed information

## Output Format
```
🔍 Memory Search Results: "{keywords}"
=====================================

📊 Search Summary:
- Total Results Found: {count}
- Knowledge Base Hits: {kb_count}
- Project Memory Hits: {pm_count}
- Search Categories: {categories}
- Search Time: {duration}ms

🎯 Top Results:

## 1. {result_title} ({category})
- Relevance: {percentage}%
- Created: {date}
- Tags: {tags}
- Summary: {brief_summary}
- Quick Access: `/memory-load {memory_id}`

## 2. {result_title} ({category})
- Relevance: {percentage}%
- Created: {date}
- Tags: {tags}
- Summary: {brief_summary}
- Quick Access: `/memory-load {memory_id}`

## 3. {result_title} ({category})
- Relevance: {percentage}%
- Created: {date}
- Tags: {tags}
- Summary: {brief_summary}
- Quick Access: `/memory-load {memory_id}`

🔗 Related Searches:
- {related_keyword_1}
- {related_keyword_2}
- {related_keyword_3}

📈 Popular Tags:
{tag_cloud_representation}

💡 Suggestions:
- Refine search with: `/memory-search {refined_keywords}`
- Browse category: `/memory-browse {category}`
- Add new memory: `/memory-store {category}`

📊 Search Analytics:
- Most searched terms: {popular_terms}
- Your recent searches: {recent_searches}
- Knowledge base growth: {growth_trend}
```

## Category Filters
- `all`: Search all categories (default)
- `solution`: Problem-solution pairs only
- `pattern`: Code/architecture patterns only
- `config`: Configuration examples only
- `troubleshooting`: Issue resolution steps only
- `decision`: Architecture decisions only
- `research`: Research findings only
- `integration`: Integration examples only

## Search Tips
- Use specific technical terms for better results
- Combine multiple keywords with spaces
- Use category filters to narrow results
- Check related searches for broader exploration

## MCP Servers Used
- **Crawl4ai-rag**: Primary knowledge base search with semantic matching
- **Filesystem MCP**: Project memory file search
- **AI-Server-Sequential-thinking**: Query processing and relevance ranking
- **Analysis Tool**: Search analytics and performance metrics
