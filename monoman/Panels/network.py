"""Network panel showing network interface metrics."""

import sys

from rich.table import Table
from rich.text import Text

from monoman.DataTypes import NetworkInterfaceMetrics
from monoman.Modules.Functions import format_bytes, format_bytes_rate, format_number
from monoman.Monoman import Monoman

# macOS virtual interfaces to hide (no real traffic)
_MACOS_VIRTUAL_INTERFACES = {
    "lo0",      # Loopback
    "awdl0",    # Apple Wireless Direct Link (AirDrop)
    "llw0",     # Low Latency WLAN
    "gif0",     # IPv6 tunneling
    "stf0",     # IPv6 tunneling
    "ap1",      # Access Point (hotspot)
    "anpi0", "anpi1", "anpi2",  # Apple Network Protocol Interface
}


def _should_show_interface(name: str, iface: NetworkInterfaceMetrics, rates: dict) -> bool:
    """Determine if an interface should be shown in the panel."""
    # Always show on non-macOS
    if sys.platform != "darwin":
        return True

    # Hide known virtual interfaces
    if name in _MACOS_VIRTUAL_INTERFACES:
        return False

    # Hide utun interfaces (VPN tunnels)
    if name.startswith("utun"):
        return False

    # Show interface if it's up and has an IP address, or has had traffic
    if iface.is_up and iface.addresses:
        return True
    if iface.bytes_sent + iface.bytes_recv > 0:
        return True

    return False


def create_network_panel(monoman: Monoman) -> Table:
    """Create the network metrics panel."""
    table = Table(
        show_header=True,
        header_style="bold #91abec",
        box=None,
        padding=(0, 1),
        expand=True,
        title="[bold]Network[/bold]",
        title_style="bold white",
    )

    table.add_column("Interface", style="bold", width=15)
    table.add_column("Status", width=8)
    table.add_column("Download", width=18)
    table.add_column("Upload", width=18)
    table.add_column("Total", width=20)
    table.add_column("Errors", ratio=1)

    shown_count = 0
    for name, iface in monoman.network.interfaces.items():
        rates = monoman.network_rates.get(name, {})

        # Filter out noise on macOS
        if not _should_show_interface(name, iface, rates):
            continue

        shown_count += 1
        # Status
        status = Text()
        if iface.is_up:
            status.append("UP", style="bold green")
            if iface.speed > 0:
                status.append(f" {iface.speed}M", style="dim")
        else:
            status.append("DOWN", style="bold red")
        recv_rate = rates.get("bytes_recv_rate", 0)
        sent_rate = rates.get("bytes_sent_rate", 0)

        # Download
        down_text = Text()
        down_text.append(f"↓ {format_bytes_rate(recv_rate)}\n", style="green")
        down_text.append(f"  {format_bytes(iface.bytes_recv)}", style="dim")

        # Upload
        up_text = Text()
        up_text.append(f"↑ {format_bytes_rate(sent_rate)}\n", style="cyan")
        up_text.append(f"  {format_bytes(iface.bytes_sent)}", style="dim")

        # Total packets
        total_text = Text()
        total_text.append(f"Pkts: {format_number(iface.packets_recv + iface.packets_sent)}\n", style="white")
        if iface.addresses:
            # Show first IP address
            total_text.append(f"{iface.addresses[0][:18]}", style="dim")

        # Errors
        errors_text = Text()
        total_errors = iface.errors_in + iface.errors_out
        total_drops = iface.drops_in + iface.drops_out
        if total_errors > 0:
            errors_text.append(f"Err: {format_number(total_errors)} ", style="red")
        if total_drops > 0:
            errors_text.append(f"Drop: {format_number(total_drops)}", style="yellow")
        if total_errors == 0 and total_drops == 0:
            errors_text.append("OK", style="green")

        table.add_row(name[:14], status, down_text, up_text, total_text, errors_text)

    if shown_count == 0:
        table.add_row("No active interfaces", "", "", "", "", "")

    # Add connection count footer
    table.add_row(
        "",
        "",
        "",
        "",
        Text(f"Connections: {monoman.network.connections_count}", style="dim"),
        "",
    )

    return table
