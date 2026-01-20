cfh
## ✨ Key Features

- 🎥 **Automatic Video Clipping** - Extract engaging moments from long-form videos using AI
- 🧠 **AI-Powered Analysis** - Transcription via OpenAI Whisper + scoring via multiple AI providers
- 🎯 **Smart Filtering** - Removes weak hooks, silence, and improper word cuts
- 📱 **Multi-Platform Support** - Auto-formats for TikTok, Instagram Reels, YouTube Shorts (9:16, 16:9, 1:1, 4:5)
- 🌐 **YouTube Integration** - Direct YouTube URL support via yt-dlp
- 🤖 **Multi-AI Provider Support** - Choose from Groq, DeepSeek, OpenAI, or Local processing
- 📊 **Explainable Scores** - Understand why each clip was selected
- 🔄 **Batch Processing** - Process multiple videos automatically
- 📁 **Folder Watch Mode** - Monitor folder for new videos and auto-process

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/princekjha-dev/clipify.git
cd clipify

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (optional - see options below)
```

### Process Your First Video

```bash
# Process a YouTube video
python clipify.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

# Process a local video file
python clipify.py "path/to/your/video.mp4"

# View all available options
python clipify.py --help
```

## 🤖 AI Provider Options

Clipify supports multiple AI providers. Choose the one that works best for you:

| Provider | Speed | Cost | Quality | Setup |
|----------|-------|------|---------|-------|
| **Groq** ⭐ | ⚡⚡⚡ Fastest | 🆓 FREE | 90% | 2 min |
| **DeepSeek** | ⚡⚡⚡ Fastest | 💰 Ultra-cheap | 88% | 2 min |
| **OpenAI** | ⚡ Moderate | 💳 Paid | 95% | 3 min |
| **Local** | ⚡⚡ Fast | 🆓 FREE | 85% | 0 min |

### Setup Your AI Provider

#### 1. Groq (Recommended - FREE)
```bash
# 1. Go to https://console.groq.com/keys
# 2. Create API key
# 3. Add to .env:
GROQ_API_KEY=your_key_here

# Test it:
python clipify.py "video.mp4" --provider groq
```

#### 2. DeepSeek (Ultra-cheap)
```bash
# 1. Go to https://platform.deepseek.com/api_keys
# 2. Create API key
# 3. Add to .env:
DEEPSEEK_API_KEY=your_key_here

# Test it:
python clipify.py "video.mp4" --provider deepseek
```

#### 3. OpenAI (Best Quality)
```bash
# 1. Go to https://platform.openai.com/api/keys
# 2. Create API key
# 3. Add to .env:
OPENAI_API_KEY=your_key_here

# Test it:
python clipify.py "video.mp4" --provider openai
```

#### 4. Local (No API needed)
```bash
# Uses local Whisper model - no API key required
python clipify.py "video.mp4" --provider local
```

### Check Available Providers
```bash
python clipify.py --show-providers
```

Output:
```
PROVIDER STATUS
  ✓ Groq (Free & Fast)
  ⚠ DeepSeek (no API key set)
  ✓ OpenAI (Paid)
  ℹ Local Processing (No API needed)
```

## 📖 Usage Examples

### Process Single Video
```bash
python clipify.py "path/to/video.mp4"
python clipify.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Process with Specific Provider
```bash
python clipify.py "video.mp4" --provider groq
python clipify.py "video.mp4" --provider openai
```

### Control Output Format
```bash
# Generate 10 clips in TikTok format (9:16)
python clipify.py "video.mp4" --clips 10 --formats 9:16

# Multiple formats for different platforms
python clipify.py "video.mp4" --formats 9:16,16:9,1:1
```

### Batch Processing
```bash
# Process all videos in folder
python clipify.py --batch --input ./videos --provider groq
```

### Watch Folder for New Videos
```bash
# Monitor folder and auto-process new videos
python clipify.py --watch --input ./videos --provider groq
```

## 📁 Output Structure

```
output/
├── 20260116_150320/              # Timestamp folder
│   ├── clips/
│   │   ├── clip_01_9x16.mp4      # TikTok/Reels format
│   │   ├── clip_02_16x9.mp4      # YouTube format
│   │   └── ...
│   ├── captions/
│   │   ├── clip_01.srt
│   │   └── clip_02.srt
│   ├── timestamps/
│   │   └── metadata.json
│   ├── reports/
│   │   └── analysis.json
│   └── temp/                      # Temporary files
```

## 🏗️ Project Structure

```
clipify/
├── core/                          # Core video processing
│   ├── downloader.py              # YouTube/file download
│   ├── transcriber.py             # Audio transcription
│   ├── clip_processor.py          # FFmpeg operations
│   └── formatter.py               # Multi-platform formatting
├── moments/                       # Moment extraction & scoring
│   ├── extractor.py               # Find candidate moments
│   ├── filter.py                  # Smart filtering
│   └── scorer.py                  # AI quality scoring
├── audio_analysis/
│   └── silence_detector.py        # Silence detection
├── alignment/
│   └── word_aligner.py            # Word-level timestamps
├── text_signals/
│   ├── hook_detector.py           # Hook detection
│   └── statement_analyzer.py      # Content analysis
├── captions/
│   └── generator.py               # Caption generation
├── ai/                            # AI provider abstraction
│   ├── provider_selector.py       # Provider selection
│   ├── groq_provider.py           # Groq integration
│   ├── deepseek_provider.py       # DeepSeek integration
│   ├── openai_provider.py         # OpenAI integration
│   └── local_provider.py          # Local processing
├── utils/
│   ├── logger.py                  # Logging
│   ├── errors.py                  # Error handling
│   └── healthcheck.py             # Health checks
├── clipify.py                     # Main entry point
└── requirements.txt               # Dependencies
```

## 🔧 Configuration

### Command-Line Options

```bash
python clipify.py --help

Options:
  FILE                    Video file or YouTube URL
  --provider PROVIDER     AI provider (groq, deepseek, openai, local)
  --show-providers        Show available AI providers
  --clips N               Number of clips to extract (default: 8)
  --min-length SEC        Minimum clip length (default: 15)
  --max-length SEC        Maximum clip length (default: 60)
  --formats FORMATS       Output formats (9:16,16:9,1:1,4:5)
  --batch                 Batch mode - process folder
  --input DIR             Input directory for batch mode
  --watch                 Watch folder for new videos
  --output DIR            Output directory (default: output/)
```

### Environment Variables

Create `.env` file in project root:

```env
# AI Providers (choose at least one)
GROQ_API_KEY=your_groq_key
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_API_KEY=your_openai_key

# Optional: YouTube (for private videos)
YOUTUBE_EMAIL=your_email
YOUTUBE_PASSWORD=your_password

# Optional: Processing
FFmpeg_PATH=/path/to/ffmpeg
```

## 🧠 How It Works

```
Input Video
    ↓
[1] Download/Load Video
    ↓
[2] Extract Audio & Transcribe (Whisper)
    ↓
[3] Extract Candidate Moments
    - Energy peaks
    - Speech patterns
    - Silence breaks
    ↓
[4] Apply Filters
    - Remove weak hooks
    - Check duration
    - Validate word boundaries
    ↓
[5] Score with AI
    - Engagement potential
    - Topic quality
    - Hook strength
    ↓
[6] Format for Multiple Platforms
    - 9:16 (TikTok/Reels)
    - 16:9 (YouTube)
    - 1:1 (Instagram Square)
    - 4:5 (Instagram Story)
    ↓
[7] Generate Captions
    ↓
Output Clips
```

## 📊 Performance

- **Processing Time**: 2-5 minutes per hour of video (depends on provider)
- **Quality**: 1080p @ 30fps with automatic audio normalization
- **Accuracy**: 85-95% depending on AI provider
- **Batch Mode**: Process multiple videos sequentially

## 🔍 Troubleshooting

### No provider available
```
Error: No AI provider available

Solutions:
1. Check .env file for API keys
2. Run: python clipify.py --show-providers
3. Set up at least one AI provider (Groq recommended)
```

### FFmpeg not found
```
Error: ffmpeg not found in PATH

Solution: Install from https://ffmpeg.org/download.html
- Windows: Download from website or use: choco install ffmpeg
- Mac: brew install ffmpeg
- Linux: sudo apt-get install ffmpeg
```

### Out of quota
```
Error: API quota exceeded

Solutions:
1. Switch to different provider (e.g., --provider groq)
2. Wait for quota reset (usually monthly)
3. Consider paid tier for higher limits
```

### Video processing fails
```
Error: Failed to process video

Solutions:
1. Check video format is supported (MP4, MKV, MOV)
2. Ensure FFmpeg can read the file
3. Check disk space for temporary files
4. Try with smaller video or specific --max-length
```

## 💡 Tips & Best Practices

1. **Start with Groq** - It's free and fast, perfect for testing
2. **Use batch mode** for multiple videos to save API calls
3. **Monitor clips folder** - Videos auto-refresh as processing completes
4. **Adjust --clips parameter** - More clips = more API calls
5. **Test with --provider local** first to see if content works
6. **Check timestamp folder** for detailed analysis and reports

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech-to-text
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Groq](https://console.groq.com/) - Fast LLM inference
- [DeepSeek](https://platform.deepseek.com/) - Cost-effective LLM
- [OpenAI](https://openai.com/) - GPT models

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/princekjha-dev/clipify/issues)
- **Discussions**: [GitHub Discussions](https://github.com/princekjha-dev/clipify/discussions)

---

**Made with ❤️ for content creators**

