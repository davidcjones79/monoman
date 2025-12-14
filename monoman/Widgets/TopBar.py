"""Top bar widget showing application status."""

from datetime import datetime

from rich.text import Text
from textual.widgets import Static

from monoman import __version__


class TopBar(Static):
    """Top bar showing application title and status."""

    DEFAULT_CSS = """
    TopBar {
        dock: top;
        height: 1;
        background: #1a1f2e;
        color: #91abec;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        hostname: str = "",
        refresh_interval: float = 1.0,
        is_paused: bool = False,
        is_recording: bool = False,
        is_replaying: bool = False,
    ) -> None:
        super().__init__()
        self.hostname = hostname
        self.refresh_interval = refresh_interval
        self.is_paused = is_paused
        self.is_recording = is_recording
        self.is_replaying = is_replaying

    def render(self) -> Text:
        """Render the top bar."""
        text = Text()

        # Application name
        text.append(" monoman ", style="bold white on #2d3748")
        text.append(f" v{__version__} ", style="dim")
        text.append(" │ ", style="dim")

        # Hostname
        if self.hostname:
            text.append(f" {self.hostname} ", style="bold cyan")
            text.append(" │ ", style="dim")

        # Status indicators
        if self.is_replaying:
            text.append(" ▶ REPLAY ", style="bold black on yellow")
        elif self.is_paused:
            text.append(" ⏸ PAUSED ", style="bold black on orange1")
        elif self.is_recording:
            text.append(" ● REC ", style="bold white on red")
        else:
            text.append(" ● LIVE ", style="bold white on green")

        text.append(" │ ", style="dim")

        # Refresh interval
        text.append(f" {self.refresh_interval:.1f}s ", style="dim")

        # Current time (right-aligned would require width calculation)
        text.append(" │ ", style="dim")
        text.append(f" {datetime.now().strftime('%H:%M:%S')} ", style="white")

        # Help hint
        text.append(" │ ", style="dim")
        text.append(" ? Help ", style="dim italic")

        return text

    def update_status(
        self,
        hostname: str | None = None,
        refresh_interval: float | None = None,
        is_paused: bool | None = None,
        is_recording: bool | None = None,
        is_replaying: bool | None = None,
    ) -> None:
        """Update status values and refresh display."""
        if hostname is not None:
            self.hostname = hostname
        if refresh_interval is not None:
            self.refresh_interval = refresh_interval
        if is_paused is not None:
            self.is_paused = is_paused
        if is_recording is not None:
            self.is_recording = is_recording
        if is_replaying is not None:
            self.is_replaying = is_replaying
        self.refresh()
