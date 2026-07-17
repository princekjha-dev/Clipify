"""
OpenRouter provider implementation (PRIMARY - Multi-model access)
Provides access to 100+ models via a single API key.
Many free-tier models available (e.g. meta-llama, mistral, google/gemma).
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


class OpenRouterProvider:
    """OpenRouter Provider - Primary multi-model gateway"""

    # Default model choices (free-tier friendly)
    CHAT_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
    FALLBACK_CHAT_MODEL = "mistralai/mistral-7b-instruct:free"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.name = "OpenRouter (Primary)"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

        try:
            from openai import OpenAI
            # OpenRouter uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/clipify",
                    "X-Title": "Clipify",
                },
            )
        except ImportError:
            raise ImportError("Install: pip install openai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.CHAT_MODEL,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True
        except Exception as e:
            # Try fallback model
            try:
                response = self.client.chat.completions.create(
                    model=self.FALLBACK_CHAT_MODEL,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5,
                )
                # Switch default model to fallback
                self.CHAT_MODEL = self.FALLBACK_CHAT_MODEL
                return True
            except Exception:
                pass
            logger.warning("OpenRouter health check failed: %s", exc)
            return False

    def get_transcriber(self):
        """Return the local Whisper function (OpenRouter has no audio API)."""
        from core.transcriber import _transcribe_with_local_whisper

        return _transcribe_with_local_whisper

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Filter moments using OpenRouter LLM."""
        if not candidates:
            return []

        logger.info("Filtering with OpenRouter (%s)...", self.CHAT_MODEL)

        # Use local aggressive filtering first
        from moments.filter import filter_moments_aggressively
        pre_filtered = filter_moments_aggressively(candidates, transcript)

        if len(pre_filtered) == 0:
            return []

        # AI filter top candidates
        filtered = []
        for moment in pre_filtered[:15]:
            if self._is_viral_worthy(moment):
                filtered.append(moment)

        return filtered if filtered else pre_filtered[:10]

    def _is_viral_worthy(self, moment: Dict) -> bool:
        """Check if moment is viral-worthy using OpenRouter"""
        prompt = f"""Is this clip viral-worthy? Reply ONLY YES or NO:

"{moment['text'][:200]}"

Requirements:
- Has clear hook/attention grabber
- Self-contained (doesn't need context)
- Engaging and shareable
- 15-90 seconds duration

Answer only YES or NO:"""

        try:
            response = self.client.chat.completions.create(
                model=self.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.3,
            )

            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer

        except Exception as exc:
            logger.warning("OpenRouter check failed: %s, using fallback", exc)
            return True

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Score moments using OpenRouter LLM."""
        logger.info("Scoring with OpenRouter (%s)...", self.CHAT_MODEL)

        for moment in moments:
            score = self._score_moment(moment)
            moment['score'] = score
            moment['ai_scored'] = True
            moment['provider'] = 'openrouter'

        return sorted(moments, key=lambda m: m['score'], reverse=True)

    def _score_moment(self, moment: Dict) -> float:
        """Calculate viral score using OpenRouter"""
        prompt = f"""Rate this clip's viral potential (0-100):

Text: "{moment['text'][:300]}"
Duration: {moment.get('duration', 30)} seconds

Score based on:
- Emotional hook (30%)
- Shareability (30%)
- Retention (20%)
- Clarity (10%)
- Engagement (10%)

Reply with ONLY a number 0-100:"""

        try:
            response = self.client.chat.completions.create(
                model=self.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.3,
            )

            score_text = response.choices[0].message.content.strip()
            match = re.search(r'\d+', score_text)
            if match:
                score = float(match.group())
                return min(max(score, 0), 100)
            else:
                return 60.0

        except Exception as exc:
            logger.warning("OpenRouter scoring failed: %s, using fallback", exc)
            text_length = len(moment.get("text", "").split())
            return min(50 + (text_length / 3), 95)
