"""
Input format (same style as First-Follow):
- First, enter number of productions (n)
- Then n lines like:
    E  -> T E'
    E' -> + T E' | ε
    T  -> F T'
    T' -> * F T' | ε
    F  -> ( E ) | id

"""

from typing import Dict, List, Set, Tuple

Grammar = Dict[str, List[List[str]]] 

EPSILON_SYMBOLS = {"ε", "epsilon"}


def is_epsilon(symbol: str) -> bool:
    return symbol in EPSILON_SYMBOLS or symbol == "ε"


def read_grammar() -> Tuple[Grammar, str]:
    print("Enter grammar:")
    try:
        n = int(input("Number of productions: ").strip())
    except (ValueError, EOFError):
        n = 0

    productions_raw: List[str] = []

    for i in range(n):
        line = input(f"Production {i + 1}: ").strip()
        if line:
            productions_raw.append(line)

    # If no productions, use a standard expression grammar example
    if not productions_raw:
        print("\nNo productions entered so using default")
        default = [
            "E  -> T E'",
            "E' -> + T E' | ε",
            "T  -> F T'",
            "T' -> * F T' | ε",
            "F  -> ( E ) | id",
        ]
        productions_raw = default
        for line in default:
            print("  ", line)

    grammar: Grammar = {}
    start_symbol = None

    for line in productions_raw:
        if "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        if start_symbol is None:
            start_symbol = lhs

        right_side = rhs.strip()
        alternatives = [alt.strip() for alt in right_side.split("|")]
        for alt in alternatives:
            if not alt or is_epsilon(alt):
                prod = ["ε"]
            else:
                prod = alt.split()
            grammar.setdefault(lhs, []).append(prod)

    if start_symbol is None:
        raise ValueError("Not valid")

    return grammar, start_symbol


def compute_first_sets(grammar: Grammar) -> Dict[str, Set[str]]:
    nonterminals = set(grammar.keys())
    first: Dict[str, Set[str]] = {A: set() for A in nonterminals}

    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for prod in prods:
                add_epsilon = True
                for X in prod:
                    if is_epsilon(X):
                        if "ε" not in first[A]:
                            first[A].add("ε")
                            changed = True
                        add_epsilon = False
                        break

                    if X not in nonterminals:
                        if X not in first[A]:
                            first[A].add(X)
                            changed = True
                        add_epsilon = False
                        break

                    before = len(first[A])
                    first[A].update(sym for sym in first[X] if sym != "ε")
                    if len(first[A]) != before:
                        changed = True

                    if "ε" in first[X]:
                        add_epsilon = True
                    else:
                        add_epsilon = False
                        break

                if add_epsilon:
                    if "ε" not in first[A]:
                        first[A].add("ε")
                        changed = True

    return first


def first_of_sequence(seq: List[str], first_sets: Dict[str, Set[str]], nonterminals: Set[str]) -> Set[str]:
    result: Set[str] = set()
    add_epsilon = True

    if not seq:
        result.add("ε")
        return result

    for X in seq:
        if is_epsilon(X):
            result.add("ε")
            add_epsilon = False
            break

        if X not in nonterminals:
            result.add(X)
            add_epsilon = False
            break

        result.update(sym for sym in first_sets[X] if sym != "ε")
        if "ε" in first_sets[X]:
            add_epsilon = True
        else:
            add_epsilon = False
            break

    if add_epsilon:
        result.add("ε")

    return result


def compute_follow_sets(grammar: Grammar, start_symbol: str, first_sets: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    nonterminals = set(grammar.keys())
    follow: Dict[str, Set[str]] = {A: set() for A in nonterminals}
    follow[start_symbol].add("$")

    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for prod in prods:
                for i, B in enumerate(prod):
                    if B not in nonterminals:
                        continue

                    beta = prod[i + 1 :]
                    first_beta = first_of_sequence(beta, first_sets, nonterminals)

                    before = len(follow[B])
                    follow[B].update(sym for sym in first_beta if sym != "ε")
                    if len(follow[B]) != before:
                        changed = True

                    if not beta or "ε" in first_beta:
                        before = len(follow[B])
                        follow[B].update(follow[A])
                        if len(follow[B]) != before:
                            changed = True

    return follow


def build_parsing_table(
    grammar: Grammar,
    start_symbol: str,
    first_sets: Dict[str, Set[str]],
    follow_sets: Dict[str, Set[str]],
) -> Tuple[Dict[Tuple[str, str], List[str]], Set[str], bool]:
    nonterminals = set(grammar.keys())

    # Collect terminals
    terminals: Set[str] = set()
    for A, prods in grammar.items():
        for prod in prods:
            for X in prod:
                if X not in nonterminals and not is_epsilon(X):
                    terminals.add(X)
    terminals.add("$")

    table: Dict[Tuple[str, str], List[str]] = {}
    is_ll1 = True

    for A, prods in grammar.items():
        for prod in prods:
            first_alpha = first_of_sequence(prod, first_sets, nonterminals)
            for a in first_alpha:
                if a != "ε":
                    key = (A, a)
                    if key in table and table[key] != prod:
                        is_ll1 = False
                    table[key] = prod

            if "ε" in first_alpha:
                for b in follow_sets[A]:
                    key = (A, b)
                    if key in table and table[key] != prod:
                        is_ll1 = False
                    table[key] = ["ε"]

    return table, terminals, is_ll1


def print_sets(title: str, sets: Dict[str, Set[str]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for A in sorted(sets.keys()):
        symbols = ", ".join(sorted(sets[A]))
        print(f"{title.split()[0]}({A}) = {{ {symbols} }}")


def print_parsing_table(
    grammar: Grammar,
    terminals: Set[str],
    table: Dict[Tuple[str, str], List[str]],
    is_ll1: bool,
) -> None:
    nonterminals = sorted(grammar.keys())
    # Exclude $ from middle columns, print it last
    term_list = sorted(t for t in terminals if t != "$") + ["$"]

    print("\nPredictive Parsing Table (LL(1))")
    if not is_ll1:
        print("Warning: Grammar is NOT LL(1) (conflicts detected).")

    # Header
    header = ["NT/T"] + term_list
    col_width = max(len(h) for h in header) + 2
    print("".join(h.ljust(col_width) for h in header))
    print("-" * (col_width * len(header)))

    # Rows
    for A in nonterminals:
        row = [A.ljust(col_width)]
        for a in term_list:
            prod = table.get((A, a))
            if prod is None:
                cell = ""
            elif prod == ["ε"]:
                cell = f"{A} -> ε"
            else:
                rhs = " ".join(prod)
                cell = f"{A} -> {rhs}"
            row.append(cell.ljust(col_width))
        print("".join(row))

#Done by Akshay 353
def main() -> None:
    grammar, start_symbol = read_grammar()

    print("\nGrammar:")
    for A, prods in grammar.items():
        rhs = " | ".join(" ".join(prod) for prod in prods)
        print(f"  {A} -> {rhs}")

    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, start_symbol, first_sets)

    print_sets("FIRST sets", first_sets)
    print_sets("FOLLOW sets", follow_sets)

    table, terminals, is_ll1 = build_parsing_table(grammar, start_symbol, first_sets, follow_sets)
    print_parsing_table(grammar, terminals, table, is_ll1)


if __name__ == "__main__":
    main()

