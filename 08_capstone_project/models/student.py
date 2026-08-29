"""
Student domain entity representing an enrolled student.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Student:
    student_id: str
    full_name: str
    email: str
    department: str = "Computer Science"
    semester: int = 1
    id: Optional[int] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

    def validate(self) -> None:
        if not self.student_id or not self.student_id.strip():
            raise ValueError("Student ID cannot be empty.")
        if not self.full_name or not self.full_name.strip():
            raise ValueError("Full name cannot be empty.")
        if "@" not in self.email or "." not in self.email:
            raise ValueError(f"Invalid email address: {self.email}")
        if not (1 <= self.semester <= 8):
            raise ValueError(f"Semester must be between 1 and 8, got {self.semester}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "full_name": self.full_name,
            "email": self.email,
            "department": self.department,
            "semester": self.semester,
            "created_at": self.created_at,
        }
