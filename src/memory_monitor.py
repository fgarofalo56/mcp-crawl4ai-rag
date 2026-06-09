"""
Memory Monitoring Module

This module provides memory monitoring and management capabilities for long-running
crawling operations. It tracks memory usage, detects potential issues, and can
adaptively throttle operations to prevent memory exhaustion.

Classes:
    MemoryMonitor: Context manager for monitoring and managing memory during operations
    MemoryStats: Data class for storing memory statistics
"""

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field


@dataclass
class MemoryStats:
    """
    Memory statistics tracking data.

    Attributes:
        start_mb: Initial memory usage in MB
        end_mb: Final memory usage in MB
        peak_mb: Peak memory usage during operation in MB
        delta_mb: Change in memory (end - start) in MB
        threshold_mb: Memory threshold that triggers throttling
        elapsed_seconds: Total elapsed time in seconds
        throttle_events: Number of times concurrency was throttled
        samples: List of memory samples taken during operation
    """

    start_mb: float = 0.0
    end_mb: float = 0.0
    peak_mb: float = 0.0
    delta_mb: float = 0.0
    threshold_mb: int = 500
    elapsed_seconds: float = 0.0
    throttle_events: int = 0
    samples: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert stats to dictionary for JSON serialization."""
        return {
            "start_mb": round(self.start_mb, 2),
            "end_mb": round(self.end_mb, 2),
            "peak_mb": round(self.peak_mb, 2),
            "delta_mb": round(self.delta_mb, 2),
            "threshold_mb": self.threshold_mb,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "throttle_events": self.throttle_events,
            "avg_mb": round(sum(self.samples) / len(self.samples), 2) if self.samples else 0.0,
            "samples_count": len(self.samples),
        }


class MemoryMonitor:
    """
    Context manager for monitoring memory usage during operations.

    This class provides memory tracking and adaptive throttling capabilities.
    It monitors memory usage in real-time and can adjust concurrency levels
    to prevent memory exhaustion.

    Attributes:
        threshold_mb: Memory threshold in MB that triggers throttling
        check_interval: Interval in seconds between memory checks (for polling)
        stats: MemoryStats object tracking memory usage
        _process: psutil.Process instance for memory monitoring

    Example:
        >>> async with MemoryMonitor(threshold_mb=500) as monitor:
        ...     # Perform memory-intensive operations
        ...     current_concurrent = monitor.check_and_adjust_concurrency(10)
        ...     # Use adjusted concurrency level
        >>> print(monitor.stats.to_dict())
    """

    def __init__(self, threshold_mb: int = 500, check_interval: float = 1.0):
        """
        Initialize the memory monitor.

        Args:
            threshold_mb: Memory threshold in MB before throttling (default: 500)
            check_interval: Seconds between memory checks (default: 1.0)
        """
        self.threshold_mb = threshold_mb
        self.check_interval = check_interval
        self.stats = MemoryStats(threshold_mb=threshold_mb)
        self._process = None
        self._start_time = None

    async def __aenter__(self):
        """Start memory monitoring when entering context."""
        try:
            import psutil

            self._process = psutil.Process()
            self._start_time = time.time()
            self.stats.start_mb = self._process.memory_info().rss / 1024 / 1024
            self.stats.peak_mb = self.stats.start_mb
            return self
        except ImportError:
            raise ImportError(
                "psutil library required for memory monitoring. " "Install with: pip install psutil"
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Finalize memory statistics when exiting context."""
        if self._process and self._start_time:
            self.stats.end_mb = self._process.memory_info().rss / 1024 / 1024
            self.stats.elapsed_seconds = time.time() - self._start_time
            self.stats.delta_mb = self.stats.end_mb - self.stats.start_mb

    def get_current_memory_mb(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Current memory usage in megabytes

        Raises:
            RuntimeError: If called outside of context manager
        """
        if not self._process:
            raise RuntimeError("MemoryMonitor must be used as a context manager")
        return self._process.memory_info().rss / 1024 / 1024

    def sample_memory(self) -> float:
        """
        Take a memory sample and update peak if needed.

        Returns:
            Current memory usage in MB
        """
        current_mb = self.get_current_memory_mb()
        self.stats.samples.append(current_mb)
        if current_mb > self.stats.peak_mb:
            self.stats.peak_mb = current_mb
        return current_mb

    def check_threshold(self) -> bool:
        """
        Check if current memory usage exceeds threshold.

        Returns:
            True if memory exceeds threshold, False otherwise
        """
        current_mb = self.sample_memory()
        return current_mb > self.threshold_mb

    def check_and_adjust_concurrency(
        self, current_concurrent: int, min_concurrent: int = 1, reduction_factor: float = 0.5
    ) -> int:
        """
        Check memory and adjust concurrency if needed.

        Args:
            current_concurrent: Current concurrency level
            min_concurrent: Minimum allowed concurrency (default: 1)
            reduction_factor: Factor to reduce concurrency by (default: 0.5)

        Returns:
            Adjusted concurrency level (may be same as input if no adjustment needed)
        """
        current_mb = self.sample_memory()

        if current_mb > self.threshold_mb and current_concurrent > min_concurrent:
            # Memory exceeded threshold, throttle
            new_concurrent = max(min_concurrent, int(current_concurrent * reduction_factor))
            if new_concurrent < current_concurrent:
                self.stats.throttle_events += 1
            return new_concurrent

        return current_concurrent

    def get_memory_pressure_ratio(self) -> float:
        """
        Calculate memory pressure as a ratio of threshold.

        Returns:
            Ratio of current memory to threshold (1.0 = at threshold, >1.0 = over)
        """
        current_mb = self.get_current_memory_mb()
        return current_mb / self.threshold_mb if self.threshold_mb > 0 else 0.0

    def should_throttle(self, safety_margin: float = 0.9) -> bool:
        """
        Determine if throttling should occur based on safety margin.

        Args:
            safety_margin: Percentage of threshold to use as trigger (default: 0.9)

        Returns:
            True if memory is above safety margin, False otherwise
        """
        return self.get_memory_pressure_ratio() >= safety_margin


@asynccontextmanager
async def monitor_memory(threshold_mb: int = 500, check_interval: float = 1.0):
    """
    Async context manager factory for memory monitoring.

    Args:
        threshold_mb: Memory threshold in MB
        check_interval: Seconds between checks

    Yields:
        MemoryMonitor instance

    Example:
        >>> async with monitor_memory(threshold_mb=500) as monitor:
        ...     # Perform operations
        ...     if monitor.should_throttle():
        ...         # Reduce workload
        ...         pass
    """
    monitor = MemoryMonitor(threshold_mb=threshold_mb, check_interval=check_interval)
    async with monitor:
        yield monitor
