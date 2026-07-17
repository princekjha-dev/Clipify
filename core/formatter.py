"""
Enhanced formatter.py - FIXED VERSION
Multiple aspect ratios and advanced features with all errors corrected
"""

from pathlib import Path
from typing import List, Dict, Union
import subprocess
import json

# ✓ FIXED: Python 3.7 compatibility for Literal
try:
    from typing import Literal
except ImportError:
    # Python < 3.8 fallback
    from typing_extensions import Literal  # type: ignore

# Type alias for aspect ratios
AspectRatio = Union[str]  # Will be constrained to 9:16, 16:9, 1:1, 4:5


def format_clips_multi_platform(
    clip_paths: List[Path],
    moments: List[Dict],
    output_dir: Path,
    formats: List[str] = None
) -> Dict[str, List[Path]]:
    """Format clips for multiple platforms with different aspect ratios"""
    if formats is None:
        formats = ["9:16", "16:9"]
    
    formatted_clips = {format: [] for format in formats}

    for i, (clip_path, moment) in enumerate(zip(clip_paths, moments), 1):
        print(f"\n  Processing clip {i}/{len(clip_paths)}...")

        video_info = get_video_metadata(clip_path)

        for aspect_ratio in formats:
            output_name = f"clip_{i:02d}_{aspect_ratio.replace(':', 'x')}.mp4"
            output_path = output_dir / output_name

            # NO CAPTIONS - disabled for production
            success = apply_format_with_aspect_ratio(
                clip_path,
                output_path,
                None,
                aspect_ratio,
                video_info,
                moment
            )

            if success:
                formatted_clips[aspect_ratio].append(output_path)
                print(f"    ✓ {aspect_ratio}: {output_name}")
            else:
                print(f"    ✗ {aspect_ratio}: Failed")

    return formatted_clips


def get_video_metadata(video_path: Path) -> Dict:
    """
    Get detailed video metadata using ffprobe
    ✓ FIXED: Safe FPS parsing, added timeout
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(video_path)
    ]

    try:
        # ✓ FIXED: Added timeout
        result = subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        data = json.loads(result.stdout)

        video_stream = next(
            (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
            {}
        )

        # ✓ FIXED: Safe FPS parsing without eval()
        fps = 30
        fps_str = video_stream.get('r_frame_rate', '30/1')
        if fps_str and '/' in fps_str:
            try:
                num, den = fps_str.split('/')
                if float(den) != 0:
                    fps = float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                fps = 30
        elif fps_str:
            try:
                fps = float(fps_str)
            except ValueError:
                fps = 30

        return {
            'width': video_stream.get('width', 1920),
            'height': video_stream.get('height', 1080),
            'duration': float(data.get('format', {}).get('duration', 0)),
            'aspect_ratio': video_stream.get('width', 16) / max(video_stream.get('height', 9), 1),
            'fps': fps
        }
    except Exception as e:
        print(f"    Warning: Could not get video info: {e}")
        return {
            'width': 1920,
            'height': 1080,
            'duration': 0,
            'aspect_ratio': 16/9,
            'fps': 30
        }


def apply_format_with_aspect_ratio(
    input_path: Path,
    output_path: Path,
    srt_path: Path,
    aspect_ratio: str,
    video_info: Dict,
    moment: Dict
) -> bool:
    """Apply formatting with specific aspect ratio - NO CAPTIONS, NO CROP (use letterbox instead)"""
    dimensions = {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350)
    }

    target_width, target_height = dimensions[aspect_ratio]
    source_ar = video_info['aspect_ratio']
    target_ar = target_width / target_height

    if abs(source_ar - target_ar) < 0.01:
        # Already correct aspect ratio - just scale
        video_filter = build_scale_filter_clean(target_width, target_height, aspect_ratio)
    elif source_ar > target_ar:
        # Source wider than target (e.g., 16:9 to 9:16) - use LETTERBOX, never crop
        video_filter = build_letterbox_filter(target_width, target_height, aspect_ratio, video_info)
    else:
        # Source taller than target - use PAD with blurred background
        video_filter = build_pad_filter_clean(target_width, target_height, aspect_ratio, video_info)

    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(input_path),
        '-vf', video_filter,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        str(output_path)
    ]

    try:
        # ✓ FIXED: Added timeout
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=300
        )
        return output_path.exists()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        if hasattr(e, 'stderr'):
            print(f"      Error: {e.stderr.decode()[:200]}")
        return False


def build_scale_filter_clean(width: int, height: int, aspect_ratio: str) -> str:
    """Simple scale with subtle enhancement - NO CAPTIONS"""
    return (
        f"scale={width}:{height},"
        f"eq=contrast=1.05:saturation=1.08"
    )


def build_letterbox_filter(width: int, height: int, aspect_ratio: str, video_info: Dict) -> str:
    """Scale then add black letterbox bars - PRESERVES ALL CONTENT"""
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"eq=contrast=1.05:saturation=1.08"
    )


def build_pad_filter_clean(width: int, height: int, aspect_ratio: str, video_info: Dict) -> str:
    """Scale then add blurred background padding - ELEGANT, NO CROP"""
    return (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[scaled];"
        f"[0:v]scale={width}:{height},boxblur=20:1[bg];"
        f"[bg][scaled]overlay=(W-w)/2:(H-h)/2,"
        f"eq=contrast=1.05:saturation=1.08"
    )


def get_subtitle_style(aspect_ratio: str) -> str:
    """DEPRECATED: Captions disabled for production"""
    return ""


def prepare_caption_text(text: str, max_words_per_line: int = 6) -> list:
    """DEPRECATED: Caption text disabled - no burned captions in production"""
    return []


def create_subtitle_file(
    srt_path: Path,
    caption_lines: list,
    total_duration: float
):
    """DEPRECATED: SRT generation disabled - no burned subtitles"""
    pass


def format_srt_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    # ✓ FIXED: Comma not period for SRT format
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def add_intro_outro(
    clip_path: Path,
    output_path: Path,
    intro_path: Path = None,
    outro_path: Path = None
) -> bool:
    """Add intro and/or outro to clip"""
    if not intro_path and not outro_path:
        return False

    concat_file = clip_path.parent / f"concat_{clip_path.stem}.txt"

    # ✓ FIXED: Added encoding
    with open(concat_file, 'w', encoding='utf-8') as f:
        if intro_path:
            f.write(f"file '{intro_path}'\n")
        f.write(f"file '{clip_path}'\n")
        if outro_path:
            f.write(f"file '{outro_path}'\n")

    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(output_path)
    ]

    try:
        # ✓ FIXED: Added timeout
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, timeout=300)
        concat_file.unlink()
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        if concat_file.exists():
            concat_file.unlink()
        return False


def add_zoom_effect(
    input_path: Path,
    output_path: Path,
    zoom_factor: float = 1.1
) -> bool:
    """Add subtle zoom effect for engagement"""
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(input_path),
        '-vf', f"zoompan=z='min(zoom+0.0015,{zoom_factor})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920",
        '-c:a', 'copy',
        str(output_path)
    ]

    try:
        # ✓ FIXED: Added timeout
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, timeout=300)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def add_progress_bar(
    input_path: Path,
    output_path: Path,
    bar_height: int = 8,
    bar_color: str = "white"
) -> bool:
    """Add progress bar at top of video"""
    color_map = {
        'white': '0xFFFFFF',
        'red': '0xFF0000',
        'blue': '0x0000FF',
        'green': '0x00FF00'
    }

    color_hex = color_map.get(bar_color, '0xFFFFFF')

    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(input_path),
        '-vf', f"drawbox=x=0:y=0:w='iw*t/duration':h={bar_height}:color={color_hex}:t=fill",
        '-c:a', 'copy',
        str(output_path)
    ]

    try:
        # ✓ FIXED: Added timeout
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, timeout=300)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False