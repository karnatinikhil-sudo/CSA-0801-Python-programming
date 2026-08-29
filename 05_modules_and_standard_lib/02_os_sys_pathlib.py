"""
CSA-0801: Python Programming - Module 05
Topic: System Programming, Filesystem Navigation with Pathlib, and CLI Parsing

Key Concepts Covered:
1. Object-oriented filesystem operations using `pathlib.Path`
2. Environment variables, process information, and working directories via `os`
3. Runtime system configuration, sys.argv, and interpreter metadata via `sys`
4. Building professional CLI tools with the standard `argparse` module
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def inspect_system_environment() -> dict[str, Any]:
    """Inspects Python interpreter environment and OS runtime parameters."""
    return {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "executable": sys.executable,
        "process_id": os.getpid(),
        "current_working_dir": os.getcwd(),
        "user_home": str(Path.home()),
    }


def demonstrate_pathlib_operations(base_dir: Path) -> dict[str, Any]:
    """Demonstrates creating nested directory trees, globbing, and file inspections."""
    docs_dir = base_dir / "academic_records" / "2026"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy files
    (docs_dir / "csa_0801_syllabus.pdf").touch()
    (docs_dir / "csa_0801_grades.csv").touch()
    (docs_dir / "csa_0801_notes.txt").touch()

    # Discover files via globbing
    all_files = list(base_dir.rglob("*.*"))

    file_details = []
    for f in all_files:
        if f.is_file():
            file_details.append({
                "name": f.name,
                "stem": f.stem,
                "suffix": f.suffix,
                "parent": str(f.parent.name),
                "is_absolute": f.is_absolute()
            })

    return {
        "base_created": str(docs_dir),
        "total_files": len(file_details),
        "file_details": file_details,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    """Builds a standard command-line argument parser for the lab suite."""
    parser = argparse.ArgumentParser(
        prog="csa-cli",
        description="CSA-0801 Python Programming Academic CLI Tool"
    )
    parser.add_argument("--course", default="CSA-0801", help="Target Course Code")
    parser.add_argument("--students", type=int, default=60, help="Number of students in cohort")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose diagnostics")
    return parser


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 5.2 - System Programming & Pathlib Navigation")
    print("=" * 60)

    print("\n[1] Runtime Interpreter & OS Metadata:")
    env = inspect_system_environment()
    for k, v in env.items():
        print(f"  * {k:<22}: {v}")

    print("\n[2] Object-Oriented Pathlib Hierarchy:")
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_res = demonstrate_pathlib_operations(Path(tmp_dir))
        print(f"  * Created Tree: {path_res['base_created']}")
        print(f"  * Total Files Created: {path_res['total_files']}")
        for f in path_res["file_details"]:
            print(f"    - File: {f['name']:<22} (Stem: {f['stem']:<15} Suffix: {f['suffix']:<5})")

    print("\n[3] CLI Argument Parser Demonstration:")
    parser = build_argument_parser()
    sample_args = parser.parse_args(["--course", "CSA-0801-AI", "--students", "75", "--verbose"])
    print(f"  * Parsed Arguments: Course={sample_args.course}, Students={sample_args.students}, Verbose={sample_args.verbose}")

    print("\n[OK] Lab 5.2 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
