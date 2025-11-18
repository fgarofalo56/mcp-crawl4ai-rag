# Knowledge Base Add Research Command

Add current research findings to the Crawl4ai-rag knowledge base with proper categorization.

## Usage
```
/kb-add-research [--source=current|url|file] [--category=auto|docs|code|pattern]
```

## Description
Processes and adds research findings, documentation, code examples, and patterns to the knowledge base with proper metadata and search optimization.

## Implementation
1. **Content Analysis**: Analyze research content and extract key information
2. **Categorization**: Automatically categorize content type and relevance
3. **Metadata Extraction**: Extract keywords, topics, and relationships
4. **Quality Assessment**: Validate information quality and accuracy
5. **Storage Optimization**: Store with optimal search and retrieval tags
6. **Cross-Linking**: Link to related existing knowledge base entries

## Output Format
```
📚 Research Added to Knowledge Base
===================================

📊 Content Analysis:
- Content Type: {documentation/code/pattern/tutorial}
- Source Quality: {high/medium/low}
- Relevance Score: {percentage}%
- Language/Technology: {detected_tech}
- Estimated Reading Time: {minutes} min

🏷️ Auto-Generated Tags:
{list_of_extracted_tags}

📂 Categorization:
- Primary Category: {category}
- Secondary Categories: {subcategories}
- Technology Stack: {technologies}
- Complexity Level: {beginner/intermediate/advanced}

🔗 Knowledge Base Integration:
- Entry ID: {unique_id}
- Related Entries: {count} found
- Cross-References: {count} created
- Search Optimization: ✅ Complete

💡 Key Insights Extracted:
{bullet_list_of_insights}

🎯 Recommended Applications:
{use_cases_and_applications}

📈 Knowledge Base Stats:
- Total Entries: {count}
- New Entries Today: {count}
- Most Active Categories: {categories}

🔍 Quick Search Examples:
- `/memory-search {keyword1}`
- `/memory-search {keyword2} {keyword3}`
```

## Source Options
- `--source=current`: Use current conversation context (default)
- `--source=url`: Crawl and add from URL
- `--source=file`: Add from local file

## Category Options
- `--category=auto`: Automatic categorization (default)
- `--category=docs`: Force documentation category
- `--category=code`: Force code example category
- `--category=pattern`: Force pattern category

## MCP Servers Used
- **Crawl4ai-rag**: Primary knowledge storage and RAG functionality
- **Microsoft Docs MCP**: Documentation validation and cross-referencing
- **Context7 MCP**: SDK and library context validation
- **AI-Server-Sequential-thinking**: Content analysis and categorization
- **Analysis Tool**: Quality assessment and statistics
