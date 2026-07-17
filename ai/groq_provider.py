"""
Groq provider implementation (FREE tier)

Uses Groq's Whisper-large-v3 for ultra-fast transcription and
Llama 3.1 for moment filtering / scoring.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import tempfile

logger = logging.getLogger(__name__)


class GroqProvider:
    """Groq Cloud Provider - FREE tier"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.name = "Groq (Free)"

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install: pip install groq")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as exc:
            logger.warning("Groq health check failed: %s", exc)
            return False

    def get_transcriber(self):
        """Return the Groq Whisper transcription callable."""
        return self._transcribe_audio

    def _transcribe_audio(
        self,
        video_path: Path,
        model_size: str = "base",
        language: Optional[str] = None,
    ) -> List[Dict]:
        """Transcribe using Groq Whisper-large-v3 with chunking for large files."""
        from core.transcriber import extract_audio_for_transcription

        logger.info("Transcribing with Groq Whisper-large-v3...")

        audio_path = extract_audio_for_transcription(video_path)

        try:
            # Get file size to check if chunking is needed
            file_size = audio_path.stat().st_size
            max_size = 23 * 1024 * 1024  # 23MB - safe limit for Groq API
            
            if file_size > max_size:
                logger.info("Audio file too large (%.1fMB), chunking...", file_size / 1024 / 1024)
                return self._transcribe_chunked(audio_path, language)
            else:
                # File is small enough, transcribe normally
                with open(audio_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3",
                        response_format="verbose_json",
                        language=language
                    )

                segments = self._parse_segments(transcription, video_path)
                logger.info("Transcribed: %d segments", len(segments))
                return segments

        finally:
            if audio_path != video_path and audio_path.exists():
                audio_path.unlink()

    def _transcribe_chunked(self, audio_path: Path, language=None) -> List[Dict]:
        """Transcribe large audio files by splitting into chunks"""
        chunk_duration = 300  # 5 minutes per chunk
        all_segments = []
        chunk_offset = 0

        # Get total duration
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            total_duration = float(result.stdout.strip())
        except (subprocess.SubprocessError, ValueError, OSError):
            total_duration = 3600  # Default 1 hour

        num_chunks = int(total_duration / chunk_duration) + (1 if total_duration % chunk_duration else 0)
        logger.info("Splitting into %d chunks (%ds each)...", num_chunks, chunk_duration)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create chunks
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
                        
                        transcription = self.client.audio.transcriptions.create(
                            file=audio_file,
                            model="whisper-large-v3",
                            response_format="verbose_json",
                            language=language
                        )

                    # Add segments with adjusted timestamps
                    if hasattr(transcription, 'segments') and transcription.segments:
                        for seg in transcription.segments:
                            all_segments.append({
                                'start': seg['start'] + chunk_offset,
                                'end': seg['end'] + chunk_offset,
                                'text': seg['text'].strip(),
                                'words': []
                            })
                    elif hasattr(transcription, 'text'):
                        all_segments.append({
                            'start': chunk_offset,
                            'end': end_time,
                            'text': transcription.text.strip(),
                            'words': []
                        })

                except Exception as exc:
                    logger.warning("Chunk %d transcription failed: %s", i, exc)
                    continue

                chunk_offset = end_time

            logger.info("Transcribed: %d segments from %d chunks", len(all_segments), num_chunks)
            return all_segments

    def _parse_segments(self, transcription, video_path) -> List[Dict]:
        """Parse transcription response into segment format"""
        segments = []
        
        if hasattr(transcription, 'segments') and transcription.segments:
            for seg in transcription.segments:
                segments.append({
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip(),
                    'words': []
                })
        else:
            # Fallback
            duration = 0
            try:
                from core.clip_processor import get_video_info
                info = get_video_info(video_path)
                duration = info.get("duration", 0)
            except Exception:
                duration = 60

            segments = [{
                'start': 0,
                'end': duration,
                'text': transcription.text if hasattr(transcription, 'text') else '',
                'words': []
            }]
        
        return segments

    def filter_moments(self, candidates: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Filter moments using Groq Llama 3.1."""
        if not candidates:
            return []

        logger.info("Filtering with Groq Llama 3.1...")

        # Use local aggressive filtering first
        from moments.filter import filter_moments_aggressively
        pre_filtered = filter_moments_aggressively(candidates, transcript)

        if len(pre_filtered) == 0:
            return []

        # AI filter top candidates
        filtered = []
        for moment in pre_filtered[:15]:
            if self._is_viral_worthy(moment):
                filtered.append(moment)

        return filtered

    def _is_viral_worthy(self, moment: Dict) -> bool:
        """Check if moment is viral-worthy"""
        prompt = f"""Is this clip viral-worthy? Reply ONLY YES or NO:

"{moment['text'][:200]}"

Must have: Clear hook, self-contained, engaging.
Answer:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.3
            )

            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer

        except Exception:
            return True  # Allow on API failure

    def score_moments(self, moments: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """Score moments using Groq Llama 3.1."""
        logger.info("Scoring with Groq Llama 3.1...")

        for moment in moments:
            score = self._score_moment(moment)
            moment['score'] = score
            moment['ai_scored'] = True

        moments.sort(key=lambda x: x['score'], reverse=True)
        return moments

    def _score_moment(self, moment: Dict) -> float:
        """Score single moment"""
        prompt = f"""Rate this clip 0-10 for viral potential. Return ONLY a number:

"{moment['text'][:250]}"
Duration: {moment['duration']:.1f}s

Score:"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()
            # Extract first number
            import re
            numbers = re.findall(r'\d+\.?\d*', content)
            if numbers:
                score = float(numbers[0])
                return min(10, max(0, score))
            return 7.0

        except Exception:
            return 7.0