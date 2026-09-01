"""CSV file persistence handler for the Complaint System.

This module provides robust serialization and deserialization of complaints,
categories, and tracking history to and from CSV files. It ensures directories are created
as needed and guards against file system IOErrors/OSErrors with user-friendly diagnostics.
"""

import csv
import json
import os
from typing import Any, Dict, Optional

import complaint_manager

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
    """Save complaints data to a CSV file.

    Creates the destination directory (e.g. data/) if it does not exist.
    Encodes status_history timeline into JSON within the CSV row. Catches
    OSError/IOError exceptions to prevent application crashes.

    Args:
        filepath: Target CSV file path (defaults to 'data/complaints.csv').
        complaints_dict: Optional dictionary of complaints. If omitted, uses global store.

    Returns:
        True if successfully saved, False if an I/O error occurred.
    """
    if complaints_dict is None:
        complaints_dict = complaint_manager.get_all_complaints()

    try:
        # Ensure parent directory exists
        parent_dir = os.path.dirname(filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

            for record in complaints_dict.values():
                # Prepare row data with clean representations
                history = record.get("status_history", [])
                history_json = json.dumps(history)

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
    """Load complaints data from a CSV file into the complaint manager.

    Deserializes status_history timelines and updates the internal ID counter
    so new registrations never conflict with loaded records. Catches OSError/IOError
    gracefully.

    Args:
        filepath: Source CSV file path (defaults to 'data/complaints.csv').

    Returns:
        Dictionary of loaded complaints keyed by Complaint ID.
    """
    if not os.path.exists(filepath):
        # File doesn't exist yet, return empty store
        return complaint_manager.get_all_complaints()

    loaded_records: Dict[str, Dict[str, Any]] = {}

    try:
        with open(filepath, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cid = row.get("complaint_id", "").strip().upper()
                if not cid:
                    continue

                # Parse JSON status history
                history_raw = row.get("status_history", "[]")
                try:
                    history_list = json.loads(history_raw)
                    # Ensure tuples of (status, timestamp)
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

        # Populate in-memory store and synchronize counter
        complaints_store = complaint_manager.get_all_complaints()
        complaints_store.clear()
        complaints_store.update(loaded_records)
        complaint_manager.sync_counter_from_existing()

        return loaded_records

    except (OSError, IOError) as err:
        print(f"[File Handler Error] Could not read complaints from '{filepath}': {err}")
        return complaint_manager.get_all_complaints()
