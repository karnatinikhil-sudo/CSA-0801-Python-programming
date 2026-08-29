"""
CSA-0801: Python Programming - Module 01
Topic: Conditional Statements, Branching Logic, and Pattern Matching

Key Concepts Covered:
1. if, elif, else construct
2. Nested conditionals & ternary conditional expressions (x if c else y)
3. Structural Pattern Matching (match-case introduced in Python 3.10+)
4. Academic grading system logic and input classification
"""

from typing import Any


def determine_letter_grade(score: float) -> tuple[str, str, float]:
    """
    Evaluates score and returns (Letter Grade, Academic Description, Grade Points).
    Uses clean multi-branch conditional structure.
    """
    if score < 0 or score > 100:
        raise ValueError(f"Invalid score: {score}. Score must be between 0 and 100.")

    if score >= 90:
        return ("O", "Outstanding", 10.0)
    elif score >= 80:
        return ("A+", "Excellent", 9.0)
    elif score >= 70:
        return ("A", "Very Good", 8.0)
    elif score >= 60:
        return ("B+", "Good", 7.0)
    elif score >= 50:
        return ("B", "Above Average", 6.0)
    elif score >= 40:
        return ("C", "Pass", 5.0)
    else:
        return ("F", "Fail", 0.0)


def classify_command_pattern_matching(command: dict[str, Any]) -> str:
    """
    Demonstrates Python 3.10+ Structural Pattern Matching (`match-case`).
    Parses structured event dictionary payloads.
    """
    match command:
        case {"action": "enroll", "student_id": sid, "course_code": code}:
            return f"Action: Enrolling student {sid} into course {code}"
        case {"action": "drop", "student_id": sid, "course_code": code, "reason": reason}:
            return f"Action: Dropping student {sid} from {code} (Reason: {reason})"
        case {"action": "grade", "student_id": sid, "marks": list(marks)}:
            avg_mark = sum(marks) / len(marks) if marks else 0.0
            return f"Action: Grading student {sid} with {len(marks)} items (Average: {avg_mark:.1f})"
        case {"action": "audit", **kwargs}:
            return f"Action: System Audit triggered with params: {kwargs}"
        case _:
            return "Unknown command signature"


def leap_year_checker(year: int) -> bool:
    """
    Determines if a year is a leap year using boolean logic.
    A year is leap if (divisible by 4 AND NOT divisible by 100) OR divisible by 400.
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 1.3 - Conditional Statements & Pattern Matching")
    print("=" * 60)

    print("\n[1] Academic Grade Evaluation Matrix:")
    test_scores = [95.5, 84.0, 72.5, 63.0, 52.0, 41.5, 28.0]
    for sc in test_scores:
        grade, desc, points = determine_letter_grade(sc)
        print(f"  * Score: {sc:>5.1f}% -> Grade: {grade:<3} Points: {points:<4.1f} ({desc})")

    print("\n[2] Leap Year Evaluation:")
    sample_years = [1900, 2000, 2024, 2026, 2028]
    for yr in sample_years:
        is_leap = leap_year_checker(yr)
        status = "Leap Year" if is_leap else "Common Year"
        print(f"  * Year {yr}: {status}")

    print("\n[3] Structural Pattern Matching (match-case):")
    commands = [
        {"action": "enroll", "student_id": "STU-101", "course_code": "CSA-0801"},
        {"action": "drop", "student_id": "STU-102", "course_code": "MATH-201", "reason": "Schedule clash"},
        {"action": "grade", "student_id": "STU-103", "marks": [88, 92, 95, 90]},
        {"action": "audit", "actor": "Admin", "timestamp": "2026-08-29"},
    ]
    for cmd in commands:
        print(f"  * {classify_command_pattern_matching(cmd)}")

    print("\n[OK] Lab 1.3 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
