"""
Clean, professional logging for Clipify
"""

import sys
import io

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    # Set UTF-8 encoding for stdout
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Logger:
    """Simple, readable CLI logger"""

    def header(self, text: str):
        """Print header"""
        print("\n" + "=" * 70)
        print(text)
        print("=" * 70)

    def step(self, current: int, total: int, description: str):
        """Print step progress"""
        print(f"\n[STEP {current}/{total}] {description}")

    def info(self, text: str):
        """Print info message"""
        print(f"  ℹ️  {text}")

    def success(self, text: str):
        """Print success message"""
        print(f"  ✅ {text}")

    def error(self, text: str):
        """Print error message"""
        print(f"  ❌ {text}")

    def warning(self, text: str):
        """Print warning message"""
        print(f"  ⚠️  {text}")