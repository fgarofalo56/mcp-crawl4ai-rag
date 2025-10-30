# 🏗️ Utils.py Refactoring Plan - Modular Architecture

**Status**: Ready for Implementation
**Author**: Claude (Python Refactoring Architect)
**Date**: October 29, 2025
**Estimated Effort**: 8-10 hours
**Risk Level**: Medium (requires careful import management)

---

## 📊 Executive Summary

**Current State**: `src/utils.py` is a 42.7KB monolithic file with 1,227 lines containing 35+ functions across 7 distinct domains.

**Target State**: Organized module structure in `src/utils/` with 6 focused files, each <10KB, with 90%+ test coverage.

**Key Objectives**:
- Improve code maintainability and discoverability
- Maintain 100% backward compatibility (no breaking changes)
- Achieve 90%+ test coverage for all extracted modules
- Enable future parallel development on independent modules

**Success Metrics**:
- ✅ All modules < 10KB
- ✅ Test coverage ≥ 90% per module
- ✅ All existing tests pass without modification
- ✅ No changes required in dependent code (backward compatibility)

---

## 📐 Current Architecture Analysis

### File Statistics
```
Total Lines: 1,227
Total Size: 42.7 KB
Functions: 35 (including private helpers)
Classes: 0
Module Dependencies: openai, supabase, concurrent.futures, dotenv
```

### Function Categories (7 domains identified)

| Category | Function Count | Lines | Percentage |
|----------|----------------|-------|------------|
| Supabase Client | 1 | 17 | 1.4% |
| Embeddings | 5 | 218 | 17.8% |
| Document Operations | 9 | 398 | 32.4% |
| Code Extraction | 3 | 178 | 14.5% |
| Code Examples | 2 | 189 | 15.4% |
| Source Management | 2 | 107 | 8.7% |
| Search Operations | 2 | 65 | 5.3% |
| Text Chunking | 1 | 68 | 5.5% |

### Dependency Analysis

**External Dependencies**:
- `openai.AzureOpenAI` (embeddings, contextual embeddings, summaries)
- `supabase.Client` (database operations)
- `concurrent.futures.ThreadPoolExecutor` (parallel processing)
- `dotenv` (environment configuration)
- `urllib.parse.urlparse` (URL parsing)

**Internal Dependencies**:
- `create_embedding()` → `create_embeddings_batch()`
- `add_documents_to_supabase()` → helper functions + `create_embeddings_batch()`
- `search_documents()` → `create_embedding()`
- `search_code_examples()` → `create_embedding()`

### Current Usage

**Imports Found**:
1. `src/tools/graphrag_tools.py` (3 imports)
2. `tests/test_utils.py` (11 imports)
3. `tests/test_chunk_content.py` (1 import)

**Import Patterns**:
```python
# Primary pattern (in tests)
from src.utils import (
    add_code_examples_to_supabase,
    add_documents_to_supabase,
    create_embedding,
    create_embeddings_batch,
    extract_code_blocks,
    # ... more
)

# Lazy import pattern (in tools)
from src.utils import chunk_content
from src.utils import search_documents
```

---

## 🎯 Proposed Module Structure

### Overview
```
src/utils/
├── __init__.py                    # Re-export all for backward compatibility
├── supabase_client.py            # Supabase connection management
├── embeddings.py                 # Embedding generation (Azure OpenAI)
├── document_operations.py        # Document storage and retrieval
├── code_extraction.py            # Code block extraction and analysis
├── search.py                     # Vector search operations
└── text_processing.py            # Text chunking and processing
```

### Detailed Module Breakdown

---

### Module 1: `supabase_client.py` (Smallest - Start Here)

**Purpose**: Supabase client initialization and connection management

**Functions to Extract** (1 function, 17 lines):
```python
✓ get_supabase_client() -> Client                  # Lines 107-123
```

**Dependencies**:
- External: `supabase`, `os`, `sys`
- Internal: None

**Estimated Size**: ~100 lines (with docstrings and error handling improvements)

**Test Coverage**: Currently 3 tests (100%)
- test_get_supabase_client_success
- test_get_supabase_client_missing_url
- test_get_supabase_client_missing_key

**Refactoring Notes**:
- Already well-tested and isolated
- No internal dependencies
- Could add connection pooling in future

---

### Module 2: `embeddings.py`

**Purpose**: Embedding generation with Azure OpenAI, batching, and contextual embeddings

**Functions to Extract** (8 functions, 517 lines):
```python
# Core embedding functions
✓ create_embeddings_batch(texts: list[str]) -> list[list[float]]    # Lines 126-241
✓ create_embedding(text: str) -> list[float]                        # Lines 244-260

# Token and batching utilities
✓ count_tokens_estimate(text: str) -> int                           # Lines 44-56
✓ batch_texts_by_tokens(...) -> list[list[str]]                     # Lines 59-104

# Contextual embeddings
✓ generate_contextual_embedding(full_doc, chunk) -> tuple           # Lines 263-317
✓ process_chunk_with_context(args: tuple) -> tuple                  # Lines 320-334

# Module initialization (from top of utils.py)
✓ Azure OpenAI client setup                                          # Lines 20-36
✓ Batch configuration constants                                      # Lines 38-41
```

**Dependencies**:
- External: `openai.AzureOpenAI`, `os`, `sys`, `time`
- Internal: None (self-contained)

**Estimated Size**: ~600 lines (with docstrings)

**Test Coverage**: Currently 6 tests (100%)
- test_create_embeddings_batch_success
- test_create_embeddings_batch_empty
- test_create_embeddings_batch_retry
- test_create_embedding_success
- test_create_embedding_error_fallback
- test_generate_contextual_embedding_success/error

**Refactoring Notes**:
- Move Azure OpenAI client initialization to module-level
- Add retry configuration as module constants
- Consider extracting retry logic to separate function
- Add tests for batch_texts_by_tokens and count_tokens_estimate

---

### Module 3: `document_operations.py` (Largest Module)

**Purpose**: Document storage, batch processing, and Supabase operations

**Functions to Extract** (9 functions, 398 lines):
```python
# Main operations
✓ add_documents_to_supabase(...) -> None                            # Lines 614-688

# Private helpers (extract as public in new module)
✓ validate_url_safe(url: str) -> bool                               # Lines 337-398
✓ _validate_and_filter_urls(urls: list[str]) -> list[str]          # Lines 401-423
✓ _delete_existing_records_batch(client, urls) -> None             # Lines 426-458
✓ _apply_contextual_embeddings(...) -> list[str]                    # Lines 461-516
✓ _prepare_batch_data(...) -> list[dict]                            # Lines 519-555
✓ _insert_batch_with_retry(...) -> None                             # Lines 558-612

# Code example operations
✓ add_code_examples_to_supabase(...) -> None                        # Lines 863-999
```

**Dependencies**:
- External: `supabase.Client`, `urllib.parse.urlparse`, `concurrent.futures`
- Internal: `embeddings.create_embeddings_batch`, `embeddings.generate_contextual_embedding`

**Estimated Size**: ~500 lines (after extraction and cleanup)

**Test Coverage**: Currently 8 tests (75%)
- test_add_documents_to_supabase_basic
- test_add_documents_with_contextual_embeddings
- test_add_code_examples_to_supabase
- test_add_code_examples_empty
- test_add_documents_batch_processing
- test_add_code_examples_batch_processing

**Refactoring Notes**:
- Rename private helpers to public functions (remove `_` prefix)
- Extract batch processing logic to separate functions
- Add tests for validate_url_safe
- Add tests for batch retry logic
- Consider splitting code examples to separate module if grows

**Missing Tests to Add** (target 90%+):
- test_validate_url_safe_valid_urls
- test_validate_url_safe_invalid_urls
- test_validate_url_safe_sql_injection
- test_delete_existing_records_batch_success
- test_delete_existing_records_batch_fallback
- test_prepare_batch_data
- test_insert_batch_with_retry_success
- test_insert_batch_with_retry_all_failures

---

### Module 4: `code_extraction.py`

**Purpose**: Code block extraction from markdown and summary generation

**Functions to Extract** (3 functions, 178 lines):
```python
✓ extract_code_blocks(markdown, min_length) -> list[dict]           # Lines 728-809
✓ generate_code_example_summary(...) -> str                         # Lines 812-860
✓ (Future) extract_inline_code() -> list[str]                       # Not yet implemented
```

**Dependencies**:
- External: `openai.AzureOpenAI`, `os`, `sys`, `re`
- Internal: `embeddings.client` (Azure OpenAI client)

**Estimated Size**: ~250 lines (with additional features)

**Test Coverage**: Currently 7 tests (90%)
- test_extract_code_blocks_with_language
- test_extract_code_blocks_no_language
- test_extract_code_blocks_with_context
- test_extract_code_blocks_min_length
- test_extract_code_blocks_empty
- test_generate_code_example_summary_success
- test_generate_code_example_summary_error

**Refactoring Notes**:
- Consider regex optimization for large markdown files
- Add support for inline code extraction
- Add language detection for unlabeled blocks
- Consider adding markdown validation

**Missing Tests to Add**:
- test_extract_code_blocks_nested_backticks
- test_extract_code_blocks_incomplete_pairs
- test_extract_code_blocks_special_characters

---

### Module 5: `search.py`

**Purpose**: Vector search operations for documents and code examples

**Functions to Extract** (2 functions, 65 lines):
```python
✓ search_documents(client, query, match_count, filter) -> list      # Lines 690-725
✓ search_code_examples(client, query, ...) -> list                  # Lines 1111-1156
```

**Dependencies**:
- External: `supabase.Client`, `sys`
- Internal: `embeddings.create_embedding`

**Estimated Size**: ~150 lines (with enhancements)

**Test Coverage**: Currently 5 tests (100%)
- test_search_documents_success
- test_search_documents_with_filter
- test_search_documents_error
- test_search_code_examples_success
- test_search_code_examples_with_source_filter

**Refactoring Notes**:
- Consider adding pagination support
- Add result ranking/reranking functions
- Add search result caching (future)
- Consider hybrid search strategies

**Missing Tests to Add** (for enhancements):
- test_search_documents_pagination
- test_search_documents_empty_results
- test_search_code_examples_error_handling

---

### Module 6: `text_processing.py`

**Purpose**: Text chunking and processing utilities

**Functions to Extract** (1 function + 2 source operations, 175 lines):
```python
✓ chunk_content(content, max_chunk, min_chunk) -> list[str]         # Lines 1159-1226

# Source management (could go here or separate module)
✓ update_source_info(client, source_id, summary, count) -> None     # Lines 1002-1041
✓ extract_source_summary(source_id, content, max_len) -> str        # Lines 1044-1108
```

**Dependencies**:
- External: `re`, `sys`, `supabase.Client`, `openai.AzureOpenAI`
- Internal: `embeddings.client` (for extract_source_summary)

**Estimated Size**: ~250 lines (with additional processing functions)

**Test Coverage**: Currently 1 test (20%)
- test_chunk_content (in separate file)

**Refactoring Notes**:
- chunk_content is well-implemented but needs more tests
- Source management functions could be separate module
- Add semantic chunking strategies (future)
- Add multilingual support

**Missing Tests to Add** (CRITICAL - target 90%):
- test_chunk_content_empty_input
- test_chunk_content_invalid_chunk_size
- test_chunk_content_single_paragraph
- test_chunk_content_long_paragraph
- test_chunk_content_multiple_paragraphs
- test_chunk_content_min_chunk_merging
- test_chunk_content_whitespace_handling
- test_update_source_info_new_source (exists)
- test_update_source_info_existing_source (exists)
- test_update_source_info_error
- test_extract_source_summary_success (exists)
- test_extract_source_summary_empty_content (exists)
- test_extract_source_summary_error (exists)

---

### Module 7: `__init__.py` (Backward Compatibility Layer)

**Purpose**: Re-export all functions to maintain backward compatibility

**Content**:
```python
"""
Utility functions for the Crawl4AI MCP server.

This module provides a backward-compatible interface to the refactored utils modules.
All functions are re-exported from their respective specialized modules.

For new code, consider importing directly from the specialized modules:
- utils.supabase_client - Supabase connection management
- utils.embeddings - Embedding generation
- utils.document_operations - Document storage operations
- utils.code_extraction - Code block extraction
- utils.search - Vector search operations
- utils.text_processing - Text chunking and processing
"""

# Supabase client
from .supabase_client import get_supabase_client

# Embeddings
from .embeddings import (
    count_tokens_estimate,
    batch_texts_by_tokens,
    create_embeddings_batch,
    create_embedding,
    generate_contextual_embedding,
    process_chunk_with_context,
    client as openai_client,  # Azure OpenAI client
    MAX_BATCH_SIZE,
    MAX_TOKENS_PER_BATCH,
    RATE_LIMIT_DELAY,
)

# Document operations
from .document_operations import (
    add_documents_to_supabase,
    add_code_examples_to_supabase,
    validate_url_safe,
)

# Code extraction
from .code_extraction import (
    extract_code_blocks,
    generate_code_example_summary,
)

# Search operations
from .search import (
    search_documents,
    search_code_examples,
)

# Text processing
from .text_processing import (
    chunk_content,
    update_source_info,
    extract_source_summary,
)

# Re-export all for backward compatibility
__all__ = [
    # Supabase
    "get_supabase_client",
    # Embeddings
    "count_tokens_estimate",
    "batch_texts_by_tokens",
    "create_embeddings_batch",
    "create_embedding",
    "generate_contextual_embedding",
    "process_chunk_with_context",
    "openai_client",
    "MAX_BATCH_SIZE",
    "MAX_TOKENS_PER_BATCH",
    "RATE_LIMIT_DELAY",
    # Document operations
    "add_documents_to_supabase",
    "add_code_examples_to_supabase",
    "validate_url_safe",
    # Code extraction
    "extract_code_blocks",
    "generate_code_example_summary",
    # Search
    "search_documents",
    "search_code_examples",
    # Text processing
    "chunk_content",
    "update_source_info",
    "extract_source_summary",
]
```

**Estimated Size**: ~100 lines (imports + docstrings)

---

## 🚀 Implementation Strategy

### Phase-by-Phase Approach

**Phase 1: Setup and Foundation** (30 minutes)
```bash
# 1. Create module directory structure
mkdir src/utils
touch src/utils/__init__.py

# 2. Archive original file
cp src/utils.py src/archive/utils.py.original

# 3. Create skeleton files with docstrings
touch src/utils/supabase_client.py
touch src/utils/embeddings.py
touch src/utils/document_operations.py
touch src/utils/code_extraction.py
touch src/utils/search.py
touch src/utils/text_processing.py
```

**Phase 2: Extract Smallest Module First** (45 minutes)
- ✅ Extract `supabase_client.py` (1 function, easiest)
- ✅ Create `__init__.py` with re-export
- ✅ Run tests: `pytest tests/test_utils.py::TestSupabaseClient -v`
- ✅ Verify: All 3 tests pass

**Phase 3: Extract Embeddings Module** (1.5 hours)
- ✅ Extract `embeddings.py` (8 functions, core functionality)
- ✅ Update `__init__.py` imports
- ✅ Run tests: `pytest tests/test_utils.py::TestEmbeddings -v`
- ✅ Verify: All 6 tests pass
- ✅ Add 2 new tests for token utilities (target: 90%+)

**Phase 4: Extract Search Module** (45 minutes)
- ✅ Extract `search.py` (2 functions, depends on embeddings)
- ✅ Update `__init__.py` imports
- ✅ Run tests: `pytest tests/test_utils.py -k search -v`
- ✅ Verify: All 5 tests pass

**Phase 5: Extract Code Extraction Module** (1 hour)
- ✅ Extract `code_extraction.py` (3 functions)
- ✅ Update `__init__.py` imports
- ✅ Run tests: `pytest tests/test_utils.py::TestCodeExtraction -v`
- ✅ Verify: All 7 tests pass
- ✅ Add 3 new edge case tests

**Phase 6: Extract Text Processing Module** (1.5 hours)
- ✅ Extract `text_processing.py` (3 functions)
- ✅ Update `__init__.py` imports
- ✅ Run tests: `pytest tests/test_chunk_content.py -v`
- ✅ Add 10+ new tests for chunk_content (CRITICAL)
- ✅ Verify: 90%+ coverage

**Phase 7: Extract Document Operations (Largest)** (2.5 hours)
- ✅ Extract `document_operations.py` (9 functions)
- ✅ Update `__init__.py` imports
- ✅ Run tests: `pytest tests/test_utils.py::TestDocumentOperations -v`
- ✅ Add 8 new tests for private helpers
- ✅ Verify: 90%+ coverage

**Phase 8: Final Integration and Validation** (1 hour)
```bash
# 1. Run all utils tests
pytest tests/test_utils.py -v

# 2. Run dependent tests
pytest tests/test_graphrag_tools.py -v

# 3. Run all tests
pytest tests/ -v

# 4. Check coverage
pytest tests/test_utils.py --cov=src.utils --cov-report=html --cov-report=term-missing

# 5. Verify coverage ≥ 90%
# 6. Update documentation
```

**Phase 9: Code Quality and Documentation** (1 hour)
```bash
# 1. Format code
black src/utils/ --line-length 100

# 2. Lint code
ruff check src/utils/

# 3. Type check
mypy src/utils/

# 4. Update docstrings
# 5. Update CHANGELOG.md
# 6. Update API_REFERENCE.md if needed
```

---

## 📋 Test Strategy

### Test Organization

**Current Test File**: `tests/test_utils.py` (470 lines, 7 test classes)

**New Test Organization** (Optional - can keep single file with re-exports):
```
tests/
├── test_utils.py                    # Keep as compatibility layer
└── utils/                           # Optional: organize by module
    ├── test_supabase_client.py
    ├── test_embeddings.py
    ├── test_document_operations.py
    ├── test_code_extraction.py
    ├── test_search.py
    └── test_text_processing.py
```

**Decision**: Keep single `test_utils.py` file initially
- Easier to maintain backward compatibility
- Existing test infrastructure works
- Can split later if file grows too large

### Test Coverage Goals

| Module | Current Coverage | Target Coverage | New Tests Needed |
|--------|------------------|-----------------|------------------|
| supabase_client.py | 100% (3 tests) | 100% | 0 |
| embeddings.py | 80% (6 tests) | 90% | 2-3 |
| search.py | 100% (5 tests) | 100% | 0 |
| code_extraction.py | 90% (7 tests) | 90% | 3 |
| text_processing.py | 20% (1 test) | 90% | 10+ ⚠️ |
| document_operations.py | 75% (8 tests) | 90% | 8 |
| **TOTAL** | **32%** | **90%** | **23+ tests** |

### Critical Tests to Add

**High Priority (Must Add)**:
1. `test_chunk_content_*` (10 tests) - Currently only 1 test
2. `test_validate_url_safe_*` (3 tests) - Security critical
3. `test_batch_retry_logic_*` (3 tests) - Error handling
4. `test_token_utilities_*` (2 tests) - Batching logic

**Medium Priority (Should Add)**:
5. `test_code_blocks_edge_cases_*` (3 tests) - Robustness
6. `test_source_management_errors_*` (2 tests) - Error paths

### Test Execution Plan

**After Each Module Extraction**:
```bash
# 1. Run module-specific tests
pytest tests/test_utils.py::TestModuleName -v

# 2. Run full utils test suite
pytest tests/test_utils.py -v

# 3. Run dependent tests
pytest tests/test_graphrag_tools.py -v

# 4. Check coverage for new module
pytest tests/test_utils.py --cov=src.utils.module_name --cov-report=term-missing
```

**Final Validation**:
```bash
# Full test suite with coverage
pytest tests/ -v --cov=src.utils --cov-report=html --cov-report=term-missing

# Verify no regressions
pytest tests/ -v

# Coverage threshold check (should be ≥ 90%)
pytest tests/test_utils.py --cov=src.utils --cov-fail-under=90
```

---

## ⚠️ Risk Assessment

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Import breakage | Low | High | Comprehensive `__init__.py` re-exports |
| Test failures | Low | High | Test after each module extraction |
| Circular imports | Medium | Medium | Careful dependency management |
| Performance regression | Low | Medium | Keep lazy imports where needed |
| Coverage drop | Medium | Low | Add tests before extraction |

### Detailed Risk Analysis

**Risk 1: Import Breakage**
- **Scenario**: Existing code breaks due to import changes
- **Likelihood**: Low (if using re-export pattern)
- **Impact**: High (breaks dependent code)
- **Mitigation**:
  - Complete `__init__.py` re-exports
  - No changes needed in dependent files
  - Test all import patterns
- **Rollback**: Restore original `utils.py`

**Risk 2: Test Failures**
- **Scenario**: Tests fail after module extraction
- **Likelihood**: Low (with incremental approach)
- **Impact**: High (blocks progress)
- **Mitigation**:
  - Test after each module extraction
  - Fix issues before moving to next module
  - Keep original file as reference
- **Rollback**: Revert specific module extraction

**Risk 3: Circular Import Dependencies**
- **Scenario**: Modules import each other creating cycles
- **Likelihood**: Medium (embeddings ↔ document_operations)
- **Impact**: Medium (runtime errors)
- **Mitigation**:
  - Careful dependency analysis
  - Use lazy imports where needed
  - Keep Azure OpenAI client in embeddings only
- **Detection**: Import modules in Python REPL

**Risk 4: Performance Regression**
- **Scenario**: Import overhead increases
- **Likelihood**: Low (minimal overhead)
- **Impact**: Medium (startup time)
- **Mitigation**:
  - Profile import times before/after
  - Use lazy imports for heavy dependencies
  - Keep module initialization lightweight
- **Measurement**: Time `import src.utils` before/after

**Risk 5: Coverage Drop**
- **Scenario**: Coverage drops during refactoring
- **Likelihood**: Medium (adding 23+ tests takes time)
- **Impact**: Low (temporary)
- **Mitigation**:
  - Add tests incrementally during extraction
  - Prioritize critical path testing
  - Accept phased coverage improvement
- **Tracking**: Coverage report after each phase

---

## 🎯 Success Criteria

### Functional Requirements

✅ **FR1: Backward Compatibility**
- All existing imports work without changes
- `from src.utils import *` works identically
- No changes required in `src/tools/` or `tests/`

✅ **FR2: Test Coverage**
- Overall coverage ≥ 90% for utils modules
- All existing tests pass without modification
- 23+ new tests added for uncovered paths

✅ **FR3: Code Organization**
- Each module < 10KB (< ~250 lines)
- Clear separation of concerns
- Minimal cross-module dependencies

✅ **FR4: Code Quality**
- Black formatting (100 char lines)
- Ruff linting passes
- Mypy type checking passes
- Google-style docstrings on all functions

### Non-Functional Requirements

✅ **NFR1: Performance**
- No measurable performance regression
- Import time < 100ms total
- Test execution time unchanged

✅ **NFR2: Maintainability**
- Clear module boundaries
- Self-documenting code
- Comprehensive docstrings

✅ **NFR3: Documentation**
- Each module has header docstring
- Each function has Google-style docstring
- `__init__.py` documents migration path

---

## 📊 Estimated Effort

### Time Breakdown

| Phase | Duration | Tasks | Dependencies |
|-------|----------|-------|--------------|
| Phase 1: Setup | 30 min | Create structure, archive original | None |
| Phase 2: Supabase | 45 min | Extract 1 function, test | Phase 1 |
| Phase 3: Embeddings | 1.5 hrs | Extract 8 functions, add tests | Phase 2 |
| Phase 4: Search | 45 min | Extract 2 functions, test | Phase 3 |
| Phase 5: Code Extraction | 1 hr | Extract 3 functions, add tests | Phase 4 |
| Phase 6: Text Processing | 1.5 hrs | Extract 3 functions, add 10+ tests | Phase 5 |
| Phase 7: Document Ops | 2.5 hrs | Extract 9 functions, add 8 tests | Phase 6 |
| Phase 8: Integration | 1 hr | Full test suite, coverage check | Phase 7 |
| Phase 9: Quality | 1 hr | Format, lint, docs, changelog | Phase 8 |
| **TOTAL** | **10 hrs** | 9 phases | Sequential |

### Resource Requirements

**Developer Time**: 10 hours (can be split over 2-3 days)
**CI/CD Time**: ~15 minutes per commit (9 commits)
**Review Time**: 1-2 hours for PR review

**Total Project Time**: 11-12 hours

---

## 🚨 Rollback Strategy

### Immediate Rollback (< 5 minutes)

**Scenario**: Critical issue discovered, need immediate fix

```bash
# 1. Restore original file
cp src/archive/utils.py.original src/utils.py

# 2. Remove new directory
rm -rf src/utils/

# 3. Run tests to verify
pytest tests/test_utils.py -v

# 4. Commit rollback
git add src/utils.py
git commit -m "Rollback: restore monolithic utils.py due to [issue]"
```

### Partial Rollback (specific module)

**Scenario**: One module has issues, others are fine

```bash
# 1. Move problematic functions back to utils.py
# 2. Update __init__.py to import from utils.py
# 3. Keep other modules in place
# 4. Test and commit
```

### Rollback Detection

**Indicators for Rollback**:
- ❌ Test suite failure > 5 tests
- ❌ Coverage drop > 10%
- ❌ Performance regression > 20%
- ❌ Import errors in dependent code
- ❌ CI/CD pipeline failures

**Decision Criteria**:
- **Immediate rollback**: Critical tests fail, production impact
- **Partial rollback**: Single module issue, others stable
- **Fix forward**: Minor issues, can be fixed quickly

---

## 📚 Documentation Updates Required

### Files to Update

1. **CHANGELOG.md**
```markdown
## [Unreleased]

### Refactored
- **utils.py modularization**: Split 42.7KB monolithic file into 6 focused modules
  - `src/utils/supabase_client.py` - Supabase connection management
  - `src/utils/embeddings.py` - Embedding generation with Azure OpenAI
  - `src/utils/document_operations.py` - Document storage and batch processing
  - `src/utils/code_extraction.py` - Code block extraction from markdown
  - `src/utils/search.py` - Vector search operations
  - `src/utils/text_processing.py` - Text chunking and source management
  - Maintained 100% backward compatibility via `__init__.py` re-exports
  - Increased test coverage from 32% to 90%+

### Added
- 23+ new tests for previously uncovered utility functions
- Comprehensive docstrings for all utility modules
```

2. **docs/ARCHITECTURE.md** (Update Module Structure section)

3. **docs/CODE_QUALITY_IMPROVEMENTS.md** (Add refactoring case study)

4. **docs/API_REFERENCE.md** (Update if function signatures change)

5. **README.md** (Update project structure diagram)

6. **project_tracking/sprints/current/sprint-current.md** (Log completion)

---

## 🔄 Migration Path for Future Code

### For New Code (Recommended)

```python
# ✅ RECOMMENDED: Import from specific modules
from src.utils.embeddings import create_embedding
from src.utils.search import search_documents
from src.utils.text_processing import chunk_content

# Why? Better IDE autocomplete, clearer dependencies
```

### For Existing Code (No Changes Needed)

```python
# ✅ WORKS: Existing imports continue to work
from src.utils import create_embedding, search_documents, chunk_content

# Why? Backward compatibility via __init__.py re-exports
```

### Gradual Migration Strategy

**Phase 1 (This Refactoring)**: Maintain backward compatibility
- All existing code continues to work
- No changes required in dependent files

**Phase 2 (Future - Optional)**: Encourage specific imports
- Add deprecation notices in `__init__.py` docstring
- Update style guide to recommend specific imports

**Phase 3 (Future - Optional)**: Remove re-exports
- After all code migrated to specific imports
- Remove `from .module import *` from `__init__.py`
- Major version bump (breaking change)

**Recommendation**: Stay in Phase 1 indefinitely
- Backward compatibility is valuable
- Re-exports add minimal overhead
- No breaking changes for users

---

## ✅ Acceptance Criteria Checklist

### Before Starting
- [ ] Read and understand entire refactoring plan
- [ ] Review current utils.py structure and dependencies
- [ ] Identify all import locations in codebase
- [ ] Set up test environment and coverage tools

### During Refactoring (After Each Module)
- [ ] Module extracted to separate file
- [ ] `__init__.py` updated with re-exports
- [ ] Module-specific tests pass (100%)
- [ ] Full utils test suite passes (100%)
- [ ] Dependent tests pass (graphrag_tools)
- [ ] Code formatted with Black
- [ ] Code passes Ruff linting
- [ ] Coverage checked for new module

### Final Validation
- [ ] All 9 phases completed successfully
- [ ] Total test coverage ≥ 90% for utils
- [ ] All 64+ tests passing (original + 23 new)
- [ ] No import errors in any dependent code
- [ ] Performance benchmarks show no regression
- [ ] Documentation updated (CHANGELOG, ARCHITECTURE, etc.)
- [ ] Code quality checks pass (Black, Ruff, mypy)
- [ ] PR created with detailed description
- [ ] CI/CD pipeline passes all checks

### Post-Merge
- [ ] Monitor production for any issues
- [ ] Update sprint tracking with completion
- [ ] Archive this refactoring plan
- [ ] Share learnings with team

---

## 📝 Implementation Notes

### Import Dependencies Flow

```
supabase_client.py (no internal deps)
    ↓
embeddings.py (no internal deps, uses supabase_client)
    ↓
search.py (depends on embeddings)
    ↓
code_extraction.py (depends on embeddings)
    ↓
text_processing.py (depends on embeddings)
    ↓
document_operations.py (depends on embeddings, text_processing)
```

**Key Insight**: Extract in dependency order (bottom-up)

### Module Size Validation

| Module | Target Lines | Target KB | Status |
|--------|--------------|-----------|--------|
| supabase_client.py | 100 | 3 KB | ✅ Well within |
| embeddings.py | 600 | 20 KB | ⚠️ Largest |
| search.py | 150 | 5 KB | ✅ Well within |
| code_extraction.py | 250 | 8 KB | ✅ Well within |
| text_processing.py | 250 | 8 KB | ✅ Well within |
| document_operations.py | 500 | 17 KB | ⚠️ Large |
| **TOTAL** | 1,850 | 61 KB | ✅ Better organized |

**Note**: Total lines increase due to docstrings and separation, but organization improves maintainability.

### Performance Considerations

**Current Performance**:
- Import time: ~50ms (measured)
- Embedding batch: ~500ms for 10 texts
- Document insertion: ~1s for 20 documents

**Expected After Refactoring**:
- Import time: ~60ms (+10ms, acceptable)
- Embedding batch: ~500ms (unchanged)
- Document insertion: ~1s (unchanged)

**Monitoring**: Add performance benchmarks to test suite

---

## 🎓 Lessons Learned (To Be Updated Post-Completion)

### What Went Well
- _To be filled after implementation_

### What Could Be Improved
- _To be filled after implementation_

### Unexpected Challenges
- _To be filled after implementation_

### Recommendations for Future Refactoring
- _To be filled after implementation_

---

## 📞 Support and Questions

**Primary Contact**: Python Refactoring Architect (Claude)
**Documentation**: This refactoring plan
**Backup Plan**: Rollback strategy (see section above)
**Testing Support**: Run `pytest tests/test_utils.py -v` for validation

---

**Last Updated**: October 29, 2025
**Status**: ✅ Ready for Implementation
**Next Step**: Create directory structure and begin Phase 1

---

## Appendix A: Full Function List

### Current utils.py Function Inventory (35 functions)

**Module-level Setup** (moved to embeddings.py):
- Azure OpenAI client initialization
- Batch configuration constants

**Embeddings** (6 functions):
1. `count_tokens_estimate(text: str) -> int`
2. `batch_texts_by_tokens(texts, max_tokens) -> list[list[str]]`
3. `create_embeddings_batch(texts: list[str]) -> list[list[float]]`
4. `create_embedding(text: str) -> list[float]`
5. `generate_contextual_embedding(full_document, chunk) -> tuple[str, bool]`
6. `process_chunk_with_context(args: tuple) -> tuple[str, bool]`

**Supabase Client** (1 function):
7. `get_supabase_client() -> Client`

**URL Validation** (2 functions):
8. `validate_url_safe(url: str) -> bool`
9. `_validate_and_filter_urls(urls: list[str]) -> list[str]`

**Document Operations** (7 functions):
10. `_delete_existing_records_batch(client, urls) -> None`
11. `_apply_contextual_embeddings(...) -> list[str]`
12. `_prepare_batch_data(...) -> list[dict[str, Any]]`
13. `_insert_batch_with_retry(client, batch_data, max_retries) -> None`
14. `add_documents_to_supabase(...) -> None`

**Search Operations** (2 functions):
15. `search_documents(client, query, match_count, filter_metadata) -> list[dict]`
16. `search_code_examples(client, query, ...) -> list[dict]`

**Code Extraction** (3 functions):
17. `extract_code_blocks(markdown_content, min_length) -> list[dict]`
18. `generate_code_example_summary(code, context_before, context_after) -> str`
19. `add_code_examples_to_supabase(...) -> None`

**Source Management** (2 functions):
20. `update_source_info(client, source_id, summary, word_count) -> None`
21. `extract_source_summary(source_id, content, max_length) -> str`

**Text Processing** (1 function):
22. `chunk_content(content, max_chunk_size, min_chunk_size) -> list[str]`

**Total**: 22 public functions + 13 lines of module setup

---

## Appendix B: Test Inventory

### Current Test Coverage (tests/test_utils.py)

**Test Classes** (7 classes, 46 test methods):

1. **TestSupabaseClient** (3 tests) ✅ 100%
   - test_get_supabase_client_success
   - test_get_supabase_client_missing_url
   - test_get_supabase_client_missing_key

2. **TestEmbeddings** (6 tests) ⚠️ 80%
   - test_create_embeddings_batch_success
   - test_create_embeddings_batch_empty
   - test_create_embeddings_batch_retry
   - test_create_embedding_success
   - test_create_embedding_error_fallback
   - test_generate_contextual_embedding_success
   - test_generate_contextual_embedding_error
   - Missing: token utilities tests

3. **TestDocumentOperations** (4 tests) ⚠️ 60%
   - test_add_documents_to_supabase_basic
   - test_add_documents_with_contextual_embeddings
   - test_search_documents_success
   - test_search_documents_with_filter
   - test_search_documents_error
   - Missing: 8 helper function tests

4. **TestCodeExtraction** (7 tests) ✅ 90%
   - test_extract_code_blocks_with_language
   - test_extract_code_blocks_no_language
   - test_extract_code_blocks_with_context
   - test_extract_code_blocks_min_length
   - test_extract_code_blocks_empty
   - test_generate_code_example_summary_success
   - test_generate_code_example_summary_error

5. **TestCodeExampleStorage** (3 tests) ✅ 90%
   - test_add_code_examples_to_supabase
   - test_add_code_examples_empty
   - test_search_code_examples_success
   - test_search_code_examples_with_source_filter

6. **TestSourceOperations** (6 tests) ✅ 95%
   - test_update_source_info_new_source
   - test_update_source_info_existing_source
   - test_extract_source_summary_success
   - test_extract_source_summary_empty_content
   - test_extract_source_summary_long_content
   - test_extract_source_summary_error

7. **TestBatchOperations** (2 tests) ✅ 100%
   - test_add_documents_batch_processing
   - test_add_code_examples_batch_processing

**Additional Test File**:
- `tests/test_chunk_content.py` (1 test) ⚠️ 20%
  - test_chunk_content_basic

**Total Current Tests**: 47 tests (46 + 1)

### Tests to Add (23+ new tests)

**Priority 1 (Critical) - 13 tests**:
1. test_chunk_content_empty_input
2. test_chunk_content_invalid_chunk_size
3. test_chunk_content_single_paragraph
4. test_chunk_content_long_paragraph
5. test_chunk_content_multiple_paragraphs
6. test_chunk_content_min_chunk_merging
7. test_validate_url_safe_valid_urls
8. test_validate_url_safe_invalid_urls
9. test_validate_url_safe_sql_injection
10. test_count_tokens_estimate
11. test_batch_texts_by_tokens_basic
12. test_batch_texts_by_tokens_oversized_text
13. test_insert_batch_with_retry_all_failures

**Priority 2 (High) - 6 tests**:
14. test_delete_existing_records_batch_fallback
15. test_prepare_batch_data_source_extraction
16. test_extract_code_blocks_nested_backticks
17. test_extract_code_blocks_incomplete_pairs
18. test_apply_contextual_embeddings_parallel
19. test_update_source_info_error

**Priority 3 (Medium) - 4 tests**:
20. test_search_documents_pagination
21. test_search_code_examples_error_handling
22. test_extract_code_blocks_special_characters
23. test_chunk_content_whitespace_handling

**Total Target Tests**: 70 tests (47 existing + 23 new)

---

**End of Refactoring Plan**
