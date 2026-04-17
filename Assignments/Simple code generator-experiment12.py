"""
Experiment 12: Simple Code Generator
(Three Address Code -> Simple Assembly Code)

Input style (very common in compiler labs):
  A:=B+C
  D:=E/F
  QUIT

Output style:
  MOV B,R0
  ADD C,R0
  MOV R0,A
  MOV E,R1
  DIV F,R1
  MOV R1,D

Supports operators: +  -  *  /  |  &
Accepts: := or =
"""

from typing import List, Optional, Tuple

OPS = ['+', '-', '*', '/', '|', '&']

OP_TO_MNEMONIC = {
    '+': 'ADD',
    '-': 'SUB',
    '*': 'MUL',
    '/': 'DIV',
    '|': 'OR',
    '&': 'AND',
}


def parse_tac_line(line: str) -> Optional[Tuple[str, ...]]:
    """
    Returns:
      ("bin", dest, arg1, op, arg2)   for A:=B+C
      ("assign", dest, src)          for A:=B
    or None for QUIT/empty
    """
    s = line.strip()
    if not s:
        return None
    if s.upper() == "QUIT":
        return None

    # remove trailing semicolon if user types it
    s = s.rstrip(';').strip()

    if ":=" in s:
        lhs, rhs = s.split(":=", 1)
    elif "=" in s:
        lhs, rhs = s.split("=", 1)
    else:
        return ("error", "No assignment operator := or = found")

    lhs = lhs.strip()
    rhs = rhs.strip()

    if not lhs or not rhs:
        return ("error", "Invalid statement (missing lhs or rhs)")

    # Find a binary operator in RHS
    for op in OPS:
        idx = rhs.find(op)
        if idx != -1:
            a1 = rhs[:idx].strip()
            a2 = rhs[idx + 1:].strip()
            if a1 and a2:
                return ("bin", lhs, a1, op, a2)

    return ("assign", lhs, rhs)


def gen_assembly(parsed: Tuple[str, ...], regno: int) -> List[str]:
    kind = parsed[0]

    if kind == "bin":
        _, dest, a1, op, a2 = parsed
        reg = f"R{regno}"
        mnem = OP_TO_MNEMONIC.get(op, "OP")

        return [
            f"MOV {a1},{reg}",
            f"{mnem} {a2},{reg}",
            f"MOV {reg},{dest}",
        ]

    if kind == "assign":
        _, dest, src = parsed
        return [f"MOV {src},{dest}"]

    if kind == "error":
        return [f"; ERROR: {parsed[1]}"]

    return ["; ERROR: Unknown statement format"]


def main() -> None:
    print("CODE GENERATOR")
    print("ENTER THREE ADDRESS CODE (type QUIT to stop)\n")
    print("Examples:")
    print("  A:=B+C")
    print("  D:=E/F")
    print("  X:=Y")
    print("  QUIT\n")

    lines: List[str] = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        if line.upper() == "QUIT":
            break

        lines.append(line)

    if not lines:
        print("\nNo input given. Using default sample:\n  A:=B+C\n  D:=E/F\n")
        lines = ["A:=B+C", "D:=E/F"]

    print("\nASSEMBLY LANGUAGE CODE:\n")

    regno = 0
    for line in lines:
        parsed = parse_tac_line(line)
        if parsed is None:
            continue

        asm = gen_assembly(parsed, regno)
        for inst in asm:
            print(inst)

        if parsed[0] == "bin":
            regno += 1


# Done by Akshay 353
if __name__ == "__main__":
    main()