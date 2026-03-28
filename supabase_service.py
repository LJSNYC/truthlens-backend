import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client: Optional[Client] = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _client = create_client(url, key)
    return _client


def log_scan(user_id: str, verdict: str, confidence: float, reason: str, file_type: str):
    client = _get_client()
    client.table("scans").insert({
        "user_id": user_id,
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "file_type": file_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
