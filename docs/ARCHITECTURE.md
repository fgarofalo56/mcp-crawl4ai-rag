# 🏗️ Crawl4AI RAG MCP Server - architecture documentation

> **🏠 [Home](../README.md)** | **📖 [Documentation](README.md)** | **👤 Architecture**

---

**Version**: 2.0.0
**Last Updated**: October 28, 2025
**Author**: Technical Documentation Team

**⚠️ Major Architecture Change**: This document has been updated to reflect the v2.0.0 modular refactoring where the monolithic `crawl4ai_mcp.py` (2000+ lines) was split into organized modules under `src/core/` and `src/tools/`.

## Table of contents

1. [System architecture overview](#1-system-architecture-diagram)
2. [Data flow architecture](#2-data-flow-diagram)
3. [Component relationships](#3-component-relationship-diagram)
4. [MCP tool flow](#4-mcp-tool-flow-diagram)
5. [Legend and conventions](#legend-and-conventions)
6. [Architectural insights](#architectural-insights)

---

## 1. System architecture diagram

This high-level C4-style diagram shows the major components and their relationships within the Crawl4AI RAG MCP Server ecosystem.

```mermaid
graph TB
    subgraph "Client Layer"
        Claude[Claude Desktop]
        Windsurf[Windsurf IDE]
        N8N[n8n Workflows]
        Other[Other MCP Clients]
    end

    subgraph "MCP Server Layer"
        FastMCP[FastMCP Framework<br/>v2.12.4]

        subgraph "Core Infrastructure"
            Server[server.py<br/>Main Entry Point]
            Lifespan[core/lifespan.py<br/>Lifecycle Management]
            Context[core/context.py<br/>Crawl4AIContext]
            BrowserValidation[core/browser_validation.py<br/>Playwright Checks]
        end

        subgraph "Tool Modules (16 MCP Tools)"
            CrawlTools[tools/crawling_tools.py<br/>5 Crawling Tools]
            RAGTools[tools/rag_tools.py<br/>2 RAG Query Tools]
            GraphRAGTools[tools/graphrag_tools.py<br/>4 GraphRAG Tools]
            SourceTools[tools/source_tools.py<br/>1 Source Tool]
            KGTools[tools/knowledge_graph_tools.py<br/>4 KG Tools]
        end

        subgraph "Utilities & Helpers"
            Utils[utils.py<br/>Core Utilities]
            RAGUtils[rag_utils.py<br/>RAG Functions]
            SearchUtils[search_utils.py<br/>Search Functions]
            CrawlUtils[crawling_utils.py<br/>Crawl Helpers]
            InitUtils[initialization_utils.py<br/>Startup Logic]
        end

        subgraph "Knowledge Graph Services"
            AIDetector[knowledge_graphs/<br/>ai_hallucination_detector.py]
            RepoParser[knowledge_graphs/<br/>parse_repo_into_neo4j.py]
            DocExtractor[knowledge_graphs/<br/>document_entity_extractor.py]
            GraphValidator[knowledge_graphs/<br/>document_graph_validator.py]
        end
    end

    subgraph "Crawler Layer"
        Crawl4AI[Crawl4AI v0.7.4<br/>Web Crawler]

        subgraph "Crawler Modes"
            Standard[Standard Mode<br/>Headless Browser]
            Stealth[Stealth Mode<br/>Undetected Browser]
            Memory[Memory Monitored<br/>Adaptive Throttling]
            MultiURL[Multi-URL Config<br/>Smart Optimization]
        end
    end

    subgraph "External Services"
        subgraph "Vector Database"
            Supabase[(Supabase<br/>PostgreSQL + pgvector)]
            PagesTable[(crawled_pages<br/>Table)]
            CodeTable[(code_examples<br/>Table)]
            SourcesTable[(sources<br/>Table)]
        end

        subgraph "Knowledge Graph"
            Neo4j[(Neo4j Graph DB)]
            Repos[Repository Nodes]
            Classes[Class Nodes]
            Methods[Method Nodes]
        end

        subgraph "AI Services"
            OpenAI[OpenAI/Azure OpenAI]
            Embeddings[text-embedding-3-small<br/>Embeddings]
            LLM[GPT-4 Models<br/>Summaries & Context]
            Reranker[CrossEncoder<br/>ms-marco-MiniLM-L-6-v2]
        end
    end

    %% Client connections
    Claude --> FastMCP
    Windsurf --> FastMCP
    N8N --> FastMCP
    Other --> FastMCP

    %% FastMCP to Core Infrastructure
    FastMCP --> Server
    Server --> Lifespan
    Server --> Context
    Lifespan --> BrowserValidation

    %% Server to Tool Modules
    Server --> CrawlTools
    Server --> RAGTools
    Server --> GraphRAGTools
    Server --> SourceTools
    Server --> KGTools

    %% Tool Modules to Utilities
    CrawlTools --> Utils
    CrawlTools --> CrawlUtils
    RAGTools --> Utils
    RAGTools --> RAGUtils
    RAGTools --> SearchUtils
    GraphRAGTools --> Utils
    GraphRAGTools --> RAGUtils
    SourceTools --> Utils
    KGTools --> Utils

    %% Lifespan initializes services
    Lifespan --> InitUtils
    InitUtils --> Supabase
    InitUtils --> Neo4j
    InitUtils --> OpenAI

    %% Tool Modules to Knowledge Graph Services
    KGTools --> AIDetector
    KGTools --> RepoParser
    GraphRAGTools --> DocExtractor
    GraphRAGTools --> GraphValidator

    %% Crawler connections
    CrawlTools --> Crawl4AI
    Crawl4AI --> Standard
    Crawl4AI --> Stealth
    Crawl4AI --> Memory
    Crawl4AI --> MultiURL

    %% Data storage connections
    Utils --> Supabase
    Supabase --> PagesTable
    Supabase --> CodeTable
    Supabase --> SourcesTable

    RepoParser --> Neo4j
    AIDetector --> Neo4j
    DocExtractor --> Neo4j
    GraphValidator --> Neo4j
    Neo4j --> Repos
    Neo4j --> Classes
    Neo4j --> Methods

    %% AI service connections
    Utils --> OpenAI
    OpenAI --> Embeddings
    OpenAI --> LLM
    Utils --> Reranker

    %% Styling
    classDef clientClass fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef mcpClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef crawlerClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef storageClass fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef aiClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class Claude,Windsurf,N8N,Other clientClass
    class FastMCP,Server,Lifespan,Context,BrowserValidation mcpClass
    class CrawlTools,RAGTools,GraphRAGTools,SourceTools,KGTools mcpClass
    class Utils,RAGUtils,SearchUtils,CrawlUtils,InitUtils mcpClass
    class AIDetector,RepoParser,DocExtractor,GraphValidator mcpClass
    class Crawl4AI,Standard,Stealth,Memory,MultiURL crawlerClass
    class Supabase,PagesTable,CodeTable,SourcesTable,Neo4j,Repos,Classes,Methods storageClass
    class OpenAI,Embeddings,LLM,Reranker aiClass
```

### Description

The system follows a **modular layered architecture** with clear separation of concerns:

- **Client Layer**: Multiple MCP clients connect via stdio or SSE transport
- **MCP Server Layer**: Organized into four logical groups:
  - **Core Infrastructure**: Entry point (server.py), lifecycle management (lifespan.py), context, browser validation
  - **Tool Modules**: 16 tools organized across 5 category modules (crawling, RAG, GraphRAG, source, knowledge graph)
  - **Utilities & Helpers**: Shared functions grouped by purpose (utils.py, rag_utils.py, search_utils.py, etc.)
  - **Knowledge Graph Services**: Independent modules in knowledge_graphs/ directory
- **Crawler Layer**: Crawl4AI with 4 specialized modes (standard, stealth, memory-monitored, multi-URL)
- **External Services**: Three distinct service categories (vector DB, knowledge graph, AI services)

**Key Design Decisions (v2.0.0 Refactoring)**:
- **Modular Tool Organization**: Tools grouped by category in separate files instead of one monolithic file
- **Core/Tools Separation**: Core infrastructure (lifespan, context) separated from tool implementations
- **Utility Categorization**: Utilities split by purpose (RAG, search, crawling, initialization) for maintainability
- **Independent Knowledge Graph**: knowledge_graphs/ directory is self-contained and can be tested independently
- **Feature Flags Preserved**: Environment flags (USE_*) still control optional features
- **Lazy Loading**: Knowledge graph tools are conditionally imported to support testing without Neo4j

---

## 2. Data flow diagram

This diagram illustrates the complete data flow for all major operations in the system.

```mermaid
flowchart TD
    Start([User Request via MCP])

    subgraph "1. Web Crawling Process"
        Input1[URL Input]
        Detect{URL Type?}

        Sitemap[Sitemap XML]
        Webpage[Regular Page]
        TextFile[.txt File]

        ExtractURLs[Extract URLs<br/>from Sitemap]
        RecursiveCrawl[Recursive Crawl<br/>Internal Links]
        DirectFetch[Direct Fetch<br/>Content]

        Parallel[Parallel Crawling<br/>MemoryAdaptiveDispatcher]

        MarkdownOut[Markdown Content]
        SmartChunk[Smart Chunking<br/>By Headers/Code Blocks]

        Chunks[Content Chunks<br/>~5000 chars each]
    end

    subgraph "2. Contextual Embedding Optional"
        ContextCheck{USE_CONTEXTUAL_<br/>EMBEDDINGS?}
        GenContext[Generate Context<br/>LLM: Full Doc + Chunk]
        ContextualText[Chunk + Context]
        OriginalText[Original Chunk]
    end

    subgraph "3. Vector Storage"
        CreateEmbed[Create Embeddings<br/>OpenAI API]
        Embedding[1536-dim Vector]

        ExtractMeta[Extract Metadata<br/>Headers, Stats, Source]

        StoreSupabase[(Store in Supabase<br/>crawled_pages)]
    end

    subgraph "4. Code Example Extraction Optional"
        CodeCheck{USE_AGENTIC_<br/>RAG?}
        ExtractCode[Extract Code Blocks<br/>&ge;1000 chars]
        SummarizeCode[Summarize Code<br/>LLM: Code + Context]
        StoreCode[(Store in Supabase<br/>code_examples)]
    end

    subgraph "5. Source Management"
        ExtractSource[Extract Source ID<br/>from URL Domain]
        GenSummary[Generate Summary<br/>LLM: First 5000 chars]
        UpdateSource[(Update sources<br/>Table)]
    end

    subgraph "6. RAG Query Process"
        QueryInput[Search Query]

        SearchMode{HYBRID_<br/>SEARCH?}

        VectorSearch[Vector Similarity<br/>Search]
        KeywordSearch[Keyword ILIKE<br/>Search]
        CombineResults[Combine Results<br/>Boost Overlaps]

        RerankCheck{USE_<br/>RERANKING?}
        Rerank[CrossEncoder<br/>Rerank by Relevance]

        Results[Formatted Results<br/>with Scores]
    end

    subgraph "7. Knowledge Graph Indexing"
        RepoURL[GitHub Repo URL]
        CloneRepo[Clone Repository]
        ASTAnalysis[AST Parse<br/>Python Files]

        ExtractNodes[Extract Nodes<br/>Classes, Methods, Functions]
        CreateGraph[(Store in Neo4j<br/>Knowledge Graph)]
    end

    subgraph "8. Hallucination Detection"
        ScriptInput[AI-Generated Script]
        ParseScript[AST Parse<br/>Imports, Calls, Classes]

        ValidateKG[Validate Against<br/>Knowledge Graph]

        CompareImports{Imports<br/>Exist?}
        CompareMethods{Methods<br/>Valid?}
        CompareParams{Parameters<br/>Match?}

        CalcConfidence[Calculate<br/>Confidence Score]
        GenReport[Generate Report<br/>Hallucinations + Fixes]
    end

    %% Flow 1: Web Crawling
    Start --> Input1
    Input1 --> Detect

    Detect -->|Sitemap| Sitemap
    Detect -->|Webpage| Webpage
    Detect -->|.txt| TextFile

    Sitemap --> ExtractURLs --> Parallel
    Webpage --> RecursiveCrawl --> Parallel
    TextFile --> DirectFetch --> MarkdownOut

    Parallel --> MarkdownOut
    MarkdownOut --> SmartChunk --> Chunks

    %% Flow 2: Contextual Embedding
    Chunks --> ContextCheck
    ContextCheck -->|Yes| GenContext --> ContextualText
    ContextCheck -->|No| OriginalText

    %% Flow 3: Vector Storage
    ContextualText --> CreateEmbed
    OriginalText --> CreateEmbed
    CreateEmbed --> Embedding

    Chunks --> ExtractMeta
    Embedding --> StoreSupabase
    ExtractMeta --> StoreSupabase

    %% Flow 4: Code Examples
    Chunks --> CodeCheck
    CodeCheck -->|Yes| ExtractCode --> SummarizeCode --> StoreCode
    CodeCheck -->|No| End1[Skip Code Extraction]

    %% Flow 5: Source Management
    Chunks --> ExtractSource --> GenSummary --> UpdateSource

    %% Flow 6: RAG Query
    Start --> QueryInput --> SearchMode

    SearchMode -->|Yes| VectorSearch
    SearchMode -->|Yes| KeywordSearch
    VectorSearch --> CombineResults
    KeywordSearch --> CombineResults

    SearchMode -->|No| VectorSearch
    VectorSearch --> RerankCheck
    CombineResults --> RerankCheck

    RerankCheck -->|Yes| Rerank --> Results
    RerankCheck -->|No| Results

    %% Flow 7: Knowledge Graph
    Start --> RepoURL --> CloneRepo --> ASTAnalysis --> ExtractNodes --> CreateGraph

    %% Flow 8: Hallucination Detection
    Start --> ScriptInput --> ParseScript --> ValidateKG

    ValidateKG --> CompareImports
    ValidateKG --> CompareMethods
    ValidateKG --> CompareParams

    CompareImports --> CalcConfidence
    CompareMethods --> CalcConfidence
    CompareParams --> CalcConfidence

    CalcConfidence --> GenReport

    %% Styling
    classDef crawlClass fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef embedClass fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef storageClass fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef queryClass fill:#f8bbd0,stroke:#c2185b,stroke-width:2px
    classDef kgClass fill:#d1c4e9,stroke:#512da8,stroke-width:2px

    class Input1,Detect,Sitemap,Webpage,TextFile,ExtractURLs,RecursiveCrawl,DirectFetch,Parallel,MarkdownOut,SmartChunk,Chunks crawlClass
    class ContextCheck,GenContext,ContextualText,OriginalText,CreateEmbed,Embedding embedClass
    class ExtractMeta,StoreSupabase,CodeCheck,ExtractCode,SummarizeCode,StoreCode,ExtractSource,GenSummary,UpdateSource storageClass
    class QueryInput,SearchMode,VectorSearch,KeywordSearch,CombineResults,RerankCheck,Rerank,Results queryClass
    class RepoURL,CloneRepo,ASTAnalysis,ExtractNodes,CreateGraph,ScriptInput,ParseScript,ValidateKG,CompareImports,CompareMethods,CompareParams,CalcConfidence,GenReport kgClass
```

### Description

The data flow diagram shows **8 distinct processes**:

1. **Web Crawling**: Smart URL detection → content extraction → chunking
2. **Contextual Embedding**: Optional LLM-powered context enrichment
3. **Vector Storage**: Embedding generation → metadata extraction → Supabase storage
4. **Code Example Extraction**: Optional code-specific RAG with summaries
5. **Source Management**: Domain-level summaries and statistics
6. **RAG Query**: Hybrid search → optional reranking → formatted results
7. **Knowledge Graph Indexing**: Repository cloning → AST parsing → Neo4j storage
8. **Hallucination Detection**: Script parsing → graph validation → confidence scoring

**Key Patterns**:
- Conditional flows based on environment flags (USE_*)
- Parallel processing for batch operations
- Fallback mechanisms for API failures
- Multi-stage validation in hallucination detection

---

## 3. Component relationship diagram

**⚠️ NOTE**: This diagram reflects the v1.x architecture with monolithic `crawl4ai_mcp.py`. The v2.0.0 modular structure is described in the text above and in Section 1. This diagram will be updated in a future documentation revision.

This class-like diagram shows how the major code modules interact with each other.

```mermaid
classDiagram
    class FastMCP {
        +FastMCP server
        +lifespan: crawl4ai_lifespan
        +tool() decorator
        +run_http_async()
        +run_stdio_async()
    }

    class crawl4ai_mcp {
        +11 MCP Tools
        +AsyncWebCrawler crawler
        +Client supabase_client
        +CrossEncoder reranking_model
        +KnowledgeGraphValidator validator
        +DirectNeo4jExtractor repo_extractor
        ---
        +crawl_single_page()
        +smart_crawl_url()
        +crawl_with_stealth_mode()
        +crawl_with_multi_url_config()
        +crawl_with_memory_monitoring()
        +get_available_sources()
        +perform_rag_query()
        +search_code_examples()
        +parse_github_repository()
        +check_ai_script_hallucinations()
        +query_knowledge_graph()
        ---
        Helper Methods:
        +rerank_results()
        +is_sitemap()
        +parse_sitemap()
        +smart_chunk_markdown()
        +extract_section_info()
        +crawl_batch()
        +crawl_recursive_internal_links()
    }

    class utils {
        +AzureOpenAI client
        ---
        RAG Functions:
        +get_supabase_client()
        +create_embeddings_batch()
        +create_embedding()
        +search_documents()
        +search_code_examples()
        ---
        Document Processing:
        +add_documents_to_supabase()
        +generate_contextual_embedding()
        +smart_chunk_markdown()
        +extract_section_info()
        ---
        Code Processing:
        +extract_code_blocks()
        +generate_code_example_summary()
        +add_code_examples_to_supabase()
        ---
        Source Management:
        +update_source_info()
        +extract_source_summary()
    }

    class Crawl4AI {
        +AsyncWebCrawler
        +BrowserConfig
        +CrawlerRunConfig
        +CacheMode
        +MemoryAdaptiveDispatcher
        ---
        +arun() single page
        +arun_many() batch
        +browser_type: undetected
        +simulate_user: bool
        +override_navigator: bool
    }

    class Supabase {
        +Client
        ---
        Tables:
        +crawled_pages
        +code_examples
        +sources
        ---
        RPC Functions:
        +match_crawled_pages()
        +match_code_examples()
        ---
        +insert()
        +select()
        +delete()
        +eq() filter
        +in_() filter
    }

    class OpenAI {
        +AzureOpenAI client
        ---
        +embeddings.create()
        +chat.completions.create()
        ---
        Models:
        +text-embedding-3-small
        +gpt-4-nano (summaries)
        +gpt-4 (context)
    }

    class Neo4j {
        +Driver
        +AsyncSession
        ---
        Nodes:
        +Repository
        +File
        +Class
        +Method
        +Function
        +Attribute
        ---
        Relationships:
        +CONTAINS
        +DEFINES
        +HAS_METHOD
        +HAS_ATTRIBUTE
    }

    class KnowledgeGraphValidator {
        +Neo4jDriver driver
        ---
        +initialize()
        +validate_script()
        +validate_import()
        +validate_method_call()
        +validate_class_instantiation()
        +calculate_confidence()
        +close()
    }

    class DirectNeo4jExtractor {
        +Neo4jDriver driver
        ---
        +initialize()
        +analyze_repository()
        +clone_repository()
        +extract_python_files()
        +parse_file_ast()
        +store_in_neo4j()
        +close()
    }

    class AIScriptAnalyzer {
        +ast module
        ---
        +analyze_script()
        +extract_imports()
        +extract_classes()
        +extract_method_calls()
        +extract_function_calls()
        +extract_attributes()
        +build_analysis_result()
    }

    class HallucinationReporter {
        +generate_comprehensive_report()
        +format_validation_summary()
        +format_hallucinations()
        +generate_recommendations()
        +format_metadata()
    }

    class CrossEncoder {
        +model: ms-marco-MiniLM-L-6-v2
        ---
        +predict(pairs)
        +score(query, documents)
        ---
        Used for:
        +Result reranking
        +Relevance scoring
    }

    class Config {
        +load_dotenv()
        +environment variables
        ---
        Flags:
        +USE_CONTEXTUAL_EMBEDDINGS
        +USE_HYBRID_SEARCH
        +USE_AGENTIC_RAG
        +USE_RERANKING
        +USE_KNOWLEDGE_GRAPH
    }

    class Validators {
        +validate_neo4j_connection()
        +validate_script_path()
        +validate_github_url()
        +format_neo4j_error()
    }

    class ErrorHandlers {
        +format_error_response()
        +handle_crawl_error()
        +handle_db_error()
        +log_error()
    }

    %% Relationships
    FastMCP <|-- crawl4ai_mcp : framework

    crawl4ai_mcp --> utils : uses for RAG
    crawl4ai_mcp --> Crawl4AI : crawls with
    crawl4ai_mcp --> Supabase : stores in
    crawl4ai_mcp --> Neo4j : graphs in
    crawl4ai_mcp --> KnowledgeGraphValidator : validates with
    crawl4ai_mcp --> DirectNeo4jExtractor : extracts with
    crawl4ai_mcp --> Config : configured by
    crawl4ai_mcp --> Validators : validated by
    crawl4ai_mcp --> ErrorHandlers : errors via

    utils --> OpenAI : embeds with
    utils --> Supabase : stores in
    utils --> CrossEncoder : reranks with

    KnowledgeGraphValidator --> Neo4j : queries
    KnowledgeGraphValidator --> AIScriptAnalyzer : analyzes with
    KnowledgeGraphValidator --> HallucinationReporter : reports with

    DirectNeo4jExtractor --> Neo4j : writes to
    DirectNeo4jExtractor --> AIScriptAnalyzer : parses with
```

### Description

The component relationship diagram reveals the **modular architecture**:

**Core Dependencies**:
- `crawl4ai_mcp.py` is the central orchestrator that ties all components together
- `utils.py` provides reusable RAG functionality independent of MCP
- Knowledge graph components are self-contained and optional

**Service Boundaries**:
- Clear separation between web crawling (Crawl4AI), storage (Supabase), and graphing (Neo4j)
- AI services (OpenAI, CrossEncoder) are accessed only through `utils.py`
- Configuration and validation are separate concerns

**Design Benefits**:
- Each component can be tested independently
- Services can be swapped (e.g., replace OpenAI with Ollama)
- Optional features (knowledge graph) don't pollute core code

---

## 4. MCP tool flow diagram

This diagram shows the workflow for each of the 11 MCP tools exposed to clients.

```mermaid
flowchart TD
    Start([MCP Client Request])

    subgraph "Core Crawling Tools"
        T1[crawl_single_page]
        T1Flow[Single URL → Crawl → Chunk → Store]

        T2[smart_crawl_url]
        T2Flow[Detect Type → Smart Crawl → Recursive/Batch → Store]
    end

    subgraph "Advanced Crawling Tools"
        T3[crawl_with_stealth_mode]
        T3Flow[Undetected Browser → Bypass Detection → Crawl → Store]

        T4[crawl_with_multi_url_config]
        T4Flow[JSON URLs → Auto-Optimize → Batch Crawl → Aggregate]

        T5[crawl_with_memory_monitoring]
        T5Flow[Track Memory → Adaptive Throttle → Crawl → Stats]
    end

    subgraph "RAG Query Tools"
        T6[get_available_sources]
        T6Flow[Query sources Table → Return List]

        T7[perform_rag_query]
        T7Flow[Create Embedding → Vector Search → Optional Hybrid → Optional Rerank → Results]

        T8[search_code_examples]
        T8Flow[Enhanced Query → Vector Search → Optional Hybrid → Optional Rerank → Code Results]
    end

    subgraph "Knowledge Graph Tools"
        T9[parse_github_repository]
        T9Flow[Clone Repo → AST Parse → Extract Nodes → Store Neo4j → Stats]

        T10[check_ai_script_hallucinations]
        T10Flow[Parse Script → Validate Graph → Calculate Confidence → Generate Report]

        T11[query_knowledge_graph]
        T11Flow[Parse Command → Execute Cypher → Format Results]
    end

    subgraph "Tool Routing Logic"
        Router{Which Tool?}

        Validate[Input Validation]
        Execute[Execute Tool Logic]
        Response[Format JSON Response]
    end

    %% Main flow
    Start --> Router

    %% Core tools routing
    Router -->|1| T1 --> T1Flow
    Router -->|2| T2 --> T2Flow

    %% Advanced tools routing
    Router -->|3| T3 --> T3Flow
    Router -->|4| T4 --> T4Flow
    Router -->|5| T5 --> T5Flow

    %% RAG tools routing
    Router -->|6| T6 --> T6Flow
    Router -->|7| T7 --> T7Flow
    Router -->|8| T8 --> T8Flow

    %% KG tools routing
    Router -->|9| T9 --> T9Flow
    Router -->|10| T10 --> T10Flow
    Router -->|11| T11 --> T11Flow

    %% All tools go through validation and response
    T1Flow --> Validate
    T2Flow --> Validate
    T3Flow --> Validate
    T4Flow --> Validate
    T5Flow --> Validate
    T6Flow --> Validate
    T7Flow --> Validate
    T8Flow --> Validate
    T9Flow --> Validate
    T10Flow --> Validate
    T11Flow --> Validate

    Validate --> Execute --> Response

    Response --> End([JSON Response to Client])

    %% Detailed tool workflows
    subgraph "Tool 1: crawl_single_page"
        S1[Input: URL]
        S1A[Configure CrawlerRunConfig]
        S1B[crawler.arun URL]
        S1C[smart_chunk_markdown]
        S1D[extract_section_info]
        S1E[create_embeddings_batch]
        S1F{USE_AGENTIC_RAG?}
        S1G[extract_code_blocks]
        S1H[add_documents_to_supabase]
        S1I[add_code_examples_to_supabase]
        S1J[Return: chunks_stored, code_examples_stored, stats]

        S1 --> S1A --> S1B --> S1C --> S1D --> S1E --> S1F
        S1F -->|Yes| S1G --> S1I
        S1F -->|No| S1H
        S1I --> S1J
        S1H --> S1J
    end

    subgraph "Tool 2: smart_crawl_url"
        S2[Input: URL, max_depth, max_concurrent]
        S2A{is_sitemap?}
        S2B{is_txt?}
        S2C[parse_sitemap → crawl_batch]
        S2D[crawl_markdown_file]
        S2E[crawl_recursive_internal_links]
        S2F[Process all results]
        S2G[Batch: smart_chunk_markdown]
        S2H[Parallel: create_embeddings_batch]
        S2I[update_source_info for each source]
        S2J[add_documents_to_supabase]
        S2K{USE_AGENTIC_RAG?}
        S2L[Extract and process all code blocks]
        S2M[Return: pages_crawled, chunks_stored, code_examples_stored]

        S2 --> S2A
        S2A -->|Yes| S2C --> S2F
        S2A -->|No| S2B
        S2B -->|Yes| S2D --> S2F
        S2B -->|No| S2E --> S2F
        S2F --> S2G --> S2H --> S2I --> S2J --> S2K
        S2K -->|Yes| S2L --> S2M
        S2K -->|No| S2M
    end

    subgraph "Tool 7: perform_rag_query"
        S7[Input: query, source filter, match_count]
        S7A[create_embedding for query]
        S7B{USE_HYBRID_SEARCH?}
        S7C[search_documents vector search]
        S7D[ILIKE keyword search]
        S7E[Combine results, boost overlaps]
        S7F{USE_RERANKING?}
        S7G[rerank_results with CrossEncoder]
        S7H[Format results with scores]
        S7I[Return: results, count, search_mode]

        S7 --> S7A --> S7B
        S7B -->|Yes| S7C
        S7B -->|Yes| S7D
        S7C --> S7E
        S7D --> S7E
        S7B -->|No| S7C
        S7C --> S7F
        S7E --> S7F
        S7F -->|Yes| S7G --> S7H --> S7I
        S7F -->|No| S7H --> S7I
    end

    subgraph "Tool 10: check_ai_script_hallucinations"
        S10[Input: script_path]
        S10A{USE_KNOWLEDGE_GRAPH enabled?}
        S10B[validate_script_path]
        S10C[AIScriptAnalyzer.analyze_script]
        S10D[Extract imports, classes, methods, functions]
        S10E[KnowledgeGraphValidator.validate_script]
        S10F[Validate imports against Neo4j]
        S10G[Validate method calls against classes]
        S10H[Validate parameters and types]
        S10I[Calculate overall_confidence score]
        S10J[HallucinationReporter.generate_report]
        S10K[Return: hallucinations, confidence, recommendations]

        S10 --> S10A
        S10A -->|Yes| S10B --> S10C --> S10D --> S10E
        S10A -->|No| Error1[Error: Feature disabled]
        S10E --> S10F
        S10E --> S10G
        S10E --> S10H
        S10F --> S10I
        S10G --> S10I
        S10H --> S10I
        S10I --> S10J --> S10K
    end

    %% Styling
    classDef coreTools fill:#bbdefb,stroke:#1976d2,stroke-width:3px
    classDef advTools fill:#c5e1a5,stroke:#558b2f,stroke-width:3px
    classDef ragTools fill:#ffccbc,stroke:#d84315,stroke-width:3px
    classDef kgTools fill:#e1bee7,stroke:#6a1b9a,stroke-width:3px
    classDef flowClass fill:#fff9c4,stroke:#f57f17,stroke-width:2px

    class T1,T2,T1Flow,T2Flow coreTools
    class T3,T4,T5,T3Flow,T4Flow,T5Flow advTools
    class T6,T7,T8,T6Flow,T7Flow,T8Flow ragTools
    class T9,T10,T11,T9Flow,T10Flow,T11Flow kgTools
    class Router,Validate,Execute,Response flowClass
```

### Description

The MCP tool flow diagram provides a **complete reference** for all 11 tools:

**Tool Categories**:
1. **Core Crawling (2 tools)**: Basic and smart crawling with automatic type detection
2. **Advanced Crawling (3 tools)**: Stealth mode, multi-URL optimization, memory monitoring
3. **RAG Query (3 tools)**: Source listing, document search, code example search
4. **Knowledge Graph (3 tools)**: Repository parsing, hallucination detection, graph exploration

**Workflow Patterns**:
- All tools follow: Input → Validation → Execution → Response
- Conditional features checked via environment flags
- Error responses follow consistent JSON format
- Parallel processing used for batch operations

**Tool Interactions**:
- `get_available_sources` should be called before `perform_rag_query` with source filter
- `parse_github_repository` must be run before `check_ai_script_hallucinations`
- `query_knowledge_graph` is used to explore data indexed by `parse_github_repository`

---

## Legend and conventions

### Diagram colors

| Color | Component Type | Example |
|-------|----------------|---------|
| **Blue** (`#e1f5ff`) | Client Layer | Claude Desktop, Windsurf |
| **Orange** (`#fff3e0`) | MCP Server Layer | FastMCP, crawl4ai_mcp.py |
| **Purple** (`#f3e5f5`) | Crawler Layer | Crawl4AI, Stealth Mode |
| **Green** (`#e8f5e9`) | Storage Layer | Supabase, Neo4j |
| **Pink** (`#fce4ec`) | AI Services | OpenAI, CrossEncoder |

### Node shapes

- **Rectangle**: Service/Component
- **Rounded Rectangle**: Function/Process
- **Cylinder**: Database/Storage
- **Diamond**: Decision Point
- **Circle**: Start/End Point

### Relationship types

- **Solid Arrow**: Direct dependency/call
- **Dashed Arrow**: Optional dependency
- **Thick Arrow**: Primary data flow
- **Dotted Line**: Configuration/control

### Abbreviations

- **MCP**: Model Context Protocol
- **RAG**: Retrieval Augmented Generation
- **AST**: Abstract Syntax Tree
- **LLM**: Large Language Model
- **KG**: Knowledge Graph
- **SSE**: Server-Sent Events

---

## Architectural insights

### Key discoveries from diagram analysis

#### 1. Modular Optional Features

The architecture demonstrates excellent **feature modularity**:

```
USE_CONTEXTUAL_EMBEDDINGS → Enriched embeddings
USE_HYBRID_SEARCH → Combined search strategy
USE_AGENTIC_RAG → Code-specific RAG
USE_RERANKING → Improved result ordering
USE_KNOWLEDGE_GRAPH → Hallucination detection
```

Each feature can be independently enabled/disabled without affecting core functionality. This allows users to optimize for speed vs. quality based on their use case.

#### 2. Multi-Layer RAG Strategy

The system implements a **sophisticated RAG pipeline**:

1. **Layer 1**: Content chunking with smart boundaries (headers, code blocks)
2. **Layer 2**: Optional contextual enrichment (LLM-generated context)
3. **Layer 3**: Vector embedding with optional code example extraction
4. **Layer 4**: Hybrid search combining semantic + keyword matching
5. **Layer 5**: Cross-encoder reranking for final ordering

This layered approach provides flexibility to balance cost, speed, and quality.

#### 3. Knowledge Graph as Validation Layer

The Neo4j knowledge graph serves as a **ground truth validation layer**:

```
GitHub Repo → AST Parse → Graph Storage → Validation
                                            ↓
AI-Generated Code → Parse → Compare → Confidence Score
```

This architecture enables **hallucination detection** by comparing AI-generated code against real repository structures, providing confidence scores and specific recommendations.

#### 4. Crawler Specialization

Four specialized crawler modes address different use cases:

- **Standard**: Fast, efficient, general-purpose
- **Stealth**: Bot detection bypass, slower but more reliable
- **Multi-URL**: Batch processing with auto-optimization
- **Memory-Monitored**: Large-scale operations with safety guarantees

This specialization allows the same core infrastructure to handle diverse scenarios without compromising on the common case.

#### 5. Separation of Concerns

Clean boundaries between responsibilities:

```
crawl4ai_mcp.py → Tool definitions, orchestration
utils.py → RAG utilities, reusable functions
knowledge_graphs/ → Independent KG subsystem
Crawl4AI → Web crawling abstraction
Supabase → Vector storage abstraction
Neo4j → Graph storage abstraction
```

Each component has a single, well-defined responsibility, making the system maintainable and testable.

#### 6. Error Handling Strategy

Robust error handling at multiple levels:

1. **Input Validation**: Type checking, URL validation, path validation
2. **Service Errors**: Retry logic with exponential backoff
3. **Fallback Mechanisms**: Individual processing when batch fails
4. **Graceful Degradation**: Continue on partial failures
5. **Detailed Logging**: Comprehensive error messages

This multi-level approach ensures reliability even when external services fail.

#### 7. Performance Optimization Patterns

Several optimization patterns identified:

- **Batch Embedding Creation**: Reduces API calls 10x-20x
- **Parallel Code Processing**: ThreadPoolExecutor for CPU-bound tasks
- **Memory Adaptive Dispatching**: Prevents memory exhaustion
- **Smart Chunking**: Respects natural content boundaries
- **Delete Before Insert**: Prevents duplicates efficiently

These patterns show careful consideration of production performance requirements.

#### 8. Extensibility Points

The architecture provides clear extension points:

1. **New MCP Tools**: Add with `@mcp.tool()` decorator
2. **New Crawler Modes**: Extend with `BrowserConfig` variations
3. **New RAG Strategies**: Add to `utils.py` with flag control
4. **New Storage Backends**: Replace Supabase/Neo4j clients
5. **New AI Services**: Swap OpenAI with Ollama or others

This extensibility aligns with the stated vision of supporting multiple embedding models and local deployment.

---

## Architecture evolution

### Current state (v2.0.0) ✅ **REFACTORED**

- **16 MCP tools** across 5 category modules (crawling, RAG, GraphRAG, source, knowledge graph)
- **Modular structure**:
  - `src/core/` - Lifecycle management (lifespan.py, context.py, browser_validation.py)
  - `src/tools/` - Tool implementations organized by category (5 files)
  - `src/` utilities - Shared functions grouped by purpose (utils.py, rag_utils.py, search_utils.py, etc.)
  - `knowledge_graphs/` - Independent KG subsystem (4 modules)
- **6 optional RAG/Graph strategies** (feature flags still supported)
- **4 crawler modes** (standard, stealth, multi-URL, memory-monitored)
- **Dual transport** (stdio/SSE)
- **Comprehensive error handling** preserved
- **Document knowledge graphs** (GraphRAG with 4 tools)
- **Code repository knowledge graphs** (hallucination detection with 4 tools)

**Major v2.0.0 Achievements**:
- ✅ Monolithic `crawl4ai_mcp.py` (2000+ lines) eliminated - moved to `src/archive/`
- ✅ Tools organized by category into 5 separate modules
- ✅ Core infrastructure extracted into `src/core/` directory
- ✅ Utilities categorized by purpose (RAG, search, crawling, init)
- ✅ Knowledge graph services independent and testable
- ✅ Lazy loading for optional dependencies (Neo4j)
- ✅ All 16 tools still functional with same API

### Completed refactoring (v2.0.0)

**Goal**: ✅ **ACHIEVED** - Improved code maintainability and testability

#### 1. Modular Tool Architecture ✅

Actual implementation:

```
src/
├── server.py                    # Main entry point (147 lines)
├── core/
│   ├── lifespan.py             # Lifecycle management (197 lines)
│   ├── context.py              # Crawl4AIContext dataclass
│   └── browser_validation.py   # Playwright validation
├── tools/
│   ├── crawling_tools.py       # 5 crawling tools
│   ├── rag_tools.py            # 2 RAG query tools
│   ├── graphrag_tools.py       # 4 GraphRAG tools
│   ├── source_tools.py         # 1 source management tool
│   └── knowledge_graph_tools.py # 4 code KG tools
└── archive/
    └── crawl4ai_mcp.py.original # Old monolithic file (preserved)
```

**Benefits Achieved**:
- ✅ Each tool module independently testable
- ✅ Easy to add new tools to appropriate category
- ✅ Code duplication significantly reduced
- ✅ Clear separation between tool definitions and implementations

#### 2. Utility Organization ✅

Actual implementation:

```
src/
├── utils.py                 # Core utilities (Supabase, embeddings)
├── rag_utils.py            # RAG-specific functions
├── search_utils.py         # Search strategies and helpers
├── crawling_utils.py       # Crawling helpers
├── github_utils.py         # GitHub batch processing
├── memory_monitor.py       # Memory monitoring utilities
├── initialization_utils.py # Startup and initialization
├── graphrag_utils.py       # GraphRAG utilities
└── knowledge_graph_commands.py # KG command patterns
```

**Benefits Achieved**:
- ✅ Utilities grouped by logical purpose
- ✅ Shared logic reused across tool modules
- ✅ Easy to find relevant helper functions
- ✅ Better test organization

#### 3. Knowledge Graph Independence ✅

Actual implementation:

```
knowledge_graphs/
├── __init__.py
├── ai_hallucination_detector.py   # Hallucination detection
├── document_entity_extractor.py   # GraphRAG entity extraction
├── document_graph_validator.py    # Graph validation
└── parse_repo_into_neo4j.py       # Repository parsing
```

**Benefits Achieved**:
- ✅ Knowledge graph is a self-contained subsystem
- ✅ Can be tested independently without MCP server
- ✅ Easy to add new KG functionality
- ✅ Clear boundary between MCP tools and KG logic

#### 4. Function Size Reduction ✅ **IN PROGRESS**

Current state (post-refactoring):
- Server entry point: 147 lines (was part of 2000+ line file)
- Lifespan management: 197 lines (extracted from monolithic file)
- Tool files: Well-organized by category
- Utilities: Smaller, focused modules

Progress:
- ✅ Main server split from 2000+ lines to multiple < 200 line files
- ✅ Tool organization improved dramatically
- ⏳ Some individual tool functions still need extraction (ongoing work)

### Future Direction (per README vision)

1. **Integration with Archon**: Building directly into the Archon framework
2. **Multiple Embedding Models**: Ollama support for local deployment
3. **Advanced RAG Strategies**: Late chunking, contextual retrieval improvements
4. **Enhanced Chunking**: Context 7-inspired semantic sections
5. **Performance Optimization**: Faster crawling and indexing
6. **Horizontal Scaling**: Multi-instance deployment with load balancing

### Recommended Next Steps

Based on the architectural analysis and refactoring plan:

#### Immediate (v1.3.0)
1. **Extract Crawling Strategies**: Implement strategy pattern for smart_crawl_url
2. **Create Memory Monitor**: Context manager for memory-monitored operations
3. **Refactor Large Functions**: Break down 11 functions > 150 lines
4. **Add Unit Tests**: Cover new strategy classes and monitors

#### Short-term (v1.4.0)
5. **Abstract Embedding Layer**: Create interface for multiple embedding providers
6. **Implement Command Pattern**: Extract knowledge graph commands
7. **Add Metrics/Observability**: Prometheus metrics for monitoring
8. **Optimize Batch Processing**: Enhance batch operations with better concurrency control

#### Long-term (v2.0.0)
9. **Horizontal Scaling Support**: Multi-instance coordination
10. **Plugin Architecture**: Support for custom crawlers and extractors
11. **Advanced Caching**: Intelligent caching for embeddings and graph data
12. **Streaming Operations**: Stream large results instead of batch loading

---

## Conclusion

The Crawl4AI RAG MCP Server demonstrates a **well-architected system** with:

- Clear separation of concerns
- Modular, optional features
- Multiple specialized crawler modes
- Sophisticated RAG pipeline
- Robust error handling
- Strong extensibility

The architecture supports the stated vision of becoming a comprehensive knowledge engine for AI coding assistants while maintaining flexibility for different deployment scenarios.

**Overall Assessment**: The system is production-ready with clear paths for enhancement and evolution.

---

**Document Version**: 1.0
**Generated**: October 6, 2025
**Diagrams**: 4 comprehensive Mermaid diagrams
**Total Lines**: 880+ lines of documentation
