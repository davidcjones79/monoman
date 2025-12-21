#!/bin/bash

# Monoman Fleet Beacon Agent Installer for Linux (systemd)
# This script installs Monoman as a systemd service that reports to Fleet Beacon

set -e

echo "======================================================================"
echo "  Monoman Fleet Beacon Agent Installer (Linux/systemd)"
echo "======================================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "Error: systemd not found. This script requires systemd."
    exit 1
fi

# Get configuration from user
read -p "Fleet Beacon server URL (e.g., http://fleet-beacon:8000): " SERVER_URL
if [ -z "$SERVER_URL" ]; then
    echo "Error: Server URL is required"
    exit 1
fi

read -p "System ID (leave empty for auto-generate): " SYSTEM_ID
read -p "Reporting interval in seconds (default: 60): " INTERVAL
INTERVAL=${INTERVAL:-60}

read -p "Enable verbose logging? (y/N): " VERBOSE
if [ "$VERBOSE" = "y" ] || [ "$VERBOSE" = "Y" ]; then
    VERBOSE_FLAG="--verbose"
else
    VERBOSE_FLAG=""
fi

# Check if monoman is installed
if ! command -v monoman &> /dev/null; then
    echo ""
    echo "Monoman is not installed. Installing via pip..."
    pip install monoman

    if ! command -v monoman &> /dev/null; then
        echo "Error: Failed to install monoman"
        exit 1
    fi
fi

# Get monoman path
MONOMAN_PATH=$(which monoman)
echo "Found monoman at: $MONOMAN_PATH"

# Build command
CMD="$MONOMAN_PATH --agent --server $SERVER_URL --interval $INTERVAL $VERBOSE_FLAG"
if [ -n "$SYSTEM_ID" ]; then
    CMD="$CMD --system-id $SYSTEM_ID"
fi

echo ""
echo "Creating systemd service file..."

# Create systemd service file
cat > /etc/systemd/system/monoman-agent.service << EOF
[Unit]
Description=Monoman Fleet Beacon Agent
Documentation=https://github.com/davidcjones79/monoman
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=nobody
Group=nogroup
ExecStart=$CMD
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadOnlyPaths=/
ReadWritePaths=/proc /sys

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at /etc/systemd/system/monoman-agent.service"

# Reload systemd
echo ""
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "Enabling service to start on boot..."
systemctl enable monoman-agent.service

# Start service
echo "Starting service..."
systemctl start monoman-agent.service

# Check status
echo ""
echo "======================================================================"
echo "  Installation Complete!"
echo "======================================================================"
echo ""
echo "Service Status:"
systemctl status monoman-agent.service --no-pager || true
echo ""
echo "Useful Commands:"
echo "  - View status:  systemctl status monoman-agent"
echo "  - View logs:    journalctl -u monoman-agent -f"
echo "  - Stop service: systemctl stop monoman-agent"
echo "  - Start:        systemctl start monoman-agent"
echo "  - Restart:      systemctl restart monoman-agent"
echo "  - Disable:      systemctl disable monoman-agent"
echo "  - Uninstall:    systemctl stop monoman-agent && systemctl disable monoman-agent && rm /etc/systemd/system/monoman-agent.service"
echo ""
echo "The agent is now reporting to: $SERVER_URL"
echo ""
