"""
CSA-0801: Python Programming - Module 04
Topic: Robust Exception Handling, Custom Exception Hierarchies, and Context Cleanups

Key Concepts Covered:
1. Complete try-except-else-finally execution lifecycle
2. Custom Exception Classes with metadata payloads
3. Exception Chaining (raise ... from err)
4. Contextual resource cleanup guarantees
5. Logging and debugging tracebacks
"""

import sys
import traceback
from typing import Optional


# 1. Custom Exception Hierarchy
class AcademicSystemError(Exception):
    """Base exception for all domain errors in the academic suite."""
    def __init__(self, message: str, error_code: str = "ERR_ACADEMIC"):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class StudentNotFoundError(AcademicSystemError):
    def __init__(self, student_id: str):
        super().__init__(f"Student with ID '{student_id}' does not exist.", "ERR_STU_404")
        self.student_id = student_id


class DuplicateEnrollmentError(AcademicSystemError):
    def __init__(self, student_id: str, course_code: str):
        super().__init__(
            f"Student '{student_id}' is already enrolled in course '{course_code}'.",
            "ERR_DUP_ENROLL"
        )
        self.student_id = student_id
        self.course_code = course_code


class InvalidGradeRangeError(AcademicSystemError):
    def __init__(self, score: float):
        super().__init__(f"Grade score '{score}' is out of bounds (0.0 to 100.0).", "ERR_INVALID_GRADE")
        self.score = score


# 2. Domain Service demonstrating Exception Raising & Catching
class CourseRegistry:
    def __init__(self):
        self._students: dict[str, str] = {"STU-101": "Nikhil Karnati", "STU-102": "Priya Sharma"}
        self._enrollments: dict[str, set[str]] = {"STU-101": {"CSA-0801"}}

    def enroll(self, student_id: str, course_code: str) -> str:
        if student_id not in self._students:
            raise StudentNotFoundError(student_id)

        student_courses = self._enrollments.setdefault(student_id, set())
        if course_code in student_courses:
            raise DuplicateEnrollmentError(student_id, course_code)

        student_courses.add(course_code)
        return f"Successfully enrolled {self._students[student_id]} into {course_code}"

    def record_grade(self, student_id: str, score: float) -> str:
        if student_id not in self._students:
            raise StudentNotFoundError(student_id)
        if not (0.0 <= score <= 100.0):
            raise InvalidGradeRangeError(score)
        return f"Recorded grade {score}% for student {self._students[student_id]}"


def execute_enrollment_pipeline(registry: CourseRegistry, sid: str, code: str) -> dict[str, str]:
    """Demonstrates complete try-except-else-finally block."""
    result = {}
    resource_acquired = False
    try:
        resource_acquired = True
        msg = registry.enroll(sid, code)
        result["status"] = "SUCCESS"
        result["message"] = msg
    except StudentNotFoundError as e:
        result["status"] = "NOT_FOUND"
        result["message"] = f"[{e.error_code}] {e.message}"
    except DuplicateEnrollmentError as e:
        result["status"] = "DUPLICATE"
        result["message"] = f"[{e.error_code}] {e.message}"
    except AcademicSystemError as e:
        result["status"] = "SYSTEM_ERROR"
        result["message"] = f"[{e.error_code}] {e.message}"
    else:
        result["audit"] = "Enrollment ledger verified."
    finally:
        result["resource_cleanup"] = f"Lock released (Resource acquired={resource_acquired})"

    return result


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 4.2 - Exceptions & Custom Domain Errors")
    print("=" * 60)

    registry = CourseRegistry()

    print("\n[1] Successful Operation (try -> else -> finally):")
    res1 = execute_enrollment_pipeline(registry, "STU-102", "CSA-0801")
    print(f"  * Status:  {res1['status']}")
    print(f"  * Message: {res1['message']}")
    print(f"  * Audit:   {res1.get('audit')}")
    print(f"  * Cleanup: {res1['resource_cleanup']}")

    print("\n[2] Handling DuplicateEnrollmentError:")
    res2 = execute_enrollment_pipeline(registry, "STU-101", "CSA-0801")
    print(f"  * Status:  {res2['status']}")
    print(f"  * Message: {res2['message']}")
    print(f"  * Cleanup: {res2['resource_cleanup']}")

    print("\n[3] Handling StudentNotFoundError:")
    res3 = execute_enrollment_pipeline(registry, "STU-999", "CSA-0801")
    print(f"  * Status:  {res3['status']}")
    print(f"  * Message: {res3['message']}")

    print("\n[4] Handling InvalidGradeRangeError:")
    try:
        registry.record_grade("STU-101", 105.0)
    except InvalidGradeRangeError as e:
        print(f"  * Caught Expected Error: [{e.error_code}] {e}")

    print("\n[OK] Lab 4.2 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
