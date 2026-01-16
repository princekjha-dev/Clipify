import os
from pathlib import Path
from typing import Optional
import yt_dlp
import time
import json
import tempfile


def download_video(url: str, output_dir: Path, use_cookies: bool = False) -> Path:
    """
    Download YouTube video to local storage

    Args:
        url: YouTube video URL
        output_dir: Directory to save video
        use_cookies: Use cookies for authentication (default: False)

    Returns:
        Path to downloaded video file
    """
    output_template = str(output_dir / "video.%(ext)s")

    # Base options - try with ipv6 disabled first to avoid some bot detection
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'merge_output_format': 'mp4',
        'socket_timeout': 30,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'prefer_free_formats': False,
    }

    # Setup cookies
    cookies_file = None
    if use_cookies:
        cookies_file = _setup_cookies()
        if cookies_file:
            ydl_opts['cookiefile'] = str(cookies_file)

    # Retry logic for bot detection
    max_retries = 2
    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # Handle cases where format might not be mp4
                if not filename.endswith('.mp4'):
                    filename = filename.rsplit('.', 1)[0] + '.mp4'

                video_path = Path(filename)

                if not video_path.exists():
                    raise FileNotFoundError(f"Downloaded file not found: {video_path}")

                return video_path

        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a bot detection error
            if "sign in to confirm you're not a bot" in error_msg or "bot" in error_msg:
                if attempt < max_retries - 1:
                    print(f"  ⚠️  Bot detection triggered, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    # Final attempt failed - provide helpful message
                    print(f"  ⚠️  YouTube is blocking automated downloads (bot detection)")
                    print(f"  💡 Solutions:")
                    print(f"     1. Export YouTube cookies: https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies")
                    print(f"     2. Place cookies.json in project root")
                    print(f"     3. Try downloading with a browser first, then use local file")
                    raise RuntimeError("YouTube bot detection - please see solutions above")
            
            # Other errors
            raise RuntimeError(f"Failed to download video: {e}")
    
    raise RuntimeError("Failed to download video after retries")


def _setup_cookies() -> Optional[Path]:
    """
    Setup cookies for YouTube authentication
    
    Looks for cookies in multiple locations:
    1. ~/.config/yt-dlp/cookies.txt (standard location)
    2. Current directory/cookies.json (JSON format)
    3. Current directory/example.cookies.json (JSON format)
    
    Returns:
        Path to cookies file or None if not found
    """
    # Check standard yt-dlp location
    standard_cookies = Path.home() / '.config' / 'yt-dlp' / 'cookies.txt'
    if standard_cookies.exists():
        return standard_cookies
    
    # Check for JSON cookies in current/project directory
    json_cookie_locations = [
        Path.cwd() / 'cookies.json',
        Path(__file__).parent.parent / 'cookies.json',
    ]
    
    for json_file in json_cookie_locations:
        if json_file.exists():
            try:
                # Convert JSON cookies to Netscape format for yt-dlp
                txt_file = _convert_json_cookies_to_txt(json_file)
                if txt_file:
                    return txt_file
            except Exception as e:
                print(f"  ⚠️  Failed to load cookies from {json_file}: {e}")
    
    return None


def _convert_json_cookies_to_txt(json_file: Path) -> Optional[Path]:
    """
    Convert JSON format cookies to Netscape cookies.txt format for yt-dlp
    
    Args:
        json_file: Path to JSON cookies file
        
    Returns:
        Path to temporary Netscape format cookies file or None if conversion failed
    """
    try:
        with open(json_file, 'r') as f:
            cookies = json.load(f)
        
        if not isinstance(cookies, list):
            return None
        
        # Create temp file with Netscape format
        fd, temp_path = tempfile.mkstemp(suffix='.txt', prefix='yt_dlp_cookies_')
        
        with os.fdopen(fd, 'w') as f:
            # Netscape cookies.txt header
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# Generated by clipify\n\n")
            
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = 'TRUE' if cookie.get('httpOnly', False) else 'FALSE'
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                
                # Handle expires - convert negative or missing values to 0
                expires_raw = cookie.get('expires', 0)
                try:
                    expires = int(expires_raw)
                    # Convert negative values to 0 (session cookie)
                    if expires < 0:
                        expires = 0
                except (ValueError, TypeError):
                    expires = 0
                
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                # Skip empty cookies
                if not name or not domain:
                    continue
                
                # Netscape format: domain flag path secure expiration name value
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        
        return Path(temp_path)
    
    except Exception as e:
        print(f"  ⚠️  Failed to convert JSON cookies: {e}")
        return None


def get_video_info(url: str) -> dict:
    """
    Get video metadata without downloading

    Args:
        url: YouTube video URL

    Returns:
        Dictionary with video metadata
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0)
            }
    except Exception as e:
        print(f"Warning: Could not extract video info: {e}")
        return {}
