"""
Moment Extraction - Both AI and Traditional Methods
Enhanced with energy spike detection and viral keyword analysis
"""

from typing import List, Dict, Optional
import os
import json
import re
from pathlib import Path


# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-4o-mini"
COSTS = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.0025, "output": 0.01}
}


def extract_auto_moments(
        video_path: Path,
        transcript: List[Dict],
        min_length: int = 30,
        max_length: int = 60,
        target_clips: int = 10,
        verbose: bool = False
) -> List[Dict]:
    """
    Auto-generate 5-10 clips using energy spikes + viral keywords
    
    This is the primary auto-generation method that combines:
    1. Audio energy spike detection
    2. Viral keyword identification
    3. Hook detection
    4. Multi-factor scoring
    
    Args:
        video_path: Path to video file
        transcript: Full transcript with timestamps
        min_length: Minimum clip duration (seconds)
        max_length: Maximum clip duration (seconds)
        target_clips: Target number of clips (5-10 recommended)
        verbose: Print detailed analysis
    
    Returns:
        List of auto-selected moments with scores
    
    Example:
        >>> moments = extract_auto_moments(
        ...     Path("video.mp4"),
        ...     transcript,
        ...     target_clips=8
        ... )
        >>> for m in moments:
        ...     print(f"{m['start']:.1f}s-{m['end']:.1f}s: {m['score']:.1f}/10")
    """
    
    try:
        from moments.energy_analyzer import (
            detect_energy_spikes,
            combine_energy_and_keywords,
            get_top_viral_moments
        )
        from text_signals.hook_detector import analyze_opening_3s
    except ImportError:
        if verbose:
            print("  ⚠️  Energy analyzer not available, using traditional extraction")
        return extract_candidate_moments(transcript, min_length, max_length)
    
    if verbose:
        print(f"  Auto-generating {target_clips} clips using energy + keywords...")
    
    try:
        # Step 1: Detect energy spikes
        if verbose:
            print(f"  Step 1: Analyzing audio energy...")
        
        energy_spikes = detect_energy_spikes(
            video_path,
            segment_size=0.5,
            threshold_multiplier=1.5,
            verbose=verbose
        )
        
        if not energy_spikes:
            if verbose:
                print("  ⚠️  No energy spikes detected, falling back to traditional extraction")
            return extract_candidate_moments(transcript, min_length, max_length)
        
        # Step 2: Combine with keyword detection
        if verbose:
            print(f"  Step 2: Detecting viral keywords...")
        
        combined_spikes = combine_energy_and_keywords(energy_spikes, transcript)
        
        # Step 3: Get top viral moments by score
        if verbose:
            print(f"  Step 3: Selecting top {target_clips} moments...")
        
        viral_moments = get_top_viral_moments(
            combined_spikes,
            count=target_clips,
            min_duration=min_length,
            max_duration=max_length
        )
        
        # Step 4: Enhance with hook detection and scoring
        final_moments = []
        
        for i, spike in enumerate(viral_moments, 1):
            # Analyze hook strength
            hook_signal = analyze_opening_3s(transcript, spike.start, spike.end)
            
            # Get full text
            text = get_text_between_times(transcript, spike.start, spike.end)
            
            # Combine scores: 50% energy+keywords, 30% hook, 20% baseline
            combined_score = (
                spike.viral_score * 0.5 +
                (hook_signal.strength / 10) * 3 * 0.3 +
                7.0 * 0.2  # Baseline score
            )
            
            moment = {
                'start': spike.start,
                'end': spike.end,
                'duration': spike.duration,
                'text': text,
                'score': min(10.0, combined_score),
                'energy_level': spike.energy_level,
                'viral_keywords': spike.keywords,
                'hook_type': hook_signal.hook_type,
                'hook_strength': hook_signal.strength,
                'reason': f"Energy: {spike.energy_level:.0f}/100, Keywords: {', '.join(spike.keywords or ['none'])}",
                'language': detect_language(text),
                'source': 'energy_analysis'
            }
            final_moments.append(moment)
        
        # Sort by score (highest first)
        final_moments.sort(key=lambda m: m['score'], reverse=True)
        
        if verbose:
            print(f"  ✓ Generated {len(final_moments)} moments")
            for i, m in enumerate(final_moments, 1):
                print(f"    {i}. {m['start']:.1f}s-{m['end']:.1f}s (score: {m['score']:.1f}/10)")
        
        return final_moments
    
    except Exception as e:
        if verbose:
            print(f"  ✗ Auto-generation failed: {e}")
            print(f"  Falling back to traditional extraction...")
        return extract_candidate_moments(transcript, min_length, max_length)


def extract_candidate_moments(
        transcript: List[Dict],
        min_length: int = 30,
        max_length: int = 60
) -> List[Dict]:
    """
    Traditional rule-based moment extraction (no AI)
    Used as fallback when AI extraction fails
    """
    candidates = []

    for i in range(len(transcript)):
        # Try different window sizes
        for window_end in range(i + 1, min(i + 20, len(transcript))):
            start_time = transcript[i]['start']
            end_time = transcript[window_end]['end']
            duration = end_time - start_time

            # Check if duration is in range
            if min_length <= duration <= max_length:
                # Extract text
                text_parts = []
                for j in range(i, window_end + 1):
                    text_parts.append(transcript[j]['text'])
                text = ' '.join(text_parts).strip()

                # Simple quality check
                if len(text.split()) > 20:  # At least 20 words
                    candidates.append({
                        'start': start_time,
                        'end': end_time,
                        'duration': duration,
                        'text': text,
                        'language': detect_language(text)
                    })

    return candidates[:50]  # Return top 50 candidates


def extract_candidate_moments_ai(
        transcript: List[Dict],
        min_length: int = 30,
        max_length: int = 60,
        target_clips: int = 15
) -> List[Dict]:
    """
    Use GPT to intelligently extract viral-worthy moments
    """
    if not OPENAI_API_KEY:
        print("  ⚠️  OPENAI_API_KEY not set, using traditional extraction")
        return extract_candidate_moments(transcript, min_length, max_length)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        print("  ⚠️  openai package not installed, using traditional extraction")
        return extract_candidate_moments(transcript, min_length, max_length)

    print(f"  Using GPT to analyze transcript...")

    full_text = prepare_transcript_for_ai(transcript)

    prompt = f"""You are an expert at identifying viral-worthy moments from podcast/video transcripts for short-form content (TikTok, Reels, Shorts).

Analyze this transcript and identify the {target_clips} BEST moments for viral clips.

RULES:
1. Each clip must be {min_length}-{max_length} seconds long
2. Must start with a CLEAR hook (question, bold statement, intriguing setup)
3. Must be SELF-CONTAINED (viewer needs no context)
4. Must be ATTENTION-GRABBING from the first 2 seconds
5. Avoid moments that start mid-thought or require prior knowledge
6. Prioritize moments with:
   - Questions followed by answers
   - Surprising facts or revelations
   - Practical tips or insights
   - Emotional or relatable content
   - Clear narrative arc (setup → insight → conclusion)

TRANSCRIPT WITH TIMESTAMPS:
{full_text}

Return a JSON array of moments in this EXACT format:
[
  {{
    "start": <start_seconds>,
    "end": <end_seconds>,
    "reason": "<why this moment is viral-worthy>",
    "hook": "<the attention-grabbing opening>",
    "score_estimate": <1-10>
  }}
]

Return ONLY the JSON array, no other text."""

    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system",
                 "content": "You are an expert video editor specializing in viral short-form content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        moments_data = json.loads(content)

        # Convert to our format
        moments = []
        for item in moments_data:
            start = float(item['start'])
            end = float(item['end'])
            duration = end - start

            if min_length <= duration <= max_length:
                text = get_text_between_times(transcript, start, end)

                moments.append({
                    'start': start,
                    'end': end,
                    'duration': duration,
                    'text': text,
                    'ai_reason': item.get('reason', ''),
                    'ai_hook': item.get('hook', ''),
                    'ai_score': item.get('score_estimate', 7),
                    'language': detect_language(text)
                })

        print(f"  ✓ GPT identified {len(moments)} high-quality moments")
        print(f"  Estimated cost: ${estimate_cost(prompt, content):.3f}")

        return moments

    except (json.JSONDecodeError, Exception) as e:
        print(f"  ✗ GPT extraction failed: {e}")
        print("  Falling back to traditional extraction...")
        return extract_candidate_moments(transcript, min_length, max_length)


def prepare_transcript_for_ai(transcript: List[Dict], max_chars: int = 20000) -> str:
    """Prepare transcript for GPT with timestamps"""
    lines = []
    char_count = 0

    for segment in transcript:
        timestamp = format_time(segment['start'])
        line = f"[{timestamp}] {segment['text']}"

        if char_count + len(line) > max_chars:
            lines.append(f"\n... (transcript truncated to fit context) ...")
            break

        lines.append(line)
        char_count += len(line)

    return '\n'.join(lines)


def get_text_between_times(transcript: List[Dict], start: float, end: float) -> str:
    """Extract text between timestamps"""
    text_parts = []
    for segment in transcript:
        if segment['start'] >= start and segment['end'] <= end:
            text_parts.append(segment['text'])
    return ' '.join(text_parts).strip()


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def detect_language(text: str) -> str:
    """Simple language detection"""
    if re.search(r'[\u0900-\u097F]', text):
        return 'hindi'
    elif re.search(r'[\u4e00-\u9fff]', text):
        return 'chinese'
    elif re.search(r'[\u0600-\u06FF]', text):
        return 'arabic'
    return 'english'


def estimate_cost(prompt: str, response: str) -> float:
    """Estimate API cost"""
    input_tokens = len(prompt) / 4
    output_tokens = len(response) / 4

    costs = COSTS.get(GPT_MODEL, {"input": 0.00015, "output": 0.0006})

    cost = (input_tokens / 1000 * costs["input"]) + (output_tokens / 1000 * costs["output"])
    return cost


def extract_with_hybrid_approach(
        transcript: List[Dict],
        min_length: int = 30,
        max_length: int = 60,
        use_ai: bool = True
) -> List[Dict]:
    """Hybrid approach: Try AI first, fallback to traditional"""
    if use_ai:
        try:
            return extract_candidate_moments_ai(transcript, min_length, max_length)
        except Exception as e:
            print(f"  AI extraction failed, using traditional method: {e}")

    return extract_candidate_moments(transcript, min_length, max_length)