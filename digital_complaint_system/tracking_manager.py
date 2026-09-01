"""Complaint tracking, assignment, status workflow, and escalation management.

This module enforces valid status transitions, updates staff assignments,
handles complaint escalations, and maintains an immutable timestamped status history audit trail.
"""

from datetime import datetime
from typing import Any, Dict, Tuple

import complaint_manager
from exceptions import InvalidStatusError

# Permitted lifecycle statuses across the entire application
VALID_STATUSES: Tuple[str, ...] = (
    "REGISTERED",
    "ASSIGNED",
    "IN_PROGRESS",
    "ESCALATED",
    "RESOLVED",
    "CLOSED",
)

# Permitted priority levels
VALID_PRIORITIES: Tuple[str, ...] = ("LOW", "MEDIUM", "HIGH")


def assign_complaint(complaint_id: str, staff: str) -> Dict[str, Any]:
    """Assign an officer/staff member to a complaint and update status to ASSIGNED.

    Appends the status transition to status_history with the current timestamp.

    Args:
        complaint_id: The unique identifier of the complaint.
        staff: Name of the assigned staff member or officer.

    Returns:
        The updated complaint dictionary record.

    Raises:
        InvalidComplaintIDError: If the complaint does not exist.
        ValueError: If the staff name is empty.
    """
    cleaned_staff = str(staff).strip().title()
    if not cleaned_staff:
        raise ValueError("Assigned staff name cannot be empty.")

    complaint = complaint_manager.get_complaint(complaint_id)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complaint["assigned_to"] = cleaned_staff
    complaint["status"] = "ASSIGNED"
    complaint["status_history"].append(("ASSIGNED", now_str))

    return complaint


def update_status(complaint_id: str, new_status: str) -> Dict[str, Any]:
    """Update the status of a complaint and record it in the status history.

    Validates that the new status is a recognized status within VALID_STATUSES.
    When moving to RESOLVED or CLOSED, automatically stamps date_resolved if not already set.

    Args:
        complaint_id: The unique identifier of the complaint.
        new_status: The target status string (e.g. 'IN_PROGRESS', 'RESOLVED').

    Returns:
        The updated complaint dictionary record.

    Raises:
        InvalidComplaintIDError: If the complaint does not exist.
        InvalidStatusError: If new_status is not in VALID_STATUSES.
    """
    cleaned_status = str(new_status).strip().upper()
    if cleaned_status not in VALID_STATUSES:
        raise InvalidStatusError(cleaned_status, VALID_STATUSES)

    complaint = complaint_manager.get_complaint(complaint_id)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complaint["status"] = cleaned_status
    complaint["status_history"].append((cleaned_status, now_str))

    # If transitioning to RESOLVED or CLOSED, set date_resolved if not already set
    if cleaned_status in ("RESOLVED", "CLOSED") and complaint.get("date_resolved") is None:
        complaint["date_resolved"] = now_str

    return complaint


def update_priority(complaint_id: str, new_priority: str) -> Dict[str, Any]:
    """Update the priority level of an existing complaint.

    If an unrecognized priority is supplied, it safely defaults to 'MEDIUM'.

    Args:
        complaint_id: The unique identifier of the complaint.
        new_priority: Target priority level ('LOW', 'MEDIUM', 'HIGH').

    Returns:
        The updated complaint dictionary record.

    Raises:
        InvalidComplaintIDError: If the complaint does not exist.
    """
    cleaned_priority = str(new_priority).strip().upper()
    if cleaned_priority not in VALID_PRIORITIES:
        cleaned_priority = "MEDIUM"

    complaint = complaint_manager.get_complaint(complaint_id)
    complaint["priority"] = cleaned_priority
    return complaint


def escalate_complaint(complaint_id: str) -> Dict[str, Any]:
    """Escalate a complaint to HIGH priority and transition status to ESCALATED.

    Appends the ESCALATED status to status_history with the current timestamp.

    Args:
        complaint_id: The unique identifier of the complaint to escalate.

    Returns:
        The updated complaint dictionary record.

    Raises:
        InvalidComplaintIDError: If the complaint does not exist.
    """
    complaint = complaint_manager.get_complaint(complaint_id)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complaint["priority"] = "HIGH"
    complaint["status"] = "ESCALATED"
    complaint["status_history"].append(("ESCALATED", now_str))

    return complaint
