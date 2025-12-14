"""Metric manager for time-series data collection."""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from monoman.Monoman import Monoman


@dataclass
class MetricSeries:
    """Time series data for a single metric."""

    name: str
    label: str
    color: str
    visible: bool = True
    max_points: int = 60
    _values: deque = field(default_factory=lambda: deque(maxlen=60))
    _timestamps: deque = field(default_factory=lambda: deque(maxlen=60))

    def __post_init__(self) -> None:
        """Initialize deques with correct maxlen."""
        self._values = deque(maxlen=self.max_points)
        self._timestamps = deque(maxlen=self.max_points)

    def add(self, value: float, timestamp: datetime | None = None) -> None:
        """Add a data point to the series."""
        if timestamp is None:
            timestamp = datetime.now()
        self._values.append(value)
        self._timestamps.append(timestamp)

    @property
    def values(self) -> list[float]:
        """Get list of values."""
        return list(self._values)

    @property
    def timestamps(self) -> list[datetime]:
        """Get list of timestamps."""
        return list(self._timestamps)

    @property
    def latest(self) -> float | None:
        """Get most recent value."""
        return self._values[-1] if self._values else None

    @property
    def min(self) -> float | None:
        """Get minimum value."""
        return min(self._values) if self._values else None

    @property
    def max(self) -> float | None:
        """Get maximum value."""
        return max(self._values) if self._values else None

    @property
    def avg(self) -> float | None:
        """Get average value."""
        if not self._values:
            return None
        return sum(self._values) / len(self._values)


class MetricManager:
    """Manages time-series metrics data for graphing."""

    def __init__(self, max_points: int = 60) -> None:
        self.max_points = max_points
        self.series: dict[str, MetricSeries] = {}
        self._init_series()

    def _init_series(self) -> None:
        """Initialize metric series."""
        # CPU metrics
        self.series["cpu_total"] = MetricSeries(
            name="cpu_total",
            label="CPU Total",
            color="#54efae",
            max_points=self.max_points,
        )
        self.series["cpu_user"] = MetricSeries(
            name="cpu_user",
            label="CPU User",
            color="#91abec",
            max_points=self.max_points,
        )
        self.series["cpu_system"] = MetricSeries(
            name="cpu_system",
            label="CPU System",
            color="#f0c674",
            max_points=self.max_points,
        )

        # Memory metrics
        self.series["memory_percent"] = MetricSeries(
            name="memory_percent",
            label="Memory %",
            color="#54efae",
            max_points=self.max_points,
        )
        self.series["swap_percent"] = MetricSeries(
            name="swap_percent",
            label="Swap %",
            color="#f0c674",
            max_points=self.max_points,
        )

        # Network metrics (totals)
        self.series["net_recv_rate"] = MetricSeries(
            name="net_recv_rate",
            label="Net Download",
            color="#54efae",
            max_points=self.max_points,
        )
        self.series["net_sent_rate"] = MetricSeries(
            name="net_sent_rate",
            label="Net Upload",
            color="#91abec",
            max_points=self.max_points,
        )

        # Disk I/O metrics (totals)
        self.series["disk_read_rate"] = MetricSeries(
            name="disk_read_rate",
            label="Disk Read",
            color="#54efae",
            max_points=self.max_points,
        )
        self.series["disk_write_rate"] = MetricSeries(
            name="disk_write_rate",
            label="Disk Write",
            color="#f0c674",
            max_points=self.max_points,
        )

        # GPU metrics (first GPU)
        self.series["gpu_util"] = MetricSeries(
            name="gpu_util",
            label="GPU Util",
            color="#54efae",
            max_points=self.max_points,
        )
        self.series["gpu_memory"] = MetricSeries(
            name="gpu_memory",
            label="GPU Memory",
            color="#91abec",
            max_points=self.max_points,
        )
        self.series["gpu_temp"] = MetricSeries(
            name="gpu_temp",
            label="GPU Temp",
            color="#f0c674",
            max_points=self.max_points,
        )

    def update(self, monoman: Monoman, timestamp: datetime | None = None) -> None:
        """Update all metric series from current monoman state."""
        if timestamp is None:
            timestamp = datetime.now()

        # CPU metrics
        self.series["cpu_total"].add(monoman.cpu.percent_total, timestamp)
        self.series["cpu_user"].add(monoman.cpu.user_time, timestamp)
        self.series["cpu_system"].add(monoman.cpu.system_time, timestamp)

        # Memory metrics
        self.series["memory_percent"].add(monoman.memory.percent, timestamp)
        self.series["swap_percent"].add(monoman.memory.swap_percent, timestamp)

        # Network rates (sum of all interfaces)
        total_recv = sum(r.get("bytes_recv_rate", 0) for r in monoman.network_rates.values())
        total_sent = sum(r.get("bytes_sent_rate", 0) for r in monoman.network_rates.values())
        self.series["net_recv_rate"].add(total_recv, timestamp)
        self.series["net_sent_rate"].add(total_sent, timestamp)

        # Disk I/O rates (sum of all disks)
        total_read = sum(r.get("read_bytes_rate", 0) for r in monoman.disk_rates.values())
        total_write = sum(r.get("write_bytes_rate", 0) for r in monoman.disk_rates.values())
        self.series["disk_read_rate"].add(total_read, timestamp)
        self.series["disk_write_rate"].add(total_write, timestamp)

        # GPU metrics (first GPU only for now)
        if monoman.gpu.available and monoman.gpu.gpus:
            gpu = monoman.gpu.gpus[0]
            self.series["gpu_util"].add(gpu.utilization, timestamp)
            self.series["gpu_memory"].add(gpu.memory_percent, timestamp)
            self.series["gpu_temp"].add(gpu.temperature, timestamp)

    def get_series(self, name: str) -> MetricSeries | None:
        """Get a metric series by name."""
        return self.series.get(name)

    def get_graph_data(self, *series_names: str) -> dict[str, list[float]]:
        """Get data for graphing multiple series."""
        result = {}
        for name in series_names:
            series = self.series.get(name)
            if series:
                result[name] = series.values
        return result

    def to_dict(self) -> dict[str, Any]:
        """Serialize metric manager state."""
        return {
            name: {
                "values": list(series._values),
                "timestamps": [ts.isoformat() for ts in series._timestamps],
            }
            for name, series in self.series.items()
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        """Restore metric manager state from dict."""
        for name, series_data in data.items():
            if name in self.series:
                series = self.series[name]
                series._values.clear()
                series._timestamps.clear()
                for v in series_data.get("values", []):
                    series._values.append(v)
                for ts in series_data.get("timestamps", []):
                    series._timestamps.append(datetime.fromisoformat(ts))
