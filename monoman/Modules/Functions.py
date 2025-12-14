"""Utility functions for Monoman."""


def format_bytes(size: int | float, precision: int = 1) -> str:
    """Format bytes to human-readable string."""
    if size < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.{precision}f} {units[unit_index]}"


def format_bytes_rate(rate: float, precision: int = 1) -> str:
    """Format bytes per second to human-readable string."""
    return f"{format_bytes(rate, precision)}/s"


def format_number(num: int | float, precision: int = 1) -> str:
    """Format large numbers with K, M, B suffixes."""
    if abs(num) < 1000:
        return str(int(num))

    units = ["", "K", "M", "B", "T"]
    unit_index = 0

    while abs(num) >= 1000 and unit_index < len(units) - 1:
        num /= 1000
        unit_index += 1

    return f"{num:.{precision}f}{units[unit_index]}"


def format_percent(value: float, precision: int = 1) -> str:
    """Format percentage value."""
    return f"{value:.{precision}f}%"


def format_frequency(mhz: float) -> str:
    """Format frequency in MHz to human-readable string."""
    if mhz >= 1000:
        return f"{mhz / 1000:.2f} GHz"
    return f"{mhz:.0f} MHz"


def format_temperature(celsius: float) -> str:
    """Format temperature in Celsius."""
    return f"{celsius:.1f}°C"


def format_power(watts: float) -> str:
    """Format power in watts."""
    return f"{watts:.1f}W"


def create_progress_bar(percent: float, width: int = 20, filled: str = "█", empty: str = "░") -> str:
    """Create a text-based progress bar."""
    percent = max(0, min(100, percent))
    filled_width = int(width * percent / 100)
    empty_width = width - filled_width
    return filled * filled_width + empty * empty_width


def get_percent_color(percent: float) -> str:
    """Get color based on percentage value."""
    if percent < 50:
        return "green"
    elif percent < 75:
        return "yellow"
    elif percent < 90:
        return "orange1"
    else:
        return "red"


def truncate_string(s: str, max_len: int, suffix: str = "...") -> str:
    """Truncate string to max length with suffix."""
    if len(s) <= max_len:
        return s
    return s[: max_len - len(suffix)] + suffix
