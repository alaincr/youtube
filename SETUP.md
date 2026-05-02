# YouTube Transcript Agent — Local Setup & Run

## Prerequisites

- Python 3.11+
- git
- pip

## Step 1: Clone and checkout

```bash
git clone https://github.com/alaincr/youtube.git
cd youtube
git checkout claude/youtube-transcript-agent-u1CAk
```

## Step 2: Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Run the transcript agent

Replace the playlist URL below with your own YouTube playlist URL:

```bash
python -m src.main "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

You can also pass a bare playlist ID:

```bash
python -m src.main "PLxxxxxxxxxx"
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir <dir>` | `transcripts/` | Directory where transcript files are saved |
| `--tracking-file <file>` | `processed_videos.json` | JSON file tracking processed videos |
| `--languages en es fr` | `en en-US en-GB` | Language codes in priority order |

### Example with all options

```bash
python -m src.main "https://www.youtube.com/playlist?list=PLxxxxx" \
  --output-dir my_transcripts \
  --tracking-file my_tracking.json \
  --languages fr en es
```

## Step 4: Re-run to process new videos

Simply run the same command again. Already-processed videos are skipped automatically:

```bash
python -m src.main "https://www.youtube.com/playlist?list=PLxxxxx"
```

## What it produces

- `transcripts/<video_id>.txt` — one file per video with timestamped transcript lines
- `processed_videos.json` — tracking file recording which videos have been processed

### Sample transcript output

```
# Rick Astley - Never Gonna Give You Up
# Video ID: dQw4w9WgXcQ
# URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
# Language: English (en) [auto-generated]
# Retrieved: 2026-05-02T14:30:00Z

[00:00:00] We're no strangers to love
[00:00:03] You know the rules and so do I
[00:00:07] A full commitment's what I'm thinking of
```

## Troubleshooting

- **Private playlists**: yt-dlp cannot access private playlists without cookies. Unlisted playlists work if you use the full URL.
- **Rate limiting**: If YouTube blocks requests, the script aborts gracefully. Progress is saved — just re-run later.
- **No transcript available**: Videos without transcripts are recorded as `failed` and retried on the next run.
- **Wrong Python version**: Make sure you activate the venv (`source .venv/bin/activate`) before running.

## Using as a Claude Code skill

Once cloned locally, the repo includes a Claude Code skill at `.claude/skills/fetch-transcripts.md`. When running Claude Code from inside the `youtube/` directory, invoke:

```
/fetch-transcripts
```

Then provide your playlist URL when prompted.
