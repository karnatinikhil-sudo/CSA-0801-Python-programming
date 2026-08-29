"""
CSA-0801: Python Programming - Module 06
Topic: SQLite Database Manager, Transactions, and Parameterized CRUD

Key Concepts Covered:
1. SQLite connection lifecycle and row factories (sqlite3.Row)
2. Safe parameterized SQL statements (preventing SQL Injection)
3. ACID Transactions with context managers
4. Foreign Key enforcement and Cascade Deletions
5. Complex multi-table JOINs and aggregation queries
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional


class DatabaseManager:
    """Enterprise SQLite Database Handler with connection pooling and transactions."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self._is_memory = (self.db_path == ":memory:")
        self._memory_conn: Optional[sqlite3.Connection] = None
        if self._is_memory:
            self._memory_conn = sqlite3.connect(":memory:")
            self._memory_conn.row_factory = sqlite3.Row
            self._memory_conn.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with foreign keys enabled."""
        if self._is_memory and self._memory_conn:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Dict-like row access
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager providing atomic commit / rollback transaction semantics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if not self._is_memory:
                conn.close()

    def close(self) -> None:
        if self._memory_conn:
            self._memory_conn.close()
            self._memory_conn = None

    def _init_schema(self) -> None:
        """Initializes database schema from schema.sql file if present."""
        schema_file = Path(__file__).parent / "schema.sql"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema_sql)

    # 1. Student CRUD Operations
    def add_student(self, student_id: str, full_name: str, email: str, department: str = "Computer Science") -> int:
        query = "INSERT INTO students (student_id, full_name, email, department) VALUES (?, ?, ?, ?);"
        with self.transaction() as cur:
            cur.execute(query, (student_id, full_name, email, department))
            return cur.lastrowid or 0

    def get_student_by_roll(self, student_id: str) -> Optional[dict[str, Any]]:
        query = "SELECT * FROM students WHERE student_id = ?;"
        with self.get_connection() as conn:
            row = conn.execute(query, (student_id,)).fetchone()
            return dict(row) if row else None

    def list_all_students(self) -> list[dict[str, Any]]:
        query = "SELECT * FROM students ORDER BY student_id ASC;"
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def update_student(self, student_id: str, full_name: Optional[str] = None, email: Optional[str] = None) -> bool:
        updates = []
        params = []
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if not updates:
            return False

        params.append(student_id)
        query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?;"
        with self.transaction() as cur:
            cur.execute(query, tuple(params))
            return cur.rowcount > 0

    def delete_student(self, student_id: str) -> bool:
        query = "DELETE FROM students WHERE student_id = ?;"
        with self.transaction() as cur:
            cur.execute(query, (student_id,))
            return cur.rowcount > 0

    # 2. Course & Enrollment Operations
    def add_course(self, course_code: str, title: str, credits: int, instructor: str) -> int:
        query = "INSERT INTO courses (course_code, title, credits, instructor) VALUES (?, ?, ?, ?);"
        with self.transaction() as cur:
            cur.execute(query, (course_code, title, credits, instructor))
            return cur.lastrowid or 0

    def enroll_student_in_course(self, student_id: str, course_code: str) -> bool:
        query = """
        INSERT INTO enrollments (student_id, course_id)
        SELECT s.id, c.id
        FROM students s, courses c
        WHERE s.student_id = ? AND c.course_code = ?;
        """
        with self.transaction() as cur:
            cur.execute(query, (student_id, course_code))
            return cur.rowcount > 0

    # 3. Grade Records & GPA Calculation
    def add_grade(self, student_id: str, course_code: str, marks: float, grade_letter: str, semester: int) -> int:
        query = """
        INSERT INTO grade_records (student_id, course_id, marks, grade_letter, semester)
        SELECT s.id, c.id, ?, ?, ?
        FROM students s, courses c
        WHERE s.student_id = ? AND c.course_code = ?;
        """
        with self.transaction() as cur:
            cur.execute(query, (marks, grade_letter, semester, student_id, course_code))
            return cur.lastrowid or 0

    def get_student_transcript(self, student_id: str) -> list[dict[str, Any]]:
        """Performs a 3-table JOIN to generate a student academic transcript."""
        query = """
        SELECT
            s.student_id, s.full_name,
            c.course_code, c.title AS course_title, c.credits,
            g.marks, g.grade_letter, g.semester, g.recorded_at
        FROM students s
        JOIN grade_records g ON s.id = g.student_id
        JOIN courses c ON g.course_id = c.id
        WHERE s.student_id = ?
        ORDER BY g.semester ASC, c.course_code ASC;
        """
        with self.get_connection() as conn:
            rows = conn.execute(query, (student_id,)).fetchall()
            return [dict(r) for r in rows]

    def compute_student_gpa(self, student_id: str) -> float:
        """Calculates credit-weighted GPA for a student."""
        transcript = self.get_student_transcript(student_id)
        if not transcript:
            return 0.0

        grade_points_map = {"O": 10.0, "A+": 9.0, "A": 8.0, "B+": 7.0, "B": 6.0, "C": 5.0, "F": 0.0}
        total_points = 0.0
        total_credits = 0

        for record in transcript:
            pts = grade_points_map.get(record["grade_letter"], 0.0)
            cred = record["credits"]
            total_points += pts * cred
            total_credits += cred

        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
