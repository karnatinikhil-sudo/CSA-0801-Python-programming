"""
AcademicService encapsulates business logic for student registration, course enrollments,
grade calculation, and GPA rankings.
"""

from typing import Any, Optional
from database.db_engine import CapstoneDBEngine
from models.student import Student
from models.course import Course
from models.grade_record import GradeRecord


class AcademicService:
    def __init__(self, db: CapstoneDBEngine):
        self.db = db

    # 1. Student Operations
    def register_student(self, student: Student) -> bool:
        student.validate()
        query = """
        INSERT INTO capstone_students (student_id, full_name, email, department, semester)
        VALUES (?, ?, ?, ?, ?);
        """
        with self.db.transaction() as cur:
            cur.execute(query, (student.student_id, student.full_name, student.email, student.department, student.semester))
            return True

    def get_all_students(self) -> list[dict[str, Any]]:
        query = "SELECT * FROM capstone_students ORDER BY student_id ASC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def get_student(self, student_id: str) -> Optional[dict[str, Any]]:
        query = "SELECT * FROM capstone_students WHERE student_id = ?;"
        with self.db.get_connection() as conn:
            row = conn.execute(query, (student_id,)).fetchone()
            return dict(row) if row else None

    # 2. Course Operations
    def register_course(self, course: Course) -> bool:
        course.validate()
        query = """
        INSERT INTO capstone_courses (course_code, title, credits, instructor, department)
        VALUES (?, ?, ?, ?, ?);
        """
        with self.db.transaction() as cur:
            cur.execute(query, (course.course_code, course.title, course.credits, course.instructor, course.department))
            return True

    def get_all_courses(self) -> list[dict[str, Any]]:
        query = "SELECT * FROM capstone_courses ORDER BY course_code ASC;"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    # 3. Grade Operations & GPA
    def record_grade(self, grade: GradeRecord) -> bool:
        query = """
        INSERT OR REPLACE INTO capstone_grades (student_id, course_code, marks, grade_letter, grade_points, semester)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        with self.db.transaction() as cur:
            cur.execute(query, (
                grade.student_id, grade.course_code, grade.marks,
                grade.grade_letter, grade.grade_points, grade.semester
            ))
            return True

    def get_student_transcript(self, student_id: str) -> list[dict[str, Any]]:
        query = """
        SELECT
            g.id, g.student_id, s.full_name,
            g.course_code, c.title AS course_title, c.credits,
            g.marks, g.grade_letter, g.grade_points, g.semester, g.recorded_at
        FROM capstone_grades g
        JOIN capstone_students s ON g.student_id = s.student_id
        JOIN capstone_courses c ON g.course_code = c.course_code
        WHERE g.student_id = ?
        ORDER BY g.semester ASC, g.course_code ASC;
        """
        with self.db.get_connection() as conn:
            rows = conn.execute(query, (student_id,)).fetchall()
            return [dict(r) for r in rows]

    def calculate_gpa(self, student_id: str) -> tuple[float, int]:
        """Returns (GPA, Total Credits)."""
        transcript = self.get_student_transcript(student_id)
        if not transcript:
            return 0.0, 0

        total_pts = sum(rec["grade_points"] * rec["credits"] for rec in transcript)
        total_cred = sum(rec["credits"] for rec in transcript)
        gpa = round(total_pts / total_cred, 2) if total_cred > 0 else 0.0
        return gpa, total_cred

    def get_cohort_rankings(self) -> list[dict[str, Any]]:
        """Computes GPA and rankings across all students."""
        students = self.get_all_students()
        rankings = []
        for s in students:
            gpa, creds = self.calculate_gpa(s["student_id"])
            rankings.append({
                "student_id": s["student_id"],
                "full_name": s["full_name"],
                "department": s["department"],
                "gpa": gpa,
                "credits": creds,
            })
        rankings.sort(key=lambda item: item["gpa"], reverse=True)
        for idx, item in enumerate(rankings, 1):
            item["rank"] = idx
        return rankings
