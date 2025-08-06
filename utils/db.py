import sqlite3
import json

DB_PATH = "meeting_minutes.db"

def init_db():
    conn = sqlite3.connect("meeting_minutes.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS meeting_minutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_datetime TEXT,
            summary TEXT,
            action_items TEXT,
            decisions TEXT,
            dates TEXT,
            diarized_transcript TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_minutes(meeting_datetime, summary, action_items, decisions, dates, diarized_transcript=""):
    conn = sqlite3.connect("meeting_minutes.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO meeting_minutes 
        (meeting_datetime, summary, action_items, decisions, dates, diarized_transcript)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        meeting_datetime,
        summary,
        "\n".join(action_items),
        "\n".join(decisions),
        json.dumps(dates),
        diarized_transcript
    ))

    conn.commit()
    conn.close()


def get_all_meetings():
    conn = sqlite3.connect("../meeting_minutes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM meeting_minutes")
    rows = c.fetchall()
    conn.close()
    return rows
