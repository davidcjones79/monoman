"""Panel implementations for Monoman."""

from monoman.Panels.cpu import create_cpu_panel
from monoman.Panels.dashboard import create_dashboard_panel
from monoman.Panels.disk import create_disk_panel
from monoman.Panels.gpu import create_gpu_panel
from monoman.Panels.graphs import create_all_graphs
from monoman.Panels.memory import create_memory_panel
from monoman.Panels.network import create_network_panel
from monoman.Panels.processes import create_processes_panel
from monoman.Panels.temperature import create_temperature_panel

__all__ = [
    "create_dashboard_panel",
    "create_cpu_panel",
    "create_memory_panel",
    "create_disk_panel",
    "create_network_panel",
    "create_processes_panel",
    "create_gpu_panel",
    "create_temperature_panel",
    "create_all_graphs",
]
