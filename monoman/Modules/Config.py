"""Configuration management for Monoman."""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_config_paths() -> list[Path]:
    """Get list of config file paths to check."""
    paths = []

    # User config directory
    if sys.platform == "win32":
        appdata = Path.home() / "AppData" / "Roaming" / "monoman"
        paths.append(appdata / "config.toml")
    else:
        # XDG config
        xdg_config = Path.home() / ".config" / "monoman"
        paths.append(xdg_config / "config.toml")

    # Home directory
    paths.append(Path.home() / ".monoman.toml")

    # System config (Unix only)
    if sys.platform != "win32":
        paths.append(Path("/etc/monoman/config.toml"))
        paths.append(Path("/etc/monoman.toml"))

    return paths


@dataclass
class Config:
    """Application configuration."""

    # Refresh settings
    refresh_interval: float = 1.0
    max_history_points: int = 60

    # Panel visibility defaults
    show_dashboard: bool = True
    show_cpu: bool = True
    show_memory: bool = True
    show_disk: bool = True
    show_network: bool = True
    show_processes: bool = True
    show_gpu: bool = True
    show_temperature: bool = True

    # Process settings
    process_sort_by: str = "cpu"
    process_sort_reverse: bool = True
    show_all_processes: bool = False
    max_processes: int = 15

    # Recording settings
    record_dir: Path = field(default_factory=lambda: Path.home() / ".monoman" / "recordings")
    record_retention_hours: int = 48

    # Display settings
    theme: str = "dark"
    hide_snap_volumes: bool = True

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load config from TOML file."""
        config = cls()

        if not path.exists():
            return config

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)

            config._apply_dict(data)
        except Exception:
            pass

        return config

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Config":
        """Create config from command line arguments."""
        config = cls()

        if hasattr(args, "refresh_interval") and args.refresh_interval is not None:
            config.refresh_interval = args.refresh_interval

        if hasattr(args, "config") and args.config:
            config_path = Path(args.config)
            if config_path.exists():
                file_config = cls.from_file(config_path)
                # File config is base, args override
                config = file_config
                if args.refresh_interval is not None:
                    config.refresh_interval = args.refresh_interval

        return config

    def _apply_dict(self, data: dict[str, Any]) -> None:
        """Apply dictionary values to config."""
        # General settings
        general = data.get("general", {})
        if "refresh_interval" in general:
            self.refresh_interval = float(general["refresh_interval"])
        if "max_history_points" in general:
            self.max_history_points = int(general["max_history_points"])
        if "theme" in general:
            self.theme = str(general["theme"])

        # Panel visibility
        panels = data.get("panels", {})
        if "dashboard" in panels:
            self.show_dashboard = bool(panels["dashboard"])
        if "cpu" in panels:
            self.show_cpu = bool(panels["cpu"])
        if "memory" in panels:
            self.show_memory = bool(panels["memory"])
        if "disk" in panels:
            self.show_disk = bool(panels["disk"])
        if "network" in panels:
            self.show_network = bool(panels["network"])
        if "processes" in panels:
            self.show_processes = bool(panels["processes"])
        if "gpu" in panels:
            self.show_gpu = bool(panels["gpu"])
        if "temperature" in panels:
            self.show_temperature = bool(panels["temperature"])
        
        # Disk settings
        disk = data.get("disk", {})
        if "hide_snap_volumes" in disk:
            self.hide_snap_volumes = bool(disk["hide_snap_volumes"])

        # Process settings
        processes = data.get("processes", {})
        if "sort_by" in processes:
            self.process_sort_by = str(processes["sort_by"])
        if "sort_reverse" in processes:
            self.process_sort_reverse = bool(processes["sort_reverse"])
        if "show_all" in processes:
            self.show_all_processes = bool(processes["show_all"])
        if "max_display" in processes:
            self.max_processes = int(processes["max_display"])

        # Recording settings
        recording = data.get("recording", {})
        if "directory" in recording:
            self.record_dir = Path(recording["directory"]).expanduser()
        if "retention_hours" in recording:
            self.record_retention_hours = int(recording["retention_hours"])

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "general": {
                "refresh_interval": self.refresh_interval,
                "max_history_points": self.max_history_points,
                "theme": self.theme,
            },
            "panels": {
                "dashboard": self.show_dashboard,
                "cpu": self.show_cpu,
                "memory": self.show_memory,
                "disk": self.show_disk,
                "network": self.show_network,
                "processes": self.show_processes,
                "gpu": self.show_gpu,
                "temperature": self.show_temperature,
            },
            "processes": {
                "sort_by": self.process_sort_by,
                "sort_reverse": self.process_sort_reverse,
                "show_all": self.show_all_processes,
                "max_display": self.max_processes,
            },
            "recording": {
                "directory": str(self.record_dir),
                "retention_hours": self.record_retention_hours,
            },
            "disk": {
                "hide_snap_volumes": self.hide_snap_volumes,
            },
        }


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="monoman",
        description="Terminal-based system performance monitor",
    )

    parser.add_argument(
        "-r",
        "--refresh-interval",
        type=float,
        default=None,
        help="Refresh interval in seconds (default: 1.0)",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=None,
        help="Path to config file",
    )

    parser.add_argument(
        "--record",
        action="store_true",
        help="Start recording immediately",
    )

    parser.add_argument(
        "--replay",
        type=str,
        default=None,
        help="Replay a recording file",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    return parser


def load_config() -> tuple[Config, argparse.Namespace]:
    """Load configuration from files and command line."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Check version flag
    if args.version:
        from monoman import __version__

        print(f"monoman {__version__}")
        sys.exit(0)

    # Load config file
    config = Config()

    # Check for config file from args first
    if args.config:
        config = Config.from_file(Path(args.config))
    else:
        # Check default locations
        for path in get_config_paths():
            if path.exists():
                config = Config.from_file(path)
                break

    # Override with command line args
    if args.refresh_interval is not None:
        config.refresh_interval = args.refresh_interval

    return config, args
