"""
Video Transcription - Supports both API and offline modes
"""

from pathlib import Path
from typing import List, Dict, Optional, Callable
import os
import time
import subprocess
import tempfile

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = "whisper-1"
MAX_RETRIES = 3


def transcribe_video(
        video_path: Path,
        model_size: str = 'base',
        language: Optional[str] = None,
        transcriber_func: Optional[Callable] = None
) -> List[Dict]:
    """
    Transcribe video using specified method or OpenAI Whisper API

    Args:
        video_path: Path to video file
        model_size: Model size for local Whisper (default: 'base')
        language: Optional language code (auto-detect if None)
        transcriber_func: Optional callable that handles transcription

    Returns:
        List of transcript segments with timestamps
    """
    
    # If a custom transcriber function is provided, use it
    if transcriber_func is not None:
        print(f"  Transcribing with custom transcriber...")
        return transcriber_func(video_path, model_size, language)
    
    # Try OpenAI API if available
    if OPENAI_API_KEY:
        return _transcribe_with_openai(video_path, language)
    
    # Fallback to local Whisper
    print(f"  No API key found, using local Whisper...")
    return _transcribe_with_local_whisper(video_path, model_size, language)


def _transcribe_with_openai(
        video_path: Path,
        language: Optional[str] = None
) -> List[Dict]:
    """Transcribe using OpenAI Whisper API with chunking for large files"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    print(f"  Transcribing with OpenAI Whisper API...")

    # Extract audio first if video
    audio_path = extract_audio_for_transcription(video_path)

    try:
        # Check file size to determine if chunking is needed
        file_size = audio_path.stat().st_size
        max_size = 23 * 1024 * 1024  # 23MB - safe limit for OpenAI API
        
        if file_size > max_size:
            print(f"  ⚠️  Audio file too large ({file_size / 1024 / 1024:.1f}MB), chunking...")
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

        print(f"  ✓ Transcribed: {len(segments)} segments")
        if hasattr(transcript, 'language'):
            print(f"  Detected language: {transcript.language}")

        return segments

    except Exception as e:
        print(f"  ✗ OpenAI Transcription failed: {e}")
        raise

    finally:
        # Cleanup temp audio file
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
    except:
        total_duration = 3600  # Default 1 hour

    num_chunks = int(total_duration / chunk_duration) + (1 if total_duration % chunk_duration else 0)
    print(f"  Splitting into {num_chunks} chunks ({chunk_duration}s each)...")

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
            except Exception as e:
                print(f"    ⚠️  Failed to create chunk {i}: {e}")
                continue

            # Transcribe chunk
            try:
                with open(chunk_path, "rb") as audio_file:
                    print(f"  Transcribing chunk {i+1}/{num_chunks}...", end='\r')
                    
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

            except Exception as e:
                print(f"    ⚠️  Chunk {i} transcription failed: {e}")
                continue

            chunk_offset = end_time

        print(f"                                    ")  # Clear progress line
        
        # Calculate cost for chunked transcription
        cost_per_minute = 0.006
        cost = (total_duration / 60) * cost_per_minute
        print(f"  Estimated cost: ${cost:.3f}")
        
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

    print(f"  Transcribing with local Whisper ({model_size} model)...")
    
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
        
        print(f"  ✓ Transcribed: {len(segments)} segments")
        if result.get('language'):
            print(f"  Detected language: {result['language']}")
        
        return segments
    
    except Exception as e:
        print(f"  ✗ Local transcription failed: {e}")
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
    except Exception as e:
        print(f"  Warning: Audio extraction failed: {e}")
        return video_path


def transcribe_with_retry(
        video_path: Path,
        max_retries: int = MAX_RETRIES
) -> List[Dict]:
    """Transcribe with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            return transcribe_video(video_path)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"  Retry {attempt + 1}/{max_retries} in {wait_time}s...")
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