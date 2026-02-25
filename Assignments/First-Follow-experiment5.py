"""
Input format:
- enter number of productions (n)
- Then n lines like:
    E -> T E'
    E' -> + T E' | ε
    T -> F T'
    T' -> * F T' | ε
    F -> ( E ) | id

    if no production is entered then i have put this sample grammar to use
"""

from typing import Dict, List, Set, Tuple

Grammar = Dict[str, List[List[str]]] 

EPSILON_SYMBOLS = {"ε", "epsilon"}

def is_epsilon(symbol: str) -> bool:
    return symbol in EPSILON_SYMBOLS

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

    # If no production entered use this same as before
    if not productions_raw:
        print("\nproduction wasnt entered")
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
        raise ValueError("not valid")

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
    follow[start_symbol].add("$")#first rule

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


def print_sets(title: str, sets: Dict[str, Set[str]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for A in sorted(sets.keys()):
        symbols = ", ".join(sorted(sets[A]))
        print(f"{title.split()[0]}({A}) = {{ {symbols} }}")

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


if __name__ == "__main__":
    main()

