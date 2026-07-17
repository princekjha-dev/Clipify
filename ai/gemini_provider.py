"""
Google Gemini provider for Clipify.

Uses the ``google-generativeai`` SDK.  Transcription is delegated to
:func:`core.transcriber._transcribe_with_local_whisper` because the
Gemini API's audio transcription path requires a File API upload and is
subject to frequent surface changes.
"""

import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Google Gemini AI provider.

    Attributes:
        name: Human-readable provider name.
        api_key: Gemini API key (from environment).
        genai: Configured ``google.generativeai`` module.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.name = "Gemini (Google)"

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self.genai = genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

    def health_check(self) -> bool:
        """Verify the API key works by listing available models.

        Returns:
            True if at least one model is returned, False otherwise.
        """
        try:
            models = list(self.genai.list_models())
            return len(models) > 0
        except Exception as exc:
            logger.warning("Gemini health check failed: %s", exc)
            return False

    def get_transcriber(self):
        """Return the local Whisper transcription function.

        Returns:
            Callable with signature ``(video_path, model_size, language) -> segments``.
        """
        from core.transcriber import _transcribe_with_local_whisper

        return _transcribe_with_local_whisper

    def filter_moments(
        self, candidates: List[Dict], transcript: List[Dict]
    ) -> List[Dict]:
        """Return candidates unchanged.

        Args:
            candidates: List of candidate moment dicts.
            transcript: Full transcript segments (unused here).

        Returns:
            The same ``candidates`` list unmodified.
        """
        return candidates

    def score_moments(
        self, moments: List[Dict], transcript: List[Dict]
    ) -> List[Dict]:
        """Apply a small score boost and sort moments descending.

        Args:
            moments: List of moment dicts with a ``score`` key.
            transcript: Full transcript segments (unused here).

        Returns:
            Moments sorted by score descending.
        """
        for moment in moments:
            moment["score"] = moment.get("score", 0) + 1
        return sorted(moments, key=lambda m: m.get("score", 0), reverse=True)
