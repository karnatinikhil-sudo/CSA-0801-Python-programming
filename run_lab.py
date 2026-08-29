#!/usr/bin/env python3
"""
================================================================================
  CSA-0801: PYTHON PROGRAMMING - ACADEMIC & LAB COURSEWORK SUITE
  Interactive Lab Navigator, Test Runner, and Capstone System Launcher
================================================================================
"""

import argparse
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

MODULES = [
    {
        "unit": "01",
        "title": "Basics & Control Flow",
        "dir": "01_basics_and_control_flow",
        "labs": [
            ("01_variables_and_datatypes.py", "Variables, Primitive Types, and Memory Model"),
            ("02_operators_and_expressions.py", "Operators, Expressions, and Bitwise Logic"),
            ("03_conditional_statements.py", "Conditionals, Grading Logic, and Pattern Matching"),
            ("04_loops_and_iterations.py", "Loops, Sieve of Eratosthenes, and Pattern Rendering"),
            ("05_functions_and_recursion.py", "Functions, Closures, Decorators, and Recursion"),
        ]
    },
    {
        "unit": "02",
        "title": "Built-in & Custom Data Structures",
        "dir": "02_data_structures",
        "labs": [
            ("01_lists_and_tuples.py", "Lists, Tuples, Matrix Operations, and Unpacking"),
            ("02_dictionaries_and_sets.py", "Dicts, Hash Tables, and Set Algebra"),
            ("03_strings_and_regex.py", "String Processing, Regex Validation, and Log Parsing"),
            ("04_custom_data_structures.py", "Custom Stack, Singly Linked List, and BST in Python"),
        ]
    },
    {
        "unit": "03",
        "title": "Object-Oriented Programming & Design Patterns",
        "dir": "03_object_oriented_programming",
        "labs": [
            ("01_classes_and_objects.py", "Classes, Instance/Class State, and Static Methods"),
            ("02_inheritance_and_polymorphism.py", "Inheritance, ABC Contracts, Polymorphism, and MRO"),
            ("03_encapsulation_and_dunder.py", "Encapsulation, @property, and Operator Overloading"),
            ("04_design_patterns.py", "Design Patterns: Singleton, Factory, and Observer"),
        ]
    },
    {
        "unit": "04",
        "title": "File Handling & Exception Management",
        "dir": "04_file_handling_and_exceptions",
        "labs": [
            ("01_file_io_operations.py", "Context Managers, CSV Processing, and JSON I/O"),
            ("02_exception_handling.py", "Custom Exception Hierarchies and Safe Handlers"),
            ("03_serialization_and_pickling.py", "Binary Pickle vs JSON Serialization"),
        ]
    },
    {
        "unit": "05",
        "title": "Python Standard Library & Concurrency",
        "dir": "05_modules_and_standard_lib",
        "labs": [
            ("01_datetime_and_math.py", "Datetime Scheduling, Statistics, and Decimal Precision"),
            ("02_os_sys_pathlib.py", "Pathlib Navigation, System Info, and CLI Argparse"),
            ("03_concurrency.py", "ThreadPoolExecutor, Multiprocessing, and Asyncio"),
        ]
    },
    {
        "unit": "06",
        "title": "Relational Database Operations (SQLite3)",
        "dir": "06_database_operations",
        "labs": [
            ("demo_crud.py", "Database Schema, Transactions, CRUD, and SQL JOINs"),
        ]
    },
    {
        "unit": "07",
        "title": "Desktop GUI Applications (Tkinter / ttk)",
        "dir": "07_gui_applications",
        "labs": [
            ("student_grade_calculator.py", "Student Grade & Credit-weighted GPA Calculator GUI"),
            ("system_monitor_gui.py", "Real-Time System Resource & Hardware Monitor GUI"),
        ]
    },
    {
        "unit": "08",
        "title": "Capstone Project",
        "dir": "08_capstone_project",
        "labs": [
            ("main.py", "Student Academic & Wellness Management System (CLI & GUI)"),
        ]
    },
]


def print_banner():
    print("=" * 76)
    print("  CSA-0801: PYTHON PROGRAMMING - ACADEMIC COURSEWORK & LAB SUITE")
    print("  Saveetha / SRM / University Engineering Curriculum Edition")
    print("=" * 76)


def run_single_lab(script_path: Path):
    """Executes a lab script as a subprocess and streams its output."""
    print("\n" + "#" * 76)
    print(f"  EXECUTING: {script_path.relative_to(ROOT_DIR)}")
    print("#" * 76 + "\n")
    cmd = [sys.executable, str(script_path)]
    subprocess.run(cmd, cwd=str(script_path.parent))


def run_all_labs():
    """Sequentially executes all lab modules in order."""
    for unit_data in MODULES:
        for script_name, desc in unit_data["labs"]:
            script_path = ROOT_DIR / unit_data["dir"] / script_name
            # Skip GUI from batch auto-run to avoid blocking terminal
            if "gui" in script_name or script_name == "main.py":
                if script_name == "main.py":
                    subprocess.run([sys.executable, str(script_path), "--demo"], cwd=str(script_path.parent))
                continue
            run_single_lab(script_path)


def run_all_tests():
    """Discovers and executes the full unit test suite."""
    print("\n" + "=" * 76)
    print("  RUNNING CSA-0801 AUTOMATED TEST SUITE")
    print("=" * 76 + "\n")
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT_DIR / "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def interactive_menu():
    """Main interactive terminal navigation loop."""
    while True:
        print_banner()
        print("  COURSE MODULES:")
        for idx, mod in enumerate(MODULES, 1):
            print(f"   [{idx}] Unit {mod['unit']}: {mod['title']} ({len(mod['labs'])} Labs)")

        print("\n  ACTIONS & TOOLS:")
        print("   [T] Run All Automated Unit Tests (unittest)")
        print("   [A] Run All Lab Demonstrations (Batch)")
        print("   [C] Launch Capstone System (CLI Menu / GUI)")
        print("   [G] Launch Capstone Desktop GUI Directly")
        print("   [Q] Quit")
        print("=" * 76)

        choice = input("\nSelect an option: ").strip().upper()

        if choice == "Q":
            print("\nExiting CSA-0801 Lab Suite. Happy Coding!")
            break
        elif choice == "T":
            run_all_tests()
        elif choice == "A":
            run_all_labs()
        elif choice == "C":
            cap_main = ROOT_DIR / "08_capstone_project" / "main.py"
            subprocess.run([sys.executable, str(cap_main)], cwd=str(cap_main.parent))
        elif choice == "G":
            cap_gui = ROOT_DIR / "08_capstone_project" / "gui_app.py"
            subprocess.run([sys.executable, str(cap_gui)], cwd=str(cap_gui.parent))
        elif choice.isdigit() and 1 <= int(choice) <= len(MODULES):
            unit_idx = int(choice) - 1
            mod = MODULES[unit_idx]
            while True:
                print("\n" + "-" * 76)
                print(f"  UNIT {mod['unit']}: {mod['title']}")
                print("-" * 76)
                for l_idx, (fname, desc) in enumerate(mod["labs"], 1):
                    print(f"   [{l_idx}] {fname:<32} : {desc}")
                print("   [B] Back to Main Menu")
                print("-" * 76)

                sub_choice = input("\nSelect lab to execute: ").strip().upper()
                if sub_choice == "B":
                    break
                elif sub_choice.isdigit() and 1 <= int(sub_choice) <= len(mod["labs"]):
                    lab_file = mod["labs"][int(sub_choice) - 1][0]
                    script_path = ROOT_DIR / mod["dir"] / lab_file
                    run_single_lab(script_path)
                    input("\nPress Enter to continue...")
                else:
                    print("Invalid choice.")
        else:
            print("Invalid selection. Please choose a valid option.")

        input("\nPress Enter to continue...")


def main():
    parser = argparse.ArgumentParser(description="CSA-0801 Python Lab Suite Runner")
    parser.add_argument("--test", action="store_true", help="Run full automated test suite")
    parser.add_argument("--all", action="store_true", help="Run all lab modules sequentially")
    parser.add_argument("--capstone", action="store_true", help="Launch Capstone CLI directly")
    parser.add_argument("--gui", action="store_true", help="Launch Capstone Desktop GUI directly")
    args = parser.parse_args()

    if args.test:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    elif args.all:
        run_all_labs()
    elif args.capstone:
        cap_main = ROOT_DIR / "08_capstone_project" / "main.py"
        subprocess.run([sys.executable, str(cap_main)], cwd=str(cap_main.parent))
    elif args.gui:
        cap_gui = ROOT_DIR / "08_capstone_project" / "gui_app.py"
        subprocess.run([sys.executable, str(cap_gui)], cwd=str(cap_gui.parent))
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
