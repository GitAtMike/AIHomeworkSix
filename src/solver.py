# solver.py
# Author: Michael
# Purpose: Solve Sudoku using Backtracking with MRV and Degree Heuristics
# Note: Forward checking is NOT included here (Person B task).

import time
from typing import List, Tuple, Optional

Grid = List[List[int]]

class SudokuSolver:
    def __init__(self, puzzle: Grid, time_limit_sec: int = 3600):
        assert len(puzzle) == 9 and all(len(row) == 9 for row in puzzle), "Puzzle must be 9x9"
        self.puzzle: Grid = [row[:] for row in puzzle]  # defensive copy
        self.start_time: Optional[float] = None
        self.time_limit = time_limit_sec
        self.timed_out = False
        self.trace = []  # records the first 4 assignments for the report

    # ---------- Helpers ----------

    def _candidates(self, row: int, col: int) -> List[int]:
        """Return sorted list of legal values {1..9} for cell (row,col)."""
        if self.puzzle[row][col] != 0:
            return []

        used = set()

        # Row
        for c in range(9):
            v = self.puzzle[row][c]
            if v:
                used.add(v)

        # Column
        for r in range(9):
            v = self.puzzle[r][col]
            if v:
                used.add(v)

        # 3x3 box
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                v = self.puzzle[r][c]
                if v:
                    used.add(v)

        return [v for v in range(1, 10) if v not in used]

    def _degree(self, row: int, col: int) -> int:
        """
        Degree heuristic: number of *unassigned* neighbors in same row/col/box.
        Higher degree preferred to break MRV ties.
        """
        if self.puzzle[row][col] != 0:
            return -1

        seen = set()

        # Row neighbors
        for c in range(9):
            if c != col and self.puzzle[row][c] == 0:
                seen.add((row, c))

        # Column neighbors
        for r in range(9):
            if r != row and self.puzzle[r][col] == 0:
                seen.add((r, col))

        # Box neighbors
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r != row or c != col) and self.puzzle[r][c] == 0:
                    seen.add((r, c))

        return len(seen)

    # ---------- Heuristic selection (MRV + Degree + L→R primary, T→B secondary) ----------

    def find_unassigned(self) -> Tuple[Optional[int], Optional[int], List[int], Optional[int], Optional[int]]:
        """
        Pick next cell using MRV then Degree.
        MRV = smallest candidate set size.
        Ties → higher degree first.
        Final tie → left-to-right (primary) then top-to-bottom (secondary).
        Returns (row, col, candidates, mrv, degree) or (None, None, [], None, None) if all filled.
        """
        best = None  # (mrv, -degree, col, row, candidates)

        for r in range(9):           # iterate grid
            for c in range(9):
                if self.puzzle[r][c] == 0:
                    cand = self._candidates(r, c)
                    mrv = len(cand)
                    if mrv == 0:
                        # Dead end; report now so caller can fail fast
                        return r, c, [], 0, self._degree(r, c)
                    deg = self._degree(r, c)
                    # Tie order: MRV, then -degree, then LEFT→RIGHT (col), then TOP→BOTTOM (row)
                    key = (mrv, -deg, c, r)
                    if best is None or key < best[:4]:
                        best = (mrv, -deg, c, r, cand)

        if best is None:
            return None, None, [], None, None
        mrv, neg_deg, c, r, cand = best
        cand.sort()  # values in increasing order per spec
        return r, c, cand, mrv, -neg_deg

    # ---------- Constraints ----------

    def is_valid(self, row: int, col: int, val: int) -> bool:
        """True if val can be placed at (row,col) per Sudoku rules."""
        # Row
        for c in range(9):
            if self.puzzle[row][c] == val:
                return False

        # Column
        for r in range(9):
            if self.puzzle[r][col] == val:
                return False

        # Box
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if self.puzzle[r][c] == val:
                    return False

        return True

    # ---------- Search ----------

    def backtrack(self) -> bool:
        """
        Recursive backtracking using MRV + Degree selection.
        Tries candidate values in increasing order.
        Enforces a 1-hour timeout.
        """
        # Timeout check
        if self.start_time is not None and (time.time() - self.start_time) > self.time_limit:
            self.timed_out = True
            return False

        r, c, cand, mrv, deg = self.find_unassigned()
        if r is None:
            return True  # all assigned

        for v in cand:
            if self.is_valid(r, c, v):
                # Log only the first four decisions
                if len(self.trace) < 4:
                    self.trace.append({
                        "row": r, "col": c,
                        "domain_size": mrv,
                        "degree": deg,
                        "value": v
                    })
                self.puzzle[r][c] = v
                if self.backtrack():
                    return True
                self.puzzle[r][c] = 0  # undo
                # Timeout check during deep recursion
                if self.start_time is not None and (time.time() - self.start_time) > self.time_limit:
                    self.timed_out = True
                    return False
        return False

    # ---------- Public API ----------

    def solve(self) -> Tuple[bool, float]:
        """Start timer, call backtrack, return (solved, elapsed_seconds)."""
        self.start_time = time.time()
        solved = self.backtrack()
        elapsed = time.time() - self.start_time
        return solved, elapsed

    @staticmethod
    def pretty_print(grid: Grid) -> None:
        for r in range(9):
            row = []
            for c in range(9):
                v = grid[r][c]
                row.append(str(v) if v != 0 else ".")
            print(" ".join(row))


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
    print("Initial:")
    SudokuSolver.pretty_print(solver.puzzle)
    solved, time_taken = solver.solve()
    print("\nSolved:", solved, f"Time: {time_taken:.3f}s", "Timed out" if solver.timed_out else "")
    print("\nFinal:")
    SudokuSolver.pretty_print(solver.puzzle)

    print("\nFirst 4 assignments:")
    for i, t in enumerate(solver.trace, 1):
        print(f"{i}) var=({t['row']},{t['col']}), domain={t['domain_size']}, degree={t['degree']}, value={t['value']}")
