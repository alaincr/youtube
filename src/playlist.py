from dataclasses import dataclass

import yt_dlp


@dataclass
class VideoEntry:
    video_id: str
    title: str
    url: str
    channel: str | None = None
    duration: float | None = None


@dataclass
class PlaylistInfo:
    playlist_id: str
    playlist_title: str
    videos: list[VideoEntry]


class PlaylistExtractionError(Exception):
    pass


def normalize_playlist_url(url_or_id: str) -> str:
    """Accept a playlist URL or bare playlist ID and return a usable URL."""
    url_or_id = url_or_id.strip()
    if url_or_id.startswith(("http://", "https://")):
        return url_or_id
    # Bare playlist ID like PLxxxxx
    return f"https://www.youtube.com/playlist?list={url_or_id}"


def extract_playlist_info(playlist_url: str) -> PlaylistInfo:
    """Extract video metadata from a YouTube playlist using yt-dlp (flat extraction)."""
    url = normalize_playlist_url(playlist_url)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "ignoreerrors": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            raise PlaylistExtractionError(f"Failed to extract playlist: {e}") from e

    if not info:
        raise PlaylistExtractionError(f"Could not retrieve playlist info from: {url}")

    entries = info.get("entries") or []
    videos = []
    for entry in entries:
        if entry is None:
            continue
        video_id = entry.get("id") or entry.get("url")
        if not video_id:
            continue
        videos.append(VideoEntry(
            video_id=video_id,
            title=entry.get("title") or "Unknown",
            url=f"https://www.youtube.com/watch?v={video_id}",
            channel=entry.get("channel") or entry.get("uploader"),
            duration=entry.get("duration"),
        ))

    if not videos:
        raise PlaylistExtractionError(
            f"Playlist is empty or all videos are unavailable: {url}"
        )

    return PlaylistInfo(
        playlist_id=info.get("id", "unknown"),
        playlist_title=info.get("title", "Unknown Playlist"),
        videos=videos,
    )
