import os
from datetime import datetime, timezone

from .transcript import TranscriptResult


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    total = int(round(seconds))
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_transcript(video_id: str, title: str, result: TranscriptResult) -> str:
    """Format a transcript into a readable text string with timestamps."""
    gen_label = " [auto-generated]" if result.is_generated else ""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        f"# {title}",
        f"# Video ID: {video_id}",
        f"# URL: https://www.youtube.com/watch?v={video_id}",
        f"# Language: {result.language} ({result.language_code}){gen_label}",
        f"# Retrieved: {now}",
        "",
    ]

    for snippet in result.snippets:
        ts = format_timestamp(snippet.start)
        lines.append(f"[{ts}] {snippet.text}")

    lines.append("")  # trailing newline
    return "\n".join(lines)


def save_transcript(
    output_dir: str, video_id: str, title: str, result: TranscriptResult
) -> str:
    """Save formatted transcript to a file. Returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{video_id}.txt")
    content = format_transcript(video_id, title, result)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path
