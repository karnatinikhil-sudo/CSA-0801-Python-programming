"""
Capstone SQLite Database Engine supporting transactional integrity and schema management.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional


class CapstoneDBEngine:
    """Manages SQLite persistent storage for the Student Academic & Wellness System."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self._is_memory = (self.db_path == ":memory:")
        self._memory_conn: Optional[sqlite3.Connection] = None
        if self._is_memory:
            self._memory_conn = sqlite3.connect(":memory:")
            self._memory_conn.row_factory = sqlite3.Row
            self._memory_conn.execute("PRAGMA foreign_keys = ON;")
        self._init_tables()

    def get_connection(self) -> sqlite3.Connection:
        if self._is_memory and self._memory_conn:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if not self._is_memory:
                conn.close()

    def _init_tables(self) -> None:
        """Initializes normalized tables for students, courses, enrollments, grades, and wellness."""
        ddl = """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS capstone_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL DEFAULT 'Computer Science',
            semester INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS capstone_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            credits INTEGER NOT NULL CHECK (credits > 0),
            instructor TEXT NOT NULL,
            department TEXT NOT NULL DEFAULT 'Computer Science'
        );

        CREATE TABLE IF NOT EXISTS capstone_grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT NOT NULL,
            marks REAL NOT NULL CHECK (marks >= 0.0 AND marks <= 100.0),
            grade_letter TEXT NOT NULL,
            grade_points REAL NOT NULL,
            semester INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES capstone_students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_code) REFERENCES capstone_courses(course_code) ON DELETE CASCADE,
            UNIQUE(student_id, course_code, semester)
        );

        CREATE TABLE IF NOT EXISTS capstone_wellness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            study_hours REAL NOT NULL,
            sleep_hours REAL NOT NULL,
            stress_level INTEGER NOT NULL CHECK (stress_level >= 1 AND stress_level <= 10),
            exercise_minutes INTEGER NOT NULL DEFAULT 0,
            water_intake_liters REAL NOT NULL DEFAULT 2.0,
            wellness_score REAL NOT NULL,
            burnout_risk TEXT NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES capstone_students(student_id) ON DELETE CASCADE
        );
        """
        with self.get_connection() as conn:
            conn.executescript(ddl)

    def seed_initial_demo_data(self) -> None:
        """Seeds the database with representative academic and wellness cohort records."""
        # 1. Seed Courses
        courses_data = [
            ("CSA-0801", "Python Programming", 4, "Prof. Nikhil Karnati", "Computer Science"),
            ("CSA-0802", "Data Structures & Algorithms", 4, "Dr. Ada Lovelace", "Computer Science"),
            ("CSA-0803", "Relational Database Management", 3, "Dr. Edgar Codd", "Computer Science"),
            ("CSA-0804", "Artificial Intelligence & ML", 4, "Prof. Alan Turing", "AI & Robotics"),
            ("MATH-201", "Linear Algebra & Probability", 3, "Dr. Carl Gauss", "Mathematics"),
        ]
        with self.transaction() as cur:
            for code, title, cred, instr, dept in courses_data:
                cur.execute(
                    "INSERT OR IGNORE INTO capstone_courses (course_code, title, credits, instructor, department) "
                    "VALUES (?, ?, ?, ?, ?);",
                    (code, title, cred, instr, dept)
                )

        # 2. Seed Students
        students_data = [
            ("STU-101", "Nikhil Karnati", "nikhil@csa.edu", "Computer Science", 4),
            ("STU-102", "Priya Sharma", "priya@csa.edu", "AI & Robotics", 4),
            ("STU-103", "Rahul Verma", "rahul@csa.edu", "Information Technology", 4),
            ("STU-104", "Ananya Reddy", "ananya@csa.edu", "Computer Science", 4),
            ("STU-105", "Karthik Raja", "karthik@csa.edu", "Data Science", 4),
        ]
        with self.transaction() as cur:
            for sid, name, email, dept, sem in students_data:
                cur.execute(
                    "INSERT OR IGNORE INTO capstone_students (student_id, full_name, email, department, semester) "
                    "VALUES (?, ?, ?, ?, ?);",
                    (sid, name, email, dept, sem)
                )

        # 3. Seed Grades
        grades_data = [
            ("STU-101", "CSA-0801", 96.0, "O", 10.0, 4),
            ("STU-101", "CSA-0802", 92.5, "O", 10.0, 4),
            ("STU-101", "CSA-0803", 88.0, "A+", 9.0, 4),
            ("STU-101", "MATH-201", 91.0, "O", 10.0, 4),

            ("STU-102", "CSA-0801", 89.5, "A+", 9.0, 4),
            ("STU-102", "CSA-0804", 94.0, "O", 10.0, 4),
            ("STU-102", "MATH-201", 86.0, "A+", 9.0, 4),

            ("STU-103", "CSA-0801", 72.0, "A", 8.0, 4),
            ("STU-103", "CSA-0802", 68.5, "B+", 7.0, 4),
            ("STU-103", "CSA-0803", 74.0, "A", 8.0, 4),

            ("STU-104", "CSA-0801", 98.0, "O", 10.0, 4),
            ("STU-104", "CSA-0802", 95.0, "O", 10.0, 4),
            ("STU-104", "CSA-0804", 97.5, "O", 10.0, 4),

            ("STU-105", "CSA-0801", 81.0, "A+", 9.0, 4),
            ("STU-105", "CSA-0803", 83.0, "A+", 9.0, 4),
        ]
        with self.transaction() as cur:
            for sid, code, marks, g_let, g_pts, sem in grades_data:
                cur.execute(
                    "INSERT OR REPLACE INTO capstone_grades (student_id, course_code, marks, grade_letter, grade_points, semester) "
                    "VALUES (?, ?, ?, ?, ?, ?);",
                    (sid, code, marks, g_let, g_pts, sem)
                )

        # 4. Seed Wellness Logs
        wellness_data = [
            ("STU-101", 4.5, 7.5, 3, 45, 2.5, 94.0, "LOW RISK - Healthy academic lifestyle"),
            ("STU-102", 5.0, 7.0, 4, 30, 2.0, 88.0, "LOW RISK - Healthy academic lifestyle"),
            ("STU-103", 8.5, 4.5, 8, 10, 1.2, 51.0, "HIGH RISK - Immediate rest & counseling advised"),
            ("STU-104", 4.0, 8.0, 2, 60, 3.0, 98.0, "LOW RISK - Healthy academic lifestyle"),
            ("STU-105", 6.0, 6.0, 6, 20, 2.0, 72.0, "MODERATE RISK - Balance study and sleep schedule"),
        ]
        with self.transaction() as cur:
            for sid, study, sleep, stress, ex, water, score, risk in wellness_data:
                cur.execute(
                    "INSERT INTO capstone_wellness (student_id, study_hours, sleep_hours, stress_level, exercise_minutes, water_intake_liters, wellness_score, burnout_risk) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                    (sid, study, sleep, stress, ex, water, score, risk)
                )
