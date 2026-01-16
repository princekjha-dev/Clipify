#!/usr/bin/env python3
"""
Clipify - Production AI Video Clipping Tool - ENHANCED
Sellable, reliable, professional.

NEW FEATURES:
✓ Auto-detect viral moments (energy spikes + keywords)
✓ Multi-threshold silence detection → smarter cuts
✓ Auto-generate 5-10 clips per video
✓ Folder-based workflow (drop video → get clips)

IMPROVEMENTS:
✓ Better error handling and recovery
✓ Progress tracking and ETA
✓ Parallel clip processing option
✓ Quality validation at each step
✓ Detailed output report
✓ Support for batch processing
✓ Resume capability
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re

from ai.provider_selector import select_ai_provider
from core.downloader import download_video
from core.transcriber import transcribe_video
from core.clip_processor import extract_clips, extract_clips_parallel, get_video_info
from core.formatter import format_clips_multi_platform
from core.folder_watcher import FolderWorkflow, create_folder_workflow
from moments.extractor import extract_candidate_moments, extract_auto_moments
from moments.filter import filter_moments_aggressively
from moments.scorer import score_and_rank_moments
from audio_analysis.silence_detector import detect_multi_threshold_silence, recommend_threshold
from captions.generator import generate_captions
from utils.logger import Logger
from utils.errors import ClipifyError


# Configuration constants
MIN_QUALITY_SCORE = 6.5  # Minimum score for clips (6.5/10)
MAX_CLIPS_PER_VIDEO = 10  # Maximum clips to extract
DEFAULT_AUTO_CLIPS = 8  # Default for auto-generation mode
SUPPORTED_FORMATS = ["9:16", "16:9", "1:1"]  # Supported output formats


def setup_output_directory(base_dir: str = "output") -> Dict[str, Path]:
    """
    Create output directory structure with timestamp
    
    Returns:
        Dict mapping directory names to Path objects
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(base_dir) / timestamp

    dirs = {
        "root": output_root,
        "clips": output_root / "clips",
        "captions": output_root / "captions",
        "timestamps": output_root / "timestamps",
        "temp": output_root / "temp",
        "reports": output_root / "reports"
    }

    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    return dirs


def validate_video_info(video_info: Dict, logger: Logger) -> bool:
    """
    Validate video meets minimum requirements
    
    Args:
        video_info: Video metadata dict
        logger: Logger instance
    
    Returns:
        True if valid, False otherwise
    """
    duration = video_info.get('duration', 0)
    width = video_info.get('width', 0)
    height = video_info.get('height', 0)
    
    issues = []
    
    # Check duration (minimum 60 seconds)
    if duration < 60:
        issues.append(f"Video too short ({duration:.1f}s < 60s minimum)")
    
    # Check resolution (minimum 480p)
    if height < 480:
        issues.append(f"Resolution too low ({width}x{height} < 480p minimum)")
    
    # Check if video has audio
    if video_info.get('audio_codec') == 'unknown':
        issues.append("No audio track detected")
    
    if issues:
        for issue in issues:
            logger.warning(f"⚠️  {issue}")
        return False
    
    return True


def save_processing_report(
        dirs: Dict[str, Path],
        video_url: str,
        video_info: Dict,
        transcript_stats: Dict,
        moments_stats: Dict,
        clips_info: List[Dict]
) -> Path:
    """
    Save detailed processing report as JSON
    
    Returns:
        Path to report file
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'video_url': video_url,
        'video_info': {
            'duration': video_info.get('duration', 0),
            'resolution': f"{video_info.get('width', 0)}x{video_info.get('height', 0)}",
            'fps': video_info.get('fps', 0),
            'codec': video_info.get('codec', 'unknown'),
            'file_size': video_info.get('file_size', 0)
        },
        'transcript': transcript_stats,
        'moments': moments_stats,
        'clips': clips_info,
        'output_directory': str(dirs['root'])
    }
    
    report_path = dirs['reports'] / 'processing_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_path


def process_video(
        video_url: str,
        logger: Logger,
        use_parallel: bool = True,
        output_formats: List[str] = None,
        auto_mode: bool = False,
        target_clips: int = DEFAULT_AUTO_CLIPS,
        provider_name: Optional[str] = None
) -> Dict:
    """
    Main video processing pipeline
    
    Args:
        video_url: YouTube URL or video file path
        logger: Logger instance
        use_parallel: Use parallel clip extraction (faster)
        output_formats: List of output formats (default: ["9:16", "16:9"])
        auto_mode: Use auto-generation (energy + keywords) instead of AI filtering
        target_clips: Number of clips to generate in auto mode
        provider_name: Optional provider name ('groq', 'gemini', 'openai', 'local')
    
    Returns:
        Dict with processing results
    
    Raises:
        ClipifyError: If processing fails
    """
    
    if output_formats is None:
        output_formats = ["9:16", "16:9"]
    
    logger.header("CLIPIFY - PRODUCTION AI VIDEO CLIPPING")
    if auto_mode:
        logger.info(f"Mode: AUTO-GENERATION ({target_clips} clips)")
    logger.info(f"Video: {video_url}")
    
    # STEP 1: Select and verify AI provider (only for non-auto mode)
    if not auto_mode:
        logger.step(1, 10, "Selecting AI Provider")
        ai_provider = select_ai_provider(logger, provider_name=provider_name)
        logger.success(f"Using: {ai_provider.name}")
        step_offset = 0
    else:
        ai_provider = None
        step_offset = -1
        logger.step(1, 9, "Preparing Auto-Generation")
        logger.info("Using energy spike + keyword detection")
    
    # STEP 2: Download video
    logger.step(2 + step_offset, 10 + step_offset, "Downloading Video")
    dirs = setup_output_directory()
    
    try:
        video_path = download_video(video_url, dirs["temp"], use_cookies=True)
    except Exception as e:
        raise ClipifyError(f"Download failed: {e}")
    
    video_info = get_video_info(video_path)
    logger.success(f"Downloaded: {video_path.name}")
    logger.info(
        f"Duration: {video_info.get('duration', 0):.1f}s | "
        f"Resolution: {video_info.get('width', '?')}x{video_info.get('height', '?')} | "
        f"FPS: {video_info.get('fps', '?'):.1f}"
    )
    
    # Validate video
    if not validate_video_info(video_info, logger):
        raise ClipifyError("Video does not meet minimum requirements")
    
    # STEP 3: Transcribe
    logger.step(3 + step_offset, 10 + step_offset, "Transcribing Audio")
    
    if not auto_mode:
        transcriber_func = ai_provider.get_transcriber()
    else:
        transcriber_func = None
    
    try:
        transcript = transcribe_video(
            video_path,
            model_size='base',
            transcriber_func=transcriber_func
        )
    except Exception as e:
        raise ClipifyError(f"Transcription failed: {e}")
    
    logger.success(f"Transcribed: {len(transcript)} segments")
    
    # Calculate transcript stats
    total_words = sum(len(seg.get('text', '').split()) for seg in transcript)
    transcript_stats = {
        'segments': len(transcript),
        'total_words': total_words,
        'avg_words_per_segment': total_words / max(1, len(transcript))
    }
    logger.info(f"Words: {total_words} ({transcript_stats['avg_words_per_segment']:.1f} per segment)")
    
    # STEP 4: Extract candidate moments or use auto-generation
    logger.step(4 + step_offset, 10 + step_offset, "Analyzing Content")
    
    if auto_mode:
        logger.info("Detecting viral moments (energy + keywords)...")
        try:
            # Use auto-generation based on energy spikes
            candidates = extract_auto_moments(
                video_path,
                transcript,
                min_length=30,
                max_length=60,
                target_clips=target_clips,
                verbose=True
            )
        except Exception as e:
            logger.warning(f"Auto-generation failed: {e}, using traditional extraction")
            candidates = extract_candidate_moments(
                transcript,
                min_length=30,
                max_length=60
            )
    else:
        try:
            candidates = extract_candidate_moments(
                transcript,
                min_length=30,
                max_length=60
            )
        except Exception as e:
            raise ClipifyError(f"Moment extraction failed: {e}")
    
    logger.success(f"Analyzed: {len(candidates)} candidates")
    
    if len(candidates) == 0:
        raise ClipifyError("No candidate moments found. Video may be too short or unsuitable.")
    
    # STEP 5: Filter with AI (skip for auto mode)
    if auto_mode:
        logger.step(5 + step_offset, 10 + step_offset, "Ranking Moments")
        filtered_moments = candidates  # Already ranked by energy/keywords
        logger.success(f"Using energy-based ranking")
    else:
        logger.step(5, 10, "Filtering with AI")
        
        try:
            filtered_moments = ai_provider.filter_moments(candidates, transcript)
        except Exception as e:
            raise ClipifyError(f"AI filtering failed: {e}")
        
        logger.success(f"Filtered: {len(filtered_moments)}/{len(candidates)} passed")
        
        if len(filtered_moments) == 0:
            raise ClipifyError("All moments rejected by AI filter. Try different content.")
    
    # STEP 6: Score and rank
    logger.step(6 + step_offset, 10 + step_offset, "Scoring Moments")
    
    if auto_mode:
        # Auto mode: moments already scored
        scored_moments = filtered_moments
        logger.info("Using energy + keyword scores")
    else:
        try:
            scored_moments = ai_provider.score_moments(filtered_moments, transcript)
        except Exception as e:
            raise ClipifyError(f"Moment scoring failed: {e}")
    
    # Quality enforcement: Only clips >= MIN_QUALITY_SCORE
    top_moments = [m for m in scored_moments if m.get('score', 0) >= MIN_QUALITY_SCORE]
    top_moments = top_moments[:min(MAX_CLIPS_PER_VIDEO, len(top_moments))]
    
    if len(top_moments) == 0:
        raise ClipifyError(
            f"No clips meet minimum quality threshold ({MIN_QUALITY_SCORE}/10). "
            f"Video unsuitable for clipping."
        )
    
    moments_stats = {
        'candidates': len(candidates),
        'filtered': len(filtered_moments),
        'scored': len(scored_moments),
        'final_clips': len(top_moments),
        'score_range': f"{top_moments[0]['score']:.1f}-{top_moments[-1]['score']:.1f}"
    }
    
    logger.success(
        f"Selected: {len(top_moments)} clips "
        f"(scores: {moments_stats['score_range']})"
    )
    
    # STEP 7: Extract video clips
    logger.step(7 + step_offset, 10 + step_offset, "Extracting Video Clips")
    
    try:
        if use_parallel:
            logger.info("Using parallel extraction (4x faster)")
            clips = extract_clips_parallel(
                video_path,
                top_moments,
                dirs["clips"],
                max_workers=4
            )
        else:
            clips = extract_clips(
                video_path,
                top_moments,
                dirs["clips"]
            )
    except Exception as e:
        raise ClipifyError(f"Clip extraction failed: {e}")
    
    logger.success(f"Extracted: {len(clips)} video clips")
    
    if len(clips) == 0:
        raise ClipifyError("Failed to extract any video clips")
    
    # STEP 8: Format for platforms
    logger.step(8 + step_offset, 10 + step_offset, "Formatting for Platforms")
    
    try:
        formatted_clips = format_clips_multi_platform(
            clips,
            top_moments,
            dirs["clips"],
            formats=output_formats
        )
    except Exception as e:
        logger.warning(f"Formatting failed: {e}")
        formatted_clips = {}
    
    total_formatted = sum(len(paths) for paths in formatted_clips.values())
    logger.success(f"Formatted: {total_formatted} clips ({', '.join(output_formats)})")
    
    # STEP 9: Captions (optional/disabled)
    logger.step(9 + step_offset, 10 + step_offset, "Skipping Captions")
    logger.info("Caption burning disabled for production quality")
    captions = []
    
    # STEP 10: Generate report and complete
    logger.step(10 + step_offset, 10 + step_offset, "Generating Report")
    
    clips_info = []
    for i, (clip_path, moment) in enumerate(zip(clips, top_moments), 1):
        clips_info.append({
            'clip_number': i,
            'filename': clip_path.name,
            'start_time': moment['start'],
            'end_time': moment['end'],
            'duration': moment['end'] - moment['start'],
            'score': moment.get('score', 0),
            'reason': moment.get('reason', 'N/A')
        })
    
    report_path = save_processing_report(
        dirs,
        video_url,
        video_info,
        transcript_stats,
        moments_stats,
        clips_info
    )
    
    logger.success(f"Report saved: {report_path.name}")
    
    # Return results
    results = {
        'success': True,
        'output_dir': dirs['root'],
        'clips': clips,
        'formatted_clips': formatted_clips,
        'moments': top_moments,
        'video_info': video_info,
        'transcript_stats': transcript_stats,
        'moments_stats': moments_stats,
        'report_path': report_path
    }
    
    return results


def main():
    """Main entry point"""
    logger = Logger()

    if len(sys.argv) < 2:
        logger.error("Usage: python clipify.py [<YOUTUBE_URL> | --watch | --batch | --show-providers] [OPTIONS]")
        logger.info("")
        logger.info("MODES:")
        logger.info("  <URL>     : Process single video")
        logger.info("  --watch   : Watch input/ folder and auto-process videos (daemon)")
        logger.info("  --batch   : Process all pending videos in input/ folder")
        logger.info("  --show-providers : Show available AI providers and their status")
        logger.info("")
        logger.info("OPTIONS:")
        logger.info("  --auto           : Use auto-generation (energy + keywords, no API needed)")
        logger.info("  --provider NAME  : Choose AI provider (groq, gemini, openai, deepseek, local)")
        logger.info("  --clips N        : Number of clips to generate (5-10, default: 8)")
        logger.info("  --parallel       : Use parallel extraction (default: enabled)")
        logger.info("  --no-parallel    : Disable parallel extraction")
        logger.info("  --formats FMT    : Output formats: 9:16,16:9,1:1 (default: 9:16,16:9)")
        logger.info("  --input DIR      : Input folder for batch/watch (default: input/)")
        logger.info("  --output DIR     : Output folder (default: output/)")
        logger.info("")
        logger.info("PROVIDERS:")
        logger.info("  groq       - ⚡⚡⚡ Ultra-fast, FREE, recommended")
        logger.info("  deepseek   - ⚡⚡⚡ Ultra-fast, ULTRA-CHEAP")
        logger.info("  gemini     - ⚡⚡ Fast, FREE tier available")
        logger.info("  openai     - ⚡ Fast, PAID, highest quality")
        logger.info("  local      - ⚡⚡ Fast, FREE, no API key needed")
        logger.info("")
        logger.info("EXAMPLES:")
        logger.info("  python clipify.py https://youtube.com/watch?v=xyz --auto --clips 10")
        logger.info("  python clipify.py https://youtube.com/watch?v=xyz --provider groq")
        logger.info("  python clipify.py https://youtube.com/watch?v=xyz --provider deepseek")
        logger.info("  python clipify.py https://youtube.com/watch?v=xyz --provider local")
        logger.info("  python clipify.py --show-providers  # Check available API providers")
        logger.info("  python clipify.py --watch --auto  # Monitor input/ folder")
        logger.info("  python clipify.py --batch --provider openai")
        sys.exit(1)

    # Parse arguments
    mode = sys.argv[1]
    use_parallel = True
    output_formats = ["9:16", "16:9"]
    auto_mode = False
    target_clips = DEFAULT_AUTO_CLIPS
    input_dir = "input"
    output_dir = "output"
    provider_name = None
    
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--auto':
            auto_mode = True
        elif arg == '--no-parallel':
            use_parallel = False
        elif arg == '--parallel':
            use_parallel = True
        elif arg == '--clips' and i + 1 < len(sys.argv):
            try:
                target_clips = min(10, max(5, int(sys.argv[i + 1])))
            except ValueError:
                pass
        elif arg == '--provider' and i + 1 < len(sys.argv):
            provider_name = sys.argv[i + 1].lower()
        elif arg == '--formats' and i + 1 < len(sys.argv):
            output_formats = sys.argv[i + 1].split(',')
        elif arg == '--input' and i + 1 < len(sys.argv):
            input_dir = sys.argv[i + 1]
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]

    try:
        # Mode 0: Show provider status
        if mode == '--show-providers':
            from ai.provider_selector import show_provider_status
            show_provider_status(logger)
            sys.exit(0)
        
        # Mode 1: Process single video
        elif not mode.startswith('--'):
            video_url = mode
            results = process_video(
                video_url,
                logger,
                use_parallel=use_parallel,
                output_formats=output_formats,
                auto_mode=auto_mode,
                target_clips=target_clips,
                provider_name=provider_name
            )
            
            # Display summary
            logger.header("✅ CLIPIFY COMPLETE")
            logger.info(f"Output directory: {results['output_dir']}")
            logger.info(f"Total clips: {len(results['clips'])}")
            logger.info(f"Formatted variants: {sum(len(p) for p in results['formatted_clips'].values())}")
            logger.info(f"Formats: {', '.join(results['formatted_clips'].keys())}")
            logger.info(f"Processing report: {results['report_path']}")
            
            # Show clip details
            logger.header("CLIP DETAILS")
            for i, moment in enumerate(results['moments'], 1):
                logger.info(
                    f"Clip {i}: {moment['start']:.1f}s-{moment['end']:.1f}s "
                    f"(score: {moment.get('score', 0):.1f}/10)"
                )
            
            sys.exit(0)
        
        # Mode 2: Batch processing
        elif mode == '--batch':
            logger.header("BATCH PROCESSING MODE")
            
            workflow = create_folder_workflow(
                input_dir=input_dir,
                output_dir=output_dir,
                logger=logger
            )
            
            def process_func(video_path, log):
                return process_video(
                    str(video_path),
                    log,
                    use_parallel=use_parallel,
                    output_formats=output_formats,
                    auto_mode=auto_mode,
                    target_clips=target_clips,
                    provider_name=provider_name
                )
            
            results = workflow.process_batch(process_func)
            
            # Export manifest
            manifest_path = workflow.export_manifest()
            logger.success(f"Manifest saved: {manifest_path}")
            
            # Save status
            status_path = workflow.save_status()
            logger.success(f"Status saved: {status_path}")
            
            sys.exit(0)
        
        # Mode 3: Watch folder (daemon)
        elif mode == '--watch':
            logger.header("FOLDER WATCH MODE")
            
            workflow = create_folder_workflow(
                input_dir=input_dir,
                output_dir=output_dir,
                logger=logger
            )
            
            def process_func(video_path, log):
                return process_video(
                    str(video_path),
                    log,
                    use_parallel=use_parallel,
                    output_formats=output_formats,
                    auto_mode=auto_mode,
                    target_clips=target_clips,
                    provider_name=provider_name
                )
            
            workflow.process_watch(
                process_func,
                poll_interval=10,
                max_workers=1
            )
            
            sys.exit(0)
        
        else:
            logger.error(f"Unknown mode: {mode}")
            sys.exit(1)

    except ClipifyError as e:
        logger.error(f"Clipify Error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.error("\n⚠️  Operation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error("\nTraceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()