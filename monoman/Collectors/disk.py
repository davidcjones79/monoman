"""Disk metrics collector."""

import psutil

from monoman.DataTypes import DiskIOMetrics, DiskMetrics, DiskPartitionMetrics


def collect_disk_metrics(hide_snap_volumes: bool = True) -> DiskMetrics:
    """Collect disk metrics."""
    partitions = []

    for part in psutil.disk_partitions(all=False):
        # Skip snap volumes if configured
        if hide_snap_volumes and part.mountpoint.startswith("/snap/"):
            continue
            
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append(
                DiskPartitionMetrics(
                    device=part.device,
                    mountpoint=part.mountpoint,
                    fstype=part.fstype,
                    total=usage.total,
                    used=usage.used,
                    free=usage.free,
                    percent=usage.percent,
                )
            )
        except (PermissionError, OSError):
            # Skip partitions we can't access
            continue

    # Get disk I/O counters
    io = {}
    try:
        io_counters = psutil.disk_io_counters(perdisk=True)
        if io_counters:
            for device, counters in io_counters.items():
                io[device] = DiskIOMetrics(
                    device=device,
                    read_bytes=counters.read_bytes,
                    write_bytes=counters.write_bytes,
                    read_count=counters.read_count,
                    write_count=counters.write_count,
                    read_time=counters.read_time,
                    write_time=counters.write_time,
                    busy_time=getattr(counters, "busy_time", 0),
                )
    except (PermissionError, OSError):
        pass

    return DiskMetrics(partitions=partitions, io=io)
