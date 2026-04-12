import argparse
import sys

from .playlist import PlaylistExtractionError, extract_playlist_info
from .transcript import NoTranscriptAvailable, fetch_transcript
from .tracker import is_processed, load_tracking, mark_processed, save_tracking
from .formatter import save_transcript


def process_playlist(
    playlist_url: str,
    output_dir: str = "transcripts",
    tracking_file: str = "processed_videos.json",
    languages: list[str] | None = None,
) -> dict:
    """Download transcripts for all new videos in a playlist.

    Returns a dict with lists of processed, skipped, and failed video IDs.
    """
    # Extract playlist metadata
    print(f"Fetching playlist info from: {playlist_url}")
    playlist = extract_playlist_info(playlist_url)
    print(f"Playlist: {playlist.playlist_title} ({len(playlist.videos)} videos)")

    # Load tracking state
    tracking = load_tracking(tracking_file)
    tracking["playlist_id"] = playlist.playlist_id
    tracking["playlist_title"] = playlist.playlist_title

    processed = []
    skipped = []
    failed = []

    for i, video in enumerate(playlist.videos, 1):
        prefix = f"[{i}/{len(playlist.videos)}]"

        if is_processed(tracking, video.video_id):
            print(f"{prefix} Skipping (already processed): {video.title}")
            skipped.append(video.video_id)
            continue

        print(f"{prefix} Processing: {video.title}")
        try:
            result = fetch_transcript(video.video_id, languages)
            file_path = save_transcript(output_dir, video.video_id, video.title, result)
            mark_processed(
                tracking,
                video.video_id,
                video.title,
                transcript_file=file_path,
                language=result.language_code,
                is_generated=result.is_generated,
                status="success",
            )
            save_tracking(tracking, tracking_file)
            gen = " (auto-generated)" if result.is_generated else ""
            print(f"         Saved: {file_path} [{result.language_code}{gen}]")
            processed.append(video.video_id)

        except NoTranscriptAvailable as e:
            print(f"         No transcript available: {e}")
            mark_processed(
                tracking,
                video.video_id,
                video.title,
                transcript_file=None,
                language=None,
                is_generated=None,
                status="failed",
                error=str(e),
            )
            save_tracking(tracking, tracking_file)
            failed.append(video.video_id)

        except Exception as e:
            error_type = type(e).__name__
            # Abort on rate-limiting / IP blocks
            if error_type in ("RequestBlocked", "IpBlocked"):
                print(f"\n  Blocked by YouTube ({error_type}). Aborting.")
                print("  Wait a while and try again. Already-processed videos are saved.")
                mark_processed(
                    tracking,
                    video.video_id,
                    video.title,
                    transcript_file=None,
                    language=None,
                    is_generated=None,
                    status="failed",
                    error=error_type,
                )
                save_tracking(tracking, tracking_file)
                failed.append(video.video_id)
                break

            print(f"         Error ({error_type}): {e}")
            mark_processed(
                tracking,
                video.video_id,
                video.title,
                transcript_file=None,
                language=None,
                is_generated=None,
                status="failed",
                error=str(e),
            )
            save_tracking(tracking, tracking_file)
            failed.append(video.video_id)

    # Summary
    print(f"\nDone. Processed: {len(processed)}, Skipped: {len(skipped)}, Failed: {len(failed)}")
    return {"processed": processed, "skipped": skipped, "failed": failed}


def main():
    parser = argparse.ArgumentParser(
        description="Download transcripts from a YouTube playlist"
    )
    parser.add_argument("playlist_url", help="YouTube playlist URL or playlist ID")
    parser.add_argument(
        "--output-dir", default="transcripts",
        help="Directory for transcript files (default: transcripts/)",
    )
    parser.add_argument(
        "--tracking-file", default="processed_videos.json",
        help="Path to tracking JSON file (default: processed_videos.json)",
    )
    parser.add_argument(
        "--languages", nargs="+", default=None,
        help="Language codes in priority order (default: en en-US en-GB)",
    )
    args = parser.parse_args()

    try:
        result = process_playlist(
            args.playlist_url,
            output_dir=args.output_dir,
            tracking_file=args.tracking_file,
            languages=args.languages,
        )
        sys.exit(0 if not result["failed"] else 1)
    except PlaylistExtractionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
