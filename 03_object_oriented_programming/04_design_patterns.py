"""
CSA-0801: Python Programming - Module 03
Topic: Python Design Patterns (Singleton, Factory, Observer)

Key Concepts Covered:
1. Singleton Pattern via __new__ for centralized state management
2. Factory Pattern for polymorphic object creation
3. Observer / Publish-Subscribe Pattern for event notifications
"""

from typing import Any, Callable, Optional


# 1. Singleton Pattern
class SystemConfig:
    """Thread-safe Singleton Configuration Manager."""
    _instance: Optional["SystemConfig"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, app_name: str = "CSA Academic Suite", environment: str = "Production"):
        if not getattr(self, "_initialized", False):
            self.app_name = app_name
            self.environment = environment
            self.settings: dict[str, Any] = {"debug": False, "max_sessions": 100}
            self._initialized = True


# 2. Factory Pattern
class Course:
    def __init__(self, code: str, title: str, credits: int):
        self.code = code
        self.title = title
        self.credits = credits

    def get_syllabus_type(self) -> str:
        raise NotImplementedError


class TheoryCourse(Course):
    def get_syllabus_type(self) -> str:
        return "Classroom Lectures & Seminar Sessions"


class LabCourse(Course):
    def get_syllabus_type(self) -> str:
        return "Hands-on Practical Coding & Continuous Evaluation"


class CourseFactory:
    """Factory creating specialized course instances based on type code."""

    @staticmethod
    def create_course(course_type: str, code: str, title: str, credits: int) -> Course:
        c_type = course_type.strip().lower()
        if c_type in ("theory", "lecture"):
            return TheoryCourse(code, title, credits)
        elif c_type in ("lab", "practical"):
            return LabCourse(code, title, credits)
        else:
            raise ValueError(f"Unknown course type: {course_type}")


# 3. Observer Pattern (Pub-Sub)
class AcademicEventBus:
    """Observer Event Bus for broadcasting notifications to subscribers."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[str, Any], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[str, Any], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, payload: Any) -> int:
        listeners = self._subscribers.get(event_type, [])
        for callback in listeners:
            callback(event_type, payload)
        return len(listeners)


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 3.4 - Design Patterns (Singleton, Factory, Observer)")
    print("=" * 60)

    print("\n[1] Singleton Pattern Verification:")
    cfg1 = SystemConfig("CSA System", "Production")
    cfg2 = SystemConfig("Another Name", "Testing")
    print(f"  * Config 1 Instance: {id(cfg1)} (App: {cfg1.app_name})")
    print(f"  * Config 2 Instance: {id(cfg2)} (App: {cfg2.app_name})")
    print(f"  * cfg1 is cfg2:      {cfg1 is cfg2}")

    print("\n[2] Factory Pattern Creation:")
    c1 = CourseFactory.create_course("theory", "CSA-0801", "Python Programming", 4)
    c2 = CourseFactory.create_course("lab", "CSA-0801-L", "Python Programming Lab", 2)
    print(f"  * Created {c1.code} ({c1.__class__.__name__}): {c1.get_syllabus_type()}")
    print(f"  * Created {c2.code} ({c2.__class__.__name__}): {c2.get_syllabus_type()}")

    print("\n[3] Observer Pattern Notification Dispatch:")
    event_bus = AcademicEventBus()

    # Define subscriber listener callbacks
    def email_notifier(event: str, data: Any):
        print(f"    [Email Notification]: Event '{event}' dispatched for student {data}")

    def audit_logger(event: str, data: Any):
        print(f"    [Audit Log]: Event '{event}' logged in security database")

    event_bus.subscribe("GRADE_POSTED", email_notifier)
    event_bus.subscribe("GRADE_POSTED", audit_logger)
    event_bus.subscribe("COURSE_ENROLLED", email_notifier)

    print("  * Publishing 'GRADE_POSTED' event:")
    event_bus.publish("GRADE_POSTED", {"student_id": "STU-101", "grade": "O"})

    print("  * Publishing 'COURSE_ENROLLED' event:")
    event_bus.publish("COURSE_ENROLLED", {"student_id": "STU-102", "course": "CSA-0801"})

    print("\n[OK] Lab 3.4 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
