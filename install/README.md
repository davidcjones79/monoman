# Monoman Fleet Beacon Agent Installation

Install Monoman as a system service that continuously reports metrics to Fleet Beacon.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Fleet Beacon server running and accessible

## Quick Install

### Linux (systemd)

```bash
# Download and run the installer
curl -O https://raw.githubusercontent.com/davidcjones79/monoman/main/install/install-linux.sh
chmod +x install-linux.sh
sudo ./install-linux.sh
```

**Requirements:**
- systemd-based Linux distribution (Ubuntu, Debian, Fedora, CentOS, etc.)
- Root access (sudo)

**What it does:**
- Installs monoman via pip if not already installed
- Creates systemd service file at `/etc/systemd/system/monoman-agent.service`
- Enables and starts the service
- Configures auto-start on boot

### macOS (launchd)

```bash
# Download and run the installer
curl -O https://raw.githubusercontent.com/davidcjones79/monoman/main/install/install-macos.sh
chmod +x install-macos.sh
./install-macos.sh
```

**Requirements:**
- macOS 10.10 or higher
- Homebrew (optional, for Python installation)

**What it does:**
- Installs monoman via pip if not already installed
- Creates launchd plist file at `~/Library/LaunchAgents/com.monoman.agent.plist`
- Loads and starts the service
- Configures auto-start on login

### Windows (Task Scheduler)

```powershell
# Download and run the installer (PowerShell as Administrator)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/davidcjones79/monoman/main/install/install-windows.ps1" -OutFile install-windows.ps1
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install-windows.ps1
```

**Requirements:**
- Windows 10 or Server 2016 or higher
- PowerShell 5.0 or higher
- Administrator privileges

**What it does:**
- Installs monoman via pip if not already installed
- Creates scheduled task named "MonomanFleetBeaconAgent"
- Starts the task immediately
- Configures auto-start on system boot

## Manual Installation

If you prefer to set up the service manually:

### 1. Install Monoman

```bash
pip install monoman
```

### 2. Test Agent Mode

```bash
monoman --agent --server http://your-fleet-beacon:8000 --verbose
```

### 3. Configure System Service

Follow the platform-specific instructions below.

#### Linux (systemd)

Create `/etc/systemd/system/monoman-agent.service`:

```ini
[Unit]
Description=Monoman Fleet Beacon Agent
After=network-online.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/local/bin/monoman --agent --server http://fleet-beacon:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable monoman-agent
sudo systemctl start monoman-agent
```

#### macOS (launchd)

Create `~/Library/LaunchAgents/com.monoman.agent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monoman.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/monoman</string>
        <string>--agent</string>
        <string>--server</string>
        <string>http://fleet-beacon:8000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.monoman.agent.plist
```

#### Windows (PowerShell as Administrator)

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "-m monoman --agent --server http://fleet-beacon:8000"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "MonomanFleetBeaconAgent" -Action $action -Trigger $trigger -Settings $settings
Start-ScheduledTask -TaskName "MonomanFleetBeaconAgent"
```

## Configuration Options

### Command Line Arguments

```bash
monoman --agent --server <URL> [OPTIONS]
```

**Required:**
- `--agent` - Run in Fleet Beacon agent mode
- `--server <URL>` - Fleet Beacon server URL (e.g., `http://fleet-beacon:8000`)

**Optional:**
- `--system-id <ID>` - Custom system identifier (default: auto-generated from hostname)
- `--interval <seconds>` - Reporting interval in seconds (default: 60)
- `--verbose` - Enable verbose logging

### Examples

```bash
# Basic usage
monoman --agent --server http://192.168.1.100:8000

# Custom system ID and interval
monoman --agent --server http://fleet-beacon.local:8000 --system-id my-laptop --interval 30

# Verbose logging
monoman --agent --server http://fleet-beacon:8000 --verbose
```

## Monitoring

### Linux

```bash
# View service status
systemctl status monoman-agent

# View logs
journalctl -u monoman-agent -f

# Restart service
sudo systemctl restart monoman-agent
```

### macOS

```bash
# View status
launchctl list | grep com.monoman.agent

# View logs
tail -f /tmp/monoman-agent.log

# Restart service
launchctl stop com.monoman.agent
launchctl start com.monoman.agent
```

### Windows

```powershell
# View status
Get-ScheduledTask -TaskName "MonomanFleetBeaconAgent"

# View task info
Get-ScheduledTaskInfo -TaskName "MonomanFleetBeaconAgent"

# Restart task
Stop-ScheduledTask -TaskName "MonomanFleetBeaconAgent"
Start-ScheduledTask -TaskName "MonomanFleetBeaconAgent"
```

## Metrics Reported

The agent automatically collects and reports:

- **CPU**: Load percentage (1-minute average)
- **Memory**: Total, used (GB), and percentage
- **Disk**: Total, used (TB), and percentage
- **Network**: Throughput (Mbps)
- **Storage**: Total capacity (TB)

## Uninstallation

### Linux

```bash
sudo systemctl stop monoman-agent
sudo systemctl disable monoman-agent
sudo rm /etc/systemd/system/monoman-agent.service
sudo systemctl daemon-reload
```

### macOS

```bash
launchctl unload ~/Library/LaunchAgents/com.monoman.agent.plist
rm ~/Library/LaunchAgents/com.monoman.agent.plist
```

### Windows

```powershell
Unregister-ScheduledTask -TaskName "MonomanFleetBeaconAgent" -Confirm:$false
```

## Troubleshooting

### Agent not connecting

1. Check Fleet Beacon is running: `curl http://your-server:8000`
2. Verify network connectivity
3. Check firewall rules (port 8000 by default)
4. Review logs for error messages

### High CPU/Memory usage

- Increase the `--interval` value (default: 60 seconds)
- Check for network issues causing retries

### Service not starting

**Linux:**
```bash
journalctl -u monoman-agent -n 50
```

**macOS:**
```bash
cat /tmp/monoman-agent.error.log
```

**Windows:**
- Check Event Viewer > Task Scheduler logs

## Support

- GitHub Issues: https://github.com/davidcjones79/monoman/issues
- Documentation: https://github.com/davidcjones79/monoman
