"""
Experiment 8: Computation of Leading and Trailing Sets

Input format:
- Number of productions
- Productions like:
    E -> E + T
    E -> T
    T -> T * F
    T -> F
    F -> ( E )
    F -> id

Note: One production per line (no | alternatives).
Leading and Trailing sets are used in Operator Precedence Parsing.
"""

from typing import Dict, List, Set, Tuple

Production = Tuple[str, List[str]]  # (LHS, [RHS symbols])


def read_grammar() -> Tuple[List[Production], str, Set[str]]:
    print("Enter grammar:")
    try:
        n = int(input("Number of productions: ").strip())
    except (ValueError, EOFError):
        n = 0

    raw_lines: List[str] = []
    for i in range(n):
        line = input(f"Production {i + 1}: ").strip()
        if line:
            raw_lines.append(line)

    if not raw_lines:
        print("\nNo productions entered, using default grammar:")
        raw_lines = [
            "E -> E + T",
            "E -> T",
            "T -> T * F",
            "T -> F",
            "F -> ( E )",
            "F -> id",
        ]
        for l in raw_lines:
            print("  ", l)

    productions: List[Production] = []
    start_symbol = None
    nonterminals: Set[str] = set()

    # First pass: collect all LHS (nonterminals)
    for line in raw_lines:
        if "->" not in line:
            continue
        lhs, _ = line.split("->", 1)
        lhs = lhs.strip()
        nonterminals.add(lhs)
        if start_symbol is None:
            start_symbol = lhs

    # Second pass: build productions
    for line in raw_lines:
        if "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        rhs_symbols = rhs.strip().split()
        productions.append((lhs, rhs_symbols))

    if start_symbol is None:
        raise ValueError("No valid productions found.")

    return productions, start_symbol, nonterminals


def compute_leading(
    productions: List[Production],
    nonterminals: Set[str],
) -> Dict[str, Set[str]]:
    """
    LEADING(A):
    For each production A -> X1 X2 ... Xn:
      - If X1 is terminal: add X1 to LEADING(A)
      - If X1 is non-terminal B:
            add LEADING(B) to LEADING(A)  (propagate)
            if X2 exists and X2 is terminal: add X2 to LEADING(A)
    Repeat until no changes.
    """
    leading: Dict[str, Set[str]] = {A: set() for A in nonterminals}

    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            before = len(leading[lhs])

            if not rhs:
                continue

            x1 = rhs[0]

            if x1 not in nonterminals:
                # X1 is a terminal
                leading[lhs].add(x1)
            else:
                # X1 is a non-terminal B: propagate LEADING(B)
                leading[lhs].update(leading[x1])

                # If X2 exists and is a terminal, add it too
                if len(rhs) >= 2 and rhs[1] not in nonterminals:
                    leading[lhs].add(rhs[1])

            if len(leading[lhs]) != before:
                changed = True

    return leading


def compute_trailing(
    productions: List[Production],
    nonterminals: Set[str],
) -> Dict[str, Set[str]]:
    """
    TRAILING(A):
    For each production A -> X1 X2 ... Xn:
      - If Xn is terminal: add Xn to TRAILING(A)
      - If Xn is non-terminal B:
            add TRAILING(B) to TRAILING(A)  (propagate)
            if X(n-1) exists and is terminal: add X(n-1) to TRAILING(A)
    Repeat until no changes.
    """
    trailing: Dict[str, Set[str]] = {A: set() for A in nonterminals}

    changed = True
    while changed:
        changed = False
        for lhs, rhs in productions:
            before = len(trailing[lhs])

            if not rhs:
                continue

            xn = rhs[-1]

            if xn not in nonterminals:
                # Xn is a terminal
                trailing[lhs].add(xn)
            else:
                # Xn is a non-terminal B: propagate TRAILING(B)
                trailing[lhs].update(trailing[xn])

                # If X(n-1) exists and is a terminal, add it too
                if len(rhs) >= 2 and rhs[-2] not in nonterminals:
                    trailing[lhs].add(rhs[-2])

            if len(trailing[lhs]) != before:
                changed = True

    return trailing


def print_sets(title: str, sets: Dict[str, Set[str]]) -> None:
    label = title.split()[0]  # "LEADING" or "TRAILING"
    print(f"\n{title}")
    print("-" * len(title))
    for A in sorted(sets.keys()):
        symbols = ", ".join(sorted(sets[A])) if sets[A] else "(empty)"
        print(f"  {label}({A}) = {{ {symbols} }}")


def main() -> None:
    productions, start_symbol, nonterminals = read_grammar()

    print("\nGrammar (productions):")
    for i, (lhs, rhs) in enumerate(productions):
        print(f"  {i + 1}. {lhs} -> {' '.join(rhs)}")
    print(f"\n  Non-terminals : {', '.join(sorted(nonterminals))}")

    # Collect terminals
    terminals = set()
    for _, rhs in productions:
        for sym in rhs:
            if sym not in nonterminals:
                terminals.add(sym)
    print(f"  Terminals     : {', '.join(sorted(terminals))}")
    print(f"  Start symbol  : {start_symbol}")

    leading  = compute_leading(productions, nonterminals)
    trailing = compute_trailing(productions, nonterminals)

    print_sets("LEADING sets", leading)
    print_sets("TRAILING sets", trailing)


# Done by Akshay 353
if __name__ == "__main__":
    main()