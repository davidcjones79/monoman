"""Graph panels showing historical metrics using sparklines."""

from monoman.Modules.Functions import format_bytes_rate, format_percent
from monoman.Modules.MetricManager import MetricManager

# Sparkline characters (increasing height)
SPARK_CHARS = " ▁▂▃▄▅▆▇█"


def _sparkline(data: list[float], width: int = 60, min_val: float = 0, max_val: float | None = None) -> str:
    """Create a sparkline from data."""
    if not data:
        return " " * width

    # Use last 'width' points
    data = data[-width:]

    # Calculate range
    if max_val is None:
        max_val = max(data) if data else 1
    val_range = max_val - min_val
    if val_range == 0:
        val_range = 1

    # Build sparkline
    chars = []
    for val in data:
        # Normalize to 0-1
        normalized = (val - min_val) / val_range
        normalized = max(0, min(1, normalized))
        # Map to character index
        idx = int(normalized * (len(SPARK_CHARS) - 1))
        chars.append(SPARK_CHARS[idx])

    # Pad to width if needed
    result = "".join(chars)
    if len(result) < width:
        result = " " * (width - len(result)) + result

    return result


def _format_bytes_short(value: float) -> str:
    """Format bytes to short human-readable string."""
    if value < 1024:
        return f"{value:.0f}B"
    elif value < 1024 * 1024:
        return f"{value/1024:.0f}K"
    elif value < 1024 * 1024 * 1024:
        return f"{value/(1024*1024):.1f}M"
    else:
        return f"{value/(1024*1024*1024):.1f}G"


def create_cpu_graph(metric_manager: MetricManager, width: int = 60) -> str:
    """Create CPU usage sparkline."""
    cpu_data = metric_manager.series["cpu_total"].values
    current = cpu_data[-1] if cpu_data else 0

    spark = _sparkline(cpu_data, width=width, min_val=0, max_val=100)
    return f"[bold #54efae]CPU[/] {format_percent(current):>6}\n[green]{spark}[/]"


def create_memory_graph(metric_manager: MetricManager, width: int = 60) -> str:
    """Create memory usage sparkline."""
    mem_data = metric_manager.series["memory_percent"].values
    swap_data = metric_manager.series["swap_percent"].values

    current_mem = mem_data[-1] if mem_data else 0
    current_swap = swap_data[-1] if swap_data else 0

    spark_mem = _sparkline(mem_data, width=width, min_val=0, max_val=100)
    spark_swap = _sparkline(swap_data, width=width, min_val=0, max_val=100)

    lines = [
        f"[bold #54efae]RAM[/]  {format_percent(current_mem):>6}",
        f"[green]{spark_mem}[/]",
    ]

    if swap_data and any(v > 0 for v in swap_data):
        lines.append(f"[bold #f0c674]Swap[/] {format_percent(current_swap):>6}")
        lines.append(f"[yellow]{spark_swap}[/]")

    return "\n".join(lines)


def create_network_graph(metric_manager: MetricManager, width: int = 60) -> str:
    """Create network throughput sparkline."""
    recv_data = metric_manager.series["net_recv_rate"].values
    sent_data = metric_manager.series["net_sent_rate"].values

    current_recv = recv_data[-1] if recv_data else 0
    current_sent = sent_data[-1] if sent_data else 0

    # Auto-scale based on max of both
    all_data = recv_data + sent_data
    max_val = max(all_data) * 1.1 if all_data else 1024

    spark_recv = _sparkline(recv_data, width=width, min_val=0, max_val=max_val)
    spark_sent = _sparkline(sent_data, width=width, min_val=0, max_val=max_val)

    return "\n".join([
        f"[bold #54efae]Net ↓[/] {format_bytes_rate(current_recv):>12}",
        f"[green]{spark_recv}[/]",
        f"[bold #91abec]Net ↑[/] {format_bytes_rate(current_sent):>12}",
        f"[cyan]{spark_sent}[/]",
    ])


def create_disk_io_graph(metric_manager: MetricManager, width: int = 60) -> str:
    """Create disk I/O sparkline."""
    read_data = metric_manager.series["disk_read_rate"].values
    write_data = metric_manager.series["disk_write_rate"].values

    current_read = read_data[-1] if read_data else 0
    current_write = write_data[-1] if write_data else 0

    # Auto-scale based on max of both
    all_data = read_data + write_data
    max_val = max(all_data) * 1.1 if all_data else 1024

    spark_read = _sparkline(read_data, width=width, min_val=0, max_val=max_val)
    spark_write = _sparkline(write_data, width=width, min_val=0, max_val=max_val)

    return "\n".join([
        f"[bold #54efae]Read[/]  {format_bytes_rate(current_read):>12}",
        f"[green]{spark_read}[/]",
        f"[bold #f0c674]Write[/] {format_bytes_rate(current_write):>12}",
        f"[yellow]{spark_write}[/]",
    ])


def create_gpu_graph(metric_manager: MetricManager, width: int = 60) -> str:
    """Create GPU usage sparkline."""
    util_data = metric_manager.series["gpu_util"].values
    mem_data = metric_manager.series["gpu_memory"].values
    temp_data = metric_manager.series["gpu_temp"].values

    # Check if we have GPU data
    if not util_data or not any(v > 0 for v in util_data):
        return ""

    current_util = util_data[-1] if util_data else 0
    current_mem = mem_data[-1] if mem_data else 0
    current_temp = temp_data[-1] if temp_data else 0

    spark_util = _sparkline(util_data, width=width, min_val=0, max_val=100)
    spark_mem = _sparkline(mem_data, width=width, min_val=0, max_val=100)

    lines = [
        f"[bold #54efae]GPU[/]  {format_percent(current_util):>6}",
        f"[green]{spark_util}[/]",
        f"[bold #91abec]VRAM[/] {format_percent(current_mem):>6}",
        f"[cyan]{spark_mem}[/]",
    ]

    if current_temp > 0:
        lines[0] = f"[bold #54efae]GPU[/]  {format_percent(current_util):>6}  [#f0c674]{current_temp:.0f}°C[/]"

    return "\n".join(lines)


def create_all_graphs(
    metric_manager: MetricManager,
    show_gpu: bool = True,
    width: int = 60,
    height: int = 6,  # kept for compatibility but unused
) -> str:
    """Create all graphs combined."""
    sections = [
        "[bold #91abec]━━━ Historical Graphs ━━━[/]",
        "",
        create_cpu_graph(metric_manager, width=width),
        "",
        create_memory_graph(metric_manager, width=width),
        "",
        create_network_graph(metric_manager, width=width),
        "",
        create_disk_io_graph(metric_manager, width=width),
    ]

    if show_gpu:
        gpu_graph = create_gpu_graph(metric_manager, width=width)
        if gpu_graph:
            sections.append("")
            sections.append(gpu_graph)

    return "\n".join(sections)
