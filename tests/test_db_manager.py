"""
Unit Tests for Module 06: Relational Database Operations with SQLite3.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def load_module(rel_path: str, module_name: str):
    file_path = ROOT_DIR / rel_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod6_db = load_module("06_database_operations/db_manager.py", "m6_db")


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db = mod6_db.DatabaseManager(":memory:")

    def tearDown(self):
        self.db.close()

    def test_student_crud(self):
        # Insert
        row_id = self.db.add_student("STU-501", "Test User", "test@csa.edu", "Computer Science")
        self.assertGreater(row_id, 0)

        # Read
        stu = self.db.get_student_by_roll("STU-501")
        self.assertIsNotNone(stu)
        self.assertEqual(stu["full_name"], "Test User")

        # Update
        updated = self.db.update_student("STU-501", full_name="Updated User")
        self.assertTrue(updated)
        stu_updated = self.db.get_student_by_roll("STU-501")
        self.assertEqual(stu_updated["full_name"], "Updated User")

        # Delete
        deleted = self.db.delete_student("STU-501")
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_student_by_roll("STU-501"))

    def test_course_and_transcript_gpa(self):
        self.db.add_student("STU-601", "Alice Smith", "alice@csa.edu")
        self.db.add_course("CSA-0801", "Python Programming", 4, "Prof. Karnati")
        self.db.add_course("CSA-0802", "Data Structures", 4, "Dr. Lovelace")

        self.db.enroll_student_in_course("STU-601", "CSA-0801")
        self.db.enroll_student_in_course("STU-601", "CSA-0802")

        self.db.add_grade("STU-601", "CSA-0801", 95.0, "O", 1)  # 10 pts * 4 cred = 40
        self.db.add_grade("STU-601", "CSA-0802", 85.0, "A+", 1)  # 9 pts * 4 cred = 36

        transcript = self.db.get_student_transcript("STU-601")
        self.assertEqual(len(transcript), 2)

        # Expected GPA = (40 + 36) / 8 = 76 / 8 = 9.5
        gpa = self.db.compute_student_gpa("STU-601")
        self.assertAlmostEqual(gpa, 9.50)


if __name__ == "__main__":
    unittest.main()
