"""Main entry point and interactive CLI menu for the Complaint System.

This module coordinates user interactions, runs the primary command loop,
routes menu actions, and ensures fault tolerance through structured exception
handling and automatic data persistence on shutdown.
"""

import sys
from typing import Optional

import analytics
import category_manager
import complaint_manager
from exceptions import ComplaintSystemError, InvalidComplaintIDError, InvalidStatusError
import file_handler
import reports
import tracking_manager


def print_banner() -> None:
    """Print the welcome application header."""
    print("=" * 68)
    print("   DIGITAL COMPLAINT REGISTRATION AND TRACKING SYSTEM")
    print("   Municipal & Public Service Incident Management Console")
    print("=" * 68)


def display_menu() -> None:
    """Display the primary navigation menu options."""
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
    """Handle interactive user prompt flow for registering a new complaint."""
    print("\n--- [1] REGISTER NEW COMPLAINT ---")
    name = input("Enter Complainant Name: ").strip()
    if not name:
        print("[Error] Complainant name cannot be empty.")
        return

    # Display available categories
    available_cats = category_manager.list_categories()
    print("\nAvailable Categories:")
    for idx, cat in enumerate(available_cats, start=1):
        dept = category_manager.get_department(cat)
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

    cid = complaint_manager.register_complaint(
        name=name,
        category=selected_cat,
        description=description,
        priority=priority_input,
    )
    rec = complaint_manager.get_complaint(cid)
    print(f"\n[Success] Complaint successfully registered!")
    print(f"  -> Generated Complaint ID : {cid}")
    print(f"  -> Routed Department     : {rec.get('department')}")
    print(f"  -> Assigned Priority      : {rec.get('priority')}")
    print(f"  -> Status                 : {rec.get('status')}")


def handle_assign_update() -> None:
    """Handle assignment, status transitions, priority modifications, and escalations."""
    print("\n--- [2] ASSIGN / UPDATE COMPLAINT LIFECYCLE ---")
    cid = input("Enter Complaint ID (e.g. CMP1001): ").strip().upper()
    if not cid:
        print("[Error] Complaint ID is required.")
        return

    # Verify existence
    rec = complaint_manager.get_complaint(cid)
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
        updated = tracking_manager.assign_complaint(cid, officer)
        print(f"[Success] Assigned to {updated['assigned_to']}. Status updated to {updated['status']}.")

    elif action == "2":
        print(f"\nValid Statuses: {', '.join(tracking_manager.VALID_STATUSES)}")
        new_status = input("Enter New Status: ").strip().upper()
        updated = tracking_manager.update_status(cid, new_status)
        print(f"[Success] Status updated to {updated['status']}.")
        if updated.get("date_resolved"):
            print(f"  -> Stamped Resolution Date: {updated['date_resolved']}")

    elif action == "3":
        print("Valid Priorities: LOW, MEDIUM, HIGH")
        new_priority = input("Enter New Priority: ").strip().upper()
        updated = tracking_manager.update_priority(cid, new_priority)
        print(f"[Success] Priority updated to {updated['priority']}.")

    elif action == "4":
        updated = tracking_manager.escalate_complaint(cid)
        print(f"[Success] Complaint {cid} escalated! Status: {updated['status']}, Priority: {updated['priority']}.")

    elif action == "5":
        print("Action cancelled.")
    else:
        print("[Error] Invalid selection.")


def handle_search_by_status() -> None:
    """Handle searching and displaying complaints filtered by status."""
    print("\n--- [3] SEARCH COMPLAINTS BY STATUS ---")
    print(f"Status options: {', '.join(tracking_manager.VALID_STATUSES)}")
    target_status = input("Enter status to filter by: ").strip()

    matches = analytics.search_complaints_by_status(target_status)
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
    """Handle printing a single complaint's detailed report."""
    print("\n--- [4] VIEW SINGLE COMPLAINT DETAIL REPORT ---")
    cid = input("Enter Complaint ID: ").strip().upper()
    if not cid:
        print("[Error] Complaint ID is required.")
        return

    report_text = reports.generate_complaint_report(cid)
    print("\n" + report_text)


def handle_view_summary_report() -> None:
    """Handle printing the overall executive summary report."""
    print("\n--- [5] EXECUTIVE SUMMARY & ANALYTICS ---")
    summary_text = reports.generate_summary_report()
    print("\n" + summary_text)


def handle_manage_categories() -> None:
    """Handle category inspection and addition."""
    print("\n--- [6] MANAGE CATEGORIES & DEPARTMENTS ---")
    mappings = category_manager.get_all_category_mappings()
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
        category_manager.add_category(cat_name, dept_name)
        print(f"[Success] Added category '{cat_name.title()}' mapped to '{dept_name.title()}'.")


def handle_save_csv() -> None:
    """Explicitly trigger CSV save."""
    print("\n--- [7] SAVE DATA TO CSV ---")
    saved = file_handler.save_complaints_to_csv()
    if saved:
        print("[Success] All complaint data successfully saved to 'data/complaints.csv'.")
    else:
        print("[Warning] Could not complete CSV save.")


def run_interactive_loop() -> None:
    """Execute the primary interactive application loop with exception safety."""
    print_banner()

    # Load existing records on startup
    loaded = file_handler.load_complaints_from_csv()
    if loaded:
        print(f"[Startup] Successfully restored {len(loaded)} complaint record(s) from CSV storage.")
    else:
        print("[Startup] Ready with clean/default storage.")

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
        # Automatic CSV persistence on exit
        saved = file_handler.save_complaints_to_csv()
        if saved:
            print("[Persistence] Auto-save completed to 'data/complaints.csv'. Goodbye!")
        else:
            print("[Persistence Warning] Auto-save could not write data.")


if __name__ == "__main__":
    run_interactive_loop()
