from __future__ import annotations

import importlib
import types
from unittest import mock

import sitecustomize


def _make_aiohttp_module(with_hdrs: bool) -> types.ModuleType:
    module = types.ModuleType("aiohttp")
    if with_hdrs:
        module.hdrs = object()
    return module


def test_repair_triggered_when_hdrs_missing():
    unhealthy_module = _make_aiohttp_module(with_hdrs=False)
    healthy_module = _make_aiohttp_module(with_hdrs=True)
    import_sequence = [unhealthy_module, healthy_module]

    def fake_import(name: str, package: str | None = None):
        assert name == "aiohttp"
        return import_sequence.pop(0)

    with mock.patch.object(sitecustomize.importlib, "import_module", side_effect=fake_import):
        with mock.patch.object(sitecustomize, "_run_aiohttp_reinstall") as reinstall_mock:
            sitecustomize.ensure_aiohttp_integrity(force_check=True)

    assert reinstall_mock.call_count == 1
    assert import_sequence == []


def test_repair_not_triggered_when_module_is_healthy():
    healthy_module = _make_aiohttp_module(with_hdrs=True)

    with mock.patch.object(sitecustomize.importlib, "import_module", return_value=healthy_module) as import_mock:
        with mock.patch.object(sitecustomize, "_run_aiohttp_reinstall") as reinstall_mock:
            sitecustomize.ensure_aiohttp_integrity(force_check=True)

    import_mock.assert_called_once()
    reinstall_mock.assert_not_called()


def test_repair_triggered_on_import_error():
    healthy_module = _make_aiohttp_module(with_hdrs=True)

    with mock.patch.object(
        sitecustomize.importlib,
        "import_module",
        side_effect=[ImportError("missing"), healthy_module],
    ):
        with mock.patch.object(sitecustomize, "_run_aiohttp_reinstall") as reinstall_mock:
            sitecustomize.ensure_aiohttp_integrity(force_check=True)

    assert reinstall_mock.call_count == 1
