"""Memory panel showing detailed memory metrics."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import (
    create_progress_bar,
    format_bytes,
    format_percent,
    get_percent_color,
)
from monoman.Monoman import Monoman


def create_memory_panel(monoman: Monoman) -> Table:
    """Create the memory metrics panel."""
    mem = monoman.memory

    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]Memory[/bold]",
        title_style="bold white",
    )

    table.add_column("Type", style="bold", width=12)
    table.add_column("Usage", width=30)
    table.add_column("Details", ratio=1)

    # Physical memory
    mem_color = get_percent_color(mem.percent)
    mem_bar = Text()
    mem_bar.append(f"{format_percent(mem.percent):>6} ", style=f"bold {mem_color}")
    mem_bar.append(create_progress_bar(mem.percent, width=20), style=mem_color)

    mem_details = Text()
    mem_details.append(f"Used: {format_bytes(mem.used)}  ", style="white")
    mem_details.append(f"Free: {format_bytes(mem.free)}  ", style="green")
    mem_details.append(f"Total: {format_bytes(mem.total)}", style="dim")

    table.add_row("Physical", mem_bar, mem_details)

    # Available memory
    avail_percent = (mem.available / mem.total * 100) if mem.total > 0 else 0
    avail_color = "green" if avail_percent > 25 else "yellow" if avail_percent > 10 else "red"
    avail_bar = Text()
    avail_bar.append(f"{format_percent(avail_percent):>6} ", style=f"bold {avail_color}")
    avail_bar.append(create_progress_bar(avail_percent, width=20), style=avail_color)

    avail_details = Text()
    avail_details.append(f"Available: {format_bytes(mem.available)}", style="green")

    table.add_row("Available", avail_bar, avail_details)

    # Cached and buffers (Linux)
    if mem.cached > 0 or mem.buffers > 0:
        cache_text = Text()
        if mem.cached > 0:
            cache_text.append(f"Cached: {format_bytes(mem.cached)}  ", style="cyan")
        if mem.buffers > 0:
            cache_text.append(f"Buffers: {format_bytes(mem.buffers)}", style="cyan")
        table.add_row("Cache", "", cache_text)

    # Swap memory
    if mem.swap_total > 0:
        swap_color = get_percent_color(mem.swap_percent)
        swap_bar = Text()
        swap_bar.append(f"{format_percent(mem.swap_percent):>6} ", style=f"bold {swap_color}")
        swap_bar.append(create_progress_bar(mem.swap_percent, width=20), style=swap_color)

        swap_details = Text()
        swap_details.append(f"Used: {format_bytes(mem.swap_used)}  ", style="white")
        swap_details.append(f"Free: {format_bytes(mem.swap_free)}  ", style="green")
        swap_details.append(f"Total: {format_bytes(mem.swap_total)}", style="dim")

        table.add_row("Swap", swap_bar, swap_details)
    else:
        table.add_row("Swap", Text("N/A", style="dim"), Text("No swap configured", style="dim"))

    return table
