import json
import tempfile
from pathlib import Path

import pytest

from core.downloader import _convert_json_cookies_to_txt, _setup_cookies
from audio_analysis.silence_detector import _get_cache_key, _save_to_cache, _load_from_cache, SilenceRegion


def test_convert_json_cookies_to_txt(tmp_path):
    cookies = [
        {
            "domain": ".youtube.com",
            "httpOnly": False,
            "path": "/",
            "secure": True,
            "expires": 1893456000,
            "name": "YSC",
            "value": "dummy"
        }
    ]
    json_file = tmp_path / "cookies.json"
    json_file.write_text(json.dumps(cookies), encoding='utf-8')

    txt_path = _convert_json_cookies_to_txt(json_file)
    assert txt_path is not None
    assert txt_path.exists()

    content = txt_path.read_text(encoding='utf-8')
    assert ".youtube.com" in content
    assert "YSC" in content


def test_silence_detector_cache(tmp_path):
    video_path = tmp_path / "dummy.mp4"
    video_path.write_text("nothing", encoding='utf-8')

    cache_key = _get_cache_key(video_path, threshold=-40.0, min_duration=0.5)
    regions = [SilenceRegion(start=0.1, end=0.5, duration=0.4)]

    _save_to_cache(cache_key, regions)
    loaded = _load_from_cache(cache_key)

    assert loaded is not None
    assert len(loaded) == 1
    assert loaded[0].start == 0.1
    assert loaded[0].end == 0.5
    assert abs(loaded[0].duration - 0.4) < 1e-6


def test_setup_cookies_local_json(tmp_path, monkeypatch):
    # Create hypothetical cookies file in cwd
    cookie_json = tmp_path / "cookies.json"
    cookie_json.write_text(json.dumps([{"domain": ".example.com", "httpOnly": True, "path": "/", "secure": True, "expires": 0, "name": "XSRF", "value": "1"}]), encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    found = _setup_cookies()

    assert found is not None
    assert found.exists()

    # Should be a text file when derived from JSON
    assert found.suffix == '.txt'


def test_transcribe_video_selects_gemini(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_gemini_key")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    import core.transcriber as transcriber

    monkeypatch.setattr(transcriber, '_transcribe_with_gemini', lambda video_path, language=None: [
        {'start': 0.0, 'end': 1.0, 'text': 'gemini test', 'words': []}
    ])

    result = transcriber.transcribe_video(tmp_path / "dummy.mp4")
    assert result[0]['text'] == 'gemini test'


def test_transcribe_video_selects_anthropic(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake_anthropic_key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    import core.transcriber as transcriber

    monkeypatch.setattr(transcriber, '_transcribe_with_anthropic', lambda video_path, language=None: [
        {'start': 0.0, 'end': 1.0, 'text': 'anthropic test', 'words': []}
    ])

    result = transcriber.transcribe_video(tmp_path / "dummy.mp4")
    assert result[0]['text'] == 'anthropic test'
