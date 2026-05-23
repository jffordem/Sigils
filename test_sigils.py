import unittest
import time
import numpy as np
from sigils import *

class TestSigls(unittest.TestCase):

    def testSigil(self):
        self.assertTrue(len(SIGIL_O.shapes) == 1)
        actual = SIGIL_O.shapes[0]
        expected = {(0, 0), (0, 1), (1, 0), (1, 1)}
        self.assertEqual(actual, expected)

    def testEmptyBoard(self):
        board = Board(Board.empty(3, 4))
        actual = str(board)
        expected = "\n".join(["...."] * 3)
        self.assertEqual(actual, expected)
        rows, cols = board.size()
        self.assertEqual((rows, cols), (3, 4))
        islands = board.islands()
        self.assertEqual(1, len(islands))
        self.assertEqual(12, len(islands[0]))

    def testPlacePiece(self):
        board = Board(Board.empty(3, 4))
        board = board.placePiece(SIGIL_O.shapes[0], 1, 1, 'X')
        actual = str(board)
        expected = "....\n.XX.\n.XX."
        self.assertEqual(actual, expected)
        islands = board.islands()
        self.assertEqual(1, len(islands))
        self.assertEqual(8, len(islands[0]))

    def testSolveIII(self):
        board = Board(Board.empty(3, 4))
        pieces = [SIGIL_I] * 3
        actual = str(solve(board, pieces))
        expected = "AAAA\nBBBB\nCCCC"
        self.assertEqual(actual, expected)

    def testSolveJLO(self):
        board = Board(Board.empty(3, 4))
        pieces = [SIGIL_O, SIGIL_J, SIGIL_L]
        actual = str(solve(board, pieces))
        expected = "CAAB\nCAAB\nCCBB"
        self.assertEqual(actual, expected)

    def testNoSolution(self):
        board = Board(Board.empty(3, 4))
        pieces = [SIGIL_O] * 3
        actual = solve(board, pieces)
        self.assertTrue(actual is None)

    # --- placePiece edge cases ---

    def testPlacePieceOutOfBoundsRight(self):
        board = Board(Board.empty(3, 4))
        # Horizontal I at col 1 would reach col 4, which is out of bounds
        result = board.placePiece(SIGIL_I.shapes[0], 0, 1, 'A')
        self.assertIsNone(result)

    def testPlacePieceOutOfBoundsBottom(self):
        board = Board(Board.empty(3, 4))
        # Vertical I at row 1 would reach row 4, which is out of bounds
        result = board.placePiece(SIGIL_I.shapes[1], 1, 0, 'A')
        self.assertIsNone(result)

    def testPlacePieceCollision(self):
        board = Board(Board.empty(3, 4))
        board = board.placePiece(SIGIL_O.shapes[0], 0, 0, 'A')
        self.assertIsNotNone(board)
        result = board.placePiece(SIGIL_O.shapes[0], 0, 0, 'B')
        self.assertIsNone(result)

    # --- island detection ---

    def testIslandsDisconnected(self):
        # Two isolated 2-cell regions separated by a filled column
        arr = np.full((2, 3), 'X')
        arr[:, 0] = '.'
        arr[:, 2] = '.'
        islands = Board(arr).islands()
        self.assertEqual(2, len(islands))
        self.assertEqual(sorted(len(i) for i in islands), [2, 2])

    def testIslandsOddSizePrunable(self):
        # A 3-cell island can never be filled by tetrominoes — solver should prune it
        arr = np.full((2, 4), 'X')
        arr[0, 0] = '.'
        arr[0, 1] = '.'
        arr[1, 0] = '.'
        board = Board(arr)
        islands = board.islands()
        self.assertEqual(1, len(islands))
        self.assertEqual(3, len(islands[0]))
        self.assertTrue(any(len(island) % 4 != 0 for island in islands))

    # --- findSolution API ---

    def testFindSolutionWrongCount(self):
        solution, message = findSolution(3, 4, "I")   # 1 piece, board needs 3
        self.assertIsNone(solution)
        self.assertIn("Wrong number", message)

    def testFindSolutionUnknownPiece(self):
        solution, message = findSolution(2, 4, "IX")  # X is not a valid piece
        self.assertIsNone(solution)
        self.assertIn("unknown piece", message)

    def testFindSolutionFillsBoard(self):
        solution, message = findSolution(3, 4, "JLO")
        self.assertIsNotNone(solution)
        self.assertNotIn('.', str(solution))
        self.assertIn("Duration", message)

    def testFindSolutionNoSolution(self):
        solution, message = findSolution(3, 4, "OOO")
        self.assertIsNone(solution)

    def testFindSolutionSinglePiece(self):
        solution, message = findSolution(1, 4, "I")
        self.assertIsNotNone(solution)
        self.assertEqual(str(solution), "AAAA")

    def testFindSolutionLarger(self):
        solution, _ = findSolution(4, 4, "OOOO")
        self.assertIsNotNone(solution)
        self.assertNotIn('.', str(solution))

    # --- solve robustness ---

    def testSolveDefaultMetaFreshEachCall(self):
        # Each bare solve() call should get independent state, not share a dict
        board = Board(Board.empty(3, 4))
        pieces = [SIGIL_I] * 3
        r1 = solve(board, pieces)
        r2 = solve(board, pieces)
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)

    def testSolveTimeout(self):
        # Pre-expire the start time so the solver bails immediately
        board = Board(Board.empty(4, 4))
        pieces = [SIGIL_T] * 4
        meta = {"count": 0, "bad": 0, "missing": 0, "start": time.time() - 100}
        result = solve(board, pieces, timeout=60, meta=meta)
        self.assertIsNone(result)

    def testSolveEmptyPiecesEmptyBoard(self):
        # Zero pieces on a zero-island board should return the (trivially solved) board
        board = Board(Board.empty(0, 0))
        result = solve(board, [])
        self.assertIsNotNone(result)

    def testSolveEmptyPiecesRemainingCells(self):
        # Pieces exhausted but cells remain — must return None, not raise IndexError
        board = Board(Board.empty(3, 4))
        result = solve(board, [])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
