"""
FFmpeg-based audio extraction for the music-recognition pipeline.

    video.mp4 -> ffmpeg -> audio.mp3 (10-20s sample, mono, 16kHz -> good enough
    for ACRCloud fingerprinting while keeping the upload small and fast).
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class FFmpegError(Exception):
    pass


def extract_audio_sample(
    video_path: str,
    output_dir: str = "/tmp/downloads",
    start_seconds: float = 0.0,
    duration_seconds: int = 18,
) -> str:
    """
    Extract a short mono MP3 sample from `video_path`, suitable for sending to
    ACRCloud. Returns the path to the generated audio file.
    """
    video_file = Path(video_path)
    if not video_file.exists():
        raise FFmpegError(f"Source video not found: {video_path}")

    out_path = Path(output_dir) / f"{video_file.stem}_sample.mp3"

    cmd = [
        "ffmpeg",
        "-y",  # overwrite
        "-i", str(video_file),
        "-ss", str(start_seconds),
        "-t", str(duration_seconds),
        "-vn",  # no video
        "-ac", "1",  # mono
        "-ar", "16000",  # 16kHz, plenty for fingerprinting
        "-b:a", "64k",
        str(out_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        logger.error("ffmpeg failed: %s", result.stderr)
        raise FFmpegError(f"ffmpeg exited with code {result.returncode}: {result.stderr[-500:]}")

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise FFmpegError("ffmpeg produced no output audio file.")

    return str(out_path)


def get_duration_seconds(media_path: str) -> float:
    """Return media duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        media_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise FFmpegError(f"ffprobe failed: {result.stderr}")
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0
