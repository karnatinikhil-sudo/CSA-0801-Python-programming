"""
CSA-0801: Python Programming - Capstone Project
Interactive Terminal Application: Student Academic & Wellness Management System
"""

import argparse
import sys
from pathlib import Path

# Add project root and local directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from database.db_engine import CapstoneDBEngine
from models.student import Student
from models.course import Course
from models.grade_record import GradeRecord
from models.wellness_log import WellnessLog
from services.academic_service import AcademicService
from services.wellness_service import WellnessService
from services.analytics_service import AnalyticsService
from services.report_service import ReportService
from gui_app import run_capstone_gui


class CapstoneCLI:
    def __init__(self, db_path: str = "csa_capstone_academic.db"):
        self.db = CapstoneDBEngine(db_path)
        self.db.seed_initial_demo_data()

        self.academic = AcademicService(self.db)
        self.wellness = WellnessService(self.db)
        self.analytics = AnalyticsService(self.db)
        self.reports = ReportService(self.db)

    def print_banner(self):
        print("=" * 72)
        print("  CSA-0801 CAPSTONE: STUDENT ACADEMIC & WELLNESS MANAGEMENT SYSTEM")
        print("=" * 72)

    def display_leaderboard(self):
        print("\n" + "=" * 70)
        print(" COHORT LEADERBOARD & GPA RANKINGS")
        print("=" * 70)
        rankings = self.academic.get_cohort_rankings()
        print(f" {'Rank':<6} | {'Student ID':<12} | {'Full Name':<20} | {'GPA':<6} | {'Credits':<8}")
        print("-" * 70)
        for r in rankings:
            print(f" #{r['rank']:<5} | {r['student_id']:<12} | {r['full_name']:<20} | {r['gpa']:<6.2f} | {r['credits']:<8}")
        print("-" * 70)

    def display_report_card(self, student_id: str):
        card = self.reports.generate_student_report_card(student_id)
        print("\n" + card)

    def display_analytics_summary(self):
        summary = self.analytics.get_executive_summary()
        print("\n" + "=" * 70)
        print(" EXECUTIVE COHORT ANALYTICS & HEALTH SUMMARY")
        print("=" * 70)
        print(f"  * Total Students Enrolled : {summary['total_students']}")
        print(f"  * Average Cohort GPA      : {summary['average_gpa']:.2f} / 10.0")
        if summary.get("top_performer"):
            tp = summary["top_performer"]
            print(f"  * Top Ranked Student      : {tp['full_name']} ({tp['student_id']}) with GPA {tp['gpa']:.2f}")
        print(f"  * Mean Wellness Score     : {summary['average_wellness_score']:.1f} / 100.0")
        print(f"  * Avg Daily Sleep Hours   : {summary['average_sleep_hours']} hrs")
        print(f"  * High Burnout Risk Cases : {summary['high_risk_burnout_count']} students")
        print("\n  Grade Distribution Matrix:")
        for grade, count in summary["grade_distribution"].items():
            print(f"    Grade {grade:<3}: {'#' * (count * 3)} ({count})")
        print("=" * 70)

    def run_menu(self):
        while True:
            self.print_banner()
            print(" 1. View Cohort Leaderboard & GPA Rankings")
            print(" 2. View Individual Student Comprehensive Report Card")
            print(" 3. View Executive Analytics & Wellness Health Summary")
            print(" 4. Register New Student")
            print(" 5. Record Course Grade")
            print(" 6. Log Daily Wellness & Burnout Assessment")
            print(" 7. Export Entire System Data to JSON")
            print(" 8. Launch Desktop Tkinter GUI Application")
            print(" 9. Exit")
            print("=" * 72)

            choice = input("\nSelect an option [1-9]: ").strip()
            if choice == "1":
                self.display_leaderboard()
            elif choice == "2":
                sid = input("Enter Student ID (e.g. STU-101): ").strip()
                self.display_report_card(sid)
            elif choice == "3":
                self.display_analytics_summary()
            elif choice == "4":
                sid = input("Student ID (e.g. STU-106): ").strip()
                name = input("Full Name: ").strip()
                email = input("Email: ").strip()
                dept = input("Department [Computer Science]: ").strip() or "Computer Science"
                try:
                    self.academic.register_student(Student(sid, name, email, dept, 4))
                    print(f"\n[+] Successfully registered student {name} ({sid})!")
                except Exception as e:
                    print(f"\n[-] Error: {e}")
            elif choice == "5":
                sid = input("Student ID: ").strip()
                code = input("Course Code (e.g. CSA-0801): ").strip()
                try:
                    marks = float(input("Marks (0-100): ").strip())
                    sem = int(input("Semester (e.g. 4): ").strip())
                    self.academic.record_grade(GradeRecord(sid, code, marks, sem))
                    print(f"\n[+] Grade recorded successfully!")
                except Exception as e:
                    print(f"\n[-] Error: {e}")
            elif choice == "6":
                sid = input("Student ID: ").strip()
                try:
                    study = float(input("Daily Study Hours: ").strip())
                    sleep = float(input("Daily Sleep Hours: ").strip())
                    stress = int(input("Stress Level (1-10): ").strip())
                    ex = int(input("Exercise Minutes (e.g. 30): ").strip())
                    log = WellnessLog(sid, study, sleep, stress, ex)
                    self.wellness.log_wellness(log)
                    print(f"\n[+] Wellness logged! Score: {log.compute_wellness_score()}/100 ({log.get_burnout_risk()})")
                except Exception as e:
                    print(f"\n[-] Error: {e}")
            elif choice == "7":
                out_path = Path("capstone_export.json")
                self.reports.export_all_to_json(out_path)
                print(f"\n[+] Complete system exported to {out_path.resolve()}")
            elif choice == "8":
                print("\n[+] Launching Capstone Desktop GUI...")
                run_capstone_gui()
            elif choice == "9":
                print("\nExiting CSA-0801 Capstone Suite. Goodbye!")
                break
            else:
                print("\nInvalid selection. Please enter a number 1-9.")

            input("\nPress Enter to continue...")


def run_demo_mode():
    """Non-interactive test run demonstrating all Capstone features."""
    cli = CapstoneCLI(":memory:")
    cli.print_banner()
    cli.display_leaderboard()
    cli.display_report_card("STU-101")
    cli.display_analytics_summary()
    print("\n[OK] Capstone Demo execution completed successfully!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSA-0801 Capstone CLI")
    parser.add_argument("--demo", action="store_true", help="Run automated non-interactive demo")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter desktop GUI directly")
    args = parser.parse_args()

    if args.gui:
        run_capstone_gui()
    elif args.demo:
        run_demo_mode()
    else:
        cli = CapstoneCLI()
        cli.run_menu()
