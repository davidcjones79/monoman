"""Main Monoman application."""

from datetime import datetime
from pathlib import Path

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Footer, Static

from monoman.Collectors import (
    collect_cpu_metrics,
    collect_disk_metrics,
    collect_gpu_metrics,
    collect_memory_metrics,
    collect_network_metrics,
    collect_process_metrics,
    collect_system_info,
    collect_temperature_metrics,
)
from monoman.Modules.Config import Config, load_config
from monoman.Modules.MetricManager import MetricManager
from monoman.Modules.ReplayManager import (
    RecordingWriter,
    ReplayManager,
    cleanup_old_recordings,
    get_recording_filename,
)
from monoman.Monoman import Monoman
from monoman.Panels import (
    create_cpu_panel,
    create_dashboard_panel,
    create_disk_panel,
    create_gpu_panel,
    create_memory_panel,
    create_network_panel,
    create_processes_panel,
    create_temperature_panel,
)
from monoman.Widgets.GraphsPanel import GraphsPanel
from monoman.Widgets.HelpModal import HelpModal
from monoman.Widgets.TopBar import TopBar


class MonomanApp(App):
    """Monoman TUI Application."""

    CSS_PATH = "Monoman.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("space", "toggle_pause", "Pause"),
        ("plus", "increase_refresh", "+Refresh"),
        ("minus", "decrease_refresh", "-Refresh"),
        ("1", "toggle_dashboard", "Dashboard"),
        ("2", "toggle_cpu", "CPU"),
        ("3", "toggle_memory", "Memory"),
        ("4", "toggle_disk", "Disk"),
        ("5", "toggle_network", "Network"),
        ("6", "toggle_processes", "Processes"),
        ("7", "toggle_gpu", "GPU"),
        ("8", "toggle_temperature", "Temp"),
        ("g", "toggle_graphs", "Graphs"),
        ("c", "sort_cpu", "Sort CPU"),
        ("m", "sort_memory", "Sort Mem"),
        ("p", "sort_pid", "Sort PID"),
        ("n", "sort_name", "Sort Name"),
        ("r", "reverse_sort", "Reverse"),
        ("R", "toggle_recording", "Record"),
    ]

    def __init__(
        self,
        config: Config | None = None,
        replay_path: Path | None = None,
        start_recording: bool = False,
    ) -> None:
        super().__init__()
        self.config = config or Config()
        self.monoman = Monoman(
            refresh_interval=self.config.refresh_interval,
            max_history_points=self.config.max_history_points,
            process_sort_by=self.config.process_sort_by,
            process_sort_reverse=self.config.process_sort_reverse,
            show_all_processes=self.config.show_all_processes,
        )

        # Apply panel visibility from config
        self.monoman.panels.dashboard = self.config.show_dashboard
        self.monoman.panels.cpu = self.config.show_cpu
        self.monoman.panels.memory = self.config.show_memory
        self.monoman.panels.disk = self.config.show_disk
        self.monoman.panels.network = self.config.show_network
        self.monoman.panels.processes = self.config.show_processes
        self.monoman.panels.gpu = self.config.show_gpu
        self.monoman.panels.temperature = self.config.show_temperature

        self.metric_manager = MetricManager(max_points=self.config.max_history_points)

        # Replay mode
        self.replay_manager: ReplayManager | None = None
        if replay_path:
            self.replay_manager = ReplayManager(replay_path)
            self.monoman.is_replaying = True

        # Recording
        self.recording_writer: RecordingWriter | None = None
        if start_recording:
            self._start_recording()

        # Clean up old recordings on startup
        cleanup_old_recordings(self.config.record_dir, self.config.record_retention_hours)

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield TopBar(
            hostname=self.monoman.system_info.hostname,
            refresh_interval=self.monoman.refresh_interval,
            is_paused=self.monoman.pause_refresh,
            is_recording=self.monoman.is_recording,
            is_replaying=self.monoman.is_replaying,
        )

        with VerticalScroll(id="main-content"):
            yield Static(id="dashboard-panel", classes="panel-container")
            yield GraphsPanel(self.metric_manager, show_gpu=self.config.show_gpu, id="graphs-panel", classes="panel-container")
            yield Static(id="cpu-panel", classes="panel-container")
            yield Static(id="memory-panel", classes="panel-container")
            yield Static(id="disk-panel", classes="panel-container")
            yield Static(id="network-panel", classes="panel-container")
            yield Static(id="processes-panel", classes="panel-container")
            yield Static(id="gpu-panel", classes="panel-container")
            yield Static(id="temperature-panel", classes="panel-container")

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        # Collect initial system info
        self.monoman.system_info = collect_system_info()

        # Update top bar with hostname
        top_bar = self.query_one(TopBar)
        top_bar.update_status(hostname=self.monoman.system_info.hostname)

        # Initial data collection
        self._collect_data()

        # Auto-hide GPU and temperature panels if not available
        # (unless user explicitly enabled them in config)
        if not self.monoman.gpu.available and self.config.show_gpu:
            self.monoman.panels.gpu = False
        if not self.monoman.temperature.available and self.config.show_temperature:
            self.monoman.panels.temperature = False

        # Start refresh timer
        self.set_interval(self.monoman.refresh_interval, self._refresh_tick)

        # Update panels
        self._update_panels()

    def _collect_data(self) -> None:
        """Collect all system metrics."""
        if self.monoman.is_replaying and self.replay_manager:
            # Load data from replay
            snapshot = self.replay_manager.current_snapshot
            if snapshot:
                self.monoman.load_snapshot(snapshot)
            return

        timestamp = datetime.now()

        # Collect metrics
        self.monoman.cpu = collect_cpu_metrics()
        self.monoman.memory = collect_memory_metrics()
        self.monoman.disk = collect_disk_metrics(hide_snap_volumes=self.config.hide_snap_volumes)
        self.monoman.network = collect_network_metrics()
        self.monoman.processes = collect_process_metrics(
            include_all=self.monoman.show_all_processes
        )
        self.monoman.gpu = collect_gpu_metrics()
        self.monoman.temperature = collect_temperature_metrics()

        # Update system info (for uptime)
        self.monoman.system_info = collect_system_info()

        # Calculate rates
        self.monoman.calculate_rates(timestamp)

        # Update metric manager
        self.metric_manager.update(self.monoman, timestamp)

        # Record if recording
        if self.recording_writer:
            snapshot = self.monoman.create_snapshot()
            self.recording_writer.write(snapshot)

        self.monoman.last_refresh = timestamp

    def _refresh_tick(self) -> None:
        """Handle refresh timer tick."""
        if self.monoman.pause_refresh:
            return

        if self.monoman.is_replaying and self.replay_manager:
            if self.replay_manager.is_playing:
                snapshot = self.replay_manager.step_forward()
                if snapshot:
                    self.monoman.load_snapshot(snapshot)
                else:
                    # End of replay
                    self.replay_manager.pause()
        else:
            self._collect_data()

        self._update_panels()
        self._update_top_bar()

    def _update_panels(self) -> None:
        """Update all visible panels."""
        # Dashboard
        dashboard = self.query_one("#dashboard-panel", Static)
        if self.monoman.panels.dashboard:
            dashboard.update(create_dashboard_panel(self.monoman))
            dashboard.display = True
        else:
            dashboard.display = False

        # Graphs (historical)
        graphs_panel = self.query_one("#graphs-panel", GraphsPanel)
        if self.monoman.panels.graphs:
            graphs_panel.update_graphs(self.metric_manager)
            graphs_panel.display = True
        else:
            graphs_panel.display = False

        # CPU
        cpu_panel = self.query_one("#cpu-panel", Static)
        if self.monoman.panels.cpu:
            cpu_panel.update(create_cpu_panel(self.monoman))
            cpu_panel.display = True
        else:
            cpu_panel.display = False

        # Memory
        memory_panel = self.query_one("#memory-panel", Static)
        if self.monoman.panels.memory:
            memory_panel.update(create_memory_panel(self.monoman))
            memory_panel.display = True
        else:
            memory_panel.display = False

        # Disk
        disk_panel = self.query_one("#disk-panel", Static)
        if self.monoman.panels.disk:
            disk_panel.update(create_disk_panel(self.monoman))
            disk_panel.display = True
        else:
            disk_panel.display = False

        # Network
        network_panel = self.query_one("#network-panel", Static)
        if self.monoman.panels.network:
            network_panel.update(create_network_panel(self.monoman))
            network_panel.display = True
        else:
            network_panel.display = False

        # Processes
        processes_panel = self.query_one("#processes-panel", Static)
        if self.monoman.panels.processes:
            processes_panel.update(
                create_processes_panel(self.monoman, max_rows=self.config.max_processes)
            )
            processes_panel.display = True
        else:
            processes_panel.display = False

        # GPU
        gpu_panel = self.query_one("#gpu-panel", Static)
        if self.monoman.panels.gpu:
            gpu_panel.update(create_gpu_panel(self.monoman))
            gpu_panel.display = True
        else:
            gpu_panel.display = False

        # Temperature
        temp_panel = self.query_one("#temperature-panel", Static)
        if self.monoman.panels.temperature:
            temp_panel.update(create_temperature_panel(self.monoman))
            temp_panel.display = True
        else:
            temp_panel.display = False

    def _update_top_bar(self) -> None:
        """Update the top bar status."""
        top_bar = self.query_one(TopBar)
        top_bar.update_status(
            is_paused=self.monoman.pause_refresh,
            is_recording=self.monoman.is_recording,
            is_replaying=self.monoman.is_replaying,
            refresh_interval=self.monoman.refresh_interval,
        )

    def _start_recording(self) -> None:
        """Start recording."""
        filename = get_recording_filename()
        path = self.config.record_dir / filename
        self.recording_writer = RecordingWriter(path)
        self.monoman.is_recording = True

    def _stop_recording(self) -> None:
        """Stop recording."""
        if self.recording_writer:
            self.recording_writer.close()
            self.recording_writer = None
        self.monoman.is_recording = False

    # Actions
    def action_help(self) -> None:
        """Show help modal."""
        self.push_screen(HelpModal())

    def action_toggle_pause(self) -> None:
        """Toggle pause."""
        self.monoman.pause_refresh = not self.monoman.pause_refresh
        self._update_top_bar()

    def action_increase_refresh(self) -> None:
        """Increase refresh interval."""
        self.monoman.refresh_interval = min(10.0, self.monoman.refresh_interval + 0.5)
        self._update_top_bar()

    def action_decrease_refresh(self) -> None:
        """Decrease refresh interval."""
        self.monoman.refresh_interval = max(0.5, self.monoman.refresh_interval - 0.5)
        self._update_top_bar()

    def action_toggle_dashboard(self) -> None:
        """Toggle dashboard panel."""
        self.monoman.toggle_panel("dashboard")
        self._update_panels()

    def action_toggle_cpu(self) -> None:
        """Toggle CPU panel."""
        self.monoman.toggle_panel("cpu")
        self._update_panels()

    def action_toggle_memory(self) -> None:
        """Toggle memory panel."""
        self.monoman.toggle_panel("memory")
        self._update_panels()

    def action_toggle_disk(self) -> None:
        """Toggle disk panel."""
        self.monoman.toggle_panel("disk")
        self._update_panels()

    def action_toggle_network(self) -> None:
        """Toggle network panel."""
        self.monoman.toggle_panel("network")
        self._update_panels()

    def action_toggle_processes(self) -> None:
        """Toggle processes panel."""
        self.monoman.toggle_panel("processes")
        self._update_panels()

    def action_toggle_gpu(self) -> None:
        """Toggle GPU panel."""
        self.monoman.toggle_panel("gpu")
        self._update_panels()

    def action_toggle_temperature(self) -> None:
        """Toggle temperature panel."""
        self.monoman.toggle_panel("temperature")
        self._update_panels()

    def action_toggle_graphs(self) -> None:
        """Toggle historical graphs panel."""
        self.monoman.toggle_panel("graphs")
        self._update_panels()

    def action_sort_cpu(self) -> None:
        """Sort processes by CPU."""
        self.monoman.process_sort_by = "cpu"
        self._update_panels()

    def action_sort_memory(self) -> None:
        """Sort processes by memory."""
        self.monoman.process_sort_by = "memory"
        self._update_panels()

    def action_sort_pid(self) -> None:
        """Sort processes by PID."""
        self.monoman.process_sort_by = "pid"
        self._update_panels()

    def action_sort_name(self) -> None:
        """Sort processes by name."""
        self.monoman.process_sort_by = "name"
        self._update_panels()

    def action_reverse_sort(self) -> None:
        """Reverse sort order."""
        self.monoman.process_sort_reverse = not self.monoman.process_sort_reverse
        self._update_panels()

    def action_toggle_recording(self) -> None:
        """Toggle recording."""
        if self.monoman.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
        self._update_top_bar()

    def on_unmount(self) -> None:
        """Handle unmount - cleanup."""
        if self.recording_writer:
            self._stop_recording()
        if self.replay_manager:
            self.replay_manager.close()


def main() -> None:
    """Main entry point."""
    config, args = load_config()

    replay_path = None
    if args.replay:
        replay_path = Path(args.replay)

    app = MonomanApp(
        config=config,
        replay_path=replay_path,
        start_recording=args.record,
    )
    app.run()


if __name__ == "__main__":
    main()
