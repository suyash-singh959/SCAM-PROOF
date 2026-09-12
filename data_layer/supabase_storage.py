from uuid import uuid4
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client | None = None

BUCKET_NAME = "scanned-audio"


def init_supabase():
    global _supabase

    if _supabase is not None:
        return

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY "
            "must be set in .env"
        )

    try:
        _supabase = create_client(url, key)

    except Exception as e:
        raise RuntimeError(
            f"Supabase initialization failed: {e}"
        )


def upload_scanned_audio(file_path, destination_path=None):

    if _supabase is None:
        raise RuntimeError(
            "Supabase is not initialized. "
            "Call init_supabase() first."
        )

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Audio file not found: {file_path}"
        )
    if destination_path is None:
        filename = os.path.basename(file_path)
        destination_path = f"{uuid4().hex}_{filename}"

    try:
        with open(file_path, "rb") as audio_file:
            _supabase.storage.from_(BUCKET_NAME).upload(
                destination_path,
                audio_file,
                {"upsert": "true"}
            )

        return destination_path

    except Exception as e:
        raise RuntimeError(
            f"Failed to upload scanned audio: {e}"
        )