# Monoman Fleet Beacon Agent Installer for Windows (Task Scheduler)
# This script installs Monoman as a Windows scheduled task that reports to Fleet Beacon

# Requires PowerShell 5.0 or higher and Administrator privileges

#Requires -RunAsAdministrator

Write-Host "======================================================================"
Write-Host "  Monoman Fleet Beacon Agent Installer (Windows/Task Scheduler)"
Write-Host "======================================================================"
Write-Host ""

# Get configuration from user
$serverUrl = Read-Host "Fleet Beacon server URL (e.g., http://fleet-beacon:8000)"
if ([string]::IsNullOrWhiteSpace($serverUrl)) {
    Write-Error "Server URL is required"
    exit 1
}

$systemId = Read-Host "System ID (leave empty for auto-generate)"
$interval = Read-Host "Reporting interval in seconds (default: 60)"
if ([string]::IsNullOrWhiteSpace($interval)) {
    $interval = 60
}

$verboseInput = Read-Host "Enable verbose logging? (y/N)"
$verboseFlag = ""
if ($verboseInput -eq "y" -or $verboseInput -eq "Y") {
    $verboseFlag = "--verbose"
}

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python is not installed or not in PATH. Please install Python first."
    exit 1
}

Write-Host "Found Python at: $($pythonCmd.Source)"

# Check if monoman is installed
$monomanInstalled = $false
try {
    & python -m monoman --version 2>&1 | Out-Null
    $monomanInstalled = $true
} catch {
    $monomanInstalled = $false
}

if (-not $monomanInstalled) {
    Write-Host ""
    Write-Host "Monoman is not installed. Installing via pip..."
    & python -m pip install monoman

    # Verify installation
    try {
        & python -m monoman --version 2>&1 | Out-Null
    } catch {
        Write-Error "Failed to install monoman"
        exit 1
    }
}

Write-Host "Monoman is installed"

# Build command arguments
$argsList = @(
    "-m", "monoman",
    "--agent",
    "--server", $serverUrl,
    "--interval", $interval
)

if (-not [string]::IsNullOrWhiteSpace($systemId)) {
    $argsList += "--system-id", $systemId
}

if (-not [string]::IsNullOrWhiteSpace($verboseFlag)) {
    $argsList += $verboseFlag
}

$args = $argsList -join " "

Write-Host ""
Write-Host "Creating scheduled task..."

# Create the scheduled task
$taskName = "MonomanFleetBeaconAgent"
$taskDescription = "Monoman agent that reports system metrics to Fleet Beacon"

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$pythonPath = (Get-Command python).Source
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $args

# Create trigger (at startup)
$trigger = New-ScheduledTaskTrigger -AtStartup

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 1)

# Create principal (run as SYSTEM)
$principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the task
Register-ScheduledTask `
    -TaskName $taskName `
    -Description $taskDescription `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal

# Start the task immediately
Write-Host "Starting task..."
Start-ScheduledTask -TaskName $taskName

# Wait a moment for it to start
Start-Sleep -Seconds 2

# Check status
$task = Get-ScheduledTask -TaskName $taskName
$taskInfo = Get-ScheduledTaskInfo -TaskName $taskName

Write-Host ""
Write-Host "======================================================================"
Write-Host "  Installation Complete!"
Write-Host "======================================================================"
Write-Host ""
Write-Host "Task Status:"
Write-Host "  Name:         $($task.TaskName)"
Write-Host "  State:        $($task.State)"
Write-Host "  Last Run:     $($taskInfo.LastRunTime)"
Write-Host "  Last Result:  $($taskInfo.LastTaskResult)"
Write-Host "  Next Run:     $($taskInfo.NextRunTime)"
Write-Host ""
Write-Host "Useful Commands (PowerShell):"
Write-Host "  - View status:  Get-ScheduledTask -TaskName '$taskName'"
Write-Host "  - Stop task:    Stop-ScheduledTask -TaskName '$taskName'"
Write-Host "  - Start task:   Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  - View logs:    Get-ScheduledTaskInfo -TaskName '$taskName'"
Write-Host "  - Disable:      Disable-ScheduledTask -TaskName '$taskName'"
Write-Host "  - Enable:       Enable-ScheduledTask -TaskName '$taskName'"
Write-Host "  - Uninstall:    Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
Write-Host ""
Write-Host "The agent is now reporting to: $serverUrl"
Write-Host ""
Write-Host "Note: The task will automatically start on system boot."
Write-Host ""

# Show recent output
Write-Host "Checking recent logs..."
Write-Host "(You can view detailed logs in Event Viewer under Task Scheduler)"
Write-Host ""
