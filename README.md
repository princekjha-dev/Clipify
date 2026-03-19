# Clipify - AI-Powered Viral Clip Generator

A powerful Python application that automatically extracts viral moments from videos and generates multi-format clips optimized for social media.

## Features

- 🎬 **YouTube Download** - Download videos with automatic authentication handling
- 📝 **Auto Transcription** - Transcribe videos using Whisper API or local models
- 🎯 **Viral Moment Detection** - AI-powered detection of viral moments in videos
- ✂️ **Clip Extraction** - Fast stream-copy based clip extraction (no re-encoding)
- 🎨 **Multi-Format Generation** - Generate clips in multiple aspect ratios (9:16, 16:9, etc.)
- 📊 **Moment Scoring** - Automatic ranking of moments by viral potential
- 📝 **Caption Generation** - Auto-generate captions for accessibility

## Quick Start

### 1. Installation

**Option A: Install from source**
```bash
# Clone or download the repository
git clone https://github.com/princekjha-dev/Clipify.git
cd clipify

# Install dependencies
pip install -r requirements.txt
```

**Option B: Install as package**
```bash
# Install directly from source
pip install .
# Or for development
pip install -e .
```

### 2. Get YouTube Cookies (if downloading from YouTube)

YouTube requires authentication. Get cookies with this helper script:

```bash
python get_youtube_cookies.py
```

Follow the on-screen instructions to:
1. Install the browser extension
2. Export YouTube cookies
3. Save as `cookies.txt`

### 3. Basic Usage

**Process a local video:**
```bash
python clipify.py --video my_video.mp4 --output clips
```

**Download and process a YouTube video:**
```bash
python clipify.py --url https://www.youtube.com/watch?v=... --output clips --cookies cookies.txt
```

**Test YouTube download:**
```bash
python test_download.py --url https://www.youtube.com/watch?v=... --output downloads
```

## Advanced Usage

### Options

```
--url URL                 YouTube video URL
--video VIDEO            Local video file path
-o, --output OUTPUT      Output directory (default: output)
--clips CLIPS            Number of clips to extract (default: 50)
--formats FORMATS        Video formats: 9:16 16:9 1:1 (default: 9:16 16:9)
--quality QUALITY        Video quality: low/medium/high (default: high)
--ai AI_PROVIDER         AI provider: groq, deepseek, openai, anthropic, gemini, local
--captions               Generate captions (default: enabled)
--no-captions            Skip caption generation
--cookies COOKIES        Path to cookies.txt for YouTube auth
--verbose                Enable verbose logging
```

### Examples

```bash
# Download YouTube video with specific settings
python clipify.py --url "https://youtube.com/watch?v=..." \
  --output clips \
  --clips 20 \
  --quality high \
  --formats 9:16 16:9 1:1 \
  --cookies cookies.txt

# Process local video with verbose output
python clipify.py --video podcast.mp4 --output clips --clips 15 --verbose

# Generate without captions for faster processing
python clipify.py --video video.mp4 --output clips --no-captions

# Test if cookies work
python test_download.py --url "https://youtube.com/watch?v=..." \
  --output downloads \
  --cookies cookies.txt
```

## Project Structure

```
clipify/
├── ai/                    # AI provider integrations (Groq, OpenAI, etc.)
├── alignment/             # Word alignment for captions
├── audio_analysis/        # Audio processing and analysis
├── captions/              # Caption generation
├── core/                  # Core functionality
│   ├── downloader.py     # YouTube/video downloads
│   ├── transcriber.py    # Video transcription
│   ├── clip_processor.py # Clip extraction
│   └── formatter.py      # Multi-format conversion
├── moments/               # Moment detection and scoring
├── text_signals/          # Text analysis
├── utils/                 # Utilities and configuration
├── clipify.py            # Main entry point
├── get_youtube_cookies.py # Helper to get cookies
└── test_download.py      # Test download functionality
```

## Configuration

Edit `utils/config.py` to customize:

```python
# Default clip count
DEFAULT_CLIP_COUNT = 50

# Clip length constraints (seconds)
MIN_CLIP_LENGTH = 25
MAX_CLIP_LENGTH = 50
TARGET_CLIP_LENGTH = 35

# Output formats
DEFAULT_FORMATS = ["9:16", "16:9"]

# Video quality
VIDEO_QUALITY = "high"  # low, medium, high
```

## Troubleshooting

### YouTube Authentication Error

If you get "Sign in to confirm you're not a bot" error:

```bash
# Step 1: Get cookies
python get_youtube_cookies.py

# Step 2: Run with cookies
python clipify.py --url "https://youtube.com/watch?v=..." --cookies cookies.txt
```

### Transcription Fails

Make sure you have:
- OpenAI API key set in environment: `OPENAI_API_KEY`
- Or install local Whisper: `pip install openai-whisper`

### Slow Clip Extraction

- Use `--no-captions` to skip caption generation
- Reduce `--clips` count
- Use `--quality low` for faster processing

### FFmpeg Not Found

Install FFmpeg:
- Windows: `choco install ffmpeg` or download from ffmpeg.org
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## Environment Variables

```bash
# OpenAI/Whisper API
OPENAI_API_KEY=sk_...

# Alternative AI providers
GROQ_API_KEY=gsk_...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
```

## Performance Tips

1. **Faster Processing**: Skip captions with `--no-captions`
2. **Lower Quality**: Use `--quality low` for faster extraction
3. **Fewer Clips**: Reduce `--clips` count
4. **Parallel Processing**: System uses all CPU cores by default

## Output Structure

```
output/
├── downloads/           # Downloaded videos
├── clips/              # Extracted clips
├── formatted/
│   ├── 9x16/          # Clips in 9:16 aspect ratio
│   └── 16x9/          # Clips in 16:9 aspect ratio
└── metadata/          # JSON metadata about moments
```

## API Keys

For AI-powered moment extraction, get API keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **Groq**: https://console.groq.com
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **OpenRouter**: https://openrouter.ai/keys

## Limitations

- YouTube downloads require valid cookies due to anti-bot protection
- Age-restricted videos may fail without proper authentication
- Large videos may take significant time to process
- Transcription accuracy depends on audio quality and language

## Contributing

Contributions welcome! Areas for improvement:
- Additional AI provider integrations
- Better moment detection algorithms
- More output format options
- Batch processing improvements

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Run `python test_download.py` to test downloads
3. Run `python get_youtube_cookies.py` for authentication help
4. Check logs with `--verbose` flag
