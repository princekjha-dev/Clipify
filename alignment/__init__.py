"""
Alignment Module (Word-level Timing)
Responsibility:
- Convert segment timestamps to word-level boundaries
- Enable precise cutting (no mid-word/mid-sentence cuts)
- Provide alignment data for subtitle generation
- Inspired by whisperX architecture (simple JSON, no extra deps)
"""

from .word_aligner import align_words_to_timestamps, WordTimestamp, align_transcript

__all__ = ['align_words_to_timestamps', 'WordTimestamp', 'align_transcript']
