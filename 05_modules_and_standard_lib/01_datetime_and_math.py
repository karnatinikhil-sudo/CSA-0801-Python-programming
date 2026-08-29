"""
CSA-0801: Python Programming - Module 05
Topic: Standard Library: Datetime, Math, Statistics, and Decimal Precision

Key Concepts Covered:
1. Date arithmetic with `datetime`, `timedelta`, and `timezone`
2. String parsing (`strptime`) and custom formatting (`strftime`)
3. Mathematical computations with the `math` module
4. Descriptive statistics using the `statistics` module
5. High precision financial and GPA calculations with `decimal.Decimal`
"""

import datetime
import math
import statistics
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


def calculate_academic_timeline(start_date_str: str, duration_weeks: int) -> dict[str, Any]:
    """Computes course milestones, exam windows, and remaining time from start date."""
    date_format = "%Y-%m-%d"
    start_date = datetime.datetime.strptime(start_date_str, date_format)

    midterm_date = start_date + datetime.timedelta(weeks=duration_weeks // 2)
    end_date = start_date + datetime.timedelta(weeks=duration_weeks)

    now = datetime.datetime.now()
    days_to_midterm = (midterm_date - now).days
    days_to_end = (end_date - now).days

    return {
        "start_date": start_date.strftime("%A, %d %B %Y"),
        "midterm_date": midterm_date.strftime("%A, %d %B %Y"),
        "end_date": end_date.strftime("%A, %d %B %Y"),
        "days_to_midterm": days_to_midterm,
        "days_to_end": days_to_end,
    }


def compute_cohort_statistics(scores: list[float]) -> dict[str, float]:
    """Computes comprehensive statistical measures on a sample cohort."""
    if not scores:
        return {}

    return {
        "count": len(scores),
        "mean": round(statistics.mean(scores), 2),
        "median": round(statistics.median(scores), 2),
        "stdev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
        "variance": round(statistics.variance(scores), 2) if len(scores) > 1 else 0.0,
        "min": min(scores),
        "max": max(scores),
    }


def decimal_precision_financial_calc(principal: str, rate: str, periods: int) -> Decimal:
    """Uses decimal.Decimal to eliminate floating-point rounding inaccuracies."""
    p = Decimal(principal)
    r = Decimal(rate) / Decimal("100")
    total = p * ((Decimal("1") + r) ** periods)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 5.1 - Datetime, Statistics & High Precision Math")
    print("=" * 60)

    print("\n[1] Academic Semester Timeline & Milestones:")
    timeline = calculate_academic_timeline("2026-08-01", 16)
    print(f"  * Semester Start:    {timeline['start_date']}")
    print(f"  * Midterm Exam Date: {timeline['midterm_date']}")
    print(f"  * Final Exam Date:   {timeline['end_date']}")

    print("\n[2] Cohort Statistical Performance Analysis:")
    scores = [88.5, 92.0, 79.5, 95.0, 68.0, 84.5, 91.0, 76.5, 100.0, 82.0]
    stats = compute_cohort_statistics(scores)
    for k, v in stats.items():
        print(f"  * {k.capitalize():<12}: {v}")

    print("\n[3] Floating-point Inaccuracy vs Decimal Precision:")
    float_sum = 0.1 + 0.1 + 0.1 - 0.3
    decimal_sum = Decimal("0.1") + Decimal("0.1") + Decimal("0.1") - Decimal("0.3")
    print(f"  * Float computation (0.1 + 0.1 + 0.1 - 0.3)   = {float_sum}")
    print(f"  * Decimal computation (Exact financial check) = {decimal_sum}")

    tuition = decimal_precision_financial_calc("15000.00", "4.5", 4)
    print(f"  * Compound Tuition ($15,000 at 4.5% 4 years)  = ${tuition:,.2f}")

    print("\n[OK] Lab 5.1 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
