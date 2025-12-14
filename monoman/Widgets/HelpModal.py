"""Help modal widget."""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class HelpModal(ModalScreen[None]):
    """Modal screen showing keyboard shortcuts and help."""

    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
    }

    HelpModal > Container {
        width: 70;
        height: auto;
        max-height: 80%;
        background: #1a1f2e;
        border: thick #91abec;
        padding: 1 2;
    }

    HelpModal #title {
        text-align: center;
        text-style: bold;
        color: #91abec;
        padding-bottom: 1;
    }

    HelpModal #content {
        height: auto;
        max-height: 50;
    }

    HelpModal .section {
        color: #54efae;
        text-style: bold;
        padding-top: 1;
    }

    HelpModal .shortcut {
        padding-left: 2;
    }

    HelpModal .key {
        color: #f0c674;
    }

    HelpModal Button {
        margin-top: 1;
        width: 100%;
    }
    """

    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
        ("?", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help modal."""
        with Container():
            yield Static("Monoman Help", id="title")
            with VerticalScroll(id="content"):
                yield Static("[bold #54efae]Navigation[/]", classes="section")
                yield Static("  [#f0c674]q[/]         Quit application", classes="shortcut")
                yield Static("  [#f0c674]?[/]         Show this help", classes="shortcut")
                yield Static("  [#f0c674]Space[/]     Pause/resume refresh", classes="shortcut")
                yield Static("  [#f0c674]+/-[/]       Increase/decrease refresh rate", classes="shortcut")

                yield Static("[bold #54efae]Panels[/]", classes="section")
                yield Static("  [#f0c674]1[/]         Toggle Dashboard", classes="shortcut")
                yield Static("  [#f0c674]2[/]         Toggle CPU panel", classes="shortcut")
                yield Static("  [#f0c674]3[/]         Toggle Memory panel", classes="shortcut")
                yield Static("  [#f0c674]4[/]         Toggle Disk panel", classes="shortcut")
                yield Static("  [#f0c674]5[/]         Toggle Network panel", classes="shortcut")
                yield Static("  [#f0c674]6[/]         Toggle Processes panel", classes="shortcut")
                yield Static("  [#f0c674]7[/]         Toggle GPU panel", classes="shortcut")
                yield Static("  [#f0c674]8[/]         Toggle Temperature panel", classes="shortcut")
                yield Static("  [#f0c674]g[/]         Toggle Historical Graphs", classes="shortcut")

                yield Static("[bold #54efae]Process List[/]", classes="section")
                yield Static("  [#f0c674]c[/]         Sort by CPU", classes="shortcut")
                yield Static("  [#f0c674]m[/]         Sort by Memory", classes="shortcut")
                yield Static("  [#f0c674]p[/]         Sort by PID", classes="shortcut")
                yield Static("  [#f0c674]n[/]         Sort by Name", classes="shortcut")
                yield Static("  [#f0c674]r[/]         Reverse sort order", classes="shortcut")
                yield Static("  [#f0c674]/[/]         Filter processes", classes="shortcut")

                yield Static("[bold #54efae]Recording[/]", classes="section")
                yield Static("  [#f0c674]R[/]         Start/stop recording", classes="shortcut")

            yield Button("Close [Esc]", variant="primary", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close":
            self.dismiss()

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss()
