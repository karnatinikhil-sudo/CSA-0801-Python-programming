"""Digital Complaint Registration and Tracking System (Single-File Distribution).

A comprehensive Python 3 console application for public service complaint registration,
category-to-department routing, lifecycle tracking, escalation, statistical analytics,
plain-text reporting, and CSV data persistence.

Python Standard Library only (Python 3.9+). Zero external dependencies.
"""

import csv
from datetime import datetime
import json
import os
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

_DEFAULT_MAPPINGS: Dict[str, str] = {
    "Water Supply": "Water Works Department",
    "Electricity": "Power & Electricity Department",
    "Sanitation": "Public Health & Sanitation",
    "Roads & Infrastructure": "Public Works Department",
    "Billing & Accounts": "Finance & Revenue Department",
    "Public Safety": "Municipal Police & Safety",
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


def get_all_category_mappings() -> Dict[str, str]:
    """Retrieve a copy of all category-to-department mappings."""
    return dict(category_department_map)


# =============================================================================
# 3. COMPLAINT MANAGER & DATA STORE
# =============================================================================

complaints: Dict[str, Dict[str, Any]] = {}
_complaint_counter: int = 1000

VALID_PRIORITIES: Tuple[str, ...] = ("LOW", "MEDIUM", "HIGH")
DEFAULT_PRIORITY: str = "MEDIUM"


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


def register_complaint(
    name: str,
    category: str,
    description: str,
    priority: str = DEFAULT_PRIORITY,
) -> str:
    """Register a new complaint, defaulting invalid priority to MEDIUM safely."""
    cleaned_name = str(name).strip().title()
    cleaned_category = str(category).strip().title()
    cleaned_description = str(description).strip()

    if not cleaned_name:
        raise ValueError("Complainant name cannot be empty.")
    if not cleaned_category:
        raise ValueError("Complaint category cannot be empty.")
    if not cleaned_description:
        raise ValueError("Complaint description cannot be empty.")

    normalized_priority = str(priority).strip().upper()
    if normalized_priority not in VALID_PRIORITIES:
        normalized_priority = DEFAULT_PRIORITY

    department = get_department(cleaned_category)
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
    """Calculate the frequency distribution of complaints across categories."""
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
        "   DIGITAL COMPLAINT SYSTEM - EXECUTIVE SUMMARY REPORT",
        "=" * 64,
        f" Total Complaints Registered : {total_count}",
        f" Pending / In-Progress       : {pending_count}",
        f" Resolved / Closed           : {resolved_count}",
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
            lines.append(f"   - {cat:<24} ({dept}): {count}")

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

                record: Dict[str, Any] = {
                    "complaint_id": cid,
                    "complainant": row.get("complainant", "").strip(),
                    "category": row.get("category", "").strip(),
                    "department": row.get("department", "").strip(),
                    "description": row.get("description", "").strip(),
                    "priority": row.get("priority", "MEDIUM").strip().upper(),
                    "status": row.get("status", "REGISTERED").strip().upper(),
                    "assigned_to": assigned,
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
    print("               MAIN MENU")
    print("-" * 40)
    print(" [1] Register New Complaint")
    print(" [2] Assign / Update Complaint Lifecycle")
    print(" [3] Search Complaints by Status")
    print(" [4] View Single Complaint Detail Report")
    print(" [5] View Executive Summary & Analytics")
    print(" [6] Manage Categories & Departments")
    print(" [7] Save Data to CSV")
    print(" [8] Exit Program")
    print("-" * 40)


def handle_register() -> None:
    """Handle interactive registration flow."""
    print("\n--- [1] REGISTER NEW COMPLAINT ---")
    name = input("Enter Complainant Name: ").strip()
    if not name:
        print("[Error] Complainant name cannot be empty.")
        return

    available_cats = list_categories()
    print("\nAvailable Categories:")
    for idx, cat in enumerate(available_cats, start=1):
        dept = get_department(cat)
        print(f"  ({idx}) {cat:<24} -> Department: {dept}")

    cat_input = input("\nEnter Category (Type name or number): ").strip()
    selected_cat = ""
    if cat_input.isdigit() and 1 <= int(cat_input) <= len(available_cats):
        selected_cat = available_cats[int(cat_input) - 1]
    else:
        selected_cat = cat_input

    if not selected_cat:
        print("[Error] Category cannot be empty.")
        return

    description = input("Enter Detailed Description: ").strip()
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
    )
    rec = get_complaint(cid)
    print(f"\n[Success] Complaint successfully registered!")
    print(f"  -> Generated Complaint ID : {cid}")
    print(f"  -> Routed Department     : {rec.get('department')}")
    print(f"  -> Assigned Priority      : {rec.get('priority')}")
    print(f"  -> Status                 : {rec.get('status')}")


def handle_assign_update() -> None:
    """Handle assignment and lifecycle status updates."""
    print("\n--- [2] ASSIGN / UPDATE COMPLAINT LIFECYCLE ---")
    cid = input("Enter Complaint ID (e.g. CMP1001): ").strip().upper()
    if not cid:
        print("[Error] Complaint ID is required.")
        return

    rec = get_complaint(cid)
    print(f"\nSelected Complaint: {cid} | Current Status: {rec['status']} | Priority: {rec['priority']}")
    print(f"Complainant: {rec['complainant']} | Department: {rec['department']}")
    print(f"Assigned To: {rec.get('assigned_to') or 'Unassigned'}")

    print("\nChoose Action:")
    print(" [1] Assign / Reassign Staff Officer")
    print(" [2] Update Lifecycle Status")
    print(" [3] Update Priority Level")
    print(" [4] Escalate Complaint (High Priority)")
    print(" [5] Cancel")

    action = input("Select an option (1-5): ").strip()

    if action == "1":
        officer = input("Enter Officer / Staff Name: ").strip()
        if not officer:
            print("[Error] Staff name cannot be empty.")
            return
        updated = assign_complaint(cid, officer)
        print(f"[Success] Assigned to {updated['assigned_to']}. Status updated to {updated['status']}.")
    elif action == "2":
        print(f"\nValid Statuses: {', '.join(VALID_STATUSES)}")
        new_status = input("Enter New Status: ").strip().upper()
        updated = update_status(cid, new_status)
        print(f"[Success] Status updated to {updated['status']}.")
        if updated.get("date_resolved"):
            print(f"  -> Stamped Resolution Date: {updated['date_resolved']}")
    elif action == "3":
        print("Valid Priorities: LOW, MEDIUM, HIGH")
        new_priority = input("Enter New Priority: ").strip().upper()
        updated = update_priority(cid, new_priority)
        print(f"[Success] Priority updated to {updated['priority']}.")
    elif action == "4":
        updated = escalate_complaint(cid)
        print(f"[Success] Complaint {cid} escalated! Status: {updated['status']}, Priority: {updated['priority']}.")
    elif action == "5":
        print("Action cancelled.")
    else:
        print("[Error] Invalid selection.")


def handle_search_by_status() -> None:
    """Handle filtering complaints by status."""
    print("\n--- [3] SEARCH COMPLAINTS BY STATUS ---")
    print(f"Status options: {', '.join(VALID_STATUSES)}")
    target_status = input("Enter status to filter by: ").strip()

    matches = search_complaints_by_status(target_status)
    if not matches:
        print(f"\nNo complaints found matching status: '{target_status}'.")
        return

    print(f"\nFound {len(matches)} complaint(s) with status '{target_status.upper()}':")
    print("-" * 76)
    print(f"{'ID':<10} {'Complainant':<18} {'Category':<16} {'Priority':<10} {'Assigned To'}")
    print("-" * 76)
    for item in matches:
        cid = item.get("complaint_id", "")
        name = item.get("complainant", "")[:16]
        cat = item.get("category", "")[:14]
        pri = item.get("priority", "")
        assigned = item.get("assigned_to") or "Unassigned"
        print(f"{cid:<10} {name:<18} {cat:<16} {pri:<10} {assigned}")
    print("-" * 76)


def handle_view_complaint_report() -> None:
    """Handle single complaint report display."""
    print("\n--- [4] VIEW SINGLE COMPLAINT DETAIL REPORT ---")
    cid = input("Enter Complaint ID: ").strip().upper()
    if not cid:
        print("[Error] Complaint ID is required.")
        return
    print("\n" + generate_complaint_report(cid))


def handle_view_summary_report() -> None:
    """Handle summary report display."""
    print("\n--- [5] EXECUTIVE SUMMARY & ANALYTICS ---")
    print("\n" + generate_summary_report())


def handle_manage_categories() -> None:
    """Handle category inspection and creation."""
    print("\n--- [6] MANAGE CATEGORIES & DEPARTMENTS ---")
    mappings = get_all_category_mappings()
    print("\nCurrent Category Mappings:")
    for cat, dept in sorted(mappings.items()):
        print(f"  - {cat:<24} -> {dept}")

    print("\nActions:")
    print(" [1] Add New Category & Department Mapping")
    print(" [2] Return to Main Menu")
    choice = input("Select option (1-2): ").strip()

    if choice == "1":
        cat_name = input("Enter New Category Name: ").strip()
        dept_name = input("Enter Responsible Department: ").strip()
        if not cat_name or not dept_name:
            print("[Error] Both category and department names are required.")
            return
        add_category(cat_name, dept_name)
        print(f"[Success] Added category '{cat_name.title()}' mapped to '{dept_name.title()}'.")


def handle_save_csv() -> None:
    """Handle explicit CSV save."""
    print("\n--- [7] SAVE DATA TO CSV ---")
    if save_complaints_to_csv():
        print("[Success] All complaint data successfully saved to 'data/complaints.csv'.")
    else:
        print("[Warning] Could not complete CSV save.")


def run_interactive_loop() -> None:
    """Execute the primary interactive application loop."""
    print("=" * 68)
    print("   DIGITAL COMPLAINT REGISTRATION AND TRACKING SYSTEM")
    print("   Municipal & Public Service Incident Management Console")
    print("=" * 68)

    loaded = load_complaints_from_csv()
    if loaded:
        print(f"[Startup] Restored {len(loaded)} complaint record(s) from CSV storage.")
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
                    handle_assign_update()
                elif choice == "3":
                    handle_search_by_status()
                elif choice == "4":
                    handle_view_complaint_report()
                elif choice == "5":
                    handle_view_summary_report()
                elif choice == "6":
                    handle_manage_categories()
                elif choice == "7":
                    handle_save_csv()
                elif choice == "8":
                    print("\nExiting Digital Complaint System. Saving records...")
                    break
                else:
                    print("\n[Invalid Selection] Please enter a valid option between 1 and 8.")

            except ComplaintSystemError as c_err:
                print(f"\n[Complaint System Error] {c_err}")
            except ValueError as v_err:
                print(f"\n[Validation Error] {v_err}")
            except Exception as u_err:
                print(f"\n[Unexpected Error] {u_err}")

    finally:
        save_complaints_to_csv()
        print("[Persistence] Auto-save completed. Goodbye!")


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
        cid = register_complaint("Alice Johnson", "Water Supply", "Low pressure", "HIGH")
        self.assertEqual(cid, "CMP1001")
        rec = get_complaint(cid)
        self.assertEqual(rec["status"], "REGISTERED")
        self.assertEqual(rec["priority"], "HIGH")

    def test_02_register_invalid_priority_defaults_to_medium(self) -> None:
        cid = register_complaint("Bob", "Sanitation", "Overflow", "SUPER_URGENT")
        rec = get_complaint(cid)
        self.assertEqual(rec["priority"], "MEDIUM")

    def test_03_assign_complaint(self) -> None:
        cid = register_complaint("Charlie", "Electricity", "Outage", "HIGH")
        updated = assign_complaint(cid, "Officer Dave")
        self.assertEqual(updated["assigned_to"], "Officer Dave")
        self.assertEqual(updated["status"], "ASSIGNED")

    def test_04_full_status_lifecycle(self) -> None:
        cid = register_complaint("Dave", "Electricity", "Wire spark", "MEDIUM")
        assign_complaint(cid, "Officer Dave")
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
        cid = register_complaint("Grace", "Sanitation", "Litter")
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            self.assertTrue(save_complaints_to_csv(filepath=tmp_path))
            clear_complaints()
            loaded = load_complaints_from_csv(filepath=tmp_path)
            self.assertIn(cid, loaded)
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
