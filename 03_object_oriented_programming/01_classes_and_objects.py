"""
CSA-0801: Python Programming - Module 03
Topic: Classes, Instances, Class vs Instance Attributes, and Methods

Key Concepts Covered:
1. Class definition, constructor (__init__), and self reference
2. Class variables (shared state) vs Instance variables (isolated state)
3. Instance methods, Class methods (@classmethod), and Static methods (@staticmethod)
4. String representation (__str__ for users, __repr__ for developers)
5. Garbage collection and destructor hook (__del__)
"""

from typing import Optional


class Student:
    """Represents a student enrolled in the CSA department."""

    # Class Variables (Shared across all instances)
    INSTITUTE_NAME: str = "CSA Institute of Technology"
    TOTAL_STUDENTS_ENROLLED: int = 0
    PASSING_GPA: float = 5.0

    def __init__(self, student_id: str, full_name: str, department: str = "Computer Science"):
        # Instance Variables (Unique to each instance)
        self.student_id: str = student_id
        self.full_name: str = full_name
        self.department: str = department
        self._gpa: float = 0.0
        self._course_credits: dict[str, int] = {}

        Student.TOTAL_STUDENTS_ENROLLED += 1

    # Instance Method
    def enroll_course(self, course_code: str, credits: int) -> None:
        """Enrolls the student in a course with specified credits."""
        self._course_credits[course_code] = credits

    # Instance Method
    def update_gpa(self, gpa: float) -> None:
        """Sets the student's cumulative GPA."""
        if not (0.0 <= gpa <= 10.0):
            raise ValueError(f"GPA must be between 0.0 and 10.0, got {gpa}")
        self._gpa = gpa

    # Instance Method
    def is_in_good_standing(self) -> bool:
        return self._gpa >= Student.PASSING_GPA

    # Class Method
    @classmethod
    def get_enrollment_statistics(cls) -> str:
        """Class method accessing and reporting class-level state."""
        return f"{cls.INSTITUTE_NAME} - Total Enrolled: {cls.TOTAL_STUDENTS_ENROLLED}"

    # Class Method Factory
    @classmethod
    def from_csv_line(cls, csv_line: str) -> "Student":
        """Factory method to construct a Student instance from a comma-separated string."""
        parts = [p.strip() for p in csv_line.split(",")]
        return cls(student_id=parts[0], full_name=parts[1], department=parts[2])

    # Static Method
    @staticmethod
    def calculate_letter_grade(percentage: float) -> str:
        """Pure utility function that does not depend on instance or class state."""
        if percentage >= 90:
            return "O"
        elif percentage >= 80:
            return "A+"
        elif percentage >= 70:
            return "A"
        elif percentage >= 60:
            return "B+"
        elif percentage >= 50:
            return "B"
        return "F"

    # Developer-facing string representation
    def __repr__(self) -> str:
        return f"Student(id={self.student_id!r}, name={self.full_name!r}, dept={self.department!r}, gpa={self._gpa})"

    # User-facing string representation
    def __str__(self) -> str:
        return f"[{self.student_id}] {self.full_name} ({self.department}) - GPA: {self._gpa:.2f}"


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 3.1 - Classes, Objects & Methods")
    print("=" * 60)

    print("\n[1] Instantiation and Class Variable Tracking:")
    s1 = Student("STU-101", "Nikhil Karnati", "Computer Science & AI")
    s2 = Student("STU-102", "Priya Sharma", "Information Technology")
    s1.update_gpa(9.45)
    s2.update_gpa(8.80)

    print(f"  * Instance 1: {s1}")
    print(f"  * Instance 2: {s2}")
    print(f"  * Class Stats: {Student.get_enrollment_statistics()}")

    print("\n[2] Class Factory Method (from_csv_line):")
    csv_sample = "STU-103, Rahul Verma, Data Science"
    s3 = Student.from_csv_line(csv_sample)
    s3.update_gpa(4.80)
    print(f"  * Factory Created: {s3}")
    print(f"  * In Good Standing: {s3.is_in_good_standing()} (Threshold: {Student.PASSING_GPA})")

    print("\n[3] Static Method Utility:")
    for score in [94.5, 78.0, 52.5, 38.0]:
        print(f"  * Score {score}% -> Grade: {Student.calculate_letter_grade(score)}")

    print("\n[4] __repr__ vs __str__ Inspection:")
    print(f"  * str(s1)  -> {str(s1)}")
    print(f"  * repr(s1) -> {repr(s1)}")

    print("\n[OK] Lab 3.1 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
