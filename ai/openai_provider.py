"""
OpenAI provider for Clipify.

Provides GPT-based moment filtering/scoring and OpenAI Whisper transcription.
"""

import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI GPT provider.

    Attributes:
        name: Human-readable provider name.
        api_key: OpenAI API key (from environment).
        client: Authenticated :class:`openai.OpenAI` instance.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.name = "OpenAI"

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def health_check(self) -> bool:
        """Verify API connection with a minimal completion.

        Returns:
            True if the API responded successfully, False otherwise.
        """
        try:
            self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True
        except Exception as exc:
            logger.warning("OpenAI health check failed: %s", exc)
            return False

    def get_transcriber(self):
        """Return the OpenAI Whisper transcription function.

        Returns:
            Callable with signature ``(video_path, language=None) -> segments``.
        """
        from core.transcriber import _transcribe_with_openai

        return lambda video_path, model_size=None, language=None: _transcribe_with_openai(
            video_path, language
        )

    def filter_moments(
        self, candidates: List[Dict], transcript: List[Dict]
    ) -> List[Dict]:
        """Filter moments using aggressive local rules.

        Args:
            candidates: List of candidate moment dicts.
            transcript: Full transcript segments.

        Returns:
            Filtered list of moments.
        """
        from moments.filter import filter_moments_aggressively

        return filter_moments_aggressively(candidates, transcript)

    def score_moments(
        self, moments: List[Dict], transcript: List[Dict]
    ) -> List[Dict]:
        """Score and rank moments.

        Args:
            moments: List of moment dicts.
            transcript: Full transcript segments.

        Returns:
            Scored and sorted moments.
        """
        from moments.scorer import score_and_rank_moments

        return score_and_rank_moments(moments, transcript)