"""
CSA-0801: Python Programming - Module 04
Topic: Data Serialization, Object Pickling, and Custom JSON Encoders

Key Concepts Covered:
1. Binary serialization with the `pickle` module
2. Pickling custom class objects & methods
3. Custom JSON Encoder (json.JSONEncoder) for complex types (datetime, sets, custom objects)
4. Security implications of deserialization (safe loading guidelines)
"""

import datetime
import json
import pickle
import sys
from typing import Any


class AcademicSession:
    """Class to test Python object pickling and state preservation."""

    def __init__(self, course_code: str, term: str, max_capacity: int):
        self.course_code = course_code
        self.term = term
        self.max_capacity = max_capacity
        self.enrolled_students: set[str] = set()
        self.created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

    def add_student(self, student_id: str) -> bool:
        if len(self.enrolled_students) < self.max_capacity:
            self.enrolled_students.add(student_id)
            return True
        return False

    def __repr__(self) -> str:
        return f"AcademicSession({self.course_code}, term={self.term}, enrolled={len(self.enrolled_students)}/{self.max_capacity})"


class CustomAcademicJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder handling datetime, sets, and AcademicSession instances."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, set):
            return sorted(list(obj))
        if isinstance(obj, AcademicSession):
            return {
                "__class__": "AcademicSession",
                "course_code": obj.course_code,
                "term": obj.term,
                "max_capacity": obj.max_capacity,
                "enrolled_students": sorted(list(obj.enrolled_students)),
                "created_at": obj.created_at.isoformat()
            }
        return super().default(obj)


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 4.3 - Serialization (Pickle vs JSON)")
    print("=" * 60)

    # 1. Create instance and populate state
    session = AcademicSession("CSA-0801", "Fall 2026", 50)
    session.add_student("STU-101")
    session.add_student("STU-102")
    session.add_student("STU-103")

    print(f"\n[1] Original Python Object: {session}")

    # 2. Binary Pickling (pickle.dumps and pickle.loads)
    pickled_bytes = pickle.dumps(session)
    restored_session: AcademicSession = pickle.loads(pickled_bytes)

    print("\n[2] Pickle Serialization:")
    print(f"  * Binary Payload Size: {len(pickled_bytes)} bytes")
    print(f"  * Restored Object:     {restored_session}")
    print(f"  * Enrolled Students:   {restored_session.enrolled_students}")
    print(f"  * Restored Methods:    Able to enroll STU-104? {restored_session.add_student('STU-104')}")

    # 3. JSON Custom Serialization
    json_str = json.dumps(session, cls=CustomAcademicJSONEncoder, indent=2)
    print("\n[3] JSON Custom Serialization (Human-readable & interoperable):")
    print(json_str)

    print("\n[OK] Lab 4.3 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
