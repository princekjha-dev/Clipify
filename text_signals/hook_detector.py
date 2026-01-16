"""
Hook Detection (First 3 seconds) - ENHANCED
Editorial rule: MUST have strong hook in first 3s or reject

Scoring:
- Question (strong): +10 points
- Surprising statement: +8 points
- Numbers/data: +7 points
- Call to action: +6 points
- Vague start: 0 points (reject)

IMPROVEMENTS:
✓ Better Unicode handling for international characters
✓ More comprehensive hook patterns
✓ Emotional trigger detection
✓ Contextual analysis
✓ Better edge case handling
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re


@dataclass
class HookSignal:
    """Detected hook signal with strength"""
    hook_type: str  # 'question', 'surprising', 'data', 'cta', 'emotional', 'none'
    strength: float  # 0-10
    text: str
    confidence: float  # 0-1
    reasons: List[str] = None  # Why this hook was detected
    
    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []


def analyze_opening_3s(
        transcript: List[Dict],
        moment_start: float,
        moment_end: Optional[float] = None
) -> HookSignal:
    """
    Analyze first 3 seconds of a moment for hook strength
    
    Args:
        transcript: Full transcript segments
        moment_start: Start time of moment (seconds)
        moment_end: Optional end time (uses start+3s if not provided)
    
    Returns:
        HookSignal with strength 0-10
    
    Editorial rule:
        < 6: REJECT (no clear hook)
        6-7: WEAK (accept but low priority)
        7-9: STRONG (good candidate)
        9-10: EXCELLENT (priority)
    """
    
    if moment_end is None:
        moment_end = moment_start + 3.0
    
    # Extract text from first 3 seconds
    opening_text = ''
    for segment in transcript:
        seg_start = segment.get('start', 0)
        seg_end = segment.get('end', 0)
        
        # Full overlap
        if seg_start >= moment_start and seg_end <= moment_end:
            opening_text += ' ' + segment.get('text', '')
        # Partial overlap
        elif seg_start < moment_end and seg_end > moment_start:
            opening_text += ' ' + segment.get('text', '')
    
    opening_text = opening_text.strip()
    
    if not opening_text:
        return HookSignal(
            hook_type='none',
            strength=0.0,
            text='',
            confidence=1.0,
            reasons=['No text in opening 3 seconds']
        )
    
    # Run all hook detectors and collect signals
    signals = []
    
    # Check 1: Question marks (multiple formats)
    question_patterns = ['?', '？', '¿']  # Latin, CJK, Spanish
    has_question = any(q in opening_text for q in question_patterns)
    
    # Enhanced question word detection
    question_words = [
        'what', 'why', 'how', 'when', 'where', 'who', 'which',
        'can', 'could', 'would', 'should', 'will', 'did', 'does',
        'is', 'are', 'was', 'were'
    ]
    
    lower_text = opening_text.lower()
    starts_with_question = any(lower_text.startswith(qw) for qw in question_words)
    
    if has_question or starts_with_question:
        confidence = 1.0 if has_question else 0.85
        signals.append(HookSignal(
            hook_type='question',
            strength=10.0,
            text=opening_text[:80],
            confidence=confidence,
            reasons=['Question mark detected' if has_question else 'Question word at start']
        ))
    
    # Check 2: Surprising/contrarian words (expanded)
    surprising_words = {
        'strong': ['actually', 'surprisingly', 'shocking', 'incredible', 
                   'unbelievable', 'secret', 'truth', 'reality', 'wrong'],
        'medium': ['wait', 'but', 'however', 'though', 'never knew', 
                   "didn't know", 'realize', 'turns out', 'plot twist'],
        'weak': ['interesting', 'fascinating', 'curious', 'unusual']
    }
    
    for strength_level, words in surprising_words.items():
        for word in words:
            if word in lower_text:
                strength_map = {'strong': 9.0, 'medium': 8.0, 'weak': 7.0}
                signals.append(HookSignal(
                    hook_type='surprising',
                    strength=strength_map[strength_level],
                    text=opening_text[:80],
                    confidence=0.85,
                    reasons=[f'Surprising word: "{word}"']
                ))
                break
        if signals and signals[-1].hook_type == 'surprising':
            break
    
    # Check 3: Numbers and data (enhanced)
    # Detect percentages, large numbers, ranges
    number_patterns = [
        (r'\d+%', 'percentage', 8.0),
        (r'\d{4,}', 'large number', 7.5),
        (r'\d+\s*(?:million|billion|thousand)', 'magnitude', 8.0),
        (r'\d+[-–]\d+', 'range', 7.0),
        (r'#?\d+\s+(?:ways|reasons|tips|secrets|facts)', 'listicle', 9.0),
        (r'\d+', 'number', 7.0)
    ]
    
    for pattern, desc, strength in number_patterns:
        if re.search(pattern, opening_text, re.IGNORECASE):
            signals.append(HookSignal(
                hook_type='data',
                strength=strength,
                text=opening_text[:80],
                confidence=0.9,
                reasons=[f'Numeric pattern: {desc}']
            ))
            break
    
    # Check 4: Strong CTAs (expanded)
    cta_patterns = {
        'direct': ['watch this', 'check this out', 'look at this', 'see this'],
        'instructive': ["here's", 'let me show', 'let me tell', 'i\'ll show'],
        'imperative': ['listen', 'understand', 'learn', 'discover', 'find out'],
        'engaging': ['imagine', 'picture this', 'think about', 'consider']
    }
    
    for category, phrases in cta_patterns.items():
        for phrase in phrases:
            if phrase in lower_text:
                strength_map = {'direct': 8.0, 'instructive': 7.0, 
                               'imperative': 6.5, 'engaging': 7.5}
                signals.append(HookSignal(
                    hook_type='cta',
                    strength=strength_map[category],
                    text=opening_text[:80],
                    confidence=0.75,
                    reasons=[f'CTA phrase: "{phrase}"']
                ))
                break
        if signals and signals[-1].hook_type == 'cta':
            break
    
    # Check 5: Emotional triggers (NEW)
    emotional_triggers = [
        'love', 'hate', 'fear', 'worry', 'excited', 'angry',
        'frustrated', 'amazing', 'terrible', 'best', 'worst',
        'dangerous', 'safe', 'risky', 'genius', 'stupid'
    ]
    
    for trigger in emotional_triggers:
        if trigger in lower_text:
            signals.append(HookSignal(
                hook_type='emotional',
                strength=7.5,
                text=opening_text[:80],
                confidence=0.7,
                reasons=[f'Emotional trigger: "{trigger}"']
            ))
            break
    
    # Check 6: Urgency/scarcity (NEW)
    urgency_words = ['now', 'today', 'immediately', 'quickly', 'before', 
                     'limited', 'only', 'last chance', 'hurry']
    
    if any(word in lower_text for word in urgency_words):
        signals.append(HookSignal(
            hook_type='urgency',
            strength=7.0,
            text=opening_text[:80],
            confidence=0.7,
            reasons=['Urgency/scarcity language']
        ))
    
    # Penalty: Vague starts (downgrade strong signals)
    vague_starts = ['so', 'and', 'um', 'uh', 'like', 'basically', 
                    'literally', 'you know', 'i mean']
    
    starts_vague = any(lower_text.startswith(v) for v in vague_starts)
    
    if starts_vague and signals:
        # Reduce strength of all signals by 20%
        for signal in signals:
            signal.strength *= 0.8
            signal.reasons.append('Penalty: vague start')
    
    # Return strongest signal
    if signals:
        best = max(signals, key=lambda s: s.strength * s.confidence)
        return best
    
    # No hook detected
    return HookSignal(
        hook_type='none',
        strength=0.0,
        text=opening_text[:80],
        confidence=1.0,
        reasons=['No hook patterns detected']
    )


def detect_hook_strength(moment: Dict, transcript: List[Dict]) -> float:
    """
    Convenience function: detect hook strength for a moment
    
    Returns:
        Hook strength 0-10
    """
    signal = analyze_opening_3s(
        transcript,
        moment['start'],
        moment.get('end', moment['start'] + 30)
    )
    return signal.strength


def reject_by_hook(moment: Dict, transcript: List[Dict], threshold: float = 6.0) -> bool:
    """
    Check if moment should be rejected due to weak hook
    
    Args:
        moment: Moment dictionary with start/end times
        transcript: Full transcript
        threshold: Minimum acceptable hook strength (default: 6.0)
    
    Returns:
        True if should reject (strength < threshold)
    """
    strength = detect_hook_strength(moment, transcript)
    return strength < threshold


def analyze_hook_with_context(
        moment: Dict,
        transcript: List[Dict],
        video_context: Optional[Dict] = None
) -> Dict:
    """
    Enhanced hook analysis with full context
    
    Args:
        moment: Moment to analyze
        transcript: Full transcript
        video_context: Optional metadata (title, description, category)
    
    Returns:
        Dict with comprehensive hook analysis
    """
    signal = analyze_opening_3s(transcript, moment['start'], moment.get('end'))
    
    analysis = {
        'hook_type': signal.hook_type,
        'strength': signal.strength,
        'confidence': signal.confidence,
        'opening_text': signal.text,
        'reasons': signal.reasons,
        'verdict': 'REJECT' if signal.strength < 6.0 else 'ACCEPT',
        'priority': _get_priority_level(signal.strength)
    }
    
    # Add contextual adjustments if available
    if video_context:
        adjustments = _apply_contextual_adjustments(signal, video_context)
        analysis['adjustments'] = adjustments
        analysis['adjusted_strength'] = signal.strength + adjustments.get('bonus', 0)
    
    return analysis


def _get_priority_level(strength: float) -> str:
    """Convert strength score to priority level"""
    if strength >= 9.0:
        return 'EXCELLENT'
    elif strength >= 7.0:
        return 'STRONG'
    elif strength >= 6.0:
        return 'WEAK'
    else:
        return 'REJECT'


def _apply_contextual_adjustments(signal: HookSignal, context: Dict) -> Dict:
    """Apply contextual bonuses/penalties based on video metadata"""
    adjustments = {'bonus': 0.0, 'reasons': []}
    
    # Example: Educational content gets bonus for question hooks
    if context.get('category') == 'education' and signal.hook_type == 'question':
        adjustments['bonus'] += 0.5
        adjustments['reasons'].append('Educational content + question hook')
    
    # Example: Entertainment needs stronger hooks
    if context.get('category') == 'entertainment' and signal.strength < 8.0:
        adjustments['bonus'] -= 0.5
        adjustments['reasons'].append('Entertainment requires stronger hook')
    
    return adjustments


def batch_analyze_hooks(
        moments: List[Dict],
        transcript: List[Dict],
        threshold: float = 6.0
) -> Dict:
    """
    Batch analyze multiple moments for hook strength
    
    Returns:
        Dict with accepted/rejected moments and statistics
    """
    results = {
        'accepted': [],
        'rejected': [],
        'statistics': {
            'total': len(moments),
            'hook_types': {},
            'avg_strength': 0.0
        }
    }
    
    total_strength = 0.0
    
    for moment in moments:
        signal = analyze_opening_3s(transcript, moment['start'], moment.get('end'))
        
        moment_with_hook = moment.copy()
        moment_with_hook['hook_analysis'] = {
            'type': signal.hook_type,
            'strength': signal.strength,
            'confidence': signal.confidence,
            'reasons': signal.reasons
        }
        
        if signal.strength >= threshold:
            results['accepted'].append(moment_with_hook)
        else:
            results['rejected'].append(moment_with_hook)
        
        # Update statistics
        total_strength += signal.strength
        hook_type = signal.hook_type
        results['statistics']['hook_types'][hook_type] = \
            results['statistics']['hook_types'].get(hook_type, 0) + 1
    
    if moments:
        results['statistics']['avg_strength'] = total_strength / len(moments)
    
    return results