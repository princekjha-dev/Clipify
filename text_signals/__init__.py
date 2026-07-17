"""
Text Signals Module
Responsibility:
- Detect hooks (attention-grabbing first 3 seconds)
- Identify strong statements/questions
- Detect mid-thought starts
- Score text quality indicators
- Inspired by sumy-style extractive summarization
"""

from .hook_detector import detect_hook_strength, HookSignal, analyze_opening_3s
from .statement_analyzer import analyze_statement_strength, StatementStrength

__all__ = [
    'detect_hook_strength',
    'HookSignal',
    'analyze_opening_3s',
    'analyze_statement_strength',
    'StatementStrength'
]
