import sqlite3
import os

DB_FILE = "newsbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feeds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 url TEXT UNIQUE,
                 region TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blog
                 (id INTEGER PRIMARY KEY,
                 blog_id TEXT)''')
    conn.commit()
    conn.close()

def add_feed(url, region):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO feeds (url, region) VALUES (?, ?)", (url, region))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_feeds():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT url, region FROM feeds")
    feeds = c.fetchall()
    conn.close()
    return feeds

def set_blog(blog_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM blog")
    c.execute("INSERT INTO blog (id, blog_id) VALUES (1, ?)", (blog_id,))
    conn.commit()
    conn.close()

def get_blog():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT blog_id FROM blog WHERE id=1")
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize database on first run
if not os.path.exists(DB_FILE):
    init_db()