"""
Clipify - AI-Powered Viral Clip Generator
Main entry point for the application

Workflow:
1. Download video from YouTube or use local video
2. Transcribe video to text
3. Extract viral moments using AI/traditional methods
4. Generate clips from extracted moments
5. Create multiple format versions (9:16, 16:9, etc.)
6. Generate VTT captions for clips
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Import project modules
from utils.config import Config
from utils.logger import Logger
from utils.errors import ClipifyError, ValidationError
from ai.provider_selector import select_provider

from core.downloader import download_video
from core.transcriber import transcribe_video
from core.clip_processor import extract_clips
from core.formatter import format_clips_multi_platform

from moments.extractor import extract_auto_moments
from moments.scorer import score_and_rank_moments

from captions.generator import generate_vtt_captions


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

VALID_FORMATS = {"9:16", "16:9", "1:1", "4:5"}
VALID_QUALITIES = {"low", "medium", "high"}
VALID_PROVIDERS = {
    "openrouter",
    "groq",
    "deepseek",
    "openai",
    "anthropic",
    "gemini",
    "local",
    "xai",
}


def setup_argparse() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Clipify - AI-Powered Viral Clip Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and process YouTube video
  python clipify.py --url https://youtube.com/watch?v=... --output clips

  # Process local video
  python clipify.py --video local_video.mp4 --output clips

  # Watch folder for new videos
  python clipify.py --watch input_folder --output output_folder

  # Custom processing with AI selection
  python clipify.py --video video.mp4 --ai groq --clips 20
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--url",
        type=str,
        help="YouTube video URL to download and process",
    )
    input_group.add_argument(
        "--video",
        type=str,
        help="Local video file path",
    )
    input_group.add_argument(
        "--watch",
        type=str,
        help="Directory path to watch for new videos",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=str(Config.DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {Config.DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--clips",
        type=int,
        default=Config.DEFAULT_CLIP_COUNT,
        help=f"Number of clips to extract (default: {Config.DEFAULT_CLIP_COUNT})",
    )

    parser.add_argument(
        "--formats",
        nargs="+",
        default=Config.DEFAULT_FORMATS,
        help=f"Video formats to generate (default: {Config.DEFAULT_FORMATS})",
    )

    parser.add_argument(
        "--quality",
        type=str,
        choices=list(VALID_QUALITIES),
        default=Config.VIDEO_QUALITY,
        help=f"Video quality (default: {Config.VIDEO_QUALITY})",
    )

    parser.add_argument(
        "--no-captions",
        action="store_true",
        help="Skip VTT caption generation",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--cookies",
        type=str,
        help="Path to cookies.txt file for YouTube authentication",
    )

    parser.add_argument(
        "--ai",
        type=str,
        choices=sorted(VALID_PROVIDERS),
        default=None,
        help="Preferred AI provider (default: auto-select, openrouter is primary)",
    )

    parser.add_argument(
        "--anti-hallucination",
        action="store_true",
        help="Enable anti-hallucination mode (forces local provider, conservative processing)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.1",
    )

    return parser


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def validate_inputs(args: argparse.Namespace, logger: Logger) -> Dict[str, Any]:
    """Validate CLI arguments and build the runtime configuration dict.

    Args:
        args: Parsed argument namespace.
        logger: Logger instance.

    Returns:
        Runtime configuration dictionary.

    Raises:
        ValidationError: If any argument is invalid.
    """
    # Validate clip count
    if args.clips < 1:
        raise ValidationError("--clips must be at least 1")
    if args.clips > 100:
        raise ValidationError("--clips must not exceed 100")

    # Validate formats
    formats = args.formats or Config.DEFAULT_FORMATS
    for fmt in formats:
        if fmt not in VALID_FORMATS:
            raise ValidationError(
                f"Invalid format '{fmt}'. Valid: {', '.join(sorted(VALID_FORMATS))}"
            )

    # Validate cookies path (existence check happens in main)
    cookies_path: Optional[Path] = None
    if args.cookies:
        cookies_path = Path(args.cookies)

    # Build config
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    anti_hallucination = args.anti_hallucination or os.getenv(
        "ANTI_HALLUCINATION", ""
    ).lower() in ("1", "true", "yes", "on")

    config: Dict[str, Any] = {
        "output_dir": output_dir,
        "clip_count": args.clips,
        "min_length": Config.MIN_CLIP_LENGTH,
        "max_length": Config.MAX_CLIP_LENGTH,
        "formats": formats,
        "quality": args.quality,
        "generate_captions": not args.no_captions,
        "verbose": args.verbose,
        "cookies": cookies_path,
        "ai_provider": args.ai,
        "anti_hallucination": anti_hallucination,
    }

    return config


# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------


def process_video(
    video_path: Path,
    config: Dict[str, Any],
    logger: Logger,
) -> Dict[str, Any]:
    """Run the full video processing pipeline on a local file.

    Args:
        video_path: Path to video file.
        config: Runtime configuration dictionary.
        logger: Logger instance.

    Returns:
        Results dictionary with keys ``video_path``, ``clips``,
        ``moments``, ``transcript``, and ``errors``.
    """
    results: Dict[str, Any] = {
        "video_path": str(video_path),
        "clips": [],
        "moments": [],
        "transcript": None,
        "errors": [],
    }

    try:
        logger.info(f"🎬 Starting processing: {video_path.name}")

        # ------------------------------------------------------------------
        # Step 1: Transcribe video
        # ------------------------------------------------------------------
        logger.info("📝 Transcribing video...")
        try:
            provider = config.get("provider_instance") or config.get("ai_provider")
            transcript = transcribe_video(video_path, provider=provider)
            results["transcript"] = transcript
            logger.success(f"Transcription complete ({len(transcript)} segments)")
        except Exception as exc:
            results["errors"].append(f"Transcription failed: {exc}")
            logger.error(f"Transcription error: {exc}")
            return results

        # ------------------------------------------------------------------
        # Step 2: Extract moments
        # ------------------------------------------------------------------
        logger.info("🎯 Extracting viral moments...")
        try:
            moments = extract_auto_moments(
                video_path=video_path,
                transcript=transcript,
                min_length=config["min_length"],
                max_length=config["max_length"],
                target_clips=config["clip_count"],
                verbose=config["verbose"],
            )
            logger.success(f"Moment extraction: {len(moments)} moments found")
            results["moments"] = moments
        except Exception as exc:
            results["errors"].append(f"Moment extraction failed: {exc}")
            logger.error(f"Moment extraction error: {exc}")
            return results

        if not moments:
            logger.warning("No moments extracted from video")
            return results

        # ------------------------------------------------------------------
        # Step 3: Provider-specific filtering + scoring
        # ------------------------------------------------------------------
        provider_instance = config.get("provider_instance")
        if provider_instance and hasattr(provider_instance, "filter_moments"):
            try:
                filtered = provider_instance.filter_moments(moments, transcript)
                if filtered:
                    moments = filtered
                    logger.success(
                        f"Filtered moments using {getattr(provider_instance, 'name', 'provider')}"
                    )
            except Exception as exc:
                logger.warning(f"Provider filtering failed: {exc}")

        logger.info("⭐ Scoring moments...")
        try:
            if provider_instance and hasattr(provider_instance, "score_moments"):
                moments = provider_instance.score_moments(moments, transcript)
                logger.success(
                    f"Scored moments with {getattr(provider_instance, 'name', 'provider')}"
                )
            else:
                moments = score_and_rank_moments(moments, transcript)
                logger.success("Moments scored and ranked")
        except Exception as exc:
            logger.warning(f"Moment scoring failed: {exc}")

        # ------------------------------------------------------------------
        # Step 4: Extract clips
        # ------------------------------------------------------------------
        logger.info("✂️  Extracting clips...")
        clips_dir = config["output_dir"] / "clips"
        clips_dir.mkdir(exist_ok=True)
        try:
            clip_paths = extract_clips(
                video_path=video_path,
                moments=moments[: config["clip_count"]],
                output_dir=clips_dir,
                quality=config["quality"],
            )
            results["clips"] = [str(p) for p in clip_paths]
            logger.success(f"Extracted {len(clip_paths)} clips")
        except Exception as exc:
            results["errors"].append(f"Clip extraction failed: {exc}")
            logger.error(f"Clip extraction error: {exc}")
            return results

        # ------------------------------------------------------------------
        # Step 5: Format clips
        # ------------------------------------------------------------------
        if config["formats"] and clip_paths:
            logger.info(f"🎨 Formatting clips ({', '.join(config['formats'])})...")
            try:
                formatted_results = format_clips_multi_platform(
                    clip_paths=clip_paths,
                    moments=moments[: config["clip_count"]],
                    output_base_dir=config["output_dir"] / "formatted",
                    formats=config["formats"],
                )
                total_formatted = sum(len(v) for v in formatted_results.values())
                logger.success(f"Formatted {total_formatted} clips")
            except Exception as exc:
                logger.warning(f"Clip formatting failed: {exc}")

        # ------------------------------------------------------------------
        # Step 6: Generate VTT captions
        # ------------------------------------------------------------------
        if config["generate_captions"] and clip_paths:
            logger.info("📝 Generating VTT captions...")
            caption_count = 0
            for i, (clip_path, moment) in enumerate(
                zip(clip_paths[: config["clip_count"]], moments[: config["clip_count"]]),
                1,
            ):
                try:
                    caption_file = Path(clip_path).with_suffix(".vtt")
                    clip_start = moment.get("start", 0.0)
                    result = generate_vtt_captions(
                        video_path=Path(clip_path),
                        transcript=transcript,
                        output_path=caption_file,
                        clip_start=clip_start,
                    )
                    if result:
                        caption_count += 1
                        logger.debug(f"Generated captions for clip {i}")
                except Exception as exc:
                    logger.warning(f"Caption generation failed for clip {i}: {exc}")
            if caption_count:
                logger.success(f"Generated {caption_count} VTT caption files")

        logger.success("Processing complete!")
        return results

    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        results["errors"].append(f"Unexpected error: {exc}")
        return results


def process_youtube_url(
    url: str,
    config: Dict[str, Any],
    logger: Logger,
) -> Dict[str, Any]:
    """Download a YouTube video and run the processing pipeline.

    Args:
        url: YouTube video URL.
        config: Runtime configuration dictionary.
        logger: Logger instance.

    Returns:
        Results dictionary (same structure as :func:`process_video`).
    """
    logger.info(f"📥 Downloading video from: {url}")

    download_dir = config["output_dir"] / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)

    try:
        use_cookies = bool(config.get("cookies"))
        video_path = download_video(url, download_dir, use_cookies=use_cookies)
        logger.success(f"Video downloaded: {video_path}")
        return process_video(video_path, config, logger)
    except Exception as exc:
        logger.error(f"YouTube download failed: {exc}")
        return {"clips": [], "moments": [], "transcript": None, "errors": [str(exc)]}


def watch_folder(
    folder_path: Path,
    config: Dict[str, Any],
    logger: Logger,
) -> None:
    """Watch a folder and process new video files as they appear.

    Runs until interrupted with Ctrl-C.  Uses a *seen* set to avoid
    re-processing files.  Files that fail are still added to the seen
    set to prevent infinite retry loops.

    Args:
        folder_path: Directory to monitor.
        config: Runtime configuration dictionary.
        logger: Logger instance.

    Raises:
        ValidationError: If folder_path does not exist or is not a directory.
    """
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValidationError(
            f"Watch folder not found or not a directory: {folder_path}"
        )

    logger.info(f"👁️  Watching folder: {folder_path}")
    seen_files: set = set()

    try:
        while True:
            for path in sorted(folder_path.iterdir()):
                if not path.is_file():
                    continue
                if path in seen_files:
                    continue
                if path.suffix.lower() not in Config.SUPPORTED_VIDEO_EXTENSIONS:
                    continue

                # Mark as seen immediately to prevent concurrent re-processing
                seen_files.add(path)
                logger.info(f"🔎 New video detected: {path.name}")
                try:
                    process_video(path, config, logger)
                    logger.success(f"Processed {path.name}")
                except Exception as exc:
                    logger.error(f"Failed to process {path.name}: {exc}")

            time.sleep(Config.POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Folder watcher stopped.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Initialise logger with verbose flag before anything else
    logger = Logger(verbose=args.verbose)

    try:
        # Validate cookies path early to give a clear error
        if args.cookies:
            cookies_path = Path(args.cookies)
            if not cookies_path.exists():
                raise ValidationError(f"Cookies file not found: {cookies_path}")

        # Validate all inputs
        config = validate_inputs(args, logger)
        logger.success("Configuration validated")

        # Select AI provider
        provider_instance = select_provider(
            args.ai,
            logger,
            safe_mode=config.get("anti_hallucination", False),
        )
        config["provider_instance"] = provider_instance

        # Dispatch to the appropriate mode
        results: Dict[str, Any]
        if args.url:
            results = process_youtube_url(args.url, config, logger)
        elif args.video:
            video_path = Path(args.video)
            if not video_path.exists():
                raise ValidationError(f"Video file not found: {video_path}")
            if not video_path.is_file():
                raise ValidationError(f"Path is not a file: {video_path}")
            results = process_video(video_path, config, logger)
        else:  # --watch
            watch_folder(Path(args.watch), config, logger)
            results = {"moments": [], "clips": [], "errors": []}

        # Print results summary
        errors = results.get("errors", [])
        if errors:
            logger.error("Processing completed with errors:")
            for err in errors:
                logger.error(f"  - {err}")

            # Provide YouTube auth hint when relevant
            error_text = " ".join(str(e) for e in errors).lower()
            if any(kw in error_text for kw in ("bot", "sign in", "authentication")):
                logger.info("\n💡 YouTube authentication required!")
                logger.info("   Run: python get_youtube_cookies.py")
                logger.info("   Then: python clipify.py --url ... --cookies cookies.txt")

        logger.info("Results:")
        logger.info(f"  - Moments extracted: {len(results.get('moments', []))}")
        logger.info(f"  - Clips generated:   {len(results.get('clips', []))}")
        logger.info(f"  - Output directory:  {config['output_dir']}")

    except ValidationError as exc:
        logger.error(f"Validation error: {exc}")
        sys.exit(1)
    except ClipifyError as exc:
        logger.error(f"Error: {exc}")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
