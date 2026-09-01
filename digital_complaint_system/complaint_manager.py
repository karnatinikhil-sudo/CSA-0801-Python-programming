"""Complaint registration and CRUD operations for the Complaint System.

Maintains in-memory dictionary of complaints, auto-generates Complaint IDs (CMP1001),
handles geographic zoning/coordinates for Chennai, Tamil Nadu crime mapping, and enforces
mandatory high-priority escalation for critical violent crimes (Homicide, Sexual Assault, Robbery).
"""

from datetime import datetime
import random
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

# Critical keywords that trigger automatic HIGH priority escalation
CRITICAL_CRIME_KEYWORDS: Tuple[str, ...] = (
    "murder",
    "homicide",
    "rape",
    "sexual assault",
    "molestation",
    "kidnapping",
    "hostage",
    "armed robbery",
    "gunshot",
    "knife attack",
    "stabbing",
    "extortion",
)

# Chennai Metropolitan Zones and accurate GPS coordinates
ZONE_COORDINATES: Dict[str, Tuple[float, float]] = {
    "T. Nagar": (13.0418, 80.2341),
    "George Town / Parrys": (13.0900, 80.2900),
    "Marina Beach & Triplicane": (13.0500, 80.2824),
    "Anna Nagar": (13.0850, 80.2101),
    "Velachery": (12.9815, 80.2180),
    "OMR IT Corridor": (12.9352, 80.2312),
    "Guindy & Alandur": (13.0067, 80.2024),
    "Adyar & Besant Nagar": (13.0012, 80.2565),
    "Koyambedu": (13.0694, 80.1948),
    "Tambaram": (12.9249, 80.1472),
}

DEFAULT_LOCATION = "T. Nagar"
DEFAULT_COORDS = (13.0418, 80.2341)


def _generate_complaint_id() -> str:
    """Generate the next unique sequential Complaint ID."""
    global _complaint_counter
    _complaint_counter += 1
    new_id = f"CMP{_complaint_counter}"
    while new_id in complaints:
        _complaint_counter += 1
        new_id = f"CMP{_complaint_counter}"
    return new_id


def sync_counter_from_existing() -> None:
    """Synchronize counter based on currently loaded complaints."""
    global _complaint_counter
    max_val = 1000
    for cid in complaints:
        if cid.startswith("CMP") and cid[3:].isdigit():
            val = int(cid[3:])
            if val > max_val:
                max_val = val
    _complaint_counter = max_val


def get_zone_coordinates(zone_name: str) -> Tuple[float, float]:
    """Get latitude and longitude for a given Chennai zone with slight jitter to prevent pin overlap."""
    base = ZONE_COORDINATES.get(zone_name, DEFAULT_COORDS)
    # Small jitter ~ 100-300m
    lat = round(base[0] + random.uniform(-0.005, 0.005), 6)
    lon = round(base[1] + random.uniform(-0.005, 0.005), 6)
    return (lat, lon)


def register_complaint(
    name: str,
    category: str,
    description: str,
    priority: str = DEFAULT_PRIORITY,
    location: str = DEFAULT_LOCATION,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> str:
    """Register a new complaint or criminal incident in Chennai.

    Validates and normalizes inputs. Severe violent crimes (Murder, Rape, Armed Robbery)
    are automatically escalated to HIGH priority for Chennai City Police units.

    Args:
        name: Name of complainant / reporting citizen.
        category: Incident category.
        description: Incident details & landmark description.
        priority: Initial priority level ('LOW', 'MEDIUM', 'HIGH').
        location: Chennai locality / zone name.
        latitude: GPS latitude in Chennai.
        longitude: GPS longitude in Chennai.

    Returns:
        The generated Complaint ID (e.g. 'CMP1001').
    """
    cleaned_name = str(name).strip().title()
    cleaned_category = str(category).strip().title()
    cleaned_description = str(description).strip()
    cleaned_location = str(location).strip() if location else DEFAULT_LOCATION

    if not cleaned_name:
        raise ValueError("Complainant name cannot be empty.")
    if not cleaned_category:
        raise ValueError("Complaint category cannot be empty.")
    if not cleaned_description:
        raise ValueError("Complaint description cannot be empty.")

    # Check for Critical Severe Crimes
    desc_lower = cleaned_description.lower()
    is_critical_crime = (
        category_manager.is_critical_crime_category(cleaned_category)
        or any(keyword in desc_lower for keyword in CRITICAL_CRIME_KEYWORDS)
        or any(keyword in cleaned_category.lower() for keyword in CRITICAL_CRIME_KEYWORDS)
    )

    if is_critical_crime:
        normalized_priority = "HIGH"
    else:
        normalized_priority = str(priority).strip().upper()
        if normalized_priority not in VALID_PRIORITIES:
            normalized_priority = DEFAULT_PRIORITY

    department = category_manager.get_department(cleaned_category)

    # Assign Chennai GPS coordinates
    if latitude is None or longitude is None:
        lat, lon = get_zone_coordinates(cleaned_location)
    else:
        lat, lon = float(latitude), float(longitude)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complaint_id = _generate_complaint_id()

    complaint_record: Dict[str, Any] = {
        "complaint_id": complaint_id,
        "complainant": cleaned_name,
        "category": cleaned_category,
        "department": department,
        "description": cleaned_description,
        "priority": normalized_priority,
        "status": "REGISTERED",
        "assigned_to": None,
        "location": cleaned_location,
        "latitude": lat,
        "longitude": lon,
        "is_critical_crime": is_critical_crime,
        "date_registered": now_str,
        "date_resolved": None,
        "status_history": [("REGISTERED", now_str)],
    }

    complaints[complaint_id] = complaint_record
    return complaint_id


def get_complaint(complaint_id: str) -> Dict[str, Any]:
    """Retrieve single complaint record by ID."""
    if not complaint_id:
        raise InvalidComplaintIDError(str(complaint_id))
    normalized_id = str(complaint_id).strip().upper()
    if normalized_id not in complaints:
        raise InvalidComplaintIDError(normalized_id)
    return complaints[normalized_id]


def get_all_complaints() -> Dict[str, Dict[str, Any]]:
    """Retrieve all complaints in memory."""
    return complaints


def delete_complaint(complaint_id: str) -> bool:
    """Delete a complaint by ID."""
    normalized_id = str(complaint_id).strip().upper()
    if normalized_id not in complaints:
        raise InvalidComplaintIDError(normalized_id)
    del complaints[normalized_id]
    return True


def clear_complaints() -> None:
    """Reset store and counter."""
    global _complaint_counter
    complaints.clear()
    _complaint_counter = 1000
