"""
OpenAI provider (PAID)
"""

import os
from pathlib import Path
from typing import List, Dict


class OpenAIProvider:
    """OpenAI Provider"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.name = "OpenAI"

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install: pip install openai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"OpenAI health check failed: {e}")
            return False

    def get_transcriber(self):
        """Use OpenAI Whisper"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.transcriber import _transcribe_with_openai
        return lambda *args, **kwargs: _transcribe_with_openai(args[0], None)

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Filter with GPT"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from moments.filter import filter_moments_aggressively
        return filter_moments_aggressively(candidates, transcript)

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Score with GPT"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from moments.scorer import score_and_rank_moments
        return score_and_rank_moments(moments, transcript)