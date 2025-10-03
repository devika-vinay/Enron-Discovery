import hashlib, json, time, os
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("logs/coc.jsonl")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def now_utc_iso():
    return datetime.now(timezone.utc).isoformat()

def log_coc(event_type: str, **details):
    record = {"ts_utc": now_utc_iso(), "event_type": event_type, **details}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
