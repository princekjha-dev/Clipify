"""
Anthropic (Claude) provider for Clipify.

Uses the official `anthropic` Python SDK.  Transcription is delegated
to :func:`core.transcriber._transcribe_with_local_whisper` because
Anthropic does not expose a public audio-transcription endpoint.
"""

import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Anthropic Claude provider.

    Attributes:
        name: Human-readable provider name.
        api_key: Anthropic API key (from environment).
        client: Authenticated :class:`anthropic.Anthropic` instance.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.name = "Anthropic (Claude)"

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )

    def health_check(self) -> bool:
        """Verify the API key is accepted by sending a minimal request.

        Returns:
            True if the provider responded successfully, False otherwise.
        """
        try:
            self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception as exc:
            logger.warning("Anthropic health check failed: %s", exc)
            return False

    def get_transcriber(self):
        """Return the local Whisper transcription function.

        Anthropic does not expose an audio-transcription endpoint, so we
        fall back to the local Whisper model.

        Returns:
            Callable with signature ``(video_path, model_size, language) -> segments``.
        """
        from core.transcriber import _transcribe_with_local_whisper

        return _transcribe_with_local_whisper

    def filter_moments(
        self, candidates: List[Dict], transcript: List[Dict]
    ) -> List[Dict]:
        """Return candidates unchanged (no LLM filtering for this provider).

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
        """Apply a small score boost and return moments sorted descending.

        Args:
            moments: List of moment dicts, each with a ``score`` key.
            transcript: Full transcript segments (unused here).

        Returns:
            Moments sorted by score descending.
        """
        for moment in moments:
            moment["score"] = moment.get("score", 0) + 1
        return sorted(moments, key=lambda m: m.get("score", 0), reverse=True)
