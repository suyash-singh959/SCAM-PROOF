from data_layer.sqlite_db import init_db, insert_log
from data_layer.firebase_alerts import (
    init_firebase,
    push_emergency_alert
)

DATABASE_URL = "https://scam-ai-14d6b-default-rtdb.firebaseio.com/"
CREDENTIALS_FILE = "firebase-service-account.json"

SCAM_THRESHOLD = 85


init_db()

init_firebase(
    CREDENTIALS_FILE,
    DATABASE_URL
)

caller_id = "CALL_2048"
scam_score = 94.7
transcript = "This is a test emergency call."
status = "BLOCKED"

log_id = insert_log(
    caller_id,
    scam_score,
    transcript,
    status
)

print("SQLite log created:", log_id)

if scam_score >= SCAM_THRESHOLD:
    alert_id = push_emergency_alert(
        caller_id,
        scam_score
    )

    print("Firebase alert created:", alert_id)
else:
    print("No emergency alert required.")