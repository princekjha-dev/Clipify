"""Utilities module for Clipify.

This module provides configuration, logging, error handling, and health check utilities.

Exports:
    Config: Configuration constants for Clipify
    Logger: CLI output logger with colored messages
    ClipifyError: Base custom exception class
    healthcheck: Health check utilities
"""

from utils.config import Config
from utils.logger import Logger
from utils.errors import ClipifyError

__all__ = [
    "Config",
    "Logger",
    "ClipifyError",
]

__version__ = "1.0.1"
