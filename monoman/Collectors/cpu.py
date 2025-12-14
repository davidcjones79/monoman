"""CPU metrics collector."""

import platform

import psutil

from monoman.DataTypes import CPUMetrics


def collect_cpu_metrics() -> CPUMetrics:
    """Collect CPU metrics."""
    # Get CPU times for user/system/idle breakdown
    cpu_times = psutil.cpu_times_percent(interval=None)

    # Get per-core percentages
    per_core = psutil.cpu_percent(interval=None, percpu=True)

    # Get CPU frequency
    freq = psutil.cpu_freq()
    freq_current = freq.current if freq else 0.0
    freq_max = freq.max if freq else 0.0

    # Get CPU stats (context switches, interrupts)
    stats = psutil.cpu_stats()

    # Get load average (not available on Windows)
    load_avg = (0.0, 0.0, 0.0)
    if platform.system() != "Windows":
        try:
            load_avg = psutil.getloadavg()
        except (AttributeError, OSError):
            pass

    return CPUMetrics(
        percent_total=psutil.cpu_percent(interval=None),
        percent_per_core=per_core,
        load_avg_1=load_avg[0],
        load_avg_5=load_avg[1],
        load_avg_15=load_avg[2],
        frequency_current=freq_current,
        frequency_max=freq_max,
        core_count=psutil.cpu_count(logical=False) or 0,
        thread_count=psutil.cpu_count(logical=True) or 0,
        ctx_switches=stats.ctx_switches,
        interrupts=stats.interrupts,
        user_time=getattr(cpu_times, "user", 0.0),
        system_time=getattr(cpu_times, "system", 0.0),
        idle_time=getattr(cpu_times, "idle", 0.0),
        iowait_time=getattr(cpu_times, "iowait", 0.0),
    )
