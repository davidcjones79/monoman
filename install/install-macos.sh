#!/bin/bash

# Monoman Fleet Beacon Agent Installer for macOS (launchd)
# This script installs Monoman as a launchd service that reports to Fleet Beacon

set -e

echo "======================================================================"
echo "  Monoman Fleet Beacon Agent Installer (macOS/launchd)"
echo "======================================================================"
echo ""

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
    pip3 install monoman

    if ! command -v monoman &> /dev/null; then
        echo "Error: Failed to install monoman"
        echo "Try installing with: pip3 install --user monoman"
        exit 1
    fi
fi

# Get monoman path
MONOMAN_PATH=$(which monoman)
echo "Found monoman at: $MONOMAN_PATH"

# Get Python path
PYTHON_PATH=$(which python3)
echo "Found Python at: $PYTHON_PATH"

# Build program arguments array
ARGS=(
    "$MONOMAN_PATH"
    "--agent"
    "--server"
    "$SERVER_URL"
    "--interval"
    "$INTERVAL"
)

if [ -n "$SYSTEM_ID" ]; then
    ARGS+=("--system-id" "$SYSTEM_ID")
fi

if [ -n "$VERBOSE_FLAG" ]; then
    ARGS+=("$VERBOSE_FLAG")
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Create plist file
PLIST_PATH=~/Library/LaunchAgents/com.monoman.agent.plist

echo ""
echo "Creating launchd plist file..."

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.monoman.agent</string>

    <key>ProgramArguments</key>
    <array>
EOF

# Add each argument to the plist
for arg in "${ARGS[@]}"; do
    echo "        <string>$arg</string>" >> "$PLIST_PATH"
done

cat >> "$PLIST_PATH" << EOF
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/monoman-agent.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/monoman-agent.error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo "Plist file created at: $PLIST_PATH"

# Load the service
echo ""
echo "Loading launchd service..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

# Wait a moment for it to start
sleep 2

# Check if it's running
echo ""
echo "======================================================================"
echo "  Installation Complete!"
echo "======================================================================"
echo ""
echo "Service Status:"
if launchctl list | grep -q com.monoman.agent; then
    echo "✓ Service is running"
    launchctl list | grep com.monoman.agent
else
    echo "⚠ Service may not be running. Check logs for details."
fi

echo ""
echo "Useful Commands:"
echo "  - View status:  launchctl list | grep com.monoman.agent"
echo "  - View logs:    tail -f /tmp/monoman-agent.log"
echo "  - View errors:  tail -f /tmp/monoman-agent.error.log"
echo "  - Stop service: launchctl stop com.monoman.agent"
echo "  - Start:        launchctl start com.monoman.agent"
echo "  - Restart:      launchctl stop com.monoman.agent && launchctl start com.monoman.agent"
echo "  - Unload:       launchctl unload ~/Library/LaunchAgents/com.monoman.agent.plist"
echo "  - Uninstall:    launchctl unload ~/Library/LaunchAgents/com.monoman.agent.plist && rm ~/Library/LaunchAgents/com.monoman.agent.plist"
echo ""
echo "The agent is now reporting to: $SERVER_URL"
echo ""
echo "Note: The service will automatically start on login."
echo ""
