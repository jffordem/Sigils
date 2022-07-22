import unittest
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


if __name__ == "__main__":
    unittest.main()
