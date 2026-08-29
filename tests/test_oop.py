"""
Unit Tests for Module 03: OOP and Design Patterns.
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


mod3_classes = load_module("03_object_oriented_programming/01_classes_and_objects.py", "m3_classes")
mod3_inherit = load_module("03_object_oriented_programming/02_inheritance_and_polymorphism.py", "m3_inherit")
mod3_dunder = load_module("03_object_oriented_programming/03_encapsulation_and_dunder.py", "m3_dunder")
mod3_patterns = load_module("03_object_oriented_programming/04_design_patterns.py", "m3_patterns")


class TestObjectOrientedProgramming(unittest.TestCase):

    def test_student_class_and_methods(self):
        s = mod3_classes.Student("STU-99", "Test Student", "CS")
        s.update_gpa(8.5)
        self.assertEqual(s.student_id, "STU-99")
        self.assertTrue(s.is_in_good_standing())

        s_from_csv = mod3_classes.Student.from_csv_line("STU-100, John Doe, AI")
        self.assertEqual(s_from_csv.student_id, "STU-100")
        self.assertEqual(s_from_csv.full_name, "John Doe")

        self.assertEqual(mod3_classes.Student.calculate_letter_grade(92), "O")

    def test_inheritance_and_polymorphism(self):
        ug = mod3_inherit.UndergraduateStudent("STU-1", "Alice", "alice@csa.edu", credit_hours=15)
        prof = mod3_inherit.Professor("FAC-1", "Dr. Bob", "bob@csa.edu", courses_taught=2, research_grants=1)
        ta = mod3_inherit.TeachingAssistant("TA-1", "Charlie", "charlie@csa.edu", credit_hours=10, lab_sections=2)

        self.assertEqual(ug.calculate_workload_hours(), 45.0)  # 15 * 3
        self.assertEqual(prof.calculate_workload_hours(), 35.0)  # 2*10 + 1*15
        self.assertEqual(ta.calculate_workload_hours(), 42.0)  # 10*3 + 2*6

        self.assertIn("TeachingAssistant", [c.__name__ for c in mod3_inherit.TeachingAssistant.__mro__])

    def test_encapsulation_and_dunder(self):
        acct = mod3_dunder.BankAccount("Nikhil", 1000.0)
        self.assertEqual(acct.balance, 1000.0)
        acct.deposit(200.0)
        self.assertEqual(acct.balance, 1200.0)

        with self.assertRaises(ValueError):
            acct.withdraw(5000.0)

        v1 = mod3_dunder.GradeVector([70, 80, 90])
        v2 = mod3_dunder.GradeVector([10, 10, 10])
        v3 = v1 + v2
        self.assertEqual(v3.average(), 90.0)
        self.assertTrue(v1 < v3)
        self.assertEqual(len(v3), 3)

    def test_design_patterns(self):
        # Singleton
        c1 = mod3_patterns.SystemConfig("App1", "Prod")
        c2 = mod3_patterns.SystemConfig("App2", "Dev")
        self.assertIs(c1, c2)

        # Factory
        t_course = mod3_patterns.CourseFactory.create_course("theory", "T-101", "Discrete Math", 3)
        l_course = mod3_patterns.CourseFactory.create_course("lab", "L-101", "Python Lab", 2)
        self.assertIsInstance(t_course, mod3_patterns.TheoryCourse)
        self.assertIsInstance(l_course, mod3_patterns.LabCourse)

        # Observer
        bus = mod3_patterns.AcademicEventBus()
        events_received = []
        bus.subscribe("TEST_EVENT", lambda evt, data: events_received.append(data))
        bus.publish("TEST_EVENT", "Payload 1")
        self.assertEqual(events_received, ["Payload 1"])


if __name__ == "__main__":
    unittest.main()
