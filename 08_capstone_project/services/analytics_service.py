"""
AnalyticsService computes statistical metrics, grade distributions, and correlations
between study habits, sleep, and GPA performance.
"""

import statistics
from typing import Any
from database.db_engine import CapstoneDBEngine
from services.academic_service import AcademicService
from services.wellness_service import WellnessService


class AnalyticsService:
    def __init__(self, db: CapstoneDBEngine):
        self.db = db
        self.academic = AcademicService(db)
        self.wellness = WellnessService(db)

    def get_grade_distribution(self) -> dict[str, int]:
        """Calculates total distribution of letter grades (O, A+, A, B+, B, C, F)."""
        query = "SELECT grade_letter, COUNT(*) as count FROM capstone_grades GROUP BY grade_letter;"
        dist = {"O": 0, "A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "F": 0}
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            for r in rows:
                if r["grade_letter"] in dist:
                    dist[r["grade_letter"]] = r["count"]
        return dist

    def get_executive_summary(self) -> dict[str, Any]:
        """Produces a holistic dashboard report combining academic and wellness KPIs."""
        rankings = self.academic.get_cohort_rankings()
        gpa_list = [r["gpa"] for r in rankings if r["gpa"] > 0]

        wellness_records = self.wellness.get_cohort_wellness_overview()
        wellness_scores = [w["wellness_score"] for w in wellness_records]
        study_hours = [w["study_hours"] for w in wellness_records]
        sleep_hours = [w["sleep_hours"] for w in wellness_records]

        high_risk_count = sum(1 for w in wellness_records if "HIGH RISK" in w["burnout_risk"])

        return {
            "total_students": len(rankings),
            "average_gpa": round(statistics.mean(gpa_list), 2) if gpa_list else 0.0,
            "top_performer": rankings[0] if rankings else None,
            "grade_distribution": self.get_grade_distribution(),
            "average_wellness_score": round(statistics.mean(wellness_scores), 1) if wellness_scores else 0.0,
            "average_study_hours": round(statistics.mean(study_hours), 1) if study_hours else 0.0,
            "average_sleep_hours": round(statistics.mean(sleep_hours), 1) if sleep_hours else 0.0,
            "high_risk_burnout_count": high_risk_count,
        }
