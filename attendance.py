from db import get_connection
from datetime import datetime, date, time,timedelta
import mysql.connector
import logging

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="attendance.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- CALCULATE HOURS ----------------
def calculate_hours(login_time, logout_time):
    today = date.today()

    # If login_time comes as timedelta, convert it
    if isinstance(login_time, timedelta):
        login_time = (datetime.min + login_time).time()

    # If logout_time comes as timedelta, convert it
    if isinstance(logout_time, timedelta):
        logout_time = (datetime.min + logout_time).time()

    start = datetime.combine(today, login_time)
    end = datetime.combine(today, logout_time)

    hours = (end - start).total_seconds() / 3600
    return round(hours, 2)


# ---------------- LOGIN ----------------
def login(emp_id):
    conn = get_connection()
    cur = conn.cursor()
    today = date.today()
    now = datetime.now().time()

    try:
        cur.execute(
            "INSERT INTO attendance (emp_id, att_date, login_time) VALUES (%s,%s,%s)",
            (emp_id, today, now)
        )
        conn.commit()
        print("Login successful")
        logging.info(f"Employee {emp_id} logged in")

    except mysql.connector.Error as err:
        if err.errno == 1062:
            print("Duplicate login not allowed for today")
            logging.warning(f"Duplicate login attempt: {emp_id}")
        else:
            print("Database error")

    conn.close()

# ---------------- LOGOUT ----------------
def logout(emp_id):
    conn = get_connection()
    cur = conn.cursor()
    today = date.today()
    now = datetime.now().time()

    cur.execute(
        "SELECT login_time, logout_time FROM attendance WHERE emp_id=%s AND att_date=%s",
        (emp_id, today)
    )
    row = cur.fetchone()

    if row:
        login_time, logout_time = row

        if logout_time is not None:
            print("Already logged out")
            return

        hours = calculate_hours(login_time, now)
        cur.execute(
            "UPDATE attendance SET logout_time=%s, work_hours=%s WHERE emp_id=%s AND att_date=%s",
            (now, hours, emp_id, today)
        )
        conn.commit()
        print("Logout successful. Hours worked:", hours)
        logging.info(f"Employee {emp_id} logged out")

    else:
        print("No login found for today")

    conn.close()

# ---------------- AUTO LOGOUT (7 PM) ----------------
def auto_logout():
    conn = get_connection()
    cur = conn.cursor()
    today = date.today()
    auto_time = time(19, 0, 0)   # 7:00 PM

    cur.execute(
        "SELECT emp_id, login_time FROM attendance WHERE att_date=%s AND logout_time IS NULL",
        (today,)
    )

    for emp_id, login_time in cur.fetchall():
        hours = calculate_hours(login_time, auto_time)
        cur.execute(
            "UPDATE attendance SET logout_time=%s, work_hours=%s WHERE emp_id=%s AND att_date=%s",
            (auto_time, hours, emp_id, today)
        )
        logging.info(f"Auto logout done for emp {emp_id}")

    conn.commit()
    conn.close()

# ---------------- DAILY REPORT ----------------
def generate_report():
    conn = get_connection()
    cur = conn.cursor()
    today = date.today()

    cur.execute("""
        SELECT e.emp_name, a.login_time, a.logout_time, a.work_hours
        FROM employee e
        JOIN attendance a ON e.emp_id = a.emp_id
        WHERE a.att_date=%s
    """, (today,))

    print("\n--- Daily Attendance Report ---")
    print("Name | Login | Logout | Hours | Status")
    print("-" * 45)

    for name, login, logout, hours in cur.fetchall():
        if hours is None:
            status = "Logged In"
        elif hours < 8:
            status = "Underworked"
        else:
            status = "Present"

        print(f"{name} | {login} | {logout} | {hours} | {status}")

    conn.close()
