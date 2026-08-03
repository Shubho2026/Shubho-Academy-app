import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import io


# ============================================================
# PDF GENERATION FOR RESULT SHEET
# ============================================================
def generate_result_pdf(
    exam_name, subject, total_marks, course, exam_date, results_data
):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    # Academy Title
    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4,
        textColor=colors.HexColor("#1565C0"),
    )
    story.append(Paragraph("Shubho Academy", title_style))

    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"], fontSize=11, spaceAfter=2, textColor=colors.grey
    )
    story.append(Paragraph("Excellence in Education", sub_style))
    story.append(Spacer(1, 10))

    # Exam Info
    info_style = ParagraphStyle(
        "info", parent=styles["Normal"], fontSize=10, spaceAfter=3
    )
    story.append(Paragraph(f"<b>Course/Batch:</b> {course}", info_style))
    story.append(Paragraph(f"<b>Subject:</b> {subject}", info_style))
    story.append(Paragraph(f"<b>Exam:</b> {exam_name}", info_style))
    story.append(Paragraph(f"<b>Total Marks:</b> {int(total_marks)}", info_style))
    story.append(Paragraph(f"<b>Date:</b> {exam_date}", info_style))
    story.append(Spacer(1, 14))

    # Grade function
    def get_grade(pct):
        if pct >= 80:
            return "A+"
        elif pct >= 70:
            return "A"
        elif pct >= 60:
            return "A-"
        elif pct >= 50:
            return "B"
        elif pct >= 40:
            return "C"
        elif pct >= 33:
            return "D"
        else:
            return "F"

    # Table
    table_data = [["SL", "Student ID", "Name", "Marks", "Percentage", "Grade"]]
    for i, row in enumerate(results_data, 1):
        pct = round((row["marks"] / total_marks) * 100, 1)
        grade = get_grade(pct)
        table_data.append(
            [str(i), str(row["id"]), row["name"], str(row["marks"]), f"{pct}%", grade]
        )

    table = Table(table_data, colWidths=[30, 70, 180, 60, 80, 50])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#E3F2FD")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)

    # Summary
    story.append(Spacer(1, 16))
    marks_list = [r["marks"] for r in results_data]
    pct_list = [(r["marks"] / total_marks * 100) for r in results_data]
    summary_style = ParagraphStyle(
        "summary", parent=styles["Normal"], fontSize=9, textColor=colors.grey
    )
    story.append(
        Paragraph(
            f"Total Students: {len(results_data)} | "
            f"Highest: {max(marks_list):.0f} | "
            f"Lowest: {min(marks_list):.0f} | "
            f"Average: {sum(marks_list) / len(marks_list):.1f} | "
            f"Pass Rate: {sum(1 for p in pct_list if p >= 33) / len(pct_list) * 100:.1f}%",
            summary_style,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def generate_routine_pdf(routine_data, class_filter="All"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4,
        textColor=colors.HexColor("#1565C0"),
    )
    story.append(Paragraph("Shubho Academy", title_style))
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"], fontSize=11, spaceAfter=2, textColor=colors.grey
    )
    story.append(Paragraph("Class Routine", sub_style))
    if class_filter != "All":
        story.append(Paragraph(f"Course/Batch: {class_filter}", sub_style))
    story.append(Spacer(1, 12))

    table_data = [["Class/Batch", "Day", "Time", "Subject", "Teacher"]]
    for _, row in routine_data.iterrows():
        table_data.append(
            [
                row.get("class_name", ""),
                row.get("day", ""),
                row.get("time_slot", ""),
                row.get("subject", ""),
                row.get("teacher_name", "") or "N/A",
            ]
        )

    col_widths = [100, 70, 100, 90, 110]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#E3F2FD")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def generate_attendance_pdf(
    attendance_data, report_type="summary", date_str="", class_name=None
):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4,
        textColor=colors.HexColor("#1565C0"),
    )
    story.append(Paragraph("Shubho Academy", title_style))
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"], fontSize=11, spaceAfter=4, textColor=colors.grey
    )

    if report_type == "by_date":
        title_text = f"Attendance Report — {date_str}"
        if class_name:
            title_text += f"  |  Class: {class_name}"
        story.append(Paragraph(title_text, sub_style))
        story.append(Spacer(1, 12))
        if class_name:
            table_data = [["ID", "Name", "Status"]]
            for _, row in attendance_data.iterrows():
                table_data.append(
                    [str(row.get("student_id", "")), row["name"], row["status"]]
                )
            col_widths = [50, 280, 100]
        else:
            table_data = [["Name", "Class", "Status"]]
            for _, row in attendance_data.iterrows():
                table_data.append([row["name"], row["class"], row["status"]])
            col_widths = [180, 150, 100]
    else:
        title_text = "Overall Attendance Summary"
        if class_name:
            title_text += f"  |  Class: {class_name}"
        story.append(Paragraph(title_text, sub_style))
        story.append(Spacer(1, 12))
        if class_name:
            table_data = [["ID", "Name", "Days Present", "Days Absent", "Attendance %"]]
        else:
            table_data = [
                ["Name", "Class", "Days Present", "Days Absent", "Attendance %"]
            ]
        for _, row in attendance_data.iterrows():
            total = row["days_present"] + row["days_absent"]
            pct = f"{(row['days_present'] / total * 100):.1f}%" if total > 0 else "0%"
            if class_name:
                table_data.append(
                    [
                        str(row.get("student_id", "")),
                        row["name"],
                        str(int(row["days_present"])),
                        str(int(row["days_absent"])),
                        pct,
                    ]
                )
            else:
                table_data.append(
                    [
                        row["name"],
                        row["class"],
                        str(int(row["days_present"])),
                        str(int(row["days_absent"])),
                        pct,
                    ]
                )
        col_widths = [50, 200, 80, 80, 80] if class_name else [150, 120, 80, 80, 80]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#E3F2FD")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def generate_fee_pdf(fee_data, class_name=None, student_name=None, month_name=None):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=18,
        spaceAfter=4,
        textColor=colors.HexColor("#1565C0"),
    )
    story.append(Paragraph("Shubho Academy", title_style))
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"], fontSize=11, spaceAfter=4, textColor=colors.grey
    )

    title_text = "Fee / Payment Report"
    if month_name:
        title_text += f"  |  Month: {month_name}"
    if class_name:
        title_text += f"  |  Class: {class_name}"
    if student_name:
        title_text += f"  |  Student: {student_name}"
    story.append(Paragraph(title_text, sub_style))
    story.append(Spacer(1, 12))

    if class_name:
        table_data = [["ID", "Name", "Month", "Amount", "Status", "Payment Date"]]
        for _, row in fee_data.iterrows():
            table_data.append(
                [
                    str(row.get("student_id", "")),
                    row["name"],
                    row["month"],
                    f"{row['amount']:.0f}",
                    row["status"],
                    row.get("payment_date", "") or "-",
                ]
            )
        col_widths = [35, 110, 75, 70, 65, 90]
    else:
        table_data = [
            ["ID", "Name", "Class", "Month", "Amount", "Status", "Payment Date"]
        ]
        for _, row in fee_data.iterrows():
            table_data.append(
                [
                    str(row.get("student_id", "")),
                    row["name"],
                    row["class"],
                    row["month"],
                    f"{row['amount']:.0f}",
                    row["status"],
                    row.get("payment_date", "") or "-",
                ]
            )
        col_widths = [30, 90, 75, 65, 60, 55, 80]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#E3F2FD")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)

    # Summary
    story.append(Spacer(1, 14))
    total_paid = fee_data[fee_data["status"] == "Paid"]["amount"].sum()
    total_pending = fee_data[fee_data["status"] == "Pending"]["amount"].sum()
    summary_style = ParagraphStyle(
        "summary", parent=styles["Normal"], fontSize=9, textColor=colors.grey
    )
    story.append(
        Paragraph(
            f"Total Records: {len(fee_data)} | "
            f"Total Paid: {total_paid:.0f} Taka | "
            f"Total Pending: {total_pending:.0f} Taka",
            summary_style,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ---------- Page Setting ----------
st.set_page_config(page_title="Shubho Academy", layout="wide")

# ============================================================
# LOGIN SYSTEM
# ============================================================
# Simple fixed admin username/password.
# In a real production app, this would be stored securely (hashed) in
# the database instead of directly in code, but for this academic
# project a simple check is enough to demonstrate access control.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "shubho2026"


def login_page():
    st.title("🔒 Shubho Academy - Login")
    st.write("Please log in to access the Management System.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect username or password. Please try again.")


# Initialize login state once per session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If not logged in, show only the login page and stop everything else
if not st.session_state.logged_in:
    login_page()
    st.stop()

DB_FILE = "academy.db"


# ============================================================
# DATABASE SETUP
# ============================================================
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            phone TEXT NOT NULL,
            guardian_phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            payment_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            day TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            subject TEXT NOT NULL,
            faculty_id INTEGER,
            FOREIGN KEY (faculty_id) REFERENCES faculty (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL UNIQUE,
            monthly_fee REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty_payment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            payment_date TEXT,
            FOREIGN KEY (faculty_id) REFERENCES faculty (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exam_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            marks_obtained REAL NOT NULL,
            total_marks REAL NOT NULL,
            exam_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    """)

    conn.commit()
    conn.close()

    # Add default courses the first time the app runs, so dropdowns are never empty
    default_courses = [
        ("Class 6", 1000),
        ("Class 7", 1000),
        ("Class 8", 1200),
        ("Class 9", 1600),
        ("Class 10", 1600),
        ("HSC 1st Year", 3000),
        ("HSC 2nd Year", 3000),
        ("Spoken English Course", 1500),
    ]
    conn2 = get_connection()
    cursor2 = conn2.cursor()
    for name, fee in default_courses:
        cursor2.execute(
            "INSERT OR IGNORE INTO courses (course_name, monthly_fee) VALUES (?, ?)",
            (name, fee),
        )
    conn2.commit()
    conn2.close()


create_tables()


# ============================================================
# STUDENT FUNCTIONS
# ============================================================
def add_student(name, student_class, phone, guardian_phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, class, phone, guardian_phone) VALUES (?, ?, ?, ?)",
        (name, student_class, phone, guardian_phone),
    )
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


# ============================================================
# FEE FUNCTIONS
# ============================================================
def add_fee_record(student_id, month, amount, status, payment_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fees (student_id, month, amount, status, payment_date) VALUES (?, ?, ?, ?, ?)",
        (student_id, month, amount, status, payment_date),
    )
    conn.commit()
    conn.close()


def get_all_fees():
    conn = get_connection()
    query = """
        SELECT fees.id, students.id AS student_id, students.name, students.class,
               fees.month, fees.amount, fees.status, fees.payment_date
        FROM fees
        JOIN students ON fees.student_id = students.id
        ORDER BY students.class, students.id, fees.id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def delete_fee_record(fee_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fees WHERE id = ?", (fee_id,))
    conn.commit()
    conn.close()


def get_pending_fees():
    conn = get_connection()
    query = """
        SELECT students.name, students.phone, students.guardian_phone,
               fees.month, fees.amount
        FROM fees
        JOIN students ON fees.student_id = students.id
        WHERE fees.status = 'Pending'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_pending_fees_for_student(student_id):
    """All pending (unpaid) fee rows for one student, oldest first."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, month, amount FROM fees WHERE student_id = ? AND status = 'Pending' ORDER BY id ASC",
        conn,
        params=(student_id,),
    )
    conn.close()
    return df


def get_total_due_for_student(student_id):
    pending_df = get_pending_fees_for_student(student_id)
    if pending_df.empty:
        return 0.0
    return float(pending_df["amount"].sum())


def apply_payment(student_id, payment_amount, payment_date):
    """
    Clears a student's pending dues FIFO (oldest month first) using the
    payment amount received. Fully covered months are marked Paid; if the
    payment only partially covers the oldest pending month, that record's
    remaining due is reduced and it stays Pending.
    Returns the total amount actually applied.
    """
    pending_df = get_pending_fees_for_student(student_id)
    remaining_payment = float(payment_amount)
    applied = 0.0

    conn = get_connection()
    cursor = conn.cursor()

    for _, row in pending_df.iterrows():
        if remaining_payment <= 0:
            break
        fee_id = int(row["id"])
        due_amount = float(row["amount"])

        if remaining_payment >= due_amount:
            # Fully pay off this month
            cursor.execute(
                "UPDATE fees SET status = 'Paid', payment_date = ? WHERE id = ?",
                (payment_date, fee_id),
            )
            remaining_payment -= due_amount
            applied += due_amount
        else:
            # Partially pay this month — reduce its remaining due, stays Pending
            new_due = due_amount - remaining_payment
            cursor.execute(
                "UPDATE fees SET amount = ? WHERE id = ?",
                (new_due, fee_id),
            )
            applied += remaining_payment
            remaining_payment = 0.0

    conn.commit()
    conn.close()
    return applied


def get_course_monthly_fee(course_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT monthly_fee FROM courses WHERE course_name = ?", (course_name,)
    )
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row else 0.0


def ensure_current_month_due(student_id, student_class):
    """
    Auto-bills the current calendar month for a student, if it hasn't been
    billed yet, using the monthly fee set for their course. This removes the
    need to manually type a month/amount every time — the Due box just
    reflects reality automatically.
    """
    month_name = date.today().strftime("%B")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM fees WHERE student_id = ? AND month = ?",
        (student_id, month_name),
    )
    already_billed = cursor.fetchone()
    conn.close()

    if already_billed is None:
        monthly_fee = get_course_monthly_fee(student_class)
        if monthly_fee > 0:
            add_fee_record(student_id, month_name, monthly_fee, "Pending", "")


def fix_student_pending_amounts(student_id, correct_fee):
    """
    Resets every Pending fee row for this student to the class's official
    monthly fee. Used to clean up old records where someone had typed a
    different amount by mistake (e.g. 500 instead of the class's 1600).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE fees SET amount = ? WHERE student_id = ? AND status = 'Pending'",
        (correct_fee, student_id),
    )
    conn.commit()
    conn.close()


# ============================================================
# FACULTY FUNCTIONS
# ============================================================
def add_faculty(name, subject, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty (name, subject, phone) VALUES (?, ?, ?)",
        (name, subject, phone),
    )
    conn.commit()
    conn.close()


def get_all_faculty():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM faculty", conn)
    conn.close()
    return df


def delete_faculty(faculty_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty WHERE id = ?", (faculty_id,))
    conn.commit()
    conn.close()


# ============================================================
# ROUTINE FUNCTIONS
# ============================================================
def add_routine(class_name, day, time_slot, subject, faculty_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO routine (class_name, day, time_slot, subject, faculty_id) VALUES (?, ?, ?, ?, ?)",
        (class_name, day, time_slot, subject, faculty_id),
    )
    conn.commit()
    conn.close()


def get_all_routine():
    conn = get_connection()
    query = """
        SELECT routine.id, routine.class_name, routine.day, routine.time_slot,
               routine.subject, faculty.name AS teacher_name
        FROM routine
        LEFT JOIN faculty ON routine.faculty_id = faculty.id
        ORDER BY routine.class_name, routine.day
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def delete_routine(routine_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routine WHERE id = ?", (routine_id,))
    conn.commit()
    conn.close()


# ============================================================
# ATTENDANCE FUNCTIONS
# ============================================================
def mark_attendance(student_id, att_date, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
        (student_id, att_date, status),
    )
    conn.commit()
    conn.close()


def get_attendance_by_date(att_date):
    conn = get_connection()
    query = """
        SELECT attendance.id, students.name, students.class,
               attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE attendance.date = ?
    """
    df = pd.read_sql_query(query, conn, params=(att_date,))
    conn.close()
    return df


def get_attendance_summary():
    conn = get_connection()
    query = """
        SELECT students.name, students.class,
               SUM(CASE WHEN attendance.status = 'Present' THEN 1 ELSE 0 END) AS days_present,
               SUM(CASE WHEN attendance.status = 'Absent' THEN 1 ELSE 0 END) AS days_absent
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        GROUP BY students.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ============================================================
# RESULT FUNCTIONS
# ============================================================
def add_result(student_id, exam_name, subject, marks_obtained, total_marks, exam_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (student_id, exam_name, subject, marks_obtained, total_marks, exam_date) VALUES (?, ?, ?, ?, ?, ?)",
        (student_id, exam_name, subject, marks_obtained, total_marks, exam_date),
    )
    conn.commit()
    conn.close()


def get_results_by_student(student_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM results WHERE student_id = ? ORDER BY exam_date DESC",
        conn,
        params=(student_id,),
    )
    conn.close()
    return df


def delete_result(result_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    conn.close()


# ============================================================
# STUDENT PROFILE FUNCTION (all info in one place by ID)
# ============================================================
def get_student_profile(student_id):
    conn = get_connection()

    # Basic info
    student = pd.read_sql_query(
        "SELECT * FROM students WHERE id = ?", conn, params=(student_id,)
    )

    # Fee history
    fees = pd.read_sql_query(
        "SELECT month, amount, status, payment_date FROM fees WHERE student_id = ? ORDER BY id DESC",
        conn,
        params=(student_id,),
    )

    # Attendance
    attendance = pd.read_sql_query(
        "SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC",
        conn,
        params=(student_id,),
    )

    # Results
    results = pd.read_sql_query(
        "SELECT exam_name, subject, marks_obtained, total_marks, exam_date FROM results WHERE student_id = ? ORDER BY exam_date DESC",
        conn,
        params=(student_id,),
    )

    conn.close()
    return student, fees, attendance, results


# ============================================================
# COURSE FUNCTIONS (dynamic batches/courses, no code change needed)
# ============================================================
def add_course(course_name, monthly_fee):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (course_name, monthly_fee) VALUES (?, ?)",
        (course_name, monthly_fee),
    )
    conn.commit()
    conn.close()


def get_all_courses():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM courses ORDER BY course_name", conn)
    conn.close()
    return df


def delete_course(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()


def update_course_fee(course_id, new_fee):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE courses SET monthly_fee = ? WHERE id = ?", (new_fee, course_id)
    )
    conn.commit()
    conn.close()


# ============================================================
# FACULTY PAYMENT FUNCTIONS
# ============================================================
def add_faculty_payment(faculty_id, month, amount, status, payment_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty_payment (faculty_id, month, amount, status, payment_date) VALUES (?, ?, ?, ?, ?)",
        (faculty_id, month, amount, status, payment_date),
    )
    conn.commit()
    conn.close()


def get_all_faculty_payments():
    conn = get_connection()
    query = """
        SELECT faculty_payment.id, faculty.name, faculty.subject, faculty_payment.month,
               faculty_payment.amount, faculty_payment.status, faculty_payment.payment_date
        FROM faculty_payment
        JOIN faculty ON faculty_payment.faculty_id = faculty.id
        ORDER BY faculty_payment.id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def delete_faculty_payment(payment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faculty_payment WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()


# ============================================================
# FINANCIAL SUMMARY FUNCTIONS
# ============================================================
def get_expected_monthly_income():
    # Expected income = for each student, the monthly_fee of the course they are in
    conn = get_connection()
    query = """
        SELECT students.class, courses.monthly_fee
        FROM students
        LEFT JOIN courses ON students.class = courses.course_name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df["monthly_fee"] = df["monthly_fee"].fillna(0)
    return df["monthly_fee"].sum()


# ============================================================
# APP TITLE / BANNER
# ============================================================
import os as _os

LOGO_PATH = "assets/logo_banner.png"
if _os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, use_container_width=True)
else:
    st.title("📚 Shubho Academy Management System")

st.caption(
    "Subjects Taught: Physics • Chemistry • Higher Math • General Math • Biology • English • Bangla • ICT"
)

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Add Student",
        "Student List",
        "Student Profile",
        "Add Fee Record",
        "Fee Records",
        "Pending Fees",
        "Add Result",
        "Results",
        "Add Faculty",
        "Faculty List",
        "Add Faculty Payment",
        "Faculty Payments",
        "Add Routine",
        "Routine",
        "Take Attendance",
        "Attendance Summary",
        "Add Course",
        "Course List",
        "Financial Summary",
    ],
    key="main_menu",
)

st.sidebar.divider()
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ============================================================
# PAGE 1: ADD STUDENT
# ============================================================
# ============================================================
# PAGE 0: DASHBOARD
# ============================================================
if menu == "Dashboard":
    st.header("Dashboard Overview")

    students_df = get_all_students()
    faculty_df = get_all_faculty()
    courses_df = get_all_courses()
    fees_df = get_all_fees()
    pending_df = get_pending_fees()

    # Top row: basic counts
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(students_df))
    col2.metric("Total Faculty", len(faculty_df))
    col3.metric("Total Courses", len(courses_df))

    st.divider()

    # Second row: money summary
    total_collected = (
        fees_df[fees_df["status"] == "Paid"]["amount"].sum() if not fees_df.empty else 0
    )
    total_pending = (
        fees_df[fees_df["status"] == "Pending"]["amount"].sum()
        if not fees_df.empty
        else 0
    )
    expected_income = get_expected_monthly_income()

    col4, col5, col6 = st.columns(3)
    col4.metric("Expected Monthly Income", f"{expected_income:.0f} Taka")
    col5.metric("Total Collected", f"{total_collected:.0f} Taka")
    col6.metric("Total Pending (Students)", f"{total_pending:.0f} Taka")

    st.divider()

    # Today's attendance summary
    st.subheader("Today's Attendance")
    today_str = str(date.today())
    today_attendance = get_attendance_by_date(today_str)

    if today_attendance.empty:
        st.info("No attendance taken yet today.")
    else:
        present_count = len(today_attendance[today_attendance["status"] == "Present"])
        absent_count = len(today_attendance[today_attendance["status"] == "Absent"])
        col7, col8 = st.columns(2)
        col7.metric("Present Today", present_count)
        col8.metric("Absent Today", absent_count)

    st.divider()

    # Students with pending fees - quick view
    st.subheader("Students With Pending Fees")
    if pending_df.empty:
        st.success("No pending fees! Everyone has paid.")
    else:
        st.dataframe(pending_df, use_container_width=True)

# ============================================================
# PAGE 1: ADD STUDENT
# ============================================================
elif menu == "Add Student":
    st.header("Add New Student")

    name = st.text_input("Student Name")
    courses_df = get_all_courses()
    if courses_df.empty:
        st.warning("No courses found. Please add a course first in 'Add Course'.")
        student_class = None
    else:
        student_class = st.selectbox(
            "Class / Course", courses_df["course_name"].tolist()
        )
    phone = st.text_input("Student Phone Number")
    guardian_phone = st.text_input("Guardian Phone Number")

    if st.button("Save Student"):
        if name.strip() == "" or phone.strip() == "" or student_class is None:
            st.error("Name, Phone Number, and Class/Course are required!")
        else:
            add_student(name, student_class, phone, guardian_phone)
            st.success(f"{name} has been added successfully!")

# ============================================================
# PAGE 2: STUDENT LIST
# ============================================================
elif menu == "Student List":
    st.header("All Students")

    students_df = get_all_students()

    if students_df.empty:
        st.info("No students added yet. Go to 'Add Student' first.")
    else:
        st.dataframe(students_df, use_container_width=True)
        st.write(f"**Total Students:** {len(students_df)}")

        st.subheader("Delete a Student")
        students_df["label"] = (
            "ID "
            + students_df["id"].astype(str)
            + " - "
            + students_df["name"]
            + " - "
            + students_df["class"]
            + " - "
            + students_df["phone"]
        )
        student_to_delete = st.selectbox(
            "Select student to delete", students_df["label"]
        )
        delete_id = int(student_to_delete.split(" ")[1])

        if st.button("Delete This Student"):
            delete_student(delete_id)
            st.success("Student deleted! Switch menu to see the update.")

# ============================================================
# PAGE 3: ADD FEE RECORD (Class -> Student -> Auto Due -> Payment)
# ============================================================
elif menu == "Add Fee Record":
    st.header("Add Fee Record")

    courses_df = get_all_courses()
    students_df = get_all_students()

    if students_df.empty:
        st.warning("Please add students first.")
    elif courses_df.empty:
        st.warning("Please add a course/class first.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            pay_class = st.selectbox(
                "Select Class", courses_df["course_name"].tolist(), key="fee_class"
            )
        class_students = students_df[students_df["class"] == pay_class].reset_index(
            drop=True
        )

        with c2:
            if class_students.empty:
                st.warning(f"No students found in '{pay_class}'.")
                fee_student_id = None
            else:
                student_labels = (
                    "ID "
                    + class_students["id"].astype(str)
                    + " - "
                    + class_students["name"]
                )
                fee_student_choice = st.selectbox(
                    "Select Student (ID - Name)", student_labels, key="fee_student"
                )
                fee_student_id = int(fee_student_choice.split(" ")[1])

        class_fee = get_course_monthly_fee(pay_class)
        st.info(
            f"📌 **{pay_class}** official monthly fee: **{class_fee:.0f} Taka** "
            "— every student in this class should be billed this amount."
        )

        if fee_student_id is not None:
            # Auto-bill this month if it hasn't been billed yet
            ensure_current_month_due(fee_student_id, pay_class)

            pending_df = get_pending_fees_for_student(fee_student_id)
            total_due = get_total_due_for_student(fee_student_id)

            # Catch old/mistyped dues that don't match this class's official fee
            mismatched = (
                pending_df[pending_df["amount"] != class_fee]
                if not pending_df.empty
                else pending_df
            )
            if not mismatched.empty:
                mismatch_list = ", ".join(
                    f"{m} ({a:.0f} Taka)"
                    for m, a in zip(mismatched["month"], mismatched["amount"])
                )
                st.warning(
                    f"⚠️ This student's due doesn't match the class fee for: {mismatch_list}. "
                    f"It should be {class_fee:.0f} Taka per month."
                )
                if st.button(
                    f"🔧 Fix Due to Match Class Fee ({class_fee:.0f} Taka)",
                    key="fix_due_btn",
                ):
                    fix_student_pending_amounts(fee_student_id, class_fee)
                    st.success("Due amount corrected to match the class fee!")
                    st.rerun()

            st.divider()

            d1, d2 = st.columns(2)
            with d1:
                st.text_input(
                    "Due (Taka)",
                    value=f"{total_due:.0f}",
                    disabled=True,
                    key="fee_due_display",
                )
            with d2:
                due_months = (
                    ", ".join(pending_df["month"].tolist())
                    if not pending_df.empty
                    else "None"
                )
                st.text_input(
                    "Due Month(s)",
                    value=due_months,
                    disabled=True,
                    key="fee_due_months_display",
                )

            payment_amount = st.number_input(
                "Payment (Taka)",
                min_value=0.0,
                max_value=float(total_due) if total_due > 0 else 0.0,
                step=50.0,
                key="fee_payment_amount",
            )

            remaining_due = total_due - payment_amount
            st.text_input(
                "Remaining Due (Taka)",
                value=f"{remaining_due:.0f}",
                disabled=True,
                key="fee_remaining_due",
            )

            pay_date = st.date_input("Date", value=date.today(), key="fee_pay_date")

            if st.button("✅ Save", type="primary", use_container_width=True):
                if total_due <= 0:
                    st.info("No due for this student — nothing to save.")
                elif payment_amount <= 0:
                    st.error("Please enter a Payment amount greater than 0.")
                else:
                    applied = apply_payment(
                        fee_student_id, payment_amount, str(pay_date)
                    )
                    st.success(
                        f"Payment of {applied:.0f} Taka saved! "
                        f"Remaining due: {total_due - applied:.0f} Taka."
                    )
                    st.balloons()

# ============================================================
# PAGE 4: ALL FEE RECORDS
# ============================================================
elif menu == "Fee Records":
    st.header("All Fee Records")

    fees_df = get_all_fees()

    if fees_df.empty:
        st.info("No fee records yet.")
    else:
        overall_paid = fees_df[fees_df["status"] == "Paid"]["amount"].sum()
        overall_pending = fees_df[fees_df["status"] == "Pending"]["amount"].sum()
        col1, col2 = st.columns(2)
        col1.metric("Total Collected (All Classes)", f"{overall_paid:.0f} Taka")
        col2.metric("Total Pending (All Classes)", f"{overall_pending:.0f} Taka")

        st.divider()

        class_list3 = sorted(fees_df["class"].unique().tolist())
        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        months_present = month_order

        f1, f2 = st.columns(2)
        with f1:
            class_choice3 = st.selectbox(
                "Filter by Class",
                ["All (class-wise tables)"] + class_list3,
                key="fee_class_filter",
            )
        with f2:
            month_choice = st.selectbox(
                "Filter by Month",
                ["All Months"] + months_present,
                key="fee_month_filter",
            )
        search_query = st.text_input(
            "🔍 Search by Student ID or Name (optional)", key="fee_search"
        )

        selected_month = None if month_choice == "All Months" else month_choice

        display_cols = [
            "student_id",
            "name",
            "month",
            "amount",
            "status",
            "payment_date",
        ]
        rename_cols = {
            "student_id": "ID",
            "name": "Name",
            "month": "Month",
            "amount": "Amount",
            "status": "Status",
            "payment_date": "Payment Date",
        }

        def apply_search(df):
            if selected_month:
                df = df[df["month"] == selected_month]
            if not search_query.strip():
                return df
            q = search_query.strip()
            return df[
                df["name"].str.contains(q, case=False, na=False)
                | df["student_id"].astype(str).str.contains(q, na=False)
            ]

        month_tag = f"_{selected_month}" if selected_month else ""

        if class_choice3 == "All (class-wise tables)":
            for cls in class_list3:
                cls_df = apply_search(fees_df[fees_df["class"] == cls])
                if cls_df.empty:
                    continue
                st.subheader(f"📘 {cls}")
                shown = cls_df[display_cols].rename(columns=rename_cols)
                st.dataframe(shown, use_container_width=True, hide_index=True)

                paid_c = cls_df[cls_df["status"] == "Paid"]["amount"].sum()
                pending_c = cls_df[cls_df["status"] == "Pending"]["amount"].sum()
                m1, m2 = st.columns(2)
                m1.metric("Collected", f"{paid_c:.0f} Taka")
                m2.metric("Pending", f"{pending_c:.0f} Taka")

                pdf_bytes = generate_fee_pdf(
                    cls_df, class_name=cls, month_name=selected_month
                )
                st.download_button(
                    label=f"⬇️ Download {cls} Fee Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"Fee_Report_{cls}{month_tag}.pdf".replace(" ", "_"),
                    mime="application/pdf",
                    key=f"fee_pdf_{cls}",
                )
                st.divider()

            combined_df = apply_search(fees_df)
            if not combined_df.empty:
                pdf_bytes_all = generate_fee_pdf(combined_df, month_name=selected_month)
                st.download_button(
                    label="⬇️ Download Combined Fee Report — All Classes (PDF)",
                    data=pdf_bytes_all,
                    file_name=f"Fee_Report_AllClasses{month_tag}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            cls_df = apply_search(fees_df[fees_df["class"] == class_choice3])
            if cls_df.empty:
                st.info("No matching fee records for this class / month / search.")
            else:
                shown = cls_df[display_cols].rename(columns=rename_cols)
                st.dataframe(shown, use_container_width=True, hide_index=True)

                paid_c = cls_df[cls_df["status"] == "Paid"]["amount"].sum()
                pending_c = cls_df[cls_df["status"] == "Pending"]["amount"].sum()
                m1, m2 = st.columns(2)
                m1.metric("Collected", f"{paid_c:.0f} Taka")
                m2.metric("Pending", f"{pending_c:.0f} Taka")

                student_name_for_pdf = None
                if search_query.strip() and cls_df["student_id"].nunique() == 1:
                    student_name_for_pdf = cls_df["name"].iloc[0]

                pdf_bytes = generate_fee_pdf(
                    cls_df,
                    class_name=class_choice3,
                    student_name=student_name_for_pdf,
                    month_name=selected_month,
                )
                pdf_label = (
                    f"⬇️ Download {student_name_for_pdf}'s Fee Report (PDF)"
                    if student_name_for_pdf
                    else f"⬇️ Download {class_choice3} Fee Report (PDF)"
                )
                st.download_button(
                    label=pdf_label,
                    data=pdf_bytes,
                    file_name=f"Fee_Report_{class_choice3}{month_tag}.pdf".replace(
                        " ", "_"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                )

        st.divider()
        st.subheader("Delete a Fee Record")
        fees_df["label"] = (
            "ID "
            + fees_df["id"].astype(str)
            + " - "
            + fees_df["name"]
            + " - "
            + fees_df["month"]
            + " - "
            + fees_df["amount"].astype(str)
            + " Taka"
        )
        record_to_delete = st.selectbox("Select record to delete", fees_df["label"])
        delete_id = int(record_to_delete.split(" ")[1])

        if st.button("Delete This Record"):
            delete_fee_record(delete_id)
            st.success(
                "Record deleted! Please refresh the page or switch menu to see the update."
            )

# ============================================================
# PAGE 5: PENDING FEES
# ============================================================
elif menu == "Pending Fees":
    st.header("Students With Pending Fees")

    pending_df = get_pending_fees()

    if pending_df.empty:
        st.success("No pending fees! Everyone has paid.")
    else:
        st.dataframe(pending_df, use_container_width=True)
        st.write(f"**Total Students with Pending Fees:** {len(pending_df)}")

# ============================================================
# PAGE 6: ADD FACULTY
# ============================================================
elif menu == "Add Faculty":
    st.header("Add New Faculty")

    f_name = st.text_input("Faculty Name")
    f_subjects = st.multiselect(
        "Subject(s) - You can select more than one",
        [
            "Physics",
            "Chemistry",
            "Higher Math",
            "General Math",
            "Biology",
            "English",
            "Bangla",
            "ICT",
        ],
    )
    f_phone = st.text_input("Faculty Phone Number")

    if st.button("Save Faculty"):
        if f_name.strip() == "" or f_phone.strip() == "" or len(f_subjects) == 0:
            st.error("Name, Phone Number, and at least one Subject are required!")
        else:
            # Join multiple subjects into one text like "Physics, Higher Math"
            subject_text = ", ".join(f_subjects)
            add_faculty(f_name, subject_text, f_phone)
            st.success(f"{f_name} has been added successfully!")

# ============================================================
# PAGE 7: FACULTY LIST
# ============================================================
elif menu == "Faculty List":
    st.header("All Faculty")

    faculty_df = get_all_faculty()

    if faculty_df.empty:
        st.info("No faculty added yet. Go to 'Add Faculty' first.")
    else:
        st.dataframe(faculty_df, use_container_width=True)
        st.write(f"**Total Faculty:** {len(faculty_df)}")

        st.subheader("Delete a Faculty Member")
        faculty_df["label"] = (
            "ID "
            + faculty_df["id"].astype(str)
            + " - "
            + faculty_df["name"]
            + " - "
            + faculty_df["subject"]
        )
        faculty_to_delete = st.selectbox(
            "Select faculty to delete", faculty_df["label"]
        )
        delete_id = int(faculty_to_delete.split(" ")[1])

        if st.button("Delete This Faculty"):
            delete_faculty(delete_id)
            st.success("Faculty deleted! Switch menu to see the update.")

# ============================================================
# PAGE 8: ADD ROUTINE
# ============================================================
elif menu == "Add Routine":
    st.header("Add Class Routine")

    faculty_df = get_all_faculty()
    courses_df = get_all_courses()

    if courses_df.empty:
        st.warning("No courses found. Please add a course first in 'Add Course'.")
        r_class = None
    else:
        r_class = st.selectbox("Class / Batch", courses_df["course_name"].tolist())
    r_day = st.selectbox(
        "Day",
        ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    )
    r_time = st.text_input("Time (example: 4:00 PM - 5:30 PM)")
    r_subject = st.selectbox(
        "Subject",
        [
            "Physics",
            "Chemistry",
            "Higher Math",
            "General Math",
            "Biology",
            "English",
            "Bangla",
            "ICT",
        ],
    )

    faculty_id = None
    if not faculty_df.empty:
        faculty_choice = st.selectbox("Assign Teacher", faculty_df["name"])
        faculty_id = int(
            faculty_df.loc[faculty_df["name"] == faculty_choice, "id"].iloc[0]
        )
    else:
        st.warning(
            "No faculty added yet. You can still save the routine without a teacher assigned."
        )

    if st.button("Save Routine"):
        if r_time.strip() == "":
            st.error("Please enter a time slot.")
        else:
            add_routine(r_class, r_day, r_time, r_subject, faculty_id)
            st.success("Routine added successfully!")

# ============================================================
# PAGE 9: VIEW ROUTINE
# ============================================================
elif menu == "Routine":
    st.header("Class Routine")

    routine_df = get_all_routine()

    if routine_df.empty:
        st.info("No routine added yet. Go to 'Add Routine' first.")
    else:
        class_filter = st.selectbox(
            "Filter by Class",
            ["All"] + sorted(routine_df["class_name"].unique().tolist()),
        )
        if class_filter != "All":
            display_df = routine_df[routine_df["class_name"] == class_filter]
        else:
            display_df = routine_df

        st.dataframe(display_df, use_container_width=True)

        st.divider()

        # PDF Download
        try:
            pdf_bytes = generate_routine_pdf(display_df, class_filter)
            fname = f"Routine_{class_filter}.pdf".replace(" ", "_")
            st.download_button(
                label="⬇️ Download Routine (PDF)",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

        st.divider()
        st.subheader("Delete a Routine Entry")
        routine_df["label"] = (
            "ID "
            + routine_df["id"].astype(str)
            + " - "
            + routine_df["class_name"]
            + " - "
            + routine_df["day"]
            + " - "
            + routine_df["subject"]
        )
        routine_to_delete = st.selectbox(
            "Select routine entry to delete", routine_df["label"]
        )
        delete_id = int(routine_to_delete.split(" ")[1])

        if st.button("Delete This Routine Entry"):
            delete_routine(delete_id)
            st.success("Routine entry deleted! Switch menu to see the update.")

# ============================================================
# PAGE 10: TAKE ATTENDANCE
# ============================================================
elif menu == "Take Attendance":
    st.header("Take Attendance")

    students_df = get_all_students()

    if students_df.empty:
        st.warning("Please add students first.")
    else:
        att_date = st.date_input("Select Date", value=date.today())
        class_choice = st.selectbox(
            "Select Class", ["All"] + sorted(students_df["class"].unique().tolist())
        )

        if class_choice != "All":
            filtered_students = students_df[students_df["class"] == class_choice]
        else:
            filtered_students = students_df

        st.write("Mark each student as Present or Absent:")

        # Store choices in a dictionary as we go through each student
        attendance_choices = {}
        for _, row in filtered_students.iterrows():
            choice = st.radio(
                row["name"],
                ["Present", "Absent"],
                key=f"att_{row['id']}",
                horizontal=True,
            )
            attendance_choices[row["id"]] = choice

        if st.button("Save Attendance"):
            for student_id, status in attendance_choices.items():
                mark_attendance(student_id, str(att_date), status)
            st.success(
                f"Attendance saved for {len(attendance_choices)} students on {att_date}."
            )

# ============================================================
# PAGE 11: ATTENDANCE SUMMARY
# ============================================================
elif menu == "Attendance Summary":
    st.header("Attendance Summary")

    tab1, tab2 = st.tabs(["By Date", "Overall Summary"])

    with tab1:
        check_date = st.date_input(
            "Check attendance for date", value=date.today(), key="check_date"
        )

        # Fetch this date's attendance with student ID and class included
        conn = get_connection()
        day_with_class = pd.read_sql_query(
            """
            SELECT students.id AS student_id, students.name, students.class,
                   attendance.status
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            WHERE attendance.date = ?
            ORDER BY students.class, students.id
        """,
            conn,
            params=(str(check_date),),
        )
        conn.close()

        if day_with_class.empty:
            st.info("No attendance recorded for this date.")
        else:
            present = len(day_with_class[day_with_class["status"] == "Present"])
            absent = len(day_with_class[day_with_class["status"] == "Absent"])
            col1, col2 = st.columns(2)
            col1.metric("Present", present)
            col2.metric("Absent", absent)

            st.divider()

            class_list = sorted(day_with_class["class"].unique().tolist())
            class_choice = st.selectbox(
                "Filter by Class",
                ["All (class-wise tables)"] + class_list,
                key="att_by_date_class_filter",
            )

            if class_choice == "All (class-wise tables)":
                # Show a separate ID / Name / Status table for each class
                for cls in class_list:
                    st.subheader(f"📘 {cls}")
                    cls_df = day_with_class[day_with_class["class"] == cls][
                        ["student_id", "name", "status"]
                    ].rename(
                        columns={"student_id": "ID", "name": "Name", "status": "Status"}
                    )
                    st.dataframe(cls_df, use_container_width=True, hide_index=True)

                    pdf_bytes = generate_attendance_pdf(
                        day_with_class[day_with_class["class"] == cls].rename(
                            columns={"student_id": "student_id"}
                        ),
                        report_type="by_date",
                        date_str=str(check_date),
                        class_name=cls,
                    )
                    st.download_button(
                        label=f"⬇️ Download {cls} Attendance (PDF)",
                        data=pdf_bytes,
                        file_name=f"Attendance_{cls}_{check_date}.pdf".replace(
                            " ", "_"
                        ),
                        mime="application/pdf",
                        key=f"att_pdf_{cls}",
                    )
                    st.divider()

                # Combined PDF (all classes together, like before)
                pdf_bytes_all = generate_attendance_pdf(
                    day_with_class, report_type="by_date", date_str=str(check_date)
                )
                st.download_button(
                    label="⬇️ Download Combined Attendance — All Classes (PDF)",
                    data=pdf_bytes_all,
                    file_name=f"Attendance_AllClasses_{check_date}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                cls_df = day_with_class[day_with_class["class"] == class_choice][
                    ["student_id", "name", "status"]
                ].rename(
                    columns={"student_id": "ID", "name": "Name", "status": "Status"}
                )
                st.dataframe(cls_df, use_container_width=True, hide_index=True)

                pdf_bytes = generate_attendance_pdf(
                    day_with_class[day_with_class["class"] == class_choice],
                    report_type="by_date",
                    date_str=str(check_date),
                    class_name=class_choice,
                )
                st.download_button(
                    label=f"⬇️ Download {class_choice} Attendance (PDF)",
                    data=pdf_bytes,
                    file_name=f"Attendance_{class_choice}_{check_date}.pdf".replace(
                        " ", "_"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                )

    with tab2:
        # Fetch overall summary with student ID and class included
        conn = get_connection()
        summary_with_class = pd.read_sql_query(
            """
            SELECT students.id AS student_id, students.name, students.class,
                   SUM(CASE WHEN attendance.status = 'Present' THEN 1 ELSE 0 END) AS days_present,
                   SUM(CASE WHEN attendance.status = 'Absent' THEN 1 ELSE 0 END) AS days_absent
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            GROUP BY students.id
            ORDER BY students.class, students.id
        """,
            conn,
        )
        conn.close()

        if summary_with_class.empty:
            st.info("No attendance records yet.")
        else:
            summary_with_class["Total Days"] = (
                summary_with_class["days_present"] + summary_with_class["days_absent"]
            )
            summary_with_class["Attendance %"] = (
                summary_with_class["days_present"]
                / summary_with_class["Total Days"]
                * 100
            ).round(1).astype(str) + "%"

            class_list2 = sorted(summary_with_class["class"].unique().tolist())
            class_choice2 = st.selectbox(
                "Filter by Class",
                ["All (class-wise tables)"] + class_list2,
                key="att_overall_class_filter",
            )

            display_cols = {
                "student_id": "ID",
                "name": "Name",
                "days_present": "Days Present",
                "days_absent": "Days Absent",
                "Attendance %": "Attendance %",
            }

            if class_choice2 == "All (class-wise tables)":
                for cls in class_list2:
                    st.subheader(f"📘 {cls}")
                    cls_df = summary_with_class[summary_with_class["class"] == cls][
                        list(display_cols.keys())
                    ].rename(columns=display_cols)
                    st.dataframe(cls_df, use_container_width=True, hide_index=True)

                    pdf_bytes = generate_attendance_pdf(
                        summary_with_class[summary_with_class["class"] == cls],
                        report_type="overall",
                        class_name=cls,
                    )
                    st.download_button(
                        label=f"⬇️ Download {cls} Summary (PDF)",
                        data=pdf_bytes,
                        file_name=f"Attendance_Summary_{cls}.pdf".replace(" ", "_"),
                        mime="application/pdf",
                        key=f"att_summary_pdf_{cls}",
                    )
                    st.divider()

                pdf_bytes_all = generate_attendance_pdf(
                    summary_with_class, report_type="overall"
                )
                st.download_button(
                    label="⬇️ Download Combined Summary — All Classes (PDF)",
                    data=pdf_bytes_all,
                    file_name="Attendance_Summary_AllClasses.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                cls_df = summary_with_class[
                    summary_with_class["class"] == class_choice2
                ][list(display_cols.keys())].rename(columns=display_cols)
                st.dataframe(cls_df, use_container_width=True, hide_index=True)

                pdf_bytes = generate_attendance_pdf(
                    summary_with_class[summary_with_class["class"] == class_choice2],
                    report_type="overall",
                    class_name=class_choice2,
                )
                st.download_button(
                    label=f"⬇️ Download {class_choice2} Summary (PDF)",
                    data=pdf_bytes,
                    file_name=f"Attendance_Summary_{class_choice2}.pdf".replace(
                        " ", "_"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                )

# ============================================================
# PAGE 12: ADD COURSE (Create a new batch/course without coding)
# ============================================================
elif menu == "Add Course":
    st.header("Add New Course / Batch")
    st.write(
        "Use this page to create a new course or batch — for example 'SSC FRB Batch 2' or 'HSC FRB Batch 1'. No coding needed, it will appear everywhere automatically."
    )

    c_name = st.text_input("Course / Batch Name")
    c_fee = st.number_input("Monthly Fee (Taka)", min_value=0, step=100)

    if st.button("Create Course"):
        if c_name.strip() == "":
            st.error("Course name is required!")
        else:
            try:
                add_course(c_name.strip(), c_fee)
                st.success(f"Course '{c_name}' created successfully!")
            except Exception as e:
                st.error(
                    "A course with this name already exists. Please choose a different name."
                )

# ============================================================
# PAGE 13: COURSE LIST
# ============================================================
elif menu == "Course List":
    st.header("All Courses / Batches")

    courses_df = get_all_courses()

    if courses_df.empty:
        st.info("No courses added yet. Go to 'Add Course' first.")
    else:
        st.dataframe(courses_df, use_container_width=True)
        st.write(f"**Total Courses:** {len(courses_df)}")

        st.divider()
        st.subheader("💰 Change a Course's Monthly Fee")
        st.caption(
            "Fees can change anytime — the coaching centre decides. Update it here "
            "and every student in this course will automatically be billed the new "
            "amount from their next due onward."
        )
        edit_labels = (
            "ID "
            + courses_df["id"].astype(str)
            + " - "
            + courses_df["course_name"]
            + " (currently "
            + courses_df["monthly_fee"].astype(str)
            + " Taka/month)"
        )
        e1, e2 = st.columns([2, 1])
        with e1:
            course_to_edit_label = st.selectbox(
                "Select course to update fee", edit_labels, key="fee_edit_select"
            )
        edit_id = int(course_to_edit_label.split(" ")[1])
        current_fee = float(
            courses_df.loc[courses_df["id"] == edit_id, "monthly_fee"].iloc[0]
        )
        with e2:
            new_fee = st.number_input(
                "New Monthly Fee (Taka)",
                min_value=0,
                value=int(current_fee),
                step=100,
                key="new_fee_input",
            )

        if st.button("Update Fee"):
            update_course_fee(edit_id, new_fee)
            st.success(
                f"Fee updated to {new_fee:.0f} Taka! New dues for this course will use this amount."
            )
            st.rerun()

        st.divider()
        st.subheader("Delete a Course")
        st.caption(
            "Note: deleting a course does not delete students already in it, but new students won't be able to select it."
        )
        courses_df["label"] = (
            "ID "
            + courses_df["id"].astype(str)
            + " - "
            + courses_df["course_name"]
            + " - "
            + courses_df["monthly_fee"].astype(str)
            + " Taka/month"
        )
        course_to_delete = st.selectbox("Select course to delete", courses_df["label"])
        delete_id = int(course_to_delete.split(" ")[1])

        if st.button("Delete This Course"):
            delete_course(delete_id)
            st.success("Course deleted! Switch menu to see the update.")

# ============================================================
# PAGE 14: ADD FACULTY PAYMENT
# ============================================================
elif menu == "Add Faculty Payment":
    st.header("Add Faculty Payment")

    faculty_df = get_all_faculty()

    if faculty_df.empty:
        st.warning("Please add faculty first before recording payments.")
    else:
        faculty_choice = st.selectbox("Select Faculty", faculty_df["name"])
        faculty_id = int(
            faculty_df.loc[faculty_df["name"] == faculty_choice, "id"].iloc[0]
        )

        fp_month = st.selectbox(
            "Month",
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
        )
        fp_amount = st.number_input("Payment Amount (Taka)", min_value=0, step=500)
        fp_status = st.radio("Status", ["Paid", "Pending"], key="fp_status")

        fp_date = ""
        if fp_status == "Paid":
            fp_date = str(
                st.date_input("Payment Date", value=date.today(), key="fp_date")
            )

        if st.button("Save Faculty Payment"):
            add_faculty_payment(faculty_id, fp_month, fp_amount, fp_status, fp_date)
            st.success("Faculty payment record saved successfully!")

# ============================================================
# PAGE 15: FACULTY PAYMENTS LIST
# ============================================================
elif menu == "Faculty Payments":
    st.header("All Faculty Payments")

    fp_df = get_all_faculty_payments()

    if fp_df.empty:
        st.info("No faculty payment records yet.")
    else:
        st.dataframe(fp_df, use_container_width=True)

        total_paid = fp_df[fp_df["status"] == "Paid"]["amount"].sum()
        total_due = fp_df[fp_df["status"] == "Pending"]["amount"].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total Paid to Faculty", f"{total_paid:.0f} Taka")
        col2.metric("Total Due to Faculty", f"{total_due:.0f} Taka")

        st.subheader("Delete a Payment Record")
        fp_df["label"] = (
            "ID "
            + fp_df["id"].astype(str)
            + " - "
            + fp_df["name"]
            + " - "
            + fp_df["month"]
            + " - "
            + fp_df["amount"].astype(str)
            + " Taka"
        )
        fp_to_delete = st.selectbox("Select payment record to delete", fp_df["label"])
        delete_id = int(fp_to_delete.split(" ")[1])

        if st.button("Delete This Payment Record"):
            delete_faculty_payment(delete_id)
            st.success("Payment record deleted! Switch menu to see the update.")

# ============================================================
# PAGE 16: FINANCIAL SUMMARY
# ============================================================
elif menu == "Financial Summary":
    st.header("Financial Summary")

    expected_income = get_expected_monthly_income()
    fees_df = get_all_fees()
    fp_df = get_all_faculty_payments()

    total_collected = (
        fees_df[fees_df["status"] == "Paid"]["amount"].sum() if not fees_df.empty else 0
    )
    total_student_due = (
        fees_df[fees_df["status"] == "Pending"]["amount"].sum()
        if not fees_df.empty
        else 0
    )
    total_faculty_paid = (
        fp_df[fp_df["status"] == "Paid"]["amount"].sum() if not fp_df.empty else 0
    )
    total_faculty_due = (
        fp_df[fp_df["status"] == "Pending"]["amount"].sum() if not fp_df.empty else 0
    )

    st.subheader("Income (from Students)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Monthly Income", f"{expected_income:.0f} Taka")
    col2.metric("Total Collected (Gain)", f"{total_collected:.0f} Taka")
    col3.metric("Total Due (Students)", f"{total_student_due:.0f} Taka")

    st.subheader("Expense (Faculty Payment)")
    col4, col5 = st.columns(2)
    col4.metric("Total Paid to Faculty", f"{total_faculty_paid:.0f} Taka")
    col5.metric("Total Due to Faculty", f"{total_faculty_due:.0f} Taka")

    st.subheader("Net Position")
    net = total_collected - total_faculty_paid
    st.metric("Net (Collected - Paid to Faculty)", f"{net:.0f} Taka")

# ============================================================
# STUDENT PROFILE PAGE
# ============================================================
elif menu == "Student Profile":
    st.header("Student Profile")

    students_df = get_all_students()

    if students_df.empty:
        st.info("No students added yet.")
    else:
        search_query = st.text_input("🔍 Search by name or ID")

        if search_query.strip() == "":
            st.dataframe(
                students_df[["id", "name", "class", "phone"]], use_container_width=True
            )
        else:
            # Filter by name OR id
            filtered = students_df[
                students_df["name"].str.contains(search_query, case=False, na=False)
                | students_df["id"].astype(str).str.contains(search_query, na=False)
            ]

            if filtered.empty:
                st.warning("কোনো Student পাওয়া যায়নি। অন্য নাম বা ID দিয়ে চেষ্টা করুন।")
            else:
                st.success(f"{len(filtered)} জন Student পাওয়া গেছে।")
                st.dataframe(
                    filtered[["id", "name", "class", "phone"]], use_container_width=True
                )

                # If exactly one found, auto-load profile
                if len(filtered) == 1:
                    selected_id = int(filtered.iloc[0]["id"])
                    st.info(f"Student ID {selected_id} এর পুরো profile নিচে দেখানো হচ্ছে।")
                else:
                    # Multiple found, let user pick
                    options = (
                        "ID "
                        + filtered["id"].astype(str)
                        + " - "
                        + filtered["name"]
                        + " ("
                        + filtered["class"]
                        + ")"
                    )
                    selected_option = st.selectbox(
                        "কোন Student এর Profile দেখতে চান?", options
                    )
                    selected_id = int(selected_option.split(" ")[1])

                # Show full profile
                student_info, fee_history, att_history, result_history = (
                    get_student_profile(selected_id)
                )
                row = student_info.iloc[0]

                st.divider()
                st.subheader(f"📋 Profile: {row['name']}")

                col1, col2 = st.columns(2)
                col1.write(f"**ID:** {row['id']}")
                col1.write(f"**Name:** {row['name']}")
                col1.write(f"**Class/Course:** {row['class']}")
                col2.write(f"**Phone:** {row['phone']}")
                col2.write(f"**Guardian Phone:** {row['guardian_phone']}")

                st.divider()

                st.subheader("💰 Fee History")
                if fee_history.empty:
                    st.info("No fee records yet.")
                else:
                    total_paid = fee_history[fee_history["status"] == "Paid"][
                        "amount"
                    ].sum()
                    total_due = fee_history[fee_history["status"] == "Pending"][
                        "amount"
                    ].sum()
                    col3, col4 = st.columns(2)
                    col3.metric("Total Paid", f"{total_paid:.0f} Taka")
                    col4.metric("Total Due", f"{total_due:.0f} Taka")
                    st.dataframe(fee_history, use_container_width=True)

                st.divider()

                st.subheader("📅 Attendance")
                if att_history.empty:
                    st.info("No attendance records yet.")
                else:
                    present = len(att_history[att_history["status"] == "Present"])
                    total = len(att_history)
                    percentage = (present / total * 100) if total > 0 else 0
                    col5, col6, col7 = st.columns(3)
                    col5.metric("Total Classes", total)
                    col6.metric("Present", present)
                    col7.metric("Attendance %", f"{percentage:.1f}%")
                    st.dataframe(att_history, use_container_width=True)

                st.divider()

                st.subheader("📝 Exam Results")
                if result_history.empty:
                    st.info("No results added yet.")
                else:
                    result_history["Percentage"] = (
                        result_history["marks_obtained"]
                        / result_history["total_marks"]
                        * 100
                    ).round(1).astype(str) + "%"
                    st.dataframe(result_history, use_container_width=True)

# ============================================================
# ADD RESULT PAGE
# ============================================================
elif menu == "Add Result":
    st.header("📝 Publish Exam Result")

    courses_df = get_all_courses()
    students_df = get_all_students()

    if students_df.empty:
        st.warning("Please add students first.")
    elif courses_df.empty:
        st.warning("Please add courses first.")
    else:
        # ── Step 1: Teacher fills 4 inputs ──────────────────────
        c1, c2 = st.columns(2)
        with c1:
            selected_course = st.selectbox(
                "Course / Batch", courses_df["course_name"].tolist()
            )
            subject = st.selectbox(
                "Subject",
                [
                    "Physics",
                    "Chemistry",
                    "Higher Math",
                    "General Math",
                    "Biology",
                    "English",
                    "Bangla",
                    "ICT",
                ],
            )
        with c2:
            exam_name = st.text_input("Exam Name (e.g. Weekly Exam, Chapter 3 Test)")
            total_marks = st.number_input(
                "Total Marks", min_value=1.0, value=100.0, step=1.0
            )
        exam_date = str(st.date_input("Exam Date", value=date.today()))

        st.divider()

        # ── Step 2: Table with Student ID, Name, Marks input ────
        course_students = students_df[
            students_df["class"] == selected_course
        ].reset_index(drop=True)

        if course_students.empty:
            st.warning(
                f"No students found in '{selected_course}'. Please add students to this course first."
            )
        else:
            st.subheader(f"Enter Marks for — {selected_course}")

            # Header row
            h1, h2, h3 = st.columns([1, 4, 3])
            h1.markdown("**Student ID**")
            h2.markdown("**Student Name**")
            h3.markdown("**Marks Obtained**")
            st.markdown("---")

            marks_data = {}
            for _, row in course_students.iterrows():
                r1, r2, r3 = st.columns([1, 4, 3])
                r1.write(f"**{int(row['id'])}**")
                r2.write(row["name"])
                marks = r3.number_input(
                    f"marks_{row['id']}",
                    min_value=0.0,
                    max_value=float(total_marks),
                    value=0.0,
                    step=0.5,
                    key=f"marks_{row['id']}",
                    label_visibility="collapsed",
                )
                marks_data[int(row["id"])] = {"name": row["name"], "marks": marks}

            st.markdown("---")

            # ── Step 3: Submit button ────────────────────────────
            if st.button("✅ Submit Result", type="primary", use_container_width=True):
                if exam_name.strip() == "":
                    st.error("Please enter an Exam Name!")
                else:
                    for student_id, info in marks_data.items():
                        add_result(
                            student_id,
                            exam_name,
                            subject,
                            info["marks"],
                            total_marks,
                            exam_date,
                        )
                    st.success(f"✅ Result published for {len(marks_data)} students!")
                    st.balloons()

# ============================================================
# RESULTS PAGE — View Result Report + PDF Download
# ============================================================
elif menu == "Results":
    st.header("📊 Result Report")

    courses_df = get_all_courses()

    if courses_df.empty:
        st.info("No courses yet.")
    else:
        # Filter controls
        c1, c2, c3 = st.columns(3)
        with c1:
            selected_course = st.selectbox(
                "Course / Batch", ["-- Select --"] + courses_df["course_name"].tolist()
            )
        with c2:
            subject_filter = st.selectbox(
                "Subject",
                [
                    "All",
                    "Physics",
                    "Chemistry",
                    "Higher Math",
                    "General Math",
                    "Biology",
                    "English",
                    "Bangla",
                    "ICT",
                ],
            )
        with c3:
            exam_filter = st.text_input("Exam Name (optional filter)")

        if selected_course == "-- Select --":
            st.info("Please select a Course/Batch to view results.")
        else:
            # Fetch results
            conn = get_connection()
            query = """
                SELECT results.id, students.id AS student_id, students.name,
                       results.exam_name, results.subject,
                       results.marks_obtained, results.total_marks, results.exam_date
                FROM results
                JOIN students ON results.student_id = students.id
                WHERE students.class = ?
                ORDER BY students.id ASC
            """
            all_results = pd.read_sql_query(query, conn, params=(selected_course,))
            conn.close()

            # Apply filters
            if subject_filter != "All":
                all_results = all_results[all_results["subject"] == subject_filter]
            if exam_filter.strip():
                all_results = all_results[
                    all_results["exam_name"].str.contains(
                        exam_filter.strip(), case=False, na=False
                    )
                ]

            if all_results.empty:
                st.warning(
                    "No results found. Please publish results from 'Add Result' page."
                )
            else:
                # Calculate Grade & Percentage
                def get_grade(pct):
                    if pct >= 80:
                        return "A+"
                    elif pct >= 70:
                        return "A"
                    elif pct >= 60:
                        return "A-"
                    elif pct >= 50:
                        return "B"
                    elif pct >= 40:
                        return "C"
                    elif pct >= 33:
                        return "D"
                    else:
                        return "F"

                all_results["Percentage"] = (
                    all_results["marks_obtained"] / all_results["total_marks"] * 100
                ).round(1)
                all_results["Grade"] = all_results["Percentage"].apply(get_grade)

                exam_info = all_results.iloc[0]

                # ── Report Header ──────────────────────────────
                st.markdown(f"""
| | |
|---|---|
| **Course/Batch** | {selected_course} |
| **Subject** | {exam_info["subject"]} |
| **Exam** | {exam_info["exam_name"]} |
| **Total Marks** | {int(exam_info["total_marks"])} |
| **Date** | {exam_info["exam_date"]} |
                """)

                st.divider()

                # ── Result Table ───────────────────────────────
                display_df = all_results[
                    ["student_id", "name", "marks_obtained", "Grade", "Percentage"]
                ].copy()
                display_df.columns = ["ID", "Name", "Marks", "Grade", "Percentage (%)"]
                display_df["Percentage (%)"] = (
                    display_df["Percentage (%)"].astype(str) + "%"
                )

                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # ── Summary ────────────────────────────────────
                st.divider()
                s1, s2, s3, s4, s5 = st.columns(5)
                s1.metric("Total Students", len(all_results))
                s2.metric("Highest", f"{all_results['marks_obtained'].max():.0f}")
                s3.metric("Lowest", f"{all_results['marks_obtained'].min():.0f}")
                s4.metric("Average", f"{all_results['marks_obtained'].mean():.1f}")
                pass_count = len(all_results[all_results["Percentage"] >= 33])
                s5.metric("Pass Rate", f"{pass_count / len(all_results) * 100:.0f}%")

                # ── PDF Download ───────────────────────────────
                st.divider()
                results_for_pdf = [
                    {
                        "id": int(r["student_id"]),
                        "name": r["name"],
                        "marks": r["marks_obtained"],
                    }
                    for _, r in all_results.iterrows()
                ]
                try:
                    pdf_bytes = generate_result_pdf(
                        exam_name=exam_info["exam_name"],
                        subject=exam_info["subject"],
                        total_marks=float(exam_info["total_marks"]),
                        course=selected_course,
                        exam_date=str(exam_info["exam_date"]),
                        results_data=results_for_pdf,
                    )
                    st.download_button(
                        label="⬇️ Download Result Sheet (PDF)",
                        data=pdf_bytes,
                        file_name=f"Result_{selected_course}_{exam_info['subject']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(
                        f"PDF error: {e}. Please make sure 'reportlab' is installed."
                    )
