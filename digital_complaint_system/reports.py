"""Report generation module for the Complaint System.

This module produces human-readable, formatted plain-text reports for individual complaints,
executive summaries, and departmental workload distribution.
"""

from typing import Any, Dict

import analytics
import category_manager
import complaint_manager


def generate_complaint_report(complaint_id: str) -> str:
    """Generate a detailed plain-text report for a single complaint.

    Includes full metadata, current assignment status, and complete timestamped status history.

    Args:
        complaint_id: The unique Complaint ID (e.g. 'CMP1001').

    Returns:
        Formatted multi-line plain text report.

    Raises:
        InvalidComplaintIDError: If the complaint ID does not exist.
    """
    record = complaint_manager.get_complaint(complaint_id)

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
    """Generate a high-level summary report of all complaints in the system.

    Aggregates totals, pending/resolved counts, average resolution duration,
    priority breakdown, and category distribution.

    Returns:
        Formatted multi-line plain text summary report.
    """
    all_complaints = complaint_manager.get_all_complaints()
    total_count = len(all_complaints)
    pending_count = analytics.count_pending_complaints(all_complaints)
    resolved_count = total_count - pending_count
    avg_res_time = analytics.average_resolution_time(all_complaints)
    cat_freq = analytics.category_frequency(all_complaints)

    # Status distribution
    status_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for record in all_complaints.values():
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
            dept = category_manager.get_department(cat)
            lines.append(f"   - {cat:<24} ({dept}): {count}")

    lines.append("=" * 64)
    return "\n".join(lines)


def generate_department_report() -> str:
    """Generate a breakdown of complaints and resolution rates by department.

    Returns:
        Formatted multi-line plain text departmental workload report.
    """
    all_complaints = complaint_manager.get_all_complaints()
    dept_stats: Dict[str, Dict[str, int]] = {}

    for record in all_complaints.values():
        dept = record.get("department", "General Administration")
        if dept not in dept_stats:
            dept_stats[dept] = {"total": 0, "pending": 0, "resolved": 0}

        dept_stats[dept]["total"] += 1
        st = record.get("status", "").upper()
        if st in ("RESOLVED", "CLOSED"):
            dept_stats[dept]["resolved"] += 1
        else:
            dept_stats[dept]["pending"] += 1

    lines = [
        "=" * 64,
        "      DEPARTMENTAL WORKLOAD & PERFORMANCE REPORT",
        "=" * 64,
    ]

    if not dept_stats:
        lines.append("   (No departmental data available)")
    else:
        for dept, stats in sorted(dept_stats.items()):
            lines.append(f" Department: {dept}")
            lines.append(f"   - Total Assigned : {stats['total']}")
            lines.append(f"   - Pending        : {stats['pending']}")
            lines.append(f"   - Resolved       : {stats['resolved']}")
            lines.append("-" * 64)

    lines.append("=" * 64)
    return "\n".join(lines)
