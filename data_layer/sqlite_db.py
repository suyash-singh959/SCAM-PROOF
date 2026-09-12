import time
import sqlite3
from datetime import datetime, timezone

DB_NAME = "auraguard.db"
def get_connection():
    while True:
        try:
            connection = sqlite3.connect(DB_NAME)
            return connection

        except sqlite3.Error as e:
            #print(f"Database connection failed: {e}")
            #print("Retrying database connection...")
            time.sleep(1)

def init_db():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                caller_id TEXT NOT NULL,
                scam_score REAL NOT NULL,
                transcript TEXT,
                status TEXT NOT NULL
            )
        """)
        connection.commit()

    except sqlite3.Error as e:
        connection.rollback()
        raise RuntimeError(f"Database initialization failed: {e}")

    finally:
        connection.close()


def insert_log(caller_id, scam_score, transcript, status):
    if not caller_id:
        raise ValueError("caller_id cannot be empty")
    try:
        scam_score = float(scam_score)
    except (TypeError, ValueError):
        raise ValueError("scam_score must be a number")
    if not 0 <= scam_score <= 100:
        raise ValueError("scam_score must be between 0 and 100")
    if not status:
        raise ValueError("status cannot be empty")
    timestamp = datetime.now(timezone.utc).isoformat()
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO scan_logs
            (timestamp, caller_id, scam_score, transcript, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            timestamp,
            caller_id,
            scam_score,
            transcript,
            status
        ))
        connection.commit()
        return cursor.lastrowid

    except sqlite3.Error as e:
        connection.rollback()
        raise RuntimeError(f"Failed to insert scan log: {e}")

    finally:
        connection.close()


def get_recent_logs(limit=10):

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive integer")

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, timestamp, caller_id, scam_score, transcript, status
            FROM scan_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to retrieve scan logs: {e}")
    finally:
        connection.close()

 
def clear_logs():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM scan_logs")
        connection.commit()

    except sqlite3.Error as e:
        connection.rollback()
        raise RuntimeError(f"Failed to clear scan logs: {e}")

    finally:
        connection.close() 