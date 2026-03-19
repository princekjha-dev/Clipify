"""
Anthropic provider (Claude)
"""

import os
from pathlib import Path
from typing import List, Dict


class AnthropicProvider:
    """Anthropic provider implementation"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.name = "Anthropic"

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install: pip install anthropic")

    def health_check(self) -> bool:
        try:
            response = self.client.chat.completions.create(
                model="claude-3-100k",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"Anthropic health check failed: {e}")
            return False

    def get_transcriber(self):
        from core.transcriber import _transcribe_with_anthropic
        return lambda video_path, *args, **kwargs: _transcribe_with_anthropic(video_path, *args, **kwargs)

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        return candidates

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        for moment in moments:
            moment['score'] = moment.get('score', 0) + 1
        return moments
