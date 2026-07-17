"""Caption generation module for Clipify.

This module handles automatic caption generation and rendering for video clips.
Captions are word-aligned for accuracy and burned into clips for accessibility.

Exports:
    generate_captions: Generate captions from transcript
    render_captions: Render captions onto video
"""

from captions.generator import generate_captions

__all__ = [
    "generate_captions",
]
