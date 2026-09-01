"""Analytics and statistical analysis engine for the Complaint System.

This module provides aggregation utilities including pending counts, case-insensitive
status filtering, category frequency analysis, resolution duration calculations,
and overdue SLA breach detection.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import complaint_manager

# Pending status definition
PENDING_STATUSES = ("REGISTERED", "ASSIGNED", "IN_PROGRESS", "ESCALATED")
RESOLVED_STATUSES = ("RESOLVED", "CLOSED")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _get_target_complaints(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """Retrieve target complaints dictionary, defaulting to global complaint store."""
    if complaints_dict is not None:
        return complaints_dict
    return complaint_manager.get_all_complaints()


def count_pending_complaints(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> int:
    """Count total number of unresolved/pending complaints.

    Pending complaints are those in 'REGISTERED', 'ASSIGNED', 'IN_PROGRESS', or 'ESCALATED' status.

    Args:
        complaints_dict: Optional dictionary of complaints to evaluate.

    Returns:
        Integer count of pending complaints.
    """
    store = _get_target_complaints(complaints_dict)
    count = 0
    for record in store.values():
        if record.get("status", "").upper() in PENDING_STATUSES:
            count += 1
    return count


def search_complaints_by_status(
    status: str,
    complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Search and filter complaints by status using case-insensitive matching.

    This function safely handles unknown or mismatched statuses by returning an
    empty list instead of raising an exception.

    Args:
        status: The target status to search for (e.g. 'registered', 'RESOLVED').
        complaints_dict: Optional dictionary of complaints to evaluate.

    Returns:
        List of matching complaint record dictionaries, or an empty list if no matches exist.
    """
    if not status:
        return []

    target_status = str(status).strip().upper()
    store = _get_target_complaints(complaints_dict)
    matches: List[Dict[str, Any]] = []

    for record in store.values():
        if record.get("status", "").upper() == target_status:
            matches.append(record)

    return matches


def category_frequency(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, int]:
    """Calculate the frequency distribution of complaints across categories.

    Args:
        complaints_dict: Optional dictionary of complaints to evaluate.

    Returns:
        Dictionary mapping category names to their respective complaint counts.
    """
    store = _get_target_complaints(complaints_dict)
    frequency: Dict[str, int] = {}

    for record in store.values():
        cat = record.get("category", "Uncategorized")
        frequency[cat] = frequency.get(cat, 0) + 1

    return frequency


def average_resolution_time(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> float:
    """Compute the average resolution time in hours for all resolved complaints.

    Safely handles scenarios with zero resolved complaints by returning 0.0 without
    raising a ZeroDivisionError.

    Args:
        complaints_dict: Optional dictionary of complaints to evaluate.

    Returns:
        Average resolution time in hours as a float rounded to 2 decimal places (or 0.0).
    """
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
    """Identify pending complaints that have exceeded the resolution threshold.

    Args:
        threshold_days: Number of days beyond which an unresolved complaint is considered overdue.
        complaints_dict: Optional dictionary of complaints to evaluate.

    Returns:
        List of overdue complaint records.
    """
    store = _get_target_complaints(complaints_dict)
    overdue_list: List[Dict[str, Any]] = []
    now = datetime.now()

    for record in store.values():
        if record.get("status", "").upper() in PENDING_STATUSES:
            date_reg_str = record.get("date_registered")
            if date_reg_str:
                try:
                    dt_reg = datetime.strptime(date_reg_str, DATETIME_FORMAT)
                    elapsed_days = (now - dt_reg).days
                    if elapsed_days >= threshold_days:
                        overdue_list.append(record)
                except (ValueError, TypeError):
                    continue

    return overdue_list
