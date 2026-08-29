"""
CSA-0801: Python Programming - Module 04
Topic: File I/O, Context Managers, CSV and JSON Processing

Key Concepts Covered:
1. File operations (r, w, a, r+, b) with safe Context Managers (`with`)
2. Stream positioning using `seek()` and `tell()`
3. CSV file processing with `csv.DictReader` and `csv.DictWriter`
4. JSON serialization and deserialization with pretty-printing
5. Atomic file writing and resource safety
"""

import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def process_student_csv(file_path: Path, output_path: Path) -> int:
    """Reads a CSV file of student grades, calculates averages, and writes an enriched CSV."""
    records = []
    with open(file_path, mode="r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            m1 = float(row["marks1"])
            m2 = float(row["marks2"])
            m3 = float(row["marks3"])
            avg = round((m1 + m2 + m3) / 3.0, 2)
            status = "Pass" if avg >= 50.0 else "Fail"

            records.append({
                "student_id": row["student_id"],
                "name": row["name"],
                "average_score": avg,
                "status": status
            })

    # Write enriched data to output CSV
    fieldnames = ["student_id", "name", "average_score", "status"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return len(records)


def export_and_import_json(data: dict[str, Any], json_path: Path) -> dict[str, Any]:
    """Demonstrates JSON serialization with indentation and round-trip parsing."""
    # Write JSON
    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, sort_keys=True)

    # Read back JSON
    with open(json_path, mode="r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    return loaded_data


def stream_seek_tell_demo(temp_path: Path) -> dict[str, Any]:
    """Demonstrates seek() and tell() stream pointer controls."""
    with open(temp_path, mode="w+", encoding="utf-8") as f:
        f.write("0123456789ABCDEF")
        pos_end = f.tell()

        f.seek(5)
        pos_mid = f.tell()
        content_from_5 = f.read(5)

        f.seek(0)
        content_full = f.read()

    return {
        "end_position": pos_end,
        "mid_position": pos_mid,
        "content_from_5": content_from_5,
        "full_content": content_full,
    }


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 4.1 - File I/O, CSV & JSON Operations")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        dir_path = Path(tmp_dir)

        # 1. Create Sample Input CSV
        input_csv = dir_path / "students_input.csv"
        output_csv = dir_path / "students_summary.csv"

        sample_csv_content = (
            "student_id,name,marks1,marks2,marks3\n"
            "STU-001,Nikhil Karnati,95,92,98\n"
            "STU-002,Priya Sharma,88,85,90\n"
            "STU-003,Rahul Verma,45,40,48\n"
        )
        input_csv.write_text(sample_csv_content, encoding="utf-8")

        count = process_student_csv(input_csv, output_csv)
        print(f"\n[1] CSV Processing ({count} records processed):")
        with open(output_csv, mode="r", encoding="utf-8") as f:
            print(f.read().strip())

        # 2. JSON Export & Import
        json_file = dir_path / "course_catalog.json"
        catalog_payload = {
            "course_code": "CSA-0801",
            "title": "Python Programming",
            "instructor": {
                "name": "Prof. Karnati",
                "department": "Computer Science & AI"
            },
            "topics": ["Basics", "Data Structures", "OOP", "File Handling", "SQLite", "GUI", "Capstone"]
        }
        loaded_json = export_and_import_json(catalog_payload, json_file)
        print("\n[2] JSON Serialization & Round-Trip Parsing:")
        print(f"  * Course:     {loaded_json['course_code']} - {loaded_json['title']}")
        print(f"  * Instructor: {loaded_json['instructor']['name']}")
        print(f"  * Topics:     {len(loaded_json['topics'])} syllabus units loaded")

        # 3. Stream seek & tell
        stream_file = dir_path / "stream_demo.txt"
        stream_results = stream_seek_tell_demo(stream_file)
        print("\n[3] File Pointer Mechanics (seek & tell):")
        print(f"  * Stream end position: {stream_results['end_position']}")
        print(f"  * Read from offset 5:  '{stream_results['content_from_5']}'")

    print("\n[OK] Lab 4.1 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
