from data_layer.sqlite_db import insert_log
from data_layer.firebase_alerts import push_emergency_alert
from data_layer.supabase_storage import (
    init_supabase,
    upload_scanned_audio
)

SCAM_THRESHOLD = 85


def process_scan(
    caller_id,
    scam_score,
    transcript,
    status,
    audio_path=None
):
    result = {
    "log_id": None,
    "alert_id": None,
    "firebase_error": None,
    "audio_path": None,
    "audio_upload_error": None
    }

    # 1. Save scan to SQLite
    result["log_id"] = insert_log(
        caller_id,
        scam_score,
        transcript,
        status
    )

    # 2. Send emergency alert if score is high
    if scam_score >= SCAM_THRESHOLD:
        try:
            result["alert_id"] = push_emergency_alert(
                caller_id,
                scam_score
            )
        except Exception as e:
            result["firebase_error"] = str(e)

    # 3. Upload audio to Supabase if an audio file was provided
    if audio_path:
        try:
            init_supabase()

            result["audio_path"] = upload_scanned_audio(
                audio_path
            )

        except Exception as e:
            result["audio_upload_error"] = str(e)

    return result