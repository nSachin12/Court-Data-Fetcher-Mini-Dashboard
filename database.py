import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("court_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_type TEXT,
        case_number TEXT,
        filing_year TEXT,
        response TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def log_query(case_type, case_number, filing_year, response):
    conn = sqlite3.connect("court_data.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO queries (case_type, case_number, filing_year, response, timestamp) VALUES (?, ?, ?, ?, ?)",
              (case_type, case_number, filing_year, response, timestamp))
    conn.commit()
    conn.close()