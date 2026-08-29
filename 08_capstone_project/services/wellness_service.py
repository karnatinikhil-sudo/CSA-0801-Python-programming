"""
WellnessService manages student physical, mental, and workload health tracking.
"""

from typing import Any, Optional
from database.db_engine import CapstoneDBEngine
from models.wellness_log import WellnessLog


class WellnessService:
    def __init__(self, db: CapstoneDBEngine):
        self.db = db

    def log_wellness(self, log: WellnessLog) -> bool:
        score = log.compute_wellness_score()
        risk = log.get_burnout_risk()
        query = """
        INSERT INTO capstone_wellness
        (student_id, study_hours, sleep_hours, stress_level, exercise_minutes, water_intake_liters, wellness_score, burnout_risk)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self.db.transaction() as cur:
            cur.execute(query, (
                log.student_id, log.study_hours, log.sleep_hours,
                log.stress_level, log.exercise_minutes, log.water_intake_liters,
                score, risk
            ))
            return True

    def get_latest_wellness(self, student_id: str) -> Optional[dict[str, Any]]:
        query = """
        SELECT * FROM capstone_wellness
        WHERE student_id = ?
        ORDER BY id DESC LIMIT 1;
        """
        with self.db.get_connection() as conn:
            row = conn.execute(query, (student_id,)).fetchone()
            return dict(row) if row else None

    def get_cohort_wellness_overview(self) -> list[dict[str, Any]]:
        query = """
        SELECT
            w.student_id, s.full_name,
            w.study_hours, w.sleep_hours, w.stress_level,
            w.exercise_minutes, w.wellness_score, w.burnout_risk, w.logged_at
        FROM capstone_wellness w
        JOIN capstone_students s ON w.student_id = s.student_id
        GROUP BY w.student_id
        HAVING w.id = MAX(w.id)
        ORDER BY w.wellness_score DESC;
        """
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]
