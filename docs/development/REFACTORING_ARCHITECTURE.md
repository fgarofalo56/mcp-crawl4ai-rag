# Refactoring Architecture Diagram

## Overview

This document provides visual representations of the refactored architecture for the two target functions.

---

## 1. `smart_crawl_url` - Strategy Pattern Architecture

### Before Refactoring (Monolithic)
```
┌─────────────────────────────────────────────────────────────┐
│              smart_crawl_url (232 lines)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Get context clients                                   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  URL Type Detection Logic (if-elif-else)              │  │
│  │    ├─ Check if sitemap                                │  │
│  │    ├─ Check if text file                              │  │
│  │    └─ Default to recursive                            │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Sitemap Crawling Logic (50+ lines)                   │  │
│  │    ├─ Parse sitemap XML                               │  │
│  │    ├─ Extract URLs                                    │  │
│  │    └─ Batch crawl all URLs                            │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Text File Crawling Logic (40+ lines)                 │  │
│  │    ├─ Direct HTTP request                             │  │
│  │    └─ Process text content                            │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Recursive Crawling Logic (60+ lines)                 │  │
│  │    ├─ Extract internal links                          │  │
│  │    ├─ Track visited URLs                              │  │
│  │    └─ Recursive depth handling                        │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Storage Logic (80+ lines)                            │  │
│  │    ├─ Chunk content                                   │  │
│  │    ├─ Generate embeddings                             │  │
│  │    ├─ Store in Supabase                               │  │
│  │    ├─ Extract code examples                           │  │
│  │    └─ Update source info                              │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Build and return response                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### After Refactoring (Strategy Pattern)
```
┌─────────────────────────────────────────────────────────────┐
│            smart_crawl_url (79 lines)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Get context clients                                   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Get appropriate strategy                             │  │
│  │    strategy = CrawlingStrategyFactory.get_strategy()  │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ├──────────────┬──────────────┐        │
│                       ▼              ▼              ▼        │
│          ┌──────────────────┐ ┌───────────┐ ┌────────────┐  │
│          │ SitemapCrawling  │ │ TextFile  │ │ Recursive  │  │
│          │    Strategy      │ │ Crawling  │ │ Crawling   │  │
│          └──────────────────┘ │ Strategy  │ │ Strategy   │  │
│                               └───────────┘ └────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Execute crawl with selected strategy                 │  │
│  │    crawl_result = await strategy.crawl(...)           │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Handle failures                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Process and store results (delegated to helper)      │  │
│  │    storage_stats = process_and_store_crawl_results()  │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│          ┌───────────────────────────────────┐              │
│          │  process_and_store_crawl_results  │              │
│          │         (168 lines)               │              │
│          └───────────────────────────────────┘              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Return success response                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Strategy Pattern Details
```
┌─────────────────────────────────────────────────────────────────┐
│              crawling_strategies.py (418 lines)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         CrawlingStrategy (Abstract Base Class)            │  │
│  │                                                           │  │
│  │    + crawl(crawler, url, ...) -> CrawlResult             │  │
│  │    + detect(url: str) -> bool                            │  │
│  │    + get_strategy_name() -> str                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                         ▲                                       │
│                         │ inherits                              │
│       ┌─────────────────┼─────────────────┐                     │
│       │                 │                 │                     │
│       ▼                 ▼                 ▼                     │
│  ┌─────────┐    ┌─────────────┐    ┌──────────────┐            │
│  │ Sitemap │    │  TextFile   │    │  Recursive   │            │
│  │Crawling │    │  Crawling   │    │  Crawling    │            │
│  │Strategy │    │  Strategy   │    │  Strategy    │            │
│  └─────────┘    └─────────────┘    └──────────────┘            │
│       │                 │                 │                     │
│       │                 │                 │                     │
│  ┌────▼─────────────────▼─────────────────▼──────┐              │
│  │                                                │              │
│  │       CrawlingStrategyFactory                  │              │
│  │                                                │              │
│  │   + get_strategy(url) -> CrawlingStrategy     │              │
│  │   + register_strategy(strategy_class)          │              │
│  │   + get_all_strategies() -> List[type]         │              │
│  │                                                │              │
│  └────────────────────────────────────────────────┘              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         CrawlResult (Dataclass)                           │  │
│  │                                                           │  │
│  │    - success: bool                                        │  │
│  │    - url: str                                             │  │
│  │    - pages_crawled: int                                   │  │
│  │    - documents: List[Dict[str, Any]]                      │  │
│  │    - error_message: Optional[str]                         │  │
│  │    - metadata: Optional[Dict[str, Any]]                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. `parse_github_repositories_batch` - Helper Function Architecture

### Before Refactoring (Monolithic)
```
┌─────────────────────────────────────────────────────────────┐
│      parse_github_repositories_batch (274 lines)            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Environment and configuration checks                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Input Validation (inline - 30+ lines)                │  │
│  │    ├─ JSON parsing                                    │  │
│  │    ├─ Type checking                                   │  │
│  │    ├─ Parameter validation                            │  │
│  │    └─ Error handling                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  URL Validation (inline - 20+ lines)                  │  │
│  │    ├─ Validate each GitHub URL                        │  │
│  │    ├─ Extract repository names                        │  │
│  │    └─ Collect validation errors                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Repository Processing (inline - 100+ lines)          │  │
│  │    ├─ Setup semaphore                                 │  │
│  │    ├─ Create tasks                                    │  │
│  │    ├─ For each repository:                            │  │
│  │    │   ├─ Clone repository                            │  │
│  │    │   ├─ Parse structure                             │  │
│  │    │   ├─ Store in Neo4j                              │  │
│  │    │   ├─ Query statistics                            │  │
│  │    │   └─ Retry on failure (inline retry logic)       │  │
│  │    └─ Gather results                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Statistics Calculation (inline - 60+ lines)          │  │
│  │    ├─ Count successes/failures                        │  │
│  │    ├─ Calculate aggregates                            │  │
│  │    └─ Build failed repo lists                         │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Response Building (inline - 60+ lines)               │  │
│  │    ├─ Build response dictionary                       │  │
│  │    ├─ Add optional sections                           │  │
│  │    └─ Format timing information                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Console output and return                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### After Refactoring (Helper Functions)
```
┌─────────────────────────────────────────────────────────────┐
│      parse_github_repositories_batch (142 lines)            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Environment and configuration checks                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Validate input (delegated to helper)                 │  │
│  │    validate_batch_input(repo_urls_json, ...)          │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│            ┌──────────────────────────┐                      │
│            │  validate_batch_input()  │                      │
│            │      (24 lines)          │                      │
│            └──────────────────────────┘                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Validate URLs (delegated to helper)                  │  │
│  │    validate_repository_urls(repo_urls, ...)           │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│          ┌────────────────────────────────┐                  │
│          │  validate_repository_urls()    │                  │
│          │        (17 lines)              │                  │
│          └────────────────────────────────┘                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Setup parallel processing                             │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Process repositories (delegated to helper)            │  │
│  │    process_single_repository() for each repo          │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│          ┌────────────────────────────────┐                  │
│          │  process_single_repository()   │                  │
│          │       (107 lines)              │                  │
│          │  ┌──────────────────────────┐  │                  │
│          │  │ Clone & parse repository │  │                  │
│          │  └──────────────────────────┘  │                  │
│          │  ┌──────────────────────────┐  │                  │
│          │  │ Query Neo4j statistics   │  │                  │
│          │  └──────────────────────────┘  │                  │
│          │  ┌──────────────────────────┐  │                  │
│          │  │ Retry logic with delay   │  │                  │
│          │  └──────────────────────────┘  │                  │
│          └────────────────────────────────┘                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Build response (delegated to helper)                 │  │
│  │    build_batch_response(results, errors, time)        │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│          ┌────────────────────────────────┐                  │
│          │   build_batch_response()       │                  │
│          │        (59 lines)              │                  │
│          │  ┌──────────────────────────┐  │                  │
│          │  │ Calculate statistics     │  │                  │
│          │  └──────────────────────────┘  │                  │
│          │  ┌──────────────────────────┐  │                  │
│          │  │ Build response dict      │  │                  │
│          │  └──────────────────────────┘  │                  │
│          └────────────────────────────────┘                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Print summary (delegated to helper)                  │  │
│  │    print_batch_summary(total, success, failed, ...)   │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                      │
│                       ▼                                      │
│            ┌──────────────────────────┐                      │
│            │  print_batch_summary()   │                      │
│            │      (16 lines)          │                      │
│            └──────────────────────────┘                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Return JSON response                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### GitHub Utils Module Details
```
┌─────────────────────────────────────────────────────────────────┐
│                  github_utils.py (336 lines)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  validate_batch_input(repo_urls_json, max_concurrent,    │  │
│  │                       max_retries) -> Tuple               │  │
│  │                                                           │  │
│  │    Validates and parses batch processing parameters      │  │
│  │    - JSON parsing and type checking                      │  │
│  │    - Parameter range validation                          │  │
│  │    - Error message formatting                            │  │
│  │    Returns: (parsed_urls, validated_concurrent,          │  │
│  │              validated_retries)                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  validate_repository_urls(urls, validate_func)           │  │
│  │                           -> Tuple[List[Dict], List[Dict]]│  │
│  │                                                           │  │
│  │    Validates a list of GitHub repository URLs            │  │
│  │    - Calls validate_func for each URL                    │  │
│  │    - Collects validation errors                          │  │
│  │    - Ensures at least one valid URL                      │  │
│  │    Returns: (validated_repos, validation_errors)         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  calculate_batch_statistics(results) -> Dict[str, Any]   │  │
│  │                                                           │  │
│  │    Calculate aggregate statistics from batch results     │  │
│  │    - Count successes, failures, retries                  │  │
│  │    - Aggregate file/class/method/function counts         │  │
│  │    - Build failed repository lists                       │  │
│  │    Returns: Dictionary with all statistics               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  build_batch_response(results, validation_errors,        │  │
│  │                       elapsed_time) -> Dict[str, Any]    │  │
│  │                                                           │  │
│  │    Build the final response dictionary                   │  │
│  │    - Calls calculate_batch_statistics                    │  │
│  │    - Adds timing information                             │  │
│  │    - Includes optional sections                          │  │
│  │    Returns: Complete response dictionary                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  print_batch_summary(total, successful, failed, retried) │  │
│  │                                                           │  │
│  │    Print summary to console                              │  │
│  │    - Formatted output with symbols                       │  │
│  │    - Success/failure counts                              │  │
│  │    - Retry information                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  async process_single_repository(repo_info, extractor,   │  │
│  │                        semaphore, max_retries, attempt)  │  │
│  │                                          -> Dict[str, Any]│  │
│  │                                                           │  │
│  │    Process a single repository with retry logic          │  │
│  │    ┌─────────────────────────────────────────────────┐   │  │
│  │    │  Acquire semaphore                              │   │  │
│  │    └─────────────────────────────────────────────────┘   │  │
│  │    ┌─────────────────────────────────────────────────┐   │  │
│  │    │  Clone and analyze repository                   │   │  │
│  │    └─────────────────────────────────────────────────┘   │  │
│  │    ┌─────────────────────────────────────────────────┐   │  │
│  │    │  Query Neo4j for statistics                     │   │  │
│  │    └─────────────────────────────────────────────────┘   │  │
│  │    ┌─────────────────────────────────────────────────┐   │  │
│  │    │  On failure: Retry with exponential backoff     │   │  │
│  │    └─────────────────────────────────────────────────┘   │  │
│  │    Returns: Dict with status, statistics, or error       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                       crawl4ai_mcp.py                           │
│                    (Main MCP Server)                            │
└────────────────┬──────────────────────────────┬─────────────────┘
                 │                              │
                 │                              │
    ┌────────────▼─────────────┐   ┌────────────▼──────────────┐
    │                          │   │                           │
    │  crawling_strategies.py  │   │     github_utils.py       │
    │      (418 lines)         │   │       (336 lines)         │
    │                          │   │                           │
    ├──────────────────────────┤   ├───────────────────────────┤
    │                          │   │                           │
    │ • CrawlResult            │   │ • validate_batch_input    │
    │ • CrawlingStrategy       │   │ • validate_repository_urls│
    │ • SitemapCrawling        │   │ • calculate_statistics    │
    │ • TextFileCrawling       │   │ • build_batch_response    │
    │ • RecursiveCrawling      │   │ • print_batch_summary     │
    │ • CrawlingStrategyFactory│   │ • process_single_repo     │
    │                          │   │                           │
    └──────────────────────────┘   └───────────────────────────┘
                 │                              │
                 │                              │
                 └──────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │                               │
                │      crawl4ai_mcp.py          │
                │    (Helper Functions)         │
                │                               │
                ├───────────────────────────────┤
                │                               │
                │ • is_sitemap()                │
                │ • is_txt()                    │
                │ • parse_sitemap()             │
                │ • crawl_batch()               │
                │ • crawl_markdown_file()       │
                │ • crawl_recursive_internal_   │
                │   links()                     │
                │ • process_and_store_crawl_    │
                │   results()                   │
                │                               │
                └───────────────────────────────┘
```

---

## 4. Data Flow Diagrams

### Smart Crawl URL Data Flow
```
┌──────────┐
│  Client  │
└─────┬────┘
      │ smart_crawl_url(url, max_depth, max_concurrent, chunk_size)
      ▼
┌─────────────────────────────────────────────┐
│         smart_crawl_url Function            │
│  ┌───────────────────────────────────────┐  │
│  │  1. Extract crawler & supabase client │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  2. Get strategy from factory         │  │
│  │     strategy = Factory.get_strategy() │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│       CrawlingStrategyFactory                  │
│  ┌──────────────────────────────────────────┐  │
│  │  For each strategy in _strategies:       │  │
│  │    if strategy.detect(url):              │  │
│  │      return strategy()                   │  │
│  └─────────────────┬────────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
  ┌─────────┐  ┌──────────┐  ┌──────────┐
  │ Sitemap │  │ TextFile │  │Recursive │
  │Strategy │  │ Strategy │  │ Strategy │
  └────┬────┘  └─────┬────┘  └─────┬────┘
       │             │             │
       │  crawl()    │  crawl()    │  crawl()
       ▼             ▼             ▼
  ┌──────────────────────────────────────┐
  │      Returns: CrawlResult            │
  │  - success: bool                     │
  │  - url: str                          │
  │  - pages_crawled: int                │
  │  - documents: List[Dict]             │
  │  - error_message: Optional[str]      │
  │  - metadata: Optional[Dict]          │
  └────────────────┬─────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         smart_crawl_url Function            │
│  ┌───────────────────────────────────────┐  │
│  │  3. Check if crawl_result.success     │  │
│  │     If False: return error response   │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  4. Process and store results         │  │
│  │     process_and_store_crawl_results() │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│    process_and_store_crawl_results            │
│  ┌──────────────────────────────────────────┐  │
│  │  • Chunk content                         │  │
│  │  • Generate embeddings                   │  │
│  │  • Store in Supabase                     │  │
│  │  • Extract & store code examples         │  │
│  │  • Update source info                    │  │
│  └─────────────────┬────────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     │ Returns: storage_stats
                     ▼
┌─────────────────────────────────────────────┐
│         smart_crawl_url Function            │
│  ┌───────────────────────────────────────┐  │
│  │  5. Build success response JSON       │  │
│  │     - url, crawl_type                 │  │
│  │     - pages_crawled                   │  │
│  │     - chunks_stored                   │  │
│  │     - code_examples_stored            │  │
│  │     - urls_crawled (sample)           │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
              ┌──────────┐
              │  Client  │
              │ (JSON)   │
              └──────────┘
```

### GitHub Batch Processing Data Flow
```
┌──────────┐
│  Client  │
└─────┬────┘
      │ parse_github_repositories_batch(repo_urls_json, max_concurrent, max_retries)
      ▼
┌─────────────────────────────────────────────┐
│   parse_github_repositories_batch           │
│  ┌───────────────────────────────────────┐  │
│  │  1. Check environment config          │  │
│  │     USE_KNOWLEDGE_GRAPH=true?         │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  2. Get & initialize repo_extractor   │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  3. Validate input                    │  │
│  │     validate_batch_input()            │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│           validate_batch_input                │
│  • Parse JSON                                 │
│  • Validate list type                         │
│  • Check concurrency > 0                      │
│  • Check retries >= 0                         │
│  Returns: (urls, max_concurrent, max_retries) │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   parse_github_repositories_batch           │
│  ┌───────────────────────────────────────┐  │
│  │  4. Validate repository URLs          │  │
│  │     validate_repository_urls()        │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│         validate_repository_urls              │
│  For each URL:                                │
│    • Call validate_github_url()               │
│    • Collect valid repos                      │
│    • Collect validation errors                │
│  Returns: (validated_repos, validation_errors)│
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   parse_github_repositories_batch           │
│  ┌───────────────────────────────────────┐  │
│  │  5. Setup parallel processing         │  │
│  │     semaphore = Semaphore(max_conc)   │  │
│  │     start_time = time.time()          │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  6. Create tasks for each repo        │  │
│  │     tasks = [process_single_repo()]   │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  7. Gather all results                │  │
│  │     results = await gather(*tasks)    │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │ (parallel execution)  │
         ▼                       ▼
   ┌──────────┐            ┌──────────┐
   │  Repo 1  │    ...     │  Repo N  │
   └────┬─────┘            └────┬─────┘
        │                       │
        ▼                       ▼
┌────────────────────────────────────────────────┐
│      process_single_repository                │
│  ┌──────────────────────────────────────────┐  │
│  │  async with semaphore:                   │  │
│  │    1. Clone repository                   │  │
│  │    2. Analyze with repo_extractor        │  │
│  │    3. Query Neo4j for statistics         │  │
│  │    4. On error: retry with delay         │  │
│  └─────────────────┬────────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     │ Returns: result dict
                     ▼
┌─────────────────────────────────────────────┐
│   parse_github_repositories_batch           │
│  ┌───────────────────────────────────────┐  │
│  │  8. Calculate elapsed time            │  │
│  │     elapsed = time.time() - start     │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  9. Build response                    │  │
│  │     build_batch_response()            │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────┐
│         build_batch_response                  │
│  • Call calculate_batch_statistics()          │
│  • Add timing information                     │
│  • Include validation errors                  │
│  • Add failed repo lists                      │
│  Returns: complete response dictionary        │
└────────────────┬───────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   parse_github_repositories_batch           │
│  ┌───────────────────────────────────────┐  │
│  │  10. Print summary                    │  │
│  │      print_batch_summary()            │  │
│  └─────────────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │  11. Return JSON response             │  │
│  └─────────────────┬─────────────────────┘  │
└────────────────────┼──────────────────────────┘
                     │
                     ▼
              ┌──────────┐
              │  Client  │
              │ (JSON)   │
              └──────────┘
```

---

## 5. Complexity Comparison

### Cyclomatic Complexity Estimation

#### Smart Crawl URL
```
Before Refactoring:
├─ if is_sitemap(url)              [+2]
│  ├─ try/except                   [+2]
│  ├─ if not sitemap_urls          [+1]
│  └─ for url in urls              [+1]
├─ elif is_txt(url)                [+2]
│  ├─ try/except                   [+2]
│  └─ if not documents             [+1]
└─ else                             [+1]
   ├─ try/except                   [+2]
   └─ if not documents             [+1]
└─ Storage logic                   [+10]
   ├─ for doc in results           [+1]
   ├─ for chunk in chunks          [+1]
   ├─ if code_examples_enabled     [+1]
   ├─ for block in code_blocks     [+1]
   └─ try/except blocks            [+6]

Estimated Complexity: ~27

After Refactoring:
├─ try/except                      [+2]
├─ if not crawl_result.success     [+1]

Estimated Complexity: ~5

Complexity Reduction: 81%
```

#### Parse GitHub Repositories Batch
```
Before Refactoring:
├─ if not knowledge_graph_enabled  [+1]
├─ if not repo_extractor           [+1]
├─ try/except (input parse)        [+2]
├─ for url in urls                 [+1]
│  └─ if validation.valid          [+1]
├─ if not validated_repos          [+1]
├─ for repo in repos               [+1]
│  ├─ try/except                   [+2]
│  │  └─ Neo4j query               [+1]
│  └─ retry loop                   [+3]
└─ Statistics calculation          [+8]
   ├─ for successful_repos         [+1]
   ├─ if successful_repos          [+1]
   ├─ if failed_repos              [+1]
   └─ various aggregations         [+5]

Estimated Complexity: ~24

After Refactoring:
├─ if not knowledge_graph_enabled  [+1]
├─ if not repo_extractor           [+1]
├─ try/except (validate_input)     [+2]
├─ try/except (validate_urls)      [+2]
├─ gather tasks                    [+1]
└─ try/except (main)               [+2]

Estimated Complexity: ~10

Complexity Reduction: 58%
```

---

## 6. Testing Structure

### Unit Tests for Strategies
```
tests/test_crawling_strategies.py
├─ test_sitemap_strategy_detect()
├─ test_sitemap_strategy_crawl_success()
├─ test_sitemap_strategy_crawl_no_urls()
├─ test_textfile_strategy_detect()
├─ test_textfile_strategy_crawl_success()
├─ test_recursive_strategy_detect()
├─ test_recursive_strategy_crawl_success()
├─ test_crawl_result_dataclass()
└─ test_factory_get_strategy()
```

### Unit Tests for GitHub Utils
```
tests/test_github_utils.py
├─ test_validate_batch_input_success()
├─ test_validate_batch_input_invalid_json()
├─ test_validate_batch_input_not_list()
├─ test_validate_repository_urls_all_valid()
├─ test_validate_repository_urls_mixed()
├─ test_calculate_batch_statistics()
├─ test_build_batch_response()
└─ test_process_single_repository()
```

---

## Summary

This refactoring demonstrates professional software engineering practices:

1. **Design Patterns Applied**
   - Strategy Pattern for crawling
   - Factory Pattern for strategy selection
   - Helper Function Pattern for utilities

2. **Code Quality Improvements**
   - 66% reduction in `smart_crawl_url` (232 → 79 lines)
   - 48% reduction in `parse_github_repositories_batch` (274 → 142 lines)
   - 81% complexity reduction in crawling logic
   - 58% complexity reduction in batch processing

3. **Maintainability Enhancements**
   - Clear separation of concerns
   - Reusable helper functions
   - Independent testing capability
   - Easy to extend with new functionality

4. **No Breaking Changes**
   - 100% backward compatibility
   - Same function signatures
   - Same input/output formats
   - All error handling preserved

---

**Architecture Documentation Generated:** 2025-10-09
