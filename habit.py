import sqlite3
from datetime import datetime, date, timedelta
import time
import threading

conn = sqlite3.connect("habit_final.db", check_same_thread=False)
cursor = conn.cursor()

# CREATE TABLES
cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    reminder_time TEXT,
    created_date DATE
);

CREATE TABLE IF NOT EXISTS habit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER,
    date DATE,
    status INTEGER
);
""")

conn.commit()

# ---------------- AUTH ----------------
def register():
    u = input("Username: ")
    p = input("Password: ")

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        print("✅ Registered successfully")
    except:
        print("❌ Username already exists")

def login():
    u = input("Username: ")
    p = input("Password: ")

    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p))
    user = cursor.fetchone()

    if user:
        print("✅ Login successful")
        return user[0]
    else:
        print("❌ Invalid credentials")
        return None

# ---------------- HABITS ----------------
def add_habit(user_id):
    name = input("Habit name: ")
    reminder = input("Reminder time (HH:MM 24hr): ")

    cursor.execute("""
    INSERT INTO habits (user_id, name, reminder_time, created_date)
    VALUES (?, ?, ?, ?)
    """, (user_id, name, reminder, date.today()))

    conn.commit()
    print("✅ Habit added with reminder")

def mark_done():
    habit_id = int(input("Habit ID: "))

    cursor.execute("""
    INSERT INTO habit_log (habit_id, date, status)
    VALUES (?, ?, 1)
    """, (habit_id, date.today()))

    conn.commit()
    print("🔥 Marked done!")

# ---------------- STREAK ----------------
def current_streak(habit_id):
    streak = 0
    today = date.today()

    while True:
        cursor.execute("""
        SELECT status FROM habit_log 
        WHERE habit_id=? AND date=?
        """, (habit_id, today))

        result = cursor.fetchone()

        if result:
            streak += 1
            today -= timedelta(days=1)
        else:
            break

    return streak

# ---------------- DASHBOARD ----------------
def dashboard(user_id):
    cursor.execute("SELECT * FROM habits WHERE user_id=?", (user_id,))
    habits = cursor.fetchall()

    for h in habits:
        streak = current_streak(h[0])

        print(f"\n📌 ID: {h[0]} | {h[2]}")
        print(f"🔥 Streak: {streak}")
        print(f"⏰ Reminder: {h[3]}")

# ---------------- 🔔 REMINDER SYSTEM ----------------
def reminder_system(user_id):
    while True:
        now = datetime.now().strftime("%H:%M")

        cursor.execute("""
        SELECT name FROM habits 
        WHERE user_id=? AND reminder_time=?
        """, (user_id, now))

        reminders = cursor.fetchall()

        for r in reminders:
            print(f"\n🔔 Reminder: Time to do '{r[0]}'!")

        time.sleep(60)  # check every minute

# ---------------- MAIN ----------------
def main():
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        ch = input("Choose: ")

        if ch == "1":
            register()

        elif ch == "2":
            user_id = login()

            if user_id:
                # start reminder thread
                t = threading.Thread(target=reminder_system, args=(user_id,), daemon=True)
                t.start()

                while True:
                    print("\n1. Add Habit\n2. Mark Done\n3. Dashboard\n4. Logout")
                    c = input("Choose: ")

                    if c == "1":
                        add_habit(user_id)
                    elif c == "2":
                        mark_done()
                    elif c == "3":
                        dashboard(user_id)
                    elif c == "4":
                        break

        elif ch == "3":
            print("Goodbye 👋")
            break

if __name__ == "__main__":
    main()