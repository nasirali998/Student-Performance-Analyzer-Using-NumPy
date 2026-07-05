"""
=====================================================================
   STUDENT PERFORMANCE ANALYZER  —  Professional Desktop Edition
=====================================================================
A NumPy-powered analytics tool with a Tkinter GUI, hand-drawn
Tkinter Canvas charts (no charting library), a sortable results
table, and a one-click text report export.

Only external dependency: NumPy.
Tkinter is part of the Python standard library (no install needed).

Run:
    python student_performance_analyzer.py

Requirements:
    pip install numpy
=====================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import numpy as np

# ---------------------------------------------------------------
# THEME / CONSTANTS
# ---------------------------------------------------------------
BG_DARK = "#1e2530"
BG_PANEL = "#262f3d"
BG_CARD = "#2e3947"
ACCENT = "#4fd1c5"
ACCENT_DARK = "#38a89d"
TEXT_LIGHT = "#f0f4f8"
TEXT_MUTED = "#9aa7b5"
PASS_COLOR = "#4fd17a"
FAIL_COLOR = "#e5534b"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUB = ("Segoe UI", 10)
FONT_BODY = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")

SUBJECTS = ["Math", "Physics", "English"]

DEFAULT_STUDENTS = ["Ali", "Ahmed", "Sara", "Ayesha", "Zain"]
DEFAULT_MARKS = np.array([
    [85, 90, 78],
    [70, 88, 80],
    [92, 81, 95],
    [65, 75, 70],
    [88, 79, 84],
])


# =================================================================
# DATA / ANALYTICS ENGINE  (pure NumPy, kept separate from the GUI)
# =================================================================
class PerformanceEngine:
    def __init__(self, students, marks):
        self.students = list(students)
        self.marks = np.array(marks, dtype=float)

    # ---- core NumPy computations -------------------------------
    @property
    def total_marks(self):
        return np.sum(self.marks, axis=1)

    @property
    def average_marks(self):
        return np.mean(self.marks, axis=1)

    @property
    def subject_highest(self):
        return np.max(self.marks, axis=0)

    @property
    def subject_lowest(self):
        return np.min(self.marks, axis=0)

    @property
    def subject_average(self):
        return np.mean(self.marks, axis=0)

    @property
    def topper_index(self):
        return int(np.argmax(self.total_marks))

    @property
    def lowest_index(self):
        return int(np.argmin(self.total_marks))

    def pass_fail(self, threshold=40):
        return [bool(np.all(row >= threshold)) for row in self.marks]

    @staticmethod
    def grade_for(avg):
        if avg >= 90:
            return "A+"
        elif avg >= 80:
            return "A"
        elif avg >= 70:
            return "B"
        elif avg >= 60:
            return "C"
        return "F"

    def grades(self):
        return [self.grade_for(a) for a in self.average_marks]

    def class_average(self):
        return float(np.mean(self.average_marks))

    def std_dev(self):
        return float(np.std(self.total_marks))

    def summary_text(self):
        lines = []
        lines.append("=" * 64)
        lines.append("      STUDENT PERFORMANCE ANALYZER — FULL REPORT")
        lines.append("=" * 64)
        lines.append(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Students  : {len(self.students)}   |   Subjects: {len(SUBJECTS)}")
        lines.append("-" * 64)

        lines.append(f"{'Name':<10}{'Total':>8}{'Average':>10}{'Grade':>8}{'Status':>10}")
        pf = self.pass_fail()
        grades = self.grades()
        for i, name in enumerate(self.students):
            status = "PASS" if pf[i] else "FAIL"
            lines.append(
                f"{name:<10}{self.total_marks[i]:>8.0f}"
                f"{self.average_marks[i]:>10.2f}{grades[i]:>8}{status:>10}"
            )

        lines.append("-" * 64)
        lines.append(f"Class Topper     : {self.students[self.topper_index]} "
                      f"({self.total_marks[self.topper_index]:.0f} marks)")
        lines.append(f"Lowest Scorer    : {self.students[self.lowest_index]} "
                      f"({self.total_marks[self.lowest_index]:.0f} marks)")
        lines.append(f"Class Average    : {self.class_average():.2f}")
        lines.append(f"Std. Deviation   : {self.std_dev():.2f}")
        lines.append("-" * 64)
        for i, subj in enumerate(SUBJECTS):
            lines.append(f"{subj:<10} Highest: {self.subject_highest[i]:>5.0f}   "
                         f"Lowest: {self.subject_lowest[i]:>5.0f}   "
                         f"Average: {self.subject_average[i]:>6.2f}")
        lines.append("=" * 64)
        lines.append("Report generated successfully.")
        lines.append("=" * 64)
        return "\n".join(lines)


# =================================================================
# GUI APPLICATION
# =================================================================
class PerformanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Performance Analyzer  |  NumPy Analytics Suite")
        self.geometry("1180x720")
        self.minsize(1000, 640)
        self.configure(bg=BG_DARK)

        self.engine = PerformanceEngine(DEFAULT_STUDENTS, DEFAULT_MARKS)

        self._build_style()
        self._build_header()
        self._build_body()
        self._refresh_all()

    # -------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_MUTED,
                         padding=(18, 10), font=FONT_BODY, borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT)])

        style.configure("Treeview", background=BG_CARD, fieldbackground=BG_CARD,
                        foreground=TEXT_LIGHT, rowheight=28, font=FONT_BODY, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_PANEL, foreground=ACCENT,
                        font=FONT_BOLD, borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT_DARK)])

        style.configure("Accent.TButton", background=ACCENT, foreground="#0b1620",
                        font=FONT_BOLD, padding=(14, 8), borderwidth=0)
        style.map("Accent.TButton", background=[("active", ACCENT_DARK)])

        style.configure("Ghost.TButton", background=BG_CARD, foreground=TEXT_LIGHT,
                        font=FONT_BODY, padding=(12, 7), borderwidth=0)
        style.map("Ghost.TButton", background=[("active", BG_PANEL)])

    # -------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=BG_DARK, pady=16, padx=24)
        header.pack(fill="x")

        left = tk.Frame(header, bg=BG_DARK)
        left.pack(side="left")
        tk.Label(left, text="📊 Student Performance Analyzer", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_LIGHT).pack(anchor="w")
        tk.Label(left, text="NumPy-powered analytics  •  live charts  •  exportable reports",
                 font=FONT_SUB, bg=BG_DARK, fg=TEXT_MUTED).pack(anchor="w")

        right = tk.Frame(header, bg=BG_DARK)
        right.pack(side="right")
        ttk.Button(right, text="➕ Add Student", style="Ghost.TButton",
                   command=self.add_student_dialog).pack(side="left", padx=4)
        ttk.Button(right, text="🗑 Remove Selected", style="Ghost.TButton",
                   command=self.remove_selected_student).pack(side="left", padx=4)
        ttk.Button(right, text="💾 Export Report", style="Accent.TButton",
                   command=self.export_report).pack(side="left", padx=4)

    # -------------------------------------------------------------
    def _build_body(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.tab_data = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_analysis = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_charts = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_report = tk.Frame(self.notebook, bg=BG_DARK)

        self.notebook.add(self.tab_data, text="  📋 Marks Data  ")
        self.notebook.add(self.tab_analysis, text="  🧮 Analysis  ")
        self.notebook.add(self.tab_charts, text="  📈 Charts  ")
        self.notebook.add(self.tab_report, text="  📄 Report  ")

        self._build_data_tab()
        self._build_analysis_tab()
        self._build_charts_tab()
        self._build_report_tab()

    # -------------------------------------------------------------
    # TAB 1 : DATA (editable table)
    # -------------------------------------------------------------
    def _build_data_tab(self):
        wrap = tk.Frame(self.tab_data, bg=BG_DARK)
        wrap.pack(fill="both", expand=True, pady=16)

        cols = ["Student"] + SUBJECTS
        self.data_tree = ttk.Treeview(wrap, columns=cols, show="headings", height=12)
        for c in cols:
            self.data_tree.heading(c, text=c)
            self.data_tree.column(c, anchor="center", width=140)
        self.data_tree.column("Student", width=180, anchor="w")
        self.data_tree.pack(fill="both", expand=True, padx=4)
        self.data_tree.bind("<Double-1>", self._edit_cell)

        hint = tk.Label(self.tab_data,
                         text="Double-click any mark to edit it, then press Enter. "
                              "Use the header buttons to add or remove students.",
                         font=FONT_SUB, bg=BG_DARK, fg=TEXT_MUTED)
        hint.pack(anchor="w", padx=8, pady=(0, 8))

        recalc = ttk.Button(self.tab_data, text="🔄 Recalculate Analytics",
                             style="Accent.TButton", command=self._refresh_all)
        recalc.pack(anchor="e", padx=8, pady=4)

    def _edit_cell(self, event):
        item = self.data_tree.identify_row(event.y)
        col = self.data_tree.identify_column(event.x)
        if not item or col == "#1":  # don't edit name column
            return
        col_index = int(col.replace("#", "")) - 1
        x, y, w, h = self.data_tree.bbox(item, col)
        value = self.data_tree.set(item, self.data_tree["columns"][col_index])

        entry = tk.Entry(self.data_tree, font=FONT_BODY, justify="center")
        entry.insert(0, value)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus()

        def save(_=None):
            new_val = entry.get()
            try:
                new_val_num = float(new_val)
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter a numeric mark (0-100).")
                entry.destroy()
                return
            row_idx = self.data_tree.index(item)
            subj_idx = col_index - 1
            self.engine.marks[row_idx, subj_idx] = new_val_num
            self.data_tree.set(item, self.data_tree["columns"][col_index], f"{new_val_num:.0f}")
            entry.destroy()
            self._refresh_all(rebuild_data_table=False)

        entry.bind("<Return>", save)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def _rebuild_data_table(self):
        self.data_tree.delete(*self.data_tree.get_children())
        for name, row in zip(self.engine.students, self.engine.marks):
            self.data_tree.insert("", "end", values=[name] + [f"{v:.0f}" for v in row])

    # -------------------------------------------------------------
    def add_student_dialog(self):
        dlg = tk.Toplevel(self, bg=BG_PANEL)
        dlg.title("Add Student")
        dlg.geometry("340x260")
        dlg.grab_set()

        tk.Label(dlg, text="New Student", font=FONT_BOLD, bg=BG_PANEL, fg=TEXT_LIGHT).pack(pady=10)

        name_var = tk.StringVar()
        tk.Label(dlg, text="Name", bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_SUB).pack(anchor="w", padx=24)
        tk.Entry(dlg, textvariable=name_var, font=FONT_BODY).pack(fill="x", padx=24, pady=(0, 10))

        mark_vars = []
        for subj in SUBJECTS:
            tk.Label(dlg, text=subj, bg=BG_PANEL, fg=TEXT_MUTED, font=FONT_SUB).pack(anchor="w", padx=24)
            v = tk.StringVar()
            tk.Entry(dlg, textvariable=v, font=FONT_BODY).pack(fill="x", padx=24, pady=(0, 6))
            mark_vars.append(v)

        def submit():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Missing name", "Please enter a student name.")
                return
            try:
                vals = [float(v.get()) for v in mark_vars]
            except ValueError:
                messagebox.showerror("Invalid marks", "Please enter numeric marks for all subjects.")
                return
            self.engine.students.append(name)
            self.engine.marks = np.vstack([self.engine.marks, vals])
            dlg.destroy()
            self._refresh_all()

        ttk.Button(dlg, text="Add Student", style="Accent.TButton", command=submit).pack(pady=14)

    def remove_selected_student(self):
        sel = self.data_tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a student row to remove.")
            return
        idx = self.data_tree.index(sel[0])
        if len(self.engine.students) <= 1:
            messagebox.showwarning("Not allowed", "At least one student must remain.")
            return
        del self.engine.students[idx]
        self.engine.marks = np.delete(self.engine.marks, idx, axis=0)
        self._refresh_all()

    # -------------------------------------------------------------
    # TAB 2 : ANALYSIS (summary cards + results table)
    # -------------------------------------------------------------
    def _build_analysis_tab(self):
        self.cards_frame = tk.Frame(self.tab_analysis, bg=BG_DARK)
        self.cards_frame.pack(fill="x", pady=(16, 12))

        cols = ["Student", "Total", "Average", "Grade", "Status"]
        self.result_tree = ttk.Treeview(self.tab_analysis, columns=cols, show="headings", height=10)
        for c in cols:
            self.result_tree.heading(c, text=c)
            self.result_tree.column(c, anchor="center", width=140)
        self.result_tree.column("Student", width=180, anchor="w")
        self.result_tree.pack(fill="both", expand=True, padx=4)
        self.result_tree.tag_configure("pass", foreground=PASS_COLOR)
        self.result_tree.tag_configure("fail", foreground=FAIL_COLOR)

    def _make_card(self, parent, title, value, color=ACCENT):
        card = tk.Frame(parent, bg=BG_CARD, padx=18, pady=12)
        tk.Label(card, text=title, font=FONT_SUB, bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg=BG_CARD, fg=color).pack(anchor="w")
        return card

    def _rebuild_analysis_tab(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        e = self.engine
        cards_data = [
            ("Class Average", f"{e.class_average():.2f}", ACCENT),
            ("Class Topper", f"{e.students[e.topper_index]}", PASS_COLOR),
            ("Lowest Scorer", f"{e.students[e.lowest_index]}", FAIL_COLOR),
            ("Std. Deviation", f"{e.std_dev():.2f}", ACCENT),
            ("Total Students", f"{len(e.students)}", TEXT_LIGHT),
        ]
        for title, value, color in cards_data:
            card = self._make_card(self.cards_frame, title, value, color)
            card.pack(side="left", expand=True, fill="x", padx=6)

        self.result_tree.delete(*self.result_tree.get_children())
        pf = e.pass_fail()
        grades = e.grades()
        for i, name in enumerate(e.students):
            status = "PASS" if pf[i] else "FAIL"
            tag = "pass" if pf[i] else "fail"
            self.result_tree.insert("", "end", tags=(tag,), values=[
                name, f"{e.total_marks[i]:.0f}", f"{e.average_marks[i]:.2f}", grades[i], status
            ])

    # -------------------------------------------------------------
    # TAB 3 : CHARTS (matplotlib embedded)
    # -------------------------------------------------------------
    def _build_charts_tab(self):
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor=BG_DARK)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_charts)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def _rebuild_charts_tab(self):
        e = self.engine
        self.fig.clear()
        self.fig.patch.set_facecolor(BG_DARK)

        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax3 = self.fig.add_subplot(2, 2, 3)
        ax4 = self.fig.add_subplot(2, 2, 4)

        for ax in (ax1, ax2, ax3, ax4):
            ax.set_facecolor(BG_PANEL)
            ax.tick_params(colors=TEXT_MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(BG_CARD)

        # Total marks per student
        ax1.bar(e.students, e.total_marks, color=ACCENT)
        ax1.set_title("Total Marks per Student", color=TEXT_LIGHT, fontsize=10)
        ax1.tick_params(axis="x", rotation=30)

        # Average marks per student
        ax2.bar(e.students, e.average_marks, color="#f0b429")
        ax2.set_title("Average Marks per Student", color=TEXT_LIGHT, fontsize=10)
        ax2.tick_params(axis="x", rotation=30)

        # Subject-wise average
        ax3.bar(SUBJECTS, e.subject_average, color="#7c83fd")
        ax3.set_title("Subject-wise Class Average", color=TEXT_LIGHT, fontsize=10)

        # Pass/Fail distribution
        pf = e.pass_fail()
        pass_count = sum(pf)
        fail_count = len(pf) - pass_count
        if fail_count == 0:
            ax4.pie([pass_count], labels=["PASS"], colors=[PASS_COLOR],
                    autopct="%1.0f%%", textprops={"color": TEXT_LIGHT})
        else:
            ax4.pie([pass_count, fail_count], labels=["PASS", "FAIL"],
                    colors=[PASS_COLOR, FAIL_COLOR], autopct="%1.0f%%",
                    textprops={"color": TEXT_LIGHT})
        ax4.set_title("Pass / Fail Distribution", color=TEXT_LIGHT, fontsize=10)

        self.fig.tight_layout(pad=2.5)
        self.canvas.draw()

    # -------------------------------------------------------------
    # TAB 4 : REPORT (plain text summary + export)
    # -------------------------------------------------------------
    def _build_report_tab(self):
        wrap = tk.Frame(self.tab_report, bg=BG_DARK)
        wrap.pack(fill="both", expand=True, pady=16, padx=4)

        self.report_box = tk.Text(wrap, bg=BG_CARD, fg=TEXT_LIGHT, font=("Consolas", 10),
                                   wrap="none", relief="flat", padx=16, pady=16)
        self.report_box.pack(fill="both", expand=True)

    def _rebuild_report_tab(self):
        self.report_box.config(state="normal")
        self.report_box.delete("1.0", "end")
        self.report_box.insert("1.0", self.engine.summary_text())
        self.report_box.config(state="disabled")

    def export_report(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="student_performance_report.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.engine.summary_text())
        messagebox.showinfo("Exported", f"Report saved to:\n{path}")

    # -------------------------------------------------------------
    def _refresh_all(self, rebuild_data_table=True):
        if rebuild_data_table:
            self._rebuild_data_table()
        self._rebuild_analysis_tab()
        self._rebuild_charts_tab()
        self._rebuild_report_tab()


# =================================================================
if __name__ == "__main__":
    app = PerformanceApp()
    app.mainloop()