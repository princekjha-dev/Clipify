"""
Statement Strength Analysis - ENHANCED
Rates overall statement quality independent of hooks

IMPROVEMENTS:
✓ More sophisticated scoring algorithms
✓ Readability analysis
✓ Engagement metrics
✓ Language pattern detection
✓ Better edge case handling
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import re


class StatementStrength(Enum):
    """Statement quality levels"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    EXCELLENT = 4  # NEW: Top tier


@dataclass
class StatementQuality:
    """Analyzed statement quality with detailed breakdown"""
    strength: StatementStrength
    score: float  # 0-10
    factors: Dict[str, float]  # Component scores
    recommendations: List[str] = None  # Improvement suggestions
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


def analyze_statement_strength(
        text: str,
        language: str = 'english',
        context: Optional[Dict] = None
) -> StatementQuality:
    """
    Analyze overall quality/strength of a statement
    
    Factors (enhanced):
    - Length (word count, optimal range)
    - Specificity (numbers, concrete nouns, examples)
    - Clarity (no mid-thought starts, proper structure)
    - Completeness (proper endings, no trailing)
    - Actionability (contains useful information)
    - Engagement (interesting, varied vocabulary)
    - Readability (sentence complexity, flow)
    
    Args:
        text: Statement to analyze
        language: Language code (default: 'english')
        context: Optional context (topic, audience, purpose)
    
    Returns:
        StatementQuality with detailed component breakdown
    """
    
    factors = {}
    recommendations = []
    
    # Normalize text
    text_clean = text.strip()
    words = text_clean.split()
    word_count = len(words)
    lower_text = text_clean.lower()
    
    # Factor 1: Length (optimal range 15-60 words)
    if word_count < 10:
        factors['length'] = max(0, word_count * 0.5)
        recommendations.append("Statement too short - add more detail")
    elif word_count <= 60:
        # Optimal range: 15-50 words gets 10 points
        optimal_score = min(10.0, (word_count / 5.0))
        factors['length'] = optimal_score
    else:
        # Diminishing returns after 60 words
        factors['length'] = max(5.0, 10.0 - (word_count - 60) * 0.1)
        recommendations.append("Statement too long - consider splitting")
    
    # Factor 2: Specificity (enhanced)
    specificity_score = 0.0
    
    # Numbers and data
    num_count = len(re.findall(r'\d+', text_clean))
    specificity_score += min(3.0, num_count * 1.0)
    
    # Concrete nouns (proper nouns, specific terms)
    proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', text_clean))
    specificity_score += min(2.0, proper_nouns * 0.5)
    
    # Technical/specific terms (words with 8+ letters)
    long_words = [w for w in words if len(w) >= 8]
    specificity_score += min(2.0, len(long_words) * 0.3)
    
    # Examples and illustrations
    example_indicators = ['for example', 'such as', 'like', 'including', 'e.g.', 'i.e.']
    has_examples = any(ind in lower_text for ind in example_indicators)
    if has_examples:
        specificity_score += 3.0
    
    factors['specificity'] = min(10.0, specificity_score)
    
    if specificity_score < 5.0:
        recommendations.append("Add specific examples, numbers, or concrete details")
    
    # Factor 3: Clarity (enhanced)
    clarity_score = 10.0
    
    # Vague starts (penalty)
    vague_starts = [
        'so', 'and', 'but', 'like', 'basically', 'literally',
        'um', 'uh', 'you know', 'i mean', 'kind of', 'sort of'
    ]
    starts_vague = any(lower_text.startswith(v) for v in vague_starts)
    if starts_vague:
        clarity_score -= 4.0
        recommendations.append("Avoid vague opening words")
    
    # Filler words (penalty)
    filler_words = ['actually', 'really', 'very', 'just', 'quite', 'rather']
    filler_count = sum(1 for word in filler_words if word in lower_text)
    if filler_count > 2:
        clarity_score -= min(3.0, filler_count * 0.5)
        recommendations.append("Reduce filler words for clarity")
    
    # Run-on sentences (penalty for very long sentences)
    if word_count > 40 and ',' not in text_clean[:len(text_clean)//2]:
        clarity_score -= 2.0
        recommendations.append("Break up long sentences with punctuation")
    
    factors['clarity'] = max(0.0, clarity_score)
    
    # Factor 4: Completeness (enhanced)
    completeness_score = 0.0
    
    # Proper ending punctuation
    ends_properly = text_clean.rstrip().endswith(('.', '!', '?', ':', ';'))
    if ends_properly:
        completeness_score += 5.0
    else:
        recommendations.append("Complete the statement with proper punctuation")
    
    # Doesn't trail off
    trailing_indicators = ['...', 'etc', 'and so on', 'or whatever', 'or something']
    trails_off = any(ind in lower_text[-20:] for ind in trailing_indicators)
    if not trails_off:
        completeness_score += 3.0
    else:
        recommendations.append("Avoid trailing off at the end")
    
    # Has complete thought structure
    has_subject_verb = _has_subject_verb_structure(text_clean)
    if has_subject_verb:
        completeness_score += 2.0
    
    factors['completeness'] = min(10.0, completeness_score)
    
    # Factor 5: Actionability (enhanced)
    actionable_score = 0.0
    
    # Action verbs
    action_verbs = [
        'do', 'make', 'create', 'build', 'learn', 'understand',
        'discover', 'show', 'try', 'find', 'change', 'improve',
        'develop', 'achieve', 'implement', 'solve', 'apply'
    ]
    action_count = sum(1 for verb in action_verbs if verb in lower_text)
    actionable_score += min(4.0, action_count * 1.0)
    
    # Instructional language
    instructional_words = ['how to', 'step', 'method', 'way', 'technique', 'approach']
    has_instruction = any(word in lower_text for word in instructional_words)
    if has_instruction:
        actionable_score += 3.0
    
    # Practical outcomes
    outcome_words = ['result', 'outcome', 'benefit', 'advantage', 'impact', 'effect']
    has_outcomes = any(word in lower_text for word in outcome_words)
    if has_outcomes:
        actionable_score += 3.0
    
    factors['actionable'] = min(10.0, actionable_score)
    
    if actionable_score < 4.0:
        recommendations.append("Add actionable information or practical value")
    
    # Factor 6: Engagement (NEW)
    engagement_score = 0.0
    
    # Varied vocabulary (not too repetitive)
    unique_words = len(set(words))
    vocab_ratio = unique_words / max(1, word_count)
    engagement_score += min(3.0, vocab_ratio * 5.0)
    
    # Emotional language
    emotional_words = [
        'amazing', 'incredible', 'powerful', 'important', 'critical',
        'essential', 'surprising', 'interesting', 'fascinating'
    ]
    has_emotion = any(word in lower_text for word in emotional_words)
    if has_emotion:
        engagement_score += 2.0
    
    # Questions (engaging)
    has_question = '?' in text_clean
    if has_question:
        engagement_score += 2.0
    
    # Conversational tone
    personal_pronouns = ['you', 'we', 'us', 'your', 'our']
    has_personal = any(word in lower_text for word in personal_pronouns)
    if has_personal:
        engagement_score += 3.0
    
    factors['engagement'] = min(10.0, engagement_score)
    
    # Factor 7: Readability (NEW)
    readability_score = 10.0
    
    # Average word length (penalize overly complex)
    avg_word_length = sum(len(w) for w in words) / max(1, word_count)
    if avg_word_length > 6.5:
        readability_score -= 2.0
        recommendations.append("Use simpler words for better readability")
    
    # Sentence structure (not too complex)
    clause_markers = [',', ';', ':', '—', '–']
    clause_count = sum(text_clean.count(m) for m in clause_markers)
    if clause_count > word_count / 10:  # More than 1 clause per 10 words
        readability_score -= 2.0
        recommendations.append("Simplify sentence structure")
    
    factors['readability'] = max(0.0, readability_score)
    
    # Calculate overall score (weighted average)
    weights = {
        'length': 0.10,
        'specificity': 0.20,
        'clarity': 0.25,
        'completeness': 0.15,
        'actionable': 0.15,
        'engagement': 0.10,
        'readability': 0.05
    }
    
    overall_score = sum(
        factors.get(k, 0) * v for k, v in weights.items()
    )
    
    # Apply contextual adjustments if provided
    if context:
        adjustments = _apply_contextual_adjustments(factors, context)
        overall_score += adjustments
    
    # Determine strength category
    if overall_score >= 8.5:
        strength = StatementStrength.EXCELLENT
    elif overall_score >= 7.0:
        strength = StatementStrength.STRONG
    elif overall_score >= 4.5:
        strength = StatementStrength.MODERATE
    else:
        strength = StatementStrength.WEAK
    
    return StatementQuality(
        strength=strength,
        score=round(overall_score, 2),
        factors={k: round(v, 2) for k, v in factors.items()},
        recommendations=recommendations[:3]  # Top 3 recommendations
    )


def _has_subject_verb_structure(text: str) -> bool:
    """
    Simple check for subject-verb structure
    Not perfect but catches obvious fragments
    """
    # Very basic heuristic: has words before and after common verbs
    common_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 
                    'do', 'does', 'did', 'can', 'could', 'will', 'would']
    
    words = text.lower().split()
    if len(words) < 3:
        return False
    
    for i, word in enumerate(words):
        if word in common_verbs and i > 0 and i < len(words) - 1:
            return True
    
    return False


def _apply_contextual_adjustments(factors: Dict[str, float], context: Dict) -> float:
    """Apply contextual bonuses/penalties based on use case"""
    adjustment = 0.0
    
    content_type = context.get('type', 'general')
    
    # Educational content: favor clarity and actionability
    if content_type == 'educational':
        if factors.get('clarity', 0) >= 8.0:
            adjustment += 0.5
        if factors.get('actionable', 0) >= 7.0:
            adjustment += 0.5
    
    # Entertainment: favor engagement
    elif content_type == 'entertainment':
        if factors.get('engagement', 0) >= 8.0:
            adjustment += 0.5
    
    # Marketing: favor specificity and CTAs
    elif content_type == 'marketing':
        if factors.get('specificity', 0) >= 7.0:
            adjustment += 0.3
        if factors.get('actionable', 0) >= 8.0:
            adjustment += 0.7
    
    return adjustment


def compare_statements(statements: List[str]) -> List[StatementQuality]:
    """
    Batch analyze and compare multiple statements
    
    Returns:
        List of StatementQuality objects, sorted by score (highest first)
    """
    analyses = []
    
    for statement in statements:
        quality = analyze_statement_strength(statement)
        analyses.append(quality)
    
    # Sort by score descending
    analyses.sort(key=lambda q: q.score, reverse=True)
    
    return analyses


def get_improvement_suggestions(text: str, target_score: float = 8.0) -> List[str]:
    """
    Get specific suggestions to improve statement to target score
    
    Args:
        text: Statement to analyze
        target_score: Desired quality score (0-10)
    
    Returns:
        List of actionable suggestions
    """
    quality = analyze_statement_strength(text)
    
    if quality.score >= target_score:
        return ["Statement already meets target quality!"]
    
    suggestions = quality.recommendations.copy()
    
    # Add specific suggestions based on weak factors
    weak_factors = {k: v for k, v in quality.factors.items() if v < 6.0}
    
    for factor, score in sorted(weak_factors.items(), key=lambda x: x[1]):
        if factor == 'specificity' and score < 6.0:
            suggestions.append("Add specific examples, statistics, or concrete details")
        elif factor == 'engagement' and score < 6.0:
            suggestions.append("Use more engaging language and conversational tone")
        elif factor == 'actionable' and score < 6.0:
            suggestions.append("Include actionable insights or practical applications")
    
    return suggestions[:5]  # Top 5 suggestions