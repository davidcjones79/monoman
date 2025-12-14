"""Temperature metrics collector."""

import platform

import psutil

from monoman.DataTypes import GroupedTemperature, TemperatureMetrics, TemperatureReading


# Invalid sensor readings to filter out
INVALID_THRESHOLDS = {
    "min": -50.0,  # Below -50°C is likely invalid
    "max": 150.0,  # Above 150°C is likely invalid
}

# Apple SMC sensor groupings
APPLESMC_GROUPS = {
    "CPU": {
        "labels": ["TC0C", "TC1C", "TCXC", "TC0E", "TC0F"],
        "method": "max",  # Use max for CPU temps
    },
    "GPU": {
        "labels": ["TCGC"],
        "method": "max",
    },
    "Memory": {
        "labels": ["TM0P"],
        "method": "max",
    },
    "Battery": {
        "labels": ["TB0T", "TB1T", "TB2T"],
        "method": "avg",
    },
    "Ambient": {
        "labels": ["TA0P", "TA1P"],
        "method": "avg",
    },
    "Heatsink": {
        "labels": ["TH0a", "TH0b", "TH0x", "Th1H", "Th2H"],
        "method": "avg",
    },
    "Palm Rest": {
        "labels": ["Ts0P"],
        "method": "max",
    },
    "Wireless": {
        "labels": ["TW0P"],
        "method": "max",
    },
}

# Coretemp groupings (Intel CPUs)
CORETEMP_GROUPS = {
    "CPU Package": {
        "labels": ["Package id 0", "Package id 1"],
        "method": "max",
    },
    "CPU Cores": {
        "labels_pattern": "Core",  # Match any label containing "Core"
        "method": "max",
    },
}


def _is_valid_reading(temp: float) -> bool:
    """Check if a temperature reading is valid."""
    return INVALID_THRESHOLDS["min"] <= temp <= INVALID_THRESHOLDS["max"]


def _group_sensors(
    sensors: dict[str, list[TemperatureReading]]
) -> list[GroupedTemperature]:
    """Group raw sensor readings into summarized categories."""
    grouped: list[GroupedTemperature] = []
    used_labels: set[str] = set()

    # Process applesmc sensors
    if "applesmc" in sensors:
        applesmc_readings = {r.label: r for r in sensors["applesmc"]}

        for group_name, config in APPLESMC_GROUPS.items():
            labels = config["labels"]
            method = config["method"]
            valid_readings = []
            source_labels = []

            for label in labels:
                if label in applesmc_readings:
                    reading = applesmc_readings[label]
                    if _is_valid_reading(reading.current):
                        valid_readings.append(reading)
                        source_labels.append(label)
                        used_labels.add(f"applesmc:{label}")

            if valid_readings:
                if method == "max":
                    current = max(r.current for r in valid_readings)
                else:  # avg
                    current = sum(r.current for r in valid_readings) / len(valid_readings)

                # Get high/critical from readings that have them
                highs = [r.high for r in valid_readings if r.high is not None]
                criticals = [r.critical for r in valid_readings if r.critical is not None]

                grouped.append(
                    GroupedTemperature(
                        name=group_name,
                        current=round(current, 1),
                        high=min(highs) if highs else None,
                        critical=min(criticals) if criticals else None,
                        source_labels=source_labels,
                    )
                )

    # Process coretemp sensors (Intel CPUs)
    if "coretemp" in sensors:
        coretemp_readings = sensors["coretemp"]

        # CPU Package
        package_readings = [
            r for r in coretemp_readings
            if r.label.startswith("Package") and _is_valid_reading(r.current)
        ]
        if package_readings:
            reading = max(package_readings, key=lambda r: r.current)
            # Only add if we don't already have a CPU group from applesmc
            if not any(g.name == "CPU" for g in grouped):
                grouped.append(
                    GroupedTemperature(
                        name="CPU",
                        current=round(reading.current, 1),
                        high=reading.high,
                        critical=reading.critical,
                        source_labels=[reading.label],
                    )
                )
            used_labels.add(f"coretemp:{reading.label}")

        # CPU Cores - combine into single entry
        core_readings = [
            r for r in coretemp_readings
            if r.label.startswith("Core") and _is_valid_reading(r.current)
        ]
        if core_readings:
            max_core = max(core_readings, key=lambda r: r.current)
            # Only add if different from package temp
            if not any(g.name in ("CPU", "CPU Package") for g in grouped):
                grouped.append(
                    GroupedTemperature(
                        name="CPU Cores",
                        current=round(max_core.current, 1),
                        high=max_core.high,
                        critical=max_core.critical,
                        source_labels=[r.label for r in core_readings],
                    )
                )
            for r in core_readings:
                used_labels.add(f"coretemp:{r.label}")

    # Process battery sensor (BAT0)
    if "BAT0" in sensors and not any(g.name == "Battery" for g in grouped):
        bat_readings = [r for r in sensors["BAT0"] if _is_valid_reading(r.current)]
        if bat_readings:
            reading = bat_readings[0]
            grouped.append(
                GroupedTemperature(
                    name="Battery",
                    current=round(reading.current, 1),
                    high=reading.high,
                    critical=reading.critical,
                    source_labels=[reading.label],
                )
            )

    # Sort by temperature (hottest first)
    grouped.sort(key=lambda g: g.current, reverse=True)

    return grouped


def collect_temperature_metrics() -> TemperatureMetrics:
    """Collect temperature sensor metrics."""
    sensors: dict[str, list[TemperatureReading]] = {}

    # Temperature sensors are not available on Windows via psutil
    if platform.system() == "Windows":
        return TemperatureMetrics(sensors={}, grouped=[], available=False)

    try:
        temps = psutil.sensors_temperatures()

        if not temps:
            return TemperatureMetrics(sensors={}, grouped=[], available=False)

        for sensor_name, entries in temps.items():
            readings = []
            for entry in entries:
                readings.append(
                    TemperatureReading(
                        label=entry.label or sensor_name,
                        current=entry.current,
                        high=entry.high,
                        critical=entry.critical,
                    )
                )
            sensors[sensor_name] = readings

        # Generate grouped summary
        grouped = _group_sensors(sensors)

        return TemperatureMetrics(
            sensors=sensors,
            grouped=grouped,
            available=len(sensors) > 0
        )

    except (AttributeError, OSError, Exception):
        return TemperatureMetrics(sensors={}, grouped=[], available=False)
