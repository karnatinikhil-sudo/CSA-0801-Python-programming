"""Complaint registration and CRUD operations for the Complaint System.

This module maintains the in-memory dictionary of complaints, enforces unique auto-generated
Complaint IDs (e.g. CMP1001), validates input fields, and manages basic complaint retrieval.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import category_manager
from exceptions import InvalidComplaintIDError

# Primary in-memory store: Complaint ID -> Complaint Record Dictionary
complaints: Dict[str, Dict[str, Any]] = {}

# Auto-incrementing identifier counter
_complaint_counter: int = 1000

# Permitted priorities
VALID_PRIORITIES: Tuple[str, ...] = ("LOW", "MEDIUM", "HIGH")
DEFAULT_PRIORITY: str = "MEDIUM"


def _generate_complaint_id() -> str:
    """Generate the next unique sequential Complaint ID.

    Returns:
        A unique identifier string formatted as 'CMPxxxx' (e.g., 'CMP1001').
    """
    global _complaint_counter
    _complaint_counter += 1
    new_id = f"CMP{_complaint_counter}"
    while new_id in complaints:
        _complaint_counter += 1
        new_id = f"CMP{_complaint_counter}"
    return new_id


def sync_counter_from_existing() -> None:
    """Synchronize the internal counter based on currently loaded complaints.

    Ensures newly generated IDs do not collide with records loaded from storage.
    """
    global _complaint_counter
    max_val = 1000
    for cid in complaints:
        if cid.startswith("CMP") and cid[3:].isdigit():
            val = int(cid[3:])
            if val > max_val:
                max_val = val
    _complaint_counter = max_val


def register_complaint(
    name: str,
    category: str,
    description: str,
    priority: str = DEFAULT_PRIORITY,
) -> str:
    """Register a new complaint and store it in the complaints dictionary.

    Validates and normalizes complainant name, category, and description.
    If the provided priority is invalid, safely falls back to 'MEDIUM' instead
    of raising an error. Generates a unique Complaint ID and initializes the
    complaint with status 'REGISTERED'.

    Args:
        name: Name of the citizen/user filing the complaint.
        category: Complaint category (e.g., 'Water Supply', 'Sanitation').
        description: Detailed explanation of the issue.
        priority: Initial priority level ('LOW', 'MEDIUM', 'HIGH'). Defaults to 'MEDIUM'.

    Returns:
        The newly generated unique Complaint ID (e.g., 'CMP1001').

    Raises:
        ValueError: If name, category, or description is empty after stripping whitespace.
    """
    cleaned_name = str(name).strip().title()
    cleaned_category = str(category).strip().title()
    cleaned_description = str(description).strip()

    if not cleaned_name:
        raise ValueError("Complainant name cannot be empty.")
    if not cleaned_category:
        raise ValueError("Complaint category cannot be empty.")
    if not cleaned_description:
        raise ValueError("Complaint description cannot be empty.")

    # Validate and normalize priority (fallback to DEFAULT_PRIORITY if invalid)
    normalized_priority = str(priority).strip().upper()
    if normalized_priority not in VALID_PRIORITIES:
        normalized_priority = DEFAULT_PRIORITY

    # Route department based on category
    department = category_manager.get_department(cleaned_category)

    # Generate timestamp and unique ID
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complaint_id = _generate_complaint_id()

    # Construct complaint record
    complaint_record: Dict[str, Any] = {
        "complaint_id": complaint_id,
        "complainant": cleaned_name,
        "category": cleaned_category,
        "department": department,
        "description": cleaned_description,
        "priority": normalized_priority,
        "status": "REGISTERED",
        "assigned_to": None,
        "date_registered": now_str,
        "date_resolved": None,
        "status_history": [("REGISTERED", now_str)],
    }

    # Store in memory
    complaints[complaint_id] = complaint_record
    return complaint_id


def get_complaint(complaint_id: str) -> Dict[str, Any]:
    """Retrieve a single complaint record by its Complaint ID.

    Args:
        complaint_id: Unique identifier (e.g., 'CMP1001').

    Returns:
        The complaint dictionary containing all fields.

    Raises:
        InvalidComplaintIDError: If the ID does not exist in the store.
    """
    if not complaint_id:
        raise InvalidComplaintIDError(str(complaint_id))

    normalized_id = str(complaint_id).strip().upper()
    if normalized_id not in complaints:
        raise InvalidComplaintIDError(normalized_id)

    return complaints[normalized_id]


def get_all_complaints() -> Dict[str, Dict[str, Any]]:
    """Retrieve all stored complaints.

    Returns:
        The entire dictionary of complaints.
    """
    return complaints


def delete_complaint(complaint_id: str) -> bool:
    """Delete a complaint by its Complaint ID.

    Args:
        complaint_id: Unique identifier of the complaint to remove.

    Returns:
        True if successfully deleted.

    Raises:
        InvalidComplaintIDError: If the complaint ID is not found.
    """
    normalized_id = str(complaint_id).strip().upper()
    if normalized_id not in complaints:
        raise InvalidComplaintIDError(normalized_id)

    del complaints[normalized_id]
    return True


def clear_complaints() -> None:
    """Clear all complaints from memory and reset counter (useful for test isolation)."""
    global _complaint_counter
    complaints.clear()
    _complaint_counter = 1000
