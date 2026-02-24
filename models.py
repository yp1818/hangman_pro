import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # Users table - completions column add kiya hai
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        total_score INTEGER DEFAULT 0,
        coins INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        completions INTEGER DEFAULT 0
    )
    """)
    # Login Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        login_time TEXT,
        ip_address TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    # Applications table for 'Work with Us'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, reason TEXT, submitted_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def record_login(user_id, username, ip_address):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO login_logs (user_id, username, login_time, ip_address) VALUES (?, ?, ?, ?)", (user_id, username, now, ip_address))
    conn.commit()
    conn.close()

def save_application(name, email, reason):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO applications (name, email, reason, submitted_at) VALUES (?, ?, ?, ?)", (name, email, reason, now))
    conn.commit()
    conn.close()

def restart_user_game(user_id):
    """User ki progress reset karke completions badhane ke liye"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET level = 1, total_score = 0, completions = completions + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

def update_score_and_level(user_id, score, win):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # Coins calculation based on score
    coins_earned = score // 5 
    if win:
        # Jeetne par Level +1 aur Score/Coins update
        cursor.execute("UPDATE users SET total_score = total_score + ?, coins = coins + ?, level = level + 1 WHERE id=?", (score, coins_earned, user_id))
    else:
        # Harne par ya skip par score handle karna
        cursor.execute("UPDATE users SET total_score = total_score + ?, coins = coins + ? WHERE id=?", (score, coins_earned, user_id))
    conn.commit()
    conn.close()

def has_applied(email):
    """Check if the user has already submitted an application"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM applications WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_user_stats(user_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # Dashboard stats fetch logic (Completions bhi fetch ho rahe hain)
    cursor.execute("SELECT total_score, coins, level, completions FROM users WHERE id=?", (user_id,))
    stats = cursor.fetchone()
    conn.close()
    return stats