"""GPU metrics collector."""

import platform
from typing import Any

from monoman.DataTypes import GPUListMetrics, GPUMetrics

# Try to import nvidia-ml-py for NVIDIA GPU support
_nvml_available = False
_nvml: Any = None

if platform.system() != "Darwin":  # Not macOS
    try:
        # Suppress the deprecation warning from pynvml wrapper
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            import pynvml as _nvml_module

        _nvml = _nvml_module
        _nvml_available = True
    except ImportError:
        pass


def _init_nvml() -> bool:
    """Initialize NVML library."""
    global _nvml_available
    if not _nvml_available or _nvml is None:
        return False

    try:
        _nvml.nvmlInit()
        return True
    except Exception:
        _nvml_available = False
        return False


def collect_gpu_metrics() -> GPUListMetrics:
    """Collect GPU metrics."""
    gpus = []

    if not _nvml_available or _nvml is None:
        return GPUListMetrics(gpus=[], available=False)

    if not _init_nvml():
        return GPUListMetrics(gpus=[], available=False)

    try:
        device_count = _nvml.nvmlDeviceGetCount()

        for i in range(device_count):
            try:
                handle = _nvml.nvmlDeviceGetHandleByIndex(i)

                # Get name
                name = _nvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")

                # Get driver version
                driver = _nvml.nvmlSystemGetDriverVersion()
                if isinstance(driver, bytes):
                    driver = driver.decode("utf-8")

                # Get memory info
                mem = _nvml.nvmlDeviceGetMemoryInfo(handle)
                memory_total = mem.total
                memory_used = mem.used
                memory_free = mem.free
                memory_percent = (memory_used / memory_total * 100) if memory_total > 0 else 0.0

                # Get utilization
                util = _nvml.nvmlDeviceGetUtilizationRates(handle)
                utilization = util.gpu

                # Get temperature
                try:
                    temperature = _nvml.nvmlDeviceGetTemperature(handle, _nvml.NVML_TEMPERATURE_GPU)
                except Exception:
                    temperature = 0.0

                # Get fan speed
                try:
                    fan_speed = _nvml.nvmlDeviceGetFanSpeed(handle)
                except Exception:
                    fan_speed = 0.0

                # Get power
                try:
                    power_draw = _nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert mW to W
                except Exception:
                    power_draw = 0.0

                try:
                    power_limit = _nvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
                except Exception:
                    power_limit = 0.0

                gpus.append(
                    GPUMetrics(
                        index=i,
                        name=name,
                        driver_version=driver,
                        memory_total=memory_total,
                        memory_used=memory_used,
                        memory_free=memory_free,
                        memory_percent=memory_percent,
                        utilization=utilization,
                        temperature=temperature,
                        fan_speed=fan_speed,
                        power_draw=power_draw,
                        power_limit=power_limit,
                    )
                )

            except Exception:
                continue

        return GPUListMetrics(gpus=gpus, available=len(gpus) > 0)

    except Exception:
        return GPUListMetrics(gpus=[], available=False)

    finally:
        try:
            _nvml.nvmlShutdown()
        except Exception:
            pass
