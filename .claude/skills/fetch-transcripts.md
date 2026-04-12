---
name: fetch-transcripts
description: Download and process transcripts from a YouTube playlist, skipping already-processed videos
---

# Fetch YouTube Transcripts

Download transcripts for all videos in a YouTube playlist. Already-processed videos are tracked and skipped automatically on subsequent runs.

## Instructions

When the user provides a YouTube playlist URL or ID, run the transcript fetcher:

```bash
cd /home/user/youtube && python -m src.main "<PLAYLIST_URL>"
```

Replace `<PLAYLIST_URL>` with the actual URL or playlist ID provided by the user.

## Options

- `--output-dir <dir>` - Directory for transcript files (default: `transcripts/`)
- `--tracking-file <file>` - Path to tracking JSON file (default: `processed_videos.json`)
- `--languages en es fr` - Language codes in priority order (default: en, en-US, en-GB)

## Examples

```bash
# Process a playlist
cd /home/user/youtube && python -m src.main "https://www.youtube.com/playlist?list=PLxxxxxxx"

# Specify output directory and preferred languages
cd /home/user/youtube && python -m src.main "https://www.youtube.com/playlist?list=PLxxxxxxx" --output-dir my_transcripts --languages fr en

# Use a bare playlist ID
cd /home/user/youtube && python -m src.main "PLxxxxxxx"
```

## Behavior

- Fetches playlist metadata via yt-dlp (no API key needed)
- Downloads transcripts via youtube-transcript-api (no API key needed)
- Prefers manual English transcripts, falls back to auto-generated, then any available language
- Each transcript is saved as `transcripts/<video_id>.txt` with timestamps
- Progress is tracked in `processed_videos.json` -- already-processed videos are skipped
- Failed videos are recorded but retried on subsequent runs
- If YouTube rate-limits the requests, the run aborts gracefully and can be resumed later

## Output

Each transcript file contains:
- A header with video title, ID, URL, language, and retrieval date
- Timestamped transcript lines in `[HH:MM:SS] text` format

The tracking file (`processed_videos.json`) records every video's status so the tool can be run incrementally.
