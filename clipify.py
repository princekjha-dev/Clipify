"""
Clipify - AI-Powered Viral Clip Generator
Main entry point for the application

Workflow:
1. Download video from YouTube or use local video
2. Transcribe video to text
3. Extract viral moments using AI/traditional methods
4. Generate clips from extracted moments
5. Create multiple format versions (9:16, 16:9, etc.)
6. Generate captions for clips
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Import project modules
from utils.config import Config
from utils.logger import Logger
from utils.errors import ClipifyError


class ValidationError(ClipifyError):
    """Validation error for input parameters"""
    pass

from core.downloader import download_video
from core.transcriber import transcribe_video
from core.clip_processor import extract_clips
from core.formatter import format_clips_multi_platform

from moments.extractor import extract_auto_moments
from moments.scorer import score_and_rank_moments

from captions.generator import generate_captions


# Setup logger
logger = Logger()


def setup_argparse() -> argparse.ArgumentParser:
    """Setup command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Clipify - AI-Powered Viral Clip Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and process YouTube video
  python main.py --url https://youtube.com/watch?v=... --output clips

  # Process local video
  python main.py --video local_video.mp4 --output clips

  # Watch folder for new videos
  python main.py --watch input_folder --output output_folder

  # Custom processing with AI selection
  python main.py --video video.mp4 --ai groq --clips 20
        """
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--url",
        type=str,
        help="YouTube video URL to download and process"
    )
    input_group.add_argument(
        "--video",
        type=str,
        help="Local video file path"
    )
    input_group.add_argument(
        "--watch",
        type=str,
        help="Directory path to watch for new videos"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=Config.DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {Config.DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--clips",
        type=int,
        default=Config.DEFAULT_CLIP_COUNT,
        help=f"Number of clips to extract (default: {Config.DEFAULT_CLIP_COUNT})"
    )
    
    parser.add_argument(
        "--formats",
        nargs="+",
        default=Config.DEFAULT_FORMATS,
        help=f"Video formats to generate (default: {Config.DEFAULT_FORMATS})"
    )
    
    parser.add_argument(
        "--quality",
        type=str,
        choices=["low", "medium", "high"],
        default=Config.VIDEO_QUALITY,
        help=f"Video quality (default: {Config.VIDEO_QUALITY})"
    )
    
    parser.add_argument(
        "--captions",
        action="store_true",
        default=True,
        help="Generate captions for clips"
    )
    
    parser.add_argument(
        "--no-captions",
        action="store_true",
        help="Skip caption generation"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--cookies",
        type=str,
        help="Path to cookies.txt file for YouTube authentication"
    )

    parser.add_argument(
        "--ai",
        type=str,
        choices=["openrouter", "groq", "deepseek", "openai", "anthropic", "gemini", "local"],
        default=None,
        help="Preferred AI provider (default auto-select, openrouter is primary)"
    )
    
    return parser


def validate_inputs(args: argparse.Namespace, logger: Logger) -> Dict[str, Any]:
    """Validate and prepare input parameters"""
    config = {
        "output_dir": Path(args.output),
        "clip_count": args.clips,
        "min_length": Config.MIN_CLIP_LENGTH,
        "max_length": Config.MAX_CLIP_LENGTH,
        "formats": args.formats or Config.DEFAULT_FORMATS,
        "quality": args.quality,
        "generate_captions": not args.no_captions,
        "verbose": args.verbose,
        "cookies": Path(args.cookies) if args.cookies else None,
        "ai_provider": args.ai,
    }
    
    # Validate clip count
    if config["clip_count"] < 1:
        raise ValidationError("Clip count must be at least 1")
    
    if config["clip_count"] > 100:
        raise ValidationError("Clip count should not exceed 100")
    
    # Create output directory
    config["output_dir"].mkdir(parents=True, exist_ok=True)
    
    return config


def process_video(video_path: Path, config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """
    Main video processing pipeline
    
    Args:
        video_path: Path to video file
        config: Configuration dictionary
        logger: Logger instance
        
    Returns:
        Processing results
    """
    results = {
        "video_path": str(video_path),
        "clips": [],
        "moments": [],
        "transcript": None,
        "errors": [],
    }
    
    try:
        logger.info(f"🎬 Starting processing: {video_path.name}")
        
        # Step 1: Transcribe video
        logger.info("📝 Transcribing video...")
        try:
            provider = config.get('ai_provider')
            transcript = transcribe_video(video_path, provider=provider)
            results["transcript"] = transcript
            logger.success(f"Transcription complete ({len(transcript)} segments)")
        except Exception as e:
            results["errors"].append(f"Transcription failed: {str(e)}")
            logger.error(f"Transcription error: {e}")
            return results
        
        # Step 2: Extract moments
        logger.info("🎯 Extracting viral moments...")
        try:
            moments = extract_auto_moments(
                video_path=video_path,
                transcript=transcript,
                min_length=config["min_length"],
                max_length=config["max_length"],
                target_clips=config["clip_count"],
                verbose=config["verbose"]
            )
            logger.success(f"Moment extraction: {len(moments)} moments found")
            
            results["moments"] = moments
            
        except Exception as e:
            results["errors"].append(f"Moment extraction failed: {str(e)}")
            logger.error(f"Moment extraction error: {e}")
            return results
        
        if not moments:
            logger.warning("No moments extracted from video")
            return results
        
        # Step 3: Score and rank moments
        logger.info("⭐ Scoring moments...")
        try:
            scored_moments = score_and_rank_moments(moments)
            moments = sorted(scored_moments, key=lambda x: x.get('score', 0), reverse=True)
            logger.success("Moments scored and ranked")
        except Exception as e:
            logger.warning(f"Moment scoring failed: {e}")
        
        # Step 4: Extract clips
        logger.info("✂️  Extracting clips...")
        try:
            clips_dir = config["output_dir"] / "clips"
            clips_dir.mkdir(exist_ok=True)
            
            clip_paths = extract_clips(
                video_path=video_path,
                moments=moments[:config["clip_count"]],
                output_dir=clips_dir,
                quality=config["quality"]
            )
            
            results["clips"] = [str(clip) for clip in clip_paths]
            logger.success(f"Extracted {len(clip_paths)} clips")
            
        except Exception as e:
            results["errors"].append(f"Clip extraction failed: {str(e)}")
            logger.error(f"Clip extraction error: {e}")
            return results
        
        # Step 5: Format clips
        if config["formats"]:
            logger.info(f"🎨 Formatting clips ({', '.join(config['formats'])})...")
            try:
                formatted_results = format_clips_multi_platform(
                    clip_paths=clip_paths,
                    moments=moments[:config["clip_count"]],
                    output_base_dir=config["output_dir"] / "formatted",
                    formats=config["formats"]
                )
                
                total_formatted = sum(len(v) for v in formatted_results.values())
                logger.success(f"Formatted {total_formatted} clips")
            except Exception as e:
                logger.warning(f"Clip formatting failed: {e}")
        
        # Step 6: Generate captions
        if config["generate_captions"]:
            logger.info("📝 Generating captions...")
            try:
                for i, clip_path in enumerate(clip_paths[:5]):  # First 5 clips
                    caption_file = Path(clip_path).with_suffix('.vtt')
                    captions = generate_captions(
                        video_path=Path(clip_path),
                        transcript=transcript,
                        output_path=caption_file
                    )
                    logger.success(f"Generated captions for clip {i+1}")
            except Exception as e:
                logger.warning(f"Caption generation failed: {e}")
        
        logger.success("Processing complete!")
        return results
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        results["errors"].append(f"Unexpected error: {str(e)}")
        return results


def process_youtube_url(url: str, config: Dict[str, Any], logger: Logger) -> Dict[str, Any]:
    """Download and process YouTube video"""
    try:
        logger.info(f"📥 Downloading video from: {url}")

        # Download video
        download_dir = config["output_dir"] / "downloads"
        download_dir.mkdir(parents=True, exist_ok=True)

        use_cookies = bool(config.get("cookies"))
        video_path = download_video(url, download_dir, use_cookies=use_cookies)

        logger.success(f"Video downloaded: {video_path}")

        # Process the downloaded video
        return process_video(video_path, config, logger)
        
    except Exception as e:
        logger.error(f"YouTube download failed: {e}")
        return {"errors": [str(e)]}


def watch_folder(folder_path: Path, config: Dict[str, Any], logger: Logger) -> None:
    """Watch folder for new videos and process them"""
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValidationError(f"Watch folder not found or not a directory: {folder_path}")

    logger.info(f"👁️  Watching folder: {folder_path}")
    seen_files = set()

    while True:
        for path in folder_path.iterdir():
            if not path.is_file():
                continue

            if path in seen_files:
                continue

            if path.suffix.lower() not in Config.SUPPORTED_VIDEO_EXTENSIONS:
                continue

            logger.info(f"🔎 New video detected: {path.name}")
            try:
                process_video(path, config, logger)
                seen_files.add(path)
                logger.success(f"Processed {path.name}")
            except Exception as e:
                logger.error(f"Failed to process {path.name}: {e}")

        time.sleep(Config.POLL_INTERVAL_SECONDS)


def main():
    """Main entry point"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Create logger with verbose setting
    logger_instance = Logger()
    
    try:
        # Handle cookies if provided
        if args.cookies:
            cookies_path = Path(args.cookies)
            if not cookies_path.exists():
                raise ValidationError(f"Cookies file not found: {cookies_path}")
            
            # Copy cookies to current directory for yt-dlp to find
            import shutil
            dest_cookies = Path.cwd() / "cookies.txt"
            shutil.copy(cookies_path, dest_cookies)
            logger_instance.success(f"Loaded cookies from: {cookies_path}")
        
        # Validate inputs
        config = validate_inputs(args, logger_instance)
        logger_instance.success("Configuration validated")
        
        # Route to appropriate processing mode
        if args.url:
            results = process_youtube_url(args.url, config, logger_instance)
            
        elif args.video:
            video_path = Path(args.video)
            if not video_path.exists():
                raise ValidationError(f"Video file not found: {video_path}")
            results = process_video(video_path, config, logger_instance)

        elif args.watch:
            watch_folder(Path(args.watch), config, logger_instance)
            results = {"moments": [], "clips": [], "errors": []}
        
        # Print results summary
        if results and "errors" in results:
            if results["errors"]:
                logger_instance.error("Processing completed with errors:")
                for error in results["errors"]:
                    logger_instance.error(f"  - {error}")
                
                # Check if it's a YouTube auth error and provide help
                error_text = " ".join(str(e) for e in results["errors"]).lower()
                if "bot" in error_text or "sign in" in error_text or "authentication" in error_text:
                    logger_instance.info("\n💡 YouTube authentication required!")
                    logger_instance.info("   Run: python get_youtube_cookies.py")
                    logger_instance.info("   Then: python main.py --url ... --cookies cookies.txt")
            
            logger_instance.info("Results:")
            logger_instance.info(f"  - Moments extracted: {len(results.get('moments', []))}")
            logger_instance.info(f"  - Clips generated: {len(results.get('clips', []))}")
            logger_instance.info(f"  - Output directory: {config['output_dir']}")
        
    except ValidationError as e:
        logger_instance.error(f"Validation error: {e}")
        sys.exit(1)
    except ClipifyError as e:
        logger_instance.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger_instance.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
