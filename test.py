import sqlite3

conn = sqlite3.connect("meeting_minutes.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(meeting_minutes)")
for row in cursor.fetchall():
    print(row)
conn.close()
