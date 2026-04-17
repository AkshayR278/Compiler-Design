"""
Experiment 10: Intermediate Code Generation — Prefix & Postfix

Input:
- An infix expression using operands (a-z, A-Z, 0-9)
  and operators: + - * / ^ ( )
  e.g.:  a + b * c
         (a + b) * (c - d)
         a ^ b + c * d - e

Output:
- Postfix expression
- Prefix  expression
- Three Address Code (TAC) generated from postfix
"""

from typing import List


# Operator precedence (higher = tighter binding)
PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
}

# ^ is right-associative, others are left
RIGHT_ASSOC = {'^'}


def is_operand(ch: str) -> bool:
    return ch.isalnum()


def is_operator(ch: str) -> bool:
    return ch in PRECEDENCE


def tokenize(expr: str) -> List[str]:
    """
    Split expression into tokens.
    Handles multi-character operands like 'id', 'a1', etc.
    """
    tokens: List[str] = []
    i = 0
    expr = expr.replace(" ", "")
    while i < len(expr):
        ch = expr[i]
        if ch.isalnum():
            # Collect full operand (e.g. 'id', 'a1')
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


# ─────────────────────────────────────────────
#  INFIX  →  POSTFIX  (Shunting-Yard Algorithm)
# ─────────────────────────────────────────────
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
                stack.pop()  # remove '('
            else:
                print("  Warning: Mismatched parentheses detected.")

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
        if top in ('(', ')'):
            print("  Warning: Mismatched parentheses detected.")
        else:
            output.append(top)

    return output


# ─────────────────────────────────────────────
#  INFIX  →  PREFIX
#  Strategy: reverse tokens (swap brackets),
#  run postfix algorithm, reverse result
# ─────────────────────────────────────────────
def infix_to_prefix(tokens: List[str]) -> List[str]:
    # Reverse tokens and swap ( <-> )
    reversed_tokens: List[str] = []
    for tok in reversed(tokens):
        if tok == '(':
            reversed_tokens.append(')')
        elif tok == ')':
            reversed_tokens.append('(')
        else:
            reversed_tokens.append(tok)

    # For prefix we treat ^ as left-associative in the reversed pass
    # so temporarily adjust: use a modified postfix on reversed
    output: List[str] = []
    stack:  List[str] = []

    for tok in reversed_tokens:
        if is_operand(tok):
            output.append(tok)

        elif tok == '(':
            stack.append(tok)

        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()
            else:
                print("  Warning: Mismatched parentheses.")

        elif is_operator(tok):
            while (
                stack
                and stack[-1] != '('
                and is_operator(stack[-1])
                and (
                    (tok not in RIGHT_ASSOC and PRECEDENCE[stack[-1]] >  PRECEDENCE[tok])
                    or
                    (tok in RIGHT_ASSOC and PRECEDENCE[stack[-1]] >= PRECEDENCE[tok])
                )
            ):
                output.append(stack.pop())
            stack.append(tok)

    while stack:
        top = stack.pop()
        if top not in ('(', ')'):
            output.append(top)

    # Reverse to get prefix
    return list(reversed(output))


# ─────────────────────────────────────────────
#  POSTFIX  →  Three Address Code (TAC)
# ─────────────────────────────────────────────
def generate_tac(postfix: List[str]) -> List[str]:
    """
    Evaluate postfix using a stack.
    Each time an operator is encountered, pop two operands,
    create a temporary variable, emit a TAC instruction.
    """
    stack:  List[str] = []
    tac:    List[str] = []
    temp_count = 1

    for tok in postfix:
        if is_operand(tok):
            stack.append(tok)

        elif is_operator(tok):
            if len(stack) < 2:
                print("  Error: Not enough operands for operator", tok)
                return tac
            b = stack.pop()
            a = stack.pop()
            temp = f"t{temp_count}"
            temp_count += 1
            tac.append(f"  {temp} = {a} {tok} {b}")
            stack.append(temp)

    return tac


# ─────────────────────────────────────────────
#  PRINT helpers
# ─────────────────────────────────────────────
def print_steps(label: str, tokens: List[str]) -> None:
    print(f"  {label:<12}: {' '.join(tokens)}")


def main() -> None:
    print("Intermediate Code Generation — Prefix & Postfix")
    print("=" * 50)
    print("Supported operators : + - * / ^")
    print("Operands            : letters and digits (e.g. a, b, id, x1)")
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

    tokens = tokenize(expr)

    print("\n" + "─" * 50)
    print_steps("Infix", tokens)

    postfix = infix_to_postfix(tokens)
    prefix  = infix_to_prefix(tokens)

    print_steps("Postfix", postfix)
    print_steps("Prefix",  prefix)

    tac = generate_tac(postfix)
    print("\nThree Address Code (TAC):")
    print("─" * 50)
    if tac:
        for line in tac:
            print(line)
    else:
        print("  (could not generate TAC)")

    print("\nSummary:")
    print("─" * 50)
    print(f"  Infix  expression : {' '.join(tokens)}")
    print(f"  Postfix expression: {' '.join(postfix)}")
    print(f"  Prefix  expression: {' '.join(prefix)}")


# Done by Akshay 353
if __name__ == "__main__":
    main()