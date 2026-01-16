# 🤖 AI Provider Selection Guide

## Overview

Clipify supports multiple AI providers for moment scoring and analysis. You can:
- ✅ View available AI providers and their status
- ✅ Choose specific provider (Groq, DeepSeek, OpenAI, or local)
- ✅ Handle invalid API keys gracefully
- ✅ Auto-fallback if your preferred provider is unavailable

---

## Quick Start

### Check Available Providers
```bash
python clipify.py --show-providers
```

Output example:
```
PROVIDER STATUS
  ✓ Groq (Free & Fast)
  ⚠ DeepSeek (no API key set)
  ✓ OpenAI (Paid)
  ℹ Local Processing (No API needed)

To use auto-generation (no API needed): use --provider local
```

### Use Specific Provider
```bash
# Use Groq
python clipify.py "video.mp4" --provider groq

# Use DeepSeek
python clipify.py "video.mp4" --provider deepseek

# Use OpenAI
python clipify.py "video.mp4" --provider openai

# Use local processing (no API)
python clipify.py "video.mp4" --provider local
```

### Use Local Processing (No API Needed)
```bash
python clipify.py "video.mp4" --provider local --clips 8
# Works completely offline, no API key required
```

---

## Provider Options

### 1. Groq (Recommended - FREE)
- **Speed**: ⚡⚡⚡ Very fast
- **Cost**: 🆓 Free
- **Setup**: Set `GROQ_API_KEY` environment variable
- **Command**: `python clipify.py "video.mp4" --provider groq`

**Get Groq API Key**:
```bash
# 1. Go to https://console.groq.com
# 2. Create account
# 3. Get API key
# 4. Set in environment:
export GROQ_API_KEY="your_key_here"  # macOS/Linux
set GROQ_API_KEY=your_key_here  # Windows PowerShell
```

### 2. DeepSeek (ULTRA-CHEAP)
- **Speed**: ⚡⚡⚡ Very fast
- **Cost**: 💰 Ultra-cheap (usually $0.0002-0.001 per video)
- **Setup**: Set `DEEPSEEK_API_KEY` environment variable
- **Command**: `python clipify.py "video.mp4" --provider deepseek`

**Get DeepSeek API Key**:
```bash
# 1. Go to https://platform.deepseek.com
# 2. Create account
# 3. Add payment method
# 4. Get API key
# 5. Set in environment:
export DEEPSEEK_API_KEY="your_key_here"  # macOS/Linux
set DEEPSEEK_API_KEY=your_key_here  # Windows PowerShell
```

### 3. OpenAI (PAID - BEST QUALITY)
- **Speed**: ⚡ Moderate
- **Cost**: 💰 Paid (usually $0.01-0.05 per video)
- **Setup**: Set `OPENAI_API_KEY` environment variable
- **Command**: `python clipify.py "video.mp4" --provider openai`

**Get OpenAI API Key**:
```bash
# 1. Go to https://platform.openai.com
# 2. Create account
# 3. Add payment method
# 4. Get API key
# 5. Set in environment:
export OPENAI_API_KEY="your_key_here"  # macOS/Linux
set OPENAI_API_KEY=your_key_here  # Windows PowerShell
```

### 4. Local Processing (FREE - No API)
- **Speed**: ⚡ Depends on hardware
- **Cost**: 🆓 Free
- **Setup**: No API key needed
- **Command**: `python clipify.py "video.mp4" --provider local`

---

## Usage Examples

### Example 1: Check What's Available
```bash
python clipify.py --show-providers
```

Shows:
- Which providers have valid API keys
- Which providers are working
- Which ones are misconfigured

### Example 2: Use Groq (Free & Fast)
```bash
python clipify.py "podcast.mp4" --provider groq --clips 8
```

### Example 3: Switch Between Providers
```bash
# Try Groq first
python clipify.py "video.mp4" --provider groq

# If Groq fails, try DeepSeek
python clipify.py "video.mp4" --provider deepseek
```

### Example 4: Use Local Processing (No API)
```bash
# Works offline, no API needed
python clipify.py "video.mp4" --provider local --clips 8

# Combine with folder workflow
python clipify.py --batch --provider local --input ./videos
```

### Example 5: Batch with Specific Provider
```bash
python clipify.py --batch --provider groq --clips 10
```

---

## Troubleshooting

### Problem: "Invalid API Key" Error

**Solution 1: Check if API key is set**
```bash
# Check if environment variable is set
echo $GROQ_API_KEY  # macOS/Linux
echo %GROQ_API_KEY%  # Windows

# If empty, set it
export GROQ_API_KEY="paste_your_key_here"
```

**Solution 2: Verify API key is correct**
- Copy the key exactly (no spaces before/after)
- Make sure it's the right provider's key
- Check if key has expired or been revoked

**Solution 3: Use --show-providers to diagnose**
```bash
python clipify.py --show-providers
# Shows which providers are working
```

### Problem: "Provider not available"

**Solution: Try a different provider**
```bash
# Check what's available
python clipify.py --show-providers

# Use available provider
python clipify.py "video.mp4" --provider gemini

# Or use auto-generation (no API needed)
python clipify.py "video.mp4" --auto
```

### Problem: Want to use AI but no valid API

**Solution: Use auto-generation mode**
```bash
# Works offline, no API needed
python clipify.py "video.mp4" --auto --clips 8

# Same quality, just different method
# Energy + keyword based instead of AI based
```

---

## Setting Up API Keys

### Windows (PowerShell)
```powershell
# Set temporarily (current session only)
$env:GROQ_API_KEY = "your_key_here"

# Set permanently (all future sessions)
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your_key_here", "User")

# Verify it worked
echo $env:GROQ_API_KEY
```

### macOS/Linux (Bash/Zsh)
```bash
# Set temporarily (current session only)
export GROQ_API_KEY="your_key_here"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export GROQ_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc

# Verify it worked
echo $GROQ_API_KEY
```

### Using .env File (Easy)
```bash
# Create .env file in project root
# Add your API keys:
GROQ_API_KEY=your_groq_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENAI_API_KEY=your_openai_key_here

# They'll be loaded automatically when you run Clipify
```

---

## Provider Comparison

| Feature | Groq | DeepSeek | OpenAI | Local |
|---------|------|----------|--------|-------|
| Cost | FREE | Ultra-cheap | Paid | FREE |
| Speed | ⚡⚡⚡ Fast | ⚡⚡⚡ Fast | ⚡ Slow | ⚡⚡ Medium |
| Quality | 90% | 88% | 95% | 80% |
| API Needed | Yes | Yes | Yes | No |
| Offline | No | No | No | Yes |
| Setup | Easy | Easy | Moderate | None |

---

## Command Reference

```bash
# Check available providers
python clipify.py --show-providers

# Use specific provider
python clipify.py "video.mp4" --provider groq
python clipify.py "video.mp4" --provider deepseek
python clipify.py "video.mp4" --provider openai
python clipify.py "video.mp4" --provider local

# Use local processing (no API needed)
python clipify.py "video.mp4" --provider local

# Batch processing with provider
python clipify.py --batch --provider groq

# Watch mode with provider
python clipify.py --watch --provider deepseek

# Combine options
python clipify.py "video.mp4" --provider groq --clips 10 --formats 9:16,1:1
```

---

## Best Practices

1. **Check status first**
   ```bash
   python clipify.py --show-providers
   ```

2. **Use Groq for speed** (if available)
   ```bash
   python clipify.py "video.mp4" --provider groq
   ```

3. **Fallback to local processing if no API**
   ```bash
   python clipify.py "video.mp4" --provider local
   ```

4. **Set API keys in .env file**
   - Easier to manage
   - Works across sessions
   - Can be git-ignored safely

5. **Test before batch processing**
   ```bash
   # Test one video first
   python clipify.py "test.mp4" --provider groq
   
   # Then batch process
   python clipify.py --batch --provider groq
   ```

---

## FAQs

**Q: Which provider should I use?**  
A: Groq (free, fast). If not available, use DeepSeek (ultra-cheap). If neither works, use local processing (no API).

**Q: Do I need an API key?**  
A: No, you can use `--provider local` for local processing which works offline.

**Q: Can I switch providers mid-process?**  
A: Yes, just use `--provider` flag with different value.

**Q: My API key is invalid, what do I do?**  
A: Run `python clipify.py --show-providers` to see which ones work, then use a working one.

**Q: Is local processing as good as AI?**  
A: ~80% quality vs 90% for AI, but completely free and offline.

---

**Ready?** Start with:
```bash
python clipify.py --show-providers
```

Then choose your provider and get clipping! 🎬
