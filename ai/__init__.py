"""AI provider module for Clipify.

This module manages integrations with 13+ AI providers including OpenAI, Groq,
Anthropic, Google Gemini, and local providers. Supports automatic provider selection
and fallback chains.

Supported Providers:
    - OpenAI (GPT-4, GPT-3.5)
    - Groq (Ultra-fast inference)
    - Anthropic Claude (Long context, reasoning)
    - Google Gemini (Multimodal)
    - DeepSeek (Budget-friendly)
    - Mistral AI
    - Cohere
    - Together AI
    - Fireworks AI
    - Perplexity
    - xAI (Grok)
    - OpenRouter (150+ models)
    - Local/Ollama (Private, offline)

Exports:
    BaseProvider: Abstract base class for all providers
    ProviderManager: Manager for provider registry and selection
    get_provider: Get provider instance by name
"""

from ai.base_provider import BaseProvider
from ai.provider_manager import ProviderManager

__all__ = [
    "BaseProvider",
    "ProviderManager",
]


def get_provider(provider_name: str):
    """Get a provider instance by name.
    
    Args:
        provider_name: Name of the provider (e.g., 'openai', 'groq', 'local')
        
    Returns:
        Provider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    manager = ProviderManager()
    return manager.get_provider(provider_name)
