"""
DeepSeek provider implementation (VERY CHEAP & FAST)
"""

import os
from pathlib import Path
from typing import List, Dict
import json

class DeepSeekProvider:
    """DeepSeek Provider - Very cheap and fast alternative to OpenAI"""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.name = "DeepSeek (Ultra-Cheap)"

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        try:
            from openai import OpenAI
            # DeepSeek uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
        except ImportError:
            raise ImportError("Install: pip install openai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            # Silently skip if balance is insufficient (402 error)
            error_msg = str(e)
            if "402" in error_msg or "insufficient" in error_msg.lower():
                return False
            print(f"DeepSeek health check failed: {e}")
            return False

    def get_transcriber(self):
        """Return transcription function using local Whisper"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.transcriber import _transcribe_with_local_whisper
        return _transcribe_with_local_whisper

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Filter moments using DeepSeek"""
        if len(candidates) == 0:
            return []

        print(f"  Filtering with DeepSeek...")

        # Use local aggressive filtering first
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
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
        """Check if moment is viral-worthy using DeepSeek"""
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
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.3
            )

            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer

        except Exception as e:
            print(f"  Warning: DeepSeek check failed: {e}, using fallback")
            return True

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Score moments using DeepSeek"""
        print(f"  Scoring with DeepSeek...")

        for moment in moments:
            score = self._score_moment(moment)
            moment['score'] = score
            moment['ai_scored'] = True
            moment['provider'] = 'deepseek'

        return sorted(moments, key=lambda m: m['score'], reverse=True)

    def _score_moment(self, moment: Dict) -> float:
        """Calculate viral score using DeepSeek"""
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
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.3
            )

            score_text = response.choices[0].message.content.strip()
            # Extract number from response
            import re
            match = re.search(r'\d+', score_text)
            if match:
                score = float(match.group())
                return min(max(score, 0), 100)
            else:
                return 60.0

        except Exception as e:
            print(f"  Warning: DeepSeek scoring failed: {e}, using fallback")
            # Fallback scoring based on text features
            text_length = len(moment.get('text', '').split())
            return min(50 + (text_length / 3), 95)
