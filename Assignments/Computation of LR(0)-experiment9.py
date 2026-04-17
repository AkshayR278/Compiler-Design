"""
Experiment 9: Computation of LR(0) Items

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
The program computes:
  1. All LR(0) items for each production
  2. Closure of the initial item set (I0)
  3. All canonical LR(0) item sets (states) via GOTO
"""

from typing import Dict, FrozenSet, List, Set, Tuple

# An LR(0) item is (LHS, RHS tuple, dot position)
Item = Tuple[str, Tuple[str, ...], int]

Production = Tuple[str, List[str]]


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

    # First pass: collect nonterminals
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


def augment_grammar(
    productions: List[Production], start_symbol: str
) -> Tuple[List[Production], str]:
    """Add S' -> S to the grammar."""
    new_start = start_symbol + "'"
    augmented = [(new_start, [start_symbol])] + productions
    return augmented, new_start


def closure(
    items: Set[Item],
    productions: List[Production],
    nonterminals: Set[str],
) -> Set[Item]:
    """
    Closure operation:
    If A -> α • B β is in the set, add B -> • γ for all B productions.
    """
    closed = set(items)
    changed = True
    while changed:
        changed = False
        new_items: Set[Item] = set()
        for (lhs, rhs, dot) in closed:
            if dot < len(rhs):
                B = rhs[dot]
                if B in nonterminals:
                    for (prod_lhs, prod_rhs) in productions:
                        if prod_lhs == B:
                            new_item: Item = (prod_lhs, tuple(prod_rhs), 0)
                            if new_item not in closed:
                                new_items.add(new_item)
                                changed = True
        closed.update(new_items)
    return closed


def goto(
    items: Set[Item],
    symbol: str,
    productions: List[Production],
    nonterminals: Set[str],
) -> Set[Item]:
    """
    GOTO(I, X):
    Move dot past symbol X for all items where dot is before X.
    Then take closure of the result.
    """
    moved: Set[Item] = set()
    for (lhs, rhs, dot) in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((lhs, rhs, dot + 1))
    if not moved:
        return set()
    return closure(moved, productions, nonterminals)


def canonical_collection(
    productions: List[Production],
    start_symbol: str,
    nonterminals: Set[str],
) -> Tuple[List[Set[Item]], Dict[Tuple[int, str], int]]:
    """
    Build the canonical collection of LR(0) item sets.
    Returns:
      - List of item sets (states)
      - GOTO table as dict: (state_index, symbol) -> state_index
    """
    # Initial item: S' -> • S
    start_item: Item = (start_symbol, tuple([p[1][0] for p in productions if p[0] == start_symbol][0:1]), 0)
    # More robust: find the augmented start production
    for lhs, rhs in productions:
        if lhs == start_symbol:
            start_item = (lhs, tuple(rhs), 0)
            break

    I0 = closure({start_item}, productions, nonterminals)
    states: List[Set[Item]] = [I0]
    goto_table: Dict[Tuple[int, str], int] = {}

    # Collect all grammar symbols
    all_symbols: Set[str] = set()
    for _, rhs in productions:
        for sym in rhs:
            all_symbols.add(sym)

    i = 0
    while i < len(states):
        for symbol in sorted(all_symbols):
            next_state = goto(states[i], symbol, productions, nonterminals)
            if not next_state:
                continue
            # Check if this state already exists
            found = -1
            for j, state in enumerate(states):
                if state == next_state:
                    found = j
                    break
            if found == -1:
                states.append(next_state)
                found = len(states) - 1
            goto_table[(i, symbol)] = found
        i += 1

    return states, goto_table


def item_to_str(item: Item) -> str:
    """Pretty print an LR(0) item with the dot shown as •"""
    lhs, rhs, dot = item
    rhs_list = list(rhs)
    rhs_list.insert(dot, "•")
    return f"  {lhs} -> {' '.join(rhs_list)}"


def print_all_lr0_items(productions: List[Production]) -> None:
    """Print all possible LR(0) items for every production."""
    print("\nAll LR(0) Items:")
    print("-" * 40)
    for lhs, rhs in productions:
        for dot in range(len(rhs) + 1):
            rhs_list = list(rhs)
            rhs_list.insert(dot, "•")
            print(f"  {lhs} -> {' '.join(rhs_list)}")


def print_canonical_collection(
    states: List[Set[Item]],
    goto_table: Dict[Tuple[int, str], int],
) -> None:
    print("\nCanonical Collection of LR(0) Item Sets:")
    print("=" * 45)
    for i, state in enumerate(states):
        print(f"\nI{i}:")
        for item in sorted(state):
            print(item_to_str(item))

    print("\nGOTO Table:")
    print("-" * 35)
    print(f"  {'State':<8} {'Symbol':<12} {'Next State'}")
    print(f"  {'-'*7:<8} {'-'*10:<12} {'-'*10}")
    for (state, symbol), next_state in sorted(goto_table.items()):
        print(f"  I{state:<7} {symbol:<12} I{next_state}")


def main() -> None:
    productions, start_symbol, nonterminals = read_grammar()

    # Augment grammar
    productions, start_symbol = augment_grammar(productions, start_symbol)
    nonterminals.add(start_symbol)

    print("\nAugmented Grammar:")
    print("-" * 30)
    for i, (lhs, rhs) in enumerate(productions):
        print(f"  {i}. {lhs} -> {' '.join(rhs)}")

    # Collect terminals
    terminals: Set[str] = set()
    for _, rhs in productions:
        for sym in rhs:
            if sym not in nonterminals:
                terminals.add(sym)

    print(f"\n  Non-terminals : {', '.join(sorted(nonterminals))}")
    print(f"  Terminals     : {', '.join(sorted(terminals))}")
    print(f"  Start symbol  : {start_symbol}")

    # Print all LR(0) items
    print_all_lr0_items(productions)

    # Build canonical collection
    states, goto_table = canonical_collection(productions, start_symbol, nonterminals)

    # Print results
    print_canonical_collection(states, goto_table)

    print(f"\nTotal number of LR(0) states: {len(states)}")


# Done by Akshay 353
if __name__ == "__main__":
    main()