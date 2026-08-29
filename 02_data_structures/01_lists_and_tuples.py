"""
CSA-0801: Python Programming - Module 02
Topic: Lists, Tuples, Slicing, List Comprehensions, and Sequence Unpacking

Key Concepts Covered:
1. List mutability vs Tuple immutability (memory footprints)
2. Slicing with step syntax ([start:stop:step], reversal)
3. Advanced List Comprehensions (nested, conditional)
4. Sequence unpacking (*rest, named tuples)
5. Matrix transformations (transpose, flattening)
"""

import sys
from collections import namedtuple


StudentPoint = namedtuple("StudentPoint", ["roll_no", "name", "gpa"])


def list_comprehension_suite(numbers: list[int]) -> dict[str, list]:
    """Demonstrates single and conditional list comprehensions."""
    return {
        "even_squares": [x ** 2 for x in numbers if x % 2 == 0],
        "odd_cubes": [x ** 3 for x in numbers if x % 2 != 0],
        "positive_labels": ["Even" if x % 2 == 0 else "Odd" for x in numbers],
    }


def matrix_operations_demo(matrix: list[list[int]]) -> dict[str, Any]:
    """Demonstrates 2D matrix transpose, row sums, and flattened list."""
    # Matrix Transpose using nested comprehension
    transpose = [[row[i] for row in matrix] for i in range(len(matrix[0]))]

    # Flattened Matrix
    flattened = [val for row in matrix for val in row]

    # Row sums
    row_sums = [sum(row) for row in matrix]

    return {
        "original": matrix,
        "transpose": transpose,
        "flattened": flattened,
        "row_sums": row_sums,
    }


def demonstrate_tuple_immutability() -> dict[str, Any]:
    """Illustrates namedtuple, memory compactness, and hashability."""
    tup = (101, "Alice", 9.2)
    lst = [101, "Alice", 9.2]

    nt = StudentPoint("CSA-001", "Bob Smith", 9.5)

    return {
        "tuple_size_bytes": sys.getsizeof(tup),
        "list_size_bytes": sys.getsizeof(lst),
        "named_tuple_val": nt,
        "named_tuple_field_access": f"Name={nt.name}, GPA={nt.gpa}",
        "tuple_hash": hash(tup),
    }


def advanced_unpacking_demo(records: list[str]) -> list[dict[str, Any]]:
    """Demonstrates extended iterable unpacking (*rest syntax)."""
    parsed = []
    for line in records:
        # Expected format: "ID, FirstName, LastName, Course1, Course2, Course3, ..."
        student_id, first_name, last_name, *courses = [p.strip() for p in line.split(",")]
        parsed.append({
            "id": student_id,
            "full_name": f"{first_name} {last_name}",
            "enrolled_courses": courses,
            "course_count": len(courses)
        })
    return parsed


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 2.1 - Lists, Tuples & Sequence Unpacking")
    print("=" * 60)

    print("\n[1] List Comprehensions (Numbers 1 to 10):")
    sample_nums = list(range(1, 11))
    for k, v in list_comprehension_suite(sample_nums).items():
        print(f"  * {k:<18}: {v}")

    print("\n[2] Matrix Transposition & Flattening:")
    mat = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    res = matrix_operations_demo(mat)
    print(f"  * Original:  {res['original']}")
    print(f"  * Transpose: {res['transpose']}")
    print(f"  * Flattened: {res['flattened']}")

    print("\n[3] Memory Efficiency & Named Tuples:")
    t_info = demonstrate_tuple_immutability()
    print(f"  * Tuple Size: {t_info['tuple_size_bytes']} bytes vs List Size: {t_info['list_size_bytes']} bytes")
    print(f"  * NamedTuple: {t_info['named_tuple_val']}")
    print(f"  * Access:     {t_info['named_tuple_field_access']}")

    print("\n[4] Extended Unpacking (*rest):")
    raw_lines = [
        "101, Nikhil, Karnati, CSA-0801, MATH-201, PHY-102",
        "102, Priya, Sharma, CSA-0801, AI-301",
        "103, Rahul, Verma, CSA-0801, DS-202, WEB-105, STAT-204",
    ]
    for p in advanced_unpacking_demo(raw_lines):
        print(f"  * Student {p['id']}: {p['full_name']} ({p['course_count']} courses -> {p['enrolled_courses']})")

    print("\n[OK] Lab 2.1 execution completed successfully.\n")


if __name__ == "__main__":
    from typing import Any
    run_demo()
