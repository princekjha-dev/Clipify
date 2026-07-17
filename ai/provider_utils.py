"""
Provider Utilities & Helpers

Common utility functions for provider implementations.
"""

import time
import logging
from typing import Dict, Any, List, Callable, Optional, Union
from functools import wraps
from datetime import datetime, timedelta
import json

from ai.errors import TokenLimitExceededError, ProviderError


logger = logging.getLogger(__name__)


class TokenCounter:
    """Utility for token counting across different providers"""
    
    # Approximate token ratios (tokens per character)
    # These are rough estimates; actual counts vary by model
    CHAR_TO_TOKEN_RATIOS = {
        "gpt-4": 0.35,      # 1 token ≈ 2.86 chars
        "gpt-3.5": 0.30,    # 1 token ≈ 3.33 chars
        "claude": 0.32,     # 1 token ≈ 3.125 chars
        "llama": 0.28,      # 1 token ≈ 3.57 chars
        "gemini": 0.30,
        "mistral": 0.28,
    }
    
    @staticmethod
    def estimate_tokens(
        text: str,
        model_family: str = "gpt-3.5"
    ) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to count
            model_family: Model family (determines ratio)
            
        Returns:
            Estimated token count
        """
        ratio = TokenCounter.CHAR_TO_TOKEN_RATIOS.get(
            model_family.lower(),
            0.30
        )
        return max(1, int(len(text) * ratio))
    
    @staticmethod
    def count_messages_tokens(
        messages: List[Dict[str, str]],
        model_family: str = "gpt-3.5"
    ) -> int:
        """
        Estimate total tokens for messages (conversation).
        
        Args:
            messages: List of message dicts
            model_family: Model family
            
        Returns:
            Total estimated tokens
        """
        # Count message content
        total = sum(
            TokenCounter.estimate_tokens(msg.get("content", ""), model_family)
            for msg in messages
        )
        
        # Add overhead for formatting (roles, separators, etc.)
        overhead = len(messages) * 4  # ~4 tokens per message overhead
        
        return total + overhead


class CostCalculator:
    """Utility for calculating API call costs"""
    
    # Pricing per 1K tokens (USD)
    # Update as pricing changes
    PRICING = {
        "gpt-4": {
            "input": 0.03,
            "output": 0.06,
        },
        "gpt-4-turbo": {
            "input": 0.01,
            "output": 0.03,
        },
        "gpt-3.5-turbo": {
            "input": 0.0005,
            "output": 0.0015,
        },
        "claude-3-opus": {
            "input": 0.015,
            "output": 0.075,
        },
        "claude-3-sonnet": {
            "input": 0.003,
            "output": 0.015,
        },
        "claude-3-haiku": {
            "input": 0.00025,
            "output": 0.00125,
        },
        "llama-2-7b": {
            "input": 0.0001,
            "output": 0.0001,
        },
        "mistral-7b": {
            "input": 0.00014,
            "output": 0.00042,
        },
        "gemini-pro": {
            "input": 0.001,
            "output": 0.002,
        },
    }
    
    @staticmethod
    def calculate(
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost in USD.
        
        Args:
            model: Model name/ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        model_lower = model.lower()
        
        # Try exact model match
        if model_lower in CostCalculator.PRICING:
            pricing = CostCalculator.PRICING[model_lower]
            return (
                (input_tokens / 1000) * pricing["input"] +
                (output_tokens / 1000) * pricing["output"]
            )
        
        # Try model family match
        for key in CostCalculator.PRICING:
            if key in model_lower:
                pricing = CostCalculator.PRICING[key]
                return (
                    (input_tokens / 1000) * pricing["input"] +
                    (output_tokens / 1000) * pricing["output"]
                )
        
        # Default: assume free tier
        logger.warning(f"Unknown model {model}, using default pricing (free)")
        return 0.0


class RateLimiter:
    """Rate limiting utility with exponential backoff"""
    
    def __init__(
        self,
        calls_per_minute: int = 60,
        burst_size: int = 10
    ):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Max calls per minute
            burst_size: Burst allowance
        """
        self.calls_per_minute = calls_per_minute
        self.burst_size = burst_size
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time = 0
        self.burst_remaining = burst_size
    
    def wait_if_needed(self) -> float:
        """
        Wait if necessary to comply with rate limit.
        
        Returns:
            Time waited in seconds
        """
        now = time.time()
        time_since_last = now - self.last_call_time
        
        if self.burst_remaining > 0:
            self.burst_remaining -= 1
            self.last_call_time = now
            return 0.0
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            self.last_call_time = time.time()
            return wait_time
        
        self.last_call_time = now
        return 0.0


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    on_retry: Optional[Callable] = None
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum retry attempts
        initial_delay: Initial wait time in seconds
        backoff_factor: Multiplier for delay each retry
        max_delay: Maximum wait time between retries
        on_retry: Callback function called on retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ProviderError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # Call retry callback if provided
                        if on_retry:
                            on_retry(
                                attempt=attempt + 1,
                                error=e,
                                delay=delay
                            )
                        
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed: {e}"
                        )
            
            if last_exception:
                raise last_exception
            raise Exception(f"Failed after {max_retries} attempts")
        
        return wrapper
    return decorator


def timeout_handler(timeout_seconds: float):
    """
    Decorator to add timeout to function.
    Note: This uses threading and may not work with all scenarios.
    
    Args:
        timeout_seconds: Timeout duration
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For now, just log warning if needed
            # Full timeout implementation requires threading
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ResponseValidator:
    """Validate provider API responses"""
    
    @staticmethod
    def validate_completion_response(response: Dict[str, Any]) -> bool:
        """
        Validate completion API response structure.
        
        Args:
            response: Response dict
            
        Returns:
            True if valid
            
        Raises:
            ProviderError: If response invalid
        """
        required_fields = ["text", "model", "input_tokens", "output_tokens"]
        for field in required_fields:
            if field not in response:
                raise ProviderError(f"Missing required field: {field}")
        
        return True
    
    @staticmethod
    def validate_token_limits(
        input_tokens: int,
        output_tokens: int,
        max_tokens: int,
        context_window: int
    ) -> bool:
        """
        Validate token limits.
        
        Args:
            input_tokens: Input token count
            output_tokens: Output token count
            max_tokens: Model's max output tokens
            context_window: Model's context window
            
        Returns:
            True if valid
            
        Raises:
            TokenLimitExceededError: If limits exceeded
        """
        total_tokens = input_tokens + output_tokens
        
        if input_tokens > context_window:
            raise TokenLimitExceededError(
                f"Input tokens ({input_tokens}) exceeds context window ({context_window})",
                input_tokens=input_tokens,
                max_tokens=context_window
            )
        
        if output_tokens > max_tokens:
            raise TokenLimitExceededError(
                f"Output tokens ({output_tokens}) exceeds max ({max_tokens})",
                input_tokens=input_tokens,
                max_tokens=max_tokens
            )
        
        if total_tokens > context_window:
            raise TokenLimitExceededError(
                f"Total tokens ({total_tokens}) exceeds context window ({context_window})",
                input_tokens=input_tokens,
                max_tokens=context_window
            )
        
        return True


class ProviderMetrics:
    """Track provider metrics for monitoring"""
    
    def __init__(self):
        self.total_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = datetime.now()
        self.call_times: List[float] = []
    
    def record_call(
        self,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        latency_ms: float
    ) -> None:
        """Record a provider call"""
        self.total_calls += 1
        self.total_tokens += input_tokens + output_tokens
        self.total_cost += cost
        self.call_times.append(latency_ms)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        avg_latency = sum(self.call_times) / len(self.call_times) if self.call_times else 0
        
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "avg_latency_ms": round(avg_latency, 1),
            "duration_seconds": round(duration, 1),
            "calls_per_minute": round((self.total_calls / duration) * 60, 2) if duration > 0 else 0,
        }
    
    def __repr__(self) -> str:
        summary = self.get_summary()
        return json.dumps(summary, indent=2)
