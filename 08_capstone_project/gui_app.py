"""
CSA-0801: Python Programming - Capstone Desktop GUI
Student Academic & Wellness Management System (Tkinter & ttk)
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# Ensure local package path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.db_engine import CapstoneDBEngine
from models.student import Student
from models.course import Course
from models.grade_record import GradeRecord
from models.wellness_log import WellnessLog
from services.academic_service import AcademicService
from services.wellness_service import WellnessService
from services.analytics_service import AnalyticsService
from services.report_service import ReportService


class CapstoneAppGUI:
    """Multi-tab Desktop Suite for Student Academics and Wellness Analytics."""

    def __init__(self, root: tk.Tk, db_engine: CapstoneDBEngine = None):
        self.root = root
        self.root.title("CSA-0801: Academic & Wellness Management Suite")
        self.root.geometry("950x700")
        self.root.minsize(850, 600)

        self.db = db_engine or CapstoneDBEngine("csa_capstone_academic.db")
        self.db.seed_initial_demo_data()

        self.academic = AcademicService(self.db)
        self.wellness = WellnessService(self.db)
        self.analytics = AnalyticsService(self.db)
        self.reports = ReportService(self.db)

        self._init_theme()
        self._build_tabs()

    def _init_theme(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[12, 6])
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground="#0f172a")
        self.style.configure("SubHeader.TLabel", font=("Helvetica", 10), foreground="#64748b")
        self.style.configure("CardTitle.TLabel", font=("Helvetica", 9), foreground="#64748b")
        self.style.configure("CardVal.TLabel", font=("Helvetica", 18, "bold"), foreground="#2563eb")

    def _build_tabs(self):
        # Top banner
        banner = ttk.Frame(self.root, padding="14 10")
        banner.pack(fill=tk.X)
        ttk.Label(banner, text="Academic & Wellness Management System", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(banner, text="CSA-0801 Python Programming Capstone Project", style="SubHeader.TLabel").pack(anchor=tk.W)

        # Tabbed Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Tabs
        self.tab_dashboard = ttk.Frame(self.notebook, padding="10")
        self.tab_students = ttk.Frame(self.notebook, padding="10")
        self.tab_grades = ttk.Frame(self.notebook, padding="10")
        self.tab_wellness = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.tab_dashboard, text=" Dashboard & Analytics ")
        self.notebook.add(self.tab_students, text=" Students & Leaderboard ")
        self.notebook.add(self.tab_grades, text=" Grades & Transcript ")
        self.notebook.add(self.tab_wellness, text=" Wellness & Health Index ")

        self._build_dashboard_tab()
        self._build_students_tab()
        self._build_grades_tab()
        self._build_wellness_tab()

    # 1. Dashboard Tab
    def _build_dashboard_tab(self):
        cards_frame = ttk.Frame(self.tab_dashboard)
        cards_frame.pack(fill=tk.X, pady=(0, 12))

        # Card 1: Total Students
        c1 = ttk.Frame(cards_frame, padding="10", relief="solid", borderwidth=1)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(c1, text="ENROLLED STUDENTS", style="CardTitle.TLabel").pack()
        self.lbl_card_students = ttk.Label(c1, text="0", style="CardVal.TLabel")
        self.lbl_card_students.pack()

        # Card 2: Average GPA
        c2 = ttk.Frame(cards_frame, padding="10", relief="solid", borderwidth=1)
        c2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(c2, text="COHORT AVG GPA", style="CardTitle.TLabel").pack()
        self.lbl_card_gpa = ttk.Label(c2, text="0.00", style="CardVal.TLabel")
        self.lbl_card_gpa.pack()

        # Card 3: Avg Wellness
        c3 = ttk.Frame(cards_frame, padding="10", relief="solid", borderwidth=1)
        c3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(c3, text="WELLNESS INDEX", style="CardTitle.TLabel").pack()
        self.lbl_card_wellness = ttk.Label(c3, text="0.0", style="CardVal.TLabel")
        self.lbl_card_wellness.pack()

        # Card 4: Burnout Risk
        c4 = ttk.Frame(cards_frame, padding="10", relief="solid", borderwidth=1)
        c4.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(c4, text="HIGH BURNOUT RISKS", style="CardTitle.TLabel").pack()
        self.lbl_card_burnout = ttk.Label(c4, text="0", style="CardVal.TLabel")
        self.lbl_card_burnout.pack()

        # Grade Distribution Box
        dist_frame = ttk.LabelFrame(self.tab_dashboard, text=" Academic Grade Distribution ", padding="12")
        dist_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.lbl_dist = ttk.Label(dist_frame, text="", font=("Courier", 10))
        self.lbl_dist.pack(anchor=tk.W)

        btn_refresh = ttk.Button(self.tab_dashboard, text="Refresh Analytics", command=self._refresh_dashboard)
        btn_refresh.pack(anchor=tk.E, pady=6)

        self._refresh_dashboard()

    def _refresh_dashboard(self):
        summary = self.analytics.get_executive_summary()
        self.lbl_card_students.config(text=str(summary["total_students"]))
        self.lbl_card_gpa.config(text=f"{summary['average_gpa']:.2f}")
        self.lbl_card_wellness.config(text=f"{summary['average_wellness_score']:.1f}/100")
        self.lbl_card_burnout.config(text=str(summary["high_risk_burnout_count"]))

        # Format Grade Distribution Text
        dist = summary["grade_distribution"]
        dist_lines = ["Grade Distribution Breakdown:"]
        for g, count in dist.items():
            bar = "#" * (count * 4)
            dist_lines.append(f"  Grade {g:<3}: {count:>2} records | {bar}")
        self.lbl_dist.config(text="\n".join(dist_lines))

    # 2. Students & Leaderboard Tab
    def _build_students_tab(self):
        tree_frame = ttk.Frame(self.tab_students)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("rank", "id", "name", "dept", "gpa", "credits")
        self.stu_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.stu_tree.heading("rank", text="Rank")
        self.stu_tree.heading("id", text="Student ID")
        self.stu_tree.heading("name", text="Full Name")
        self.stu_tree.heading("dept", text="Department")
        self.stu_tree.heading("gpa", text="GPA")
        self.stu_tree.heading("credits", text="Credits")

        self.stu_tree.column("rank", width=50, anchor=tk.CENTER)
        self.stu_tree.column("id", width=100, anchor=tk.CENTER)
        self.stu_tree.column("name", width=180, anchor=tk.W)
        self.stu_tree.column("dept", width=160, anchor=tk.W)
        self.stu_tree.column("gpa", width=80, anchor=tk.CENTER)
        self.stu_tree.column("credits", width=80, anchor=tk.CENTER)

        sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stu_tree.yview)
        self.stu_tree.configure(yscroll=sb.set)

        self.stu_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh_students_table()

    def _refresh_students_table(self):
        for item in self.stu_tree.get_children():
            self.stu_tree.delete(item)
        rankings = self.academic.get_cohort_rankings()
        for r in rankings:
            self.stu_tree.insert("", tk.END, values=(
                f"#{r['rank']}", r["student_id"], r["full_name"],
                r["department"], f"{r['gpa']:.2f}", r["credits"]
            ))

    # 3. Grades & Transcript Tab
    def _build_grades_tab(self):
        ctrl_frame = ttk.Frame(self.tab_grades)
        ctrl_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(ctrl_frame, text="Select Student ID:").pack(side=tk.LEFT, padx=(0, 6))
        self.combo_student_sel = ttk.Combobox(ctrl_frame, state="readonly", width=16)
        self.combo_student_sel.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(ctrl_frame, text="View Transcript Card", command=self._show_transcript_card).pack(side=tk.LEFT)

        self.txt_transcript = tk.Text(self.tab_grades, font=("Courier", 10), background="#f8fafc", wrap=tk.NONE)
        self.txt_transcript.pack(fill=tk.BOTH, expand=True)

        self._populate_student_combobox()

    def _populate_student_combobox(self):
        students = self.academic.get_all_students()
        ids = [s["student_id"] for s in students]
        self.combo_student_sel["values"] = ids
        if ids:
            self.combo_student_sel.current(0)
            self._show_transcript_card()

    def _show_transcript_card(self):
        sid = self.combo_student_sel.get()
        if sid:
            report_text = self.reports.generate_student_report_card(sid)
            self.txt_transcript.delete("1.0", tk.END)
            self.txt_transcript.insert(tk.END, report_text)

    # 4. Wellness Tab
    def _build_wellness_tab(self):
        w_frame = ttk.Frame(self.tab_wellness)
        w_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "name", "study", "sleep", "stress", "exercise", "score", "risk")
        self.w_tree = ttk.Treeview(w_frame, columns=cols, show="headings")
        self.w_tree.heading("id", text="Student ID")
        self.w_tree.heading("name", text="Name")
        self.w_tree.heading("study", text="Study (hrs)")
        self.w_tree.heading("sleep", text="Sleep (hrs)")
        self.w_tree.heading("stress", text="Stress (1-10)")
        self.w_tree.heading("exercise", text="Exercise (mins)")
        self.w_tree.heading("score", text="Wellness Score")
        self.w_tree.heading("risk", text="Burnout Assessment")

        self.w_tree.column("id", width=90, anchor=tk.CENTER)
        self.w_tree.column("name", width=140, anchor=tk.W)
        self.w_tree.column("study", width=80, anchor=tk.CENTER)
        self.w_tree.column("sleep", width=80, anchor=tk.CENTER)
        self.w_tree.column("stress", width=80, anchor=tk.CENTER)
        self.w_tree.column("exercise", width=90, anchor=tk.CENTER)
        self.w_tree.column("score", width=95, anchor=tk.CENTER)
        self.w_tree.column("risk", width=220, anchor=tk.W)

        sb = ttk.Scrollbar(w_frame, orient=tk.VERTICAL, command=self.w_tree.yview)
        self.w_tree.configure(yscroll=sb.set)

        self.w_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh_wellness_table()

    def _refresh_wellness_table(self):
        for item in self.w_tree.get_children():
            self.w_tree.delete(item)
        logs = self.wellness.get_cohort_wellness_overview()
        for w in logs:
            self.w_tree.insert("", tk.END, values=(
                w["student_id"], w["full_name"], f"{w['study_hours']}h",
                f"{w['sleep_hours']}h", f"{w['stress_level']}/10",
                f"{w['exercise_minutes']}m", f"{w['wellness_score']}/100",
                w["burnout_risk"]
            ))


def run_capstone_gui():
    root = tk.Tk()
    app = CapstoneAppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_capstone_gui()
