"""
CSA-0801: Python Programming - Module 02
Topic: Dictionaries, Sets, Hash Tables, and Set Algebra

Key Concepts Covered:
1. Dictionary CRUD operations, defaults, and views (keys, values, items)
2. Dictionary Comprehensions and merging (Python 3.9+ | operator)
3. Set operations: Union, Intersection, Difference, Symmetric Difference
4. Word frequency analyzer & inverted index builder
5. Hash table lookup time complexity O(1)
"""

from collections import defaultdict
from typing import Any


def analyze_word_frequency(corpus: str) -> dict[str, int]:
    """
    Builds a word frequency distribution using defaultdict.
    Strips punctuation and normalizes to lower case.
    """
    clean_text = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in corpus)
    freq = defaultdict(int)
    for word in clean_text.split():
        freq[word] += 1
    return dict(sorted(freq.items(), key=lambda item: item[1], reverse=True))


def compute_set_algebra(cohort_a: set[str], cohort_b: set[str]) -> dict[str, set[str]]:
    """
    Demonstrates set operations for academic cohort analysis:
    - Enrolled in both (Intersection)
    - Total distinct students (Union)
    - Enrolled only in A (Difference A - B)
    - Enrolled in either A or B, but not both (Symmetric Difference)
    """
    return {
        "union (A | B)": cohort_a | cohort_b,
        "intersection (A & B)": cohort_a & cohort_b,
        "difference (A - B)": cohort_a - cohort_b,
        "symmetric_difference (A ^ B)": cohort_a ^ cohort_b,
    }


def dictionary_transformations(student_scores: dict[str, float]) -> dict[str, Any]:
    """
    Demonstrates dict comprehensions, filtering, and modern dict merge syntax (|).
    """
    # Grade classifications via dict comprehension
    status_map = {
        name: ("Pass" if score >= 50.0 else "Fail")
        for name, score in student_scores.items()
    }

    # Top performers (> 85.0)
    distinction_students = {
        name: score for name, score in student_scores.items() if score >= 85.0
    }

    # Merging metadata with update operator (|)
    metadata = {"course": "CSA-0801", "term": "Fall 2026"}
    combined_record = student_scores | metadata

    return {
        "status_map": status_map,
        "distinction_students": distinction_students,
        "combined_record": combined_record,
    }


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 2.2 - Dictionaries, Sets & Hash Tables")
    print("=" * 60)

    print("\n[1] Word Frequency & Corpus Tokenizer:")
    text_sample = (
        "Python is a versatile programming language. Python is dynamically typed, "
        "and Python provides clean data structures for modern programming."
    )
    freq = analyze_word_frequency(text_sample)
    print(f"  * Top Word Frequencies: {freq}")

    print("\n[2] Set Operations for Course Cohorts:")
    cs_students = {"Alice", "Bob", "Charlie", "David", "Eve"}
    ai_students = {"David", "Eve", "Frank", "Grace", "Heidi"}
    algebra_results = compute_set_algebra(cs_students, ai_students)
    for op, s_val in algebra_results.items():
        print(f"  * {op:<30}: {sorted(list(s_val))}")

    print("\n[3] Dictionary Comprehension & Merge Operations:")
    scores = {"Alice": 92.5, "Bob": 74.0, "Charlie": 45.0, "David": 88.0, "Eve": 96.0}
    dict_res = dictionary_transformations(scores)
    print(f"  * Status Map:          {dict_res['status_map']}")
    print(f"  * Distinction (>85%):  {dict_res['distinction_students']}")
    print(f"  * Merged Record Count: {len(dict_res['combined_record'])} keys")

    print("\n[OK] Lab 2.2 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
