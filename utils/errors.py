"""
Custom exceptions for Clipify

Provides a hierarchy of typed exceptions used throughout the pipeline.
All errors inherit from ClipifyError so callers can catch the base type.
"""


class ClipifyError(Exception):
    """Base exception for Clipify errors"""
    pass


class ValidationError(ClipifyError):
    """Input validation failed (bad CLI args, missing files, invalid config)"""
    pass


class DownloadError(ClipifyError):
    """Video download failed"""
    pass


class TranscriptionError(ClipifyError):
    """Transcription failed"""
    pass


class ExtractionError(ClipifyError):
    """Clip extraction failed"""
    pass


class AIProviderError(ClipifyError):
    """AI provider error"""
    pass


class FormatError(ClipifyError):
    """Clip formatting / aspect-ratio conversion failed"""
    pass


class ConfigError(ClipifyError):
    """Configuration is invalid or incomplete"""
    pass


class CaptionError(ClipifyError):
    """Caption generation or VTT writing failed"""
    pass