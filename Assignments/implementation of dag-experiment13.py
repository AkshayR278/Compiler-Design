"""
Experiment 13: Implementation of DAG for a Basic Block (Local Optimization)

Input format (simple):
- Enter number of statements (n)
- Then n lines of three-address code, like:
    t1 := a + b
    t2 := a + b
    x  := t1 * c
    y  := x
Supported forms:
  1) x := y op z      (op in + - * /)
  2) x := y           (copy/assignment)
Also accepts '=' instead of ':=' and optional ';'

Output:
- DAG node table
- Optimized three-address code regenerated from the DAG
"""

from typing import Dict, List, Optional, Set, Tuple
import re

COMMUTATIVE = {"+", "*"}
OPS = {"+", "-", "*", "/"}

# regex: x := y op z
RE_BIN = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*(?::=|=)\s*([A-Za-z_]\w*|\d+)\s*([+\-*/])\s*([A-Za-z_]\w*|\d+)\s*$"
)

# regex: x := y
RE_COPY = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*(?::=|=)\s*([A-Za-z_]\w*|\d+)\s*$"
)

RE_TEMP = re.compile(r"^t\d+$", re.IGNORECASE)


def is_temp(name: str) -> bool:
    return RE_TEMP.match(name) is not None


class Node:
    def __init__(self, nid: int, op: Optional[str], value: Optional[str], left: Optional[int], right: Optional[int]):
        self.id = nid
        self.op = op          # None for leaf
        self.value = value    # operand for leaf
        self.left = left
        self.right = right
        self.labels: Set[str] = set()          # variables attached to this node
        self.label_time: Dict[str, int] = {}   # label -> statement index (for choosing a rep name)
        self.rep: Optional[str] = None         # chosen representative name for codegen


def parse_stmt(line: str) -> Tuple[str, ...]:
    """
    Returns one of:
      ("bin", lhs, a1, op, a2)
      ("copy", lhs, src)
      ("err", message)
    """
    s = line.strip().rstrip(";").strip()
    if not s:
        return ("err", "empty")

    m = RE_BIN.match(s)
    if m:
        lhs, a1, op, a2 = m.group(1), m.group(2), m.group(3), m.group(4)
        if op not in OPS:
            return ("err", f"unsupported operator {op}")
        return ("bin", lhs, a1, op, a2)

    m = RE_COPY.match(s)
    if m:
        lhs, src = m.group(1), m.group(2)
        return ("copy", lhs, src)

    return ("err", f"cannot parse: {line}")


def read_basic_block() -> List[str]:
    print("Enter Basic Block:")
    try:
        n = int(input("Number of statements: ").strip())
    except (ValueError, EOFError):
        n = 0

    stmts: List[str] = []
    for i in range(n):
        try:
            line = input(f"S{i+1}: ").strip()
        except EOFError:
            line = ""
        if line:
            stmts.append(line)

    if not stmts:
        print("\nNo statements entered, using default basic block:")
        stmts = [
            "t1 := a + b",
            "t2 := a + b",
            "t3 := t1 * c",
            "x  := t2 * c",
            "y  := x",
        ]
        for s in stmts:
            print("  ", s)

    return stmts


def build_dag(stmts: List[str]) -> Tuple[List[Node], Dict[str, int], List[str]]:
    """
    Build DAG for the basic block.
    Returns:
      nodes list
      var_to_node (current node for each variable)
      lhs_order (LHS variables in statement order)
    """
    nodes: List[Node] = []

    # operand -> leaf node id
    leaf_map: Dict[str, int] = {}

    # (op, left_id, right_id) -> node id
    expr_map: Dict[Tuple[str, int, int], int] = {}

    # current mapping of variable -> node id
    var_to_node: Dict[str, int] = {}

    lhs_order: List[str] = []

    def new_node(op: Optional[str], value: Optional[str], left: Optional[int], right: Optional[int]) -> int:
        nid = len(nodes)
        nodes.append(Node(nid, op, value, left, right))
        return nid

    def get_leaf(operand: str) -> int:
        if operand in leaf_map:
            return leaf_map[operand]
        nid = new_node(None, operand, None, None)
        leaf_map[operand] = nid
        return nid

    def attach_label(nid: int, var: str, time_idx: int) -> None:
        # If var was attached elsewhere before, remove it (redefinition handling)
        if var in var_to_node:
            old = var_to_node[var]
            if var in nodes[old].labels:
                nodes[old].labels.remove(var)
                nodes[old].label_time.pop(var, None)

        nodes[nid].labels.add(var)
        nodes[nid].label_time[var] = time_idx
        var_to_node[var] = nid

    for i, line in enumerate(stmts):
        parsed = parse_stmt(line)
        if parsed[0] == "err":
            # ignore empty lines; show other errors as comments
            if parsed[1] != "empty":
                print(f"  Warning: {parsed[1]}")
            continue

        kind = parsed[0]
        if kind == "copy":
            _, lhs, src = parsed
            lhs_order.append(lhs)

            # Source may be variable or constant; if variable never defined, make leaf (initial value)
            src_nid = var_to_node.get(src, get_leaf(src))
            attach_label(src_nid, lhs, i)

        elif kind == "bin":
            _, lhs, a1, op, a2 = parsed
            lhs_order.append(lhs)

            left_id = var_to_node.get(a1, get_leaf(a1))
            right_id = var_to_node.get(a2, get_leaf(a2))

            # For commutative ops, normalize order so a+b and b+a map to same node
            l_id, r_id = left_id, right_id
            if op in COMMUTATIVE and l_id > r_id:
                l_id, r_id = r_id, l_id

            sig = (op, l_id, r_id)
            if sig in expr_map:
                expr_id = expr_map[sig]
            else:
                expr_id = new_node(op, None, l_id, r_id)
                expr_map[sig] = expr_id

            attach_label(expr_id, lhs, i)

    return nodes, var_to_node, lhs_order


def print_dag(nodes: List[Node]) -> None:
    print("\nDAG Node Table")
    print("-" * 80)
    print(f"{'ID':<5}{'Type':<10}{'Op/Val':<10}{'Left':<8}{'Right':<8}{'Labels'}")
    print("-" * 80)

    for n in nodes:
        if n.op is None:
            typ = "LEAF"
            opv = n.value if n.value is not None else ""
            left = "-"
            right = "-"
        else:
            typ = "OP"
            opv = n.op
            left = str(n.left)
            right = str(n.right)

        labels = ", ".join(sorted(n.labels)) if n.labels else ""
        print(f"{n.id:<5}{typ:<10}{opv:<10}{left:<8}{right:<8}{labels}")


def regenerate_code(nodes: List[Node], var_to_node: Dict[str, int], lhs_order: List[str]) -> List[str]:
    """
    Regenerate optimized 3-address code from DAG.
    We generate code only for the final node of each LHS variable (after all redefinitions).
    """
    # Keep only the last occurrence of each LHS variable, preserving order
    last_pos: Dict[str, int] = {}
    for idx, v in enumerate(lhs_order):
        last_pos[v] = idx
    final_vars = [v for idx, v in enumerate(lhs_order) if last_pos[v] == idx]

    temp_count = 1
    code: List[str] = []
    generated: Set[int] = set()

    def choose_rep(n: Node) -> str:
        nonlocal temp_count
        if n.rep:
            return n.rep

        if n.labels:
            # Prefer a non-temp label if possible; otherwise choose the most recent label
            candidates = list(n.labels)
            candidates.sort(key=lambda v: (is_temp(v), -n.label_time.get(v, -1), v))
            n.rep = candidates[0]
        else:
            n.rep = f"tmp{temp_count}"
            temp_count += 1
        return n.rep

    def gen(nid: int) -> str:
        n = nodes[nid]
        if n.op is None:
            # leaf: return operand directly (variable name or constant)
            return n.value if n.value is not None else ""

        rep = choose_rep(n)
        if nid in generated:
            return rep

        left_name = gen(n.left)   # type: ignore[arg-type]
        right_name = gen(n.right) # type: ignore[arg-type]

        code.append(f"{rep} := {left_name} {n.op} {right_name}")
        generated.add(nid)
        return rep

    # Ensure each final variable gets assigned its final value
    for v in final_vars:
        nid = var_to_node.get(v)
        if nid is None:
            continue

        n = nodes[nid]
        if n.op is None:
            src = n.value if n.value is not None else ""
            # If v is itself, skip (like a := a)
            if src != v:
                code.append(f"{v} := {src}")
        else:
            rep = gen(nid)
            if rep != v:
                code.append(f"{v} := {rep}")

    return code


def main() -> None:
    stmts = read_basic_block()

    print("\nInput Basic Block:")
    print("-" * 30)
    for s in stmts:
        print(" ", s)

    nodes, var_to_node, lhs_order = build_dag(stmts)
    print_dag(nodes)

    opt_code = regenerate_code(nodes, var_to_node, lhs_order)

    print("\nOptimized Three Address Code (from DAG):")
    print("-" * 50)
    if not opt_code:
        print("  (no code generated)")
    else:
        for line in opt_code:
            print(" ", line)


# Done by Akshay 353
if __name__ == "__main__":
    main()