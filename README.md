# Monoman

A terminal-based system performance monitor inspired by [Dolphie](https://github.com/charles-001/dolphie).

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Real-time monitoring** of CPU, Memory, Disk, Network, Processes, GPU, and Temperature
- **Cross-platform** support for Windows, macOS, and Linux
- **Beautiful TUI** built with Textual and Rich
- **Recording & Replay** - Record sessions for later analysis
- **Configurable** via config files and command-line arguments
- **Keyboard shortcuts** for quick navigation and filtering

## Installation

```bash
pip install monoman
```

Or install from source:

```bash
git clone https://github.com/davidcjones79/monoman.git
cd monoman
pip install -e .
```

## Usage

Simply run:

```bash
monoman
```

### Command Line Options

```
monoman [OPTIONS]

Options:
  -r, --refresh-interval FLOAT  Refresh interval in seconds (default: 1.0)
  -c, --config PATH             Path to config file
  --record                      Start recording immediately
  --replay PATH                 Replay a recording file
  -v, --version                 Show version and exit
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `?` | Show help |
| `Space` | Pause/resume refresh |
| `+`/`-` | Increase/decrease refresh rate |
| `1`-`8` | Toggle panels (Dashboard, CPU, Memory, Disk, Network, Processes, GPU, Temp) |
| `c` | Sort processes by CPU |
| `m` | Sort processes by Memory |
| `p` | Sort processes by PID |
| `n` | Sort processes by Name |
| `r` | Reverse sort order |
| `R` | Start/stop recording |

## Configuration

Create a config file at `~/.monoman.toml` or `~/.config/monoman/config.toml`:

```toml
[general]
refresh_interval = 1.0
max_history_points = 60
theme = "dark"

[panels]
dashboard = true
cpu = true
memory = true
disk = true
network = true
processes = true
gpu = true
temperature = true

[processes]
sort_by = "cpu"
sort_reverse = true
show_all = false
max_display = 15

[recording]
directory = "~/.monoman/recordings"
retention_hours = 48
```

## Panels

### Dashboard
System overview with hostname, uptime, and quick stats for CPU, Memory, Disk, and Network.

### CPU
Detailed CPU metrics including:
- Total and per-core usage
- User/System/Idle breakdown
- Frequency and load average (Unix)
- Context switches and interrupts

### Memory
Physical and swap memory usage with:
- Used/Free/Available breakdown
- Cache and buffers (Linux)
- Visual progress bars

### Disk
Disk partitions and I/O:
- Usage per mount point
- Read/Write rates
- Filesystem types

### Network
Network interfaces with:
- Upload/Download rates
- Total bytes transferred
- Error and drop counts
- IP addresses

### Processes
Top processes sorted by resource usage:
- CPU and Memory percentage
- Thread count
- Command line
- Sortable columns

### GPU
NVIDIA GPU monitoring (requires pynvml):
- Utilization percentage
- Memory usage
- Temperature and fan speed
- Power consumption

### Temperature
Sensor readings (Linux with lm-sensors):
- Current temperature
- High/Critical thresholds
- Visual status indicators

## Platform Support

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| CPU | ✅ | ✅ | ✅ |
| Memory | ✅ | ✅ | ✅ |
| Disk | ✅ | ✅ | ✅ |
| Network | ✅ | ✅ | ✅ |
| Processes | ✅ | ✅ | ✅ |
| GPU (NVIDIA) | ✅ | ❌ | ✅ |
| Temperature | ❌ | ❌ | ✅ |
| Load Average | ❌ | ✅ | ✅ |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy monoman

# Linting
ruff check monoman
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by [Dolphie](https://github.com/charles-001/dolphie)
- Built with [Textual](https://github.com/Textualize/textual) and [Rich](https://github.com/Textualize/rich)
- System metrics via [psutil](https://github.com/giampaolo/psutil)
