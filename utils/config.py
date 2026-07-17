"""Configuration defaults for Clipify

This module provides configuration constants used throughout the Clipify application.
All values are typed for better IDE support and type checking.
"""
from pathlib import Path
from typing import List


class Config:
    """Configuration constants for Clipify application.
    
    Attributes:
        DEFAULT_OUTPUT_DIR (Path): Default output directory for generated clips
        DEFAULT_CLIP_COUNT (int): Default number of clips to extract
        DEFAULT_FORMATS (List[str]): Default aspect ratios for output (9:16, 16:9, 1:1)
        VIDEO_QUALITY (str): Default video quality (low, medium, high)
        MIN_CLIP_LENGTH (float): Minimum clip duration in seconds
        MAX_CLIP_LENGTH (float): Maximum clip duration in seconds
        POLL_INTERVAL_SECONDS (int): Polling interval for async operations
        SUPPORTED_VIDEO_EXTENSIONS (List[str]): Supported video file formats
    """
    DEFAULT_OUTPUT_DIR: Path = Path("output")
    DEFAULT_CLIP_COUNT: int = 10
    DEFAULT_FORMATS: List[str] = ["9:16", "16:9"]
    VIDEO_QUALITY: str = "high"
    MIN_CLIP_LENGTH: float = 2.0
    MAX_CLIP_LENGTH: float = 30.0
    POLL_INTERVAL_SECONDS: int = 8
    SUPPORTED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".mov", ".mkv", ".avi", ".webm"]
