import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("database/robots.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS robots (
            domain TEXT PRIMARY KEY,
            content TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_robots_from_db(domain):
    conn = sqlite3.connect("database/robots.db")
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM robots WHERE domain = ?", (domain,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def store_robots_in_db(domain, content):
    conn = sqlite3.connect("database/robots.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO robots (domain, content, last_updated)
        VALUES (?, ?, ?)
    """, (domain, content, datetime.now()))
    conn.commit()
    conn.close()
