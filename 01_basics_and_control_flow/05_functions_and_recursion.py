"""
CSA-0801: Python Programming - Module 01
Topic: Functions, Variable Scope, Lambda, Higher-Order Functions, and Recursion

Key Concepts Covered:
1. Positional, Keyword, *args, and **kwargs parameters
2. First-class functions, closures, and decorators
3. Functional programming primitives: map(), filter(), reduce()
4. Recursive problem solving (Factorial, Fibonacci with memoization, Tower of Hanoi)
5. Type hinting and docstring standards (PEP 257 / PEP 484)
"""

import time
from functools import lru_cache, reduce
from typing import Any, Callable


# 1. Flexible Argument Unpacking
def generate_course_summary(
    course_name: str,
    instructor: str,
    *modules: str,
    semester: int = 1,
    **metadata: Any
) -> dict[str, Any]:
    """Demonstrates positional, variable positional (*args), default, and keyword (**kwargs) args."""
    return {
        "course": course_name,
        "instructor": instructor,
        "semester": semester,
        "modules_count": len(modules),
        "module_list": list(modules),
        "extra_metadata": metadata,
    }


# 2. Timing Decorator (Higher-Order Function & Closure)
def execution_timer(func: Callable) -> Callable:
    """Decorator to benchmark execution time of a function."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return result, duration
    return wrapper


# 3. Recursion & Memoization
@lru_cache(maxsize=128)
def fibonacci_memoized(n: int) -> int:
    """Computes nth Fibonacci number using recursion with LRU cache."""
    if n < 0:
        raise ValueError("Fibonacci index must be non-negative.")
    if n in (0, 1):
        return n
    return fibonacci_memoized(n - 1) + fibonacci_memoized(n - 2)


def tower_of_hanoi(n_disks: int, source: str, target: str, auxiliary: str) -> list[str]:
    """
    Solves Tower of Hanoi problem recursively.
    Total moves required: 2^n - 1.
    """
    moves = []

    def _hanoi(n, src, tgt, aux):
        if n == 1:
            moves.append(f"Move disk 1 from {src} -> {tgt}")
            return
        _hanoi(n - 1, src, aux, tgt)
        moves.append(f"Move disk {n} from {src} -> {tgt}")
        _hanoi(n - 1, aux, tgt, src)

    _hanoi(n_disks, source, target, auxiliary)
    return moves


# 4. Functional Programming Suite
def functional_analytics(grades: list[float]) -> dict[str, Any]:
    """Demonstrates map(), filter(), reduce(), and lambda expressions."""
    # Filter passing grades (>= 50)
    passing_grades = list(filter(lambda g: g >= 50.0, grades))

    # Curve grades by 5% (map)
    curved_grades = list(map(lambda g: round(min(100.0, g * 1.05), 2), passing_grades))

    # Compute total score using reduce
    total_score = reduce(lambda acc, val: acc + val, curved_grades, 0.0)

    # Average score
    avg_curved = total_score / len(curved_grades) if curved_grades else 0.0

    return {
        "original_count": len(grades),
        "passing_count": len(passing_grades),
        "curved_grades": curved_grades,
        "average_curved": round(avg_curved, 2),
    }


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 1.5 - Functions, Higher-Order Tools & Recursion")
    print("=" * 60)

    print("\n[1] Dynamic Function Signatures (*args, **kwargs):")
    summary = generate_course_summary(
        "CSA-0801 Python Programming",
        "Prof. Karnati",
        "Basics & Control Flow",
        "Data Structures",
        "OOP & Design Patterns",
        "Database & SQLite",
        "Tkinter GUI",
        "Capstone Project",
        semester=4,
        credits=4,
        lab_hours=30
    )
    for k, v in summary.items():
        print(f"  * {k:<15}: {v}")

    print("\n[2] Memoized Recursion (Fibonacci 50th Term):")
    fib_50 = fibonacci_memoized(50)
    print(f"  * Fib(50) = {fib_50:,}")

    print("\n[3] Tower of Hanoi Recursive Steps (3 Disks):")
    steps = tower_of_hanoi(3, "Peg-A", "Peg-C", "Peg-B")
    for idx, step in enumerate(steps, 1):
        print(f"  * Step {idx}: {step}")

    print("\n[4] Functional Transformations (map, filter, reduce):")
    raw_scores = [45.0, 88.0, 92.5, 34.0, 76.0, 95.0, 62.0]
    analytics = functional_analytics(raw_scores)
    print(f"  * Raw Scores: {raw_scores}")
    print(f"  * Analytics Summary: {analytics}")

    print("\n[OK] Lab 1.5 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
