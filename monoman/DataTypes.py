"""Data types and models for Monoman."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class PanelType(Enum):
    """Panel types available in Monoman."""

    DASHBOARD = auto()
    CPU = auto()
    MEMORY = auto()
    DISK = auto()
    NETWORK = auto()
    PROCESSES = auto()
    GPU = auto()
    TEMPERATURE = auto()


@dataclass
class PanelVisibility:
    """Tracks which panels are visible."""

    dashboard: bool = True
    cpu: bool = True
    memory: bool = True
    disk: bool = True
    network: bool = True
    processes: bool = True
    gpu: bool = True
    temperature: bool = True
    graphs: bool = False  # Historical graphs view


@dataclass
class CPUMetrics:
    """CPU metrics data."""

    percent_total: float = 0.0
    percent_per_core: list[float] = field(default_factory=list)
    load_avg_1: float = 0.0
    load_avg_5: float = 0.0
    load_avg_15: float = 0.0
    frequency_current: float = 0.0
    frequency_max: float = 0.0
    core_count: int = 0
    thread_count: int = 0
    ctx_switches: int = 0
    interrupts: int = 0
    user_time: float = 0.0
    system_time: float = 0.0
    idle_time: float = 0.0
    iowait_time: float = 0.0


@dataclass
class MemoryMetrics:
    """Memory metrics data."""

    total: int = 0
    available: int = 0
    used: int = 0
    free: int = 0
    percent: float = 0.0
    cached: int = 0
    buffers: int = 0
    swap_total: int = 0
    swap_used: int = 0
    swap_free: int = 0
    swap_percent: float = 0.0


@dataclass
class DiskIOMetrics:
    """Disk I/O metrics for a single disk."""

    device: str = ""
    read_bytes: int = 0
    write_bytes: int = 0
    read_count: int = 0
    write_count: int = 0
    read_time: int = 0
    write_time: int = 0
    busy_time: int = 0


@dataclass
class DiskPartitionMetrics:
    """Disk partition/mount metrics."""

    device: str = ""
    mountpoint: str = ""
    fstype: str = ""
    total: int = 0
    used: int = 0
    free: int = 0
    percent: float = 0.0


@dataclass
class DiskMetrics:
    """Combined disk metrics."""

    partitions: list[DiskPartitionMetrics] = field(default_factory=list)
    io: dict[str, DiskIOMetrics] = field(default_factory=dict)


@dataclass
class NetworkInterfaceMetrics:
    """Network metrics for a single interface."""

    name: str = ""
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    errors_in: int = 0
    errors_out: int = 0
    drops_in: int = 0
    drops_out: int = 0
    is_up: bool = False
    speed: int = 0  # Mbps
    addresses: list[str] = field(default_factory=list)


@dataclass
class NetworkMetrics:
    """Combined network metrics."""

    interfaces: dict[str, NetworkInterfaceMetrics] = field(default_factory=dict)
    connections_count: int = 0


@dataclass
class ProcessMetrics:
    """Metrics for a single process."""

    pid: int = 0
    name: str = ""
    username: str = ""
    status: str = ""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_rss: int = 0
    memory_vms: int = 0
    threads: int = 0
    create_time: float = 0.0
    cmdline: str = ""
    nice: int = 0
    io_read_bytes: int = 0
    io_write_bytes: int = 0


@dataclass
class ProcessListMetrics:
    """Process list metrics."""

    processes: list[ProcessMetrics] = field(default_factory=list)
    total_count: int = 0
    running_count: int = 0
    sleeping_count: int = 0
    stopped_count: int = 0


@dataclass
class GPUMetrics:
    """GPU metrics for a single GPU."""

    index: int = 0
    name: str = ""
    driver_version: str = ""
    memory_total: int = 0
    memory_used: int = 0
    memory_free: int = 0
    memory_percent: float = 0.0
    utilization: float = 0.0
    temperature: float = 0.0
    fan_speed: float = 0.0
    power_draw: float = 0.0
    power_limit: float = 0.0


@dataclass
class GPUListMetrics:
    """Combined GPU metrics."""

    gpus: list[GPUMetrics] = field(default_factory=list)
    available: bool = False


@dataclass
class TemperatureReading:
    """Single temperature sensor reading."""

    label: str = ""
    current: float = 0.0
    high: float | None = None
    critical: float | None = None


@dataclass
class GroupedTemperature:
    """Grouped/summarized temperature reading."""

    name: str = ""  # Human-friendly name (e.g., "CPU", "Battery")
    current: float = 0.0  # Current temperature (max or avg depending on group)
    high: float | None = None
    critical: float | None = None
    source_labels: list[str] = field(default_factory=list)  # Original sensor labels


@dataclass
class TemperatureMetrics:
    """Combined temperature metrics."""

    sensors: dict[str, list[TemperatureReading]] = field(default_factory=dict)
    grouped: list[GroupedTemperature] = field(default_factory=list)  # Summarized view
    available: bool = False


@dataclass
class SystemInfo:
    """Static system information."""

    hostname: str = ""
    platform: str = ""
    platform_release: str = ""
    platform_version: str = ""
    architecture: str = ""
    processor: str = ""
    python_version: str = ""
    boot_time: datetime | None = None
    uptime_seconds: float = 0.0


@dataclass
class Snapshot:
    """Complete system metrics snapshot at a point in time."""

    timestamp: datetime = field(default_factory=datetime.now)
    system_info: SystemInfo = field(default_factory=SystemInfo)
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    disk: DiskMetrics = field(default_factory=DiskMetrics)
    network: NetworkMetrics = field(default_factory=NetworkMetrics)
    processes: ProcessListMetrics = field(default_factory=ProcessListMetrics)
    gpu: GPUListMetrics = field(default_factory=GPUListMetrics)
    temperature: TemperatureMetrics = field(default_factory=TemperatureMetrics)

    def to_dict(self) -> dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        import dataclasses

        def convert(obj: Any) -> Any:
            if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
                return {k: convert(v) for k, v in dataclasses.asdict(obj).items()}
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            return obj

        return convert(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snapshot":
        """Create snapshot from dictionary."""
        # Parse timestamp
        timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))

        # Parse system info
        sys_data = data.get("system_info", {})
        boot_time = None
        if sys_data.get("boot_time"):
            boot_time = datetime.fromisoformat(sys_data["boot_time"])
        system_info = SystemInfo(
            hostname=sys_data.get("hostname", ""),
            platform=sys_data.get("platform", ""),
            platform_release=sys_data.get("platform_release", ""),
            platform_version=sys_data.get("platform_version", ""),
            architecture=sys_data.get("architecture", ""),
            processor=sys_data.get("processor", ""),
            python_version=sys_data.get("python_version", ""),
            boot_time=boot_time,
            uptime_seconds=sys_data.get("uptime_seconds", 0.0),
        )

        # Parse CPU metrics
        cpu_data = data.get("cpu", {})
        cpu = CPUMetrics(**{k: v for k, v in cpu_data.items() if k in CPUMetrics.__dataclass_fields__})

        # Parse memory metrics
        mem_data = data.get("memory", {})
        memory = MemoryMetrics(**{k: v for k, v in mem_data.items() if k in MemoryMetrics.__dataclass_fields__})

        # Parse disk metrics
        disk_data = data.get("disk", {})
        partitions = [DiskPartitionMetrics(**p) for p in disk_data.get("partitions", [])]
        io = {k: DiskIOMetrics(**v) for k, v in disk_data.get("io", {}).items()}
        disk = DiskMetrics(partitions=partitions, io=io)

        # Parse network metrics
        net_data = data.get("network", {})
        interfaces = {k: NetworkInterfaceMetrics(**v) for k, v in net_data.get("interfaces", {}).items()}
        network = NetworkMetrics(interfaces=interfaces, connections_count=net_data.get("connections_count", 0))

        # Parse process metrics
        proc_data = data.get("processes", {})
        processes_list = [ProcessMetrics(**p) for p in proc_data.get("processes", [])]
        processes = ProcessListMetrics(
            processes=processes_list,
            total_count=proc_data.get("total_count", 0),
            running_count=proc_data.get("running_count", 0),
            sleeping_count=proc_data.get("sleeping_count", 0),
            stopped_count=proc_data.get("stopped_count", 0),
        )

        # Parse GPU metrics
        gpu_data = data.get("gpu", {})
        gpus = [GPUMetrics(**g) for g in gpu_data.get("gpus", [])]
        gpu = GPUListMetrics(gpus=gpus, available=gpu_data.get("available", False))

        # Parse temperature metrics
        temp_data = data.get("temperature", {})
        sensors = {}
        for sensor_name, readings in temp_data.get("sensors", {}).items():
            sensors[sensor_name] = [TemperatureReading(**r) for r in readings]
        grouped = [GroupedTemperature(**g) for g in temp_data.get("grouped", [])]
        temperature = TemperatureMetrics(
            sensors=sensors,
            grouped=grouped,
            available=temp_data.get("available", False)
        )

        return cls(
            timestamp=timestamp,
            system_info=system_info,
            cpu=cpu,
            memory=memory,
            disk=disk,
            network=network,
            processes=processes,
            gpu=gpu,
            temperature=temperature,
        )


@dataclass
class MetricDataPoint:
    """Single data point for a metric time series."""

    timestamp: datetime
    value: float


@dataclass
class MetricSeries:
    """Time series data for a single metric."""

    name: str
    label: str
    color: str
    visible: bool = True
    data: list[MetricDataPoint] = field(default_factory=list)
    max_points: int = 60

    def add(self, value: float, timestamp: datetime | None = None) -> None:
        """Add a data point to the series."""
        if timestamp is None:
            timestamp = datetime.now()
        self.data.append(MetricDataPoint(timestamp=timestamp, value=value))
        if len(self.data) > self.max_points:
            self.data.pop(0)

    def values(self) -> list[float]:
        """Get list of values."""
        return [p.value for p in self.data]

    def latest(self) -> float | None:
        """Get most recent value."""
        return self.data[-1].value if self.data else None
