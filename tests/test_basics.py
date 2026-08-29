"""
Unit Tests for Module 01: Basics, Control Flow, and Functions.
"""

import sys
import unittest
from pathlib import Path

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Dynamic import for numeric-prefixed directories
import importlib.util

def load_module(rel_path: str, module_name: str):
    file_path = ROOT_DIR / rel_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

mod1_types = load_module("01_basics_and_control_flow/01_variables_and_datatypes.py", "m1_types")
mod1_ops = load_module("01_basics_and_control_flow/02_operators_and_expressions.py", "m1_ops")
mod1_cond = load_module("01_basics_and_control_flow/03_conditional_statements.py", "m1_cond")
mod1_loops = load_module("01_basics_and_control_flow/04_loops_and_iterations.py", "m1_loops")
mod1_funcs = load_module("01_basics_and_control_flow/05_functions_and_recursion.py", "m1_funcs")


class TestBasicsAndControlFlow(unittest.TestCase):

    def test_type_conversion_pipeline(self):
        inputs = ["100", "3.14", "True", "False", "Sample String"]
        results = mod1_types.type_conversion_pipeline(inputs)
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0]["converted"], 100)
        self.assertEqual(results[0]["type"], "int")
        self.assertAlmostEqual(results[1]["converted"], 3.14)
        self.assertEqual(results[1]["type"], "float")
        self.assertTrue(results[2]["converted"])
        self.assertFalse(results[3]["converted"])
        self.assertEqual(results[4]["type"], "str")

    def test_arithmetic_suite(self):
        ops = mod1_ops.compute_arithmetic_suite(20, 5)
        self.assertEqual(ops["addition"], 25)
        self.assertEqual(ops["subtraction"], 15)
        self.assertEqual(ops["multiplication"], 100)
        self.assertEqual(ops["true_division"], 4.0)
        self.assertEqual(ops["floor_division"], 4)
        self.assertEqual(ops["modulus"], 0)

        with self.assertRaises(ZeroDivisionError):
            mod1_ops.compute_arithmetic_suite(10, 0)

    def test_letter_grade_determination(self):
        self.assertEqual(mod1_cond.determine_letter_grade(95)[0], "O")
        self.assertEqual(mod1_cond.determine_letter_grade(85)[0], "A+")
        self.assertEqual(mod1_cond.determine_letter_grade(75)[0], "A")
        self.assertEqual(mod1_cond.determine_letter_grade(65)[0], "B+")
        self.assertEqual(mod1_cond.determine_letter_grade(55)[0], "B")
        self.assertEqual(mod1_cond.determine_letter_grade(45)[0], "C")
        self.assertEqual(mod1_cond.determine_letter_grade(25)[0], "F")

        with self.assertRaises(ValueError):
            mod1_cond.determine_letter_grade(150)

    def test_leap_year(self):
        self.assertTrue(mod1_cond.leap_year_checker(2000))
        self.assertTrue(mod1_cond.leap_year_checker(2024))
        self.assertFalse(mod1_cond.leap_year_checker(1900))
        self.assertFalse(mod1_cond.leap_year_checker(2023))

    def test_sieve_of_eratosthenes(self):
        primes_20 = mod1_loops.generate_primes_sieve(20)
        self.assertEqual(primes_20, [2, 3, 5, 7, 11, 13, 17, 19])

    def test_fibonacci_and_hanoi(self):
        self.assertEqual(mod1_funcs.fibonacci_memoized(0), 0)
        self.assertEqual(mod1_funcs.fibonacci_memoized(1), 1)
        self.assertEqual(mod1_funcs.fibonacci_memoized(10), 55)

        hanoi_moves = mod1_funcs.tower_of_hanoi(3, "A", "C", "B")
        self.assertEqual(len(hanoi_moves), 7)  # 2^3 - 1 = 7

    def test_functional_analytics(self):
        scores = [40.0, 60.0, 80.0]
        res = mod1_funcs.functional_analytics(scores)
        self.assertEqual(res["original_count"], 3)
        self.assertEqual(res["passing_count"], 2)


if __name__ == "__main__":
    unittest.main()
