"""
CSA-0801: Python Programming - Module 06
Topic: Demonstration of Relational CRUD & Transcript Analytics

Key Concepts Covered:
1. Database population and transaction rollbacks
2. CRUD Lifecycle (Create, Read, Update, Delete)
3. Relational joins and weighted GPA calculation
4. Parameterized query security
"""

from db_manager import DatabaseManager


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 6.1 - SQLite Relational Database CRUD")
    print("=" * 60)

    # Initialize in-memory SQLite database
    db = DatabaseManager(":memory:")

    print("\n[1] Seeding Courses & Academic Catalog:")
    c1 = db.add_course("CSA-0801", "Python Programming", 4, "Prof. Karnati")
    c2 = db.add_course("CSA-0802", "Data Structures & Algorithms", 4, "Dr. A. Lovelace")
    c3 = db.add_course("CSA-0803", "Database Management Systems", 3, "Dr. E. F. Codd")
    print(f"  * Seeded 3 courses (IDs: {c1}, {c2}, {c3})")

    print("\n[2] Student Registration & Profile Management:")
    s1 = db.add_student("STU-101", "Nikhil Karnati", "nikhil@csa.edu", "Computer Science")
    s2 = db.add_student("STU-102", "Priya Sharma", "priya@csa.edu", "AI & Robotics")
    s3 = db.add_student("STU-103", "Rahul Verma", "rahul@csa.edu", "Information Technology")
    print(f"  * Enrolled 3 students (STU-101, STU-102, STU-103)")

    print("\n[3] Course Enrollments & Grade Allocations:")
    db.enroll_student_in_course("STU-101", "CSA-0801")
    db.enroll_student_in_course("STU-101", "CSA-0802")
    db.enroll_student_in_course("STU-101", "CSA-0803")

    db.add_grade("STU-101", "CSA-0801", 96.5, "O", semester=4)
    db.add_grade("STU-101", "CSA-0802", 91.0, "O", semester=4)
    db.add_grade("STU-101", "CSA-0803", 86.0, "A+", semester=4)

    print("\n[4] Generating Academic Transcript (Multi-table SQL JOIN):")
    transcript = db.get_student_transcript("STU-101")
    for rec in transcript:
        print(f"  * [{rec['course_code']}] {rec['course_title']:<30} Credits: {rec['credits']} Marks: {rec['marks']:<5} Grade: {rec['grade_letter']}")

    gpa = db.compute_student_gpa("STU-101")
    print(f"\n  >> Cumulative Weighted GPA for STU-101: {gpa} / 10.0")

    print("\n[5] Testing Update & Delete CRUD Operations:")
    db.update_student("STU-103", full_name="Rahul V. Verma", email="rahul.v@csa.edu")
    updated_stu = db.get_student_by_roll("STU-103")
    print(f"  * Updated Record: {updated_stu['full_name']} <{updated_stu['email']}>")

    deleted = db.delete_student("STU-103")
    print(f"  * Deleted STU-103? {deleted} (Verify: {db.get_student_by_roll('STU-103')})")

    print("\n[OK] Lab 6.1 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
