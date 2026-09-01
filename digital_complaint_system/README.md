# Digital Complaint Registration and Tracking System

A robust, production-grade Python 3 console application designed for municipal and organizational public service incident tracking, automated departmental routing, lifecycle status tracking, statistical analytics, and reporting.

---

## 📌 Project Overview

The **Digital Complaint Registration and Tracking System** streamlines how citizen complaints are recorded, assigned, prioritized, escalated, resolved, and audited. Built entirely with the **Python 3 Standard Library** (Python 3.9+), the application operates without any third-party package dependencies.

---

## 📁 Project Architecture & File Structure

```
digital_complaint_system/
├── complaint_manager.py       # Core complaint registration and in-memory CRUD operations
├── category_manager.py        # Set-based categories and category-to-department routing
├── tracking_manager.py        # Staff assignment, status lifecycle, priority, escalation
├── analytics.py               # Aggregation metrics, resolution times, status filtering, SLA alerts
├── reports.py                 # Detail, summary, and departmental plain-text reports
├── file_handler.py            # CSV read/write persistence with JSON timeline serialization
├── exceptions.py              # Domain exception hierarchy (ComplaintSystemError)
├── main.py                    # Interactive console UI loop with safe exception handling
├── tests/
│   ├── __init__.py
│   └── test_complaint_system.py # Automated test suite (Python unittest)
├── data/                      # Auto-created runtime directory for CSV storage
│   └── complaints.csv
├── requirements.txt           # Standard library declaration (0 external dependencies)
└── README.md                  # Project documentation and execution instructions
```

---

## 🚀 How to Run the Application

### Prerequisites
- **Python 3.9+** installed on your system.
- No external packages (`pip install`) required.

### Launching the Application
Navigate to the project root directory and execute `main.py`:

```bash
cd digital_complaint_system
python main.py
```

### Interactive Menu Options
```text
====================================================================
   DIGITAL COMPLAINT REGISTRATION AND TRACKING SYSTEM
   Municipal & Public Service Incident Management Console
====================================================================

----------------------------------------
               MAIN MENU
----------------------------------------
 [1] Register New Complaint
 [2] Assign / Update Complaint Lifecycle
 [3] Search Complaints by Status
 [4] View Single Complaint Detail Report
 [5] View Executive Summary & Analytics
 [6] Manage Categories & Departments
 [7] Save Data to CSV
 [8] Exit Program
----------------------------------------
```

---

## 🧪 Testing Framework & Automated Tests

The test suite is built using Python's built-in **`unittest`** framework (`unittest.TestCase`).

### Running the Test Suite
Execute the test runner from the `digital_complaint_system/` root:

```bash
# Run all tests with verbose output
python -m unittest discover -s tests -v

# Or run the specific test file directly
python -m unittest tests/test_complaint_system.py -v
```

### Mandated Test Scenarios Covered
The test suite implements and validates all 8 core assignment scenarios:
1. **Valid Registration**: Generates unique `CMPxxxx` identifier with initial status `REGISTERED`.
2. **Priority Defaulting**: Invalid priority input safely defaults to `MEDIUM` without raising exceptions.
3. **Staff Assignment**: Assigning staff updates `assigned_to` and transitions status to `ASSIGNED`.
4. **Full Lifecycle & Audit Trail**: Comprehensive status transitions (`REGISTERED` $\to$ `ASSIGNED` $\to$ `IN_PROGRESS` $\to$ `ESCALATED` $\to$ `RESOLVED` $\to$ `CLOSED`) maintain an immutable timestamped `status_history`.
5. **Safe Status Search**: Searching by unknown/empty status returns `[]` without raising errors.
6. **Error on Missing ID**: Accessing non-existent Complaint ID raises `InvalidComplaintIDError`.
7. **CSV Persistence Round-trip**: Saving and reloading complaints from CSV preserves all fields, timestamps, and history.
8. **Safe Division Guard**: Calculating average resolution duration with zero resolved records returns `0.0` safely.

---

## ⚙️ Module Responsibilities

| Module | Core Responsibility |
| :--- | :--- |
| `exceptions.py` | Defines `ComplaintSystemError` base class and specialized domain exceptions (`InvalidComplaintIDError`, `InvalidStatusError`, `DuplicateComplaintError`). |
| `category_manager.py` | Manages active complaint categories as a `set` and maps categories to responsible municipal departments. |
| `complaint_manager.py` | Auto-generates incremental IDs (`CMP1001`, `CMP1002`, ...), normalizes fields (`.strip().title()`), and handles in-memory storage. |
| `tracking_manager.py` | Enforces `VALID_STATUSES`, manages assignments, priorities, escalations, and appends timestamped entries to `status_history`. |
| `analytics.py` | Provides pending counts, case-insensitive status searching, category frequencies, average resolution time, and overdue complaint detection. |
| `reports.py` | Generates formatted, plain-text reports for single complaints, executive summaries, and department workloads. |
| `file_handler.py` | Handles CSV persistence with `csv.DictWriter` / `DictReader` and serializes `status_history` via `json.dumps()`, catching `OSError`/`IOError`. |
| `main.py` | Interactive CLI menu loop wrapped in `try/except ComplaintSystemError/except Exception/finally` with startup loading and auto-save on shutdown. |

---

## 💾 CSV Data Persistence Format

Complaints are stored in `data/complaints.csv` using standard CSV with header fields:
- `complaint_id`: String (e.g. `CMP1001`)
- `complainant`: Normalized name string
- `category`: Complaint category
- `department`: Automatically routed department name
- `description`: Detailed text description
- `priority`: `LOW`, `MEDIUM`, or `HIGH`
- `status`: `REGISTERED`, `ASSIGNED`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`, or `CLOSED`
- `assigned_to`: Name of officer/technician or empty string
- `date_registered`: Timestamp formatted as `YYYY-MM-DD HH:MM:SS`
- `date_resolved`: Timestamp formatted as `YYYY-MM-DD HH:MM:SS` or empty string
- `status_history`: JSON-serialized list of `[status, timestamp]` pairs

---

## 🛡️ Exception Hierarchy

```
Exception
   └── ComplaintSystemError (Base domain exception)
         ├── InvalidComplaintIDError
         ├── InvalidStatusError
         └── DuplicateComplaintError
```
