"""
Audio Analysis Module
Responsibility:
- Detect silence/speech transitions
- Identify "dead air" regions (>300ms silence)
- Provide frame-accurate silence boundaries
- Enable smart clip cutting (avoid mid-speech)
"""

from .silence_detector import detect_silence_regions, SilenceRegion

__all__ = ['detect_silence_regions', 'SilenceRegion']
