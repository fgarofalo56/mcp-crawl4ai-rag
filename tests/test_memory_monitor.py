"""
Tests for Memory Monitor Module

This module tests the MemoryMonitor class and MemoryStats data class which
provide memory monitoring and adaptive throttling capabilities.
"""

import asyncio
from unittest.mock import MagicMock, Mock, patch

import pytest

from memory_monitor import MemoryMonitor, MemoryStats, monitor_memory


class TestMemoryStats:
    """Test MemoryStats data class."""

    def test_memory_stats_initialization(self):
        """Test MemoryStats initialization with defaults."""
        stats = MemoryStats()

        assert stats.start_mb == 0.0
        assert stats.end_mb == 0.0
        assert stats.peak_mb == 0.0
        assert stats.delta_mb == 0.0
        assert stats.threshold_mb == 500
        assert stats.elapsed_seconds == 0.0
        assert stats.throttle_events == 0
        assert stats.samples == []

    def test_memory_stats_custom_values(self):
        """Test MemoryStats with custom values."""
        stats = MemoryStats(start_mb=100.0, end_mb=150.0, peak_mb=200.0, threshold_mb=300)

        assert stats.start_mb == 100.0
        assert stats.end_mb == 150.0
        assert stats.peak_mb == 200.0
        assert stats.threshold_mb == 300

    def test_to_dict_format(self):
        """Test to_dict conversion."""
        stats = MemoryStats(
            start_mb=100.5,
            end_mb=150.8,
            peak_mb=200.3,
            delta_mb=50.3,
            threshold_mb=300,
            elapsed_seconds=45.6,
            throttle_events=2,
            samples=[100, 120, 140, 160],
        )

        result = stats.to_dict()

        assert result["start_mb"] == 100.5
        assert result["end_mb"] == 150.8
        assert result["peak_mb"] == 200.3
        assert result["delta_mb"] == 50.3
        assert result["threshold_mb"] == 300
        assert result["elapsed_seconds"] == 45.6
        assert result["throttle_events"] == 2
        assert result["avg_mb"] == 130.0
        assert result["samples_count"] == 4

    def test_to_dict_empty_samples(self):
        """Test to_dict with no samples."""
        stats = MemoryStats()
        result = stats.to_dict()

        assert result["avg_mb"] == 0.0
        assert result["samples_count"] == 0


class TestMemoryMonitorInit:
    """Test MemoryMonitor initialization."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        monitor = MemoryMonitor()

        assert monitor.threshold_mb == 500
        assert monitor.check_interval == 1.0
        assert isinstance(monitor.stats, MemoryStats)
        assert monitor.stats.threshold_mb == 500

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        monitor = MemoryMonitor(threshold_mb=300, check_interval=0.5)

        assert monitor.threshold_mb == 300
        assert monitor.check_interval == 0.5
        assert monitor.stats.threshold_mb == 300


class TestMemoryMonitorContextManager:
    """Test MemoryMonitor as async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_without_psutil(self):
        """Test context manager when psutil is not available."""
        with patch(
            "memory_monitor.MemoryMonitor.__aenter__",
            side_effect=ImportError("No module named 'psutil'"),
        ):
            monitor = MemoryMonitor()
            with pytest.raises(ImportError) as exc_info:
                async with monitor:
                    pass
            assert "psutil" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_context_manager_success(self):
        """Test successful context manager usage."""
        with patch("memory_monitor.psutil") as mock_psutil:
            # Mock psutil.Process
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB in bytes
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor as m:
                assert m == monitor
                assert m.stats.start_mb == 100.0
                assert m.stats.peak_mb == 100.0

            # Check that exit updates stats
            assert m.stats.end_mb == 100.0
            assert m.stats.delta_mb == 0.0
            assert m.stats.elapsed_seconds > 0


class TestMemoryMonitorMethods:
    """Test MemoryMonitor methods."""

    @pytest.mark.asyncio
    async def test_get_current_memory_outside_context(self):
        """Test get_current_memory_mb raises error outside context."""
        monitor = MemoryMonitor()

        with pytest.raises(RuntimeError) as exc_info:
            monitor.get_current_memory_mb()
        assert "context manager" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_sample_memory_updates_peak(self):
        """Test sample_memory updates peak memory."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()

            # Set up memory info to increase over time
            memory_values = [100, 150, 200, 180]  # MB
            memory_call_count = [0]

            def get_memory_info():
                value = memory_values[min(memory_call_count[0], len(memory_values) - 1)]
                memory_call_count[0] += 1
                mock_info = MagicMock()
                mock_info.rss = value * 1024 * 1024
                return mock_info

            mock_process.memory_info = get_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor()

            async with monitor:
                # Take multiple samples
                monitor.sample_memory()
                monitor.sample_memory()
                monitor.sample_memory()

                assert monitor.stats.peak_mb >= 100.0
                assert len(monitor.stats.samples) == 3

    @pytest.mark.asyncio
    async def test_check_threshold_below(self):
        """Test check_threshold when below threshold."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                assert monitor.check_threshold() is False

    @pytest.mark.asyncio
    async def test_check_threshold_above(self):
        """Test check_threshold when above threshold."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 600 * 1024 * 1024  # 600 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                assert monitor.check_threshold() is True

    @pytest.mark.asyncio
    async def test_check_and_adjust_concurrency_no_throttle(self):
        """Test check_and_adjust_concurrency when below threshold."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                adjusted = monitor.check_and_adjust_concurrency(10)
                assert adjusted == 10
                assert monitor.stats.throttle_events == 0

    @pytest.mark.asyncio
    async def test_check_and_adjust_concurrency_throttle(self):
        """Test check_and_adjust_concurrency when above threshold."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 600 * 1024 * 1024  # 600 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                adjusted = monitor.check_and_adjust_concurrency(10)
                assert adjusted == 5  # Default reduction factor is 0.5
                assert monitor.stats.throttle_events == 1

    @pytest.mark.asyncio
    async def test_check_and_adjust_concurrency_min_limit(self):
        """Test check_and_adjust_concurrency respects minimum."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 600 * 1024 * 1024  # 600 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                adjusted = monitor.check_and_adjust_concurrency(2, min_concurrent=2)
                assert adjusted == 2  # Should not go below min
                assert monitor.stats.throttle_events == 0  # No actual reduction

    @pytest.mark.asyncio
    async def test_check_and_adjust_concurrency_custom_factor(self):
        """Test check_and_adjust_concurrency with custom reduction factor."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 600 * 1024 * 1024  # 600 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                adjusted = monitor.check_and_adjust_concurrency(10, reduction_factor=0.7)
                assert adjusted == 7  # 10 * 0.7
                assert monitor.stats.throttle_events == 1

    @pytest.mark.asyncio
    async def test_get_memory_pressure_ratio(self):
        """Test memory pressure ratio calculation."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 400 * 1024 * 1024  # 400 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                ratio = monitor.get_memory_pressure_ratio()
                assert ratio == 0.8  # 400 / 500

    @pytest.mark.asyncio
    async def test_should_throttle_below_margin(self):
        """Test should_throttle when below safety margin."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 400 * 1024 * 1024  # 400 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                # 400MB / 500MB = 0.8, which is < 0.9 (default safety margin)
                assert monitor.should_throttle() is False

    @pytest.mark.asyncio
    async def test_should_throttle_above_margin(self):
        """Test should_throttle when above safety margin."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 480 * 1024 * 1024  # 480 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                # 480MB / 500MB = 0.96, which is >= 0.9 (default safety margin)
                assert monitor.should_throttle() is True

    @pytest.mark.asyncio
    async def test_should_throttle_custom_margin(self):
        """Test should_throttle with custom safety margin."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 400 * 1024 * 1024  # 400 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            monitor = MemoryMonitor(threshold_mb=500)

            async with monitor:
                # 400MB / 500MB = 0.8
                assert monitor.should_throttle(safety_margin=0.7) is True
                assert monitor.should_throttle(safety_margin=0.9) is False


class TestMonitorMemoryFactory:
    """Test monitor_memory async context manager factory."""

    @pytest.mark.asyncio
    async def test_monitor_memory_factory(self):
        """Test monitor_memory factory function."""
        with patch("memory_monitor.psutil") as mock_psutil:
            mock_process = MagicMock()
            mock_memory_info = MagicMock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process

            async with monitor_memory(threshold_mb=300, check_interval=0.5) as monitor:
                assert isinstance(monitor, MemoryMonitor)
                assert monitor.threshold_mb == 300
                assert monitor.check_interval == 0.5
                assert monitor.stats.start_mb == 100.0
