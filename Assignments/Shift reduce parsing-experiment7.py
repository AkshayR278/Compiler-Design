"""
Experiment 7: Shift-Reduce Parsing

Input format:
- Number of productions
- Productions like:
    E -> E + E
    E -> E * E
    E -> ( E )
    E -> id
- Then the input string (space-separated tokens), e.g.: id + id * id

The parser will simulate the shift-reduce steps and show
the stack, input buffer, and action at each step.
"""

from typing import List, Tuple

Production = Tuple[str, List[str]]  # (LHS, [RHS symbols])


def read_grammar() -> Tuple[List[Production], str]:
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
            "E -> E + E",
            "E -> E * E",
            "E -> ( E )",
            "E -> id",
        ]
        for l in raw_lines:
            print("  ", l)

    productions: List[Production] = []
    start_symbol = None

    for line in raw_lines:
        if "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        if start_symbol is None:
            start_symbol = lhs
        # Each line is ONE production (no | splitting here for simplicity)
        rhs_symbols = rhs.strip().split()
        productions.append((lhs, rhs_symbols))

    if start_symbol is None:
        raise ValueError("No valid productions found.")

    return productions, start_symbol


def try_reduce(stack: List[str], productions: List[Production]) -> Tuple[bool, str, List[str]]:
    """
    Try to find a production whose RHS matches the top of the stack.
    Returns (reduced, lhs, matched_rhs) if a reduction is possible.
    Tries longest match first.
    """
    for lhs, rhs in productions:
        rlen = len(rhs)
        if stack[-rlen:] == rhs:
            return True, lhs, rhs
    return False, "", []


def shift_reduce_parse(tokens: List[str], productions: List[Production], start_symbol: str) -> bool:
    stack: List[str] = []
    inp = tokens + ["$"]
    idx = 0

    # Column widths for pretty printing
    col = 28
    print(f"\n{'Stack':<{col}} {'Input':<{col}} {'Action'}")
    print("-" * (col * 2 + 20))

    def show(action: str):
        stack_str = " ".join(stack) if stack else ""
        input_str = " ".join(inp[idx:])
        print(f"{'$' + stack_str:<{col}} {input_str:<{col}} {action}")

    show("START")

    while True:
        # Try to reduce
        reduced, lhs, matched_rhs = try_reduce(stack, productions)

        if reduced:
            rlen = len(matched_rhs)
            rhs_str = " ".join(matched_rhs)
            action = f"Reduce: {lhs} -> {rhs_str}"
            # Pop RHS, push LHS
            stack = stack[:-rlen]
            stack.append(lhs)
            show(action)

            # Accept condition
            if stack == [start_symbol] and inp[idx] == "$":
                print(f"\n{'$' + start_symbol:<{col}} {'$':<{col}} ACCEPT ✓")
                return True

        else:
            # Shift
            if inp[idx] == "$":
                # Nothing left to shift and can't reduce
                if stack == [start_symbol]:
                    print(f"\n{'$' + start_symbol:<{col}} {'$':<{col}} ACCEPT ✓")
                    return True
                else:
                    show("ERROR: Cannot shift or reduce")
                    return False

            token = inp[idx]
            stack.append(token)
            idx += 1
            show(f"Shift:  {token}")


def main() -> None:
    productions, start_symbol = read_grammar()

    print("\nGrammar (productions):")
    for i, (lhs, rhs) in enumerate(productions):
        print(f"  {i + 1}. {lhs} -> {' '.join(rhs)}")
    print(f"  Start symbol: {start_symbol}")

    print("\nEnter input string (space-separated tokens):")
    print("  e.g.: id + id * id")
    try:
        raw_input_str = input("Input: ").strip()
    except EOFError:
        raw_input_str = ""

    if not raw_input_str:
        raw_input_str = "id + id * id"
        print(f"  Using default: {raw_input_str}")

    tokens = raw_input_str.split()

    result = shift_reduce_parse(tokens, productions, start_symbol)

    if result:
        print(f'\n✓ String "{raw_input_str}" is ACCEPTED by the grammar.')
    else:
        print(f'\n✗ String "{raw_input_str}" is REJECTED by the grammar.')


# Done by Akshay 353
if __name__ == "__main__":
    main()