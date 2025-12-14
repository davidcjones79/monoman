"""Memory metrics collector."""

import psutil

from monoman.DataTypes import MemoryMetrics


def collect_memory_metrics() -> MemoryMetrics:
    """Collect memory metrics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return MemoryMetrics(
        total=mem.total,
        available=mem.available,
        used=mem.used,
        free=mem.free,
        percent=mem.percent,
        cached=getattr(mem, "cached", 0),
        buffers=getattr(mem, "buffers", 0),
        swap_total=swap.total,
        swap_used=swap.used,
        swap_free=swap.free,
        swap_percent=swap.percent,
    )
