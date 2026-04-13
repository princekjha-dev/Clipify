"""Configuration defaults for Clipify"""
from pathlib import Path


class Config:
    """Configuration constants for Clipify"""
    DEFAULT_OUTPUT_DIR = Path("output")
    DEFAULT_CLIP_COUNT = 10
    DEFAULT_FORMATS = ["9:16", "16:9"]
    VIDEO_QUALITY = "high"
    MIN_CLIP_LENGTH = 2.0
    MAX_CLIP_LENGTH = 30.0
    POLL_INTERVAL_SECONDS = 8
    SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv", ".avi", ".webm"]
