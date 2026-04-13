"""
Base Provider Interface for AI Services

This module defines the abstract base class that all AI providers must implement.
Provides common functionality and enforces a consistent interface across different LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    TRANSCRIPTION = "transcription"


class ProviderStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    name: str
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Message structure for chat APIs"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


@dataclass
class ModelInfo:
    """Information about an available model"""
    id: str
    name: str
    provider: str
    model_type: ModelType
    context_window: int
    max_tokens: int
    cost_per_1k_input: float  # USD
    cost_per_1k_output: float  # USD
    supports_streaming: bool = True
    supports_function_calling: bool = False
    release_date: Optional[str] = None
    description: str = ""


@dataclass
class CompletionResponse:
    """Structured response from completion API"""
    text: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    stop_reason: str
    finish_time: datetime = field(default_factory=datetime.now)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    cost_usd: Optional[float] = None


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.
    
    All provider implementations must inherit from this class and implement
    the abstract methods. This ensures a consistent interface across different
    LLM services (OpenAI, Groq, Anthropic, etc.)
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.
        
        Args:
            config: ProviderConfig object with API credentials and settings
            
        Raises:
            ValueError: If required configuration is missing
        """
        self.config = config
        self.name = config.name
        self.api_key = config.api_key
        self._status = ProviderStatus.UNKNOWN
        self._last_health_check = None
        
        if not self.api_key:
            raise ValueError(f"{self.name}: API key not provided")
        
        logger.info(f"Initializing {self.name} provider")

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify provider is working and credentials are valid.
        
        Returns:
            bool: True if provider is accessible and working
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """
        Get list of available models for this provider.
        
        Returns:
            List of ModelInfo objects describing available models
        """
        pass

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> CompletionResponse:
        """
        Generate text completion based on messages.
        
        Args:
            messages: List of Message objects (conversation history)
            model: Model ID to use
            temperature: Randomness (0.0-2.0), lower = more deterministic
            max_tokens: Maximum tokens in response
            stop_sequences: Stop generation at these sequences
            **kwargs: Provider-specific parameters
            
        Returns:
            CompletionResponse with generated text and metadata
        """
        pass

    @abstractmethod
    def stream_complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Stream text completion (generator).
        
        Args:
            messages: List of Message objects
            model: Model ID to use
            temperature: Randomness level
            max_tokens: Maximum tokens
            **kwargs: Provider-specific parameters
            
        Yields:
            str: Text chunks as they're generated
        """
        pass

    def get_status(self) -> ProviderStatus:
        """Get current health status of provider"""
        return self._status

    def set_status(self, status: ProviderStatus) -> None:
        """Set provider status"""
        self._status = status
        self._last_health_check = datetime.now()

    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """
        Count tokens in text (approximate for this model).
        
        Args:
            text: Text to count tokens for
            model: Model ID
            
        Returns:
            Estimated token count
        """
        pass

    @abstractmethod
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """
        Calculate cost of API call in USD.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model ID
            
        Returns:
            float: Estimated cost in USD
        """
        pass

    def validate_model(self, model: str) -> bool:
        """
        Check if model is available in this provider.
        
        Args:
            model: Model ID to validate
            
        Returns:
            bool: True if model is available
        """
        available = self.get_available_models()
        return any(m.id == model for m in available)

    def format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format messages for API call (standard format).
        Can be overridden by providers with custom requirements.
        
        Args:
            messages: List of Message objects
            
        Returns:
            List of dicts with 'role' and 'content' keys
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def parse_response(self, response: Dict[str, Any]) -> CompletionResponse:
        """
        Parse provider's API response into CompletionResponse.
        Must be implemented by each provider.
        
        Args:
            response: Raw response from provider API
            
        Returns:
            CompletionResponse object
        """
        raise NotImplementedError(f"{self.name} must implement parse_response()")

    def retry_on_failure(self, func, max_retries: Optional[int] = None, *args, **kwargs):
        """
        Retry function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Max retry attempts (uses config default if None)
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
        """
        max_retries = max_retries or self.config.max_retries
        delay = self.config.retry_delay
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"{self.name}: Attempt {attempt + 1}/{max_retries}")
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        f"{self.name}: Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    import time
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"{self.name}: All {max_retries} attempts failed")
        
        raise last_exception

    def log_api_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: float
    ) -> None:
        """Log API call metrics for monitoring."""
        logger.info(
            f"{self.name}: model={model}, "
            f"input={input_tokens}, output={output_tokens}, "
            f"cost=${cost_usd:.6f}, latency={latency_ms:.1f}ms"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, status={self._status.value})"
