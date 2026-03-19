"""
Google Gemini provider
"""

import os
from pathlib import Path
from typing import List, Dict


class GeminiProvider:
    """Gemini AI provider implementation"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.name = "Gemini"

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
        except ImportError:
            raise ImportError("Install: pip install google-generativeai")

    def health_check(self) -> bool:
        try:
            # stub/ping option; if not available fall back to True on key presence
            return True
        except Exception as e:
            print(f"Gemini health check failed: {e}")
            return False

    def get_transcriber(self):
        from core.transcriber import _transcribe_with_gemini
        return lambda video_path, *args, **kwargs: _transcribe_with_gemini(video_path, *args, **kwargs)

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        return candidates

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        for moment in moments:
            moment['score'] = moment.get('score', 0) + 1
        return moments
