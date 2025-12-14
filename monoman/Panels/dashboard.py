"""Dashboard panel showing system overview."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import (
    format_bytes,
    format_frequency,
    format_percent,
    get_percent_color,
)
from monoman.Monoman import Monoman


def create_dashboard_panel(monoman: Monoman) -> Table:
    """Create the dashboard overview panel."""
    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
    )

    table.add_column("System", style="bold white", ratio=1)
    table.add_column("CPU", ratio=1)
    table.add_column("Memory", ratio=1)
    table.add_column("Disk", ratio=1)
    table.add_column("Network", ratio=1)

    # System info column
    sys_info = monoman.system_info
    system_text = Text()
    system_text.append(f"{sys_info.hostname}\n", style="bold cyan")
    system_text.append(f"{sys_info.platform} {sys_info.platform_release}\n", style="dim")
    system_text.append(f"Uptime: {monoman.format_uptime()}\n", style="dim")
    system_text.append(f"Procs: {monoman.processes.total_count}", style="dim")

    # CPU column
    cpu = monoman.cpu
    cpu_color = get_percent_color(cpu.percent_total)
    cpu_text = Text()
    cpu_text.append(f"{format_percent(cpu.percent_total)}\n", style=f"bold {cpu_color}")
    cpu_text.append(f"{cpu.core_count}C/{cpu.thread_count}T\n", style="dim")
    if cpu.frequency_current > 0:
        cpu_text.append(f"{format_frequency(cpu.frequency_current)}\n", style="dim")
    if cpu.load_avg_1 > 0:
        cpu_text.append(f"Load: {cpu.load_avg_1:.2f}", style="dim")

    # Memory column
    mem = monoman.memory
    mem_color = get_percent_color(mem.percent)
    mem_text = Text()
    mem_text.append(f"{format_percent(mem.percent)}\n", style=f"bold {mem_color}")
    mem_text.append(f"{format_bytes(mem.used)}/{format_bytes(mem.total)}\n", style="dim")
    if mem.swap_total > 0:
        swap_color = get_percent_color(mem.swap_percent)
        mem_text.append(f"Swap: ", style="dim")
        mem_text.append(f"{format_percent(mem.swap_percent)}", style=swap_color)

    # Disk column
    disk_text = Text()
    if monoman.disk.partitions:
        # Show first/main partition
        part = monoman.disk.partitions[0]
        disk_color = get_percent_color(part.percent)
        disk_text.append(f"{format_percent(part.percent)}\n", style=f"bold {disk_color}")
        disk_text.append(f"{format_bytes(part.used)}/{format_bytes(part.total)}\n", style="dim")
        disk_text.append(f"{part.mountpoint}", style="dim")
    else:
        disk_text.append("N/A", style="dim")

    # Network column
    net_text = Text()
    total_recv_rate = 0.0
    total_sent_rate = 0.0
    for name in monoman.network.interfaces:
        rates = monoman.network_rates.get(name, {})
        total_recv_rate += rates.get("bytes_recv_rate", 0)
        total_sent_rate += rates.get("bytes_sent_rate", 0)

    net_text.append(f"↓ {format_bytes(total_recv_rate)}/s\n", style="green")
    net_text.append(f"↑ {format_bytes(total_sent_rate)}/s\n", style="cyan")
    net_text.append(f"Conns: {monoman.network.connections_count}", style="dim")

    table.add_row(system_text, cpu_text, mem_text, disk_text, net_text)

    return table
