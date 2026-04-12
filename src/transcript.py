from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
)


DEFAULT_LANGUAGES = ["en", "en-US", "en-GB"]


class NoTranscriptAvailable(Exception):
    """Raised when no transcript can be obtained after all fallback attempts."""
    pass


@dataclass
class TranscriptSnippet:
    text: str
    start: float
    duration: float


@dataclass
class TranscriptResult:
    video_id: str
    language: str
    language_code: str
    is_generated: bool
    snippets: list[TranscriptSnippet]


def _to_result(fetched, video_id: str | None = None) -> TranscriptResult:
    """Convert a FetchedTranscript into our TranscriptResult."""
    return TranscriptResult(
        video_id=fetched.video_id if hasattr(fetched, "video_id") else (video_id or ""),
        language=getattr(fetched, "language", "unknown"),
        language_code=getattr(fetched, "language_code", ""),
        is_generated=getattr(fetched, "is_generated", False),
        snippets=[
            TranscriptSnippet(text=s.text, start=s.start, duration=s.duration)
            for s in fetched
        ],
    )


def fetch_transcript(
    video_id: str, languages: list[str] | None = None
) -> TranscriptResult:
    """Fetch transcript for a video with multi-step language fallback.

    Strategy:
      1. Try direct fetch with preferred languages
      2. Try auto-generated transcripts in preferred languages
      3. Try any available transcript translated to English
      4. Return whatever transcript is available
    """
    api = YouTubeTranscriptApi()
    langs = languages or DEFAULT_LANGUAGES

    # Attempt 1: direct fetch with preferred languages
    try:
        result = api.fetch(video_id, languages=langs)
        return _to_result(result)
    except (NoTranscriptFound, CouldNotRetrieveTranscript):
        pass

    # Attempt 2+: enumerate available transcripts and try fallbacks
    try:
        transcript_list = api.list(video_id)
    except TranscriptsDisabled:
        raise NoTranscriptAvailable(
            f"Transcripts are disabled for video {video_id}"
        )
    except CouldNotRetrieveTranscript:
        raise NoTranscriptAvailable(
            f"Could not retrieve transcript list for video {video_id}"
        )

    # Try auto-generated in preferred languages
    try:
        transcript = transcript_list.find_generated_transcript(langs)
        return _to_result(transcript.fetch())
    except NoTranscriptFound:
        pass

    # Try any transcript, translated to English if possible
    for transcript in transcript_list:
        translation_codes = [
            t["language_code"] for t in transcript.translation_languages
        ]
        if "en" in translation_codes:
            return _to_result(transcript.translate("en").fetch())

    # Last resort: return the first available transcript in any language
    for transcript in transcript_list:
        return _to_result(transcript.fetch())

    raise NoTranscriptAvailable(
        f"No transcript available for video {video_id}"
    )
