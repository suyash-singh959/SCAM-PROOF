from data_layer.scan_handler import process_scan
from data_layer.firebase_alerts import init_firebase

init_firebase(
    "firebase-service-account.json",
    "https://scam-ai-14d6b-default-rtdb.firebaseio.com/"
)

try:
    result = process_scan(
        caller_id="test_caller_001",
        scam_score=92.4,
        transcript="Your bank account has been compromised.",
        status="SCAM",
        audio_path="file_example_WAV_1MG.wav"
    )

    print("Full scan processed successfully!")
    print("Result:", result)

except Exception as e:
    print(f"Scan failed: {e}")