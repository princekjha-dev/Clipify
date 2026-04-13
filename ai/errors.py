"""
Provider Error Handling & Exceptions

Custom exceptions and error handling for AI provider operations.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ProviderError(Exception):
    """Base exception for provider errors"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        self.severity = severity
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        parts = []
        if self.provider:
            parts.append(f"[{self.provider}]")
        if self.error_code:
            parts.append(f"({self.error_code})")
        parts.append(self.message)
        return " ".join(parts)


class AuthenticationError(ProviderError):
    """Authentication/API key related errors"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="AUTH_ERROR",
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class RateLimitError(ProviderError):
    """Rate limit exceeded errors"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        super().__init__(
            message=message,
            provider=provider,
            error_code="RATE_LIMIT",
            severity=ErrorSeverity.WARNING,
            **kwargs
        )


class QuotaExceededError(ProviderError):
    """Account quota exceeded errors"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="QUOTA_EXCEEDED",
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class ModelNotFoundError(ProviderError):
    """Requested model not available"""
    
    def __init__(
        self,
        model: str,
        provider: Optional[str] = None,
        available_models: Optional[list] = None,
        **kwargs
    ):
        self.model = model
        self.available_models = available_models or []
        message = f"Model '{model}' not found"
        if self.available_models:
            message += f". Available: {', '.join(self.available_models[:3])}"
        super().__init__(
            message=message,
            provider=provider,
            error_code="MODEL_NOT_FOUND",
            **kwargs
        )


class TimeoutError(ProviderError):
    """API request timeout"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="TIMEOUT",
            severity=ErrorSeverity.WARNING,
            **kwargs
        )


class ConnectionError(ProviderError):
    """Network/connection errors"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="CONNECTION_ERROR",
            severity=ErrorSeverity.WARNING,
            **kwargs
        )


class ProviderUnavailableError(ProviderError):
    """Provider service unavailable"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        super().__init__(
            message=message,
            provider=provider,
            error_code="SERVICE_UNAVAILABLE",
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class HealthCheckFailedError(ProviderError):
    """Health check failed for provider"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="HEALTH_CHECK_FAILED",
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class InvalidConfigError(ProviderError):
    """Invalid provider configuration"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="INVALID_CONFIG",
            severity=ErrorSeverity.ERROR,
            **kwargs
        )


class InvalidInputError(ProviderError):
    """Invalid input parameters"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="INVALID_INPUT",
            severity=ErrorSeverity.WARNING,
            **kwargs
        )


class TokenLimitExceededError(ProviderError):
    """Input exceeds model token limit"""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        input_tokens: Optional[int] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        self.input_tokens = input_tokens
        self.max_tokens = max_tokens
        super().__init__(
            message=message,
            provider=provider,
            error_code="TOKEN_LIMIT_EXCEEDED",
            **kwargs
        )


class ProviderNotSupportedError(ProviderError):
    """Requested provider is not supported"""
    
    def __init__(
        self,
        provider: str,
        supported_providers: Optional[list] = None,
        **kwargs
    ):
        self.supported_providers = supported_providers or []
        message = f"Provider '{provider}' not supported"
        if self.supported_providers:
            message += f". Supported: {', '.join(self.supported_providers)}"
        super().__init__(
            message=message,
            provider=provider,
            error_code="PROVIDER_NOT_SUPPORTED",
            **kwargs
        )


class FeatureNotSupportedError(ProviderError):
    """Feature not supported by provider"""
    
    def __init__(
        self,
        feature: str,
        provider: Optional[str] = None,
        **kwargs
    ):
        self.feature = feature
        message = f"Feature '{feature}' not supported"
        super().__init__(
            message=message,
            provider=provider,
            error_code="FEATURE_NOT_SUPPORTED",
            **kwargs
        )


class CostCalculationError(ProviderError):
    """Error calculating API call cost"""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            provider=provider,
            error_code="COST_CALCULATION_ERROR",
            **kwargs
        )


# Error handler utility functions

def handle_provider_error(error: Exception, provider: str) -> ProviderError:
    """
    Convert various exceptions into structured ProviderErrors.
    
    Args:
        error: Original exception
        provider: Provider name
        
    Returns:
        ProviderError with appropriate type
    """
    error_str = str(error).lower()
    
    # Authentication errors
    if any(x in error_str for x in ["unauthorized", "invalid api key", "authentication", "auth"]):
        return AuthenticationError(str(error), provider=provider)
    
    # Rate limiting
    if any(x in error_str for x in ["rate limit", "too many requests", "429"]):
        return RateLimitError(str(error), provider=provider)
    
    # Quota exceeded
    if any(x in error_str for x in ["quota", "limit", "exceeded"]):
        return QuotaExceededError(str(error), provider=provider)
    
    # Service unavailable
    if any(x in error_str for x in ["unavailable", "503", "service", "maintenance"]):
        return ProviderUnavailableError(str(error), provider=provider)
    
    # Timeout
    if any(x in error_str for x in ["timeout", "timed out"]):
        return TimeoutError(str(error), provider=provider)
    
    # Connection errors
    if any(x in error_str for x in ["connection", "network", "connected"]):
        return ConnectionError(str(error), provider=provider)
    
    # Token limits
    if any(x in error_str for x in ["token", "context", "length"]):
        return TokenLimitExceededError(str(error), provider=provider)
    
    # Fallback
    return ProviderError(str(error), provider=provider, error_code="UNKNOWN_ERROR")


def format_error_message(error: ProviderError, include_details: bool = False) -> str:
    """
    Format error message for logging or user display.
    
    Args:
        error: ProviderError instance
        include_details: Include error details
        
    Returns:
        Formatted error message
    """
    message = f"[{error.severity.value.upper()}] {str(error)}"
    
    if include_details and error.details:
        details_str = ", ".join(f"{k}={v}" for k, v in error.details.items())
        message += f" ({details_str})"
    
    return message
