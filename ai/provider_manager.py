"""
Provider Registry & Manager

Manages available providers, registration, and instantiation.
Handles provider discovery and selection.
"""

import os
import logging
from typing import Dict, List, Optional, Type, Any
from importlib import import_module

from ai.base_provider import BaseProvider, ProviderConfig
from ai.errors import ProviderNotSupportedError, InvalidConfigError


logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry of available AI providers"""
    
    # Map of provider names to module paths
    PROVIDER_MAP = {
        "openai": ("ai.openai_provider", "OpenAIProvider"),
        "groq": ("ai.groq_provider", "GroqProvider"),
        "anthropic": ("ai.anthropic_provider", "AnthropicProvider"),
        "gemini": ("ai.gemini_provider", "GeminiProvider"),
        "deepseek": ("ai.deepseek_provider", "DeepSeekProvider"),
        "openrouter": ("ai.openrouter_provider", "OpenRouterProvider"),
        "local": ("ai.local_provider", "LocalProvider"),
        "mistral": ("ai.mistral_provider", "MistralProvider"),
        "cohere": ("ai.cohere_provider", "CohereProvider"),
        "together": ("ai.together_provider", "TogetherProvider"),
        "fireworks": ("ai.fireworks_provider", "FireworksProvider"),
        "perplexity": ("ai.perplexity_provider", "PerplexityProvider"),
        "xai": ("ai.xai_provider", "XAIProvider"),
    }
    
    def __init__(self):
        """Initialize provider registry"""
        self._providers: Dict[str, Type[BaseProvider]] = {}
        self._instances: Dict[str, BaseProvider] = {}
    
    def register_provider(
        self,
        name: str,
        provider_class: Type[BaseProvider]
    ) -> None:
        """
        Register a provider class.
        
        Args:
            name: Provider identifier
            provider_class: Provider class (inherits from BaseProvider)
        """
        if not issubclass(provider_class, BaseProvider):
            raise InvalidConfigError(
                f"Provider {name} must inherit from BaseProvider"
            )
        self._providers[name.lower()] = provider_class
        logger.info(f"Registered provider: {name}")
    
    def get_provider_class(self, name: str) -> Type[BaseProvider]:
        """
        Get provider class by name.
        Attempts to load from module path if not already registered.
        
        Args:
            name: Provider name
            
        Returns:
            Provider class
            
        Raises:
            ProviderNotSupportedError: If provider not found
        """
        name_lower = name.lower()
        
        # Check if already registered
        if name_lower in self._providers:
            return self._providers[name_lower]
        
        # Try to load from module path
        if name_lower in self.PROVIDER_MAP:
            module_path, class_name = self.PROVIDER_MAP[name_lower]
            try:
                module = import_module(module_path)
                provider_class = getattr(module, class_name)
                self.register_provider(name_lower, provider_class)
                return provider_class
            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to load provider {name}: {e}")
        
        supported = ", ".join(list(self.PROVIDER_MAP.keys()) + list(self._providers.keys()))
        raise ProviderNotSupportedError(
            name,
            supported_providers=supported.split(", ")
        )
    
    def create_provider(
        self,
        name: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseProvider:
        """
        Create and return a provider instance.
        
        Args:
            name: Provider name
            api_key: API key (uses env var if not provided)
            **kwargs: Additional config parameters
            
        Returns:
            Instantiated provider
            
        Raises:
            ProviderNotSupportedError: If provider not found
            InvalidConfigError: If configuration invalid
        """
        provider_class = self.get_provider_class(name)
        
        # Get API key from parameter or environment
        if not api_key:
            env_keys = [
                f"{name.upper()}_API_KEY",
                f"{name.upper()}_KEY",
            ]
            for env_key in env_keys:
                api_key = os.getenv(env_key)
                if api_key:
                    break
        
        if not api_key:
            raise InvalidConfigError(
                f"API key not provided for {name}. "
                f"Set {env_keys[0]} environment variable or pass api_key parameter"
            )
        
        # Create config
        config = ProviderConfig(
            name=name,
            api_key=api_key,
            **kwargs
        )
        
        # Instantiate provider
        provider = provider_class(config)
        logger.info(f"Created provider instance: {name}")
        return provider
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider names.
        
        Returns:
            List of provider identifiers
        """
        return list(set(list(self.PROVIDER_MAP.keys()) + list(self._providers.keys())))
    
    def is_available(self, name: str) -> bool:
        """
        Check if provider is available.
        
        Args:
            name: Provider name
            
        Returns:
            True if provider can be loaded
        """
        try:
            self.get_provider_class(name)
            return True
        except ProviderNotSupportedError:
            return False


class ProviderManager:
    """Manages provider instances and selection"""
    
    def __init__(self):
        """Initialize provider manager"""
        self.registry = ProviderRegistry()
        self._active_provider: Optional[BaseProvider] = None
        self._provider_instances: Dict[str, BaseProvider] = {}
    
    def select_provider(self, name: str) -> BaseProvider:
        """
        Select and activate a provider.
        
        Args:
            name: Provider name
            
        Returns:
            Active provider instance
        """
        if name not in self._provider_instances:
            self._provider_instances[name] = self.registry.create_provider(name)
        
        self._active_provider = self._provider_instances[name]
        logger.info(f"Selected provider: {name}")
        return self._active_provider
    
    def get_active_provider(self) -> Optional[BaseProvider]:
        """Get currently active provider"""
        return self._active_provider
    
    def get_provider(self, name: str) -> BaseProvider:
        """
        Get provider instance by name (doesn't activate).
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or creates new one
        """
        if name not in self._provider_instances:
            self._provider_instances[name] = self.registry.create_provider(name)
        return self._provider_instances[name]
    
    def find_best_provider(
        self,
        required_features: Optional[List[str]] = None,
        max_cost: Optional[float] = None
    ) -> BaseProvider:
        """
        Find best available provider based on criteria.
        
        Args:
            required_features: List of required features
            max_cost: Maximum cost per 1K tokens
            
        Returns:
            Best available provider
            
        Raises:
            ProviderNotSupportedError: No provider meets requirements
        """
        available = self.registry.get_available_providers()
        
        for provider_name in available:
            try:
                provider = self.get_provider(provider_name)
                
                # Check health
                if not provider.health_check():
                    logger.debug(f"{provider_name} health check failed")
                    continue
                
                # TODO: Check features and cost if implemented
                
                logger.info(f"Selected provider: {provider_name}")
                return provider
            except Exception as e:
                logger.debug(f"Failed to use {provider_name}: {e}")
                continue
        
        raise ProviderNotSupportedError(
            "default",
            supported_providers=available
        )
    
    def list_providers(self) -> Dict[str, Any]:
        """
        List all available providers with their status.
        
        Returns:
            Dict with provider names and status
        """
        result = {}
        for name in self.registry.get_available_providers():
            try:
                provider = self.get_provider(name)
                result[name] = {
                    "available": True,
                    "status": provider.get_status().value,
                    "health": provider.health_check()
                }
            except Exception as e:
                result[name] = {
                    "available": False,
                    "error": str(e)
                }
        return result


# Global provider manager instance
_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Get or create global provider manager"""
    global _manager
    if _manager is None:
        _manager = ProviderManager()
    return _manager


def select_provider(name: str) -> BaseProvider:
    """
    Convenience function to select a provider.
    
    Args:
        name: Provider name
        
    Returns:
        Active provider
    """
    return get_provider_manager().select_provider(name)


def get_provider(name: str) -> BaseProvider:
    """
    Convenience function to get a provider instance.
    
    Args:
        name: Provider name
        
    Returns:
        Provider instance
    """
    return get_provider_manager().get_provider(name)


def list_providers() -> Dict[str, Any]:
    """
    Convenience function to list all providers.
    
    Returns:
        Dict with provider names and status
    """
    return get_provider_manager().list_providers()
