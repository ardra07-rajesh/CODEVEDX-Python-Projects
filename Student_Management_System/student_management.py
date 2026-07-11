"""
Student Management System
==========================

A console-based Student Management System that handles student records,
attendance tracking, marks/grading, and basic performance analytics —
all from a single self-contained Python file.

Data is persisted locally as JSON files (students.json, attendance.json,
marks.json), so the program can be run immediately without any external
database or account setup.

Author: Ardra Rajesh
"""

import json
import os
import datetime
from collections import defaultdict  # used for department counts & grade distribution tallies

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
# Local JSON files used for persistent storage. Created automatically
# on first save; no external database or setup required.
STUDENTS_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"
MARKS_FILE = "marks.json"

# Badge definitions used purely for reference/documentation purposes.
# The actual badge-award logic lives in StudentManager._get_badges().
BADGES = {
    "Top Scorer": {"condition": "avg >= 90", "icon": "🥇"},
    "Good Performer": {"condition": "avg >= 75", "icon": "🥈"},
    "Attendance Star": {"condition": "att >= 90", "icon": "⭐"},
    "Consistent": {"condition": "avg >= 60 and att >= 75", "icon": "🎯"},
    "Needs Boost": {"condition": "avg < 50", "icon": "💪"},
}

# ─────────────────────────────────────────────
# FILE UTILITIES
# ─────────────────────────────────────────────

def load_data(filepath):
    """Load JSON data from file."""
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_data(filepath, data):
    """Save JSON data to file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

# ─────────────────────────────────────────────
# DISPLAY UTILITIES
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title):
    width = 60
    print("\n" + "═" * width)
    print(f"{'  ' + title:^{width}}")
    print("═" * width)

def print_table(headers, rows, col_widths=None):
    """Print a nicely formatted table."""
    if not col_widths:
        col_widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0)) + 2
                      for i, h in enumerate(headers)]
    header_row = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)
    print("\n" + separator)
    print(header_row)
    print(separator)
    for row in rows:
        print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))))
    print(separator)
    print(f"  Total records: {len(rows)}\n")

def pause():
    input("\n  Press Enter to continue...")

# ─────────────────────────────────────────────
# INPUT VALIDATION
# ─────────────────────────────────────────────

def get_valid_input(prompt, validator=None, error_msg="Invalid input."):
    while True:
        value = input(prompt).strip()
        if validator:
            try:
                if validator(value):
                    return value
                else:
                    print(f"   {error_msg}")
            except Exception:
                print(f"   {error_msg}")
        else:
            if value:
                return value
            print("  Input cannot be empty.")

def validate_email(email):
    return "@" in email and "." in email.split("@")[-1]

def validate_phone(phone):
    return phone.isdigit() and len(phone) in range(7, 16)

def validate_age(age):
    return age.isdigit() and 10 <= int(age) <= 100

def validate_id(sid):
    return sid.strip() != ""

# ─────────────────────────────────────────────
# STUDENT CLASS
# ─────────────────────────────────────────────

class StudentManager:
    """
    Core application class that owns all in-memory data (students,
    attendance, marks) and exposes the operations used by the menus:
    CRUD for students, attendance marking/reporting, marks entry/grading,
    sorting, and analytics (prediction, suggestions, leaderboard, stats).
    """

    def __init__(self):
        # Load any existing data from disk on startup so the program
        # can resume from where it left off.
        self.students = load_data(STUDENTS_FILE)
        self.attendance = load_data(ATTENDANCE_FILE)
        self.marks = load_data(MARKS_FILE)

    def save_all(self):
        """Persist students, attendance, and marks to their JSON files."""
        save_data(STUDENTS_FILE, self.students)
        save_data(ATTENDANCE_FILE, self.attendance)
        save_data(MARKS_FILE, self.marks)

    # ── STUDENT CRUD ──────────────────────────

    def add_student(self):
        """Prompt for and validate a new student's details, then save the record."""
        print_header(" ADD STUDENT")
        sid = get_valid_input("  Student ID     : ", validate_id, "ID cannot be empty.")
        if sid in self.students:
            print(f"  Student ID '{sid}' already exists.")
            pause()
            return
        name = get_valid_input("  Full Name       : ")
        age  = get_valid_input("  Age             : ", validate_age, "Age must be between 10 and 100.")
        dept = get_valid_input("  Department      : ")
        email= get_valid_input("  Email           : ", validate_email, "Enter a valid email address.")
        phone= get_valid_input("  Phone Number    : ", validate_phone, "Phone must be 7–15 digits.")

        self.students[sid] = {
            "name": name, "age": int(age),
            "department": dept, "email": email, "phone": phone,
            "joined": str(datetime.date.today())
        }
        self.save_all()
        print(f"\n   Student '{name}' added successfully!")
        pause()

    def view_students(self):
        """Display all students in a formatted table."""
        print_header(" ALL STUDENTS")
        if not self.students:
            print("  No students found.")
            pause()
            return
        headers = ["ID", "Name", "Age", "Department", "Email", "Phone"]
        rows = [[sid, s["name"], s["age"], s["department"], s["email"], s["phone"]]
                for sid, s in self.students.items()]
        print_table(headers, rows, [10, 18, 5, 15, 25, 14])
        pause()

    def update_student(self):
        """Update one or more fields of an existing student; blank input keeps the current value."""
        print_header(" UPDATE STUDENT")
        sid = get_valid_input("  Enter Student ID to update: ")
        if sid not in self.students:
            print("   Student not found.")
            pause()
            return
        s = self.students[sid]
        print(f"\n  Updating: {s['name']} | Leave blank to keep current value.\n")
        fields = [("name", "Full Name", None, None),
                  ("age", "Age", validate_age, "Age must be 10–100"),
                  ("department", "Department", None, None),
                  ("email", "Email", validate_email, "Invalid email"),
                  ("phone", "Phone Number", validate_phone, "Phone must be 7–15 digits")]
        for key, label, validator, err in fields:
            new_val = input(f"  {label} [{s[key]}]: ").strip()
            if new_val:
                if validator:
                    while not validator(new_val):
                        print(f"  {err}")
                        new_val = input(f"  {label} [{s[key]}]: ").strip()
                        if not new_val:
                            break
                if new_val:
                    s[key] = int(new_val) if key == "age" else new_val
        self.students[sid] = s
        self.save_all()
        print("\n  Student updated successfully!")
        pause()

    def delete_student(self):
        """Delete a student (with confirmation) and clean up their attendance/marks records."""
        print_header("  DELETE STUDENT")
        sid = get_valid_input("  Enter Student ID to delete: ")
        if sid not in self.students:
            print("  Student not found.")
            pause()
            return
        confirm = input(f"  Are you sure you want to delete '{self.students[sid]['name']}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            del self.students[sid]
            self.attendance.pop(sid, None)
            self.marks.pop(sid, None)
            self.save_all()
            print("  Student deleted.")
        else:
            print("  Deletion cancelled.")
        pause()

    def search_student(self):
        """Search students by partial match on ID or name (case-insensitive)."""
        print_header(" SEARCH STUDENT")
        query = input("  Enter Name or ID to search: ").strip().lower()
        results = [(sid, s) for sid, s in self.students.items()
                   if query in sid.lower() or query in s["name"].lower()]
        if not results:
            print("  No matching students found.")
        else:
            headers = ["ID", "Name", "Age", "Department", "Email", "Phone"]
            rows = [[sid, s["name"], s["age"], s["department"], s["email"], s["phone"]]
                    for sid, s in results]
            print_table(headers, rows, [10, 18, 5, 15, 25, 14])
        pause()

    # ── ATTENDANCE ────────────────────────────

    def mark_attendance(self):
        """Record today's attendance (Present/Absent/Leave) for every student."""
        print_header(" MARK ATTENDANCE")
        if not self.students:
            print("  No students to mark attendance for.")
            pause()
            return
        date = str(datetime.date.today())
        print(f"  Date: {date}\n")
        if date not in self.attendance:
            self.attendance[date] = {}
        for sid, s in self.students.items():
            status = ""
            while status not in ["p", "a", "l"]:
                status = input(f"  {s['name']:<20} (P=Present / A=Absent / L=Leave): ").strip().lower()
            self.attendance[date][sid] = status.upper()
        self.save_all()
        print("\n  Attendance marked for today!")
        pause()

    def view_attendance(self):
        """Show each student's overall attendance percentage, flagging those below 75%."""
        print_header(" ATTENDANCE PERCENTAGE")
        if not self.students:
            print("  No students found.")
            pause()
            return
        rows = []
        for sid, s in self.students.items():
            total = present = 0
            for date, records in self.attendance.items():
                if sid in records:
                    total += 1
                    if records[sid] == "P":
                        present += 1
            pct = round((present / total * 100), 1) if total > 0 else 0.0
            alert = "🚨 LOW" if pct < 75 else "✅ OK"
            rows.append([sid, s["name"], present, total, f"{pct}%", alert])
        headers = ["ID", "Name", "Present", "Total", "Percentage", "Status"]
        print_table(headers, rows, [10, 18, 8, 7, 11, 10])
        pause()

    # ── MARKS ─────────────────────────────────

    def add_marks(self):
        """Record marks (0–100) for a student across all predefined subjects."""
        print_header(" ADD MARKS")
        sid = get_valid_input("  Enter Student ID: ")
        if sid not in self.students:
            print("  Student not found.")
            pause()
            return
        subjects = ["Mathematics", "Programming", "English", "Science", "Project"]
        print(f"  Adding marks for: {self.students[sid]['name']}\n")
        if sid not in self.marks:
            self.marks[sid] = {}
        for sub in subjects:
            while True:
                try:
                    mark = int(input(f"  {sub:<15}: "))
                    if 0 <= mark <= 100:
                        self.marks[sid][sub] = mark
                        break
                    else:
                        print("  Marks must be 0–100.")
                except ValueError:
                    print(" Enter a valid number.")
        self.save_all()
        print("\n  Marks saved successfully!")
        pause()

    def view_marks(self):
        """Display marks for every subject alongside each student's average and letter grade."""
        print_header(" STUDENT MARKS")
        if not self.marks:
            print("  No marks recorded yet.")
            pause()
            return
        subjects = ["Mathematics", "Programming", "English", "Science", "Project"]
        headers = ["ID", "Name"] + subjects + ["Avg", "Grade"]
        rows = []
        for sid, subj_marks in self.marks.items():
            name = self.students.get(sid, {}).get("name", "Unknown")
            marks_list = [subj_marks.get(s, "-") for s in subjects]
            valid = [m for m in marks_list if isinstance(m, int)]
            avg = round(sum(valid) / len(valid), 1) if valid else 0
            grade = self._calc_grade(avg)
            rows.append([sid, name] + marks_list + [avg, grade])
        col_widths = [10, 16] + [14] * len(subjects) + [6, 6]
        print_table(headers, rows, col_widths)
        pause()

    def _calc_grade(self, avg):
        """Convert a numeric average into a letter grade (A+ down to F)."""
        if avg >= 90: return "A+"
        elif avg >= 80: return "A"
        elif avg >= 70: return "B+"
        elif avg >= 60: return "B"
        elif avg >= 50: return "C"
        else: return "D"

    # ── SORTING ───────────────────────────────

    def sort_students(self):
        """Sort and display students by name, average marks, or department."""
        print_header(" SORT STUDENTS")
        print("  1. Sort by Name")
        print("  2. Sort by Average Marks")
        print("  3. Sort by Department")
        choice = input("\n  Choose sort option: ").strip()

        students_list = list(self.students.items())
        if choice == "1":
            sorted_list = sorted(students_list, key=lambda x: x[1]["name"])
            key_label = "Name"
        elif choice == "2":
            def avg_marks(x):
                sid = x[0]
                m = self.marks.get(sid, {}).values()
                return round(sum(m) / len(m), 1) if m else 0
            sorted_list = sorted(students_list, key=avg_marks, reverse=True)
            key_label = "Avg Marks (High→Low)"
        elif choice == "3":
            sorted_list = sorted(students_list, key=lambda x: x[1]["department"])
            key_label = "Department"
        else:
            print("  Invalid choice.")
            pause()
            return

        print(f"\n  Sorted by: {key_label}\n")
        headers = ["Rank", "ID", "Name", "Department"]
        rows = [[i+1, sid, s["name"], s["department"]] for i, (sid, s) in enumerate(sorted_list)]
        print_table(headers, rows, [5, 10, 20, 18])
        pause()

    # ── STATISTICS & PREDICTION ───────────────

    def _get_student_stats(self, sid):
        """Return avg marks and attendance % for a student."""
        m = self.marks.get(sid, {}).values()
        avg = round(sum(m) / len(m), 1) if m else 0

        total = present = 0
        for date, records in self.attendance.items():
            if sid in records:
                total += 1
                if records[sid] == "P":
                    present += 1
        att = round((present / total * 100), 1) if total > 0 else 0.0
        return avg, att

    def predict_performance(self):
        """Give a simple rule-based performance prediction combining average marks and attendance."""
        print_header(" STUDENT PERFORMANCE PREDICTION")
        if not self.students:
            print("  No students found.")
            pause()
            return
        rows = []
        for sid, s in self.students.items():
            avg, att = self._get_student_stats(sid)
            if avg >= 75 and att >= 75:
                prediction = " Excellent"
            elif avg >= 50 and att >= 60:
                prediction = " Average"
            else:
                prediction = "  Needs Improvement"
            rows.append([sid, s["name"], f"{avg}", f"{att}%", prediction])
        headers = ["ID", "Name", "Avg Marks", "Attendance", "Prediction"]
        print_table(headers, rows, [10, 18, 10, 12, 20])
        pause()

    def ai_study_suggestions(self):
        """Generate personalized, rule-based study tips for a student based on their marks and attendance."""
        print_header(" AI STUDY SUGGESTIONS")
        sid = get_valid_input("  Enter Student ID: ")
        if sid not in self.students:
            print("  Student not found.")
            pause()
            return
        s = self.students[sid]
        avg, att = self._get_student_stats(sid)
        subject_marks = self.marks.get(sid, {})

        print(f"\n  ┌─────────────────────────────────────────────┐")
        print(f"  │  Student     : {s['name']:<30}│")
        print(f"  │  Department  : {s['department']:<30}│")
        print(f"  │  Avg Marks   : {str(avg):<30}│")
        print(f"  │  Attendance  : {str(att) + '%':<30}│")
        print(f"  └─────────────────────────────────────────────┘")
        print(f"\n  📌 Personalized Study Suggestions:\n")

        suggestions = []
        if att < 75:
            suggestions.append(f" Attendance is {att}% — must improve above 75% to avoid detainment.")
        elif att < 85:
            suggestions.append(f" Attendance is {att}% — try to improve to 90%+ for better performance.")

        if avg >= 90:
            suggestions.append(" Outstanding performance! Consider joining coding competitions or research projects.")
        elif avg >= 75:
            suggestions.append(" Good performance! Focus on weak subjects to push your average above 90.")
        elif avg >= 60:
            suggestions.append(" Decent progress. Dedicate 2 extra hours daily to weaker subjects.")
        elif avg >= 50:
            suggestions.append("  Below expectation. Create a daily study schedule and seek teacher support.")
        else:
            suggestions.append(" Critical level. Immediately seek academic counseling and form a study group.")

        if subject_marks:
            weakest = min(subject_marks, key=subject_marks.get)
            best = max(subject_marks, key=subject_marks.get)
            suggestions.append(f" Weakest subject: {weakest} ({subject_marks[weakest]}) — spend extra 1 hr/day.")
            suggestions.append(f" Best subject: {best} ({subject_marks[best]}) — leverage this as your strength!")

        suggestions.append(" Stay hydrated, sleep 7–8 hrs, and practice mindfulness for stress relief.")
        suggestions.append(" Limit social media to 30 min/day during exam season.")

        for i, sug in enumerate(suggestions, 1):
            print(f"  {i}. {sug}")
        pause()

    # ── LEADERBOARD ───────────────────────────

    def leaderboard(self):
        """Rank all students by average marks and show medal/badge icons for top and notable performers."""
        print_header(" STUDENT LEADERBOARD")
        if not self.marks:
            print("  No marks data available for ranking.")
            pause()
            return
        ranked = []
        for sid, s in self.students.items():
            avg, att = self._get_student_stats(sid)
            badges = self._get_badges(avg, att)
            ranked.append((sid, s["name"], s["department"], avg, att, badges))
        ranked.sort(key=lambda x: x[3], reverse=True)

        print(f"\n  {'Rank':<5} {'Name':<20} {'Department':<15} {'Avg':<7} {'Att%':<7} Badges")
        print("  " + "─" * 70)
        for i, (sid, name, dept, avg, att, badges) in enumerate(ranked, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"#{i} "))
            print(f"  {medal:<5} {name:<20} {dept:<15} {str(avg):<7} {str(att)+'%':<7} {badges}")
        print()
        pause()

    def _get_badges(self, avg, att):
        """Return the badge icon string a student has earned based on average marks and attendance."""
        earned = []
        if avg >= 90:       earned.append("🥇")
        elif avg >= 75:     earned.append("🥈")
        if att >= 90:       earned.append("⭐")
        if avg >= 60 and att >= 75: earned.append("🎯")
        if avg < 50:        earned.append("💪")
        return " ".join(earned) if earned else "—"

    # ── ATTENDANCE ALERTS ─────────────────────

    def attendance_alerts(self):
        """List students whose overall attendance has fallen below the 75% threshold."""
        print_header(" ATTENDANCE ALERT SYSTEM")
        if not self.students:
            print("  No students found.")
            pause()
            return
        low = []
        for sid, s in self.students.items():
            total = present = 0
            for date, records in self.attendance.items():
                if sid in records:
                    total += 1
                    if records[sid] == "P":
                        present += 1
            pct = round((present / total * 100), 1) if total > 0 else 0.0
            if pct < 75:
                low.append([sid, s["name"], s["department"], s["phone"], f"{pct}%"])
        if low:
            print("    Students with attendance below 75%:\n")
            headers = ["ID", "Name", "Department", "Phone", "Attendance"]
            print_table(headers, low, [10, 18, 15, 14, 11])
        else:
            print("\n  All students have satisfactory attendance (≥ 75%).\n")
        pause()

    # ── STATISTICS DASHBOARD ──────────────────

    def statistics_dashboard(self):
        """Display an overview dashboard: totals, department breakdown, and grade distribution."""
        print_header(" STATISTICS DASHBOARD")
        if not self.students:
            print("  No data available.")
            pause()
            return
        total = len(self.students)
        depts = defaultdict(int)
        for s in self.students.values():
            depts[s["department"]] += 1

        all_avgs = []
        for sid in self.students:
            m = self.marks.get(sid, {}).values()
            if m:
                all_avgs.append(sum(m) / len(m))

        overall_avg = round(sum(all_avgs) / len(all_avgs), 1) if all_avgs else 0

        # Grade distribution
        grade_dist = defaultdict(int)
        for avg in all_avgs:
            grade_dist[self._calc_grade(avg)] += 1

        print(f"\n   Total Students      : {total}")
        print(f"  Overall Average     : {overall_avg}")
        print(f"   Departments         : {len(depts)}")
        print(f"\n  Department Breakdown:")
        for dept, count in sorted(depts.items()):
            bar = "█" * count
            print(f"    {dept:<20} {bar} ({count})")
        print(f"\n  Grade Distribution:")
        for grade in ["A+", "A", "B", "C", "D", "F"]:
            count = grade_dist.get(grade, 0)
            bar = "█" * count
            print(f"    {grade:<5} {bar} ({count})")
        pause()


# ─────────────────────────────────────────────
# MENUS
# ─────────────────────────────────────────────

def student_menu(sm):
    """Sub-menu for student CRUD operations (add/view/update/delete/search)."""
    while True:
        print_header("👨‍🎓 STUDENT MANAGEMENT")
        print("  1. Add Student")
        print("  2. View All Students")
        print("  3. Update Student")
        print("  4. Delete Student")
        print("  5. Search Student")
        print("  0. Back to Main Menu")
        ch = input("\n  Choose option: ").strip()
        if ch == "1": sm.add_student()
        elif ch == "2": sm.view_students()
        elif ch == "3": sm.update_student()
        elif ch == "4": sm.delete_student()
        elif ch == "5": sm.search_student()
        elif ch == "0": break
        else: print("  Invalid choice."); pause()

def attendance_menu(sm):
    """Sub-menu for marking attendance, viewing percentages, and viewing low-attendance alerts."""
    while True:
        print_header(" ATTENDANCE MANAGEMENT")
        print("  1. Mark Today's Attendance")
        print("  2. View Attendance Percentage")
        print("  3. Attendance Alerts (< 75%)")
        print("  0. Back to Main Menu")
        ch = input("\n  Choose option: ").strip()
        if ch == "1": sm.mark_attendance()
        elif ch == "2": sm.view_attendance()
        elif ch == "3": sm.attendance_alerts()
        elif ch == "0": break
        else: print("  Invalid choice."); pause()

def marks_menu(sm):
    """Sub-menu for entering marks and viewing marks/grades."""
    while True:
        print_header(" MARKS MANAGEMENT")
        print("  1. Add / Update Marks")
        print("  2. View All Marks & Grades")
        print("  0. Back to Main Menu")
        ch = input("\n  Choose option: ").strip()
        if ch == "1": sm.add_marks()
        elif ch == "2": sm.view_marks()
        elif ch == "0": break
        else: print("  Invalid choice."); pause()

def analytics_menu(sm):
    """Sub-menu for analytics features: prediction, study suggestions, leaderboard, stats, sorting."""
    while True:
        print_header(" ANALYTICS & INTELLIGENCE")
        print("  1. Performance Prediction")
        print("  2. AI Study Suggestions")
        print("  3. Student Leaderboard ")
        print("  4. Statistics Dashboard")
        print("  5. Sort Students")
        print("  0. Back to Main Menu")
        ch = input("\n  Choose option: ").strip()
        if ch == "1": sm.predict_performance()
        elif ch == "2": sm.ai_study_suggestions()
        elif ch == "3": sm.leaderboard()
        elif ch == "4": sm.statistics_dashboard()
        elif ch == "5": sm.sort_students()
        elif ch == "0": break
        else: print("   Invalid choice."); pause()

def main_menu():
    """Top-level menu loop; entry point for the interactive application."""
    sm = StudentManager()
    while True:
        clear()
        print("""
╔══════════════════════════════════════════════════════════╗
║        🎓  STUDENT MANAGEMENT SYSTEM  🎓                 ║
║          Python Console Application v1.0                 ║
╚══════════════════════════════════════════════════════════╝

  1.   Student Management     (Add / View / Edit / Delete)
  2.   Attendance Management  (Mark / View / Alerts)
  3.   Marks Management       (Add / View / Grade)
  4.   Analytics & AI         (Predict / Suggest / Rank)
  0.   Exit
""")
        ch = input("  Choose option: ").strip()
        if ch == "1": student_menu(sm)
        elif ch == "2": attendance_menu(sm)
        elif ch == "3": marks_menu(sm)
        elif ch == "4": analytics_menu(sm)
        elif ch == "0":
            print("\n  Goodbye! Data saved successfully.\n")
            break
        else:
            print("  Invalid choice.")
            pause()

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main_menu()
