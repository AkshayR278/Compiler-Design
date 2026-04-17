"""
Experiment 15: Storage Allocation Strategy (STACK) - Simple Implementation

Menu-driven stack simulation (LIFO):
1) PUSH  -> allocation (push)
2) POP   -> deallocation (pop)
3) DISPLAY
4) EXIT

This matches the common compiler lab "stack storage allocation" experiment style.
"""

from typing import List, Optional


class Stack:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[int] = []

    def is_full(self) -> bool:
        return len(self.items) >= self.capacity

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def push(self, x: int) -> bool:
        if self.is_full():
            return False
        self.items.append(x)
        return True

    def pop(self) -> Optional[int]:
        if self.is_empty():
            return None
        return self.items.pop()

    def display(self) -> None:
        if self.is_empty():
            print("Stack is Empty!")
            return
        print("Stack elements (TOP to BOTTOM):")
        for x in reversed(self.items):
            print(x)


# Done by Akshay 353
def main() -> None:
    print("Implementation of STACK Storage Allocation Strategy")
    print("=" * 55)

    try:
        cap_in = input("Enter stack size (default 5): ").strip()
    except EOFError:
        cap_in = ""

    if not cap_in:
        capacity = 5
    else:
        try:
            capacity = int(cap_in)
            if capacity <= 0:
                capacity = 5
        except ValueError:
            capacity = 5

    st = Stack(capacity)

    while True:
        print("\nMain Menu")
        print("1. Push")
        print("2. Pop")
        print("3. Display")
        print("4. Exit")

        try:
            choice = input("Enter your choice: ").strip()
        except EOFError:
            break

        if choice == "1":
            try:
                item_str = input("Enter item to push (integer): ").strip()
                item = int(item_str)
            except (ValueError, EOFError):
                print("Invalid input. Please enter an integer.")
                continue

            if st.push(item):
                print(f"Pushed: {item}")
            else:
                print("Stack is Full! (Overflow)")

        elif choice == "2":
            popped = st.pop()
            if popped is None:
                print("Empty stack! (Underflow)")
            else:
                print(f"Popped element is: {popped}")

        elif choice == "3":
            st.display()

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter 1/2/3/4.")


if __name__ == "__main__":
    main()