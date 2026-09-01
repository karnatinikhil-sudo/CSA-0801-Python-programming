"""Complaint registration and CRUD operations for the Complaint System.

Maintains in-memory dictionary of complaints, auto-generates Complaint IDs (CMP1001),
handles geographic zoning/coordinates for crime mapping, and enforces mandatory
high-priority escalation for critical violent crimes (e.g. Homicide, Sexual Assault, Armed Robbery).
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

# Standard Geographic Zones and baseline GPS coordinates (City Grid)
ZONE_COORDINATES: Dict[str, Tuple[float, float]] = {
    "Downtown Central": (17.3850, 78.4867),
    "Old City Sector": (17.3616, 78.4747),
    "North Industrial Ward": (17.4350, 78.4600),
    "West Tech Corridor": (17.4400, 78.3800),
    "East Suburbs & Highway": (17.3600, 78.5300),
    "South Metro District": (17.3200, 78.4700),
}


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
    """Get latitude and longitude for a given zone with slight jitter to prevent pin stacking."""
    base = ZONE_COORDINATES.get(zone_name, (17.3850, 78.4867))
    # Small jitter ~ 100-300m
    lat = round(base[0] + random.uniform(-0.006, 0.006), 6)
    lon = round(base[1] + random.uniform(-0.006, 0.006), 6)
    return (lat, lon)


def register_complaint(
    name: str,
    category: str,
    description: str,
    priority: str = DEFAULT_PRIORITY,
    location: str = "Downtown Central",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> str:
    """Register a new complaint or criminal incident.

    Validates and normalizes inputs. If the complaint pertains to severe crimes
    (e.g., Murder, Rape, Armed Robbery), it is automatically tagged as critical
    and elevated to HIGH priority for rapid law enforcement response.

    Args:
        name: Name of complainant / reporting citizen.
        category: Incident category.
        description: Incident details & location description.
        priority: Initial priority level ('LOW', 'MEDIUM', 'HIGH').
        location: Geographic municipal zone name.
        latitude: Optional explicit GPS latitude.
        longitude: Optional explicit GPS longitude.

    Returns:
        The generated Complaint ID (e.g. 'CMP1001').
    """
    cleaned_name = str(name).strip().title()
    cleaned_category = str(category).strip().title()
    cleaned_description = str(description).strip()
    cleaned_location = str(location).strip().title() if location else "Downtown Central"

    if not cleaned_name:
        raise ValueError("Complainant name cannot be empty.")
    if not cleaned_category:
        raise ValueError("Complaint category cannot be empty.")
    if not cleaned_description:
        raise ValueError("Complaint description cannot be empty.")

    # Check for Critical Severe Crimes (Rape, Murder, Violent Assault)
    desc_lower = cleaned_description.lower()
    is_critical_crime = (
        category_manager.is_critical_crime_category(cleaned_category)
        or any(keyword in desc_lower for keyword in CRITICAL_CRIME_KEYWORDS)
        or any(keyword in cleaned_category.lower() for keyword in CRITICAL_CRIME_KEYWORDS)
    )

    if is_critical_crime:
        # Mandatory emergency escalation for severe violent crime
        normalized_priority = "HIGH"
    else:
        normalized_priority = str(priority).strip().upper()
        if normalized_priority not in VALID_PRIORITIES:
            normalized_priority = DEFAULT_PRIORITY

    # Route department
    department = category_manager.get_department(cleaned_category)

    # Assign coordinates
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
