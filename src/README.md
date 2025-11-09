# Sudoku Solver

This program solves 9x9 Sudoku puzzles using backtracking with MRV and degree rules to decide what to fill in next.

## What This Part Does
This covers Michael Huber's portion of the group project.  
It includes:
- A backtracking search that fills in the board one spot at a time  
- MRV (Minimum Remaining Values) and Degree for choosing the next empty cell  
- Tie-breaking that goes left to right, then top to bottom  
- Tries numbers in order from 1 to 9  
- Stops automatically if it runs for more than 1 hour  
- Prints the first 4 moves it makes (with the spot, its domain size, degree, and the value it picked)

---

## How to Run It
From the main folder of the project, type:

```bash
python src/solver.py <puzzle_file>
