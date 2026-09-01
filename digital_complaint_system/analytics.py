"""Analytics and statistical analysis engine for the Complaint System.

Provides aggregation utilities including pending counts, case-insensitive
status filtering, category frequencies, resolution durations, overdue SLA alerts,
and geographic crime zone threat density modeling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import complaint_manager

PENDING_STATUSES = ("REGISTERED", "ASSIGNED", "IN_PROGRESS", "ESCALATED")
RESOLVED_STATUSES = ("RESOLVED", "CLOSED")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_target_complaints(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """Retrieve target complaints dictionary."""
    if complaints_dict is not None:
        return complaints_dict
    return complaint_manager.get_all_complaints()


def count_pending_complaints(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> int:
    """Count total number of unresolved complaints."""
    store = _get_target_complaints(complaints_dict)
    return sum(1 for rec in store.values() if rec.get("status", "").upper() in PENDING_STATUSES)


def search_complaints_by_status(
    status: str,
    complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Search complaints by status with case-insensitive matching."""
    if not status:
        return []
    target_status = str(status).strip().upper()
    store = _get_target_complaints(complaints_dict)
    return [rec for rec in store.values() if rec.get("status", "").upper() == target_status]


def category_frequency(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, int]:
    """Calculate frequency distribution of complaints across categories."""
    store = _get_target_complaints(complaints_dict)
    frequency: Dict[str, int] = {}
    for record in store.values():
        cat = record.get("category", "Uncategorized")
        frequency[cat] = frequency.get(cat, 0) + 1
    return frequency


def average_resolution_time(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> float:
    """Compute average resolution duration in hours, safely guarding against zero-division."""
    store = _get_target_complaints(complaints_dict)
    durations: List[float] = []

    for record in store.values():
        date_reg_str = record.get("date_registered")
        date_res_str = record.get("date_resolved")
        if date_reg_str and date_res_str:
            try:
                dt_reg = datetime.strptime(date_reg_str, DATETIME_FORMAT)
                dt_res = datetime.strptime(date_res_str, DATETIME_FORMAT)
                diff_hours = (dt_res - dt_reg).total_seconds() / 3600.0
                if diff_hours >= 0:
                    durations.append(diff_hours)
            except (ValueError, TypeError):
                continue

    if not durations:
        return 0.0
    return round(sum(durations) / len(durations), 2)


def overdue_complaints(
    threshold_days: int = 7,
    complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Identify pending complaints that have exceeded the resolution SLA."""
    store = _get_target_complaints(complaints_dict)
    overdue_list: List[Dict[str, Any]] = []
    now = datetime.now()

    for record in store.values():
        if record.get("status", "").upper() in PENDING_STATUSES:
            date_reg_str = record.get("date_registered")
            if date_reg_str:
                try:
                    dt_reg = datetime.strptime(date_reg_str, DATETIME_FORMAT)
                    if (now - dt_reg).days >= threshold_days:
                        overdue_list.append(record)
                except (ValueError, TypeError):
                    continue
    return overdue_list


def zone_crime_statistics(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Analyze crime density, critical violent crimes, and threat levels across municipal zones.

    Calculates dynamic threat score:
      threat_score = (active_critical_crimes * 5) + (active_pending_cases * 1.5)
    and assigns zone threat levels:
      - RED_HOTSPOT: High threat crime area (Red Zone)
      - AMBER_MODERATE: Moderate incident level
      - GREEN_SAFE: Low incidents / majority solved

    Returns:
        Dictionary mapping zone names to threat metrics, coordinate centers, and case lists.
    """
    store = _get_target_complaints(complaints_dict)
    zones_map: Dict[str, Dict[str, Any]] = {}

    # Initialize all standard zones
    for zone_name, (lat, lon) in complaint_manager.ZONE_COORDINATES.items():
        zones_map[zone_name] = {
            "zone_name": zone_name,
            "center": [lat, lon],
            "total_cases": 0,
            "active_pending": 0,
            "active_critical_crimes": 0,
            "solved_cases": 0,
            "threat_score": 0.0,
            "threat_level": "GREEN_SAFE",  # GREEN_SAFE, AMBER_MODERATE, RED_HOTSPOT
        }

    for record in store.values():
        zone = record.get("location", "Downtown Central")
        if zone not in zones_map:
            # Dynamically register unknown zone with record's coordinates
            lat = record.get("latitude", 17.3850)
            lon = record.get("longitude", 78.4867)
            zones_map[zone] = {
                "zone_name": zone,
                "center": [lat, lon],
                "total_cases": 0,
                "active_pending": 0,
                "active_critical_crimes": 0,
                "solved_cases": 0,
                "threat_score": 0.0,
                "threat_level": "GREEN_SAFE",
            }

        z = zones_map[zone]
        z["total_cases"] += 1
        st = record.get("status", "").upper()
        is_critical = record.get("is_critical_crime", False) or record.get("priority", "") == "HIGH"

        if st in RESOLVED_STATUSES:
            z["solved_cases"] += 1
        else:
            z["active_pending"] += 1
            if is_critical:
                z["active_critical_crimes"] += 1

    # Compute Threat Score and Alert Levels
    for z in zones_map.values():
        score = (z["active_critical_crimes"] * 5.0) + (z["active_pending"] * 1.5)
        z["threat_score"] = round(score, 1)

        if z["active_critical_crimes"] >= 2 or score >= 8.0:
            z["threat_level"] = "RED_HOTSPOT"
        elif score >= 3.0:
            z["threat_level"] = "AMBER_MODERATE"
        else:
            z["threat_level"] = "GREEN_SAFE"

    return zones_map
