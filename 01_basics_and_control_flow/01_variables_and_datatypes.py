"""
CSA-0801: Python Programming - Module 01
Topic: Variables, Data Types, Type Casting, and Memory Model

Key Concepts Covered:
1. Primitive Data Types (int, float, bool, str, complex, NoneType)
2. Dynamic Typing and Type Inference
3. Memory references (id, is vs ==, immutability)
4. Explicit and Implicit Type Conversion
5. String formatting (f-strings, format method, % operator)
"""

import sys


def demonstrate_primitive_types() -> dict[str, tuple[object, type]]:
    """Demonstrates and returns standard primitive data types in Python."""
    data = {
        "integer": (42, int),
        "floating_point": (3.14159265, float),
        "boolean": (True, bool),
        "string": ("CSA-0801 Python Programming", str),
        "complex_number": (3 + 4j, complex),
        "none_type": (None, type(None)),
    }
    return data


def demonstrate_immutability_and_references() -> list[dict[str, object]]:
    """Illustrates Python's object identity, reference caching, and immutability."""
    results = []

    # Small integer caching (-5 to 256)
    a = 256
    b = 256
    results.append({
        "case": "Small Integer Caching",
        "a": a, "b": b,
        "a_id": id(a), "b_id": id(b),
        "is_same_object": a is b,
        "is_equal_value": a == b
    })

    # String interning & immutability
    s1 = "hello_world"
    s2 = "hello_world"
    results.append({
        "case": "String Reference",
        "s1": s1, "s2": s2,
        "s1_id": id(s1), "s2_id": id(s2),
        "is_same_object": s1 is s2,
        "is_equal_value": s1 == s2
    })

    return results


def type_conversion_pipeline(raw_inputs: list[str]) -> list[dict[str, object]]:
    """
    Parses and casts a list of raw string inputs into their appropriate native types.
    """
    converted = []
    for item in raw_inputs:
        item_clean = item.strip()
        # Try integer
        try:
            val = int(item_clean)
            converted.append({"raw": item, "converted": val, "type": "int"})
            continue
        except ValueError:
            pass

        # Try float
        try:
            val = float(item_clean)
            converted.append({"raw": item, "converted": val, "type": "float"})
            continue
        except ValueError:
            pass

        # Try bool
        if item_clean.lower() in ("true", "false"):
            val = item_clean.lower() == "true"
            converted.append({"raw": item, "converted": val, "type": "bool"})
            continue

        # Fallback to string
        converted.append({"raw": item, "converted": item_clean, "type": "str"})

    return converted


def format_student_profile(name: str, roll_no: str, gpa: float, semester: int) -> str:
    """Generates formatted academic record using modern Python f-strings with specs."""
    return (
        f"+{'-' * 45}+\n"
        f"| STUDENT ACADEMIC PROFILE                    |\n"
        f"+{'-' * 45}+\n"
        f"| Name      : {name:<31} |\n"
        f"| Roll No   : {roll_no:<31} |\n"
        f"| Semester  : {semester:<31} |\n"
        f"| GPA       : {gpa:<31.2f} |\n"
        f"+{'-' * 45}+"
    )


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 1.1 - Variables, Types & Memory Model")
    print("=" * 60)

    print("\n[1] Primitive Data Types:")
    for name, (val, t) in demonstrate_primitive_types().items():
        print(f"  * {name:<15}: Value={repr(val):<28} Type={t.__name__:<10} Size={sys.getsizeof(val)}B")

    print("\n[2] Object Identity & Memory References:")
    for ref in demonstrate_immutability_and_references():
        print(f"  * {ref['case']}: id1={ref.get('a_id') or ref.get('s1_id')}, "
              f"id2={ref.get('b_id') or ref.get('s2_id')}, "
              f"is={ref['is_same_object']}, ==={ref['is_equal_value']}")

    print("\n[3] Safe Type Casting Pipeline:")
    sample_inputs = ["1042", "98.75", "True", "Python Programming", " -42 "]
    for res in type_conversion_pipeline(sample_inputs):
        print(f"  * Input: {res['raw']:<22} -> Converted: {repr(res['converted']):<20} ({res['type']})")

    print("\n[4] Formatted String Output:")
    print(format_student_profile("Nikhil Karnati", "CSA-2026-0801", 9.85, 4))
    print("\n[OK] Lab 1.1 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
