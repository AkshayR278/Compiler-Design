"""
Experiment 11: Intermediate Code Generation
           — Quadruple, Triple & Indirect Triple

Input:
- An infix expression using operands (a-z, A-Z, 0-9)
  and operators: + - * / ^
  e.g.:  a + b * c
         (a + b) * (c - d)
         a ^ b + c * d - e

Output:
- Postfix (shown for reference)
- Quadruple table
- Triple table
- Indirect Triple table
"""

from typing import List, Tuple

PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
RIGHT_ASSOC = {'^'}


def is_operand(ch: str) -> bool:
    return ch.isalnum()


def is_operator(ch: str) -> bool:
    return ch in PRECEDENCE


def tokenize(expr: str) -> List[str]:
    tokens: List[str] = []
    i = 0
    expr = expr.replace(" ", "")
    while i < len(expr):
        ch = expr[i]
        if ch.isalnum():
            j = i
            while j < len(expr) and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif ch in PRECEDENCE or ch in ('(', ')'):
            tokens.append(ch)
            i += 1
        else:
            print(f"  Warning: Unknown character '{ch}' skipped.")
            i += 1
    return tokens


def infix_to_postfix(tokens: List[str]) -> List[str]:
    output: List[str] = []
    stack:  List[str] = []
    for tok in tokens:
        if is_operand(tok):
            output.append(tok)
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()
        elif is_operator(tok):
            while (
                stack
                and stack[-1] != '('
                and is_operator(stack[-1])
                and (
                    (tok not in RIGHT_ASSOC and PRECEDENCE[stack[-1]] >= PRECEDENCE[tok])
                    or
                    (tok in RIGHT_ASSOC and PRECEDENCE[stack[-1]] >  PRECEDENCE[tok])
                )
            ):
                output.append(stack.pop())
            stack.append(tok)
    while stack:
        top = stack.pop()
        if top not in ('(', ')'):
            output.append(top)
    return output

TACRecord = Tuple[str, str, str, str]


def generate_tac_records(postfix: List[str]) -> List[TACRecord]:
    """
    Evaluate postfix using a stack.
    Returns list of (op, arg1, arg2, result) tuples.
    """
    stack:   List[str]       = []
    records: List[TACRecord] = []
    temp_count = 1

    for tok in postfix:
        if is_operand(tok):
            stack.append(tok)
        elif is_operator(tok):
            if len(stack) < 2:
                print(f"  Error: Not enough operands for operator '{tok}'")
                return records
            b = stack.pop()
            a = stack.pop()
            result = f"t{temp_count}"
            temp_count += 1
            records.append((tok, a, b, result))
            stack.append(result)

    return records



def print_quadruple(records: List[TACRecord]) -> None:
    print("\nQuadruple Table:")
    print("─" * 50)

    # Column headers
    idx_w  = 7
    op_w   = 8
    arg_w  = 10
    res_w  = 10

    header = (
        f"  {'Index':<{idx_w}}"
        f"{'Op':<{op_w}}"
        f"{'Arg1':<{arg_w}}"
        f"{'Arg2':<{arg_w}}"
        f"{'Result':<{res_w}}"
    )
    print(header)
    print("  " + "-" * (idx_w + op_w + arg_w + arg_w + res_w))

    for i, (op, a, b, res) in enumerate(records):
        print(
            f"  {i:<{idx_w}}"
            f"{op:<{op_w}}"
            f"{a:<{arg_w}}"
            f"{b:<{arg_w}}"
            f"{res:<{res_w}}"
        )



def print_triple(records: List[TACRecord]) -> None:
    print("\nTriple Table:")
    print("─" * 40)

    idx_w = 7
    op_w  = 8
    arg_w = 12

    header = (
        f"  {'Index':<{idx_w}}"
        f"{'Op':<{op_w}}"
        f"{'Arg1':<{arg_w}}"
        f"{'Arg2':<{arg_w}}"
    )
    print(header)
    print("  " + "-" * (idx_w + op_w + arg_w + arg_w))

    # Build a map: temp name -> triple index
    temp_to_idx = {}
    for i, (_, _, _, res) in enumerate(records):
        temp_to_idx[res] = i

    for i, (op, a, b, _) in enumerate(records):
        # If arg is a temp, show it as (index)
        a_str = f"({temp_to_idx[a]})" if a in temp_to_idx else a
        b_str = f"({temp_to_idx[b]})" if b in temp_to_idx else b
        print(
            f"  {i:<{idx_w}}"
            f"{op:<{op_w}}"
            f"{a_str:<{arg_w}}"
            f"{b_str:<{arg_w}}"
        )



def print_indirect_triple(records: List[TACRecord]) -> None:
    print("\nIndirect Triple Table:")
    print("─" * 60)

    # Build temp -> index map
    temp_to_idx = {}
    for i, (_, _, _, res) in enumerate(records):
        temp_to_idx[res] = i

    # Triple table (same as triple, shown on the right)
    idx_w = 7
    op_w  = 8
    arg_w = 12
    ptr_w = 12

    # Print Pointer table alongside Triple table side by side
    print(
        f"  {'Pointer Table':<{ptr_w + idx_w}}"
        f"   "
        f"{'Triple Table'}"
    )

    triple_header = (
        f"{'Index':<{idx_w}}"
        f"{'Op':<{op_w}}"
        f"{'Arg1':<{arg_w}}"
        f"{'Arg2':<{arg_w}}"
    )
    pointer_header = f"{'Ptr':<{ptr_w}}{'-> Index':<{idx_w}}"

    print(
        f"  {pointer_header:<{ptr_w + idx_w}}"
        f"   "
        f"{triple_header}"
    )
    print("  " + "-" * (ptr_w + idx_w + 3 + idx_w + op_w + arg_w + arg_w))

    for i, (op, a, b, _) in enumerate(records):
        a_str = f"({temp_to_idx[a]})" if a in temp_to_idx else a
        b_str = f"({temp_to_idx[b]})" if b in temp_to_idx else b

        ptr_part   = f"  {i:<{ptr_w}}{i:<{idx_w}}"
        triple_part = (
            f"{i:<{idx_w}}"
            f"{op:<{op_w}}"
            f"{a_str:<{arg_w}}"
            f"{b_str:<{arg_w}}"
        )
        print(f"{ptr_part}   {triple_part}")

    print("\n  Note: Pointer table references triple indices.")
    print("  Reordering is done by changing the pointer table,")
    print("  NOT the triple table itself.")



def main() -> None:
    print("Intermediate Code Generation")
    print("Quadruple  |  Triple  |  Indirect Triple")
    print("=" * 50)
    print("Supported operators : + - * / ^")
    print("e.g. inputs         : a + b * c")
    print("                      (a + b) * (c - d)")
    print("                      a ^ b + c * d - e\n")

    try:
        expr = input("Enter infix expression: ").strip()
    except EOFError:
        expr = ""

    if not expr:
        expr = "a + b * c - d"
        print(f"  Using default: {expr}")

    tokens  = tokenize(expr)
    postfix = infix_to_postfix(tokens)

    print("\n" + "─" * 50)
    print(f"  Infix  : {' '.join(tokens)}")
    print(f"  Postfix: {' '.join(postfix)}")

    records = generate_tac_records(postfix)

    if not records:
        print("  Could not generate TAC records.")
        return

    # Show TAC first for reference
    print("\nThree Address Code (TAC) — for reference:")
    print("─" * 50)
    for op, a, b, res in records:
        print(f"  {res} = {a} {op} {b}")

    # Now all three representations
    print_quadruple(records)
    print_triple(records)
    print_indirect_triple(records)


# Done by Akshay 353
if __name__ == "__main__":
    main()