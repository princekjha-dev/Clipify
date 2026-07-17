"""
Video Transcription - Supports both API and offline modes
"""

from pathlib import Path
from typing import List, Dict, Optional, Callable
import os
import logging
import time
import subprocess
import tempfile
import json

logger = logging.getLogger(__name__)

# Configuration
WHISPER_MODEL = "whisper-1"
MAX_RETRIES = 3


def _get_configured_api_keys() -> Dict[str, Optional[str]]:
    """Return currently configured API keys from the environment."""
    return {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
    }


def transcribe_video(
        video_path: Path,
        model_size: str = 'base',
        language: Optional[str] = None,
        transcriber_func: Optional[Callable] = None,
        provider: Optional[object] = None
) -> List[Dict]:
    """
    Transcribe video using a custom provider, supported API provider, or local Whisper.

    Args:
        video_path: Path to video file
        model_size: Model size for local Whisper (default: 'base')
        language: Optional language code (auto-detect if None)
        transcriber_func: Optional callable that handles transcription
        provider: Optional provider object or provider name string

    Returns:
        List of transcript segments with timestamps
    """
    
    # If a custom transcriber function is provided, use it
    if transcriber_func is not None:
        print(f"  Transcribing with custom transcriber...")
        return transcriber_func(video_path, model_size, language)

    # Provider instance support
    if provider is not None and hasattr(provider, 'get_transcriber'):
        try:
            transcriber_fn = provider.get_transcriber()
            if callable(transcriber_fn):
                logger.info("Transcribing with provider: %s", getattr(provider, 'name', 'custom'))
                return transcriber_fn(video_path, model_size, language)
        except Exception as exc:
            logger.warning("provider transcriber failed: %s", exc)

    # Provider name support
    provider_name = provider.lower() if isinstance(provider, str) else None
    api_keys = _get_configured_api_keys()

    if provider_name == 'groq':
        try:
            from ai.groq_provider import GroqProvider
            transcriber_fn = GroqProvider().get_transcriber()
            return transcriber_fn(video_path, model_size, language)
        except Exception as e:
            print(f"  Warning: Groq transcriber unavailable: {e}")

    if provider_name == 'openrouter':
        try:
            from ai.openrouter_provider import OpenRouterProvider
            transcriber_fn = OpenRouterProvider().get_transcriber()
            return transcriber_fn(video_path, model_size, language)
        except Exception as e:
            print(f"  Warning: OpenRouter transcriber unavailable: {e}")

    if provider_name == 'deepseek':
        try:
            from ai.deepseek_provider import DeepSeekProvider
            transcriber_fn = DeepSeekProvider().get_transcriber()
            return transcriber_fn(video_path, model_size, language)
        except Exception as e:
            print(f"  Warning: DeepSeek transcriber unavailable: {e}")

    if provider_name == 'local':
        return _transcribe_with_local_whisper(video_path, model_size, language)

    if provider_name == 'gemini' and api_keys["gemini"]:
        return _transcribe_with_gemini(video_path, language)

    if provider_name == 'anthropic' and api_keys["anthropic"]:
        return _transcribe_with_anthropic(video_path, language)

    if provider_name == 'openai' and api_keys["openai"]:
        return _transcribe_with_openai(video_path, language)

    # Automatic provider selection order
    if api_keys["gemini"]:
        return _transcribe_with_gemini(video_path, language)

    if api_keys["anthropic"]:
        return _transcribe_with_anthropic(video_path, language)

    if api_keys["openai"]:
        return _transcribe_with_openai(video_path, language)

    # Fallback to local Whisper
    logger.info("No API key found or supported provider unavailable, using local Whisper...")
    return _transcribe_with_local_whisper(video_path, model_size, language)


def _transcribe_with_openai(
        video_path: Path,
        language: Optional[str] = None
) -> List[Dict]:
    """Transcribe using OpenAI Whisper API with chunking for large files"""
    api_keys = _get_configured_api_keys()
    if not api_keys["openai"]:
        raise ValueError("OPENAI_API_KEY not set")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_keys["openai"])
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    logger.info("Transcribing with OpenAI Whisper API...")

    # Extract audio first if video
    audio_path = extract_audio_for_transcription(video_path)

    try:
        # Check file size to determine if chunking is needed
        file_size = audio_path.stat().st_size
        max_size = 23 * 1024 * 1024  # 23MB - safe limit for OpenAI API
        
        if file_size > max_size:
            logger.info("Audio file too large (%.1fMB), chunking...", file_size / 1024 / 1024)
            segments = _transcribe_openai_chunked(client, audio_path, language)
        else:
            # File is small enough, transcribe normally
            with open(audio_path, "rb") as audio_file:
                # Call OpenAI Whisper API
                transcript = client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    language=language
                )

            # Convert to our segment format
            segments = []
            for segment in transcript.segments:
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'words': []
                }
                segments.append(segment_data)

            # Calculate approximate cost
            duration_minutes = segments[-1]['end'] / 60 if segments else 0
            cost = duration_minutes * 0.006
            print(f"  Estimated cost: ${cost:.3f}")

        logger.info("Transcribed: %d segments", len(segments))
        if hasattr(transcript, 'language'):
            logger.info("Detected language: %s", transcript.language)

        return segments

    except Exception as exc:
        logger.error("OpenAI Transcription failed: %s", exc)
        raise

    finally:
        # Cleanup temp audio file
        if audio_path != video_path and audio_path.exists():
            audio_path.unlink()


def _transcribe_with_anthropic(
        video_path: Path,
        language: Optional[str] = None
) -> List[Dict]:
    """Transcribe using Anthropic API"""
    api_keys = _get_configured_api_keys()
    if not api_keys["anthropic"]:
        raise ValueError("ANTHROPIC_API_KEY not set")

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_keys["anthropic"])
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    logger.info("Transcribing with Anthropic API...")
    audio_path = extract_audio_for_transcription(video_path)

    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="claude-transcribe-1",
                file=audio_file,
                language=language or "en"
            )

        # Convert response to segments
        segments = []
        for seg in getattr(response, 'segments', []) or []:
            segments.append({
                'start': seg.get('start', 0),
                'end': seg.get('end', 0),
                'text': seg.get('text', '').strip(),
                'words': []
            })

        if not segments:
            text = getattr(response, 'text', '') or ''
            duration = _get_video_duration(video_path)
            segments = [{'start': 0, 'end': duration, 'text': text.strip(), 'words': []}]

        return segments

    except Exception as exc:
        logger.error("Anthropic Transcription failed: %s", exc)
        raise

    finally:
        if audio_path != video_path and audio_path.exists():
            audio_path.unlink()


def _transcribe_with_gemini(
        video_path: Path,
        language: Optional[str] = None
) -> List[Dict]:
    """Transcribe using Google Gemini API"""
    api_keys = _get_configured_api_keys()
    if not api_keys["gemini"]:
        raise ValueError("GEMINI_API_KEY not set")

    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

    genai.configure(api_key=api_keys["gemini"])
    logger.info("Transcribing with Gemini API...")

    audio_path = extract_audio_for_transcription(video_path)

    try:
        with open(audio_path, "rb") as audio_file:
            response = genai.audio.speech_to_text(
                model="gpt-4o-audio-preview",
                audio_file=audio_file,
                language=language or "en-US"
            )

        text = response.text if hasattr(response, 'text') else str(response)
        duration = _get_video_duration(video_path)

        segments = [{
            'start': 0,
            'end': duration,
            'text': text.strip(),
            'words': []
        }]

        return segments

    except Exception as exc:
        logger.error("Gemini Transcription failed: %s", exc)
        raise

    finally:
        if audio_path != video_path and audio_path.exists():
            audio_path.unlink()


def _transcribe_openai_chunked(client, audio_path: Path, language=None) -> List[Dict]:
    """Transcribe large audio files with OpenAI by splitting into chunks"""
    chunk_duration = 300  # 5 minutes per chunk
    all_segments = []
    chunk_offset = 0

    # Get total duration
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1:0', str(audio_path)],
            capture_output=True, text=True, timeout=10
        )
        total_duration = float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError, OSError):
        total_duration = 3600  # Default 1 hour

    num_chunks = int(total_duration / chunk_duration) + (1 if total_duration % chunk_duration else 0)
    logger.info("Splitting into %d chunks (%ds each)...", num_chunks, chunk_duration)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create and transcribe chunks
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, total_duration)
            chunk_path = tmpdir / f"chunk_{i:03d}.mp3"

            try:
                subprocess.run([
                    'ffmpeg', '-i', str(audio_path),
                    '-ss', str(start_time),
                    '-to', str(end_time),
                    '-q:a', '9', '-n',
                    str(chunk_path)
                ], capture_output=True, check=True, timeout=60)
            except Exception as exc:
                logger.warning("Failed to create chunk %d: %s", i, exc)
                continue

            # Transcribe chunk
            try:
                with open(chunk_path, "rb") as audio_file:
                    logger.debug("Transcribing chunk %d/%d...", i + 1, num_chunks)
                    
                    transcript = client.audio.transcriptions.create(
                        model=WHISPER_MODEL,
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                        language=language
                    )

                # Add segments with adjusted timestamps
                if hasattr(transcript, 'segments') and transcript.segments:
                    for seg in transcript.segments:
                        all_segments.append({
                            'start': seg.start + chunk_offset,
                            'end': seg.end + chunk_offset,
                            'text': seg.text.strip(),
                            'words': []
                        })

            except Exception as exc:
                logger.warning("Chunk %d transcription failed: %s", i, exc)
                continue

            chunk_offset = end_time

        logger.info("Chunked transcription cost estimate: $%.3f", cost)
        
        return all_segments


def _transcribe_with_local_whisper(
        video_path: Path,
        model_size: str = 'base',
        language: Optional[str] = None
) -> List[Dict]:
    """Transcribe using local Whisper model"""
    try:
        import whisper
    except ImportError:
        raise ImportError("whisper package not installed. Run: pip install openai-whisper")

    logger.info("Transcribing with local Whisper (%s model)...", model_size)
    
    try:
        # Load model
        model = whisper.load_model(model_size)
        
        # Transcribe
        result = model.transcribe(
            str(video_path),
            language=language,
            verbose=False
        )
        
        # Convert to our segment format
        segments = []
        for segment in result.get('segments', []):
            segment_data = {
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'words': []
            }
            segments.append(segment_data)
        
        logger.info("Transcribed: %d segments", len(segments))
        if result.get('language'):
            logger.info("Detected language: %s", result['language'])
        
        return segments
    
    except Exception as exc:
        logger.error("Local transcription failed: %s", exc)
        raise


def extract_audio_for_transcription(video_path: Path) -> Path:
    """Extract audio from video for Whisper API"""
    # If already audio, return as-is
    if video_path.suffix.lower() in ['.mp3', '.wav', '.m4a']:
        return video_path

    # Extract audio to temp file
    audio_path = video_path.parent / f"{video_path.stem}_temp.mp3"

    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(video_path),
        '-vn',
        '-acodec', 'libmp3lame',
        '-b:a', '192k',
        '-ar', '16000',
        str(audio_path)
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=300
        )
        return audio_path
    except Exception as exc:
        logger.warning("Audio extraction failed: %s", exc)
        return video_path


def _get_video_duration(video_path: Path) -> float:
    """Get duration for a video file using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(video_path)],
            capture_output=True,
            text=True,
            timeout=15
        )
        data = json.loads(result.stdout)
        return float(data.get('format', {}).get('duration', 0) or 0)
    except Exception:
        return 0.0


def transcribe_with_retry(
        video_path: Path,
        max_retries: int = MAX_RETRIES
) -> List[Dict]:
    """Transcribe with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            return transcribe_video(video_path)
        except Exception as exc:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning("Retry %d/%d in %ds...", attempt + 1, max_retries, wait_time)
                time.sleep(wait_time)
            else:
                raise


def get_text_at_time(transcript: List[Dict], start_time: float, end_time: float) -> str:
    """Extract text between two timestamps"""
    text_parts = []
    for segment in transcript:
        if segment['start'] < end_time and segment['end'] > start_time:
            text_parts.append(segment['text'])
    return ' '.join(text_parts).strip()


def get_transcript_summary(transcript: List[Dict]) -> Dict:
    """Get summary statistics about transcript"""
    if not transcript:
        return {
            'total_segments': 0,
            'total_duration': 0,
            'total_words': 0,
            'avg_segment_length': 0
        }

    total_words = sum(len(seg['text'].split()) for seg in transcript)
    total_duration = transcript[-1]['end'] - transcript[0]['start'] if transcript else 0

    return {
        'total_segments': len(transcript),
        'total_duration': total_duration,
        'total_words': total_words,
        'avg_segment_length': total_words / len(transcript) if transcript else 0,
        'start_time': transcript[0]['start'] if transcript else 0,
        'end_time': transcript[-1]['end'] if transcript else 0
    }