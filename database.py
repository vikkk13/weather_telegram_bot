import sqlite3

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            default_city TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_default_city(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT default_city FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row[0] if row else None


def save_default_city(user_id, city):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # ВАЖНО: параметры должны быть переданы
    cur.execute("""
        INSERT INTO users (user_id, default_city)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET default_city = excluded.default_city
    """, (user_id, city))

    conn.commit()
    conn.close()


def add_city(user_id, city):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("INSERT INTO cities (user_id, city) VALUES (?, ?)", (user_id, city))

    conn.commit()
    conn.close()


def get_cities(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT city FROM cities WHERE user_id=?", (user_id,))
    rows = cur.fetchall()

    conn.close()
    return [r[0] for r in rows]


def set_sub_time(user_id, time_str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO subscriptions (user_id, time)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET time = excluded.time
    """, (user_id, time_str))
    conn.commit()
    conn.close()


def get_sub_time(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT time FROM subscriptions WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def delete_sub(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM subscriptions WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def get_all_subscriptions():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT user_id, time FROM subscriptions")
    rows = cur.fetchall()
    conn.close()
    return rows

