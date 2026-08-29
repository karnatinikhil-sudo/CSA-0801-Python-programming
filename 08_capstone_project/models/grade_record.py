"""
GradeRecord entity representing evaluated score, letter grade, and grade points.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GradeRecord:
    student_id: str
    course_code: str
    marks: float
    semester: int
    id: Optional[int] = None
    grade_letter: str = ""
    grade_points: float = 0.0
    recorded_at: Optional[str] = None

    def __post_init__(self):
        if not self.grade_letter or not self.grade_points:
            self._compute_grade()

    def _compute_grade(self) -> None:
        if self.marks < 0 or self.marks > 100:
            raise ValueError(f"Invalid score: {self.marks}. Must be between 0 and 100.")

        if self.marks >= 90.0:
            self.grade_letter = "O"
            self.grade_points = 10.0
        elif self.marks >= 80.0:
            self.grade_letter = "A+"
            self.grade_points = 9.0
        elif self.marks >= 70.0:
            self.grade_letter = "A"
            self.grade_points = 8.0
        elif self.marks >= 60.0:
            self.grade_letter = "B+"
            self.grade_points = 7.0
        elif self.marks >= 50.0:
            self.grade_letter = "B"
            self.grade_points = 6.0
        elif self.marks >= 40.0:
            self.grade_letter = "C"
            self.grade_points = 5.0
        else:
            self.grade_letter = "F"
            self.grade_points = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_code": self.course_code,
            "marks": self.marks,
            "grade_letter": self.grade_letter,
            "grade_points": self.grade_points,
            "semester": self.semester,
            "recorded_at": self.recorded_at,
        }
