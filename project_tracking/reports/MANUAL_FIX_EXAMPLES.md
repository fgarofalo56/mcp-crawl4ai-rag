# Ruff Manual Fix Examples - Code Patterns

**Date**: October 29, 2025
**Purpose**: Show exact examples of 135 remaining Ruff issues that require manual fixes
**Target Audience**: Developers implementing the fixes

---

## Quick Reference: 9 Categories of Fixes Needed

| Priority | Category | Count | Effort | Examples |
|----------|----------|-------|--------|----------|
| 1️⃣ | Unused Imports (F401) | 9 | 5 min | Remove import lines |
| 2️⃣ | Deprecated Imports (UP035) | 17 | 10 min | Replace `Dict` → `dict` |
| 3️⃣ | Exception Chaining (B904) | 7 | 10 min | Add `from err` clause |
| 4️⃣ | Collapsible If (SIM102) | 5 | 10 min | Combine with `and` |
| 5️⃣ | Variable Naming (N806) | 24 | 15 min | Rename `Mock*` → `mock_*` |
| 6️⃣ | Undefined Names (F821) | 17 | 30 min | Add TYPE_CHECKING imports |
| 7️⃣ | Import Ordering (E402) | 12 | 45 min | Move imports to top |
| 8️⃣ | With Statements (SIM117) | 40 | 20 min | Combine nested with |
| 9️⃣ | Other (B007, B024, N801, SIM105) | 4 | 10 min | Various |

---

## Category 1: F401 - Unused Imports (9 issues)

**Effort**: 5 minutes | **Files**: 9 across tests/

### Pattern: Remove unused imports

```python
# Before (F401)
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

def test_something():
    # Only uses MagicMock and patch, not Mock or os or json
    pass

# After (Fixed)
from pathlib import Path
from unittest.mock import MagicMock, patch

def test_something():
    pass
```

### Files to Fix
```
tests/test_github_utils.py:21  # Unused import 'os'
tests/test_github_utils.py:22  # Unused import 'json'
tests/integration/test_docker_deployment.py:XX  # Check specific lines
tests/test_lazy_loading_cleanup.py:XX  # Check line
```

### Auto-Check Script
```bash
# See exactly what's unused
ruff check tests/test_github_utils.py --select F401
```

---

## Category 2: UP035 - Deprecated Imports (17 issues)

**Effort**: 10 minutes | **Files**: 9 test files

### Pattern: Replace deprecated typing imports

```python
# Before (UP035)
from typing import Any, Dict, List
from typing import Optional, Union

def function(data: Dict[str, List[int]]) -> Optional[List[str]]:
    config: Dict[str, Any] = {}
    return None

# After (Fixed)
from typing import Any

def function(data: dict[str, list[int]]) -> list[str] | None:
    config: dict[str, Any] = {}
    return None
```

### Files to Fix
```
tests/conftest.py:11
tests/integration/conftest.py:11
tests/integration/test_crawl_workflows.py:18
tests/integration/test_docker_deployment.py:14
tests/integration/test_knowledge_graph_integration.py:16
tests/integration/test_rag_pipeline.py:32
tests/test_crawl_helpers_batch.py:11
tests/test_github_utils.py:12
tests/test_lazy_loading_cleanup.py:23
tests/test_search_utils.py:10
```

### Replacement Rules
```
typing.Dict[K, V]      → dict[K, V]
typing.List[V]         → list[V]
typing.Optional[X]     → X | None
typing.Union[X, Y]     → X | Y
typing.Tuple[X, Y]     → tuple[X, Y]
typing.Set[X]          → set[X]
```

### Batch Fix (if available)
```bash
# Some fixes can be automated:
ruff check tests/ --fix-only=UP035
# But manual verification still needed

# Or use sed/grep for bulk replacement:
sed -i 's/from typing import Dict, List/from typing import Any/' tests/*.py
sed -i 's/Dict\[/dict[/g' tests/*.py
sed -i 's/List\[/list[/g' tests/*.py
```

---

## Category 3: B904 - Exception Chaining (7 issues)

**Effort**: 10 minutes | **Files**: 3 main files

### Pattern: Add exception context to raise statements

```python
# Before (B904)
try:
    value = int(value_str)
except ValueError:
    raise ConfigurationError(
        f"Environment variable '{var_name}' must be an integer, got: {value_str}"
    )

# After (Fixed)
try:
    value = int(value_str)
except ValueError as err:
    raise ConfigurationError(
        f"Environment variable '{var_name}' must be an integer, got: {value_str}"
    ) from err
```

### Files to Fix
```
src/env_validators.py:251  # ConfigurationError without from
src/env_validators.py:299  # ConfigurationError without from
src/env_validators.py:327  # ConfigurationError without from
src/env_validators.py:362  # ConfigurationError without from
src/error_handlers.py      # Multiple except blocks
tests/integration/test_docker_deployment.py:XX
```

### Rule
**Always use**: `except SomeException as err:` then `raise NewException(...) from err`

This preserves the exception chain for debugging.

---

## Category 4: SIM102 - Collapsible If (5 issues)

**Effort**: 10 minutes | **Files**: 2 main files

### Pattern: Combine nested if statements with `and`

```python
# Before (SIM102)
if isinstance(node, ast.Assign):
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        # process

# After (Fixed)
if isinstance(node, ast.Assign) and len(node.targets) == 1:
    if isinstance(node.targets[0], ast.Name):
        # process

# Or even better:
if (
    isinstance(node, ast.Assign)
    and len(node.targets) == 1
    and isinstance(node.targets[0], ast.Name)
):
    # process
```

### Files to Fix
```
knowledge_graphs/ai_script_analyzer.py:190
knowledge_graphs/parse_repo_into_neo4j.py:272
knowledge_graphs/parse_repo_into_neo4j.py:297
knowledge_graphs/parse_repo_into_neo4j.py:344
```

### Exact Location Examples

**File: knowledge_graphs/ai_script_analyzer.py:190**
```python
# Current (needs fixing)
if isinstance(node, ast.Assign):
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        if isinstance(node.value, ast.Call):
            # code...

# Fixed
if (
    isinstance(node, ast.Assign)
    and len(node.targets) == 1
    and isinstance(node.targets[0], ast.Name)
    and isinstance(node.value, ast.Call)
):
    # code...
```

---

## Category 5: N806 - Variable Naming (24 issues)

**Effort**: 15 minutes | **Files**: Primarily tests/integration

### Pattern: Rename Mock variables to lowercase

```python
# Before (N806)
with patch("knowledge_graph_validator.KnowledgeGraphValidator") as MockValidator:
    mock_validator = MockValidator
    # use mock_validator

# After (Fixed)
with patch("knowledge_graph_validator.KnowledgeGraphValidator") as mock_validator:
    # use mock_validator
```

### Files to Fix
```
tests/integration/test_docker_deployment.py:89   # MockValidator → mock_validator
tests/integration/test_docker_deployment.py:108  # MockOpenAI → mock_openai
tests/integration/test_docker_deployment.py:124  # MockCrawler → mock_crawler
tests/integration/test_docker_deployment.py:136  # MockEncoder → mock_encoder
tests/integration/test_docker_deployment.py:179  # MockCrawler → mock_crawler
...and more (24 total)
```

### Renaming Pattern
```
MockValidator    → mock_validator
MockOpenAI       → mock_openai
MockCrawler      → mock_crawler
MockEncoder      → mock_encoder
MockRepository   → mock_repository
MockService      → mock_service
MockClient       → mock_client
```

### Batch Fix Approach
```bash
# For each file:
# 1. Find all Mock* variables
grep -n "as Mock[A-Z]" tests/integration/test_docker_deployment.py

# 2. Manual replacement in each occurrence
# (No safe automated way due to variable scope tracking)
```

---

## Category 6: F821 - Undefined Names (17 issues)

**Effort**: 30 minutes | **Files**: 4 files

### Pattern 1: Missing import

```python
# Before (F821)
@abstractmethod
async def save_code_examples(self, examples: list["CodeExample"]) -> int:
    """..."""

# Problem: CodeExample is not imported

# After (Fixed)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import CodeExample

@abstractmethod
async def save_code_examples(self, examples: list["CodeExample"]) -> int:
    """..."""
```

### Pattern 2: Circular import handling

```python
# Before (F821)
from src.services.crawl_service import CrawlConfig  # Would be circular!

class SomeClass:
    def method(self, config: "CrawlConfig") -> None:
        pass

# After (Fixed)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.crawl_service import CrawlConfig

class SomeClass:
    def method(self, config: "CrawlConfig") -> None:
        pass
```

### Files to Fix
```
src/repositories/document_repository.py:126   # CodeExample undefined
src/repositories/document_repository.py:133   # CodeExample undefined
src/services/crawl_service.py:69              # DocumentRepository undefined
src/services/crawl_service.py:70              # CrawlConfig undefined
src/services/crawl_service.py:149             # CrawlingStrategy undefined
src/timeout_utils.py:40                       # Unknown type reference
knowledge_graphs/parse_repo_into_neo4j.py     # Various type refs
```

### Solution Strategy
For each F821 error:
1. Check if the name should be imported
2. If import would create circular dependency → use TYPE_CHECKING block
3. If it's a typo → fix the name
4. If it's from a non-existent module → fix module import

---

## Category 7: E402 - Import Ordering (12 issues)

**Effort**: 45 minutes | **Files**: 5 main files

### Pattern: Imports after code

```python
# Before (E402)
import logging
import os
from pathlib import Path

# Configure logging BEFORE imports (problem!)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

# Now try to import (too late!)
import sys  # E402 error

# Later imports
from config import load_config

# After (Fixed)
import logging
import os
import sys
from pathlib import Path

from config import load_config

# Now configure AFTER imports
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
```

### Common Pattern: Path setup before imports

```python
# Before (E402)
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Now import (too late!)
from utils import helper  # E402

# After (Fixed)
import sys
from pathlib import Path

from utils import helper

# Path setup AFTER imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
```

### Files to Fix
```
knowledge_graphs/parse_repo_into_neo4j.py:31    # import sys after logging setup
src/initialization_utils.py:28                  # imports after path setup
src/server.py:26, 35, 42, 48, 52               # multiple import blocks
tests/integration/test_crawl_workflows.py:31    # import after path setup
tests/test_stdout_safety.py:28                  # import after path setup
```

### Detailed Fix for src/server.py

Current structure:
```python
# Line 1-25: docstring and initial imports
import fastmcp
import os

# Line 25: Set path (problem!)
sys.path.insert(0, str(root_dir / "src"))

# Line 26: Try to import (E402!)
from core import crawl4ai_lifespan  # E402
from tools.crawling_tools import (...)  # E402
from tools.graphrag_tools import (...)  # E402
from tools.source_tools import (...)  # E402
from tools.knowledge_graph_tools import (...)  # E402
```

Fixed structure:
```python
# All imports at top
import fastmcp
import os
import sys
from pathlib import Path

from core import crawl4ai_lifespan
from tools.crawling_tools import (...)
from tools.graphrag_tools import (...)
from tools.source_tools import (...)
from tools.knowledge_graph_tools import (...)

# THEN path setup
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))
```

---

## Category 8: SIM117 - Multiple With Statements (40 issues)

**Effort**: 20 minutes | **Files**: Multiple test files

### Pattern: Combine nested with statements

```python
# Before (SIM117)
with patch("sys.platform", "win32"):
    with patch("sys.version_info", (3, 11)):
        # test code
        pass

# After (Fixed)
with (
    patch("sys.platform", "win32"),
    patch("sys.version_info", (3, 11)),
):
    # test code
    pass

# Or single line for 2 patches:
with patch("sys.platform", "win32"), patch("sys.version_info", (3, 11)):
    # test code
    pass
```

### Files to Fix (40 instances)
```
tests/test_browser_validation.py:32, 41, 50, 106, 115, ...
tests/test_lazy_loading.py:39, 59, 79, ...
tests/test_graphrag_tools.py:74, ...
tests/test_mcp_tools.py:36, 85, ...
tests/test_knowledge_graph.py:52, ...
tests/test_perform_rag_query_source_filter.py:60, 78, 94, ...
```

### Before/After Examples

**Example 1: test_browser_validation.py**
```python
# Before
def test_get_global_playwright_browser_path_windows(self):
    with patch("sys.platform", "win32"):
        with patch("pathlib.Path.home") as mock_home:
            # test

# After
def test_get_global_playwright_browser_path_windows(self):
    with (
        patch("sys.platform", "win32"),
        patch("pathlib.Path.home") as mock_home,
    ):
        # test
```

**Example 2: test_lazy_loading.py** (3 patches)
```python
# Before
with patch("src.core.lifespan.initialize_crawl4ai") as mock_init:
    with patch("src.core.lifespan.initialize_supabase") as mock_supa:
        with patch("src.core.lifespan.initialize_neo4j") as mock_neo4j:
            # test

# After
with (
    patch("src.core.lifespan.initialize_crawl4ai") as mock_init,
    patch("src.core.lifespan.initialize_supabase") as mock_supa,
    patch("src.core.lifespan.initialize_neo4j") as mock_neo4j,
):
    # test
```

---

## Category 9: Other Issues (4 issues)

### B007 - Unused Loop Variable (1 issue)

```python
# Before
for i, (block, summary) in enumerate(zip(code_blocks, summaries)):
    code_urls.append(source_url)  # i never used

# After
for _i, (block, summary) in enumerate(zip(code_blocks, summaries)):
    code_urls.append(source_url)
```

### B024 - Abstract Base Class (1 issue)

```python
# Before (B024)
class SomeAbstractClass:
    def abstract_method(self):
        raise NotImplementedError()

# After
from abc import ABC, abstractmethod

class SomeAbstractClass(ABC):
    @abstractmethod
    def abstract_method(self):
        raise NotImplementedError()
```

### N801 - Invalid Class Name (1 issue)

```python
# Before (N801)
class error_handler:
    """Context manager for handling errors"""
    pass

# After
class ErrorHandler:
    """Context manager for handling errors"""
    pass
```

### SIM105 - Suppressible Exception (1 issue)

```python
# Before (SIM105)
try:
    operation_that_might_fail()
except FileNotFoundError:
    pass

# After
from contextlib import suppress

with suppress(FileNotFoundError):
    operation_that_might_fail()
```

---

## Implementation Checklist

**Phase 1 (30 min)**:
- [ ] Fix F401 - Unused imports (9 issues)
- [ ] Fix UP035 - Deprecated typing imports (17 issues)
- [ ] Fix SIM102 - Collapsible if statements (5 issues)

**Phase 2 (60 min)**:
- [ ] Fix B904 - Exception chaining (7 issues)
- [ ] Fix N806 - Variable naming in tests (24 issues)
- [ ] Fix other issues (4 issues)

**Phase 3 (90 min)**:
- [ ] Fix F821 - Undefined names (17 issues)
- [ ] Fix E402 - Import ordering (12 issues)
- [ ] Fix SIM117 - With statements (40 issues)

**Testing (20 min)**:
- [ ] Run Ruff again to verify: `ruff check src/ tests/ knowledge_graphs/`
- [ ] Run Black formatter: `black src/ tests/ knowledge_graphs/`
- [ ] Run tests: `pytest tests/`
- [ ] Check coverage: `pytest --cov=src`

---

## Tools & Commands

```bash
# Check specific error type
ruff check tests/ --select F401

# Check specific file
ruff check tests/conftest.py

# Show detailed help for error
ruff rule F401
ruff rule UP035
ruff rule SIM117

# See statistics
ruff check src/ tests/ knowledge_graphs/ --statistics

# Format after fixes
black src/ tests/ knowledge_graphs/ --line-length 100

# Run tests
pytest tests/ -v
```

---

**Document Version**: 1.0
**Last Updated**: October 29, 2025
**Status**: Ready for implementation
