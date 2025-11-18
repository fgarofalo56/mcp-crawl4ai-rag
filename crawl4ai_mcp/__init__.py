"""Compatibility package for legacy ``crawl4ai_mcp`` imports.

This module acts as a lightweight shim so that historic ``import crawl4ai_mcp``
usage (and ``python -m crawl4ai_mcp`` invocations) continue to function after the
project's refactor into the ``src`` package hierarchy.

It lazily resolves attributes against the modern module layout, ensuring that
existing tooling, tests, and documentation references do not break.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from types import ModuleType
from typing import Any, Dict

__all__ = ["main", "main_async", "mcp"]

# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def main() -> None:
    """Synchronously launch the MCP server using the legacy entry point."""

    from run_mcp import main_wrapper

    main_wrapper()


async def main_async() -> None:
    """Asynchronous entry point that mirrors the modern ``src.server.main``."""

    from src.server import main as _main

    await _main()


# ---------------------------------------------------------------------------
# Lazy attribute resolution for legacy symbols
# ---------------------------------------------------------------------------

_EXPLICIT_EXPORTS: dict[str, Callable[[], Any]] = {
    "mcp": lambda: importlib.import_module("src.server").mcp,
    "FastMCP": lambda: importlib.import_module("fastmcp").FastMCP,
}

# Prefer targeted lookups for known legacy symbols before falling back to
# breadth-first module scanning.
_LEGACY_ATTR_HINTS: dict[str, str] = {
    # Crawling helpers
    "parse_sitemap": "src.crawling_utils",
    "crawl_batch": "src.crawl_helpers",
    "crawl_markdown_file": "src.crawl_helpers",
    "crawl_recursive_internal_links": "src.crawl_helpers",
    "smart_chunk_markdown": "src.crawling_utils",
    # RAG helpers
    "rerank_results": "src.core.reranking",
    # GraphRAG utilities
    "process_and_store_crawl_results": "src.tools.graphrag_tools",
}

# Modules to probe (in order) when resolving unknown legacy attributes.
_SEARCH_ORDER = [
    "src",
    "src.config",
    "src.utils",
    "src.crawl_helpers",
    "src.crawling_utils",
    "src.memory_monitor",
    "src.response_size_manager",
    "src.search_utils",
    "src.repositories",
    "src.repositories.document_repository",
    "src.repositories.supabase_document_repository",
    "src.services",
    "src.services.crawl_service",
    "src.core",
    "src.core.context",
    "src.core.lifespan",
    "src.core.reranking",
    "src.core.validators",
    "src.tools.crawling_tools",
    "src.tools.rag_tools",
    "src.tools.source_tools",
    "src.tools.graphrag_tools",
    "src.tools.knowledge_graph_tools",
]

_module_cache: dict[str, ModuleType] = {}
_attr_cache: dict[str, Any] = {}


def _import_module(name: str) -> ModuleType | None:
    module = _module_cache.get(name)
    if module is not None:
        return module
    try:
        module = importlib.import_module(name)
    except Exception:  # pragma: no cover - defensive: optional deps may be missing
        return None
    _module_cache[name] = module
    return module


def _resolve_from_hint(name: str) -> Any | None:
    module_name = _LEGACY_ATTR_HINTS.get(name)
    if not module_name:
        return None
    module = _import_module(module_name)
    if module is None or not hasattr(module, name):
        return None
    return getattr(module, name)


def _resolve_from_search(name: str) -> Any | None:
    for module_name in _SEARCH_ORDER:
        module = _import_module(module_name)
        if module is None:
            continue
        if hasattr(module, name):
            return getattr(module, name)
    return None


def __getattr__(name: str) -> Any:
    if name in _attr_cache:
        return _attr_cache[name]

    if name in _EXPLICIT_EXPORTS:
        value = _EXPLICIT_EXPORTS[name]()
        _attr_cache[name] = value
        globals()[name] = value
        return value

    value = _resolve_from_hint(name)
    if value is None:
        value = _resolve_from_search(name)
    if value is None:
        raise AttributeError(f"module 'crawl4ai_mcp' has no attribute '{name}'")

    _attr_cache[name] = value
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    names = set(__all__)
    names.update(_EXPLICIT_EXPORTS.keys())
    names.update(_LEGACY_ATTR_HINTS.keys())
    names.update(_attr_cache.keys())
    return sorted(names)


# Ensure the module is registered for legacy patching workflows that mutate
# ``sys.modules['crawl4ai_mcp']`` directly during tests.
sys.modules.setdefault("crawl4ai_mcp", sys.modules[__name__])
