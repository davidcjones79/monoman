"""Temperature panel showing sensor readings."""

from rich.table import Table
from rich.text import Text

from monoman.Modules.Functions import create_progress_bar, format_temperature
from monoman.Monoman import Monoman


def create_temperature_panel(monoman: Monoman) -> Table:
    """Create the temperature metrics panel."""
    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]Temperature[/bold]",
        title_style="bold white",
    )

    if not monoman.temperature.available or not monoman.temperature.sensors:
        table.add_column("Status", ratio=1)
        table.add_row(
            Text(
                "Temperature sensors not available (requires Linux with lm-sensors)",
                style="dim",
            )
        )
        return table

    table.add_column("Sensor", style="bold", width=20)
    table.add_column("Label", width=20)
    table.add_column("Current", width=12)
    table.add_column("Status", width=30)
    table.add_column("Limits", ratio=1)

    for sensor_name, readings in monoman.temperature.sensors.items():
        for i, reading in enumerate(readings):
            # Sensor name (only show on first reading)
            sensor_display = sensor_name if i == 0 else ""

            # Label
            label = reading.label or f"Sensor {i}"

            # Current temperature
            current = reading.current
            temp_text = Text(format_temperature(current))

            # Determine color and status based on limits
            status_text = Text()
            if reading.critical and current >= reading.critical:
                temp_text.stylize("bold red")
                status_text.append("CRITICAL ", style="bold red")
                status_text.append(create_progress_bar(100, width=15), style="red")
            elif reading.high and current >= reading.high:
                temp_text.stylize("bold yellow")
                status_text.append("HIGH ", style="bold yellow")
                # Calculate percentage between normal and high
                percent = min(100, (current / reading.high) * 100)
                status_text.append(create_progress_bar(percent, width=15), style="yellow")
            elif reading.high:
                # Calculate percentage of high limit
                percent = (current / reading.high) * 100
                if percent > 80:
                    temp_text.stylize("yellow")
                    status_text.append("WARM ", style="yellow")
                else:
                    temp_text.stylize("green")
                    status_text.append("OK ", style="green")
                status_text.append(create_progress_bar(percent, width=15), style="green")
            else:
                temp_text.stylize("white")
                status_text.append("N/A", style="dim")

            # Limits
            limits_text = Text()
            if reading.high:
                limits_text.append(f"High: {format_temperature(reading.high)}", style="yellow")
            if reading.critical:
                if reading.high:
                    limits_text.append(" | ", style="dim")
                limits_text.append(f"Crit: {format_temperature(reading.critical)}", style="red")
            if not reading.high and not reading.critical:
                limits_text.append("No limits defined", style="dim")

            table.add_row(sensor_display, label, temp_text, status_text, limits_text)

    return table
