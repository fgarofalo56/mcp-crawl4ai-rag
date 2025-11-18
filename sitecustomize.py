"""Global site customizations for the Crawl4AI MCP workspace.

This module executes on every Python interpreter startup (because the project
root is on ``sys.path``) and is responsible for proactively validating the
``aiohttp`` installation.  Certain ``pip`` installation sequences – notably when
``crawl4ai`` is installed before ``aiohttp`` – can leave ``aiohttp`` partially
installed, missing key members such as ``hdrs``.  That manifests as an
``ImportError`` the very first time ``crawl4ai`` is used.

To provide a seamless developer experience, we attempt to detect and repair the
installation early, before user code runs.  The repair uses ``uv`` when
available (for speed and reproducibility) and falls back to ``pip`` otherwise.

The helper functions are intentionally importable so that our unit tests can
exercise the behaviour without spawning subprocesses.
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
from types import ModuleType
from typing import Optional

AIOHTTP_SPEC = "aiohttp>=3.13.1,<4.0"
_ENV_SKIP = "CRAWL4AI_SKIP_AIOHTTP_CHECK"
_ENV_REPAIRING = "CRAWL4AI_AIOHTTP_REPAIR_RUNNING"


class AiohttpRepairError(RuntimeError):
    """Raised when ``aiohttp`` cannot be repaired automatically."""


def _is_aiohttp_healthy(module: ModuleType) -> bool:
    """Return ``True`` when the provided ``aiohttp`` module looks complete."""

    # ``hdrs`` is imported lazily via ``from . import hdrs as hdrs``.
    # When ``aiohttp`` is partially installed this attribute is usually missing,
    # which is the symptom we guard against.  The attribute is cheap to check and
    # stable across supported versions.
    return hasattr(module, "hdrs")


def _import_aiohttp() -> ModuleType:
    """Import and return the ``aiohttp`` module using ``importlib``."""

    return importlib.import_module("aiohttp")


def _run_aiohttp_reinstall() -> None:
    """Execute the package manager command that reinstalls ``aiohttp``."""

    env = os.environ.copy()
    # Prevent the child interpreter from re-entering the guard recursively.
    env[_ENV_SKIP] = "1"
    env[_ENV_REPAIRING] = "1"

    uv_executable: Optional[str] = shutil.which("uv")
    if uv_executable:
        command = [
            uv_executable,
            "pip",
            "install",
            "--force-reinstall",
            AIOHTTP_SPEC,
        ]
    else:
        # ``pip`` is always available inside the managed virtual environment.
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            AIOHTTP_SPEC,
        ]

    subprocess.run(command, check=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _repair_and_reimport() -> ModuleType:
    """Attempt to repair the ``aiohttp`` installation and return the module."""

    if os.environ.get(_ENV_REPAIRING) == "1":
        raise AiohttpRepairError("Detected recursive aiohttp repair attempt.")

    try:
        _run_aiohttp_reinstall()
    except subprocess.CalledProcessError as exc:  # pragma: no cover - error path logged
        # Defer raising a custom exception so that developers see useful context.
        raise AiohttpRepairError(
            "Failed to automatically reinstall aiohttp. "
            "Re-run 'uv pip install --force-reinstall aiohttp>=3.13.1,<4.0' manually."
        ) from exc

    importlib.invalidate_caches()
    return _import_aiohttp()


def ensure_aiohttp_integrity(force_check: bool = False) -> None:
    """Validate that ``aiohttp`` imports cleanly and attempt repairs if needed."""

    if not force_check and os.environ.get(_ENV_SKIP) == "1":
        return

    try:
        module = _import_aiohttp()
    except ImportError:
        module = _repair_and_reimport()
    else:
        if not _is_aiohttp_healthy(module):
            module = _repair_and_reimport()

    if not _is_aiohttp_healthy(module):  # pragma: no cover - defensive check
        raise AiohttpRepairError(
            "aiohttp remains unhealthy after attempted repair. "
            "Please reinstall manually."
        )


ensure_aiohttp_integrity()

__all__ = [
    "ensure_aiohttp_integrity",
    "AiohttpRepairError",
]
