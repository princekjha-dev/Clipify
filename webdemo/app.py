# Hugging Face Spaces metadata
# title: Clipify Demo
# emoji: 🎬
# colorFrom: indigo
# colorTo: purple
# sdk: gradio
# sdk_version: (latest stable)
# app_file: app.py
# pinned: false

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Tuple

import gradio as gr

from clipify import process_video, validate_inputs, setup_argparse
from core.transcriber import transcribe_video
from utils.logger import Logger

REPO_URL = "https://github.com/princekjha-dev/Clipify"
MAX_CLIPS = 3
MAX_VIDEO_SECONDS = 180
MAX_VIDEO_BYTES = 100 * 1024 * 1024
RATE_LIMIT_PER_HOUR = 3
RATE_LIMIT_WINDOW_SECONDS = 60 * 60
SESSION_RATE_LIMITS = {}


def _get_session_key(request: gr.Request | None) -> str:
    if request is None:
        return "anonymous"
    return getattr(request, "client", None).host if getattr(request, "client", None) else "anonymous"


def _rate_limit_ok(session_key: str) -> Tuple[bool, str]:
    now = time.time()
    entry = SESSION_RATE_LIMITS.get(session_key)
    if not entry:
        SESSION_RATE_LIMITS[session_key] = [now]
        return True, ""

    recent = [ts for ts in entry if now - ts < RATE_LIMIT_WINDOW_SECONDS]
    recent.append(now)
    SESSION_RATE_LIMITS[session_key] = recent
    if len(recent) > RATE_LIMIT_PER_HOUR:
        return False, (
            "Demo limit reached — clone the repo to run unlimited locally: "
            f"{REPO_URL}"
        )
    return True, ""


def _get_video_duration_seconds(path: Path) -> float:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint=1:nokey=1", str(path)],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return float(result.stdout.strip() or 0)
    except Exception:
        return 0.0


def _validate_upload(video_path: str | None) -> Tuple[bool, str | None]:
    if not video_path:
        return False, "Please upload a video file."

    path = Path(video_path)
    if not path.exists() or not path.is_file():
        return False, "Uploaded file was not found."

    if path.suffix.lower() not in {".mp4", ".mov", ".webm"}:
        return False, "Only .mp4, .mov, and .webm files are supported."

    if path.stat().st_size > MAX_VIDEO_BYTES:
        return False, f"Video is too large. Maximum size is {MAX_VIDEO_BYTES // (1024 * 1024)}MB."

    duration = _get_video_duration_seconds(path)
    if duration and duration > MAX_VIDEO_SECONDS:
        return False, (
            f"Video is too long for this demo. Maximum length is {MAX_VIDEO_SECONDS // 60} minute(s)."
        )
    return True, None


def process_demo(video_file, clip_count, ratio, request: gr.Request | None = None):
    ok, error = _validate_upload(video_file)
    if not ok:
        return [], error, None

    session_key = _get_session_key(request)
    allowed, limit_msg = _rate_limit_ok(session_key)
    if not allowed:
        return [], limit_msg, None

    input_path = Path(video_file)
    work_dir = Path(tempfile.mkdtemp(prefix="clipify-demo-", dir="/tmp"))
    output_dir = work_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    copied_path = work_dir / input_path.name
    shutil.copy2(input_path, copied_path)

    try:
        args = setup_argparse().parse_args([
            "--video",
            str(copied_path),
            "--output",
            str(output_dir),
            "--clips",
            str(min(int(clip_count), MAX_CLIPS)),
            "--formats",
            ratio,
            "--ai",
            "local",
            "--no-captions",
        ])
        logger = Logger()
        config = validate_inputs(args, logger)
        config["ai_provider"] = "local"
        config["provider_instance"] = None
        result = process_video(copied_path, config, logger)

        clip_files = []
        for clip in result.get("clips", []):
            clip_path = Path(clip)
            if clip_path.exists():
                clip_files.append(str(clip_path))

        status = "Completed" if clip_files else "No clips were generated"
        log_text = f"Processed {copied_path.name} with local Whisper and {min(int(clip_count), MAX_CLIPS)} clip target.\n"
        if result.get("errors"):
            log_text += "\n" + "\n".join(result["errors"])
        return clip_files, status, log_text
    except Exception as exc:
        return [], f"Processing failed: {exc}", str(exc)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


with gr.Blocks(title="Clipify Demo") as demo:
    gr.Markdown(
        "This is a rate-limited free demo (max 3 clips, max 3-minute videos, local processing only). "
        "For full features and no limits, clone the repo: https://github.com/princekjha-dev/Clipify"
    )
    with gr.Row():
        with gr.Column(scale=1):
            video_input = gr.Video(label="Upload a video")
            clip_count = gr.Slider(minimum=1, maximum=3, step=1, value=3, label="Number of clips")
            ratio = gr.Dropdown(["9:16", "1:1", "16:9"], value="9:16", label="Output ratio")
            submit = gr.Button("Generate clips")
        with gr.Column(scale=1):
            gallery = gr.Gallery(label="Generated clips", columns=1, preview=True)
            status = gr.Textbox(label="Status")
            log_box = gr.Textbox(label="Processing log", lines=8)

    submit.click(
        fn=process_demo,
        inputs=[video_input, clip_count, ratio],
        outputs=[gallery, status, log_box],
    )


if __name__ == "__main__":
    demo.launch()
