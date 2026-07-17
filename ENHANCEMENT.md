# ENHANCEMENT.md — Clipify v1.0.1 Upgrade Guide

This document covers every change introduced in v1.0.1, step-by-step upgrade instructions, compatibility notes, and a developer checklist for verifying a clean deployment.

---

## What Changed in v1.0.1

| Area | Change |
|---|---|
| AI Provider Selection | Added `--ai` flag supporting eight backends: OpenRouter, Groq, DeepSeek, OpenAI, Anthropic, Gemini, xAI, and local |
| Safe Mode | Added `--anti-hallucination` flag to constrain outputs to transcript-grounded content |
| Offline Support | Added `--ai local` for fully offline processing with zero external dependencies |
| Documentation | Added `ANTI_HALLUCINATION_GUIDELINES.md`; rewrote and expanded `README.md` |
| CLI Correctness | Fixed all stale and incorrect command examples across documentation |
| Error Handling | Improved failure handling in transcription, download, and formatting stages |

---

## Upgrade Steps

### 1. Pull the latest main branch

```bash
git checkout main
git pull origin main
```

### 2. Recreate the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the setup script

**macOS / Linux**

```bash
chmod +x setup.sh && ./setup.sh
```

**Windows**

```powershell
.\setup.bat
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Open .env and set your preferred provider key
```

At minimum, set `AI_PROVIDER` to your preferred backend. Add the corresponding API key variable. See `README.md` for the full provider key reference.

### 5. Run a smoke test

```bash
python clipify.py --video sample.mp4 --ai local --clips 3
```

This verifies the installation end-to-end using local processing — no API key required.

### 6. Verify YouTube authentication (if applicable)

```bash
python get_youtube_cookies.py
python clipify.py --url "https://youtube.com/watch?v=..." --cookies cookies.txt
```

---

## Compatibility Notes

**`--ai` flag**
This is now the canonical way to select a provider. Legacy provider flags from earlier versions are deprecated and will be removed in a future release.

**`--anti-hallucination` flag**
Enables safe mode. When active, Clipify constrains all AI outputs to content grounded in the transcript and prefers `local` processing unless an explicit provider is set with `--ai`.

**`--no-captions` flag**
Caption generation is now enabled by default. Pass `--no-captions` to disable it.

**`--watch` flag**
Monitors a directory in real time and automatically processes any new video files that are added.

---

## Developer Checklist

Before tagging a release or deploying to a new environment, confirm the following:

- [ ] `setup.py` version field reads `1.0.1`
- [ ] `README.md` references only currently supported CLI flags
- [ ] `ENHANCEMENT.md` and `ANTI_HALLUCINATION_GUIDELINES.md` are present in the repo root
- [ ] `core/transcriber.py` uses the updated provider selection logic
- [ ] `.env.example` includes both `AI_PROVIDER` and `ANTI_HALLUCINATION` variables
- [ ] Smoke test passes with `--ai local` on a clean virtual environment
- [ ] All CI checks pass on the `main` branch

---

## Reference Documents

| File | Purpose |
|---|---|
| [README.md](README.md) | Full project documentation, pipeline overview, and usage examples |
| [ANTI_HALLUCINATION_GUIDELINES.md](ANTI_HALLUCINATION_GUIDELINES.md) | Practical checklist and provider guidance for safe mode |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development setup and contribution workflow |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and security policy |
