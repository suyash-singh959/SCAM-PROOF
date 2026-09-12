import firebase_admin
from firebase_admin import credentials, db


_firebase_initialized = False


def init_firebase(credentials_path, database_url):
    global _firebase_initialized

    if _firebase_initialized:
        return

    try:
        cred = credentials.Certificate(credentials_path)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": database_url
            }
        )

        _firebase_initialized = True

    except Exception as e:
        raise RuntimeError(
            f"Firebase initialization failed: {e}"
        )


def push_emergency_alert(caller_id, score):
    if not _firebase_initialized:
        raise RuntimeError(
            "Firebase is not initialized. "
            "Call init_firebase() first."
        )

    if not caller_id:
        raise ValueError("caller_id cannot be empty")

    try:
        score = float(score)
    except (TypeError, ValueError):
        raise ValueError("score must be a number")

    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")

    alert = {
        "caller_id": caller_id,
        "scam_score": score,
        "status": "EMERGENCY"
    }

    try:
        reference = db.reference("emergency_alerts")
        result = reference.push(alert)

        return result.key

    except Exception as e:
        raise RuntimeError(
            f"Failed to push emergency alert: {e}"
        )