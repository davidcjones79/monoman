"""Core Monoman state and data model."""

from dataclasses import dataclass, field
from datetime import datetime

from monoman.DataTypes import (
    CPUMetrics,
    DiskMetrics,
    GPUListMetrics,
    MemoryMetrics,
    NetworkMetrics,
    PanelVisibility,
    ProcessListMetrics,
    Snapshot,
    SystemInfo,
    TemperatureMetrics,
)


@dataclass
class Monoman:
    """Central state manager for Monoman application."""

    # Configuration
    refresh_interval: float = 1.0
    max_history_points: int = 60
    process_sort_by: str = "cpu"  # cpu, memory, pid, name
    process_sort_reverse: bool = True
    process_filter: str = ""
    show_all_processes: bool = False  # Include system processes

    # Panel visibility
    panels: PanelVisibility = field(default_factory=PanelVisibility)

    # Current metrics
    system_info: SystemInfo = field(default_factory=SystemInfo)
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    disk: DiskMetrics = field(default_factory=DiskMetrics)
    network: NetworkMetrics = field(default_factory=NetworkMetrics)
    processes: ProcessListMetrics = field(default_factory=ProcessListMetrics)
    gpu: GPUListMetrics = field(default_factory=GPUListMetrics)
    temperature: TemperatureMetrics = field(default_factory=TemperatureMetrics)

    # Previous metrics for rate calculations
    _prev_network: NetworkMetrics | None = None
    _prev_disk: DiskMetrics | None = None
    _prev_timestamp: datetime | None = None

    # Rate calculations (bytes/sec)
    network_rates: dict[str, dict[str, float]] = field(default_factory=dict)
    disk_rates: dict[str, dict[str, float]] = field(default_factory=dict)

    # State flags
    pause_refresh: bool = False
    is_recording: bool = False
    is_replaying: bool = False

    # Timing
    last_refresh: datetime | None = None
    polling_latency: float = 0.0

    def create_snapshot(self) -> Snapshot:
        """Create a snapshot of current metrics."""
        return Snapshot(
            timestamp=datetime.now(),
            system_info=self.system_info,
            cpu=self.cpu,
            memory=self.memory,
            disk=self.disk,
            network=self.network,
            processes=self.processes,
            gpu=self.gpu,
            temperature=self.temperature,
        )

    def load_snapshot(self, snapshot: Snapshot) -> None:
        """Load metrics from a snapshot."""
        self.system_info = snapshot.system_info
        self.cpu = snapshot.cpu
        self.memory = snapshot.memory
        self.disk = snapshot.disk
        self.network = snapshot.network
        self.processes = snapshot.processes
        self.gpu = snapshot.gpu
        self.temperature = snapshot.temperature
        self.last_refresh = snapshot.timestamp

    def calculate_rates(self, timestamp: datetime) -> None:
        """Calculate rates for network and disk I/O."""
        if self._prev_timestamp is None:
            self._prev_timestamp = timestamp
            self._prev_network = self.network
            self._prev_disk = self.disk
            return

        elapsed = (timestamp - self._prev_timestamp).total_seconds()
        if elapsed <= 0:
            return

        # Calculate network rates
        if self._prev_network:
            for name, iface in self.network.interfaces.items():
                prev_iface = self._prev_network.interfaces.get(name)
                if prev_iface:
                    self.network_rates[name] = {
                        "bytes_sent_rate": (iface.bytes_sent - prev_iface.bytes_sent) / elapsed,
                        "bytes_recv_rate": (iface.bytes_recv - prev_iface.bytes_recv) / elapsed,
                        "packets_sent_rate": (iface.packets_sent - prev_iface.packets_sent) / elapsed,
                        "packets_recv_rate": (iface.packets_recv - prev_iface.packets_recv) / elapsed,
                    }

        # Calculate disk I/O rates
        if self._prev_disk:
            for device, io in self.disk.io.items():
                prev_io = self._prev_disk.io.get(device)
                if prev_io:
                    self.disk_rates[device] = {
                        "read_bytes_rate": (io.read_bytes - prev_io.read_bytes) / elapsed,
                        "write_bytes_rate": (io.write_bytes - prev_io.write_bytes) / elapsed,
                        "read_count_rate": (io.read_count - prev_io.read_count) / elapsed,
                        "write_count_rate": (io.write_count - prev_io.write_count) / elapsed,
                    }

        self._prev_timestamp = timestamp
        self._prev_network = self.network
        self._prev_disk = self.disk

    def toggle_panel(self, panel_name: str) -> bool:
        """Toggle panel visibility. Returns new state."""
        if hasattr(self.panels, panel_name):
            current = getattr(self.panels, panel_name)
            setattr(self.panels, panel_name, not current)
            return not current
        return False

    def get_sorted_processes(self) -> list:
        """Get processes sorted according to current settings."""
        processes = self.processes.processes

        # Apply filter
        if self.process_filter:
            filter_lower = self.process_filter.lower()
            processes = [
                p
                for p in processes
                if filter_lower in p.name.lower()
                or filter_lower in p.username.lower()
                or filter_lower in p.cmdline.lower()
            ]

        # Sort
        sort_key = {
            "cpu": lambda p: p.cpu_percent,
            "memory": lambda p: p.memory_percent,
            "pid": lambda p: p.pid,
            "name": lambda p: p.name.lower(),
            "user": lambda p: p.username.lower(),
        }.get(self.process_sort_by, lambda p: p.cpu_percent)

        return sorted(processes, key=sort_key, reverse=self.process_sort_reverse)

    def format_uptime(self) -> str:
        """Format uptime as human-readable string."""
        seconds = self.system_info.uptime_seconds
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)
