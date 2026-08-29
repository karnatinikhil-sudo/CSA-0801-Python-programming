<div align="center">

# 🐍 CSA-0801: Python Programming
### Comprehensive Academic Coursework, Hands-on Lab Suite & Capstone Project

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-25%2F25%20Passing-brightgreen.svg?logo=pytest&logoColor=white)](tests/)
[![Standard Library](https://img.shields.io/badge/Dependencies-Zero%20External%20(Pure%20StdLib)-success.svg)]()
[![GUI](https://img.shields.io/badge/Desktop%20GUI-Tkinter%20%2F%20ttk-orange.svg)]()
[![Database](https://img.shields.io/badge/Database-SQLite3%20ACID-003B57.svg?logo=sqlite&logoColor=white)](06_database_operations/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*An industry-grade, curriculum-aligned academic repository covering foundational to advanced Python programming, custom data structures, object-oriented design patterns, database systems, desktop GUI applications, and an interactive Student Academic & Wellness Management Capstone System.*

</div>

---

## 📚 Table of Contents

- [Overview & Objectives](#-overview--objectives)
- [Repository Architecture](#-repository-architecture)
- [Curriculum & Lab Modules Breakdown](#-curriculum--lab-modules-breakdown)
  - [Unit 01: Basics & Control Flow](#unit-01-basics--control-flow)
  - [Unit 02: Built-in & Custom Data Structures](#unit-02-built-in--custom-data-structures)
  - [Unit 03: Object-Oriented Programming & Design Patterns](#unit-03-object-oriented-programming--design-patterns)
  - [Unit 04: File Handling & Exception Management](#unit-04-file-handling--exception-management)
  - [Unit 05: Python Standard Library & Concurrency](#unit-05-python-standard-library--concurrency)
  - [Unit 06: Relational Database Operations (SQLite3)](#unit-06-relational-database-operations-sqlite3)
  - [Unit 07: Desktop GUI Applications (Tkinter / ttk)](#unit-07-desktop-gui-applications-tkinter--ttk)
  - [Unit 08: Capstone Project](#unit-08-capstone-project-student-academic--wellness-management-system)
- [Quick Start Guide](#-quick-start-guide)
- [Interactive Lab Navigator (`run_lab.py`)](#-interactive-lab-navigator-run_labpy)
- [Running the Test Suite](#-running-the-test-suite)
- [Desktop GUI Showcase](#-desktop-gui-showcase)
- [License & Academic Integrity](#-license--academic-integrity)

---

## 🎯 Overview & Objectives

This repository contains the complete practical and theoretical implementations for **CSA-0801: Python Programming**. It is designed to provide:
1. **Curriculum Completeness**: From elementary syntax and algorithms to production-grade architecture.
2. **Zero Dependency Friction**: Core execution runs entirely out-of-the-box using the Python Standard Library (`tkinter`, `sqlite3`, `pathlib`, `concurrent.futures`, `asyncio`, `dataclasses`).
3. **Automated Verification**: Comprehensive unit testing suite covering algorithms, data structures, and database services.
4. **Capstone System**: A full-stack desktop and terminal system modeling real-world academic performance and wellness analytics.

---

## 🏛️ Repository Architecture

```
CSA-0801-Python-programming/
├── 01_basics_and_control_flow/
│   ├── 01_variables_and_datatypes.py      # Primitive types, type casting, memory model
│   ├── 02_operators_and_expressions.py    # Arithmetic, bitwise logic, operator precedence
│   ├── 03_conditional_statements.py       # Branching, grading matrices, match-case pattern matching
│   ├── 04_loops_and_iterations.py         # Sieve of Eratosthenes, loop-else, ASCII patterns
│   └── 05_functions_and_recursion.py      # *args/**kwargs, decorators, closures, memoized recursion
├── 02_data_structures/
│   ├── 01_lists_and_tuples.py             # Slicing, list comprehensions, matrix transpose, unpacking
│   ├── 02_dictionaries_and_sets.py        # Defaultdicts, word frequency, set algebra
│   ├── 03_strings_and_regex.py            # Regex validators (email, phone, roll), server log parser
│   └── 04_custom_data_structures.py       # Pure Python Generic Stack, Singly Linked List, and BST
├── 03_object_oriented_programming/
│   ├── 01_classes_and_objects.py          # Class vs instance variables, classmethods, staticmethods
│   ├── 02_inheritance_and_polymorphism.py # ABCs, multiple inheritance, mixins, MRO linearization
│   ├── 03_encapsulation_and_dunder.py     # Name mangling, @property, operator overloading (GradeVector)
│   └── 04_design_patterns.py              # Singleton, Factory, and Observer (Pub-Sub) patterns
├── 04_file_handling_and_exceptions/
│   ├── 01_file_io_operations.py           # Context managers, stream seek/tell, CSV & JSON processing
│   ├── 02_exception_handling.py           # Custom exception hierarchy, try-except-else-finally
│   └── 03_serialization_and_pickling.py  # Binary pickle vs custom JSON encoders
├── 05_modules_and_standard_lib/
│   ├── 01_datetime_and_math.py            # Datetime scheduling, statistics, high-precision Decimal
│   ├── 02_os_sys_pathlib.py               # Pathlib object trees, sys metadata, argparse CLI
│   └── 03_concurrency.py                  # ThreadPoolExecutor, mutex locks, asyncio concurrency
├── 06_database_operations/
│   ├── schema.sql                         # Normalized DDL schema for students, courses, grades
│   ├── db_manager.py                      # Parameterized SQLite3 wrapper with ACID transactions
│   └── demo_crud.py                       # Multi-table SQL JOINs, transcript queries, GPA calculation
├── 07_gui_applications/
│   ├── student_grade_calculator.py        # Desktop Tkinter/ttk GPA & Letter Grade Calculator
│   └── system_monitor_gui.py              # Real-time CPU & Memory hardware monitor with Canvas waveforms
├── 08_capstone_project/
│   ├── models/                            # Student, Course, GradeRecord, WellnessLog entities
│   ├── database/                          # SQLite engine, migrations, and seed dataset
│   ├── services/                          # AcademicService, WellnessService, AnalyticsService, ReportService
│   ├── main.py                            # Interactive colored terminal system
│   └── gui_app.py                         # Multi-tab Tkinter dashboard with live charts & rankings
├── tests/
│   ├── test_basics.py                     # Unit tests for control flow and recursion
│   ├── test_data_structures.py            # Unit tests for custom Stack, Linked List, BST
│   ├── test_oop.py                        # Unit tests for inheritance, encapsulation, patterns
│   ├── test_db_manager.py                 # Unit tests for SQLite CRUD and queries
│   └── test_capstone.py                   # Integration tests for Capstone business logic
├── run_lab.py                             # Interactive CLI launcher and automated lab runner
├── requirements.txt                       # Development dependencies (pytest, rich, tabulate)
├── .gitignore                             # Standard Python gitignore rules
├── LICENSE                                # MIT License
└── README.md                              # Comprehensive documentation & syllabus guide
```

---

## 📖 Curriculum & Lab Modules Breakdown

### Unit 01: Basics & Control Flow
- **`01_variables_and_datatypes.py`**: Explores primitive types, memory caching of small integers, string interning, dynamic type casting pipelines, and formatted string profiles.
- **`02_operators_and_expressions.py`**: Implements arithmetic suites, 8-bit binary bitwise manipulations (`AND`, `OR`, `XOR`, `LSHIFT`, `RSHIFT`), Boolean short-circuiting, and compound interest calculators.
- **`03_conditional_statements.py`**: Academic grading scale conversion, leap year evaluation, and Python 3.10+ Structural Pattern Matching (`match-case`).
- **`04_loops_and_iterations.py`**: Prime number discovery with the Sieve of Eratosthenes ($O(n \log \log n)$), perfect number searching, `for-else` search mechanics, and ASCII geometric pattern generators.
- **`05_functions_and_recursion.py`**: Positional/Keyword argument unpacking (`*args`, `**kwargs`), benchmarking decorators, LRU memoized Fibonacci sequences, Tower of Hanoi recursion, and functional pipelines (`map`, `filter`, `reduce`).

### Unit 02: Built-in & Custom Data Structures
- **`01_lists_and_tuples.py`**: Memory footprint comparisons (List vs Tuple), matrix transpositions, 2D flattening, named tuples, and extended iterable unpacking.
- **`02_dictionaries_and_sets.py`**: Defaultdict corpus tokenization, word frequency ranking, set algebra (Union, Intersection, Difference, Symmetric Difference), and dictionary merge operators (`|`).
- **`03_strings_and_regex.py`**: Compiled regex patterns for email, international phone number, and student roll validation; regex log parsing with named capture groups.
- **`04_custom_data_structures.py`**: Implements from scratch:
  - `Stack[T]`: Generic LIFO structure with overflow protection.
  - `SinglyLinkedList[T]`: Node-based dynamic list with insertion, deletion, and in-place reversal.
  - `BinarySearchTree`: Key-value BST supporting search, insertion, and in-order sorted traversal.

### Unit 03: Object-Oriented Programming & Design Patterns
- **`01_classes_and_objects.py`**: Class attributes vs instance attributes, `@classmethod` factories, `@staticmethod` utilities, and `__repr__` vs `__str__` contract implementations.
- **`02_inheritance_and_polymorphism.py`**: Abstract Base Classes (`abc.ABC`), method overriding, cooperative `super()`, diagnostic mixins, and C3 Linearization Method Resolution Order (`MRO`).
- **`03_encapsulation_and_dunder.py`**: Name mangling (`__attr`), `@property` getter/setter data validation, and operator overloading (`+`, `<`, `==`, `len()`, `in`) via `GradeVector`.
- **`04_design_patterns.py`**: Production-tested patterns:
  - **Singleton**: Global thread-safe configuration manager.
  - **Factory**: Polymorphic course object instantiator.
  - **Observer**: Publish-subscribe academic event dispatch bus.

### Unit 04: File Handling & Exception Management
- **`01_file_io_operations.py`**: Safe file context managers (`with`), file pointer mechanics (`seek()` and `tell()`), CSV enrichment via `csv.DictReader`/`csv.DictWriter`, and JSON round-trip serialization.
- **`02_exception_handling.py`**: Domain exception hierarchy (`StudentNotFoundError`, `DuplicateEnrollmentError`, `InvalidGradeRangeError`) with `try-except-else-finally` lifecycle guarantees.
- **`03_serialization_and_pickling.py`**: Binary object marshaling via `pickle` vs standard `json.JSONEncoder` for datetime and custom domain instances.

### Unit 05: Python Standard Library & Concurrency
- **`01_datetime_and_math.py`**: ISO date parsing, semester milestones timeline calculation, descriptive cohort statistics (`mean`, `median`, `stdev`, `variance`), and exact `decimal.Decimal` financial computing.
- **`02_os_sys_pathlib.py`**: Object-oriented path hierarchies (`pathlib.Path`), file tree globbing, environment inspections, and command-line argument parsing (`argparse`).
- **`03_concurrency.py`**: Multi-threading with `ThreadPoolExecutor` and mutex locks, CPU-bound multiprocessing, and asynchronous I/O with `asyncio.gather()`.

### Unit 06: Relational Database Operations (SQLite3)
- **`schema.sql`**: Relational tables with Foreign Keys and cascade deletions (`students`, `courses`, `enrollments`, `grade_records`, `attendance_logs`).
- **`db_manager.py`**: Enterprise database connection manager with context-managed ACID transactions, parameterized queries (SQL injection prevention), and multi-table SQL JOIN queries.
- **`demo_crud.py`**: End-to-end CRUD demonstration and automated credit-weighted GPA calculations.

### Unit 07: Desktop GUI Applications (Tkinter / ttk)
- **`student_grade_calculator.py`**: Desktop GPA Calculator featuring course entry, credit weighting, real-time KPI cards, Treeview tables, and CSV/JSON export.
- **`system_monitor_gui.py`**: Real-time diagnostic monitor tracking CPU and Memory metrics with animated Tkinter Canvas line waveforms.

---

### Unit 08: Capstone Project: Student Academic & Wellness Management System

The capstone integrates all course topics into a full-scale academic and wellness intelligence platform.

#### Key Modules:
- **`models/`**: Domain dataclasses (`Student`, `Course`, `GradeRecord`, `WellnessLog`).
- **`database/`**: SQLite engine (`CapstoneDBEngine`) with auto-migrations and seed data.
- **`services/`**:
  - `AcademicService`: Student registration, transcript generation, credit-weighted GPA ranking.
  - `WellnessService`: Tracks study habits, sleep, stress scores, and computes the holistic **Wellness Index (0-100)** and **Burnout Risk**.
  - `AnalyticsService`: Cohort statistics, grade distributions, and executive KPI summaries.
  - `ReportService`: Generates formatted ASCII Report Cards and JSON data export packages.
- **`main.py`**: Interactive terminal command interface.
- **`gui_app.py`**: Multi-tab Tkinter desktop suite with live cards, leaderboards, transcript viewer, and wellness matrices.

```
+----------------------------------------------------------------------+
|              ACADEMIC & WELLNESS COMPREHENSIVE DOSSIER               |
+----------------------------------------------------------------------+
| Student ID  : STU-101              Department : Computer Science     |
| Full Name   : Nikhil Karnati       Semester   : 4                    |
| Email       : nikhil@csa.edu                                         |
+----------------------------------------------------------------------+
|                      COURSE TRANSCRIPT & GRADES                      |
+----------------------------------------------------------------------+
| Code       | Course Title                 | Cred | Marks | Grade     |
+----------------------------------------------------------------------+
| CSA-0801   | Python Programming           | 4    | 96.0  | O         |
| CSA-0802   | Data Structures & Algorithms | 4    | 92.5  | O         |
| CSA-0803   | Relational Database Mgmt     | 3    | 88.0  | A+        |
| MATH-201   | Linear Algebra & Probability | 3    | 91.0  | O         |
+----------------------------------------------------------------------+
| Cumulative GPA: 9.79 / 10.0    | Total Earned Credits: 14            |
+----------------------------------------------------------------------+
|                   WELLNESS & HEALTH BALANCE INDEX                    |
+----------------------------------------------------------------------+
| Daily Study : 4.5 hrs/day         Daily Sleep : 7.5 hrs/night        |
| Stress Level: 3/10                Exercise    : 45 mins/day          |
| Wellness Score: 94.0/100.0        Burnout Risk: LOW RISK             |
+----------------------------------------------------------------------+
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/karnatinikhil-sudo/CSA-0801-Python-programming.git
cd CSA-0801-Python-programming
```

### 2. Run Any Individual Lab Module
```bash
# Example: Run Module 01 Variables & Memory Model
python 01_basics_and_control_flow/01_variables_and_datatypes.py

# Example: Run Module 02 Custom Data Structures (Stack, Linked List, BST)
python 02_data_structures/04_custom_data_structures.py

# Example: Run Module 06 SQLite Database Operations
python 06_database_operations/demo_crud.py
```

### 3. Launch the Interactive Lab Navigator
```bash
python run_lab.py
```

---

## 🕹️ Interactive Lab Navigator (`run_lab.py`)

The root `run_lab.py` script provides an interactive menu to explore any unit, run automated tests, or launch the capstone.

```
============================================================================
  CSA-0801: PYTHON PROGRAMMING - ACADEMIC COURSEWORK & LAB SUITE
  Saveetha / SRM / University Engineering Curriculum Edition
============================================================================
  COURSE MODULES:
   [1] Unit 01: Basics & Control Flow (5 Labs)
   [2] Unit 02: Built-in & Custom Data Structures (4 Labs)
   [3] Unit 03: Object-Oriented Programming & Design Patterns (4 Labs)
   [4] Unit 04: File Handling & Exception Management (3 Labs)
   [5] Unit 05: Python Standard Library & Concurrency (3 Labs)
   [6] Unit 06: Relational Database Operations (SQLite3) (1 Labs)
   [7] Unit 07: Desktop GUI Applications (Tkinter / ttk) (2 Labs)
   [8] Unit 08: Capstone Project (1 Labs)

  ACTIONS & TOOLS:
   [T] Run All Automated Unit Tests (unittest)
   [A] Run All Lab Demonstrations (Batch)
   [C] Launch Capstone System (CLI Menu / GUI)
   [G] Launch Capstone Desktop GUI Directly
   [Q] Quit
============================================================================
```

---

## 🧪 Running the Test Suite

All 25 unit and integration tests can be executed with zero configuration via `unittest`:

```bash
# Using the built-in test runner:
python run_lab.py --test

# Or using standard unittest discovery:
python -m unittest discover -s tests -p "test_*.py"

# Or using pytest (if installed):
pytest tests/ -v
```

### Test Coverage Highlights:
| Test File | Target Module | Scope |
|---|---|---|
| `test_basics.py` | Unit 01 | Type conversions, operators, grading, primes, recursion |
| `test_data_structures.py` | Unit 02 | Matrix operations, word frequency, regex validation, Stack, LL, BST |
| `test_oop.py` | Unit 03 | Inheritance, MRO, encapsulation, operator overloading, design patterns |
| `test_db_manager.py` | Unit 06 | SQLite schema, transactions, student/course CRUD, transcript calculations |
| `test_capstone.py` | Unit 08 | Capstone entities, academic rankings, wellness scoring, burnout alerts |

---

## 💻 Desktop GUI Showcase

### 1. Capstone Academic & Wellness Management Suite
```bash
python 08_capstone_project/gui_app.py
```
*Features multi-tab navigation: Dashboard Analytics, Student Leaderboards, Transcript Viewer, and Wellness Matrices.*

### 2. Student Grade & GPA Calculator
```bash
python 07_gui_applications/student_grade_calculator.py
```
*Interactive credit-weighted GPA calculator with CSV/JSON export.*

### 3. Real-Time Hardware & System Diagnostics
```bash
python 07_gui_applications/system_monitor_gui.py
```
*Live CPU & RAM telemetry with dynamic Canvas waveforms.*

---

## 📄 License & Academic Integrity

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed by **Nikhil Karnati** for **CSA-0801: Python Programming**.
Designed for computer science students, educators, and software engineers seeking a rigorous reference codebase.