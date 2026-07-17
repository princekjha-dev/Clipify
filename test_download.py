"""
Simple YouTube downloader test script
Useful for testing download functionality without running full pipeline
"""

import sys
import argparse
from pathlib import Path

from core.downloader import download_video


def main():
    """Test download functionality"""
    parser = argparse.ArgumentParser(
        description="Test YouTube download",
        epilog="""
Examples:
  python test_download.py --url https://www.youtube.com/watch?v=... --output downloads
  python test_download.py --url https://www.youtube.com/watch?v=... --cookies /path/to/cookies.txt
        """
    )
    
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="YouTube video URL"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="downloads",
        help="Output directory (default: downloads)"
    )
    
    parser.add_argument(
        "--cookies",
        type=str,
        help="Path to cookies.txt file"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle cookies if provided
    if args.cookies:
        cookies_source = Path(args.cookies)
        cookies_dest = Path.cwd() / "cookies.txt"
        
        if not cookies_source.exists():
            print(f"❌ Cookies file not found: {cookies_source}")
            sys.exit(1)
        
        # Only copy if source and destination are different
        if cookies_source.resolve() != cookies_dest.resolve():
            import shutil
            shutil.copy(cookies_source, cookies_dest)
            print(f"OK: Copied cookies to: {cookies_dest}")
        else:
            print(f"OK: Cookies already in place: {cookies_dest}")
    
    try:
        print(f"📥 Downloading: {args.url}")
        print(f"📁 Output directory: {output_dir}")
        
        video_path = download_video(args.url, output_dir)
        
        print(f"\n✅ Download successful!")
        print(f"📄 File: {video_path}")
        print(f"📊 Size: {video_path.stat().st_size / (1024**2):.2f} MB")
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print(f"\n💡 Need help? Run: python get_youtube_cookies.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
