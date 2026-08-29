"""
Unit Tests for Module 02: Data Structures & Pattern Matching.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def load_module(rel_path: str, module_name: str):
    file_path = ROOT_DIR / rel_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod2_lists = load_module("02_data_structures/01_lists_and_tuples.py", "m2_lists")
mod2_dicts = load_module("02_data_structures/02_dictionaries_and_sets.py", "m2_dicts")
mod2_regex = load_module("02_data_structures/03_strings_and_regex.py", "m2_regex")
mod2_custom = load_module("02_data_structures/04_custom_data_structures.py", "m2_custom")


class TestDataStructures(unittest.TestCase):

    def test_matrix_transpose(self):
        mat = [[1, 2], [3, 4]]
        res = mod2_lists.matrix_operations_demo(mat)
        self.assertEqual(res["transpose"], [[1, 3], [2, 4]])
        self.assertEqual(res["flattened"], [1, 2, 3, 4])

    def test_word_frequency(self):
        text = "apple banana apple orange apple banana"
        freq = mod2_dicts.analyze_word_frequency(text)
        self.assertEqual(freq["apple"], 3)
        self.assertEqual(freq["banana"], 2)
        self.assertEqual(freq["orange"], 1)

    def test_set_algebra(self):
        s1 = {"A", "B", "C"}
        s2 = {"B", "C", "D"}
        algebra = mod2_dicts.compute_set_algebra(s1, s2)
        self.assertEqual(algebra["intersection (A & B)"], {"B", "C"})
        self.assertEqual(algebra["union (A | B)"], {"A", "B", "C", "D"})
        self.assertEqual(algebra["difference (A - B)"], {"A"})
        self.assertEqual(algebra["symmetric_difference (A ^ B)"], {"A", "D"})

    def test_regex_validations(self):
        self.assertTrue(mod2_regex.InputValidator.validate_email("nikhil@csa.edu"))
        self.assertFalse(mod2_regex.InputValidator.validate_email("bad-email@"))

        self.assertTrue(mod2_regex.InputValidator.validate_roll_no("CSA-2026-0801"))
        self.assertFalse(mod2_regex.InputValidator.validate_roll_no("123-abc"))

    def test_custom_stack(self):
        stack = mod2_custom.Stack(capacity=3)
        self.assertTrue(stack.is_empty())
        stack.push(10)
        stack.push(20)
        self.assertEqual(stack.peek(), 20)
        self.assertEqual(stack.pop(), 20)
        self.assertEqual(stack.size(), 1)
        stack.push(30)
        stack.push(40)
        with self.assertRaises(OverflowError):
            stack.push(50)

    def test_singly_linked_list(self):
        ll = mod2_custom.SinglyLinkedList()
        ll.append("A")
        ll.append("B")
        ll.append("C")
        self.assertEqual(ll.to_list(), ["A", "B", "C"])

        ll.prepend("Z")
        self.assertEqual(ll.to_list(), ["Z", "A", "B", "C"])

        deleted = ll.delete("B")
        self.assertTrue(deleted)
        self.assertEqual(ll.to_list(), ["Z", "A", "C"])

        ll.reverse()
        self.assertEqual(ll.to_list(), ["C", "A", "Z"])

    def test_binary_search_tree(self):
        bst = mod2_custom.BinarySearchTree()
        bst.insert(50, "Root")
        bst.insert(30, "Left")
        bst.insert(70, "Right")
        bst.insert(20, "LeftLeft")

        self.assertEqual(bst.search(30), "Left")
        self.assertEqual(bst.search(70), "Right")
        self.assertIsNone(bst.search(999))

        inorder = bst.inorder_traversal()
        keys = [k for k, v in inorder]
        self.assertEqual(keys, [20, 30, 50, 70])


if __name__ == "__main__":
    unittest.main()
