"""Processes panel showing running processes."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import (
    format_bytes,
    format_percent,
    get_percent_color,
    truncate_string,
)
from monoman.Monoman import Monoman


def create_processes_panel(monoman: Monoman, max_rows: int = 15) -> Table:
    """Create the processes panel."""
    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]Processes[/bold]",
        title_style="bold white",
    )

    # Column headers with sort indicators
    sort_by = monoman.process_sort_by
    sort_arrow = "▼" if monoman.process_sort_reverse else "▲"

    pid_header = "PID" + (f" {sort_arrow}" if sort_by == "pid" else "")
    name_header = "Name" + (f" {sort_arrow}" if sort_by == "name" else "")
    user_header = "User" + (f" {sort_arrow}" if sort_by == "user" else "")
    cpu_header = "CPU%" + (f" {sort_arrow}" if sort_by == "cpu" else "")
    mem_header = "MEM%" + (f" {sort_arrow}" if sort_by == "memory" else "")

    table.add_column(pid_header, style="dim", width=8, justify="right")
    table.add_column(name_header, style="bold", width=20)
    table.add_column(user_header, width=12)
    table.add_column(cpu_header, width=8, justify="right")
    table.add_column(mem_header, width=8, justify="right")
    table.add_column("Memory", width=10, justify="right")
    table.add_column("Threads", width=8, justify="right")
    table.add_column("Command", ratio=1)

    # Get sorted and filtered processes
    processes = monoman.get_sorted_processes()

    # Show process counts in subtitle
    procs = monoman.processes
    counts_text = f"Total: {procs.total_count} | Running: {procs.running_count} | Sleeping: {procs.sleeping_count}"
    if monoman.process_filter:
        counts_text += f" | Filter: '{monoman.process_filter}'"

    for proc in processes[:max_rows]:
        # CPU percentage
        cpu_color = get_percent_color(proc.cpu_percent)
        cpu_text = Text(f"{proc.cpu_percent:.1f}", style=cpu_color)

        # Memory percentage
        mem_color = get_percent_color(proc.memory_percent)
        mem_text = Text(f"{proc.memory_percent:.1f}", style=mem_color)

        # Memory size
        mem_size = Text(format_bytes(proc.memory_rss), style="dim")

        # Threads
        threads = Text(str(proc.threads), style="dim")

        # Command (truncated)
        cmd = proc.cmdline if proc.cmdline else proc.name
        cmd_text = Text(truncate_string(cmd, 50), style="dim")

        # User (truncated)
        user = truncate_string(proc.username, 11)

        # Status indicator in name
        name = truncate_string(proc.name, 19)
        name_text = Text(name)
        if proc.status == "running":
            name_text.stylize("bold green")
        elif proc.status == "sleeping":
            name_text.stylize("white")
        elif proc.status in ("stopped", "zombie"):
            name_text.stylize("red")

        table.add_row(
            str(proc.pid),
            name_text,
            user,
            cpu_text,
            mem_text,
            mem_size,
            threads,
            cmd_text,
        )

    # Add summary row
    if len(processes) > max_rows:
        remaining = len(processes) - max_rows
        table.add_row(
            "",
            Text(f"... and {remaining} more", style="dim italic"),
            "",
            "",
            "",
            "",
            "",
            "",
        )

    # Add footer with counts
    table.add_row(
        "",
        Text(counts_text, style="dim"),
        "",
        "",
        "",
        "",
        "",
        "",
    )

    return table
