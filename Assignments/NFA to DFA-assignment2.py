"""
Input format:
- First line   : comma-separated alphabet symbols (e.g.: a,b)
- Second line  : comma-separated NFA states        (e.g.: q0,q1,q2)
- Third line   : start state                       (e.g.: q0)
- Fourth line  : comma-separated accept states     (e.g.: q2)
- Fifth line   : number of transitions             (e.g.: 4)
- Next lines   : transitions in the form:
                 from_state symbol to_state
                 Use 'e' for epsilon (ε) transitions.
                 Example: q0 a q1
                          q0 e q2

"""

from collections import defaultdict, deque
from typing import Dict, Set, FrozenSet, List


def read_nfa():
    print("Enter NFA:")
    alphabet_line = input("Alphabet symbols (comma-separated, e.g. a,b): ").strip()
    states_line = input("NFA states (comma-separated, e.g. q0,q1,q2): ").strip()
    start_state = input("Start state (e.g. q0): ").strip()
    accept_line = input("Accept states (comma-separated, e.g. q2): ").strip()

    try:
        num_transitions = int(input("Number of transitions: ").strip())
    except ValueError:
        num_transitions = 0

    alphabet = [s.strip() for s in alphabet_line.split(",") if s.strip()]
    states = [s.strip() for s in states_line.split(",") if s.strip()]
    accept_states = {s.strip() for s in accept_line.split(",") if s.strip()}

    # transitions[(from_state, symbol)] -> set of to_states
    transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))

    print("Enter transitions as: from_state symbol to_state (use 'e' for epsilon)")
    for _ in range(num_transitions):
        line = input().strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 3:
            print("Invalid transition format, expected: from_state symbol to_state")
            continue
        from_state, symbol, to_state = parts
        transitions[from_state][symbol].add(to_state)

    return states, set(alphabet), start_state, accept_states, transitions


def epsilon_closure(states: Set[str], transitions: Dict[str, Dict[str, Set[str]]]) -> Set[str]:
    stack = list(states)
    closure = set(states)

    while stack:
        s = stack.pop()
        for t in transitions[s].get("e", set()):
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def move(states: Set[str], symbol: str, transitions: Dict[str, Dict[str, Set[str]]]) -> Set[str]:
    result = set()
    for s in states:
        result.update(transitions[s].get(symbol, set()))
    return result


def nfa_to_dfa(
    nfa_states: List[str],
    alphabet: Set[str],
    start_state: str,
    accept_states: Set[str],
    transitions: Dict[str, Dict[str, Set[str]]],
):
    sigma = {a for a in alphabet if a != "e"}

    start_closure = frozenset(epsilon_closure({start_state}, transitions))

    dfa_states: List[FrozenSet[str]] = []
    dfa_transitions: Dict[FrozenSet[str], Dict[str, FrozenSet[str]]] = {}
    dfa_start = start_closure
    dfa_accept_states: Set[FrozenSet[str]] = set()

    queue: deque[FrozenSet[str]] = deque()
    queue.append(start_closure)
    dfa_states.append(start_closure)

    DEAD = frozenset()

    while queue:
        current = queue.popleft()
        dfa_transitions.setdefault(current, {})

        if any(s in accept_states for s in current):
            dfa_accept_states.add(current)

        for symbol in sigma:
            next_nfa_states = move(set(current), symbol, transitions)

            if not next_nfa_states:
                dfa_transitions[current][symbol] = DEAD
                continue

            next_closure = frozenset(epsilon_closure(next_nfa_states, transitions))

            if next_closure not in dfa_states:
                dfa_states.append(next_closure)
                queue.append(next_closure)

            dfa_transitions[current][symbol] = next_closure

    dfa_states.append(DEAD)
    dfa_transitions[DEAD] = {symbol: DEAD for symbol in sigma}

    return sigma, dfa_start, dfa_states, dfa_accept_states, dfa_transitions


def format_state(state_set: FrozenSet[str]) -> str:
    if not state_set:
        return "∅"
    return "{" + ",".join(sorted(state_set)) + "}"


def print_dfa(
    alphabet: Set[str],
    dfa_start: FrozenSet[str],
    dfa_states: List[FrozenSet[str]],
    dfa_accept_states: Set[FrozenSet[str]],
    dfa_transitions: Dict[FrozenSet[str], Dict[str, FrozenSet[str]]],
):
    print("\n--- DFA ---")
    print("Alphabet:", ", ".join(sorted(alphabet)))
    print("States:")
    for s in dfa_states:
        marker = ""
        if s == dfa_start:
            marker += " (start)"
        if s in dfa_accept_states:
            marker += " (accept)"
        print("  ", format_state(s), marker)

    print("\nTransitions (δ):")
    for state in dfa_states:
        for symbol in sorted(alphabet):
            target = dfa_transitions.get(state, {}).get(symbol)
            if target is not None:
                print(f"  δ({format_state(state)}, {symbol}) -> {format_state(target)}")

#Done by Akshay 353
def main():
    states, alphabet, start_state, accept_states, transitions = read_nfa()

    sigma, dfa_start, dfa_states, dfa_accept_states, dfa_transitions = nfa_to_dfa(
        states, alphabet, start_state, accept_states, transitions
    )

    print_dfa(sigma, dfa_start, dfa_states, dfa_accept_states, dfa_transitions)

if __name__ == "__main__":
    main()

