# sigils.py

import random
import numpy as np
import time
import argparse
import tkinter as tk
from collections import namedtuple


class Sigil:
    def __init__(self, *patterns):
        self.shapes = [Sigil.pointsFromPattern(pattern) for pattern in patterns]

    def __iter__(self):
        return self.shapes.__iter__()

    def __len__(self):
        return len(self.shapes)

    @staticmethod
    def pointsFromPattern(pattern):
        result = set()
        for row, line in enumerate(pattern.split('\n')):
            for col, ch in enumerate(line):
                if ch == '*':
                    result.add((row, col))
        return result


SIGIL_I = Sigil(
    "****",
    "*\n*\n*\n*"
)
SIGIL_T = Sigil(
    "***\n *",
    "*\n**\n*",
    " * \n***",
    " *\n**\n *"
)
SIGIL_O = Sigil(
    "**\n**"
)
SIGIL_J = Sigil(
    "***\n  *",
    " *\n *\n**",
    "*  \n***",
    "**\n*\n*"
)
SIGIL_L = Sigil(
    "***\n*  ",
    "**\n *\n *",
    "  *\n***",
    "*\n*\n**"
)
SIGIL_S = Sigil(
    " **\n** ",
    "*\n**\n *"
)
SIGIL_Z = Sigil(
    "** \n **",
    " *\n**\n*"
)

SIGILS = {
    'I': SIGIL_I,
    'T': SIGIL_T,
    'O': SIGIL_O,
    'J': SIGIL_J,
    'L': SIGIL_L,
    'S': SIGIL_S,
    'Z': SIGIL_Z
}


class Board:
    def __init__(self, array):
        self.__array = array

    @classmethod
    def empty(cls, rows, cols):
        return cls(np.full((rows, cols), '.'))

    def __str__(self):
        rows, _ = self.size()
        return "\n".join("".join(self.__array[row]) for row in range(rows))

    def placePiece(self, shape, row, col, ch):
        rows, cols = self.size()
        if any(r + row >= rows or c + col >= cols for r, c in shape):
            return None
        if any(self.__array[r + row, c + col] != '.' for r, c in shape):
            return None
        copy = np.copy(self.__array)
        for r, c in shape:
            copy[r + row, c + col] = ch
        return Board(copy)

    def size(self):
        return self.__array.shape

    def islands(self):
        def adjacent(island, hole):
            row, col = hole
            neighbors = {
                (row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1)
            }
            return len(island.intersection(neighbors)) > 0
        rows, cols = self.size()
        holes = [(row, col) for row in range(rows) for col in range(cols) if self.__array[row, col] == '.']
        islands = list()
        for hole in holes:
            neighbors = [index for index, island in enumerate(islands) if adjacent(island, hole)]
            if len(neighbors) == 0:
                islands.append({hole})
            elif len(neighbors) == 1:
                islands[neighbors[0]].add(hole)
            else:
                island = set()
                for i in neighbors:
                    island.update(islands[i])
                    island.add(hole)
                islands = [island for index, island in enumerate(islands) if index not in neighbors]
                islands.append(island)
        return islands


def solve(board, pieces, timeout=60, ch=ord('A'), meta={"count": 0, "bad": 0, "missing": 0, "start": time.time()}):
    #print("solving", str(board), str(len(pieces)), "pieces left...")
    islands = board.islands()
    if len(pieces) == 0:
        #print("no more pieces.")
        return board
    elif meta["count"] > 100000000:
        if "quiet" not in meta:
            meta["quiet"] = True
            print("Giving up after 100M tries.")
        #print("out of count.")
        return None
    elif time.time() - meta["start"] > timeout:
        if "quiet" not in meta:
            meta["quiet"] = True
            print("Giving up after", timeout, "seconds")
        #print("out of time.")
        return None
    elif any(len(island) % 4 != 0 for island in islands):
        meta["bad"] += 1
        #print('bad.')
        return None
    else:
        #print("attempting with")
        rows, cols = board.size()
        piece, remaining = pieces[0], pieces[1:]
        for shape in piece:
            for row in range(rows):
                for col in range(cols):
                    meta["count"] += 1
                    if "quiet" not in meta and meta["count"] % 500000 == 0:
                        print(str(meta), str(board), sep='\n')
                    newBoard = board.placePiece(shape, row, col, chr(ch))
                    if newBoard:
                        solved = solve(newBoard, remaining, timeout, ch + 1, meta)
                        if solved:
                            return solved
        #print("gave up on this one.")
        return None


Var = namedtuple("Var", "var init")


class BoardCanvas:
    def __init__(self, master, width, height):
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(master, width=width, height=height)
        self.canvas.pack()
    def display(self, board):
        if board is not None:
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill="white")
            rows, cols = board.size()
            if rows > 0 and cols > 0:
                size = min(self.height / rows, self.width / cols)
                s = str(board)
                for row, line in enumerate(s.split('\n')):
                    for col, ch in enumerate(line):
                        x, y = col * size, row * size
                        self.canvas.create_rectangle(x, y, x + size, y + size, fill=BoardCanvas.getColor(ch))
            else:
                self._drawX()
        else:
            self._drawX()
    def _drawX(self):
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="yellow")
        self.canvas.create_line(0, 0, self.width, self.height, fill="black", width=3)
        self.canvas.create_line(0, self.height, self.width, 0, fill="black", width=3)
    @staticmethod
    def getColor(ch):
        colors = { 
            'A': 'red', 
            'B': 'green', 
            'C': 'blue', 
            'D': 'navy',
            'E': 'purple',
            'F': 'goldenrod',
            'G': 'cyan',
            'H': 'magenta',
            'I': 'yellow',
            'J': 'brown',
            'K': 'coral',
            'L': 'pink',
            'M': 'orchid' 
        }
        if ch not in colors: return 'dim gray'
        return colors[ch]

class Window:
    def __init__(self, master, caption="Caption"):
        self.master = master
        master.title(caption)
        self._initMenus(master)
        self._initControls(master)
    def _initMenus(self, master):
        menu = tk.Menu(master)
        master.config(menu=menu)
        fileMenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        helpMenu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=helpMenu)
        fileMenu.add_command(label="Exit", command=master.quit)
        helpMenu.add_command(label="About")
    def _initControls(self, master):
        self.fields = { 
            "Rows": Var(tk.IntVar(), 4),
            "Columns": Var(tk.IntVar(), 4),
            "L": Var(tk.IntVar(), 0),
            "I": Var(tk.IntVar(), 0),
            "O": Var(tk.IntVar(), 0),
            "T": Var(tk.IntVar(), 0),
            "J": Var(tk.IntVar(), 0),
            "Z": Var(tk.IntVar(), 0),
            "S": Var(tk.IntVar(), 0)
        }
        left = tk.Frame(master)
        right = tk.Frame(master)
        left.pack(side=tk.LEFT)
        right.pack(side=tk.RIGHT)
        for i, (name, field) in enumerate(self.fields.items()):
            tk.Label(left, width=8, text=name, anchor='w').grid(row=i, column=0)
            tk.Spinbox(left, width=5, from_=0, to=50, textvariable=field.var).grid(row=i, column=1)
            field.var.trace("w", self.onFieldChanged)
        self.canvas = BoardCanvas(right, 200, 200)
        row = len(self.fields)+1
        #tk.Button(left, text="Solve", command=self.onSolveClicked).grid(row=row, column=0)
        tk.Button(left, text="Reset", command=self.onResetClicked).grid(row=row, column=1)
        self.onResetClicked()
    def onResetClicked(self):
        for field in self.fields.values():
            field.var.set(field.init)
    def onFieldChanged(self, *args):
        self.onSolveClicked()
    def onSolveClicked(self):
        board = Board.empty(self.fields["Rows"].var.get(), self.fields["Columns"].var.get())
        pieces = [sigil for sigils in ([SIGILS[ch]] * self.fields[ch].var.get() for ch in "LIOTJSZ") for sigil in sigils]
        pieces = sorted(pieces, key=lambda piece: len(piece))
        self.master.config(cursor='wait')
        self.master.update()
        board = solve(board, pieces, timeout=2, meta={"count": 0, "bad": 0, "missing": 0, "start": time.time()})
        self.master.config(cursor='')
        self.canvas.display(board)


if __name__ == "__main__":
    root = tk.Tk()
    Window(root, "Tetrominos!")
    root.mainloop()
