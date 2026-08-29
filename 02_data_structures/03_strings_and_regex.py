"""
CSA-0801: Python Programming - Module 02
Topic: Strings, Text Processing, Regular Expressions, and Validation

Key Concepts Covered:
1. String manipulation (split, join, strip, replace, zfill, case conversions)
2. Regular Expression matching and compilation (re.search, re.findall, re.sub)
3. Input validation patterns (Email, Phone Numbers, Roll Numbers, IP Addresses)
4. Log parsing and token extraction
"""

import re
from typing import Any


class InputValidator:
    """Validates user input patterns using compiled regular expressions."""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_REGEX = re.compile(r"^\+?(\d{1,3})?[-. ]?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}$")
    ROLL_REGEX = re.compile(r"^CSA-\d{4}-\d{4}$")
    IPV4_REGEX = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

    @classmethod
    def validate_email(cls, email: str) -> bool:
        return bool(cls.EMAIL_REGEX.match(email.strip()))

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        return bool(cls.PHONE_REGEX.match(phone.strip()))

    @classmethod
    def validate_roll_no(cls, roll: str) -> bool:
        return bool(cls.ROLL_REGEX.match(roll.strip()))


def parse_server_logs(log_entries: list[str]) -> list[dict[str, Any]]:
    """
    Parses common log formats into structured dictionaries using regex capture groups.
    Pattern: [TIMESTAMP] [LEVEL] [IP] - MESSAGE
    """
    log_pattern = re.compile(r"^\[(?P<timestamp>[^\]]+)\]\s+\[(?P<level>\w+)\]\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+(?P<message>.*)$")

    parsed_logs = []
    for entry in log_entries:
        match = log_pattern.match(entry)
        if match:
            parsed_logs.append(match.groupdict())
    return parsed_logs


def sanitize_text(raw_text: str) -> str:
    """Masks sensitive information (e.g. phone numbers, email handles) in text."""
    # Mask emails: user@domain.com -> u***@domain.com
    masked = re.sub(
        r"\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b",
        r"\1***\2",
        raw_text
    )
    return masked


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 2.3 - Strings, Regex & Pattern Validation")
    print("=" * 60)

    print("\n[1] Input Validation Matrix:")
    test_emails = ["nikhil@example.com", "invalid-email@", "student.csa@univ.edu.in", "bad@.com"]
    for email in test_emails:
        valid = InputValidator.validate_email(email)
        print(f"  * Email: {email:<30} -> Valid: {valid}")

    test_rolls = ["CSA-2026-0801", "csa-2026-1", "CSA-2025-9999", "INVALID-ROLL"]
    for r in test_rolls:
        valid = InputValidator.validate_roll_no(r)
        print(f"  * Roll No: {r:<28} -> Valid: {valid}")

    print("\n[2] Log Parser (Regex Named Capture Groups):")
    sample_logs = [
        "[2026-08-29 10:15:32] [INFO] 192.168.1.10 - User login successful for student STU-101",
        "[2026-08-29 10:16:04] [WARNING] 10.0.0.5 - High memory utilization detected (88%)",
        "[2026-08-29 10:17:12] [ERROR] 172.16.0.4 - Database connection timeout on port 5432",
    ]
    parsed = parse_server_logs(sample_logs)
    for p in parsed:
        print(f"  * [{p['level']}] from {p['ip']} at {p['timestamp']} -> {p['message']}")

    print("\n[3] Text Masking & Sanitization:")
    text_to_mask = "Contact student coordinator at nikhil.karnati@university.edu or support@csa0801.org"
    print(f"  * Original: {text_to_mask}")
    print(f"  * Masked:   {sanitize_text(text_to_mask)}")

    print("\n[OK] Lab 2.3 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
