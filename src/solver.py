# solver.py
# Purpose: Solve Sudoku using Backtracking with MRV + Degree + Forward Checking

import sys, time
from typing import List, Tuple, Optional, Dict
from csp import (
    load_puzzle_file, parse_puzzle_lines, all_vars, row_major_index,
    is_consistent, degree, domain_size, next_values_in_increasing_order,
    forward_check, assign, unassign
)

Grid = List[List[int]]
Var = Tuple[int, int]

class SudokuSolver:
    def __init__(self, puzzle: Grid, time_limit_sec: int = 3600):
        assert len(puzzle) == 9 and all(len(row) == 9 for row in puzzle), "Puzzle must be 9x9"

        # Keep a grid for printing just like the original file
        self.grid: Grid = [row[:] for row in puzzle]

        # Build CSP domains + initial assignments from the grid
        self.domains: Dict[Var, set[int]] = {}
        self.assignments: Dict[Var, int] = {}
        for r in range(9):
            for c in range(9):
                v = self.grid[r][c]
                if v == 0:
                    self.domains[(r, c)] = set(range(1, 10))
                else:
                    self.domains[(r, c)] = {v}
                    self.assignments[(r, c)] = v

        # Pre-propagate the givens once with forward checking
        for v, val in list(self.assignments.items()):
            st = forward_check(self.assignments, v, val, self.domains)
            if st is None:
                raise ValueError("Puzzle has an immediate contradiction.")

        self.start_time: Optional[float] = None
        self.time_limit = time_limit_sec
        self.timed_out = False
        self.trace = []  # records the first 4 assignments for the report

    # ---------- Variable selection (MRV -> Degree -> L→R then T→B) ----------

    def select_var(self) -> Var:
        unassigned = [v for v in self.domains if v not in self.assignments]
        # MRV
        m = min(domain_size(v, self.domains) for v in unassigned)
        cand = [v for v in unassigned if domain_size(v, self.domains) == m]
        # Degree
        d = max(degree(v, self.assignments) for v in cand)
        cand = [v for v in cand if degree(v, self.assignments) == d]
        # Left-to-right primary, top-to-bottom secondary
        cand.sort(key=row_major_index)
        return cand[0]

    # ---------- Search ----------

    def backtrack(self) -> bool:
        if self.start_time is not None and (time.time() - self.start_time) > self.time_limit:
            self.timed_out = True
            return False

        if len(self.assignments) == 81:
            return True

        var = self.select_var()
        r, c = var
        # Capture logging numbers at pick time
        mrv_at_pick = domain_size(var, self.domains)
        deg_at_pick = degree(var, self.assignments)

        for v in next_values_in_increasing_order(var, self.domains):
            if is_consistent(self.assignments, var, v):
                # Log only the first four decisions
                if len(self.trace) < 4:
                    self.trace.append({
                        "row": r, "col": c,
                        "domain_size": mrv_at_pick,
                        "degree": deg_at_pick,
                        "value": v
                    })

                # Assign and propagate
                assign(var, v, self.assignments)
                self.grid[r][c] = v
                state = forward_check(self.assignments, var, v, self.domains)
                if state is not None:
                    if self.backtrack():
                        return True
                    # undo propagation
                    state.restore(self.domains)

                # undo assignment
                unassign(var, self.assignments)
                self.grid[r][c] = 0

                if self.start_time is not None and (time.time() - self.start_time) > self.time_limit:
                    self.timed_out = True
                    return False

        return False

    # ---------- Public API ----------

    def solve(self) -> Tuple[bool, float]:
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
    # If a puzzle file is given, load it; otherwise, use built-in sample
    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path) as f:
            rows = [list(map(int, line.split())) for line in f if line.strip()]
        puzzle = rows
        print(f"Loaded puzzle from {path}\n")
    else:
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
    SudokuSolver.pretty_print(solver.grid)
    solved, time_taken = solver.solve()
    print("\nSolved:", solved, f"Time: {time_taken:.3f}s", "Timed out" if solver.timed_out else "")
    print("\nFinal:")
    SudokuSolver.pretty_print(solver.grid)

    print("\nFirst 4 assignments:")
    for i, t in enumerate(solver.trace, 1):
        print(f"{i}) var=({t['row']},{t['col']}), domain={t['domain_size']}, degree={t['degree']}, value={t['value']}")

        