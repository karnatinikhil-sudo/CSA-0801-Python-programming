"""
Integration and Unit Tests for Capstone Project: Student Academic & Wellness System.
"""

import sys
import unittest
from pathlib import Path

# Add project root and capstone package to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
CAPSTONE_DIR = ROOT_DIR / "08_capstone_project"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(CAPSTONE_DIR))

from database.db_engine import CapstoneDBEngine
from models.student import Student
from models.course import Course
from models.grade_record import GradeRecord
from models.wellness_log import WellnessLog
from services.academic_service import AcademicService
from services.wellness_service import WellnessService
from services.analytics_service import AnalyticsService
from services.report_service import ReportService


class TestCapstoneSystem(unittest.TestCase):

    def setUp(self):
        self.db = CapstoneDBEngine(":memory:")
        self.db.seed_initial_demo_data()
        self.academic = AcademicService(self.db)
        self.wellness = WellnessService(self.db)
        self.analytics = AnalyticsService(self.db)
        self.reports = ReportService(self.db)

    def test_student_and_course_registration(self):
        s = Student("STU-999", "New Student", "new@csa.edu", "AI & ML", 4)
        self.assertTrue(self.academic.register_student(s))

        saved = self.academic.get_student("STU-999")
        self.assertIsNotNone(saved)
        self.assertEqual(saved["full_name"], "New Student")

        c = Course("CSA-9999", "Advanced Quantum Computing", 4, "Dr. Feynman", "Physics")
        self.assertTrue(self.academic.register_course(c))

    def test_grade_and_gpa_calculation(self):
        # STU-104 has grades: 98(O), 95(O), 97.5(O) -> all 10.0 grade points
        gpa, creds = self.academic.calculate_gpa("STU-104")
        self.assertEqual(gpa, 10.0)
        self.assertGreater(creds, 0)

    def test_wellness_scoring_and_burnout_assessment(self):
        # Good balance
        healthy_log = WellnessLog("STU-101", study_hours=4.0, sleep_hours=8.0, stress_level=2, exercise_minutes=45)
        self.assertGreaterEqual(healthy_log.compute_wellness_score(), 80.0)
        self.assertIn("LOW RISK", healthy_log.get_burnout_risk())

        # High risk burnout
        burnout_log = WellnessLog("STU-999", study_hours=12.0, sleep_hours=4.0, stress_level=9, exercise_minutes=0)
        self.assertLess(burnout_log.compute_wellness_score(), 60.0)
        self.assertIn("HIGH RISK", burnout_log.get_burnout_risk())

    def test_executive_analytics_summary(self):
        summary = self.analytics.get_executive_summary()
        self.assertGreaterEqual(summary["total_students"], 5)
        self.assertGreater(summary["average_gpa"], 0.0)
        self.assertIn("grade_distribution", summary)
        self.assertEqual(summary["grade_distribution"]["O"], 7)

    def test_report_card_generation(self):
        report = self.reports.generate_student_report_card("STU-101")
        self.assertIn("Nikhil Karnati", report)
        self.assertIn("CSA-0801", report)
        self.assertIn("Cumulative GPA", report)


if __name__ == "__main__":
    unittest.main()
