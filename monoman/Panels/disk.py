"""Disk panel showing disk usage and I/O metrics."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import (
    create_progress_bar,
    format_bytes,
    format_bytes_rate,
    format_percent,
    get_percent_color,
)
from monoman.Monoman import Monoman


def create_disk_panel(monoman: Monoman) -> Table:
    """Create the disk metrics panel."""
    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]Disk[/bold]",
        title_style="bold white",
    )

    table.add_column("Mount", style="bold", width=15)
    table.add_column("Usage", width=30)
    table.add_column("Size", width=25)
    table.add_column("I/O", ratio=1)

    for part in monoman.disk.partitions:
        # Usage bar
        usage_color = get_percent_color(part.percent)
        usage_bar = Text()
        usage_bar.append(f"{format_percent(part.percent):>6} ", style=f"bold {usage_color}")
        usage_bar.append(create_progress_bar(part.percent, width=18), style=usage_color)

        # Size info
        size_text = Text()
        size_text.append(f"{format_bytes(part.used)}", style="white")
        size_text.append(" / ", style="dim")
        size_text.append(f"{format_bytes(part.total)}", style="dim")
        size_text.append(f" ({part.fstype})", style="dim")

        # I/O rates - try to match partition to disk device
        io_text = Text()
        # Find matching disk I/O (heuristic: device name contains disk name or vice versa)
        device_base = part.device.replace("/dev/", "").rstrip("0123456789")
        matching_io = None
        for disk_name in monoman.disk.io:
            if device_base in disk_name or disk_name in device_base:
                matching_io = disk_name
                break

        if matching_io and matching_io in monoman.disk_rates:
            rates = monoman.disk_rates[matching_io]
            read_rate = rates.get("read_bytes_rate", 0)
            write_rate = rates.get("write_bytes_rate", 0)
            io_text.append(f"R: {format_bytes_rate(read_rate)}  ", style="green")
            io_text.append(f"W: {format_bytes_rate(write_rate)}", style="yellow")
        else:
            io_text.append("N/A", style="dim")

        # Truncate mount point if too long
        mount = part.mountpoint
        if len(mount) > 14:
            mount = "..." + mount[-11:]

        table.add_row(mount, usage_bar, size_text, io_text)

    if not monoman.disk.partitions:
        table.add_row("No disks", "", "", "")

    return table
