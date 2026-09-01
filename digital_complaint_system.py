"""Digital Complaint Registration and Tracking System (Single-File Distribution - Chennai Edition).

A comprehensive Python 3 console application for public service and crime tracking across Chennai,
category-to-department routing, lifecycle tracking, escalation, statistical analytics,
plain-text reporting, and CSV data persistence.

Python Standard Library only (Python 3.9+). Zero external dependencies.
"""

import csv
from datetime import datetime
import json
import os
import random
import sys
import tempfile
from typing import Any, Dict, List, Optional, Set, Tuple
import unittest

# =============================================================================
# 1. CUSTOM EXCEPTION HIERARCHY
# =============================================================================


class ComplaintSystemError(Exception):
    """Base exception class for all errors originating within the Complaint System."""

    def __init__(self, message: str = "An error occurred in the Complaint System.") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class InvalidComplaintIDError(ComplaintSystemError):
    """Exception raised when a specified Complaint ID does not exist or is invalid."""

    def __init__(self, complaint_id: str, message: Optional[str] = None) -> None:
        self.complaint_id = complaint_id
        if message is None:
            message = f"Invalid or non-existent Complaint ID: '{complaint_id}'."
        super().__init__(message)


class InvalidStatusError(ComplaintSystemError):
    """Exception raised when an unsupported or invalid status transition is requested."""

    def __init__(
        self,
        status: str,
        valid_statuses: Optional[Tuple[str, ...]] = None,
        message: Optional[str] = None,
    ) -> None:
        self.status = status
        self.valid_statuses = valid_statuses
        if message is None:
            if valid_statuses:
                message = (
                    f"Invalid status: '{status}'. "
                    f"Must be one of: {', '.join(valid_statuses)}."
                )
            else:
                message = f"Invalid status: '{status}'."
        super().__init__(message)


class DuplicateComplaintError(ComplaintSystemError):
    """Exception raised when an attempt is made to register or overwrite a duplicate complaint."""

    def __init__(self, complaint_id: str, message: Optional[str] = None) -> None:
        self.complaint_id = complaint_id
        if message is None:
            message = f"Duplicate complaint detected for ID: '{complaint_id}'."
        super().__init__(message)


# =============================================================================
# 2. CATEGORY & DEPARTMENT MANAGEMENT
# =============================================================================

categories: Set[str] = set()
category_department_map: Dict[str, str] = {}
DEFAULT_DEPARTMENT: str = "General Administration"

CRITICAL_CRIME_CATEGORIES: Tuple[str, ...] = (
    "Homicide & Murder",
    "Sexual Assault & Harassment",
    "Armed Robbery & Gang Crime",
    "Kidnapping & Human Trafficking",
    "Violent Assault & Battery",
)

_DEFAULT_MAPPINGS: Dict[str, str] = {
    "Homicide & Murder": "Special Crime Investigation & Homicide Unit",
    "Sexual Assault & Harassment": "Women & Child Protection Cell",
    "Armed Robbery & Gang Crime": "Anti-Robbery & Special Operations",
    "Kidnapping & Human Trafficking": "Anti-Human Trafficking & Rescue Unit",
    "Violent Assault & Battery": "Municipal Police & Law Enforcement",
    "Cyber Crime & Fraud": "Cyber Crime Investigation Cell",
    "Public Safety": "Municipal Police & Safety",
    "Public Safety & Weapons": "Municipal Police & Safety",
    "Water Supply": "Water Works Department",
    "Electricity": "Power & Electricity Department",
    "Sanitation": "Public Health & Sanitation",
    "Roads & Infrastructure": "Public Works Department",
    "Billing & Accounts": "Finance & Revenue Department",
}


def initialize_categories() -> None:
    """Populate default categories and departmental mappings."""
    global categories, category_department_map
    categories.clear()
    category_department_map.clear()
    for cat, dept in _DEFAULT_MAPPINGS.items():
        categories.add(cat)
        category_department_map[cat] = dept


initialize_categories()


def add_category(category_name: str, department_name: str) -> None:
    """Add a new complaint category and map it to a responsible department."""
    cleaned_category = category_name.strip().title()
    cleaned_department = department_name.strip().title()

    if not cleaned_category:
        raise ValueError("Category name cannot be empty.")
    if not cleaned_department:
        raise ValueError("Department name cannot be empty.")

    categories.add(cleaned_category)
    category_department_map[cleaned_category] = cleaned_department


def list_categories() -> List[str]:
    """Retrieve an alphabetically sorted list of all active categories."""
    return sorted(list(categories))


def get_department(category_name: str) -> str:
    """Look up the responsible department for a given complaint category."""
    cleaned = category_name.strip().title()
    return category_department_map.get(cleaned, DEFAULT_DEPARTMENT)


def is_critical_crime_category(category_name: str) -> bool:
    """Check if category is a critical high-priority violent crime."""
    cleaned = category_name.strip().title()
    return cleaned in [c.title() for c in CRITICAL_CRIME_CATEGORIES]


def get_all_category_mappings() -> Dict[str, str]:
    """Retrieve a copy of all category-to-department mappings."""
    return dict(category_department_map)


# =============================================================================
# 3. COMPLAINT MANAGER & DATA STORE (CHENNAI METROPOLITAN GRID)
# =============================================================================

complaints: Dict[str, Dict[str, Any]] = {}
_complaint_counter: int = 1000

VALID_PRIORITIES: Tuple[str, ...] = ("LOW", "MEDIUM", "HIGH")
DEFAULT_PRIORITY: str = "MEDIUM"

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

# Chennai Metropolitan Zones with accurate GPS coordinates
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
    """Generate the next unique sequential Complaint ID (CMPxxxx)."""
    global _complaint_counter
    _complaint_counter += 1
    new_id = f"CMP{_complaint_counter}"
    while new_id in complaints:
        _complaint_counter += 1
        new_id = f"CMP{_complaint_counter}"
    return new_id


def sync_counter_from_existing() -> None:
    """Synchronize the internal counter based on currently loaded complaints."""
    global _complaint_counter
    max_val = 1000
    for cid in complaints:
        if cid.startswith("CMP") and cid[3:].isdigit():
            val = int(cid[3:])
            if val > max_val:
                max_val = val
    _complaint_counter = max_val


def get_zone_coordinates(zone_name: str) -> Tuple[float, float]:
    """Get latitude and longitude for a given Chennai zone."""
    base = ZONE_COORDINATES.get(zone_name, DEFAULT_COORDS)
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
    """Register a new complaint or criminal incident in Chennai."""
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

    desc_lower = cleaned_description.lower()
    is_critical_crime = (
        is_critical_crime_category(cleaned_category)
        or any(keyword in desc_lower for keyword in CRITICAL_CRIME_KEYWORDS)
        or any(keyword in cleaned_category.lower() for keyword in CRITICAL_CRIME_KEYWORDS)
    )

    if is_critical_crime:
        normalized_priority = "HIGH"
    else:
        normalized_priority = str(priority).strip().upper()
        if normalized_priority not in VALID_PRIORITIES:
            normalized_priority = DEFAULT_PRIORITY

    department = get_department(cleaned_category)

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
    """Retrieve a single complaint record by its Complaint ID."""
    if not complaint_id:
        raise InvalidComplaintIDError(str(complaint_id))

    normalized_id = str(complaint_id).strip().upper()
    if normalized_id not in complaints:
        raise InvalidComplaintIDError(normalized_id)

    return complaints[normalized_id]


def get_all_complaints() -> Dict[str, Dict[str, Any]]:
    """Retrieve all stored complaints."""
    return complaints


def delete_complaint(complaint_id: str) -> bool:
    """Delete a complaint by its Complaint ID."""
    normalized_id = str(complaint_id).strip().upper()
    if normalized_id not in complaints:
        raise InvalidComplaintIDError(normalized_id)

    del complaints[normalized_id]
    return True


def clear_complaints() -> None:
    """Clear all complaints from memory and reset counter."""
    global _complaint_counter
    complaints.clear()
    _complaint_counter = 1000


# =============================================================================
# 4. TRACKING MANAGER & LIFECYCLE MANAGEMENT
# =============================================================================

VALID_STATUSES: Tuple[str, ...] = (
    "REGISTERED",
    "ASSIGNED",
    "IN_PROGRESS",
    "ESCALATED",
    "RESOLVED",
    "CLOSED",
)


def assign_complaint(complaint_id: str, staff: str) -> Dict[str, Any]:
    """Assign an officer/staff member to a complaint and update status to ASSIGNED."""
    cleaned_staff = str(staff).strip().title()
    if not cleaned_staff:
        raise ValueError("Assigned staff name cannot be empty.")

    complaint = get_complaint(complaint_id)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complaint["assigned_to"] = cleaned_staff
    complaint["status"] = "ASSIGNED"
    complaint["status_history"].append(("ASSIGNED", now_str))
    return complaint


def update_status(complaint_id: str, new_status: str) -> Dict[str, Any]:
    """Update the status of a complaint and append to the status history."""
    cleaned_status = str(new_status).strip().upper()
    if cleaned_status not in VALID_STATUSES:
        raise InvalidStatusError(cleaned_status, VALID_STATUSES)

    complaint = get_complaint(complaint_id)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complaint["status"] = cleaned_status
    complaint["status_history"].append((cleaned_status, now_str))

    if cleaned_status in ("RESOLVED", "CLOSED") and complaint.get("date_resolved") is None:
        complaint["date_resolved"] = now_str

    return complaint


def update_priority(complaint_id: str, new_priority: str) -> Dict[str, Any]:
    """Update the priority level of an existing complaint."""
    cleaned_priority = str(new_priority).strip().upper()
    if cleaned_priority not in VALID_PRIORITIES:
        cleaned_priority = "MEDIUM"

    complaint = get_complaint(complaint_id)
    complaint["priority"] = cleaned_priority
    return complaint


def escalate_complaint(complaint_id: str) -> Dict[str, Any]:
    """Escalate a complaint to HIGH priority and transition status to ESCALATED."""
    complaint = get_complaint(complaint_id)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complaint["priority"] = "HIGH"
    complaint["status"] = "ESCALATED"
    complaint["status_history"].append(("ESCALATED", now_str))
    return complaint


# =============================================================================
# 5. ANALYTICS & STATISTICAL ENGINE
# =============================================================================

PENDING_STATUSES = ("REGISTERED", "ASSIGNED", "IN_PROGRESS", "ESCALATED")
RESOLVED_STATUSES = ("RESOLVED", "CLOSED")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def count_pending_complaints(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> int:
    """Count total number of unresolved/pending complaints."""
    store = complaints_dict if complaints_dict is not None else complaints
    return sum(1 for rec in store.values() if rec.get("status", "").upper() in PENDING_STATUSES)


def search_complaints_by_status(
    status: str,
    complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Search and filter complaints by status using case-insensitive matching."""
    if not status:
        return []
    target_status = str(status).strip().upper()
    store = complaints_dict if complaints_dict is not None else complaints
    return [rec for rec in store.values() if rec.get("status", "").upper() == target_status]


def category_frequency(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, int]:
    """Calculate frequency distribution of complaints across categories."""
    store = complaints_dict if complaints_dict is not None else complaints
    freq: Dict[str, int] = {}
    for rec in store.values():
        cat = rec.get("category", "Uncategorized")
        freq[cat] = freq.get(cat, 0) + 1
    return freq


def average_resolution_time(complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None) -> float:
    """Compute average resolution time in hours, returning 0.0 if no resolved records."""
    store = complaints_dict if complaints_dict is not None else complaints
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
    """Identify pending complaints that have exceeded the resolution threshold."""
    store = complaints_dict if complaints_dict is not None else complaints
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
    """Analyze Chennai crime density, critical violent crimes, and threat levels."""
    store = complaints_dict if complaints_dict is not None else complaints
    zones_map: Dict[str, Dict[str, Any]] = {}

    for zone_name, (lat, lon) in ZONE_COORDINATES.items():
        zones_map[zone_name] = {
            "zone_name": zone_name,
            "center": [lat, lon],
            "total_cases": 0,
            "active_pending": 0,
            "active_critical_crimes": 0,
            "solved_cases": 0,
            "threat_score": 0.0,
            "threat_level": "GREEN_SAFE",
        }

    for record in store.values():
        zone = record.get("location", DEFAULT_LOCATION)
        if zone not in zones_map:
            lat = record.get("latitude", DEFAULT_COORDS[0])
            lon = record.get("longitude", DEFAULT_COORDS[1])
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


# =============================================================================
# 6. REPORTS GENERATION
# =============================================================================


def generate_complaint_report(complaint_id: str) -> str:
    """Generate a detailed plain-text report for a single complaint."""
    record = get_complaint(complaint_id)

    cid = record.get("complaint_id", "N/A")
    name = record.get("complainant", "Unknown")
    cat = record.get("category", "Unspecified")
    dept = record.get("department", "Unassigned")
    loc = record.get("location", "Chennai City")
    desc = record.get("description", "No description provided.")
    priority = record.get("priority", "MEDIUM")
    status = record.get("status", "REGISTERED")
    assigned_to = record.get("assigned_to") or "Unassigned"
    date_reg = record.get("date_registered", "N/A")
    date_res = record.get("date_resolved") or "N/A (Pending)"
    history = record.get("status_history", [])

    lines = [
        "=" * 64,
        f"       COMPLAINT DETAIL REPORT - {cid}",
        "=" * 64,
        f" Complaint ID     : {cid}",
        f" Complainant Name : {name}",
        f" Category         : {cat}",
        f" Department       : {dept}",
        f" Location / Zone  : {loc}",
        f" Priority Level   : {priority}",
        f" Current Status   : {status}",
        f" Assigned Officer : {assigned_to}",
        f" Date Registered  : {date_reg}",
        f" Date Resolved    : {date_res}",
        "-" * 64,
        " Description:",
        f"   {desc}",
        "-" * 64,
        " Lifecycle Status History:",
    ]

    if not history:
        lines.append("   (No status history available)")
    else:
        for idx, item in enumerate(history, start=1):
            if isinstance(item, (tuple, list)) and len(item) == 2:
                st, ts = item
                lines.append(f"   [{idx}] {st:<14} -> Timestamp: {ts}")
            else:
                lines.append(f"   [{idx}] {item}")

    lines.append("=" * 64)
    return "\n".join(lines)


def generate_summary_report() -> str:
    """Generate a high-level summary report of all complaints."""
    total_count = len(complaints)
    pending_count = count_pending_complaints(complaints)
    resolved_count = total_count - pending_count
    avg_res_time = average_resolution_time(complaints)
    cat_freq = category_frequency(complaints)

    status_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for record in complaints.values():
        st = record.get("status", "UNKNOWN").upper()
        status_counts[st] = status_counts.get(st, 0) + 1
        pr = record.get("priority", "MEDIUM").upper()
        priority_counts[pr] = priority_counts.get(pr, 0) + 1

    lines = [
        "=" * 64,
        "   CHENNAI DIGITAL COMPLAINT SYSTEM - EXECUTIVE SUMMARY",
        "=" * 64,
        f" Total Incidents Registered  : {total_count}",
        f" Active / In-Progress        : {pending_count}",
        f" Solved / Closed             : {resolved_count}",
        f" Average Resolution Time     : {avg_res_time:.2f} hours",
        "-" * 64,
        " Breakdown by Status:",
    ]

    if not status_counts:
        lines.append("   (No complaints registered yet)")
    else:
        for st, count in sorted(status_counts.items()):
            lines.append(f"   - {st:<16}: {count}")

    lines.append("-" * 64)
    lines.append(" Breakdown by Priority:")
    for pr, count in priority_counts.items():
        lines.append(f"   - {pr:<16}: {count}")

    lines.append("-" * 64)
    lines.append(" Breakdown by Category:")
    if not cat_freq:
        lines.append("   (No categories recorded)")
    else:
        for cat, count in sorted(cat_freq.items()):
            dept = get_department(cat)
            lines.append(f"   - {cat:<26} ({dept}): {count}")

    lines.append("=" * 64)
    return "\n".join(lines)


# =============================================================================
# 7. CSV PERSISTENCE FILE HANDLER
# =============================================================================

DEFAULT_COMPLAINTS_FILE: str = os.path.join("data", "complaints.csv")
CSV_FIELDNAMES = [
    "complaint_id",
    "complainant",
    "category",
    "department",
    "description",
    "priority",
    "status",
    "assigned_to",
    "location",
    "latitude",
    "longitude",
    "is_critical_crime",
    "date_registered",
    "date_resolved",
    "status_history",
]


def save_complaints_to_csv(
    filepath: str = DEFAULT_COMPLAINTS_FILE,
    complaints_dict: Optional[Dict[str, Dict[str, Any]]] = None,
) -> bool:
    """Save complaints data to a CSV file."""
    if complaints_dict is None:
        complaints_dict = complaints

    try:
        parent_dir = os.path.dirname(filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

            for record in complaints_dict.values():
                history_json = json.dumps(record.get("status_history", []))
                row = {
                    "complaint_id": record.get("complaint_id", ""),
                    "complainant": record.get("complainant", ""),
                    "category": record.get("category", ""),
                    "department": record.get("department", ""),
                    "description": record.get("description", ""),
                    "priority": record.get("priority", "MEDIUM"),
                    "status": record.get("status", "REGISTERED"),
                    "assigned_to": record.get("assigned_to") or "",
                    "location": record.get("location", DEFAULT_LOCATION),
                    "latitude": record.get("latitude", DEFAULT_COORDS[0]),
                    "longitude": record.get("longitude", DEFAULT_COORDS[1]),
                    "is_critical_crime": "1" if record.get("is_critical_crime") else "0",
                    "date_registered": record.get("date_registered", ""),
                    "date_resolved": record.get("date_resolved") or "",
                    "status_history": history_json,
                }
                writer.writerow(row)
        return True

    except (OSError, IOError) as err:
        print(f"[File Handler Error] Could not save complaints to '{filepath}': {err}")
        return False


def load_complaints_from_csv(
    filepath: str = DEFAULT_COMPLAINTS_FILE,
) -> Dict[str, Dict[str, Any]]:
    """Load complaints data from a CSV file into memory."""
    if not os.path.exists(filepath):
        return complaints

    loaded_records: Dict[str, Dict[str, Any]] = {}

    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cid = row.get("complaint_id", "").strip().upper()
                if not cid:
                    continue

                history_raw = row.get("status_history", "[]")
                try:
                    history_list = json.loads(history_raw)
                    history = [(item[0], item[1]) for item in history_list if len(item) == 2]
                except (json.JSONDecodeError, TypeError, IndexError):
                    history = [("REGISTERED", row.get("date_registered", ""))]

                assigned = row.get("assigned_to", "").strip() or None
                date_res = row.get("date_resolved", "").strip() or None

                try:
                    lat = float(row.get("latitude", DEFAULT_COORDS[0]))
                    lon = float(row.get("longitude", DEFAULT_COORDS[1]))
                except (ValueError, TypeError):
                    lat, lon = DEFAULT_COORDS

                is_critical = row.get("is_critical_crime") in ("1", "True", "true", True)

                record: Dict[str, Any] = {
                    "complaint_id": cid,
                    "complainant": row.get("complainant", "").strip(),
                    "category": row.get("category", "").strip(),
                    "department": row.get("department", "").strip(),
                    "description": row.get("description", "").strip(),
                    "priority": row.get("priority", "MEDIUM").strip().upper(),
                    "status": row.get("status", "REGISTERED").strip().upper(),
                    "assigned_to": assigned,
                    "location": row.get("location", DEFAULT_LOCATION).strip(),
                    "latitude": lat,
                    "longitude": lon,
                    "is_critical_crime": is_critical,
                    "date_registered": row.get("date_registered", "").strip(),
                    "date_resolved": date_res,
                    "status_history": history,
                }
                loaded_records[cid] = record

        complaints.clear()
        complaints.update(loaded_records)
        sync_counter_from_existing()
        return loaded_records

    except (OSError, IOError) as err:
        print(f"[File Handler Error] Could not read complaints from '{filepath}': {err}")
        return complaints


# =============================================================================
# 8. INTERACTIVE CLI & DISPATCH CONTROLLER
# =============================================================================


def display_menu() -> None:
    """Display the primary CLI menu."""
    print("\n" + "-" * 40)
    print("      CHENNAI COMPLAINT RADAR MENU")
    print("-" * 40)
    print(" [1] Register Incident / Complaint (with Chennai Locality)")
    print(" [2] Assign / Update Incident Lifecycle")
    print(" [3] Search Complaints by Status")
    print(" [4] View Single Case Detail Report")
    print(" [5] View Chennai Citywide Summary & Analytics")
    print(" [6] View Chennai Zone Threat Index (Red Zones & Solved Cases)")
    print(" [7] Save Data to CSV")
    print(" [8] Exit Program")
    print("-" * 40)


def handle_register() -> None:
    """Handle interactive registration flow."""
    print("\n--- [1] REGISTER INCIDENT / COMPLAINT (CHENNAI) ---")
    name = input("Enter Complainant / Reporting Officer Name: ").strip()
    if not name:
        print("[Error] Name cannot be empty.")
        return

    available_cats = list_categories()
    print("\nAvailable Categories:")
    for idx, cat in enumerate(available_cats, start=1):
        is_crit = is_critical_crime_category(cat)
        tag = " ⚠️ [CRITICAL VIOLENT CRIME]" if is_crit else ""
        print(f"  ({idx}) {cat:<32}{tag}")

    cat_input = input("\nEnter Category (Type name or number): ").strip()
    selected_cat = ""
    if cat_input.isdigit() and 1 <= int(cat_input) <= len(available_cats):
        selected_cat = available_cats[int(cat_input) - 1]
    else:
        selected_cat = cat_input

    if not selected_cat:
        print("[Error] Category cannot be empty.")
        return

    print("\nChennai Zones:")
    zone_names = list(ZONE_COORDINATES.keys())
    for idx, z in enumerate(zone_names, start=1):
        print(f"  ({idx}) {z}")
    loc_input = input("\nSelect Chennai Zone (name or number) [Default: T. Nagar]: ").strip()
    selected_loc = DEFAULT_LOCATION
    if loc_input.isdigit() and 1 <= int(loc_input) <= len(zone_names):
        selected_loc = zone_names[int(loc_input) - 1]
    elif loc_input:
        selected_loc = loc_input

    description = input("Enter Incident Description & Landmark: ").strip()
    if not description:
        print("[Error] Description cannot be empty.")
        return

    priority_input = input("Enter Priority (LOW / MEDIUM / HIGH) [Default: MEDIUM]: ").strip()
    if not priority_input:
        priority_input = "MEDIUM"

    cid = register_complaint(
        name=name,
        category=selected_cat,
        description=description,
        priority=priority_input,
        location=selected_loc,
    )
    rec = get_complaint(cid)
    print(f"\n[Success] Incident successfully registered!")
    print(f"  -> Generated ID           : {cid}")
    print(f"  -> Routed Department      : {rec.get('department')}")
    print(f"  -> Chennai Locality       : {rec.get('location')} (GPS: {rec.get('latitude')}, {rec.get('longitude')})")
    print(f"  -> Assigned Priority       : {rec.get('priority')}")
    print(f"  -> Status                  : {rec.get('status')}")


def handle_view_zones() -> None:
    """Display Chennai zone threat levels and solved counts."""
    print("\n--- [6] CHENNAI ZONE THREAT INDEX & HOTSPOTS ---")
    z_stats = zone_crime_statistics()
    print("-" * 76)
    print(f"{'Zone Name':<28} {'Threat Level':<18} {'Violent Crimes':<16} {'Solved'}")
    print("-" * 76)
    for zname, data in sorted(z_stats.items(), key=lambda x: x[1]['threat_score'], reverse=True):
        lvl = data['threat_level']
        lvl_display = "🚨 RED HOTSPOT" if lvl == 'RED_HOTSPOT' else "⚠️ MODERATE" if lvl == 'AMBER_MODERATE' else "🛡️ SAFE ZONE"
        print(f"{zname:<28} {lvl_display:<18} {data['active_critical_crimes']:<16} {data['solved_cases']}")
    print("-" * 76)


def run_interactive_loop() -> None:
    """Execute primary CLI application loop."""
    print("=" * 68)
    print("   CHENNAI DIGITAL COMPLAINT & CRIME ZONE TRACKING SYSTEM")
    print("   Greater Chennai Police & Municipal Command Console")
    print("=" * 68)

    loaded = load_complaints_from_csv()
    if loaded:
        print(f"[Startup] Restored {len(loaded)} incident records across Chennai.")
    else:
        print("[Startup] Ready with clean storage.")

    try:
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            try:
                if choice == "1":
                    handle_register()
                elif choice == "2":
                    cid = input("Enter ID: ").strip().upper()
                    st = input("Enter new status (REGISTERED/ASSIGNED/IN_PROGRESS/ESCALATED/RESOLVED/CLOSED): ").strip().upper()
                    update_status(cid, st)
                    print(f"Updated {cid} to {st}.")
                elif choice == "3":
                    target_status = input("Enter status to filter: ").strip()
                    matches = search_complaints_by_status(target_status)
                    print(f"Found {len(matches)} match(es).")
                elif choice == "4":
                    cid = input("Enter ID: ").strip().upper()
                    print(generate_complaint_report(cid))
                elif choice == "5":
                    print(generate_summary_report())
                elif choice == "6":
                    handle_view_zones()
                elif choice == "7":
                    save_complaints_to_csv()
                    print("Saved to CSV.")
                elif choice == "8":
                    print("Exiting...")
                    break
            except Exception as e:
                print(f"[Error] {e}")
    finally:
        save_complaints_to_csv()
        print("Auto-save completed.")


# =============================================================================
# 9. EMBEDDED AUTOMATED TEST RUNNER
# =============================================================================


class TestComplaintSystemStandalone(unittest.TestCase):
    """Test suite verifying all functional requirements and scenarios."""

    def setUp(self) -> None:
        clear_complaints()
        initialize_categories()

    def tearDown(self) -> None:
        clear_complaints()

    def test_01_register_valid_complaint(self) -> None:
        cid = register_complaint("Murugan", "Water Supply", "Low pressure", "HIGH", location="Velachery")
        self.assertEqual(cid, "CMP1001")
        rec = get_complaint(cid)
        self.assertEqual(rec["status"], "REGISTERED")
        self.assertEqual(rec["location"], "Velachery")

    def test_02_register_invalid_priority_defaults_to_medium(self) -> None:
        cid = register_complaint("Kumar", "Sanitation", "Overflow", "SUPER_URGENT", location="T. Nagar")
        rec = get_complaint(cid)
        self.assertEqual(rec["priority"], "MEDIUM")

    def test_03_assign_complaint(self) -> None:
        cid = register_complaint("Karthik", "Electricity", "Outage", "HIGH", location="Anna Nagar")
        updated = assign_complaint(cid, "Officer Selvam")
        self.assertEqual(updated["assigned_to"], "Officer Selvam")
        self.assertEqual(updated["status"], "ASSIGNED")

    def test_04_full_status_lifecycle(self) -> None:
        cid = register_complaint("Priya", "Electricity", "Wire spark", "MEDIUM", location="Guindy & Alandur")
        assign_complaint(cid, "Officer Selvam")
        update_status(cid, "IN_PROGRESS")
        escalate_complaint(cid)
        update_status(cid, "RESOLVED")
        update_status(cid, "CLOSED")
        rec = get_complaint(cid)
        statuses = [s[0] for s in rec["status_history"]]
        self.assertEqual(statuses, ["REGISTERED", "ASSIGNED", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED"])

    def test_05_search_unknown_status_returns_empty_list(self) -> None:
        self.assertEqual(search_complaints_by_status("UNKNOWN_XYZ"), [])

    def test_06_get_nonexistent_complaint_raises_error(self) -> None:
        with self.assertRaises(InvalidComplaintIDError):
            get_complaint("CMP9999")

    def test_07_csv_persistence_roundtrip(self) -> None:
        cid = register_complaint("Sundaram", "Sanitation", "Litter", location="Marina Beach & Triplicane")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self.assertTrue(save_complaints_to_csv(filepath=tmp_path))
            clear_complaints()
            loaded = load_complaints_from_csv(filepath=tmp_path)
            self.assertIn(cid, loaded)
            self.assertEqual(loaded[cid]["location"], "Marina Beach & Triplicane")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_08_average_resolution_time_zero_resolved(self) -> None:
        self.assertEqual(average_resolution_time(), 0.0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t", "test"):
        unittest.main(argv=[sys.argv[0]])
    else:
        run_interactive_loop()
