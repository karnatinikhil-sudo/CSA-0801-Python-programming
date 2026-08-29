"""
CSA-0801: Python Programming - Module 07
Topic: Student Grade & GPA Calculator Desktop GUI Application (Tkinter & ttk)

Features:
1. Modern Tkinter ttk styled interface with card layouts
2. Dynamic course entry, credit weighting, and validation
3. Real-time GPA computation, letter grade assignment, and summary cards
4. Interactive Treeview data table with row deletion and clearing
5. Export results to structured CSV / JSON files
"""

import csv
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional


class GradeCalculatorApp:
    """Modern Desktop GUI for calculating academic grades and credit-weighted GPA."""

    GRADE_POINTS = {
        "O (Outstanding - 90-100)": ("O", 10.0),
        "A+ (Excellent - 80-89)": ("A+", 9.0),
        "A (Very Good - 70-79)": ("A", 8.0),
        "B+ (Good - 60-69)": ("B+", 7.0),
        "B (Above Average - 50-59)": ("B", 6.0),
        "C (Pass - 40-49)": ("C", 5.0),
        "F (Fail - <40)": ("F", 0.0),
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CSA-0801: Academic GPA & Grade Calculator")
        self.root.geometry("820x650")
        self.root.minsize(750, 550)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

        self._records: list[dict] = []
        self._build_ui()

    def _configure_styles(self):
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#1e293b")
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 10), foreground="#64748b")
        self.style.configure("Card.TFrame", background="#f8fafc", relief="groove")
        self.style.configure("StatValue.TLabel", font=("Helvetica", 20, "bold"), foreground="#2563eb")
        self.style.configure("StatTitle.TLabel", font=("Helvetica", 9), foreground="#64748b")
        self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))

    def _build_ui(self):
        # Header Frame
        header = ttk.Frame(self.root, padding="16 12")
        header.pack(fill=tk.X)

        ttk.Label(header, text="Academic Grade & GPA Calculator", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(header, text="CSA-0801 Python Programming Lab Suite", style="Subtitle.TLabel").pack(anchor=tk.W)

        # Main Container (Left Input Card, Right Table & Stats)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Left Column: Input Form
        input_frame = ttk.LabelFrame(main_paned, text=" Add Course Grade ", padding="12")
        main_paned.add(input_frame, weight=1)

        ttk.Label(input_frame, text="Course Code:").pack(anchor=tk.W, pady=(4, 2))
        self.entry_code = ttk.Entry(input_frame, width=24)
        self.entry_code.pack(fill=tk.X, pady=(0, 8))
        self.entry_code.insert(0, "CSA-0801")

        ttk.Label(input_frame, text="Course Title:").pack(anchor=tk.W, pady=(4, 2))
        self.entry_title = ttk.Entry(input_frame, width=24)
        self.entry_title.pack(fill=tk.X, pady=(0, 8))
        self.entry_title.insert(0, "Python Programming")

        ttk.Label(input_frame, text="Credits:").pack(anchor=tk.W, pady=(4, 2))
        self.combo_credits = ttk.Combobox(input_frame, values=[1, 2, 3, 4, 5], state="readonly")
        self.combo_credits.current(3)  # Default 4 credits
        self.combo_credits.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(input_frame, text="Grade Level:").pack(anchor=tk.W, pady=(4, 2))
        self.combo_grade = ttk.Combobox(input_frame, values=list(self.GRADE_POINTS.keys()), state="readonly")
        self.combo_grade.current(0)  # Default O
        self.combo_grade.pack(fill=tk.X, pady=(0, 16))

        btn_add = ttk.Button(input_frame, text="+ Add Course Record", command=self._add_record)
        btn_add.pack(fill=tk.X, pady=4)

        btn_clear = ttk.Button(input_frame, text="Clear All", command=self._clear_all)
        btn_clear.pack(fill=tk.X, pady=4)

        # Right Column: Dashboard Summary Cards & Table
        right_frame = ttk.Frame(main_paned, padding="8")
        main_paned.add(right_frame, weight=3)

        # Stat Cards Box
        stats_box = ttk.Frame(right_frame)
        stats_box.pack(fill=tk.X, pady=(0, 12))

        # GPA Card
        card_gpa = ttk.Frame(stats_box, padding="10", relief="solid", borderwidth=1)
        card_gpa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(card_gpa, text="CUMULATIVE GPA", style="StatTitle.TLabel").pack()
        self.lbl_gpa = ttk.Label(card_gpa, text="0.00", style="StatValue.TLabel")
        self.lbl_gpa.pack()

        # Credits Card
        card_cred = ttk.Frame(stats_box, padding="10", relief="solid", borderwidth=1)
        card_cred.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(card_cred, text="TOTAL CREDITS", style="StatTitle.TLabel").pack()
        self.lbl_credits = ttk.Label(card_cred, text="0", style="StatValue.TLabel")
        self.lbl_credits.pack()

        # Courses Count Card
        card_count = ttk.Frame(stats_box, padding="10", relief="solid", borderwidth=1)
        card_count.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        ttk.Label(card_count, text="TOTAL COURSES", style="StatTitle.TLabel").pack()
        self.lbl_count = ttk.Label(card_count, text="0", style="StatValue.TLabel")
        self.lbl_count.pack()

        # Treeview Data Table
        columns = ("code", "title", "credits", "grade", "points")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=10)
        self.tree.heading("code", text="Course Code")
        self.tree.heading("title", text="Course Title")
        self.tree.heading("credits", text="Credits")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("points", text="Points")

        self.tree.column("code", width=90, anchor=tk.CENTER)
        self.tree.column("title", width=180, anchor=tk.W)
        self.tree.column("credits", width=60, anchor=tk.CENTER)
        self.tree.column("grade", width=60, anchor=tk.CENTER)
        self.tree.column("points", width=60, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Export Actions Bar
        export_bar = ttk.Frame(right_frame, padding="8 4")
        export_bar.pack(fill=tk.X, pady=(8, 0))

        ttk.Button(export_bar, text="Export to CSV", command=self._export_csv).pack(side=tk.RIGHT, padx=4)
        ttk.Button(export_bar, text="Export to JSON", command=self._export_json).pack(side=tk.RIGHT, padx=4)

        # Populate initial demo records
        self._seed_sample_data()

    def _seed_sample_data(self):
        samples = [
            ("CSA-0801", "Python Programming", 4, "O (Outstanding - 90-100)"),
            ("CSA-0802", "Data Structures", 4, "A+ (Excellent - 80-89)"),
            ("CSA-0803", "Database Systems", 3, "A (Very Good - 70-79)"),
            ("MATH-201", "Discrete Mathematics", 4, "O (Outstanding - 90-100)"),
        ]
        for code, title, cred, grade_key in samples:
            grade_let, pts = self.GRADE_POINTS[grade_key]
            rec = {"code": code, "title": title, "credits": cred, "grade": grade_let, "points": pts}
            self._records.append(rec)
            self.tree.insert("", tk.END, values=(code, title, cred, grade_let, pts))
        self._recalculate()

    def _add_record(self):
        code = self.entry_code.get().strip()
        title = self.entry_title.get().strip()
        if not code or not title:
            messagebox.showwarning("Validation Error", "Please provide Course Code and Title.")
            return

        cred = int(self.combo_credits.get())
        grade_key = self.combo_grade.get()
        grade_let, pts = self.GRADE_POINTS[grade_key]

        rec = {"code": code, "title": title, "credits": cred, "grade": grade_let, "points": pts}
        self._records.append(rec)
        self.tree.insert("", tk.END, values=(code, title, cred, grade_let, pts))

        # Clear inputs
        self.entry_code.delete(0, tk.END)
        self.entry_title.delete(0, tk.END)
        self._recalculate()

    def _clear_all(self):
        self._records.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._recalculate()

    def _recalculate(self):
        total_cred = sum(r["credits"] for r in self._records)
        total_points = sum(r["credits"] * r["points"] for r in self._records)
        gpa = round(total_points / total_cred, 2) if total_cred > 0 else 0.0

        self.lbl_gpa.config(text=f"{gpa:.2f}")
        self.lbl_credits.config(text=str(total_cred))
        self.lbl_count.config(text=str(len(self._records)))

    def _export_csv(self):
        if not self._records:
            messagebox.showinfo("Export", "No course records to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["code", "title", "credits", "grade", "points"])
                writer.writeheader()
                writer.writerows(self._records)
            messagebox.showinfo("Success", f"Exported {len(self._records)} records to CSV!")

    def _export_json(self):
        if not self._records:
            messagebox.showinfo("Export", "No course records to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"courses": self._records, "gpa": self.lbl_gpa.cget("text")}, f, indent=4)
            messagebox.showinfo("Success", f"Exported {len(self._records)} records to JSON!")


def run_app():
    root = tk.Tk()
    app = GradeCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
