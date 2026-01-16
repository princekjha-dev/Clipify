"""
Local provider (offline processing) - Smart & Advanced Edition
Uses energy spike detection, viral keyword analysis, and advanced scoring
without requiring any API keys.
"""

from pathlib import Path
from typing import List, Dict, Optional
import re


class LocalProvider:
    """Local offline provider with smart AI-like processing (no API needed)"""

    def __init__(self):
        self.name = "Local (Smart Offline)"
        self._energy_cache = {}

    def health_check(self) -> bool:
        """Always healthy - no dependencies needed"""
        return True

    def get_transcriber(self):
        """Use local Whisper"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.transcriber import _transcribe_with_local_whisper
        return _transcribe_with_local_whisper

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Smart local filtering using energy + keywords + hooks"""
        if len(candidates) == 0:
            return []

        print(f"  Filtering with Local Smart Analysis...")

        # Step 1: Use basic aggressive filtering
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from moments.filter import filter_moments_aggressively
        pre_filtered = filter_moments_aggressively(candidates, transcript)

        if len(pre_filtered) == 0:
            return []

        # Step 2: Apply smart local analysis to top candidates
        filtered = []
        for moment in pre_filtered[:20]:  # Top 20 candidates
            if self._is_viral_worthy_local(moment, transcript):
                filtered.append(moment)

        # Return at least top candidates if none passed
        return filtered if filtered else pre_filtered[:10]

    def _is_viral_worthy_local(self, moment: Dict, transcript: List[Dict]) -> bool:
        """
        Local smart analysis: Check if moment is viral-worthy
        Uses energy spikes, keyword detection, hook detection, and sentiment
        """
        
        # Calculate viral score from multiple signals
        signals = {
            'energy': self._check_energy_spike(moment),           # 0-30
            'keywords': self._check_viral_keywords(moment),       # 0-30
            'hooks': self._check_hook_pattern(moment),            # 0-20
            'pacing': self._check_pacing_energy(moment),          # 0-10
            'clarity': self._check_clarity(moment),               # 0-10
        }
        
        # Weighted calculation
        total_score = (
            signals['energy'] * 1.0 +
            signals['keywords'] * 1.0 +
            signals['hooks'] * 1.5 +  # Hooks are highly viral
            signals['pacing'] * 0.5 +
            signals['clarity'] * 0.5
        )
        
        # Threshold: 35/100 = acceptable viral moment
        return total_score >= 35

    def _check_energy_spike(self, moment: Dict) -> float:
        """
        Check if this moment has energy spike characteristics
        Returns 0-30 points
        """
        text = moment.get('text', '').lower()
        
        # Energy indicators
        energy_markers = [
            (r'\b(wow|omg|oh my god|amazing|incredible|shocking)\b', 3),
            (r'\b(wow)\b', 5),  # Double wow = extra energy
            (r'!!!', 2),
            (r'\?\?', 2),
            (r'(all caps words)', 3),
        ]
        
        score = 0
        for pattern, points in energy_markers:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += min(matches * points, 15)  # Cap at 15
        
        # Natural speech interruptions (sign of excitement)
        if re.search(r'\b(um|uh|like)\b.*\b(what|wait|stop|hold on)\b', text):
            score += 5
        
        return min(score, 30)

    def _check_viral_keywords(self, moment: Dict) -> float:
        """
        Check for viral keywords and phrases
        Returns 0-30 points
        """
        text = moment.get('text', '').lower()
        
        # Keyword categories with weights
        keyword_sets = {
            'shocking': {
                'words': ['shocking', 'unbelievable', 'crazy', 'insane', 'mind blown',
                         'did not expect', 'never saw that coming', 'plot twist'],
                'weight': 3
            },
            'action': {
                'words': ['happened', 'crashed', 'exploded', 'collapsed', 'broke',
                         'failed', 'succeeded', 'won', 'beaten', 'destroyed'],
                'weight': 3
            },
            'emotional': {
                'words': ['love', 'hate', 'proud', 'ashamed', 'happy', 'sad',
                         'angry', 'hilarious', 'awkward', 'embarrassing'],
                'weight': 2
            },
            'reveal': {
                'words': ['actually', 'turns out', 'secret', 'truth', 'never knew',
                         'didn\'t know', 'find out', 'discover', 'exposed'],
                'weight': 2.5
            },
            'numbers': {
                'pattern': r'\d+(?:%|k|m|billion|million|thousand)',
                'weight': 2
            }
        }
        
        score = 0
        
        for category, config in keyword_sets.items():
            if 'pattern' in config:
                matches = len(re.findall(config['pattern'], text))
                score += min(matches * config['weight'], 10)
            else:
                for word in config['words']:
                    if word in text:
                        score += config['weight']
        
        return min(score, 30)

    def _check_hook_pattern(self, moment: Dict) -> float:
        """
        Check for hook patterns that grab attention
        Returns 0-20 points (highly weighted)
        """
        text = moment.get('text', '').lower()
        
        hook_patterns = [
            (r'\bwait\b.*\b(what|how|why)\b', 5),
            (r'\b(what if|imagine|picture this)\b', 4),
            (r'\b(would you|could you|can you)\b', 3),
            (r'\b(have you ever|did you know)\b', 4),
            (r'\bhold on\b', 3),
            (r'\b(listen|trust me|watch this)\b', 3),
            (r'\b(this is|here\'s|you won\'t|you\'ll|you\'re)\b.*\b(crazy|insane|amazing)\b', 5),
        ]
        
        score = 0
        for pattern, points in hook_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += points
        
        return min(score, 20)

    def _check_pacing_energy(self, moment: Dict) -> float:
        """
        Check for rapid pacing and energy (short sentences, exclamations)
        Returns 0-10 points
        """
        text = moment.get('text', '')
        
        # Check sentence count and punctuation
        sentences = len(re.split(r'[.!?]+', text.strip()))
        exclamations = len(re.findall(r'!', text))
        questions = len(re.findall(r'\?', text))
        
        # Short, punchy sentences = high energy
        if len(text) > 0:
            avg_sentence_length = len(text) / max(sentences, 1)
            pacing_score = 10 if avg_sentence_length < 30 else 5
        else:
            pacing_score = 0
        
        # Punctuation intensity
        punctuation_intensity = (exclamations * 2 + questions) / max(sentences, 1)
        intensity_score = min(punctuation_intensity * 2, 5)
        
        return min(pacing_score + intensity_score, 10)

    def _check_clarity(self, moment: Dict) -> float:
        """
        Check if moment is clear and self-contained
        Returns 0-10 points
        """
        text = moment.get('text', '').lower()
        
        # Length check: too short or too long is bad
        word_count = len(text.split())
        
        if word_count < 5:
            return 2  # Too short, incomplete
        elif word_count > 150:
            return 5  # Long but might be good
        else:
            return 10  # Just right
        
        # Contains complete thoughts (not cut off)
        if text.endswith(('.', '!', '?')):
            return 10
        else:
            return 7  # Incomplete

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Score moments using smart local analysis"""
        print(f"  Scoring with Local Smart Analysis...")

        for moment in moments:
            score = self._calculate_smart_score(moment, transcript)
            moment['score'] = score
            moment['ai_method'] = 'local_smart'
            moment['scoring_factors'] = self._get_scoring_explanation(moment)

        return sorted(moments, key=lambda m: m['score'], reverse=True)

    def _calculate_smart_score(self, moment: Dict, transcript: List[Dict]) -> float:
        """
        Calculate comprehensive viral score (0-100)
        Combines energy, keywords, hooks, and other factors
        """
        
        # Get signal scores
        energy_score = self._check_energy_spike(moment)  # 0-30
        keyword_score = self._check_viral_keywords(moment)  # 0-30
        hook_score = self._check_hook_pattern(moment)  # 0-20
        pacing_score = self._check_pacing_energy(moment)  # 0-10
        clarity_score = self._check_clarity(moment)  # 0-10
        
        # Weighted calculation
        base_score = (
            energy_score * 0.3 +
            keyword_score * 0.35 +
            hook_score * 0.25 +
            pacing_score * 0.05 +
            clarity_score * 0.05
        )
        
        # Boost for clear hooks
        if self._check_hook_pattern(moment) > 10:
            base_score *= 1.15
        
        # Reduce score if too long
        text_length = len(moment.get('text', '').split())
        if text_length > 200:
            base_score *= 0.8
        
        # Ensure score is 0-100
        return min(max(base_score, 0), 100)

    def _get_scoring_explanation(self, moment: Dict) -> Dict:
        """Get breakdown of why moment scored this way"""
        return {
            'energy': self._check_energy_spike(moment),
            'keywords': self._check_viral_keywords(moment),
            'hooks': self._check_hook_pattern(moment),
            'pacing': self._check_pacing_energy(moment),
            'clarity': self._check_clarity(moment),
            'method': 'local_smart_analysis'
        }