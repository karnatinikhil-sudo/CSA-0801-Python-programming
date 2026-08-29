"""
ReportService generates formatted ASCII Report Cards, CSV transcripts, and JSON export packages.
"""

import csv
import json
from pathlib import Path
from typing import Any
from database.db_engine import CapstoneDBEngine
from services.academic_service import AcademicService
from services.wellness_service import WellnessService


class ReportService:
    def __init__(self, db: CapstoneDBEngine):
        self.db = db
        self.academic = AcademicService(db)
        self.wellness = WellnessService(db)

    def generate_student_report_card(self, student_id: str) -> str:
        """Generates a formatted report card with academic and wellness summaries."""
        stu = self.academic.get_student(student_id)
        if not stu:
            return f"Error: Student '{student_id}' not found."

        transcript = self.academic.get_student_transcript(student_id)
        gpa, total_credits = self.academic.calculate_gpa(student_id)
        wellness = self.wellness.get_latest_wellness(student_id)

        lines = [
            "+" + "-" * 70 + "+",
            f"|{'ACADEMIC & WELLNESS COMPREHENSIVE DOSSIER':^70}|",
            "+" + "-" * 70 + "+",
            f"| Student ID  : {stu['student_id']:<20} Department : {stu['department']:<23}|",
            f"| Full Name   : {stu['full_name']:<20} Semester   : {stu['semester']:<23}|",
            f"| Email       : {stu['email']:<53}|",
            "+" + "-" * 70 + "+",
            f"|{'COURSE TRANSCRIPT & GRADES':^70}|",
            "+" + "-" * 70 + "+",
            f"| {'Code':<10} | {'Course Title':<28} | {'Cred':<4} | {'Marks':<5} | {'Grade':<5} |",
            "+" + "-" * 70 + "+",
        ]

        for r in transcript:
            lines.append(
                f"| {r['course_code']:<10} | {r['course_title']:<28} | {r['credits']:<4} | {r['marks']:<5.1f} | {r['grade_letter']:<5} |"
            )

        lines.extend([
            "+" + "-" * 70 + "+",
            f"| Cumulative GPA: {gpa:<5.2f} / 10.0   | Total Earned Credits: {total_credits:<16}|",
            "+" + "-" * 70 + "+",
            f"|{'WELLNESS & HEALTH BALANCE INDEX':^70}|",
            "+" + "-" * 70 + "+",
        ])

        if wellness:
            lines.extend([
                f"| Daily Study : {wellness['study_hours']} hrs/day         Daily Sleep : {wellness['sleep_hours']} hrs/night          |",
                f"| Stress Level: {wellness['stress_level']}/10              Exercise    : {wellness['exercise_minutes']} mins/day         |",
                f"| Wellness Score: {wellness['wellness_score']}/100.0        Burnout Risk: {wellness['burnout_risk'][:20]:<20} |",
            ])
        else:
            lines.append(f"|{'No wellness logs recorded yet.':^70}|")

        lines.append("+" + "-" * 70 + "+")
        return "\n".join(lines)

    def export_all_to_json(self, output_file: Path) -> dict[str, Any]:
        """Dumps complete database state to a JSON file."""
        students = self.academic.get_all_students()
        courses = self.academic.get_all_courses()
        rankings = self.academic.get_cohort_rankings()

        payload = {
            "system": "CSA-0801 Capstone Academic & Wellness Management System",
            "total_students": len(students),
            "courses": courses,
            "rankings": rankings,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

        return payload
