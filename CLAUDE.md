# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sigils is a Python solver for tetromino packing puzzles from *The Talos Principle*. Given a grid size and a set of named pieces (I, O, T, J, L, S, Z), it finds an arrangement that fills the grid completely.

## Commands

Dependencies are managed with [uv](https://docs.astral.sh/uv/): `pyproject.toml` declares them and `uv.lock` pins exact versions (CI installs with `uv sync --locked`). pytest, flake8 and invoke are in the `dev` dependency group, which `uv sync` installs by default.

**Install dependencies:**
```
uv sync
```

**Convenience tasks ([invoke](https://www.pyinvoke.org/), defined in [tasks.py](tasks.py)):**
```
uv run invoke --list                  # show all tasks
uv run invoke start                   # Flask web app (localhost:5000)
uv run invoke start-debug             # Flask with debugger and auto-reload
uv run invoke gui                     # Tkinter GUI
uv run invoke tui                     # Textual TUI
uv run invoke test                    # pytest
uv run invoke test -v -x -k Solve     # verbose, stop on first failure, filter by keyword
uv run invoke lint                    # both flake8 passes (same as CI)
```

**Run CLI solver:**
```
uv run python sigils.py <rows> <cols> <pieces> [-t timeout]
uv run python sigils.py 5 4 IOTLJ
```

**Run Tkinter GUI:**
```
uv run python wsigils.pyw
```

**Run Textual TUI:**
```
uv run python tsigils.py
```

**Run Flask web app:**
```
uv run flask --app app.py run
```

**Run tests:**
```
uv run pytest
```

**Run a single test:**
```
uv run pytest test_sigils.py::TestSigls::testSolveJLO
```

**Lint:**
```
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```
Max line length is 127 characters.

**Add/remove dependencies:**
```
uv add <package>
uv add --dev <package>
uv remove <package>
```

## Architecture

All core logic lives in [sigils.py](sigils.py). The four frontends (CLI in `sigils.py`, Tkinter in [wsigils.pyw](wsigils.pyw), Flask in [app.py](app.py), Textual TUI in [tsigils.py](tsigils.py)) all call into `findSolution` from that module.

**`Sigil` class** — represents a tetromino piece type. Each instance holds a list of `shapes`, where each shape is a `set` of `(row, col)` offsets representing one rotation. Shapes are parsed from ASCII-art strings where `*` marks occupied cells.

**`Board` class** — wraps a NumPy 2D array of characters. Empty cells are `'.'`; placed pieces are letters `A`, `B`, `C`, … `placePiece(shape, row, col, ch)` returns a new `Board` with the piece placed, or `None` on collision/out-of-bounds. `islands()` returns a list of connected-component sets of empty cells using flood fill — used for pruning.

**`findSolution(rows, cols, sigils, timeout=60)`** — public API. Validates piece count (must equal `rows*cols / 4`), then calls `solve`. Returns `(board_or_None, message_string)`.

**`solve(board, pieces, ...)`** — recursive backtracking. Key pruning: if any empty-cell island has a size not divisible by 4, that branch is abandoned immediately. Pieces are sorted by number of rotations before solving (fewer rotations = less branching). Gives up after 100M attempts or the timeout.

**`displayBoard(board)`** — opens a Tkinter window showing the solved board with color-coded pieces (letters A–M map to named colors).

## API Usage

```python
from sigils import findSolution, displayBoard

solution, message = findSolution(3, 4, "JLO")
print(message)
if solution:
    displayBoard(solution)
```

The `R` piece code selects a random piece type at solve time.
