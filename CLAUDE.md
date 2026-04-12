# YouTube Transcript Agent

Python tool to batch-download transcripts from YouTube playlists with incremental tracking.

## Quick Start

```bash
python -m src.main "https://www.youtube.com/playlist?list=PLxxxxx"
```

## Project Structure

- `src/main.py` - CLI entry point and orchestrator
- `src/playlist.py` - Playlist metadata extraction via yt-dlp
- `src/transcript.py` - Transcript fetching via youtube-transcript-api
- `src/tracker.py` - JSON tracking file management (processed_videos.json)
- `src/formatter.py` - Transcript formatting and file output

## Dependencies

- Python 3.11+
- yt-dlp
- youtube-transcript-api

## Runtime Files (not committed)

- `transcripts/` - downloaded transcript text files
- `processed_videos.json` - tracks which videos have been processed
