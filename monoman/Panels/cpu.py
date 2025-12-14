"""CPU panel showing detailed CPU metrics."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import (
    create_progress_bar,
    format_frequency,
    format_number,
    format_percent,
    get_percent_color,
)
from monoman.Monoman import Monoman


def create_cpu_panel(monoman: Monoman) -> Table:
    """Create the CPU metrics panel."""
    cpu = monoman.cpu

    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]CPU[/bold]",
        title_style="bold white",
    )

    table.add_column("Metric", style="bold", width=12)
    table.add_column("Value", width=20)
    table.add_column("Cores", ratio=1)

    # Overall CPU usage
    cpu_color = get_percent_color(cpu.percent_total)
    overall = Text()
    overall.append(f"{format_percent(cpu.percent_total)} ", style=f"bold {cpu_color}")
    overall.append(create_progress_bar(cpu.percent_total, width=15), style=cpu_color)

    # Build core usage display
    cores_text = Text()
    cores_per_row = 8
    for i, percent in enumerate(cpu.percent_per_core):
        color = get_percent_color(percent)
        cores_text.append(f"{i}:", style="dim")
        cores_text.append(f"{percent:5.1f}% ", style=color)
        if (i + 1) % cores_per_row == 0 and i < len(cpu.percent_per_core) - 1:
            cores_text.append("\n")

    table.add_row("Usage", overall, cores_text)

    # CPU times breakdown
    times_text = Text()
    times_text.append(f"User: {format_percent(cpu.user_time)}  ", style="green")
    times_text.append(f"System: {format_percent(cpu.system_time)}  ", style="yellow")
    times_text.append(f"Idle: {format_percent(cpu.idle_time)}", style="dim")
    if cpu.iowait_time > 0:
        times_text.append(f"  IOWait: {format_percent(cpu.iowait_time)}", style="red")

    table.add_row("Times", times_text, "")

    # Frequency and stats
    freq_text = Text()
    if cpu.frequency_current > 0:
        freq_text.append(f"{format_frequency(cpu.frequency_current)}", style="cyan")
        if cpu.frequency_max > 0:
            freq_text.append(f" / {format_frequency(cpu.frequency_max)}", style="dim")

    stats_text = Text()
    stats_text.append(f"Ctx: {format_number(cpu.ctx_switches)}  ", style="dim")
    stats_text.append(f"IRQ: {format_number(cpu.interrupts)}", style="dim")

    table.add_row("Frequency", freq_text, stats_text)

    # Load average (Unix only)
    if cpu.load_avg_1 > 0:
        load_text = Text()
        load_text.append(f"1m: {cpu.load_avg_1:.2f}  ", style="white")
        load_text.append(f"5m: {cpu.load_avg_5:.2f}  ", style="white")
        load_text.append(f"15m: {cpu.load_avg_15:.2f}", style="white")
        table.add_row("Load Avg", load_text, "")

    return table
