"""Tests for metric collectors."""

import pytest

from monoman.Collectors import (
    collect_cpu_metrics,
    collect_disk_metrics,
    collect_memory_metrics,
    collect_network_metrics,
    collect_process_metrics,
    collect_system_info,
)


def test_collect_system_info():
    """Test system info collection."""
    info = collect_system_info()
    assert info.hostname
    assert info.platform
    assert info.uptime_seconds >= 0


def test_collect_cpu_metrics():
    """Test CPU metrics collection."""
    cpu = collect_cpu_metrics()
    assert 0 <= cpu.percent_total <= 100
    assert cpu.core_count > 0
    assert cpu.thread_count >= cpu.core_count


def test_collect_memory_metrics():
    """Test memory metrics collection."""
    mem = collect_memory_metrics()
    assert mem.total > 0
    assert mem.available > 0
    assert mem.used > 0
    assert 0 <= mem.percent <= 100


def test_collect_disk_metrics():
    """Test disk metrics collection."""
    disk = collect_disk_metrics()
    # Should have at least one partition
    assert len(disk.partitions) > 0
    for part in disk.partitions:
        assert part.total > 0
        assert 0 <= part.percent <= 100


def test_collect_network_metrics():
    """Test network metrics collection."""
    net = collect_network_metrics()
    # Should have at least one interface (though might be empty on some systems)
    assert isinstance(net.interfaces, dict)
    assert net.connections_count >= 0


def test_collect_process_metrics():
    """Test process metrics collection."""
    procs = collect_process_metrics()
    assert procs.total_count > 0
    assert len(procs.processes) > 0

    # Check first process has required fields
    proc = procs.processes[0]
    assert proc.pid > 0
    assert proc.name
