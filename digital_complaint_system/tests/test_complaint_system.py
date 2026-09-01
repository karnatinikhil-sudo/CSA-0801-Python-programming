"""Automated Unit Test Suite for the Digital Complaint Registration and Tracking System.

This module provides exhaustive test coverage for the 8 mandated functional scenarios
as well as additional edge cases, exceptions, lifecycle transitions, analytics, and CSV persistence.
"""

import os
import sys
import tempfile
import unittest

# Ensure project root is on sys.path for direct test execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import analytics
import category_manager
import complaint_manager
from exceptions import (
    ComplaintSystemError,
    DuplicateComplaintError,
    InvalidComplaintIDError,
    InvalidStatusError,
)
import file_handler
import reports
import tracking_manager


class TestComplaintSystem(unittest.TestCase):
    """Test suite verifying functional requirements, edge cases, and integrity."""

    def setUp(self) -> None:
        """Reset internal stores before every test to guarantee test isolation."""
        complaint_manager.clear_complaints()
        category_manager.reset_categories()

    def tearDown(self) -> None:
        """Clean up state after each test."""
        complaint_manager.clear_complaints()

    # -------------------------------------------------------------------------
    # Scenario 1: Valid registration generates unique ID with status REGISTERED
    # -------------------------------------------------------------------------
    def test_01_register_valid_complaint(self) -> None:
        """Scenario 1: Registering a valid complaint generates a unique ID with status REGISTERED."""
        cid1 = complaint_manager.register_complaint(
            name="Alice Johnson",
            category="Water Supply",
            description="Low water pressure in Sector 4.",
            priority="HIGH",
        )
        self.assertTrue(cid1.startswith("CMP"))
        self.assertEqual(cid1, "CMP1001")

        rec1 = complaint_manager.get_complaint(cid1)
        self.assertEqual(rec1["complaint_id"], "CMP1001")
        self.assertEqual(rec1["complainant"], "Alice Johnson")
        self.assertEqual(rec1["category"], "Water Supply")
        self.assertEqual(rec1["department"], "Water Works Department")
        self.assertEqual(rec1["priority"], "HIGH")
        self.assertEqual(rec1["status"], "REGISTERED")
        self.assertIsNone(rec1["assigned_to"])
        self.assertIsNone(rec1["date_resolved"])
        self.assertEqual(len(rec1["status_history"]), 1)
        self.assertEqual(rec1["status_history"][0][0], "REGISTERED")

        # Second registration should increment counter
        cid2 = complaint_manager.register_complaint(
            name="Bob Smith",
            category="Electricity",
            description="Street light flickering.",
            priority="LOW",
        )
        self.assertEqual(cid2, "CMP1002")
        self.assertNotEqual(cid1, cid2)

    # -------------------------------------------------------------------------
    # Scenario 2: Invalid priority defaults safely to MEDIUM
    # -------------------------------------------------------------------------
    def test_02_register_invalid_priority_defaults_to_medium(self) -> None:
        """Scenario 2: Registering with an invalid priority defaults safely to MEDIUM."""
        cid = complaint_manager.register_complaint(
            name="Charlie Brown",
            category="Sanitation",
            description="Garbage bin overflow near park.",
            priority="CRITICAL_SUPER_HIGH",  # Invalid priority
        )
        rec = complaint_manager.get_complaint(cid)
        self.assertEqual(rec["priority"], "MEDIUM")

        # Also test with empty string priority
        cid_empty = complaint_manager.register_complaint(
            name="Daisy Miller",
            category="Sanitation",
            description="Recycling truck missed Tuesday.",
            priority="",
        )
        rec_empty = complaint_manager.get_complaint(cid_empty)
        self.assertEqual(rec_empty["priority"], "MEDIUM")

    # -------------------------------------------------------------------------
    # Scenario 3: Assigning a complaint sets assigned_to and moves to ASSIGNED
    # -------------------------------------------------------------------------
    def test_03_assign_complaint(self) -> None:
        """Scenario 3: Assigning a complaint sets assigned_to and moves status to ASSIGNED."""
        cid = complaint_manager.register_complaint(
            name="David Miller",
            category="Roads & Infrastructure",
            description="Deep pothole on Main Street.",
            priority="HIGH",
        )
        updated = tracking_manager.assign_complaint(cid, "Officer John Doe")

        self.assertEqual(updated["assigned_to"], "Officer John Doe")
        self.assertEqual(updated["status"], "ASSIGNED")
        self.assertEqual(len(updated["status_history"]), 2)
        self.assertEqual(updated["status_history"][0][0], "REGISTERED")
        self.assertEqual(updated["status_history"][1][0], "ASSIGNED")

    # -------------------------------------------------------------------------
    # Scenario 4: Full status lifecycle records timestamped status_history
    # -------------------------------------------------------------------------
    def test_04_full_status_lifecycle(self) -> None:
        """Scenario 4: A full status lifecycle correctly records timestamped entries in status_history."""
        cid = complaint_manager.register_complaint(
            name="Elena Rostova",
            category="Electricity",
            description="Transformer noise in residential block.",
            priority="MEDIUM",
        )

        # 1. Assign
        tracking_manager.assign_complaint(cid, "Technician Mark")
        # 2. In Progress
        tracking_manager.update_status(cid, "IN_PROGRESS")
        # 3. Escalate
        tracking_manager.escalate_complaint(cid)
        # 4. Resolve
        tracking_manager.update_status(cid, "RESOLVED")
        # 5. Close
        tracking_manager.update_status(cid, "CLOSED")

        rec = complaint_manager.get_complaint(cid)
        self.assertEqual(rec["status"], "CLOSED")
        self.assertIsNotNone(rec["date_resolved"])

        statuses = [entry[0] for entry in rec["status_history"]]
        expected_sequence = ["REGISTERED", "ASSIGNED", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED"]
        self.assertEqual(statuses, expected_sequence)

        # Verify each history item has valid timestamp string
        for status_name, timestamp in rec["status_history"]:
            self.assertIsInstance(timestamp, str)
            self.assertTrue(len(timestamp) > 0)

    # -------------------------------------------------------------------------
    # Scenario 5: Searching by unknown status returns empty list without raising
    # -------------------------------------------------------------------------
    def test_05_search_unknown_status_returns_empty_list(self) -> None:
        """Scenario 5: Searching by an unknown status returns an empty list without raising."""
        complaint_manager.register_complaint(
            name="Frank Wright",
            category="Sanitation",
            description="Drain cleaning request.",
            priority="LOW",
        )

        # Search by non-existent status string
        result_invalid = analytics.search_complaints_by_status("NON_EXISTENT_STATUS")
        self.assertEqual(result_invalid, [])

        # Search by empty status
        result_empty = analytics.search_complaints_by_status("")
        self.assertEqual(result_empty, [])

        # Valid search should find matches case-insensitively
        result_registered = analytics.search_complaints_by_status("registered")
        self.assertEqual(len(result_registered), 1)
        self.assertEqual(result_registered[0]["complainant"], "Frank Wright")

    # -------------------------------------------------------------------------
    # Scenario 6: Requesting non-existent Complaint ID raises InvalidComplaintIDError
    # -------------------------------------------------------------------------
    def test_06_get_nonexistent_complaint_raises_error(self) -> None:
        """Scenario 6: Requesting a non-existent Complaint ID raises InvalidComplaintIDError."""
        with self.assertRaises(InvalidComplaintIDError) as context:
            complaint_manager.get_complaint("CMP9999")
        self.assertIn("CMP9999", str(context.exception))

        with self.assertRaises(InvalidComplaintIDError):
            tracking_manager.assign_complaint("CMP8888", "Officer Smith")

        with self.assertRaises(InvalidComplaintIDError):
            tracking_manager.update_status("CMP8888", "RESOLVED")

    # -------------------------------------------------------------------------
    # Scenario 7: Saving and reloading via CSV preserves all records
    # -------------------------------------------------------------------------
    def test_07_csv_persistence_roundtrip(self) -> None:
        """Scenario 7: Saving then reloading complaints via CSV preserves all records."""
        cid1 = complaint_manager.register_complaint(
            name="Grace Hopper",
            category="Billing & Accounts",
            description="Incorrect property tax calculation.",
            priority="HIGH",
        )
        tracking_manager.assign_complaint(cid1, "Auditor Vance")
        tracking_manager.update_status(cid1, "RESOLVED")

        cid2 = complaint_manager.register_complaint(
            name="Henry Ford",
            category="Public Safety",
            description="Damaged pedestrian crossing beacon.",
            priority="MEDIUM",
        )

        # Use temporary file for test
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Save
            save_success = file_handler.save_complaints_to_csv(filepath=tmp_path)
            self.assertTrue(save_success)

            # Clear memory
            complaint_manager.clear_complaints()
            self.assertEqual(len(complaint_manager.get_all_complaints()), 0)

            # Reload
            loaded = file_handler.load_complaints_from_csv(filepath=tmp_path)
            self.assertEqual(len(loaded), 2)
            self.assertIn("CMP1001", loaded)
            self.assertIn("CMP1002", loaded)

            # Verify contents of CMP1001
            rec1 = loaded["CMP1001"]
            self.assertEqual(rec1["complainant"], "Grace Hopper")
            self.assertEqual(rec1["category"], "Billing & Accounts")
            self.assertEqual(rec1["status"], "RESOLVED")
            self.assertEqual(rec1["assigned_to"], "Auditor Vance")
            self.assertEqual(len(rec1["status_history"]), 3)
            self.assertEqual(rec1["status_history"][2][0], "RESOLVED")

            # Verify counter is synchronized: next registration must be CMP1003
            cid3 = complaint_manager.register_complaint(
                name="Ian Fleming",
                category="Sanitation",
                description="Litter in public square.",
            )
            self.assertEqual(cid3, "CMP1003")

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    # -------------------------------------------------------------------------
    # Scenario 8: Average resolution time with zero resolved returns 0
    # -------------------------------------------------------------------------
    def test_08_average_resolution_time_zero_resolved(self) -> None:
        """Scenario 8: Computing average resolution time with zero resolved complaints returns 0."""
        # Case A: Empty store
        self.assertEqual(analytics.average_resolution_time(), 0.0)

        # Case B: Complaints exist, but none are resolved
        complaint_manager.register_complaint(
            name="Julia Roberts",
            category="Electricity",
            description="Power surge in district.",
            priority="HIGH",
        )
        complaint_manager.register_complaint(
            name="Kevin Bacon",
            category="Water Supply",
            description="Water pipeline maintenance request.",
            priority="LOW",
        )
        self.assertEqual(analytics.count_pending_complaints(), 2)
        self.assertEqual(analytics.average_resolution_time(), 0.0)

    # -------------------------------------------------------------------------
    # Additional Edge Case & Regression Tests
    # -------------------------------------------------------------------------
    def test_invalid_status_transition_raises_error(self) -> None:
        """Attempting to update to an unrecognized status raises InvalidStatusError."""
        cid = complaint_manager.register_complaint(
            name="Laura Croft",
            category="Sanitation",
            description="Blocked storm drain.",
        )
        with self.assertRaises(InvalidStatusError) as context:
            tracking_manager.update_status(cid, "INVALID_STATE")
        self.assertEqual(context.exception.status, "INVALID_STATE")

    def test_custom_category_addition(self) -> None:
        """Test adding custom category and verify automatic routing."""
        category_manager.add_category("Cyber Security", "IT Infrastructure Dept")
        self.assertIn("Cyber Security", category_manager.list_categories())
        self.assertEqual(category_manager.get_department("Cyber Security"), "It Infrastructure Dept")

        cid = complaint_manager.register_complaint(
            name="Neo Anderson",
            category="Cyber Security",
            description="Suspicious traffic detected on municipal portal.",
        )
        rec = complaint_manager.get_complaint(cid)
        self.assertEqual(rec["department"], "It Infrastructure Dept")

    def test_reports_formatting(self) -> None:
        """Test plain text formatting of single complaint and summary reports."""
        cid = complaint_manager.register_complaint(
            name="Miles Morales",
            category="Public Safety",
            description="Broken security barrier on 5th avenue.",
            priority="HIGH",
        )
        tracking_manager.assign_complaint(cid, "Captain Stacy")

        detail_rep = reports.generate_complaint_report(cid)
        self.assertIn(cid, detail_rep)
        self.assertIn("Miles Morales", detail_rep)
        self.assertIn("Captain Stacy", detail_rep)
        self.assertIn("Public Safety", detail_rep)

        summary_rep = reports.generate_summary_report()
        self.assertIn("EXECUTIVE SUMMARY REPORT", summary_rep)
        self.assertIn("Total Complaints Registered : 1", summary_rep)

        dept_rep = reports.generate_department_report()
        self.assertIn("Municipal Police & Safety", dept_rep)

    def test_exception_inheritance(self) -> None:
        """Ensure all domain exceptions inherit from ComplaintSystemError."""
        self.assertTrue(issubclass(InvalidComplaintIDError, ComplaintSystemError))
        self.assertTrue(issubclass(InvalidStatusError, ComplaintSystemError))
        self.assertTrue(issubclass(DuplicateComplaintError, ComplaintSystemError))


if __name__ == "__main__":
    unittest.main(verbosity=2)
