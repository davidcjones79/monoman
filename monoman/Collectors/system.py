"""System information collector."""

import platform
import sys
from datetime import datetime

import psutil

from monoman.DataTypes import SystemInfo


def collect_system_info() -> SystemInfo:
    """Collect static system information."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = (datetime.now() - boot_time).total_seconds()

    return SystemInfo(
        hostname=platform.node(),
        platform=platform.system(),
        platform_release=platform.release(),
        platform_version=platform.version(),
        architecture=platform.machine(),
        processor=platform.processor() or "Unknown",
        python_version=sys.version.split()[0],
        boot_time=boot_time,
        uptime_seconds=uptime,
    )
