"""GPU panel showing GPU metrics."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import (
    create_progress_bar,
    format_bytes,
    format_percent,
    format_power,
    format_temperature,
    get_percent_color,
)
from monoman.Monoman import Monoman


def create_gpu_panel(monoman: Monoman) -> Table:
    """Create the GPU metrics panel."""
    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]GPU[/bold]",
        title_style="bold white",
    )

    if not monoman.gpu.available or not monoman.gpu.gpus:
        table.add_column("Status", ratio=1)
        table.add_row(Text("No GPU detected or GPU monitoring not available", style="dim"))
        return table

    table.add_column("GPU", style="bold", width=25)
    table.add_column("Utilization", width=25)
    table.add_column("Memory", width=30)
    table.add_column("Temp", width=10)
    table.add_column("Power", ratio=1)

    for gpu in monoman.gpu.gpus:
        # GPU name
        name = gpu.name
        if len(name) > 24:
            name = name[:21] + "..."

        # Utilization
        util_color = get_percent_color(gpu.utilization)
        util_text = Text()
        util_text.append(f"{format_percent(gpu.utilization):>6} ", style=f"bold {util_color}")
        util_text.append(create_progress_bar(gpu.utilization, width=15), style=util_color)

        # Memory
        mem_color = get_percent_color(gpu.memory_percent)
        mem_text = Text()
        mem_text.append(f"{format_percent(gpu.memory_percent):>6} ", style=f"bold {mem_color}")
        mem_text.append(f"{format_bytes(gpu.memory_used)}/{format_bytes(gpu.memory_total)}", style="dim")

        # Temperature
        temp_text = Text()
        if gpu.temperature > 0:
            temp_color = "green" if gpu.temperature < 70 else "yellow" if gpu.temperature < 85 else "red"
            temp_text.append(format_temperature(gpu.temperature), style=temp_color)
        else:
            temp_text.append("N/A", style="dim")

        # Power
        power_text = Text()
        if gpu.power_draw > 0:
            power_text.append(format_power(gpu.power_draw), style="cyan")
            if gpu.power_limit > 0:
                power_text.append(f" / {format_power(gpu.power_limit)}", style="dim")
        else:
            power_text.append("N/A", style="dim")

        # Fan speed
        if gpu.fan_speed > 0:
            power_text.append(f" Fan: {gpu.fan_speed:.0f}%", style="dim")

        table.add_row(name, util_text, mem_text, temp_text, power_text)

    # Add driver info
    if monoman.gpu.gpus:
        driver = monoman.gpu.gpus[0].driver_version
        table.add_row(
            "",
            Text(f"Driver: {driver}", style="dim"),
            "",
            "",
            "",
        )

    return table
