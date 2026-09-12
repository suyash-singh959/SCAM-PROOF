from data_layer.supabase_storage import (
    init_supabase,
    upload_scanned_audio
)

try:
    init_supabase()

    uploaded_file = upload_scanned_audio(
        "file_example_WAV_1MG.wav"
    )

    print("Audio uploaded successfully!")
    print("Uploaded path:", uploaded_file)

except Exception as e:
    print(f"Upload failed: {e}")