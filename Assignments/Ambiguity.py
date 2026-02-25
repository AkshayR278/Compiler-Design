from typing import Dict, List

Grammar = Dict[str, List[str]]

def print_grammar(title: str, grammar: Grammar) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for head, bodies in grammar.items():
        rhs = " | ".join(bodies)
        print(f"{head} -> {rhs}")

def eliminate_immediate_left_recursion(nonterminal: str, productions: List[str]) -> Grammar:
    """
    Eliminate immediate left recursion for a single nonterminal.

    A -> A α1 | A α2 | ... | β1 | β2
    becomes
    A  -> β1 A' | β2 A'
    A' -> α1 A' | α2 A' | ε
    """
    alphas: List[str] = []  # suffixes in left-recursive rules
    betas: List[str] = []   # non-left-recursive rules

    for prod in productions:
        tokens = prod.split()
        if tokens and tokens[0] == nonterminal:
            # Left-recursive: A -> A α  => store α
            suffix = " ".join(tokens[1:]) if len(tokens) > 1 else "ε"
            alphas.append(suffix)
        else:
            betas.append(prod)

    # No left recursion
    if not alphas:
        return {nonterminal: productions}

    new_nt = nonterminal + "'"

    new_A: List[str] = []
    for beta in betas:
        if beta == "ε":
            new_A.append(new_nt)
        else:
            new_A.append(f"{beta} {new_nt}")

    new_A_prime: List[str] = []
    for alpha in alphas:
        if alpha == "ε":
            new_A_prime.append(new_nt)
        else:
            new_A_prime.append(f"{alpha} {new_nt}")
    new_A_prime.append("ε")

    return {nonterminal: new_A, new_nt: new_A_prime}


def left_factor_nonterminal(nonterminal: str, productions: List[str]) -> Grammar:
    """
    One-step left factoring for a single nonterminal.
    Finds longest common prefixes and introduces a new nonterminal.
    """
    # Group productions by first symbol
    groups: Dict[str, List[List[str]]] = {}
    for prod in productions:
        tokens = prod.split()
        if not tokens:
            continue
        first = tokens[0]
        groups.setdefault(first, []).append(tokens)

    result: Grammar = {}
    new_prods_for_A: List[str] = []
    prime_index = 0

    for first, group in groups.items():
        if len(group) == 1:
            new_prods_for_A.append(" ".join(group[0]))
            continue

        # Find longest common prefix of all productions in this group
        prefix = group[0]
        for tokens in group[1:]:
            i = 0
            while i < len(prefix) and i < len(tokens) and prefix[i] == tokens[i]:
                i += 1
            prefix = prefix[:i]

        if not prefix:
            for tokens in group:
                new_prods_for_A.append(" ".join(tokens))
            continue

        prime_index += 1
        prime_nt = nonterminal + ("'" if prime_index == 1 else f"'{prime_index}")

        # A -> prefix A'
        new_prods_for_A.append(" ".join(prefix + [prime_nt]))

        # A' -> suffixes | ε
        prime_prods: List[str] = []
        for tokens in group:
            suffix = tokens[len(prefix) :]
            if suffix:
                prime_prods.append(" ".join(suffix))
            else:
                prime_prods.append("ε")
        result[prime_nt] = prime_prods

    result[nonterminal] = new_prods_for_A
    return result


def experiment_ambiguity_elimination() -> None:
    """
    Classic example: arithmetic expressions with + and *.

    Ambiguous grammar:
      E -> E + E | E * E | id

    Unambiguous grammar with precedence (* higher than +) and left associativity:
      E  -> E + T | T
      T  -> T * F | F
      F  -> id
    """
    ambiguous: Grammar = {
        "E": ["E + E", "E * E", "id"],
    }

    unambiguous: Grammar = {
        "E": ["E + T", "T"],
        "T": ["T * F", "F"],
        "F": ["id"],
    }

    print("\n=== Elimination of Ambiguity ===")
    print_grammar("Ambiguous grammar (no precedence)", ambiguous)
    print_grammar("Unambiguous grammar (with precedence + associativity)", unambiguous)


def experiment_left_recursion_elimination() -> None:
    """
    Example of removing immediate left recursion.

    Left-recursive grammar:
      A -> A a | A b | c | d

    After elimination:
      A  -> c A' | d A'
      A' -> a A' | b A' | ε
    """
    left_recursive: Grammar = {
        "A": ["A a", "A b", "c", "d"],
    }

    # Use the actual algorithm to compute the transformed grammar
    transformed = eliminate_immediate_left_recursion("A", left_recursive["A"])

    print("\n=== Elimination of Left Recursion ===")
    print_grammar("Left-recursive grammar", left_recursive)
    print_grammar("Grammar after removing left recursion (computed)", transformed)


def experiment_left_factoring() -> None:
    """
    Example of left factoring.

    Before left factoring:
      S -> if E then S else S
         | if E then S
         | other

    After left factoring:
      S  -> if E then S S'
          | other
      S' -> else S | ε
    """
    before: Grammar = {
        "S": ["if E then S else S", "if E then S", "other"],
    }

    # Apply left factoring algorithm to the nonterminal S
    after = left_factor_nonterminal("S", before["S"])

    print("\n=== Left Factoring ===")
    print_grammar("Grammar before left factoring", before)
    print_grammar("Grammar after left factoring", after)


def main() -> None:
    print("Grammar Transformation Experiments")
    print("1) Elimination of ambiguity")
    print("2) Elimination of left recursion")
    print("3) Left factoring")
    print("\nRunning all three experiments...\n")

    experiment_ambiguity_elimination()
    experiment_left_recursion_elimination()
    experiment_left_factoring()


if __name__ == "__main__":
    main()

