"""Moments detection and scoring module for Clipify.

This module handles viral moment detection, extraction, and scoring based on
multiple signal types (audio energy, silence patterns, NLP hooks, sentiment).

Exports:
    extract_auto_moments: Detect viral moments in video
    score_and_rank_moments: Score and rank moments by virality
    create_energy_analyzer: Create audio energy analyzer
"""

from moments.extractor import extract_auto_moments
from moments.scorer import score_and_rank_moments
from moments.energy_analyzer import create_energy_analyzer

__all__ = [
    "extract_auto_moments",
    "score_and_rank_moments",
    "create_energy_analyzer",
]
