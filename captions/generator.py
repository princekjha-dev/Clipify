"""
Caption generation utilities
"""

from pathlib import Path
from typing import List, Dict


def generate_captions(
    moments: List[Dict],
    captions_dir: Path,
    timestamps_dir: Path
) -> List[Dict]:
    """
    Generate template-based captions (no AI)
    Used by offline provider and as fallback
    """
    caption_data = []

    for i, moment in enumerate(moments, 1):
        text = moment['text']

        # Create simple caption
        caption_text = text[:150] + ("..." if len(text) > 150 else "")

        # Save caption
        caption_path = captions_dir / f"clip_{i:02d}.txt"
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(f"=== CAPTION ===\n{caption_text}\n\n")
            f.write(f"=== ORIGINAL ===\n{text}")

        # Save timestamp
        timestamp_path = timestamps_dir / f"clip_{i:02d}.txt"
        with open(timestamp_path, 'w', encoding='utf-8') as f:
            f.write(f"Start: {int(moment['start'] // 60):02d}:{int(moment['start'] % 60):02d}\n")
            f.write(f"End: {int(moment['end'] // 60):02d}:{int(moment['end'] % 60):02d}\n")
            f.write(f"Duration: {moment['duration']:.1f}s\n")
            f.write(f"Score: {moment.get('score', 0):.2f}/10\n")

        caption_data.append({
            'clip_id': i,
            'caption': caption_text,
            'caption_file': caption_path,
            'timestamp_file': timestamp_path
        })

    return caption_data


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"