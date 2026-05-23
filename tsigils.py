"""
Textual TUI for the Sigils tetromino puzzle solver.

Usage:
    poetry run python tsigils.py
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label, Static, Header, Footer, Rule
from textual import work
from rich.text import Text

from sigils import findSolution

PIECE_NAMES = ['I', 'O', 'T', 'J', 'L', 'S', 'Z']

SAMPLE = {"rows": 5, "cols": 4, "I": 1, "O": 1, "T": 2, "J": 1}

PIECE_COLORS = {
    'A': 'red',
    'B': 'green',
    'C': 'blue',
    'D': 'dark_blue',
    'E': 'purple',
    'F': 'gold1',
    'G': 'cyan',
    'H': 'magenta',
    'I': 'yellow',
    'J': 'orange3',
    'K': 'bright_red',
    'L': 'pink1',
    'M': 'orchid',
    'N': 'spring_green1',
    'O': 'cornflower_blue',
    'P': 'hot_pink',
    'Q': 'chartreuse1',
    'R': 'dark_orange',
    'S': 'violet',
    'T': 'deep_sky_blue1',
    'U': 'aquamarine1',
}


def board_to_rich(board) -> Text:
    """Render a Board as Rich Text using Unicode block characters, 2x size."""
    if board is None:
        return Text("No solution found.", style="bold red")
    text = Text()
    first = True
    for line in str(board).split('\n'):
        for _ in range(2):
            if not first:
                text.append("\n")
            first = False
            for ch in line:
                if ch == '.':
                    text.append("░░░░", style="dim white")
                else:
                    text.append("████", style=f"bold {PIECE_COLORS.get(ch, 'white')}")
    return text


class Spinner(Horizontal):
    """Labeled numeric spinner with +/- buttons. Handles its own button presses."""

    class Changed(Message):
        """Posted when the value changes via a button press."""

    DEFAULT_CSS = """
    Spinner {
        height: 3;
    }
    Spinner Label.title {
        width: 8;
        height: 3;
        content-align: left middle;
        padding: 0 1;
    }
    Spinner Button {
        width: 3;
        min-width: 3;
        height: 3;
    }
    Spinner Label.val {
        width: 6;
        height: 3;
        content-align: center middle;
        background: $boost;
        border: tall $background;
    }
    """

    count: reactive[int] = reactive(0)

    def __init__(self, label: str, initial: int = 0, min_val: int = 0, **kwargs):
        self._label = label
        self._initial = initial
        self._min = min_val
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Label(self._label, classes="title")
        yield Button("-", id=f"{self.id}-dec")
        yield Label(str(self._initial), classes="val")
        yield Button("+", id=f"{self.id}-inc")

    def on_mount(self) -> None:
        self.count = self._initial

    def watch_count(self, val: int) -> None:
        self.query_one("Label.val", Label).update(str(val))

    @property
    def value(self) -> int:
        return self.count

    @value.setter
    def value(self, v: int) -> None:
        self.count = max(self._min, v)

    def reset(self) -> None:
        self.count = self._initial

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id.endswith("-dec"):
            self.count = max(self._min, self.count - 1)
        elif btn_id.endswith("-inc"):
            self.count = self.count + 1
        event.stop()
        self.post_message(self.Changed())


class SigilsApp(App):
    """Textual TUI for solving tetromino puzzles from The Talos Principle."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #controls {
        width: 38;
        min-width: 38;
        border: round $primary;
        padding: 1 2;
        height: 100%;
    }

    .section-label {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #action-buttons {
        height: 3;
        margin-top: 1;
    }

    #solve-btn {
        width: 1fr;
        margin-right: 1;
    }

    #reset-btn {
        width: 1fr;
    }

    #status {
        margin-top: 1;
    }

    #board-panel {
        border: round $primary;
        padding: 1 2;
        height: 100%;
    }

    #board-display {
        height: 1fr;
    }
    """

    TITLE = "Sigils — Tetromino Puzzle Solver"
    BINDINGS = [
        ("ctrl+s", "solve", "Solve"),
        ("ctrl+r", "reset", "Reset"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            with Vertical(id="controls"):
                yield Label("Grid Size", classes="section-label", id="grid-size-label")
                yield Spinner("Rows:", initial=SAMPLE["rows"], min_val=1, id="spinner-rows")
                yield Spinner("Cols:", initial=SAMPLE["cols"], min_val=1, id="spinner-cols")

                yield Rule()
                yield Label("Pieces", classes="section-label", id="pieces-label")
                for piece in PIECE_NAMES:
                    yield Spinner(f"{piece}:", initial=SAMPLE.get(piece, 0), id=f"spinner-{piece}")

                yield Rule()
                with Horizontal(id="action-buttons"):
                    yield Button("Solve", id="solve-btn", variant="primary")
                    yield Button("Reset", id="reset-btn")

                yield Label("", id="status")

            with Vertical(id="board-panel"):
                yield Label("Solution", classes="section-label")
                yield Static("", id="board-display")

        yield Footer()

    def on_mount(self) -> None:
        self.action_solve()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "solve-btn":
            self.action_solve()
        elif event.button.id == "reset-btn":
            self.action_reset()

    def on_spinner_changed(self, _: Spinner.Changed) -> None:
        self.action_solve()

    def _grid_size(self) -> tuple[int, int]:
        return (
            self.query_one("#spinner-rows", Spinner).value,
            self.query_one("#spinner-cols", Spinner).value,
        )

    def _pieces_str(self) -> str:
        return "".join(
            piece * self.query_one(f"#spinner-{piece}", Spinner).value
            for piece in PIECE_NAMES
        )

    def _update_labels(self) -> None:
        rows, cols = self._grid_size()
        total = rows * cols
        pieces_selected = sum(
            self.query_one(f"#spinner-{p}", Spinner).value for p in PIECE_NAMES
        )
        if total > 0 and total % 4 != 0:
            self.query_one("#grid-size-label", Label).update(
                "Grid Size [bold red](not divisible by 4)[/bold red]"
            )
            self.query_one("#pieces-label", Label).update("Pieces")
        else:
            self.query_one("#grid-size-label", Label).update("Grid Size")
            pieces_needed = total // 4 if total > 0 else 0
            self.query_one("#pieces-label", Label).update(
                f"Pieces ({pieces_selected} of {pieces_needed})"
            )

    def action_solve(self) -> None:
        self._update_labels()
        rows, cols = self._grid_size()
        pieces_str = self._pieces_str()
        if rows <= 0 or cols <= 0 or not pieces_str:
            self.query_one("#status").update("")
            return
        self.query_one("#solve-btn", Button).disabled = True
        self.query_one("#status").update("[bold yellow]Solving...[/bold yellow]")
        self.query_one("#board-display", Static).update("")
        self._run_solver(rows, cols, pieces_str)

    def action_reset(self) -> None:
        for spinner in self.query(Spinner):
            spinner.reset()
        self.query_one("#board-display", Static).update("")
        self.query_one("#status").update("")
        self.action_solve()

    @work(thread=True, exclusive=True)
    def _run_solver(self, rows: int, cols: int, pieces_str: str) -> None:
        solution, message = findSolution(rows, cols, pieces_str, timeout=60)
        board_text = board_to_rich(solution)
        self.call_from_thread(self._show_result, board_text, message)

    def _show_result(self, board_text: Text, message: str) -> None:
        self.query_one("#board-display", Static).update(board_text)
        self.query_one("#status").update(message)
        self.query_one("#solve-btn", Button).disabled = False


if __name__ == "__main__":
    SigilsApp().run()
