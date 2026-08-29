"""
Course domain entity representing an academic syllabus subject.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Course:
    course_code: str
    title: str
    credits: int
    instructor: str
    department: str = "Computer Science"
    id: Optional[int] = None

    def validate(self) -> None:
        if not self.course_code or not self.course_code.strip():
            raise ValueError("Course code cannot be empty.")
        if not self.title or not self.title.strip():
            raise ValueError("Course title cannot be empty.")
        if not (1 <= self.credits <= 6):
            raise ValueError(f"Course credits must be between 1 and 6, got {self.credits}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "course_code": self.course_code,
            "title": self.title,
            "credits": self.credits,
            "instructor": self.instructor,
            "department": self.department,
        }
