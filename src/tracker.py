import json
import os
from datetime import datetime, timezone


def load_tracking(tracking_file: str) -> dict:
    """Load tracking data from a JSON file. Returns empty structure if missing."""
    if os.path.exists(tracking_file):
        with open(tracking_file, "r") as f:
            return json.load(f)
    return {
        "playlist_id": None,
        "playlist_title": None,
        "last_updated": None,
        "videos": {},
    }


def is_processed(tracking_data: dict, video_id: str) -> bool:
    """Check if a video was already successfully processed."""
    entry = tracking_data.get("videos", {}).get(video_id)
    return entry is not None and entry.get("status") == "success"


def mark_processed(
    tracking_data: dict,
    video_id: str,
    title: str,
    transcript_file: str | None,
    language: str | None,
    is_generated: bool | None,
    status: str,
    error: str | None = None,
) -> None:
    """Record a video's processing result in the tracking data."""
    now = datetime.now(timezone.utc).isoformat()
    tracking_data["last_updated"] = now
    tracking_data.setdefault("videos", {})[video_id] = {
        "video_id": video_id,
        "title": title,
        "processed_date": now,
        "transcript_file": transcript_file,
        "language": language,
        "is_generated": is_generated,
        "status": status,
        "error": error,
    }


def save_tracking(tracking_data: dict, tracking_file: str) -> None:
    """Atomically write tracking data to disk."""
    tmp_file = tracking_file + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(tracking_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp_file, tracking_file)
