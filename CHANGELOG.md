# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-01
### Added
- `--ai` flag for explicit provider selection across 9 backends
- `--anti-hallucination` safe mode for transcript-grounded outputs
- Local offline processing via `--ai local`
- ANTI_HALLUCINATION_GUIDELINES.md documentation
- Expanded README with pipeline flowchart and provider selection diagram

### Fixed
- Corrected all CLI examples across documentation
- Improved error handling in transcription, download, and formatting stages
- Removed stale references in documentation

## [1.0.0] - 2024-10-01
### Added
- Initial release
- Whisper-based transcription with segment-level timestamps
- FFmpeg zero-re-encode clip extraction
- Multi-ratio export: 9:16, 16:9, 1:1
- VTT caption generation
- YouTube download via yt-dlp
- Watch directory mode
