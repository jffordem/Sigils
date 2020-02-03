# sigils.py

import sys
import random
import numpy as np
import time

__doc__ = """
Sigils

Solves tetromino problems from games like Talos Principle.

Usage:
    sigils.py <rows> <cols> <sigils...>

    Sigils are: I, O, T, J, L, S, Z

Example:
    sigils.py 4 7 I I T T Z S L
"""


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

    @staticmethod
    def empty(rows, cols):
        return np.full((rows, cols), '.')

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
    islands = board.islands()
    if len(pieces) == 0 and len(islands) == 0:
        return board
    elif meta["count"] > 100000000:
        if "quiet" not in meta:
            meta["quiet"] = True
            print("Giving up after 100M tries.")
        return None
    elif time.time() - meta["start"] > timeout:
        if "quiet" not in meta:
            meta["quiet"] = True
            print("Giving up after", timeout, "seconds")
        return None
    elif any(len(island) % 4 != 0 for island in islands):
        meta["bad"] += 1
        return None
    else:
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
        return None


if __name__ == "__main__":
    pieces = list()
    if len(sys.argv) > 3:
        rows = int(sys.argv[1])
        cols = int(sys.argv[2])
        for s in sys.argv[3:]:
            for ch in s.upper():
                if ch in SIGILS:
                    pieces.append(SIGILS[ch])
                elif ch == 'R':
                    ch = random.choice(list(SIGILS.keys()))
                    print("Selected random piece", ch)
                    pieces.append(SIGILS[ch])
                else:
                    print("Error: unknown piece", ch)
                    exit()
        board = Board(Board.empty(rows, cols))
        if len(pieces) * 4 != rows * cols:
            print("Wrong number of pieces.")
        else:
            pieces = sorted(pieces, key=lambda piece: len(piece))
            start = time.time()
            solution = solve(board, pieces)
            duration = time.time() - start
            if duration > 2:
                print("Solution:", int(duration), "seconds")
            else:
                print("Solution:", int(duration * 1000), "ms")
            print(solution)
    else:
        print(__doc__)
