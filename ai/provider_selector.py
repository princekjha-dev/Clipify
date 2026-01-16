"""
Provider selector with proper imports and fallbacks
Enhanced with provider status checking and user selection
"""

import os
from typing import Optional, List, Dict, Tuple
from pathlib import Path


def get_available_providers(logger) -> Dict[str, Tuple]:
    """
    Check all available providers and their status
    
    Returns:
        Dict mapping provider name to (provider_class, status_msg, is_available)
    """
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    providers = {}
    
    # Check Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key.strip():
        try:
            from ai.groq_provider import GroqProvider
            provider = GroqProvider()
            try:
                if provider.health_check():
                    providers["groq"] = (GroqProvider, "✓ Groq (Free & Fast)", True)
                else:
                    providers["groq"] = (GroqProvider, "✗ Groq (health check failed)", False)
            except Exception as e:
                providers["groq"] = (GroqProvider, f"✗ Groq (Invalid key or connection error)", False)
        except ImportError:
            providers["groq"] = (None, "⚠ Groq (library not installed: pip install groq)", False)
    else:
        providers["groq"] = (None, "⚠ Groq (no API key set)", False)
    
    # Check DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key and deepseek_key.strip():
        try:
            from ai.deepseek_provider import DeepSeekProvider
            provider = DeepSeekProvider()
            try:
                if provider.health_check():
                    providers["deepseek"] = (DeepSeekProvider, "✓ DeepSeek (Ultra-cheap)", True)
                else:
                    providers["deepseek"] = (DeepSeekProvider, "✗ DeepSeek (health check failed)", False)
            except Exception as e:
                providers["deepseek"] = (DeepSeekProvider, f"✗ DeepSeek (Invalid key or connection error)", False)
        except ImportError:
            providers["deepseek"] = (None, "⚠ DeepSeek (library not installed: pip install deepseek)", False)
    else:
        providers["deepseek"] = (None, "⚠ DeepSeek (no API key set)", False)
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.strip():
        try:
            from ai.openai_provider import OpenAIProvider
            provider = OpenAIProvider()
            try:
                if provider.health_check():
                    providers["openai"] = (OpenAIProvider, "✓ OpenAI (Paid)", True)
                else:
                    providers["openai"] = (OpenAIProvider, "✗ OpenAI (health check failed)", False)
            except Exception as e:
                providers["openai"] = (OpenAIProvider, f"✗ OpenAI (Invalid key or connection error)", False)
        except ImportError:
            providers["openai"] = (None, "⚠ OpenAI (library not installed: pip install openai)", False)
    else:
        providers["openai"] = (None, "⚠ OpenAI (no API key set)", False)
    
    # Local is always available
    from ai.local_provider import LocalProvider
    providers["local"] = (LocalProvider, "ℹ Local Processing (No API needed)", True)
    
    return providers


def select_ai_provider(logger, provider_name: Optional[str] = None):
    """
    Select AI provider with optional user preference
    
    Args:
        logger: Logger instance
        provider_name: Optional provider name ('groq', 'deepseek', 'openai', 'local')
                      If None, shows interactive menu
    
    Returns:
        Selected provider instance
    """
    
    logger.header("SELECTING AI PROVIDER")
    
    # Get all available providers
    providers = get_available_providers(logger)
    
    # Separate available and unavailable
    available = {k: v for k, v in providers.items() if v[2]}
    unavailable = {k: v for k, v in providers.items() if not v[2]}
    
    # Show status
    logger.info("Available Providers:")
    for name, (_, status, _) in providers.items():
        logger.info(f"  {status}")
    
    logger.info("")
    
    # If provider name provided, try to use it
    if provider_name:
        provider_name = provider_name.lower()
        
        if provider_name not in providers:
            logger.warning(f"Unknown provider: {provider_name}")
            provider_name = None
        elif not providers[provider_name][2]:
            logger.warning(f"Provider not available: {provider_name}")
            provider_name = None
        else:
            # Use the requested provider
            provider_class = providers[provider_name][0]
            if provider_class:
                logger.success(f"Using: {provider_name.upper()}")
                return provider_class()
    
    # If no valid provider selected, show interactive menu if available providers exist
    if not available:
        logger.warning("No providers available - using local processing")
        from ai.local_provider import LocalProvider
        return LocalProvider()
    
    # If only one provider available, use it
    if len(available) == 1:
        provider_name = list(available.keys())[0]
        provider_class = available[provider_name][0]
        logger.success(f"Auto-selected: {provider_name.upper()}")
        return provider_class()
    
    # Multiple providers available - show menu
    logger.info("Multiple providers available. Choose one:")
    available_list = list(available.items())
    for i, (name, (_, status, _)) in enumerate(available_list, 1):
        logger.info(f"  {i}. {status}")
    logger.info(f"  Default: 1 (will use in 5 seconds...)")
    logger.info("")
    
    try:
        # Try to get user input (with timeout)
        import sys
        if not sys.stdin.isatty():
            # Non-interactive mode (stdin redirected) - use first available
            choice = 1
        else:
            choice = input("Enter choice (1-{}): ".format(len(available_list)))
            if not choice.strip():
                choice = 1
            else:
                choice = int(choice)
        
        if 1 <= choice <= len(available_list):
            provider_name = available_list[choice - 1][0]
            provider_class = available_list[choice - 1][1][0]
            logger.success(f"Using: {provider_name.upper()}")
            return provider_class()
    except (ValueError, IndexError, EOFError):
        pass
    
    # Fallback to first available
    provider_name = available_list[0][0]
    provider_class = available_list[0][1][0]
    logger.success(f"Using: {provider_name.upper()}")
    return provider_class()


def show_provider_status(logger):
    """
    Show status of all providers (for diagnostics)
    
    Args:
        logger: Logger instance
    """
    
    logger.header("PROVIDER STATUS")
    providers = get_available_providers(logger)
    
    for name, (provider_class, status, is_available) in providers.items():
        logger.info(f"{status}")
        
        # Show missing API key hints
        if "no API key" in status:
            if name == "groq":
                logger.info(f"  → Set GROQ_API_KEY environment variable")
                logger.info(f"  → Get key: https://console.groq.com/keys")
            elif name == "openai":
                logger.info(f"  → Set OPENAI_API_KEY environment variable")
                logger.info(f"  → Get key: https://platform.openai.com/api/keys")
            elif name == "deepseek":
                logger.info(f"  → Set DEEPSEEK_API_KEY environment variable")
                logger.info(f"  → Get key: https://platform.deepseek.com/api_keys")
    
    logger.info("")
    logger.info("To use auto-generation (no API needed): use --local flag or --provider local")
