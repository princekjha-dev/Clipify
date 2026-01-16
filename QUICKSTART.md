# Clipify Enhanced - Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure ffmpeg is installed
ffmpeg -version
```

---

## 🚀 Quick Examples

### 1. Auto-Generate Clips from Single Video

**Fastest way to generate 8 viral clips automatically:**

```bash
python clipify.py "video.mp4" --auto --clips 8
```

What happens:
- ✓ Analyzes audio energy spikes
- ✓ Detects viral keywords in transcript
- ✓ Scores moments by viral potential
- ✓ Generates 8 clips automatically
- ✓ Saves to `output/[timestamp]/`

**Result**: Done in 2-5 minutes (no API calls!)

---

### 2. Batch Process Entire Folder

**Drop videos in a folder, auto-process all:**

```bash
# Add videos to input/ folder, then:
python clipify.py --batch --auto --clips 8
```

What happens:
- Finds all videos in `input/`
- Processes each video sequentially
- Saves clips to `output/[video_name]/`
- Generates `manifest.json` with all clips

**Result**: All videos processed automatically

---

### 3. Daemon Mode (Continuous Processing)

**Monitor folder continuously, process videos as added:**

```bash
python clipify.py --watch --auto
```

What happens:
- Watches `input/` folder continuously
- Auto-processes any new videos
- Runs forever (Ctrl+C to stop)
- Perfect for automated workflows

**Result**: Drop video → Get clips (automated!)

---

## 📊 Features

### Multi-Format Output

Generate clips in multiple aspect ratios:

```bash
python clipify.py "video.mp4" --auto --formats 9:16,16:9,1:1
```

### Custom Clip Count

Adjust number of clips (5-10 range):

```bash
python clipify.py "video.mp4" --auto --clips 10
```

### Custom Folders

Use different input/output locations:

```bash
python clipify.py --batch --auto --input ./videos --output ./clips
```

---

## 🔍 How It Works

### Energy + Keywords Analysis

```
Video Audio
    ↓
Energy Spike Detection (finds intense moments)
    ↓
Keyword Scanning (finds viral words)
    ↓
Hook Analysis (checks opening strength)
    ↓
Combined Scoring (0-10 viral potential)
    ↓
Top 8-10 Selected → Extract Clips
```

### Detected Viral Keywords

- **Emotional**: amazing, incredible, shocking, crazy, insane
- **Action**: crashed, exploded, destroyed, succeeded, failed
- **Revelation**: secret, exposed, truth, never knew, turns out
- **Data**: percentages, large numbers (100%, 5x, etc.)
- **Hooks**: "what if", "imagine", "have you ever"

---

## 📁 Output Structure

```
output/
├── 20260115_224425/  (timestamp)
│   ├── clips/
│   │   ├── 9_16/          (portrait format)
│   │   │   ├── clip_01.mp4
│   │   │   ├── clip_02.mp4
│   │   │   └── ...
│   │   ├── 16_9/          (landscape format)
│   │   └── 1_1/           (square format)
│   ├── reports/
│   │   └── processing_report.json
│   ├── captions/
│   ├── timestamps/
│   └── temp/
```

**When using `--batch`:**
```
output/
├── video1/
│   ├── clip_01.mp4
│   ├── clip_02.mp4
│   └── ...
├── video2/
│   ├── clip_01.mp4
│   └── ...
└── manifest.json  (all clips index)
```

---

## ⚙️ Configuration

### Default Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Auto Clips Target | 8 | Generate 8 clips by default |
| Min Clip Length | 30s | Minimum clip duration |
| Max Clip Length | 60s | Maximum clip duration |
| Quality Score | 6.5/10 | Minimum quality threshold |
| Output Formats | 9:16, 16:9 | Default aspect ratios |

### Customize in Python

```python
from pathlib import Path
from clipify import process_video
from utils.logger import Logger

logger = Logger()

# Process with custom settings
results = process_video(
    "video.mp4",
    logger,
    auto_mode=True,        # Use energy + keywords
    target_clips=10,       # Generate 10 clips
    use_parallel=True,     # Fast extraction
    output_formats=["9:16", "1:1"]  # Portrait + square only
)
```

---

## 🎯 Use Cases

### Content Creator
```bash
python clipify.py "latest_podcast.mp4" --auto
# Get 8 TikTok-ready clips automatically
```

### Batch Processing
```bash
python clipify.py --batch --auto
# Process entire week's videos at once
```

### Automated Workflow
```bash
python clipify.py --watch --auto
# Server continuously uploads clips to platform
```

### Quality Control
```bash
python clipify.py "video.mp4" --auto --clips 15
# Generate more clips for manual selection
```

---

## 🐛 Troubleshooting

### Issue: "numpy is required"
**Solution:**
```bash
pip install numpy
```

### Issue: "ffmpeg not found"
**Solution:**
```bash
# Windows (using winget)
winget install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg
```

### Issue: No energy spikes detected
**Solution:** Video may be too quiet or not suitable for auto-generation. Try:
```bash
python clipify.py "video.mp4" --auto
# Will fall back to traditional extraction
```

### Issue: Wrong folder location
**Solution:** Use absolute paths:
```bash
python clipify.py --batch --input "C:\Users\me\videos" --output "C:\Users\me\clips"
```

---

## 📈 Performance

| Operation | Time | Requirements |
|-----------|------|--------------|
| Single video (1 hour) | 2-5 min | 2GB RAM, CPU |
| Batch (5 videos) | 10-25 min | 2GB RAM, CPU |
| Energy detection | ~1x duration | CPU |
| Multi-threshold silence | ~3x duration | CPU |
| Clip extraction | ~0.5x duration | CPU/SSD |

---

## 🔗 Documentation

- **Detailed Docs**: See [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)
- **API Reference**: See module docstrings in code
- **Examples**: See section below

---

## 📚 More Examples

### Python API

```python
from pathlib import Path
from moments.energy_analyzer import (
    detect_energy_spikes,
    combine_energy_and_keywords,
    get_top_viral_moments
)

# Low-level API
video_path = Path("video.mp4")
spikes = detect_energy_spikes(video_path, verbose=True)
combined = combine_energy_and_keywords(spikes, transcript)
best = get_top_viral_moments(combined, count=10)

for moment in best:
    print(f"{moment.start:.1f}s: {moment.viral_score:.1f}/10")
```

### Folder Workflow API

```python
from core.folder_watcher import create_folder_workflow
from clipify import process_video
from utils.logger import Logger

logger = Logger()
workflow = create_folder_workflow("input", "output", logger=logger)

# Process batch
def my_processor(video_path, log):
    return process_video(
        str(video_path),
        log,
        auto_mode=True,
        target_clips=8
    )

results = workflow.process_batch(my_processor)

# Export results
workflow.export_manifest()
```

### Multi-Threshold Silence

```python
from audio_analysis.silence_detector import (
    detect_multi_threshold_silence,
    recommend_threshold
)
from pathlib import Path

# Analyze at multiple levels
results = detect_multi_threshold_silence(
    Path("video.mp4"),
    thresholds=[-30, -40, -50]
)

# Get recommendation
threshold, reason = recommend_threshold(
    results,
    video_duration=300,
    target_silence_ratio=0.20
)

print(f"Use: {threshold}dB - {reason}")
```

---

## 🎓 Next Steps

1. **Try it**: `python clipify.py "your_video.mp4" --auto`
2. **Explore**: Check output in `output/` folder
3. **Customize**: Adjust `--clips` and `--formats` as needed
4. **Automate**: Use `--watch` for production workflows
5. **Learn**: Read [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) for deep dive

---

## ✨ Features Summary

| Feature | Status | Speed |
|---------|--------|-------|
| Auto-generate clips | ✅ NEW | Fast |
| Energy spike detection | ✅ NEW | Fast |
| Viral keyword scanning | ✅ NEW | Fast |
| Multi-threshold silence | ✅ ENHANCED | Medium |
| Folder watch mode | ✅ NEW | Ongoing |
| Batch processing | ✅ NEW | Medium |
| Format conversion | ✅ Existing | Fast |
| AI filtering | ✅ Existing | Slow |

---

## 💡 Tips & Tricks

- **Fast testing**: Use `--clips 5` for quicker processing
- **High quality**: Use `--clips 12` for more options to choose from  
- **Square clips**: Add `--formats 1:1` for Instagram Reels
- **All formats**: Use `--formats 9:16,16:9,1:1` for maximum coverage
- **Quiet start**: First run may take longer (caching audio)

---

**Questions?** Check the full docs in [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) or examine the code comments!
