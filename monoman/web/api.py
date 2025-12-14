"""FastAPI web server for Monoman."""

import asyncio
import json
import logging
import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
from monoman.DataTypes import Snapshot
from monoman.Monoman import Monoman
from monoman.Modules.MetricManager import MetricManager

logger = logging.getLogger(__name__)

# History file locations
HISTORY_DIR = Path.home() / ".monoman"
HISTORY_FILE = HISTORY_DIR / "web_history.json"
LONG_HISTORY_FILE = HISTORY_DIR / "web_history_long.json"


@dataclass
class TimestampedMetrics:
    """A single timestamped metrics snapshot for long-term storage."""
    timestamp: float  # Unix timestamp
    cpu_total: float
    cpu_user: float
    cpu_system: float
    memory_percent: float
    swap_percent: float
    net_recv_rate: float
    net_sent_rate: float
    disk_read_rate: float
    disk_write_rate: float
    gpu_util: float = 0.0
    gpu_memory: float = 0.0
    gpu_temp: float = 0.0

    def to_dict(self) -> dict:
        return {
            "t": self.timestamp,
            "cpu": self.cpu_total,
            "cpu_u": self.cpu_user,
            "cpu_s": self.cpu_system,
            "mem": self.memory_percent,
            "swap": self.swap_percent,
            "net_in": self.net_recv_rate,
            "net_out": self.net_sent_rate,
            "disk_r": self.disk_read_rate,
            "disk_w": self.disk_write_rate,
            "gpu": self.gpu_util,
            "gpu_mem": self.gpu_memory,
            "gpu_t": self.gpu_temp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TimestampedMetrics":
        return cls(
            timestamp=d["t"],
            cpu_total=d.get("cpu", 0),
            cpu_user=d.get("cpu_u", 0),
            cpu_system=d.get("cpu_s", 0),
            memory_percent=d.get("mem", 0),
            swap_percent=d.get("swap", 0),
            net_recv_rate=d.get("net_in", 0),
            net_sent_rate=d.get("net_out", 0),
            disk_read_rate=d.get("disk_r", 0),
            disk_write_rate=d.get("disk_w", 0),
            gpu_util=d.get("gpu", 0),
            gpu_memory=d.get("gpu_mem", 0),
            gpu_temp=d.get("gpu_t", 0),
        )


class LongTermHistory:
    """Manages long-term historical data with different resolutions."""

    def __init__(self):
        # Store data at different resolutions
        # 1-second resolution for last 5 minutes (300 points)
        self.recent: deque[TimestampedMetrics] = deque(maxlen=300)
        # 10-second resolution for last hour (360 points)
        self.hourly: deque[TimestampedMetrics] = deque(maxlen=360)
        # 1-minute resolution for last 24 hours (1440 points)
        self.daily: deque[TimestampedMetrics] = deque(maxlen=1440)
        # 5-minute resolution for last 7 days (2016 points)
        self.weekly: deque[TimestampedMetrics] = deque(maxlen=2016)

        self._last_hourly_time = 0.0
        self._last_daily_time = 0.0
        self._last_weekly_time = 0.0
        self._accumulator: list[TimestampedMetrics] = []

    def add(self, metrics: TimestampedMetrics) -> None:
        """Add a new metrics snapshot."""
        now = metrics.timestamp

        # Always add to recent (1-second resolution)
        self.recent.append(metrics)
        self._accumulator.append(metrics)

        # Add to hourly every 10 seconds
        if now - self._last_hourly_time >= 10:
            avg = self._average_metrics(self._accumulator)
            if avg:
                self.hourly.append(avg)
            self._last_hourly_time = now

        # Add to daily every 60 seconds
        if now - self._last_daily_time >= 60:
            avg = self._average_metrics(self._accumulator)
            if avg:
                self.daily.append(avg)
            self._last_daily_time = now
            self._accumulator = []  # Reset accumulator after daily update

        # Add to weekly every 5 minutes
        if now - self._last_weekly_time >= 300:
            # Use the daily point for weekly
            if self.daily:
                self.weekly.append(self.daily[-1])
            self._last_weekly_time = now

    def _average_metrics(self, metrics_list: list[TimestampedMetrics]) -> TimestampedMetrics | None:
        """Average a list of metrics."""
        if not metrics_list:
            return None

        n = len(metrics_list)
        return TimestampedMetrics(
            timestamp=metrics_list[-1].timestamp,
            cpu_total=sum(m.cpu_total for m in metrics_list) / n,
            cpu_user=sum(m.cpu_user for m in metrics_list) / n,
            cpu_system=sum(m.cpu_system for m in metrics_list) / n,
            memory_percent=sum(m.memory_percent for m in metrics_list) / n,
            swap_percent=sum(m.swap_percent for m in metrics_list) / n,
            net_recv_rate=sum(m.net_recv_rate for m in metrics_list) / n,
            net_sent_rate=sum(m.net_sent_rate for m in metrics_list) / n,
            disk_read_rate=sum(m.disk_read_rate for m in metrics_list) / n,
            disk_write_rate=sum(m.disk_write_rate for m in metrics_list) / n,
            gpu_util=sum(m.gpu_util for m in metrics_list) / n,
            gpu_memory=sum(m.gpu_memory for m in metrics_list) / n,
            gpu_temp=sum(m.gpu_temp for m in metrics_list) / n,
        )

    def get_range(self, range_type: str) -> list[dict]:
        """Get data for a specific time range."""
        if range_type == "5m":
            return [m.to_dict() for m in self.recent]
        elif range_type == "30m":
            # Last 30 min from hourly (180 points at 10s resolution)
            cutoff = time.time() - 30 * 60
            return [m.to_dict() for m in self.hourly if m.timestamp >= cutoff]
        elif range_type == "1h":
            return [m.to_dict() for m in self.hourly]
        elif range_type == "6h":
            # Last 6 hours from daily
            cutoff = time.time() - 6 * 60 * 60
            return [m.to_dict() for m in self.daily if m.timestamp >= cutoff]
        elif range_type == "24h":
            return [m.to_dict() for m in self.daily]
        elif range_type == "7d":
            return [m.to_dict() for m in self.weekly]
        else:
            return [m.to_dict() for m in self.recent]

    def to_dict(self) -> dict:
        """Serialize for saving."""
        return {
            "recent": [m.to_dict() for m in self.recent],
            "hourly": [m.to_dict() for m in self.hourly],
            "daily": [m.to_dict() for m in self.daily],
            "weekly": [m.to_dict() for m in self.weekly],
            "last_hourly_time": self._last_hourly_time,
            "last_daily_time": self._last_daily_time,
            "last_weekly_time": self._last_weekly_time,
        }

    def from_dict(self, data: dict) -> None:
        """Deserialize from saved data."""
        self.recent = deque(
            [TimestampedMetrics.from_dict(m) for m in data.get("recent", [])],
            maxlen=300
        )
        self.hourly = deque(
            [TimestampedMetrics.from_dict(m) for m in data.get("hourly", [])],
            maxlen=360
        )
        self.daily = deque(
            [TimestampedMetrics.from_dict(m) for m in data.get("daily", [])],
            maxlen=1440
        )
        self.weekly = deque(
            [TimestampedMetrics.from_dict(m) for m in data.get("weekly", [])],
            maxlen=2016
        )
        self._last_hourly_time = data.get("last_hourly_time", 0)
        self._last_daily_time = data.get("last_daily_time", 0)
        self._last_weekly_time = data.get("last_weekly_time", 0)


class MetricsCollector:
    """Background metrics collector with WebSocket broadcasting."""

    def __init__(self, max_history_points: int = 300) -> None:
        self.monoman = Monoman()
        self.metric_manager = MetricManager(max_points=max_history_points)
        self.long_history = LongTermHistory()
        self.connections: list[WebSocket] = []
        self._task: asyncio.Task | None = None
        self._running = False
        self._save_counter = 0
        self._load_history()

    def _load_history(self) -> None:
        """Load historical data from disk."""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, "r") as f:
                    data = json.load(f)
                self.metric_manager.from_dict(data.get("metrics", {}))
                if "config" in data:
                    self.monoman.refresh_interval = data["config"].get(
                        "refresh_interval", 1.0
                    )
                logger.info("Loaded short-term history from %s", HISTORY_FILE)
        except Exception as e:
            logger.warning("Could not load short-term history: %s", e)

        try:
            if LONG_HISTORY_FILE.exists():
                with open(LONG_HISTORY_FILE, "r") as f:
                    data = json.load(f)
                self.long_history.from_dict(data)
                logger.info("Loaded long-term history from %s", LONG_HISTORY_FILE)
        except Exception as e:
            logger.warning("Could not load long-term history: %s", e)

    def _save_history(self) -> None:
        """Save historical data to disk."""
        try:
            HISTORY_DIR.mkdir(parents=True, exist_ok=True)

            # Save short-term history
            data = {
                "metrics": self.metric_manager.to_dict(),
                "config": {
                    "refresh_interval": self.monoman.refresh_interval,
                },
                "saved_at": datetime.now().isoformat(),
            }
            with open(HISTORY_FILE, "w") as f:
                json.dump(data, f)

            # Save long-term history
            with open(LONG_HISTORY_FILE, "w") as f:
                json.dump(self.long_history.to_dict(), f)
        except Exception as e:
            logger.warning("Could not save history: %s", e)

    async def start(self) -> None:
        """Start the background collection task."""
        self._running = True
        self._task = asyncio.create_task(self._collect_loop())

    async def stop(self) -> None:
        """Stop the background collection task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._save_history()

    async def _collect_loop(self) -> None:
        """Main collection loop."""
        while self._running:
            try:
                await self._collect_and_broadcast()
                await asyncio.sleep(self.monoman.refresh_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Collection error: %s", e)
                await asyncio.sleep(1)

    async def _collect_and_broadcast(self) -> None:
        """Collect metrics and broadcast to all connected clients."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._collect_metrics)

        if self.connections:
            data = self.get_snapshot_with_history()

            disconnected = []
            for ws in self.connections:
                try:
                    await ws.send_json(data)
                except Exception:
                    disconnected.append(ws)

            for ws in disconnected:
                self.connections.remove(ws)

    def _collect_metrics(self) -> None:
        """Collect all metrics (runs in thread pool)."""
        timestamp = datetime.now()
        unix_ts = timestamp.timestamp()

        self.monoman.system_info = collect_system_info()
        self.monoman.cpu = collect_cpu_metrics()
        self.monoman.memory = collect_memory_metrics()
        self.monoman.disk = collect_disk_metrics()
        self.monoman.network = collect_network_metrics()
        self.monoman.processes = collect_process_metrics()
        self.monoman.gpu = collect_gpu_metrics()
        self.monoman.temperature = collect_temperature_metrics()
        self.monoman.calculate_rates(timestamp)
        self.monoman.last_refresh = timestamp

        # Update metric manager
        self.metric_manager.update(self.monoman, timestamp)

        # Calculate network/disk rates
        total_net_recv = sum(r.get("bytes_recv_rate", 0) for r in self.monoman.network_rates.values())
        total_net_sent = sum(r.get("bytes_sent_rate", 0) for r in self.monoman.network_rates.values())
        total_disk_read = sum(r.get("read_bytes_rate", 0) for r in self.monoman.disk_rates.values())
        total_disk_write = sum(r.get("write_bytes_rate", 0) for r in self.monoman.disk_rates.values())

        # GPU metrics
        gpu_util = 0.0
        gpu_memory = 0.0
        gpu_temp = 0.0
        if self.monoman.gpu and self.monoman.gpu.available and self.monoman.gpu.gpus:
            gpu = self.monoman.gpu.gpus[0]
            gpu_util = gpu.utilization
            gpu_memory = gpu.memory_percent
            gpu_temp = gpu.temperature

        # Add to long-term history
        self.long_history.add(TimestampedMetrics(
            timestamp=unix_ts,
            cpu_total=self.monoman.cpu.percent_total,
            cpu_user=self.monoman.cpu.user_time,
            cpu_system=self.monoman.cpu.system_time,
            memory_percent=self.monoman.memory.percent,
            swap_percent=self.monoman.memory.swap_percent,
            net_recv_rate=total_net_recv,
            net_sent_rate=total_net_sent,
            disk_read_rate=total_disk_read,
            disk_write_rate=total_disk_write,
            gpu_util=gpu_util,
            gpu_memory=gpu_memory,
            gpu_temp=gpu_temp,
        ))

        # Save periodically
        self._save_counter += 1
        if self._save_counter >= 30:
            self._save_counter = 0
            self._save_history()

    def get_snapshot(self) -> dict[str, Any]:
        """Get current metrics as dictionary."""
        snapshot = self.monoman.create_snapshot()
        data = snapshot.to_dict()
        data["network_rates"] = self.monoman.network_rates
        data["disk_rates"] = self.monoman.disk_rates
        return data

    def get_snapshot_with_history(self) -> dict[str, Any]:
        """Get current metrics with historical data."""
        data = self.get_snapshot()
        data["history"] = {
            "cpu_total": self.metric_manager.series["cpu_total"].values,
            "cpu_user": self.metric_manager.series["cpu_user"].values,
            "cpu_system": self.metric_manager.series["cpu_system"].values,
            "memory_percent": self.metric_manager.series["memory_percent"].values,
            "swap_percent": self.metric_manager.series["swap_percent"].values,
            "net_recv_rate": self.metric_manager.series["net_recv_rate"].values,
            "net_sent_rate": self.metric_manager.series["net_sent_rate"].values,
            "disk_read_rate": self.metric_manager.series["disk_read_rate"].values,
            "disk_write_rate": self.metric_manager.series["disk_write_rate"].values,
            "gpu_util": self.metric_manager.series["gpu_util"].values,
            "gpu_memory": self.metric_manager.series["gpu_memory"].values,
            "gpu_temp": self.metric_manager.series["gpu_temp"].values,
        }
        # Include per-core CPU history
        core_count = len(self.monoman.cpu.percent_per_core)
        for i in range(core_count):
            series_name = f"cpu_core_{i}"
            if series_name not in self.metric_manager.series:
                from monoman.Modules.MetricManager import MetricSeries
                self.metric_manager.series[series_name] = MetricSeries(
                    name=series_name,
                    label=f"Core {i}",
                    color="#54efae",
                    max_points=self.metric_manager.max_points,
                )
            self.metric_manager.series[series_name].add(
                self.monoman.cpu.percent_per_core[i] if i < len(self.monoman.cpu.percent_per_core) else 0
            )
            data["history"][series_name] = self.metric_manager.series[series_name].values
        return data

    def get_history(self) -> dict[str, Any]:
        """Get all historical data."""
        return self.metric_manager.to_dict()


# Global collector instance
collector = MetricsCollector(max_history_points=300)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await collector.start()
    yield
    await collector.stop()


# Create FastAPI app
app = FastAPI(
    title="Monoman API",
    description="System monitoring API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/metrics")
async def get_metrics() -> dict[str, Any]:
    """Get current system metrics snapshot."""
    return collector.get_snapshot()


@app.get("/api/metrics/history")
async def get_metrics_history(
    range: str = Query("5m", description="Time range: 5m, 30m, 1h, 6h, 24h, 7d")
) -> dict[str, Any]:
    """Get historical metrics data for a specific time range."""
    data = collector.long_history.get_range(range)

    # Transform flat list into per-metric format with timestamps
    timestamps = [datetime.fromtimestamp(d["t"]).isoformat() for d in data]

    return {
        "cpu_total": {
            "values": [d["cpu"] for d in data],
            "timestamps": timestamps,
        },
        "cpu_user": {
            "values": [d["cpu_u"] for d in data],
            "timestamps": timestamps,
        },
        "cpu_system": {
            "values": [d["cpu_s"] for d in data],
            "timestamps": timestamps,
        },
        "memory_percent": {
            "values": [d["mem"] for d in data],
            "timestamps": timestamps,
        },
        "swap_percent": {
            "values": [d["swap"] for d in data],
            "timestamps": timestamps,
        },
        "net_recv_rate": {
            "values": [d["net_in"] for d in data],
            "timestamps": timestamps,
        },
        "net_sent_rate": {
            "values": [d["net_out"] for d in data],
            "timestamps": timestamps,
        },
        "disk_read_rate": {
            "values": [d["disk_r"] for d in data],
            "timestamps": timestamps,
        },
        "disk_write_rate": {
            "values": [d["disk_w"] for d in data],
            "timestamps": timestamps,
        },
    }


@app.get("/api/system")
async def get_system_info() -> dict[str, Any]:
    """Get static system information."""
    return collector.monoman.system_info.__dict__


@app.get("/api/config")
async def get_config() -> dict[str, Any]:
    """Get current configuration."""
    return {
        "refresh_interval": collector.monoman.refresh_interval,
        "max_history_points": collector.metric_manager.max_points,
        "process_sort_by": collector.monoman.process_sort_by,
        "process_sort_reverse": collector.monoman.process_sort_reverse,
        "panels": {
            "dashboard": collector.monoman.panels.dashboard,
            "cpu": collector.monoman.panels.cpu,
            "memory": collector.monoman.panels.memory,
            "disk": collector.monoman.panels.disk,
            "network": collector.monoman.panels.network,
            "processes": collector.monoman.panels.processes,
            "gpu": collector.monoman.panels.gpu,
            "temperature": collector.monoman.panels.temperature,
        },
    }


@app.post("/api/config")
async def update_config(config: dict[str, Any]) -> dict[str, Any]:
    """Update configuration."""
    if "refresh_interval" in config:
        interval = float(config["refresh_interval"])
        collector.monoman.refresh_interval = max(0.5, min(10.0, interval))
    if "process_sort_by" in config:
        if config["process_sort_by"] in ("cpu", "memory", "pid", "name", "user"):
            collector.monoman.process_sort_by = config["process_sort_by"]
    if "process_sort_reverse" in config:
        collector.monoman.process_sort_reverse = bool(config["process_sort_reverse"])
    if "panels" in config:
        panels = config["panels"]
        for panel_name in ("dashboard", "cpu", "memory", "disk", "network", "processes", "gpu", "temperature"):
            if panel_name in panels:
                setattr(collector.monoman.panels, panel_name, bool(panels[panel_name]))

    collector._save_history()
    return await get_config()


@app.post("/api/history/clear")
async def clear_history() -> dict[str, str]:
    """Clear historical data."""
    collector.metric_manager = MetricManager(max_points=collector.metric_manager.max_points)
    collector.long_history = LongTermHistory()
    collector._save_history()
    return {"status": "ok", "message": "History cleared"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time metrics streaming."""
    await websocket.accept()
    collector.connections.append(websocket)

    try:
        await websocket.send_json(collector.get_snapshot_with_history())
    except Exception:
        pass

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            elif data.startswith("config:"):
                try:
                    config_data = json.loads(data[7:])
                    await update_config(config_data)
                    await websocket.send_json({"type": "config_updated", "config": await get_config()})
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in collector.connections:
            collector.connections.remove(websocket)


# Serve static files for production
static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(static_dir / "index.html")

    @app.get("/history")
    async def serve_history_page():
        return FileResponse(static_dir / "index.html")


def main() -> None:
    """Run the web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
