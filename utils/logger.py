"""
Clean, professional logging for Clipify

Supports verbose mode: when verbose=True debug-level messages are printed.
All output goes through the Logger methods — no raw print() calls elsewhere.
"""

import sys
import io

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


class Logger:
    """Simple, readable CLI logger for Clipify operations.

    Provides console output with emoji indicators for different message
    types (info, success, error, warning, debug).  Respects the
    ``verbose`` flag: debug messages are suppressed unless verbose is
    enabled.
    """

    def __init__(self, verbose: bool = False) -> None:
        """Initialise Logger.

        Args:
            verbose: When True, :meth:`debug` messages are printed.
        """
        self.verbose = verbose

    def header(self, text: str) -> None:
        """Print a section header with decoration.

        Args:
            text: Header text to display.
        """
        print("\n" + "=" * 70)
        print(text)
        print("=" * 70)

    def step(self, current: int, total: int, description: str) -> None:
        """Print a step progress indicator.

        Args:
            current: Current step number (1-indexed).
            total: Total number of steps.
            description: Human-readable step description.
        """
        print(f"\n[STEP {current}/{total}] {description}")

    def info(self, text: str) -> None:
        """Print an informational message.

        Args:
            text: Message to display.
        """
        print(f"  ℹ️  {text}")

    def success(self, text: str) -> None:
        """Print a success message.

        Args:
            text: Message to display.
        """
        print(f"  ✅ {text}")

    def error(self, text: str) -> None:
        """Print an error message.

        Args:
            text: Message to display.
        """
        print(f"  ❌ {text}", file=sys.stderr)

    def warning(self, text: str) -> None:
        """Print a warning message.

        Args:
            text: Message to display.
        """
        print(f"  ⚠️  {text}")

    def debug(self, text: str) -> None:
        """Print a debug message (only shown when verbose=True).

        Args:
            text: Message to display.
        """
        if self.verbose:
            print(f"  🔍 {text}")