# Clipify - AI-Powered Viral Clip Generator

![Clipify logo](src/logo.png)

A powerful Python application that automatically extracts viral moments from videos and generates multi-format clips optimized for social media.

## Features

- 🎬 **YouTube Download** - Download videos with automatic authentication handling
- 📝 **Auto Transcription** - Transcribe videos using Whisper API or local models
- 🎯 **Viral Moment Detection** - AI-powered detection of viral moments in videos
- ✂️ **Clip Extraction** - Fast stream-copy based clip extraction (no re-encoding)
- 🎨 **Multi-Format Generation** - Generate clips in multiple aspect ratios (9:16, 16:9, etc.)
- 📊 **Moment Scoring** - Automatic ranking of moments by viral potential
- 📝 **Caption Generation** - Auto-generate captions for accessibility

## System Requirements

- **Python**: 3.8 or higher
- **FFmpeg**: Required for video processing
- **OS**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB+ recommended for smooth processing)
- **Disk Space**: At least 2GB free for processing and output

## Quick Start

### ⚡ Automated Setup (Recommended)

**Windows:**
```batch
# Run setup script
setup.bat
```

**macOS/Linux:**
```bash
# Run setup script
chmod +x setup.sh
./setup.sh
```

### Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/princekjha-dev/Clipify.git
cd Clipify-main
```

#### Step 2: Create Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

# If PowerShell blocks Activate.ps1, use one of these:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1

# Or run Python directly without activating:
.venv\Scripts\python.exe clipify.py --help
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Install FFmpeg

**Windows (Easiest - No Admin Required):**
```powershell
# Run this in PowerShell
$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$outputPath = "$env:TEMP\ffmpeg.zip"
$extractPath = "C:\ffmpeg"
New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $outputPath
Expand-Archive -Path $outputPath -DestinationPath $extractPath -Force
# Add to PATH:
$env:Path += ";C:\ffmpeg"
ffmpeg -version
```

**Windows (With Chocolatey - Admin Required):**
```bash
choco install ffmpeg -y
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg -y
```

**Verify Installation:**
```bash
ffmpeg -version
```

#### Step 5: Set Up Environment Variables
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env with your keys
```

Or set environment variables directly:
```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-key-here"
$env:GROQ_API_KEY = "your-key-here"

# macOS/Linux (Bash)
export OPENAI_API_KEY="your-key-here"
export GROQ_API_KEY="your-key-here"
```

### 2. YouTube Authentication (Optional)

Only needed if you plan to download age-restricted or login-required videos:

```bash
python get_youtube_cookies.py
```

This will:
1. Open a browser window
2. Ask you to log into YouTube
3. Export cookies automatically
4. Save as `cookies.txt`

### 3. First Run

**Test with a simple local video:**
```bash
python clipify.py --video sample.mp4 --clips 5 --output test_output
```

**Download and process from YouTube:**
```bash
python clipify.py \
  --url "https://www.youtube.com/watch?v=DXVHmGoCTco" \
  --output clips \
  --clips 10 \
  --quality high
```

**Expected Output:**
```
✅ Configuration validated
ℹ️  📥 Downloading video from: https://www.youtube.com/watch?v=...
ℹ️  📝 Transcribing video...
ℹ️  🎯 Extracting moments...
ℹ️  ✂️ Generating clips...
ℹ️  📝 Adding captions...
✅ Results:
  - Moments extracted: 12
  - Clips generated: 10
  - Output directory: clips/
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

## API Keys Setup

Clipify supports multiple AI providers. Set up at least one:

### OpenAI (for GPT and Whisper)
```bash
export OPENAI_API_KEY=sk_...
```
Get key from: https://platform.openai.com/api-keys

### Groq (fast LLM inference - free tier available)
```bash
export GROQ_API_KEY=gsk_...
```
Get key from: https://console.groq.com/keys

### Google Gemini
```bash
export GEMINI_API_KEY=...
```
Get key from: https://aistudio.google.com/app/apikeys

### Anthropic Claude
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```
Get key from: https://console.anthropic.com/

### OpenRouter (aggregates multiple models)
```bash
export OPENROUTER_API_KEY=sk-or-...
```
Get key from: https://openrouter.ai/keys

## AI Providers Architecture

Clipify uses a modular provider system for flexible AI model integration. The architecture supports 13+ different AI providers.

### ✅ Supported AI Providers

#### 1. **OpenAI** (`ai/openai_provider.py`) - Industry Standard
- **Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- **Best for**: High-quality moment detection, complex reasoning
- **Cost**: $0.01-0.03 per 1K tokens
- **Setup**: `export OPENAI_API_KEY=sk_...`
- **Features**: Streaming support, function calling

#### 2. **Groq** (`ai/groq_provider.py`) - ⚡ Fastest
- **Models**: Mixtral 8x7B, LLaMA 2, Gemma
- **Best for**: Speed-critical applications, real-time processing
- **Cost**: Free tier available, then $0.27/million tokens
- **Setup**: `export GROQ_API_KEY=gsk_...`
- **Features**: 500+ tokens/sec throughput, streaming

#### 3. **Google Gemini** (`ai/gemini_provider.py`) - Multimodal
- **Models**: Gemini Pro, Gemini Pro Vision
- **Best for**: Vision tasks, multimodal analysis
- **Cost**: Free tier + paid ($0.005-0.025 per 1K)
- **Setup**: `export GEMINI_API_KEY=...`
- **Features**: Vision capabilities, 32K context

#### 4. **Anthropic Claude** (`ai/anthropic_provider.py`) - Constitutional AI
- **Models**: Claude 3 Opus, Sonnet, Haiku
- **Best for**: Nuanced reasoning, safety-focused tasks
- **Cost**: $0.003-0.024 per 1K tokens
- **Setup**: `export ANTHROPIC_API_KEY=sk-ant-...`
- **Features**: 200K context window, streaming

#### 5. **DeepSeek** (`ai/deepseek_provider.py`) - Cost-Effective
- **Models**: DeepSeek V2, DeepSeek Chat
- **Best for**: Budget-conscious deployments
- **Cost**: $0.0001-0.001 per 1K tokens
- **Setup**: `export DEEPSEEK_API_KEY=...`
- **Features**: MoE architecture, high throughput

#### 6. **OpenRouter** (`ai/openrouter_provider.py`) - LLM Aggregator
- **Models**: 150+ models (OpenAI, Claude, Mistral, etc.)
- **Best for**: Model flexibility, comparison testing
- **Cost**: Varies by model ($0.0001-0.05+ per 1K)
- **Setup**: `export OPENROUTER_API_KEY=sk-or-...`
- **Features**: Fallback handling, usage tracking

#### 7. **Mistral AI** (`ai/mistral_provider.py`) - European AI
- **Models**: Mistral Small, Medium, Large
- **Best for**: European data residency, open-source focus
- **Cost**: $0.0002-0.0015 per 1K tokens
- **Setup**: `export MISTRAL_API_KEY=...`
- **Features**: 32K context, RAG support

#### 8. **Cohere** (`ai/cohere_provider.py`) - Search & RAG
- **Models**: Command R+, Command R, Command Light
- **Best for**: Search augmented generation, structured data
- **Cost**: $0.0001-0.015 per 1K tokens
- **Setup**: `export COHERE_API_KEY=...`
- **Features**: 128K context, built-in web search

#### 9. **Together AI** (`ai/together_provider.py`) - Open-Source at Scale
- **Models**: 100+ models (Llama, Mixtral, Phi, etc.)
- **Best for**: Open-source model testing, high volume
- **Cost**: $0.0002-0.0009 per 1K tokens
- **Setup**: `export TOGETHER_API_KEY=...`
- **Features**: No rate limits, streaming

#### 10. **Fireworks AI** (`ai/fireworks_provider.py`) - Fastest Open-Source
- **Models**: Llama 2, Mistral, Phi, Code models
- **Best for**: Speed-critical open-source needs
- **Cost**: $0.00008-0.0009 per 1K tokens
- **Setup**: `export FIREWORKS_API_KEY=...`
- **Features**: Sub-second latency, streaming

#### 11. **Perplexity AI** (`ai/perplexity_provider.py`) - Web-Connected
- **Models**: Sonar Pro, Sonar Small (with/without web)
- **Best for**: Current information, real-time context
- **Cost**: $0.0003-0.015 per 1K tokens
- **Setup**: `export PERPLEXITY_API_KEY=...`
- **Features**: Real-time web search, 200K context

#### 12. **xAI (Grok)** (`ai/xai_provider.py`) - Web-Native
- **Models**: Grok-2, Grok-2 Mini, Grok-1
- **Best for**: Twitter/X data processing, real-time content
- **Cost**: $0.0005-0.01 per 1K tokens
- **Setup**: `export XAI_API_KEY=...`
- **Features**: 128K context, real-time capabilities

#### 13. **Local (Ollama)** (`ai/local_provider.py`) - Privacy-First
- **Models**: Llama 2, Mistral, Neural Chat, etc.
- **Best for**: Offline processing, privacy, no API costs
- **Cost**: Free (only hardware cost)
- **Setup**: Run `ollama pull mistral` locally
- **Features**: No external API calls, complete privacy

### 🔄 How to Switch Providers

#### Method 1: Environment Variable (Recommended)
```bash
# Set preferred provider
export AI_PROVIDER=groq      # or openai, anthropic, gemini, etc.
export GROQ_API_KEY=gsk_...

# Run clipify
python clipify.py --url https://youtube.com/watch?v=...
```

#### Method 2: Command Line Argument
```bash
python clipify.py \
  --url https://youtube.com/watch?v=... \
  --ai-provider groq \
  --ai-model mixtral-8x7b-32768
```

#### Method 3: Configuration File
```python
# utils/config.py
class Config:
    AI_PROVIDER = "groq"           # Default provider
    AI_MODEL = "mixtral-8x7b-32768"
    AI_TEMPERATURE = 0.7
```

### 📊 Provider Comparison

| Provider | Speed | Cost | Quality | Privacy | Context | Best Use |
|----------|-------|------|---------|---------|---------|----------|
| OpenAI | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 128K | General purpose |
| Groq | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 32K | Real-time |
| Claude | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 200K | Quality |
| Gemini | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | 32K | Vision tasks |
| DeepSeek | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 128K | Budget |
| Mistral | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 32K | Open-source |
| Local (Ollama) | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4K-32K | Privacy |

### 🛠️ Adding New AI Providers

1. **Create Provider File**
   ```python
   # ai/new_provider.py
   from ai.base_provider import BaseProvider
   
   class NewProvider(BaseProvider):
       def complete(self, messages, model, **kwargs):
           # Implementation
           pass
   ```

2. **Implement Abstract Methods**
   - `health_check()` - Verify API connection
   - `get_available_models()` - List models
   - `complete()` - Generate completion
   - `stream_complete()` - Streaming support
   - `count_tokens()` - Token estimation
   - `calculate_cost()` - Cost calculation

3. **Register in Provider Manager**
   ```python
   # ai/provider_manager.py
   manager.register("new_provider", NewProvider)
   ```

4. **Add API Key to .env**
   ```bash
   export NEW_PROVIDER_API_KEY=...
   ```

5. **Test Provider**
   ```python
   from ai.provider_manager import ProviderManager
   manager = ProviderManager()
   provider = manager.get_provider("new_provider")
   result = provider.complete(messages)
   ```

### ⚠️ Fallback Strategy

If your primary provider fails, Clipify automatically tries fallbacks:

```python
# Order of fallback
PROVIDER_FALLBACK_CHAIN = [
    "groq",           # Try Groq first (fastest)
    "openai",         # Then OpenAI (most reliable)
    "anthropic",      # Then Claude (best quality)
    "openrouter",     # Then OpenRouter (most options)
    "local",          # Finally local (slowest but free)
]
```

## Comprehensive Troubleshooting

### ❌ FFmpeg Not Found

**Error Message:**
```
ERROR: You have requested merging of multiple formats but ffmpeg is not installed
```

**Solutions:**

1. **Verify Installation:**
   ```bash
   ffmpeg -version
   ```

2. **Windows - Manual Download (No Admin):**
   ```powershell
   # Download latest FFmpeg
   $url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
   $out = "$env:TEMP\ffmpeg.zip"
   Invoke-WebRequest -Uri $url -OutFile $out
   Expand-Archive -Path $out -DestinationPath C:\ffmpeg -Force
   # Add to PATH or use full path in .env
   echo "FFMPEG_PATH=C:\ffmpeg\ffmpeg.exe" >> .env
   ```

3. **Windows - Using Chocolatey (Admin Only):**
   ```bash
   choco install ffmpeg -y
   ```

4. **macOS:**
   ```bash
   brew install ffmpeg
   ```

5. **Linux:**
   ```bash
   sudo apt install ffmpeg -y
   ```

### ❌ ImportError: cannot import name 'Config'

**Error Message:**
```
ImportError: cannot import name 'Config' from 'utils.config'
```

**Solution:** Ensure `utils/config.py` has the Config class wrapper (Fixed in v1.0.1)

### ❌ TypeError: Logger() takes no arguments

**Error Message:**
```
TypeError: Logger() takes no arguments
```

**Solution:** This is fixed in v1.0.1. Update your code:
```bash
git pull origin main
pip install -r requirements.txt
```

### ❌ YouTube Authentication Required

**Error Message:**
```
ERROR: Sign in to confirm you're not a bot
```

**Solution:**
```bash
# Step 1: Get cookies
python get_youtube_cookies.py

# Step 2: Use cookies when downloading
python clipify.py --url "https://youtube.com/watch?v=..." --cookies cookies.txt
```

### ❌ API Key Not Set

**Error Message:**
```
AuthenticationError: API key not found
```

**Solutions:**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."

# Windows CMD
set OPENAI_API_KEY=sk-...

# macOS/Linux
export OPENAI_API_KEY=sk-...

# Or create .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### ❌ Module Not Found: whisper/yt_dlp/etc

**Error Message:**
```
ModuleNotFoundError: No module named 'yt_dlp'
```

**Solutions:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Or install specific package
pip install yt-dlp openai-whisper

# Verify virtual environment is activated
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
```

### ❌ Video Download Fails

**Error Messages:**
```
ERROR: Unable to extract video information
ERROR: The uploader has not made this video available in your country
```

**Solutions:**
- Try with `--cookies cookies.txt`
- Use a VPN if video is region-restricted
- Check if video URL is correct
- Try simpler video first to test setup

### ❌ Slow Processing / Timeout

**Solutions:**
```bash
# Skip captions (faster)
python clipify.py --video video.mp4 --no-captions

# Lower quality
python clipify.py --video video.mp4 --quality low

# Fewer clips
python clipify.py --video video.mp4 --clips 5

# All optimizations
python clipify.py --video video.mp4 --clips 5 --quality low --no-captions
```

### ❌ Out of Memory Error

**Error:**
```
MemoryError or killed process
```

**Solutions:**
- Close other applications
- Reduce `--clips` count
- Use `--quality low`
- Process shorter videos first
- Increase virtual memory
- Upgrade to 8GB+ RAM

### ✅ Verification Checklist

Run these commands to verify setup:

```bash
# Check Python version (3.8+)
python --version

# Check FFmpeg
ffmpeg -version

# Check virtual environment
pip list | grep yt-dlp

# Test basic functionality
python -c "from utils.config import Config; print(Config.DEFAULT_CLIP_COUNT)"

# Test YouTube download capability
python test_download.py --help
```

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

## Frequently Asked Questions

### Q: How long does it take to process a video?
**A:** Depends on video length and settings:
- 10-minute video: 2-5 minutes (with captions)
- 10-minute video: 1-2 minutes (without captions)
- Processing time = transcription + moment detection + clip extraction

### Q: Can I use local video instead of YouTube?
**A:** Yes! Just use `--video` instead of `--url`:
```bash
python clipify.py --video path/to/video.mp4 --output clips
```

### Q: What video formats are supported?
**A:** MP4, MOV, MKV, AVI, WebM. Supported aspect ratios: 9:16, 16:9, 1:1, 4:3

### Q: Can I run this on CPU only?
**A:** Yes, but it's slower. GPU acceleration is optional:
- GPU: Process in minutes
- CPU: Process in 5-15 minutes

### Q: Do I need API keys?
**A:** Optional. Without API keys, uses local processing (slower but free)

### Q: Can I customize moment detection?
**A:** Yes, edit `moments/scorer.py` to adjust scoring logic

### Q: How many clips can I extract?
**A:** 1-100 clips per video. More clips = longer processing time

### Q: Can I use this commercially?
**A:** Yes, subject to license terms and compliance with YouTube's ToS

## Architecture

```
                    ┌─────────────────────┐
                    │   Input Video       │
                    │ (YouTube/Local)     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Core Downloader     │ ◄─── yt-dlp (YouTube)
                    │ (download/stream)   │      ffmpeg (merge)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Transcriber         │ ◄─── OpenAI Whisper
                    │ (speech-to-text)    │      or local model
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼────┐        ┌────────▼────────┐       ┌────▼──────┐
   │ Energy  │        │ Text Analysis   │       │ Silence    │
   │Analyzer │        │ (NLP, hooks)    │       │Detection   │
   └────┬────┘        └────────┬────────┘       └────┬───────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Moment Scorer       │ ◄─── AI Provider
                    │ (rank by virality)  │      (Groq/OpenAI)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Clip Extractor      │ ◄─── ffmpeg
                    │ (stream-copy)       │      (fast, no transcode)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Multi-Format        │ ◄─── Aspect ratios
                    │ Formatter           │      9:16, 16:9, 1:1
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Caption Generator   │ ◄─── Word alignment
                    │ (optional)          │      Pydantic validation
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Output Clips        │
                    │ (formatted/ready)   │
                    └─────────────────────┘
```

## Development Guide

### Setting Up for Development

```bash
# Clone repo
git clone https://github.com/princekjha-dev/Clipify.git
cd Clipify-main

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Install dev tools
pip install pytest black pylint
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest test_clipify.py -v
```

### Code Style

```bash
# Format code
black .

# Lint code
pylint **/*.py

# Check type hints
mypy .
```

### Adding New AI Provider

1. Create new file in `ai/` (e.g., `ai/new_provider.py`)
2. Inherit from provider base class
3. Implement `generate_moments()` method
4. Register in `ai/provider_selector.py`
5. Add API key to `.env`

### Common Module Functions

**Transcriber:**
```python
from core.transcriber import transcribe_video
transcript = transcribe_video("video.mp4")
```

**Moment Detection:**
```python
from moments.extractor import extract_auto_moments
moments = extract_auto_moments(transcript, video_path)
```

**Clip Processing:**
```python
from core.clip_processor import extract_clips
clips = extract_clips(moments, video_path)
```

**Formatting:**
```python
from core.formatter import format_clips_multi_platform
formatted = format_clips_multi_platform(clips, formats=["9:16", "16:9"])
```

## Community & Contributing

Clipify is built by and for the community. We welcome all contributions! 🎉

### 📋 Community Guidelines

Before contributing, please read:
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Community standards and expectations
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Detailed contribution guidelines
- **[SECURITY.md](SECURITY.md)** - Security reporting and practices

### 🤝 How to Contribute

1. **Report Issues**
   - Use issue templates: [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md), [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
   - Check [existing issues](https://github.com/princekjha-dev/Clipify/issues)
   - Provide clear, reproducible examples

2. **Submit Pull Requests**
   - Fork the repository
   - Create a feature branch: `git checkout -b feature/your-feature`
   - Follow [commit conventions](CONTRIBUTING.md#commit-messages)
   - Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
   - Run tests: `pytest --cov=.`
   - Format code: `black .`

3. **Improve Documentation**
   - Update README for new features
   - Add docstrings to functions
   - Enhance examples and guides
   - Fix typos and clarify explanations

4. **Add Tests**
   - Write tests for new features
   - Improve test coverage
   - Test edge cases and error scenarios

### 🎯 Areas for Contribution

- Additional AI provider integrations
- Enhanced moment detection algorithms
- More output format options
- Batch processing improvements
- Performance optimizations
- Better error handling
- Documentation improvements
- UI/UX enhancements

### 📚 Development Resources

- [Contributing Guide](CONTRIBUTING.md) - Full contribution workflow
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community standards
- [Security Policy](SECURITY.md) - Security guidelines
- [Changelog](CHANGELOG.md) - Project history

### 🐛 Found a Bug?

Create an issue using our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md):
- Describe the bug clearly
- Include reproduction steps
- Provide error messages/logs
- Note your environment

### 💡 Have an Idea?

Suggest improvements using our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md):
- Explain the use case
- Describe the solution
- Consider impact and alternatives

### 🔒 Security Concerns?

See [SECURITY.md](SECURITY.md) for responsible vulnerability disclosure:
- **Never** create public issues for security vulnerabilities
- Email maintainer with details
- Allow time for coordinated fix
- Help us keep Clipify secure

### ⭐ Getting Started with Development

```bash
# Fork and clone
git clone https://github.com/princekjha-dev/Clipify.git
cd Clipify-main

# Set up development environment
make setup  # or manual steps in CONTRIBUTING.md

# Make your changes
git checkout -b feature/your-feature

# Test your changes
pytest --cov=.
black .
pylint **/*.py

# Commit with meaningful message
git commit -m "feat: add new feature with details"

# Push and create PR
git push origin feature/your-feature
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup.

### 🏆 Recognition

Contributors are recognized in:
- [README.md](README.md) contributors section
- [CHANGELOG.md](CHANGELOG.md) release notes
- GitHub contributor graphs

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### v1.0.1 (Latest)
- ✅ 13 AI provider implementations (Mistral, Cohere, Together, Fireworks, Perplexity, xAI)
- ✅ Enterprise provider infrastructure and registry
- ✅ Comprehensive community governance (Contributing, Code of Conduct, Security)
- ✅ GitHub issue and PR templates
- ✅ 500+ lines of provider documentation
- ✅ Fixed Config class and Logger initialization

### v1.0.0
- 🎉 Initial release
- ✅ YouTube downloading
- ✅ Viral moment detection
- ✅ Multi-format clip generation
- ✅ Auto captions
- ✅ 7 AI provider integrations

## License

MIT License - See [LICENSE](LICENSE) file for details

## Support

### 📖 Documentation
- [README.md](README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

### 🆘 Get Help
1. **Troubleshooting** - See [Troubleshooting Section](#comprehensive-troubleshooting)
2. **FAQ** - See [Frequently Asked Questions](#frequently-asked-questions)
3. **Issues** - Check [GitHub Issues](https://github.com/princekjha-dev/Clipify/issues)
4. **Discussions** - Ask in [GitHub Discussions](https://github.com/princekjha-dev/Clipify/discussions)
5. **Testing** - Run `python test_download.py` to verify setup

### 📞 Contact
- **Bug Reports**: [GitHub Issues](https://github.com/princekjha-dev/Clipify/issues)
- **Features**: [GitHub Discussions](https://github.com/princekjha-dev/Clipify/discussions)
- **Security**: Email maintainer privately

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Setup environment | `python -m venv .venv` |
| Activate on Windows | `.venv\Scripts\Activate.ps1` |
| Activate on macOS/Linux | `source .venv/bin/activate` |
| Install dependencies | `pip install -r requirements.txt` |
| Process local video | `python clipify.py --video video.mp4` |
| Process YouTube | `python clipify.py --url "https://youtube.com/watch?v=..."` |
| Get YouTube cookies | `python get_youtube_cookies.py` |
| Skip captions (faster) | Add `--no-captions` flag |
| Custom output dir | `python clipify.py --video video.mp4 --output my_clips` |
| Verbose logging | Add `--verbose` flag |
| Reduce processing time | `--quality low --no-captions --clips 5` |
| List all options | `python clipify.py --help` |

## Environment Template (.env.example)

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_ORG_ID=org-your-id-here

# Alternative AI Providers
GROQ_API_KEY=gsk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GEMINI_API_KEY=your-key-here
OPENROUTER_API_KEY=sk-or-your-key-here

# FFmpeg Path (if not in system PATH)
FFMPEG_PATH=/usr/bin/ffmpeg

# OpenAI Whisper Model
WHISPER_MODEL=base  # tiny, base, small, medium, large

# Processing Settings
DEFAULT_CLIPS=10
DEFAULT_QUALITY=high
DEFAULT_FORMAT=9:16

# YouTube Settings
YOUTUBE_COOKIES_PATH=./cookies.txt

# Performance
MAX_WORKERS=4
TIMEOUT_SECONDS=300
```

Save this as `.env` and the application will automatically load these variables.

---

**Made with ❤️ by the Clipify Team**

For the latest updates and documentation, visit: https://github.com/princekjha-dev/Clipify
4. Check logs with `--verbose` flag
