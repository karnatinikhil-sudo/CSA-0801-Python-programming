"""CSV file persistence handler for the Complaint System.

Provides serialization and deserialization of complaints, categories, location coordinates,
and tracking history to and from CSV files. Catches OSError/IOError exceptions gracefully.
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
    """Save complaints data to CSV file."""
    if complaints_dict is None:
        complaints_dict = complaint_manager.get_all_complaints()

    try:
        parent_dir = os.path.dirname(filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()

            for record in complaints_dict.values():
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
                    "location": record.get("location", "Downtown Central"),
                    "latitude": record.get("latitude", 17.3850),
                    "longitude": record.get("longitude", 78.4867),
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
    """Load complaints data from a CSV file into the complaint manager."""
    if not os.path.exists(filepath):
        return complaint_manager.get_all_complaints()

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

                # Parse location coordinates
                try:
                    lat = float(row.get("latitude", 17.3850))
                    lon = float(row.get("longitude", 78.4867))
                except (ValueError, TypeError):
                    lat, lon = 17.3850, 78.4867

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
                    "location": row.get("location", "Downtown Central").strip(),
                    "latitude": lat,
                    "longitude": lon,
                    "is_critical_crime": is_critical,
                    "date_registered": row.get("date_registered", "").strip(),
                    "date_resolved": date_res,
                    "status_history": history,
                }
                loaded_records[cid] = record

        complaints_store = complaint_manager.get_all_complaints()
        complaints_store.clear()
        complaints_store.update(loaded_records)
        complaint_manager.sync_counter_from_existing()

        return loaded_records

    except (OSError, IOError) as err:
        print(f"[File Handler Error] Could not read complaints from '{filepath}': {err}")
        return complaint_manager.get_all_complaints()
