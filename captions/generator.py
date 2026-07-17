"""Caption generation utilities for Clipify.

This module produces WebVTT caption files from clip transcripts.

Functions:
    generate_vtt_captions: Write a .vtt caption file for a single clip.
    generate_captions: Batch legacy helper (text + timestamp files).
    format_vtt_timestamp: Format seconds as WebVTT HH:MM:SS.mmm.
    format_timestamp: Format seconds as MM:SS (legacy helper).
"""

from pathlib import Path
from typing import List, Dict, Optional


def format_vtt_timestamp(seconds: float) -> str:
    """Format seconds as WebVTT timestamp (HH:MM:SS.mmm).

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted WebVTT timestamp string, e.g. ``00:01:23.456``.

    Example:
        >>> format_vtt_timestamp(83.456)
        '00:01:23.456'
    """
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    secs = total_s % 60
    total_m = total_s // 60
    mins = total_m % 60
    hours = total_m // 60
    return f"{hours:02d}:{mins:02d}:{secs:02d}.{ms:03d}"


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS timestamp (legacy helper).

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted timestamp string in MM:SS format.

    Example:
        >>> format_timestamp(125.5)
        '02:05'
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def generate_vtt_captions(
    video_path: Path,
    transcript: List[Dict],
    output_path: Path,
    clip_start: float = 0.0,
) -> Optional[Path]:
    """Generate a WebVTT caption file for a single clip.

    Timestamps are re-based relative to ``clip_start`` so that caption
    times match the clip rather than the original source video.

    Args:
        video_path: Path to the clip video (used only for context / logging).
        transcript: Full source transcript segment list, each with keys
            ``start``, ``end``, and ``text``.
        output_path: Destination path for the .vtt file.
        clip_start: Start time (seconds) of the clip within the source video.
            Segments are filtered to those that overlap the clip and their
            timestamps are offset by ``-clip_start``.

    Returns:
        Path to the written .vtt file, or ``None`` if no segments matched.
    """
    # Infer clip end from output filename neighbour (best-effort)
    # Filter transcript segments that overlap this clip region.
    # Since we don't receive clip_end here, collect *all* segments after
    # clip_start and let the caller pass clip_start correctly.
    segments = [
        seg
        for seg in transcript
        if seg.get("end", 0) > clip_start
    ]

    if not segments:
        return None

    lines = ["WEBVTT", ""]

    for i, seg in enumerate(segments, 1):
        # Re-base timestamps to clip-local time
        seg_start = max(seg["start"] - clip_start, 0.0)
        seg_end = max(seg["end"] - clip_start, seg_start + 0.1)
        text = seg.get("text", "").strip()
        if not text:
            continue

        lines.append(str(i))
        lines.append(f"{format_vtt_timestamp(seg_start)} --> {format_vtt_timestamp(seg_end)}")
        lines.append(text)
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def generate_captions(
    moments: List[Dict],
    captions_dir: Path,
    timestamps_dir: Path,
) -> List[Dict]:
    """Generate template-based caption and timestamp text files from moments.

    Creates one plain-text caption file and one timestamp file per moment.
    Used as the offline/legacy caption path.

    Args:
        moments: List of moment dictionaries containing ``text``, ``start``,
            ``end``, ``duration``, and optionally ``score``.
        captions_dir: Directory to save caption ``.txt`` files.
        timestamps_dir: Directory to save timestamp ``.txt`` files.

    Returns:
        List of caption data dictionaries, each with keys ``clip_id``,
        ``caption``, ``caption_file``, and ``timestamp_file``.

    Example:
        >>> moments = [{'text': 'Hello world', 'start': 0, 'end': 5, 'duration': 5}]
        >>> captions = generate_captions(moments, Path('caps'), Path('ts'))
        >>> len(captions)
        1
    """
    captions_dir.mkdir(parents=True, exist_ok=True)
    timestamps_dir.mkdir(parents=True, exist_ok=True)
    caption_data = []

    for i, moment in enumerate(moments, 1):
        text = moment.get("text", "")

        # Create simple caption (truncated)
        caption_text = text[:150] + ("..." if len(text) > 150 else "")

        # Save caption
        caption_path = captions_dir / f"clip_{i:02d}.txt"
        caption_path.write_text(
            f"=== CAPTION ===\n{caption_text}\n\n=== ORIGINAL ===\n{text}",
            encoding="utf-8",
        )

        # Save timestamp
        timestamp_path = timestamps_dir / f"clip_{i:02d}.txt"
        start = moment.get("start", 0)
        end = moment.get("end", 0)
        duration = moment.get("duration", end - start)
        score = moment.get("score", 0)
        timestamp_path.write_text(
            (
                f"Start: {int(start // 60):02d}:{int(start % 60):02d}\n"
                f"End: {int(end // 60):02d}:{int(end % 60):02d}\n"
                f"Duration: {duration:.1f}s\n"
                f"Score: {score:.2f}/10\n"
            ),
            encoding="utf-8",
        )

        caption_data.append(
            {
                "clip_id": i,
                "caption": caption_text,
                "caption_file": caption_path,
                "timestamp_file": timestamp_path,
            }
        )

    return caption_data