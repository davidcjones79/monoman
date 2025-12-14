"""Graphs panel widget using Textual's native Sparkline."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label, Sparkline, Static

from monoman.Modules.Functions import format_bytes_rate, format_percent
from monoman.Modules.MetricManager import MetricManager


class GraphsPanel(Container):
    """Panel showing historical graphs using Textual Sparkline widgets."""

    DEFAULT_CSS = """
    GraphsPanel {
        height: auto;
        padding: 0 1;
    }

    GraphsPanel .graph-title {
        text-style: bold;
        color: #91abec;
        margin-bottom: 0;
    }

    GraphsPanel .graph-section {
        height: auto;
        margin-bottom: 0;
    }

    GraphsPanel .graph-label {
        color: #54efae;
        text-style: bold;
    }

    GraphsPanel .graph-value {
        color: #e9e9e9;
    }

    GraphsPanel Sparkline {
        height: 6;
        margin: 0;
    }

    GraphsPanel .cpu-spark > .sparkline--min-color { color: #2d5a3d; }
    GraphsPanel .cpu-spark > .sparkline--max-color { color: #54efae; }

    GraphsPanel .mem-spark > .sparkline--min-color { color: #2d5a3d; }
    GraphsPanel .mem-spark > .sparkline--max-color { color: #54efae; }

    GraphsPanel .swap-spark > .sparkline--min-color { color: #5a4a2d; }
    GraphsPanel .swap-spark > .sparkline--max-color { color: #f0c674; }

    GraphsPanel .net-down-spark > .sparkline--min-color { color: #2d5a3d; }
    GraphsPanel .net-down-spark > .sparkline--max-color { color: #54efae; }

    GraphsPanel .net-up-spark > .sparkline--min-color { color: #2d3d5a; }
    GraphsPanel .net-up-spark > .sparkline--max-color { color: #91abec; }

    GraphsPanel .disk-read-spark > .sparkline--min-color { color: #2d5a3d; }
    GraphsPanel .disk-read-spark > .sparkline--max-color { color: #54efae; }

    GraphsPanel .disk-write-spark > .sparkline--min-color { color: #5a4a2d; }
    GraphsPanel .disk-write-spark > .sparkline--max-color { color: #f0c674; }

    GraphsPanel .gpu-util-spark > .sparkline--min-color { color: #2d5a3d; }
    GraphsPanel .gpu-util-spark > .sparkline--max-color { color: #54efae; }

    GraphsPanel .gpu-mem-spark > .sparkline--min-color { color: #2d3d5a; }
    GraphsPanel .gpu-mem-spark > .sparkline--max-color { color: #91abec; }
    """

    def __init__(
        self,
        metric_manager: MetricManager,
        show_gpu: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.metric_manager = metric_manager
        self.show_gpu = show_gpu

    def compose(self) -> ComposeResult:
        """Compose the graphs panel."""
        yield Static("[bold #91abec]━━━ Historical Graphs ━━━[/]", classes="graph-title")

        # CPU
        with Vertical(classes="graph-section"):
            yield Static("", id="cpu-label")
            yield Sparkline([], id="cpu-spark", classes="cpu-spark")

        # Memory
        with Vertical(classes="graph-section"):
            yield Static("", id="mem-label")
            yield Sparkline([], id="mem-spark", classes="mem-spark")

        # Swap (hidden by default)
        with Vertical(classes="graph-section", id="swap-section"):
            yield Static("", id="swap-label")
            yield Sparkline([], id="swap-spark", classes="swap-spark")

        # Network Down
        with Vertical(classes="graph-section"):
            yield Static("", id="net-down-label")
            yield Sparkline([], id="net-down-spark", classes="net-down-spark")

        # Network Up
        with Vertical(classes="graph-section"):
            yield Static("", id="net-up-label")
            yield Sparkline([], id="net-up-spark", classes="net-up-spark")

        # Disk Read
        with Vertical(classes="graph-section"):
            yield Static("", id="disk-read-label")
            yield Sparkline([], id="disk-read-spark", classes="disk-read-spark")

        # Disk Write
        with Vertical(classes="graph-section"):
            yield Static("", id="disk-write-label")
            yield Sparkline([], id="disk-write-spark", classes="disk-write-spark")

        # GPU (if available)
        if self.show_gpu:
            with Vertical(classes="graph-section", id="gpu-util-section"):
                yield Static("", id="gpu-util-label")
                yield Sparkline([], id="gpu-util-spark", classes="gpu-util-spark")

            with Vertical(classes="graph-section", id="gpu-mem-section"):
                yield Static("", id="gpu-mem-label")
                yield Sparkline([], id="gpu-mem-spark", classes="gpu-mem-spark")

    def update_graphs(self, metric_manager: MetricManager) -> None:
        """Update all sparklines with current data."""
        self.metric_manager = metric_manager

        # CPU
        cpu_data = metric_manager.series["cpu_total"].values
        current_cpu = cpu_data[-1] if cpu_data else 0
        self.query_one("#cpu-label", Static).update(
            f"[bold #54efae]CPU[/]  [#e9e9e9]{format_percent(current_cpu)}[/]"
        )
        self.query_one("#cpu-spark", Sparkline).data = cpu_data or [0]

        # Memory
        mem_data = metric_manager.series["memory_percent"].values
        current_mem = mem_data[-1] if mem_data else 0
        self.query_one("#mem-label", Static).update(
            f"[bold #54efae]RAM[/]  [#e9e9e9]{format_percent(current_mem)}[/]"
        )
        self.query_one("#mem-spark", Sparkline).data = mem_data or [0]

        # Swap
        swap_data = metric_manager.series["swap_percent"].values
        swap_section = self.query_one("#swap-section")
        if swap_data and any(v > 0 for v in swap_data):
            current_swap = swap_data[-1] if swap_data else 0
            self.query_one("#swap-label", Static).update(
                f"[bold #f0c674]Swap[/] [#e9e9e9]{format_percent(current_swap)}[/]"
            )
            self.query_one("#swap-spark", Sparkline).data = swap_data
            swap_section.display = True
        else:
            swap_section.display = False

        # Network
        recv_data = metric_manager.series["net_recv_rate"].values
        sent_data = metric_manager.series["net_sent_rate"].values
        current_recv = recv_data[-1] if recv_data else 0
        current_sent = sent_data[-1] if sent_data else 0

        self.query_one("#net-down-label", Static).update(
            f"[bold #54efae]Net ↓[/] [#e9e9e9]{format_bytes_rate(current_recv)}[/]"
        )
        self.query_one("#net-down-spark", Sparkline).data = recv_data or [0]

        self.query_one("#net-up-label", Static).update(
            f"[bold #91abec]Net ↑[/] [#e9e9e9]{format_bytes_rate(current_sent)}[/]"
        )
        self.query_one("#net-up-spark", Sparkline).data = sent_data or [0]

        # Disk I/O
        read_data = metric_manager.series["disk_read_rate"].values
        write_data = metric_manager.series["disk_write_rate"].values
        current_read = read_data[-1] if read_data else 0
        current_write = write_data[-1] if write_data else 0

        self.query_one("#disk-read-label", Static).update(
            f"[bold #54efae]Read[/]  [#e9e9e9]{format_bytes_rate(current_read)}[/]"
        )
        self.query_one("#disk-read-spark", Sparkline).data = read_data or [0]

        self.query_one("#disk-write-label", Static).update(
            f"[bold #f0c674]Write[/] [#e9e9e9]{format_bytes_rate(current_write)}[/]"
        )
        self.query_one("#disk-write-spark", Sparkline).data = write_data or [0]

        # GPU
        if self.show_gpu:
            util_data = metric_manager.series["gpu_util"].values
            mem_data_gpu = metric_manager.series["gpu_memory"].values
            temp_data = metric_manager.series["gpu_temp"].values

            gpu_util_section = self.query_one("#gpu-util-section")
            gpu_mem_section = self.query_one("#gpu-mem-section")

            if util_data and any(v > 0 for v in util_data):
                current_util = util_data[-1] if util_data else 0
                current_gpu_mem = mem_data_gpu[-1] if mem_data_gpu else 0
                current_temp = temp_data[-1] if temp_data else 0

                temp_str = f"  [#f0c674]{current_temp:.0f}°C[/]" if current_temp > 0 else ""
                self.query_one("#gpu-util-label", Static).update(
                    f"[bold #54efae]GPU[/]  [#e9e9e9]{format_percent(current_util)}[/]{temp_str}"
                )
                self.query_one("#gpu-util-spark", Sparkline).data = util_data

                self.query_one("#gpu-mem-label", Static).update(
                    f"[bold #91abec]VRAM[/] [#e9e9e9]{format_percent(current_gpu_mem)}[/]"
                )
                self.query_one("#gpu-mem-spark", Sparkline).data = mem_data_gpu or [0]

                gpu_util_section.display = True
                gpu_mem_section.display = True
            else:
                gpu_util_section.display = False
                gpu_mem_section.display = False
