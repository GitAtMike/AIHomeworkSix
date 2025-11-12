# csp.py
# Jacob York: CSP representation + forward checking for 9x9 Sudoku

from typing import Dict, Set, Tuple, List, Optional

Var = Tuple[int, int]  # (row, col) 0-based
Domain = Dict[Var, Set[int]]
Neighbors = Dict[Var, Set[Var]]

# Grid & CSP structure

def all_vars() -> List[Var]:
    return [(r, c) for r in range(9) for c in range(9)]

def row_major_index(v: Var) -> int:
    """Use to break ties left->right, then top->bottom."""
    r, c = v
    return r * 9 + c

def box_id(r: int, c: int) -> Tuple[int, int]:
    return (r // 3, c // 3)

def build_neighbors() -> Neighbors:
    N: Neighbors = {}
    for r in range(9):
        for c in range(9):
            v = (r, c)
            peers: Set[Var] = set()
            # row & col
            peers.update({(r, cc) for cc in range(9) if cc != c})
            peers.update({(rr, c) for rr in range(9) if rr != r})
            # 3x3 box
            br, bc = 3 * (r // 3), 3 * (c // 3)
            peers.update({(rr, cc)
                          for rr in range(br, br + 3)
                          for cc in range(bc, bc + 3)
                          if (rr, cc) != (r, c)})
            N[v] = peers
    return N

NEIGHBORS = build_neighbors()

def parse_puzzle_lines(lines: List[str]) -> Tuple[Domain, Dict[Var, int]]:
    
    #lines: 9 strings with 9 integers each, 0 means empty. returns (domains, initial_assignments)
    
    doms: Domain = {}
    asg: Dict[Var, int] = {}
    for r, line in enumerate(lines):
        vals = [int(x) for x in line.split()]
        for c, v in enumerate(vals):
            var = (r, c)
            if v == 0:
                doms[var] = set(range(1, 10))
            else:
                doms[var] = {v}
                asg[var] = v
    return doms, asg

def load_puzzle_file(path: str) -> Tuple[Domain, Dict[Var, int]]:
    with open(path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return parse_puzzle_lines(lines)

# Constraints & helpers

def is_consistent(assignments: Dict[Var, int], var: Var, val: int) -> bool:
    """Value must differ from all assigned peers."""
    for n in NEIGHBORS[var]:
        if n in assignments and assignments[n] == val:
            return False
    return True

def degree(var: Var, assignments: Dict[Var, int]) -> int:
    """Number of unassigned neighbors (for Degree heuristic)."""
    return sum(1 for n in NEIGHBORS[var] if n not in assignments)

def domain_size(var: Var, domains: Domain) -> int:
    return len(domains[var])

# Forward checking with restoration

class FCState:
    """
    Tracks all domain prunings so we can restore on backtrack.
    Each entry is (neighbor, removed_value).
    """
    def __init__(self):
        self.pruned: List[Tuple[Var, int]] = []

    def record_prune(self, v: Var, val: int):
        self.pruned.append((v, val))

    def restore(self, domains: Domain):
        for v, val in reversed(self.pruned):
            domains[v].add(val)
        self.pruned.clear()

def forward_check(assignments: Dict[Var, int], var: Var, val: int,
                  domains: Domain) -> Optional[FCState]:
    """
    Apply forward checking after assigning var=val.
    Remove 'val' from every unassigned neighbor's domain.
    If any neighbor domain becomes empty -> return None (failure).
    Otherwise return FCState (to be restored on backtrack).
    """
    state = FCState()
    for n in NEIGHBORS[var]:
        if n in assignments:
            continue
        if val in domains[n]:
            domains[n].remove(val)
            state.record_prune(n, val)
            if len(domains[n]) == 0:
                # dead-end; restore before returning failure
                state.restore(domains)
                return None
    return state

# Apply/undo assignments

def assign(var: Var, val: int, assignments: Dict[Var, int]):
    assignments[var] = val

def unassign(var: Var, assignments: Dict[Var, int]):
    if var in assignments:
        del assignments[var]

# Example integration skeleton (Person A owns the search)

def next_values_in_increasing_order(var: Var, domains: Domain) -> List[int]:
    """Rubric requires 1..9 increasing ordering."""
    return sorted(domains[var])

