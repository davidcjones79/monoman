"""Process metrics collector."""

import sys

import psutil

from monoman.DataTypes import ProcessListMetrics, ProcessMetrics


def collect_process_metrics(include_all: bool = False) -> ProcessListMetrics:
    """Collect process metrics.

    Args:
        include_all: If True, include system processes. Otherwise, filter some out.
    """
    processes = []
    running_count = 0
    sleeping_count = 0
    stopped_count = 0

    # Attributes to fetch (io_counters not available on macOS)
    attrs = [
        "pid",
        "name",
        "username",
        "status",
        "cpu_percent",
        "memory_percent",
        "memory_info",
        "num_threads",
        "create_time",
        "cmdline",
        "nice",
    ]
    if sys.platform != "darwin":
        attrs.append("io_counters")

    for proc in psutil.process_iter(attrs=attrs):
        try:
            info = proc.info

            # Skip kernel threads and zombies if not including all
            if not include_all:
                if info.get("pid", 0) == 0:
                    continue
                if info.get("name", "") in ("System Idle Process", ""):
                    continue

            # Get memory info
            mem_info = info.get("memory_info")
            rss = mem_info.rss if mem_info else 0
            vms = mem_info.vms if mem_info else 0

            # Get I/O counters (may not be available)
            io = info.get("io_counters")
            io_read = io.read_bytes if io else 0
            io_write = io.write_bytes if io else 0

            # Get command line
            cmdline = info.get("cmdline") or []
            cmdline_str = " ".join(cmdline) if cmdline else info.get("name", "")

            # Get status and count
            status = info.get("status", "unknown")
            if status == psutil.STATUS_RUNNING:
                running_count += 1
            elif status in (psutil.STATUS_SLEEPING, psutil.STATUS_IDLE):
                sleeping_count += 1
            elif status in (psutil.STATUS_STOPPED, psutil.STATUS_DEAD, psutil.STATUS_ZOMBIE):
                stopped_count += 1

            processes.append(
                ProcessMetrics(
                    pid=info.get("pid", 0),
                    name=info.get("name", ""),
                    username=info.get("username", "") or "",
                    status=status,
                    cpu_percent=info.get("cpu_percent", 0.0) or 0.0,
                    memory_percent=info.get("memory_percent", 0.0) or 0.0,
                    memory_rss=rss,
                    memory_vms=vms,
                    threads=info.get("num_threads", 0) or 0,
                    create_time=info.get("create_time", 0.0) or 0.0,
                    cmdline=cmdline_str,
                    nice=info.get("nice", 0) or 0,
                    io_read_bytes=io_read,
                    io_write_bytes=io_write,
                )
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return ProcessListMetrics(
        processes=processes,
        total_count=len(processes),
        running_count=running_count,
        sleeping_count=sleeping_count,
        stopped_count=stopped_count,
    )
