"""
CSA-0801: Python Programming - Module 03
Topic: Inheritance, Polymorphism, Abstract Base Classes (ABC), and MRO

Key Concepts Covered:
1. Abstract Base Classes (abc.ABC, @abstractmethod) for interface contracts
2. Single, Multiple, and Multilevel Inheritance
3. Method Overriding and super() cooperative method calling
4. Method Resolution Order (MRO / C3 Linearization algorithm)
5. Polymorphism with dynamic dispatch
"""

from abc import ABC, abstractmethod
from typing import Any


# 1. Abstract Base Class (Contract Interface)
class AcademicMember(ABC):
    """Abstract Base Class defining the protocol for university members."""

    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email

    @abstractmethod
    def calculate_workload_hours(self) -> float:
        """Abstract method that derived subclasses must implement."""
        pass

    @abstractmethod
    def get_role_description(self) -> str:
        """Returns the specific institutional role."""
        pass

    def get_contact_card(self) -> str:
        """Concrete template method in base class."""
        return f"[{self.get_role_description()}] {self.name} <{self.email}> (ID: {self.member_id})"


# 2. Single Inheritance Subclasses
class UndergraduateStudent(AcademicMember):
    def __init__(self, member_id: str, name: str, email: str, credit_hours: int):
        super().__init__(member_id, name, email)
        self.credit_hours = credit_hours

    def calculate_workload_hours(self) -> float:
        # Standard rule: 3 hours study per credit hour
        return self.credit_hours * 3.0

    def get_role_description(self) -> str:
        return "Undergraduate Student"


class Professor(AcademicMember):
    def __init__(self, member_id: str, name: str, email: str, courses_taught: int, research_grants: int):
        super().__init__(member_id, name, email)
        self.courses_taught = courses_taught
        self.research_grants = research_grants

    def calculate_workload_hours(self) -> float:
        # 10 hrs per course + 15 hrs per active grant
        return (self.courses_taught * 10.0) + (self.research_grants * 15.0)

    def get_role_description(self) -> str:
        return "Faculty Professor"


# 3. Multiple Inheritance & Cooperative super() (Diamond Problem Demo)
class LoggableMixin:
    """Mixin class for automated diagnostic logging."""
    def log_event(self, message: str) -> str:
        return f"[LOG - {self.__class__.__name__}]: {message}"


class TeachingAssistant(UndergraduateStudent, LoggableMixin):
    """Multiple inheritance combining Student capabilities and Mixin logging."""
    def __init__(self, member_id: str, name: str, email: str, credit_hours: int, lab_sections: int):
        super().__init__(member_id, name, email, credit_hours)
        self.lab_sections = lab_sections

    def calculate_workload_hours(self) -> float:
        # Student coursework + 6 hrs per lab section
        student_hours = super().calculate_workload_hours()
        return student_hours + (self.lab_sections * 6.0)

    def get_role_description(self) -> str:
        return "Graduate Teaching Assistant (TA)"


# 4. Polymorphic Dispatch Function
def print_department_roster(members: list[AcademicMember]) -> list[dict[str, Any]]:
    """Demonstrates runtime polymorphism over heterogeneous AcademicMember objects."""
    report = []
    for member in members:
        report.append({
            "card": member.get_contact_card(),
            "role": member.get_role_description(),
            "workload": member.calculate_workload_hours()
        })
    return report


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 3.2 - Inheritance, ABCs & Polymorphism")
    print("=" * 60)

    print("\n[1] Polymorphic Subclass Instances:")
    members: list[AcademicMember] = [
        UndergraduateStudent("STU-101", "Nikhil Karnati", "nikhil@csa.edu", credit_hours=18),
        Professor("FAC-007", "Dr. A. Turing", "turing@csa.edu", courses_taught=2, research_grants=1),
        TeachingAssistant("TA-204", "Priya Sharma", "priya@csa.edu", credit_hours=12, lab_sections=2),
    ]

    for item in print_department_roster(members):
        print(f"  * {item['card']}")
        print(f"    Workload: {item['workload']} hours/week")

    print("\n[2] Mixin Capabilities (Multiple Inheritance):")
    ta = members[2]
    if isinstance(ta, TeachingAssistant):
        print(f"  * {ta.log_event('Graded 45 lab submissions for Module 03')}")

    print("\n[3] Method Resolution Order (MRO / C3 Linearization):")
    print(f"  * TeachingAssistant MRO:")
    for idx, cls_item in enumerate(TeachingAssistant.__mro__, 1):
        print(f"    {idx}. {cls_item.__name__}")

    print("\n[OK] Lab 3.2 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
