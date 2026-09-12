from data_layer.firebase_alerts import (
    init_firebase,
    push_emergency_alert
)

init_firebase(
    "firebase-service-account.json",
    "https://scam-ai-14d6b-default-rtdb.firebaseio.com/"
)

alert_id = push_emergency_alert(
    "CALL_1024",
    94.7
)

print("Alert pushed successfully!")
print("Alert ID:", alert_id)