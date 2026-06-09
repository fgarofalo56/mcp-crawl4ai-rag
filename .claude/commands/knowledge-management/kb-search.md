# Knowledge Base Search Command

Search knowledge base with context and semantic matching.

## Usage
```
/kb-search <query> [--type=semantic|keyword|hybrid] [--limit=5] [--min-relevance=70]
```

## Description
Performs intelligent search through the knowledge base using semantic matching, keyword search, or hybrid approaches.

## Implementation
1. **Query Analysis**: Parse and understand search intent
2. **Search Strategy**: Choose optimal search approach
3. **Semantic Matching**: Use AI-powered semantic similarity
4. **Keyword Matching**: Traditional keyword-based search
5. **Result Ranking**: Rank by relevance, recency, and usage
6. **Context Enhancement**: Provide related content and suggestions

## Output Format
```
🔍 Knowledge Base Search: "{query}"
===================================

📊 Search Results:
- Total Matches: {count}
- Search Type: {semantic/keyword/hybrid}
- Min Relevance: {min_relevance}%
- Search Time: {duration}ms

🎯 Relevant Entries:

## 1. {entry_title}
- Relevance: {percentage}%
- Type: {content_type}
- Last Updated: {date}
- Tags: {tags}
- Summary: {brief_summary}
- Source: {source_reference}

## 2. {entry_title}
- Relevance: {percentage}%
- Type: {content_type}
- Last Updated: {date}
- Tags: {tags}
- Summary: {brief_summary}
- Source: {source_reference}

## 3. {entry_title}
- Relevance: {percentage}%
- Type: {content_type}
- Last Updated: {date}
- Tags: {tags}
- Summary: {brief_summary}
- Source: {source_reference}

🔗 Related Concepts:
{semantically_related_topics}

💡 Suggested Follow-up Searches:
- {related_search_1}
- {related_search_2}
- {related_search_3}

📊 Search Analytics:
- Popular queries: {popular_queries}
- Knowledge base coverage: {coverage_areas}
- Recent additions: {recent_additions}

🎯 Quick Actions:
- Get full content: `/kb-fetch {entry_id}`
- Add new entry: `/kb-add-research`
- Update existing: `/kb-update {entry_id}`
```

## Search Types
- `--type=semantic`: AI-powered semantic search (default)
- `--type=keyword`: Traditional keyword matching
- `--type=hybrid`: Combination of semantic and keyword

## Parameters
- `--limit=5`: Number of results to return (1-20)
- `--min-relevance=70`: Minimum relevance percentage (0-100)

## MCP Servers Used
- **Crawl4ai-rag**: Primary search and RAG functionality
- **AI-Server-Sequential-thinking**: Query understanding and semantic analysis
- **Analysis Tool**: Search performance and analytics
