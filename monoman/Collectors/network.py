"""Network metrics collector."""

import psutil

from monoman.DataTypes import NetworkInterfaceMetrics, NetworkMetrics


def collect_network_metrics() -> NetworkMetrics:
    """Collect network metrics."""
    interfaces = {}

    # Get network I/O counters per interface
    io_counters = psutil.net_io_counters(pernic=True)

    # Get interface stats (up/down, speed)
    try:
        if_stats = psutil.net_if_stats()
    except (PermissionError, OSError):
        if_stats = {}

    # Get interface addresses
    try:
        if_addrs = psutil.net_if_addrs()
    except (PermissionError, OSError):
        if_addrs = {}

    for name, counters in io_counters.items():
        # Skip loopback on some systems
        if name.lower() in ("lo", "loopback"):
            continue

        stats = if_stats.get(name)
        addrs = if_addrs.get(name, [])

        # Extract IPv4/IPv6 addresses
        addresses = []
        for addr in addrs:
            if addr.family.name in ("AF_INET", "AF_INET6"):
                addresses.append(addr.address)

        interfaces[name] = NetworkInterfaceMetrics(
            name=name,
            bytes_sent=counters.bytes_sent,
            bytes_recv=counters.bytes_recv,
            packets_sent=counters.packets_sent,
            packets_recv=counters.packets_recv,
            errors_in=counters.errin,
            errors_out=counters.errout,
            drops_in=counters.dropin,
            drops_out=counters.dropout,
            is_up=stats.isup if stats else False,
            speed=stats.speed if stats else 0,
            addresses=addresses,
        )

    # Count network connections
    try:
        connections = psutil.net_connections(kind="all")
        connections_count = len(connections)
    except (PermissionError, psutil.AccessDenied):
        connections_count = 0

    return NetworkMetrics(interfaces=interfaces, connections_count=connections_count)
