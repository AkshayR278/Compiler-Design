"""
Regular Expression to NFA Converter
Uses Thompson's construction algorithm.
Supports: single chars, concatenation (implicit), | (union), * (Kleene star), () grouping.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NFA:
    """NFA with epsilon transitions. States are integers."""
    start: int
    accept: int
    transitions: dict = field(default_factory=dict)  # (state, symbol) -> set of states; symbol None = epsilon

    def add_transition(self, from_state: int, to_state: int, symbol: Optional[str] = None):
        key = (from_state, symbol)
        if key not in self.transitions:
            self.transitions[key] = set()
        self.transitions[key].add(to_state)

    def get_states(self) -> set:
        states = {self.start, self.accept}
        for (s, _), targets in self.transitions.items():
            states.add(s)
            states.update(targets)
        return states


def re_to_postfix(re_str: str) -> str:
    """
    Convert infix RE to postfix (RPN), inserting explicit concatenation.
    Precedence: * (highest), concatenation, | (lowest).
    """
    # Insert concatenation operator '.' between: letter and letter, letter and (, ) and letter, ) and (, * and letter/(
    concat = []
    for i, c in enumerate(re_str):
        if c == " ":
            continue
        concat.append(c)
        if i + 1 >= len(re_str):
            break
        next_c = re_str[i + 1]
        if next_c == " ":
            continue
        curr_is_operand = c.isalnum() or c in ")_"  # _ for placeholder
        next_is_operand = next_c.isalnum() or next_c in "(_"
        if curr_is_operand and next_is_operand:
            concat.append(".")
        elif c == ")" and next_is_operand:
            concat.append(".")
        elif c == "*" and next_is_operand:
            concat.append(".")
    expr = "".join(concat)

    precedence = {"|": 1, ".": 2, "*": 3}
    output = []
    op_stack = []

    for c in expr:
        if c.isalnum() or c in "_":
            output.append(c)
        elif c == "(":
            op_stack.append(c)
        elif c == ")":
            while op_stack and op_stack[-1] != "(":
                output.append(op_stack.pop())
            if op_stack and op_stack[-1] == "(":
                op_stack.pop()
        elif c in precedence:
            while op_stack and op_stack[-1] != "(" and precedence.get(op_stack[-1], 0) >= precedence[c]:
                output.append(op_stack.pop())
            op_stack.append(c)

    while op_stack:
        output.append(op_stack.pop())

    return "".join(output)


def build_nfa_from_postfix(postfix: str) -> NFA:
    """Build NFA from postfix RE using Thompson's construction."""
    state_counter = [0]

    def next_state():
        s = state_counter[0]
        state_counter[0] += 1
        return s

    stack = []  # list of NFA fragments (start, accept)

    for c in postfix:
        if c.isalnum() or c == "_":
            # Single character: two states, one transition
            s, a = next_state(), next_state()
            nfa = NFA(start=s, accept=a)
            nfa.add_transition(s, a, c)
            stack.append(nfa)

        elif c == ".":
            # Concatenation: accept of second becomes start of first? No: N1 then N2 => connect N1.accept to N2.start
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1.add_transition(nfa1.accept, nfa2.start, None)  # epsilon
            nfa = NFA(start=nfa1.start, accept=nfa2.accept)
            nfa.transitions = {**nfa1.transitions, **nfa2.transitions}
            stack.append(nfa)

        elif c == "|":
            # Union: new start -> epsilon -> both starts; both accepts -> epsilon -> new accept
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            s, a = next_state(), next_state()
            nfa = NFA(start=s, accept=a)
            nfa.add_transition(s, nfa1.start, None)
            nfa.add_transition(s, nfa2.start, None)
            nfa.add_transition(nfa1.accept, a, None)
            nfa.add_transition(nfa2.accept, a, None)
            nfa.transitions = {**nfa1.transitions, **nfa2.transitions, **nfa.transitions}
            stack.append(nfa)

        elif c == "*":
            # Kleene star: new start and accept; epsilon: start->inner start, start->accept, inner accept->inner start, inner accept->accept
            nfa1 = stack.pop()
            s, a = next_state(), next_state()
            nfa = NFA(start=s, accept=a)
            nfa.add_transition(s, nfa1.start, None)
            nfa.add_transition(s, a, None)
            nfa.add_transition(nfa1.accept, nfa1.start, None)
            nfa.add_transition(nfa1.accept, a, None)
            nfa.transitions = {**nfa1.transitions, **nfa.transitions}
            stack.append(nfa)

    if len(stack) != 1:
        raise ValueError("Invalid regular expression")
    return stack[0]


def re_to_nfa(re_str: str) -> NFA:
    """Convert regular expression string to NFA."""
    postfix = re_to_postfix(re_str)
    return build_nfa_from_postfix(postfix)


def print_nfa(nfa: NFA):
    """Print NFA states and transitions in a readable form."""
    states = sorted(nfa.get_states())
    print(f"States: {states}")
    print(f"Start: {nfa.start}, Accept: {nfa.accept}")
    print("Transitions:")
    for (s, sym), targets in sorted(nfa.transitions.items()):
        sym_str = "ε" if sym is None else sym
        print(f"  δ({s}, {sym_str}) -> {sorted(targets)}")


def main():
    print("Regular Expression to NFA Converter")
    print("Supported: letters/digits, | (union), * (star), () grouping, concatenation (implicit)")
    print("Example: (a|b)*abb\n")

    try:
        re_input = input("Enter regular expression: ").strip()
    except EOFError:
        re_input = ""
    if not re_input:
        re_input = "(a|b)*abb"  # default example
        print(f"Using example: {re_input}")

    try:
        nfa = re_to_nfa(re_input)
        print("\n--- NFA ---")
        print_nfa(nfa)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
