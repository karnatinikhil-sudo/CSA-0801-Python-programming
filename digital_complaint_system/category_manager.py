"""Category and department management for the Complaint System.

This module maintains the collection of recognized complaint and crime categories (as a set)
and provides routing mechanisms to automatically assign complaints to responsible
departments via category-to-department mappings, with specialized routing for critical crimes.
"""

from typing import Dict, List, Set, Tuple

# Internal data structures
categories: Set[str] = set()
category_department_map: Dict[str, str] = {}

# Default department when category is unmapped
DEFAULT_DEPARTMENT: str = "General Administration"

# Critical violent crime categories that trigger high-priority alerts
CRITICAL_CRIME_CATEGORIES: Tuple[str, ...] = (
    "Homicide & Murder",
    "Sexual Assault & Harassment",
    "Armed Robbery & Gang Crime",
    "Kidnapping & Human Trafficking",
    "Violent Assault & Battery",
)

# Initial seed data for standard municipal and law enforcement workflows
_DEFAULT_MAPPINGS: Dict[str, str] = {
    # High-Priority Critical Crime Categories
    "Homicide & Murder": "Special Crime Investigation & Homicide Unit",
    "Sexual Assault & Harassment": "Women & Child Protection Cell",
    "Armed Robbery & Gang Crime": "Anti-Robbery & Special Operations",
    "Kidnapping & Human Trafficking": "Anti-Human Trafficking & Rescue Unit",
    "Violent Assault & Battery": "Municipal Police & Law Enforcement",
    "Cyber Crime & Fraud": "Cyber Crime Investigation Cell",
    "Public Safety": "Municipal Police & Safety",
    "Public Safety & Weapons": "Municipal Police & Safety",
    # Public Service & Municipal Categories
    "Water Supply": "Water Works Department",
    "Electricity": "Power & Electricity Department",
    "Sanitation": "Public Health & Sanitation",
    "Roads & Infrastructure": "Public Works Department",
    "Billing & Accounts": "Finance & Revenue Department",
}


def _initialize_defaults() -> None:
    """Populate default categories and departmental mappings."""
    global categories, category_department_map
    categories.clear()
    category_department_map.clear()
    for cat, dept in _DEFAULT_MAPPINGS.items():
        categories.add(cat)
        category_department_map[cat] = dept


# Initialize default categories on module load
_initialize_defaults()


def add_category(category_name: str, department_name: str) -> None:
    """Add a new complaint category and map it to a responsible department."""
    cleaned_category = category_name.strip().title()
    cleaned_department = department_name.strip().title()

    if not cleaned_category:
        raise ValueError("Category name cannot be empty.")
    if not cleaned_department:
        raise ValueError("Department name cannot be empty.")

    categories.add(cleaned_category)
    category_department_map[cleaned_category] = cleaned_department


def list_categories() -> List[str]:
    """Retrieve an alphabetically sorted list of all active categories."""
    return sorted(list(categories))


def get_department(category_name: str) -> str:
    """Look up the responsible department for a given complaint category."""
    cleaned = category_name.strip().title()
    return category_department_map.get(cleaned, DEFAULT_DEPARTMENT)


def is_critical_crime_category(category_name: str) -> bool:
    """Check if category is a critical high-priority violent crime."""
    cleaned = category_name.strip().title()
    return cleaned in [c.title() for c in CRITICAL_CRIME_CATEGORIES]


def get_all_category_mappings() -> Dict[str, str]:
    """Retrieve a copy of all category-to-department mappings."""
    return dict(category_department_map)


def reset_categories() -> None:
    """Reset categories and department mappings to initial default state."""
    _initialize_defaults()
