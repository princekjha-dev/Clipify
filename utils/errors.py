"""
Custom exceptions for Clipify
"""

class ClipifyError(Exception):
    """Base exception for Clipify errors"""
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