import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

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
        ("Class 6", 1000), ("Class 7", 1000), ("Class 8", 1200),
        ("Class 9", 1600), ("Class 10", 1600),
        ("HSC 1st Year", 3000), ("HSC 2nd Year", 3000),
        ("Spoken English Course", 1500)
    ]
    conn2 = get_connection()
    cursor2 = conn2.cursor()
    for name, fee in default_courses:
        cursor2.execute(
            "INSERT OR IGNORE INTO courses (course_name, monthly_fee) VALUES (?, ?)",
            (name, fee)
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
        (name, student_class, phone, guardian_phone)
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
        (student_id, month, amount, status, payment_date)
    )
    conn.commit()
    conn.close()

def get_all_fees():
    conn = get_connection()
    query = """
        SELECT fees.id, students.name, students.class, fees.month,
               fees.amount, fees.status, fees.payment_date
        FROM fees
        JOIN students ON fees.student_id = students.id
        ORDER BY fees.id DESC
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

# ============================================================
# FACULTY FUNCTIONS
# ============================================================
def add_faculty(name, subject, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty (name, subject, phone) VALUES (?, ?, ?)",
        (name, subject, phone)
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
        (class_name, day, time_slot, subject, faculty_id)
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
        (student_id, att_date, status)
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
        (student_id, exam_name, subject, marks_obtained, total_marks, exam_date)
    )
    conn.commit()
    conn.close()

def get_results_by_student(student_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM results WHERE student_id = ? ORDER BY exam_date DESC",
        conn, params=(student_id,)
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
        conn, params=(student_id,)
    )

    # Attendance
    attendance = pd.read_sql_query(
        "SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC",
        conn, params=(student_id,)
    )

    # Results
    results = pd.read_sql_query(
        "SELECT exam_name, subject, marks_obtained, total_marks, exam_date FROM results WHERE student_id = ? ORDER BY exam_date DESC",
        conn, params=(student_id,)
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
        (course_name, monthly_fee)
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

# ============================================================
# FACULTY PAYMENT FUNCTIONS
# ============================================================
def add_faculty_payment(faculty_id, month, amount, status, payment_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO faculty_payment (faculty_id, month, amount, status, payment_date) VALUES (?, ?, ?, ?, ?)",
        (faculty_id, month, amount, status, payment_date)
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

st.caption("Subjects Taught: Physics • Chemistry • Higher Math • General Math • Biology • English • Bangla • ICT")

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard",
     "Add Student", "Student List", "Student Profile",
     "Add Fee Record", "Fee Records", "Pending Fees",
     "Add Result", "Results",
     "Add Faculty", "Faculty List", "Add Faculty Payment", "Faculty Payments",
     "Add Routine", "Routine",
     "Take Attendance", "Attendance Summary",
     "Add Course", "Course List", "Financial Summary"]
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
    total_collected = fees_df[fees_df["status"] == "Paid"]["amount"].sum() if not fees_df.empty else 0
    total_pending = fees_df[fees_df["status"] == "Pending"]["amount"].sum() if not fees_df.empty else 0
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
        student_class = st.selectbox("Class / Course", courses_df["course_name"].tolist())
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
            "ID " + students_df["id"].astype(str) + " - " + students_df["name"]
            + " - " + students_df["class"] + " - " + students_df["phone"]
        )
        student_to_delete = st.selectbox("Select student to delete", students_df["label"])
        delete_id = int(student_to_delete.split(" ")[1])

        if st.button("Delete This Student"):
            delete_student(delete_id)
            st.success("Student deleted! Switch menu to see the update.")

# ============================================================
# PAGE 3: ADD FEE RECORD
# ============================================================
elif menu == "Add Fee Record":
    st.header("Add Fee Record")

    students_df = get_all_students()

    if students_df.empty:
        st.warning("Please add students first before recording fees.")
    else:
        student_options = students_df["name"] + " (" + students_df["class"] + ")"
        selected = st.selectbox("Select Student", student_options)
        selected_index = student_options[student_options == selected].index[0]
        student_id = int(students_df.loc[selected_index, "id"])

        month = st.selectbox(
            "Month",
            ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
        )
        amount = st.number_input("Fee Amount (Taka)", min_value=0, step=100)
        status = st.radio("Status", ["Paid", "Pending"])

        payment_date = ""
        if status == "Paid":
            payment_date = str(st.date_input("Payment Date", value=date.today()))

        if st.button("Save Fee Record"):
            add_fee_record(student_id, month, amount, status, payment_date)
            st.success("Fee record saved successfully!")

# ============================================================
# PAGE 4: ALL FEE RECORDS
# ============================================================
elif menu == "Fee Records":
    st.header("All Fee Records")

    fees_df = get_all_fees()

    if fees_df.empty:
        st.info("No fee records yet.")
    else:
        st.dataframe(fees_df, use_container_width=True)

        total_paid = fees_df[fees_df["status"] == "Paid"]["amount"].sum()
        total_pending = fees_df[fees_df["status"] == "Pending"]["amount"].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total Collected", f"{total_paid:.0f} Taka")
        col2.metric("Total Pending", f"{total_pending:.0f} Taka")

        st.subheader("Delete a Fee Record")
        # Build a readable label for each record so it's easy to pick the right one
        fees_df["label"] = (
            "ID " + fees_df["id"].astype(str) + " - " + fees_df["name"]
            + " - " + fees_df["month"] + " - " + fees_df["amount"].astype(str) + " Taka"
        )
        record_to_delete = st.selectbox("Select record to delete", fees_df["label"])
        delete_id = int(record_to_delete.split(" ")[1])

        if st.button("Delete This Record"):
            delete_fee_record(delete_id)
            st.success("Record deleted! Please refresh the page or switch menu to see the update.")

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
        ["Physics", "Chemistry", "Higher Math", "General Math",
         "Biology", "English", "Bangla", "ICT"]
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
            "ID " + faculty_df["id"].astype(str) + " - " + faculty_df["name"]
            + " - " + faculty_df["subject"]
        )
        faculty_to_delete = st.selectbox("Select faculty to delete", faculty_df["label"])
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
        ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    r_time = st.text_input("Time (example: 4:00 PM - 5:30 PM)")
    r_subject = st.selectbox(
        "Subject",
        ["Physics", "Chemistry", "Higher Math", "General Math",
         "Biology", "English", "Bangla", "ICT"]
    )

    faculty_id = None
    if not faculty_df.empty:
        faculty_choice = st.selectbox("Assign Teacher", faculty_df["name"])
        faculty_id = int(faculty_df.loc[faculty_df["name"] == faculty_choice, "id"].iloc[0])
    else:
        st.warning("No faculty added yet. You can still save the routine without a teacher assigned.")

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
        # Let the user filter by class so it's easy to see one batch's routine
        class_filter = st.selectbox(
            "Filter by Class",
            ["All"] + sorted(routine_df["class_name"].unique().tolist())
        )
        if class_filter != "All":
            display_df = routine_df[routine_df["class_name"] == class_filter]
        else:
            display_df = routine_df

        st.dataframe(display_df, use_container_width=True)

        st.subheader("Delete a Routine Entry")
        routine_df["label"] = (
            "ID " + routine_df["id"].astype(str) + " - " + routine_df["class_name"]
            + " - " + routine_df["day"] + " - " + routine_df["subject"]
        )
        routine_to_delete = st.selectbox("Select routine entry to delete", routine_df["label"])
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
            "Select Class",
            ["All"] + sorted(students_df["class"].unique().tolist())
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
                horizontal=True
            )
            attendance_choices[row["id"]] = choice

        if st.button("Save Attendance"):
            for student_id, status in attendance_choices.items():
                mark_attendance(student_id, str(att_date), status)
            st.success(f"Attendance saved for {len(attendance_choices)} students on {att_date}.")

# ============================================================
# PAGE 11: ATTENDANCE SUMMARY
# ============================================================
elif menu == "Attendance Summary":
    st.header("Attendance Summary")

    tab1, tab2 = st.tabs(["By Date", "Overall Summary"])

    with tab1:
        check_date = st.date_input("Check attendance for date", value=date.today(), key="check_date")
        day_df = get_attendance_by_date(str(check_date))

        if day_df.empty:
            st.info("No attendance recorded for this date.")
        else:
            st.dataframe(day_df, use_container_width=True)

    with tab2:
        summary_df = get_attendance_summary()

        if summary_df.empty:
            st.info("No attendance records yet.")
        else:
            st.dataframe(summary_df, use_container_width=True)

# ============================================================
# PAGE 12: ADD COURSE (Create a new batch/course without coding)
# ============================================================
elif menu == "Add Course":
    st.header("Add New Course / Batch")
    st.write("Use this page to create a new course or batch — for example 'SSC FRB Batch 2' or 'HSC FRB Batch 1'. No coding needed, it will appear everywhere automatically.")

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
                st.error("A course with this name already exists. Please choose a different name.")

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

        st.subheader("Delete a Course")
        st.caption("Note: deleting a course does not delete students already in it, but new students won't be able to select it.")
        courses_df["label"] = (
            "ID " + courses_df["id"].astype(str) + " - " + courses_df["course_name"]
            + " - " + courses_df["monthly_fee"].astype(str) + " Taka/month"
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
        faculty_id = int(faculty_df.loc[faculty_df["name"] == faculty_choice, "id"].iloc[0])

        fp_month = st.selectbox(
            "Month",
            ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
        )
        fp_amount = st.number_input("Payment Amount (Taka)", min_value=0, step=500)
        fp_status = st.radio("Status", ["Paid", "Pending"])

        fp_date = ""
        if fp_status == "Paid":
            fp_date = str(st.date_input("Payment Date", value=date.today(), key="fp_date"))

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
            "ID " + fp_df["id"].astype(str) + " - " + fp_df["name"]
            + " - " + fp_df["month"] + " - " + fp_df["amount"].astype(str) + " Taka"
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

    total_collected = fees_df[fees_df["status"] == "Paid"]["amount"].sum() if not fees_df.empty else 0
    total_student_due = fees_df[fees_df["status"] == "Pending"]["amount"].sum() if not fees_df.empty else 0
    total_faculty_paid = fp_df[fp_df["status"] == "Paid"]["amount"].sum() if not fp_df.empty else 0
    total_faculty_due = fp_df[fp_df["status"] == "Pending"]["amount"].sum() if not fp_df.empty else 0

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
                students_df[["id", "name", "class", "phone"]],
                use_container_width=True
            )
        else:
            # Filter by name OR id
            filtered = students_df[
                students_df["name"].str.contains(search_query, case=False, na=False) |
                students_df["id"].astype(str).str.contains(search_query, na=False)
            ]

            if filtered.empty:
                st.warning("কোনো Student পাওয়া যায়নি। অন্য নাম বা ID দিয়ে চেষ্টা করুন।")
            else:
                st.success(f"{len(filtered)} জন Student পাওয়া গেছে।")
                st.dataframe(
                    filtered[["id", "name", "class", "phone"]],
                    use_container_width=True
                )

                # If exactly one found, auto-load profile
                if len(filtered) == 1:
                    selected_id = int(filtered.iloc[0]["id"])
                    st.info(f"Student ID {selected_id} এর পুরো profile নিচে দেখানো হচ্ছে।")
                else:
                    # Multiple found, let user pick
                    options = "ID " + filtered["id"].astype(str) + " - " + filtered["name"] + " (" + filtered["class"] + ")"
                    selected_option = st.selectbox("কোন Student এর Profile দেখতে চান?", options)
                    selected_id = int(selected_option.split(" ")[1])

                # Show full profile
                student_info, fee_history, att_history, result_history = get_student_profile(selected_id)
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
                    total_paid = fee_history[fee_history["status"] == "Paid"]["amount"].sum()
                    total_due = fee_history[fee_history["status"] == "Pending"]["amount"].sum()
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
                    result_history["Percentage"] = (result_history["marks_obtained"] / result_history["total_marks"] * 100).round(1).astype(str) + "%"
                    st.dataframe(result_history, use_container_width=True)

# ============================================================
# ADD RESULT PAGE
# ============================================================
elif menu == "Add Result":
    st.header("Add Exam Result")

    students_df = get_all_students()

    if students_df.empty:
        st.warning("Please add students first.")
    else:
        # Show student list with ID so teacher knows which ID to use
        st.write("**Student List (for reference):**")
        st.dataframe(students_df[["id", "name", "class"]], use_container_width=True)

        st.divider()

        student_options = "ID " + students_df["id"].astype(str) + " - " + students_df["name"] + " (" + students_df["class"] + ")"
        selected = st.selectbox("Select Student", student_options)
        student_id = int(selected.split(" ")[1])

        exam_name = st.text_input("Exam Name (e.g. Monthly Test, Final Exam)")
        subject = st.selectbox("Subject", ["Physics", "Chemistry", "Higher Math", "General Math", "Biology", "English", "Bangla", "ICT"])
        marks_obtained = st.number_input("Marks Obtained", min_value=0.0, step=0.5)
        total_marks = st.number_input("Total Marks", min_value=1.0, value=100.0, step=0.5)
        exam_date = str(st.date_input("Exam Date", value=date.today()))

        if st.button("Save Result"):
            if exam_name.strip() == "":
                st.error("Exam name is required!")
            else:
                add_result(student_id, exam_name, subject, marks_obtained, total_marks, exam_date)
                percentage = (marks_obtained / total_marks) * 100
                st.success(f"Result saved! Score: {marks_obtained}/{total_marks} ({percentage:.1f}%)")

# ============================================================
# ALL RESULTS PAGE
# ============================================================
elif menu == "Results":
    st.header("All Exam Results")

    students_df = get_all_students()

    if students_df.empty:
        st.info("No students yet.")
    else:
        student_options = "ID " + students_df["id"].astype(str) + " - " + students_df["name"] + " (" + students_df["class"] + ")"
        selected = st.selectbox("Select Student to view results", student_options)
        student_id = int(selected.split(" ")[1])

        results_df = get_results_by_student(student_id)

        if results_df.empty:
            st.info("No results found for this student.")
        else:
            results_df["Percentage"] = (results_df["marks_obtained"] / results_df["total_marks"] * 100).round(1).astype(str) + "%"
            st.dataframe(results_df, use_container_width=True)

            st.subheader("Delete a Result")
            results_df["label"] = "ID " + results_df["id"].astype(str) + " - " + results_df["exam_name"] + " - " + results_df["subject"]
            result_to_delete = st.selectbox("Select result to delete", results_df["label"])
            delete_id = int(result_to_delete.split(" ")[1])

            if st.button("Delete This Result"):
                delete_result(delete_id)
                st.success("Result deleted! Switch menu to see update.")
