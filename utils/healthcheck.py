"""
Health check utilities for AI providers
"""

from typing import Callable


def run_health_check(provider_name: str, check_func: Callable[[], bool], timeout: int = 15) -> bool:
    """
    Run health check with timeout

    Args:
        provider_name: Name of provider for logging
        check_func: Function that returns True if healthy
        timeout: Timeout in seconds

    Returns:
        True if healthy, False otherwise
    """
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"{provider_name} health check timed out")

    # Set timeout (Unix only - Windows will skip)
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
    except AttributeError:
        # Windows doesn't support SIGALRM
        pass

    try:
        result = check_func()
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutError as e:
        print(f"⚠️  {e}")
        return False
    except Exception as e:
        print(f"⚠️  Health check failed: {e}")
        return False
    finally:
        try:
            signal.alarm(0)
        except AttributeError:
            pass