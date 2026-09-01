"""Category and department management for the Complaint System.

This module maintains the collection of recognized complaint categories (as a set)
and provides routing mechanisms to automatically assign complaints to responsible
departments via category-to-department mappings.
"""

from typing import Dict, List, Set

# Internal data structures
categories: Set[str] = set()
category_department_map: Dict[str, str] = {}

# Default department when category is unmapped
DEFAULT_DEPARTMENT: str = "General Administration"

# Initial seed data for standard municipal / organizational workflows
_DEFAULT_MAPPINGS: Dict[str, str] = {
    "Water Supply": "Water Works Department",
    "Electricity": "Power & Electricity Department",
    "Sanitation": "Public Health & Sanitation",
    "Roads & Infrastructure": "Public Works Department",
    "Billing & Accounts": "Finance & Revenue Department",
    "Public Safety": "Municipal Police & Safety",
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
    """Add a new complaint category and map it to a responsible department.

    Validates and normalizes the input strings before adding them to the category
    set and department dictionary.

    Args:
        category_name: The name of the complaint category (e.g., 'Sanitation').
        department_name: The department responsible for handling this category.

    Raises:
        ValueError: If category_name or department_name is empty or whitespace.
    """
    cleaned_category = category_name.strip().title()
    cleaned_department = department_name.strip().title()

    if not cleaned_category:
        raise ValueError("Category name cannot be empty.")
    if not cleaned_department:
        raise ValueError("Department name cannot be empty.")

    # Add to categories set
    categories.add(cleaned_category)
    # Map category to department
    category_department_map[cleaned_category] = cleaned_department


def list_categories() -> List[str]:
    """Retrieve an alphabetically sorted list of all active categories.

    Returns:
        A list of category names stored in the categories set.
    """
    return sorted(list(categories))


def get_department(category_name: str) -> str:
    """Look up the responsible department for a given complaint category.

    If the category has an explicit mapping, that department is returned.
    If the category is recognized or unknown without an explicit map,
    returns the default department.

    Args:
        category_name: The category to look up.

    Returns:
        The name of the responsible department.
    """
    cleaned = category_name.strip().title()
    return category_department_map.get(cleaned, DEFAULT_DEPARTMENT)


def get_all_category_mappings() -> Dict[str, str]:
    """Retrieve a copy of all category-to-department mappings.

    Returns:
        A dictionary mapping category names to department names.
    """
    return dict(category_department_map)


def reset_categories() -> None:
    """Reset categories and department mappings to initial default state."""
    _initialize_defaults()
