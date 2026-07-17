import subprocess
import sys


def test_help_runs():
    result = subprocess.run(
        [sys.executable, "clipify.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "clipify" in result.stdout.lower()


def test_version_flag():
    result = subprocess.run(
        [sys.executable, "clipify.py", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode in [0, 1]
