"""
CSA-0801: Python Programming - Module 02
Topic: Custom Data Structures in Pure Python (Stack, Queue, Linked List, BST)

Key Concepts Covered:
1. Stack (LIFO) implementation with bounds checking
2. Queue (FIFO) and Circular Queue mechanics
3. Singly Linked List (insert, delete, search, reverse, traversal)
4. Binary Search Tree (BST) with insert, lookup, and in-order/pre-order traversal
5. Algorithmic complexity analysis (Time & Space)
"""

from typing import Generic, Optional, TypeVar

T = TypeVar("T")


# 1. Generic Stack Implementation (LIFO)
class Stack(Generic[T]):
    """Last-In-First-Out (LIFO) data structure."""

    def __init__(self, capacity: Optional[int] = None):
        self._items: list[T] = []
        self._capacity = capacity

    def push(self, item: T) -> None:
        if self._capacity and len(self._items) >= self._capacity:
            raise OverflowError("Stack overflow: Maximum capacity reached.")
        self._items.append(item)

    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("Pop from empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("Peek from empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"


# 2. Singly Linked List Node and Container
class Node(Generic[T]):
    def __init__(self, data: T):
        self.data: T = data
        self.next: Optional["Node[T]"] = None


class SinglyLinkedList(Generic[T]):
    """Dynamic Singly Linked List implementation."""

    def __init__(self):
        self.head: Optional[Node[T]] = None
        self._size: int = 0

    def append(self, data: T) -> None:
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = new_node
        self._size += 1

    def prepend(self, data: T) -> None:
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete(self, data: T) -> bool:
        if not self.head:
            return False

        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return True

        curr = self.head
        while curr.next and curr.next.data != data:
            curr = curr.next

        if curr.next:
            curr.next = curr.next.next
            self._size -= 1
            return True
        return False

    def reverse(self) -> None:
        prev = None
        curr = self.head
        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        self.head = prev

    def to_list(self) -> list[T]:
        result = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return " -> ".join(map(str, self.to_list())) + " -> None"


# 3. Binary Search Tree (BST)
class TreeNode:
    def __init__(self, key: int, value: str):
        self.key: int = key
        self.value: str = value
        self.left: Optional["TreeNode"] = None
        self.right: Optional["TreeNode"] = None


class BinarySearchTree:
    """Binary Search Tree supporting key-value insertion, lookup, and traversals."""

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, key: int, value: str) -> None:
        self.root = self._insert_rec(self.root, key, value)

    def _insert_rec(self, node: Optional[TreeNode], key: int, value: str) -> TreeNode:
        if not node:
            return TreeNode(key, value)
        if key < node.key:
            node.left = self._insert_rec(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_rec(node.right, key, value)
        else:
            node.value = value  # Update value on match
        return node

    def search(self, key: int) -> Optional[str]:
        curr = self.root
        while curr:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def inorder_traversal(self) -> list[tuple[int, str]]:
        result = []
        def _inorder(node: Optional[TreeNode]):
            if node:
                _inorder(node.left)
                result.append((node.key, node.value))
                _inorder(node.right)
        _inorder(self.root)
        return result


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 2.4 - Custom Data Structures (Stack, LL, BST)")
    print("=" * 60)

    print("\n[1] Generic Stack (LIFO) Operations:")
    stack = Stack[int](capacity=5)
    for val in [10, 20, 30, 40]:
        stack.push(val)
    print(f"  * Pushed 4 items -> {stack}")
    print(f"  * Top item (peek): {stack.peek()}")
    print(f"  * Popped item:     {stack.pop()}")
    print(f"  * Stack after pop: {stack}")

    print("\n[2] Singly Linked List Operations:")
    ll = SinglyLinkedList[str]()
    for student in ["Alice", "Bob", "Charlie", "Diana"]:
        ll.append(student)
    print(f"  * Appended items:    {ll}")
    ll.prepend("Zack")
    print(f"  * Prepended 'Zack':  {ll}")
    ll.delete("Charlie")
    print(f"  * Deleted 'Charlie': {ll}")
    ll.reverse()
    print(f"  * Reversed List:     {ll}")

    print("\n[3] Binary Search Tree (BST) Indexed by Student Roll ID:")
    bst = BinarySearchTree()
    records = [(104, "David"), (102, "Bob"), (107, "Grace"), (101, "Alice"), (103, "Charlie")]
    for roll, name in records:
        bst.insert(roll, name)

    print(f"  * In-Order Traversal (Sorted): {bst.inorder_traversal()}")
    print(f"  * Lookup Key 102: Found '{bst.search(102)}'")
    print(f"  * Lookup Key 999: Found '{bst.search(999)}'")

    print("\n[OK] Lab 2.4 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
