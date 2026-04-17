"""
Experiment 14: Global Data Flow Analysis (Simple)

Input style (simple):
- Number of basic blocks (m)
- For each block Bi:
    number of statements
    then those statements (3-address-ish)
- Then CFG:
    successors of each block (space separated), e.g. "2 3" or blank for none

Statements supported (very lenient parsing):
- Assignments: x := y + z,  x = y,  x := y,  x := a*b, etc.
- Other statements: "if x goto B2", "return x", "print x", "goto B3"

Output:
- USE/DEF per block
- IN/OUT per block (for chosen analysis)
"""

from typing import Dict, List, Set, Tuple
import re

IDENT_RE = re.compile(r"[A-Za-z_]\w*")
ASSIGN_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*(?::=|=)\s*(.+?)\s*$")

# Keywords to ignore when extracting variables from statements
KEYWORDS = {
    "if", "goto", "then", "else", "return", "print", "while", "do",
    "and", "or", "not",
    # treat block labels like B1, B2 as non-variables (simple rule below too)
}

BLOCKLABEL_RE = re.compile(r"^[Bb]\d+$")


def extract_idents(s: str) -> List[str]:
    """Extract identifier-like tokens, excluding keywords and block labels."""
    raw = IDENT_RE.findall(s)
    out: List[str] = []
    for tok in raw:
        if tok.lower() in KEYWORDS:
            continue
        if BLOCKLABEL_RE.match(tok):
            continue
        out.append(tok)
    return out


def compute_use_def_for_block(stmts: List[str]) -> Tuple[Set[str], Set[str]]:
    """
    USE[B] = variables used before any definition in the block
    DEF[B] = variables assigned in the block
    """
    use: Set[str] = set()
    defs: Set[str] = set()

    for line in stmts:
        line = line.strip().rstrip(";").strip()
        if not line:
            continue

        m = ASSIGN_RE.match(line)
        if m:
            lhs = m.group(1)
            rhs = m.group(2)

            # Uses come from RHS
            rhs_ids = extract_idents(rhs)
            for v in rhs_ids:
                if v not in defs:
                    use.add(v)

            # Definition of LHS
            defs.add(lhs)
        else:
            # Non-assignment statement: treat all identifiers as USE (if not defined yet)
            ids = extract_idents(line)
            for v in ids:
                if v not in defs:
                    use.add(v)

    return use, defs


def read_program() -> Tuple[List[List[str]], Dict[int, List[int]]]:
    print("GLOBAL DATA FLOW ANALYSIS")
    print("=" * 45)
    print("Enter basic blocks.\n")

    try:
        m = int(input("Number of basic blocks: ").strip())
    except (ValueError, EOFError):
        m = 0

    blocks: List[List[str]] = []
    succ: Dict[int, List[int]] = {}

    if m <= 0:
        print("\nNo input given, using default example (3 blocks).\n")

        # Default blocks (simple)
        blocks = [
            ["t1 := a + b", "c := t1"],     # B1
            ["t2 := c + d"],                # B2
            ["print t2", "return t2"],      # B3
        ]
        # CFG: B1 -> B2,  B2 -> B3,  B3 -> (none)
        succ = {1: [2], 2: [3], 3: []}

        print("Default Basic Blocks:")
        for i, st in enumerate(blocks, start=1):
            print(f"  B{i}:")
            for s in st:
                print("    ", s)
        print("\nDefault CFG successors:")
        for i in range(1, 4):
            print(f"  succ(B{i}) = {succ[i]}")
        return blocks, succ

    # Read blocks
    for i in range(1, m + 1):
        print(f"\nBlock B{i}:")
        try:
            k = int(input("  Number of statements: ").strip())
        except (ValueError, EOFError):
            k = 0

        stmts: List[str] = []
        for j in range(k):
            try:
                line = input(f"    S{j+1}: ").strip()
            except EOFError:
                line = ""
            if line:
                stmts.append(line)
        blocks.append(stmts)

    # Read CFG successors
    print("\nEnter CFG successors:")
    print("Example: for B1 type: 2 3    (means edges B1->B2 and B1->B3)")
    print("Leave blank if no successors.\n")

    for i in range(1, m + 1):
        try:
            s = input(f"  Successors of B{i}: ").strip()
        except EOFError:
            s = ""
        if not s:
            succ[i] = []
        else:
            parts = s.split()
            succ[i] = []
            for p in parts:
                if p.isdigit():
                    x = int(p)
                    if 1 <= x <= m:
                        succ[i].append(x)

    return blocks, succ


def build_predecessors(succ: Dict[int, List[int]], m: int) -> Dict[int, List[int]]:
    pred: Dict[int, List[int]] = {i: [] for i in range(1, m + 1)}
    for u, nbrs in succ.items():
        for v in nbrs:
            pred[v].append(u)
    return pred


def solve_liveness(
    use: Dict[int, Set[str]],
    defs: Dict[int, Set[str]],
    succ: Dict[int, List[int]],
    m: int,
) -> Tuple[Dict[int, Set[str]], Dict[int, Set[str]]]:
    """Backward: OUT[B] = U IN[S], IN[B] = USE[B] U (OUT[B]-DEF[B])."""
    IN: Dict[int, Set[str]] = {i: set() for i in range(1, m + 1)}
    OUT: Dict[int, Set[str]] = {i: set() for i in range(1, m + 1)}

    changed = True
    it = 0
    while changed:
        changed = False
        it += 1
        # backward problems often iterate in reverse order; not required, but helps
        for b in range(m, 0, -1):
            old_in = set(IN[b])
            old_out = set(OUT[b])

            # OUT[b] = union of IN of successors
            new_out: Set[str] = set()
            for s in succ.get(b, []):
                new_out |= IN[s]
            OUT[b] = new_out

            # IN[b] = USE[b] U (OUT[b] - DEF[b])
            IN[b] = use[b] | (OUT[b] - defs[b])

            if IN[b] != old_in or OUT[b] != old_out:
                changed = True

        if it > 1000:  # safety
            break

    return IN, OUT


def solve_reaching_definitions(
    blocks: List[List[str]],
    succ: Dict[int, List[int]],
) -> Tuple[
    Dict[int, Set[str]], Dict[int, Set[str]], Dict[int, Set[str]], Dict[int, Set[str]],
    Dict[str, Set[str]]
]:
    """
    Forward reaching definitions at BLOCK level.

    We label each assignment definition as "x@B.k" (block B, statement index k inside that block).
    GEN[B] = the last definition in block for each variable
    KILL[B] = all other definitions of those variables (not the one in GEN[B])

    IN[B] = union of OUT[pred]
    OUT[B] = GEN[B] U (IN[B] - KILL[B])
    """
    m = len(blocks)
    pred = build_predecessors(succ, m)

    # Collect all definitions
    all_defs_by_var: Dict[str, Set[str]] = {}

    # defs_in_block[b] = list of def labels in order
    defs_in_block: Dict[int, List[Tuple[str, str]]] = {i: [] for i in range(1, m + 1)}

    for bi in range(1, m + 1):
        stmts = blocks[bi - 1]
        for si, line in enumerate(stmts, start=1):
            line2 = line.strip().rstrip(";").strip()
            m2 = ASSIGN_RE.match(line2)
            if not m2:
                continue
            lhs = m2.group(1)
            dlabel = f"{lhs}@B{bi}.{si}"
            defs_in_block[bi].append((lhs, dlabel))
            all_defs_by_var.setdefault(lhs, set()).add(dlabel)

    # Compute GEN/KILL
    GEN: Dict[int, Set[str]] = {i: set() for i in range(1, m + 1)}
    KILL: Dict[int, Set[str]] = {i: set() for i in range(1, m + 1)}

    for bi in range(1, m + 1):
        # last def per var in this block
        last: Dict[str, str] = {}
        for (var, dlabel) in defs_in_block[bi]:
            last[var] = dlabel

        GEN[bi] = set(last.values())

        # KILL: for each var defined in this block, kill all other defs of that var
        kill_set: Set[str] = set()
        for var, last_def in last.items():
            for d in all_defs_by_var.get(var, set()):
                if d != last_def:
                    kill_set.add(d)
        KILL[bi] = kill_set

    # Solve IN/OUT
    IN: Dict[int, Set[str]] = {i: set() for i in range(1, m + 1)}
    OUT: Dict[int, Set[str]] = {i: set() for i in range(1, m + 1)}

    changed = True
    it = 0
    while changed:
        changed = False
        it += 1
        for b in range(1, m + 1):
            old_in = set(IN[b])
            old_out = set(OUT[b])

            new_in: Set[str] = set()
            for p in pred[b]:
                new_in |= OUT[p]
            IN[b] = new_in

            OUT[b] = GEN[b] | (IN[b] - KILL[b])

            if IN[b] != old_in or OUT[b] != old_out:
                changed = True

        if it > 1000:
            break

    return GEN, KILL, IN, OUT, all_defs_by_var


def fmt_set(s: Set[str]) -> str:
    if not s:
        return "{}"
    return "{ " + ", ".join(sorted(s)) + " }"


def main() -> None:
    blocks, succ = read_program()
    m = len(blocks)

    # Compute USE/DEF for liveness
    use: Dict[int, Set[str]] = {}
    defs: Dict[int, Set[str]] = {}
    for bi in range(1, m + 1):
        u, d = compute_use_def_for_block(blocks[bi - 1])
        use[bi] = u
        defs[bi] = d

    print("\nUSE/DEF per block:")
    print("-" * 45)
    for bi in range(1, m + 1):
        print(f"B{bi}: USE = {fmt_set(use[bi])}    DEF = {fmt_set(defs[bi])}")

    print("\nChoose analysis:")
    print("  1) Live Variable Analysis (Backward)")
    print("  2) Reaching Definitions (Forward)")
    try:
        choice = input("Enter choice (1/2): ").strip()
    except EOFError:
        choice = "1"
    if choice not in {"1", "2"}:
        choice = "1"

    if choice == "1":
        IN, OUT = solve_liveness(use, defs, succ, m)
        print("\nLIVE VARIABLE ANALYSIS RESULT:")
        print("-" * 45)
        for bi in range(1, m + 1):
            print(f"B{bi}: IN  = {fmt_set(IN[bi])}")
            print(f"    OUT = {fmt_set(OUT[bi])}")

    else:
        GEN, KILL, IN, OUT, all_defs_by_var = solve_reaching_definitions(blocks, succ)
        print("\nREACHING DEFINITIONS RESULT:")
        print("-" * 45)
        for bi in range(1, m + 1):
            print(f"B{bi}: GEN  = {fmt_set(GEN[bi])}")
            print(f"    KILL = {fmt_set(KILL[bi])}")
            print(f"    IN   = {fmt_set(IN[bi])}")
            print(f"    OUT  = {fmt_set(OUT[bi])}")

        print("\nAll definition labels (by variable):")
        print("-" * 45)
        for var in sorted(all_defs_by_var.keys()):
            print(f"  {var}: {fmt_set(all_defs_by_var[var])}")


# Done by Akshay 353
if __name__ == "__main__":
    main()