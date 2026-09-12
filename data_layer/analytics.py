from data_layer.sqlite_db import get_connection
import sqlite3
SCAM_THRESHOLD = 85


def get_total_scans():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM scan_logs
        """)

        return cursor.fetchone()[0]

    except Exception as e:
        raise RuntimeError(
            f"Failed to get total scans: {e}"
        )

    finally:
        connection.close()


def get_high_risk_count():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM scan_logs
            WHERE scam_score >= ?
        """, (SCAM_THRESHOLD,))

        return cursor.fetchone()[0]

    except Exception as e:
        raise RuntimeError(
            f"Failed to get high-risk scan count: {e}"
        )

    finally:
        connection.close()


def get_average_scam_score():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT AVG(scam_score)
            FROM scan_logs
        """)

        result = cursor.fetchone()[0]

        return result if result is not None else 0

    except Exception as e:
        raise RuntimeError(
            f"Failed to calculate average scam score: {e}"
        )

    finally:
        connection.close()

def get_scan_statistics():
    return {
        "total_scans": get_total_scans(),
        "high_risk_scans": get_high_risk_count(),
        "average_scam_score": round(get_average_scam_score(), 2)
    }

def get_recent_scan_history(limit=10):
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive integer")

    connection = get_connection()

    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, timestamp, caller_id, scam_score, transcript, status
            FROM scan_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(
            f"Failed to get recent scan history: {e}"
        )

    finally:
        connection.close()

def get_risk_distribution():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                SUM(CASE WHEN scam_score < 50 THEN 1 ELSE 0 END),
                SUM(CASE WHEN scam_score >= 50 AND scam_score < 85 THEN 1 ELSE 0 END),
                SUM(CASE WHEN scam_score >= 85 THEN 1 ELSE 0 END)
            FROM scan_logs
        """)

        low, medium, high = cursor.fetchone()

        return {
            "low_risk": low or 0,
            "medium_risk": medium or 0,
            "high_risk": high or 0
        }

    except Exception as e:
        raise RuntimeError(
            f"Failed to get risk distribution: {e}"
        )

    finally:
        connection.close()

def get_dashboard_data():
    return {
        "statistics": get_scan_statistics(),
        "risk_distribution": get_risk_distribution(),
        "recent_scans": get_recent_scan_history(10)
    }