import time

class SudokuSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle  # 9x9 grid
        self.start_time = None

    def find_unassigned(self):
        """Locate an unassigned cell (value 0) and apply MRV + Degree heuristics."""
        pass

    def is_valid(self, row, col, val):
        """Check if placing val in puzzle[row][col] is valid."""
        pass

    def backtrack(self):
        """Perform recursive backtracking search."""
        pass

    def solve(self):
        """Wrapper that starts timer, calls backtrack, and measures runtime."""
        self.start_time = time.time()
        solved = self.backtrack()
        elapsed = time.time() - self.start_time
        return solved, elapsed


if __name__ == "__main__":
    # Example placeholder puzzle (0 = empty)
    puzzle = [
        [0,0,0,2,6,0,7,0,1],
        [6,8,0,0,7,0,0,9,0],
        [1,9,0,0,0,4,5,0,0],
        [8,2,0,1,0,0,0,4,0],
        [0,0,4,6,0,2,9,0,0],
        [0,5,0,0,0,3,0,2,8],
        [0,0,9,3,0,0,0,7,4],
        [0,4,0,0,5,0,0,3,6],
        [7,0,3,0,1,8,0,0,0]
    ]

    solver = SudokuSolver(puzzle)
    result, time_taken = solver.solve()
    print(f"Solved: {result}, Time: {time_taken:.3f}s")
