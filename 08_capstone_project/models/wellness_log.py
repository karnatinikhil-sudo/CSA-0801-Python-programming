"""
WellnessLog entity for tracking student study balance, sleep, stress, and wellness health index.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WellnessLog:
    student_id: str
    study_hours: float
    sleep_hours: float
    stress_level: int  # Scale 1 (Minimal) to 10 (High)
    exercise_minutes: int = 0
    water_intake_liters: float = 2.0
    id: Optional[int] = None
    logged_at: Optional[str] = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def compute_wellness_score(self) -> float:
        """
        Calculates holistic wellness score out of 100 based on health & productivity metrics.
        - Optimal Sleep: 7 - 9 hrs (30 pts)
        - Moderate Stress: <= 4 (30 pts)
        - Study Balance: <= 8 hrs/day (20 pts)
        - Physical Activity: >= 30 mins (20 pts)
        """
        score = 0.0

        # Sleep score (Max 30)
        if 7.0 <= self.sleep_hours <= 9.0:
            score += 30.0
        elif 6.0 <= self.sleep_hours < 7.0 or 9.0 < self.sleep_hours <= 10.0:
            score += 20.0
        else:
            score += 10.0

        # Stress score (Max 30, lower stress is better)
        stress_pts = max(0.0, 30.0 - (self.stress_level - 1) * 3.0)
        score += stress_pts

        # Study balance (Max 20)
        if 2.0 <= self.study_hours <= 6.0:
            score += 20.0
        elif self.study_hours <= 8.0:
            score += 15.0
        else:
            score += 8.0  # Risk of overworking

        # Exercise (Max 20)
        if self.exercise_minutes >= 30:
            score += 20.0
        elif self.exercise_minutes >= 15:
            score += 12.0
        else:
            score += 5.0

        return round(min(100.0, score), 1)

    def get_burnout_risk(self) -> str:
        """Categorizes student burnout risk based on metrics."""
        if self.stress_level >= 8 or self.sleep_hours < 5.0 or self.study_hours > 10.0:
            return "HIGH RISK - Immediate rest & counseling advised"
        elif self.stress_level >= 6 or self.sleep_hours < 6.5:
            return "MODERATE RISK - Balance study and sleep schedule"
        else:
            return "LOW RISK - Healthy academic lifestyle"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "student_id": self.student_id,
            "study_hours": self.study_hours,
            "sleep_hours": self.sleep_hours,
            "stress_level": self.stress_level,
            "exercise_minutes": self.exercise_minutes,
            "water_intake_liters": self.water_intake_liters,
            "wellness_score": self.compute_wellness_score(),
            "burnout_risk": self.get_burnout_risk(),
            "logged_at": self.logged_at,
        }
