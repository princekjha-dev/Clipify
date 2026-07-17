"""
Perplexity provider implementation
Web-connected reasoning with real-time search
"""

import os
from typing import List, Dict, Any, Optional
from ai.base_provider import BaseProvider, ProviderConfig, Message, CompletionResponse, ModelInfo, ModelType


class PerplexityProvider(BaseProvider):
    """Perplexity Provider - Web-connected AI"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
        except ImportError:
            raise ImportError("Install: pip install openai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model="sonar-small-online",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return bool(response)
        except Exception as e:
            print(f"Perplexity health check failed: {e}")
            return False

    def get_available_models(self) -> List[ModelInfo]:
        """Get available Perplexity models"""
        return [
            ModelInfo(
                id="sonar-pro",
                name="Sonar Pro",
                provider="perplexity",
                model_type=ModelType.CHAT,
                context_window=200000,
                max_tokens=4000,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                description="Most capable with real-time web search"
            ),
            ModelInfo(
                id="sonar-small-online",
                name="Sonar Small Online",
                provider="perplexity",
                model_type=ModelType.CHAT,
                context_window=12000,
                max_tokens=2048,
                cost_per_1k_input=0.0003,
                cost_per_1k_output=0.0009,
                description="Fast model with web search"
            ),
            ModelInfo(
                id="sonar-small-chat",
                name="Sonar Small Chat",
                provider="perplexity",
                model_type=ModelType.CHAT,
                context_window=12000,
                max_tokens=2048,
                cost_per_1k_input=0.0002,
                cost_per_1k_output=0.0006,
                description="Fast model without web search"
            ),
        ]

    def complete(
        self,
        messages: List[Message],
        model: str = "sonar-pro",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> CompletionResponse:
        """Generate completion"""
        formatted_messages = self.format_messages(messages)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens or 1024,
            **kwargs
        )
        
        text = response.choices[0].message.content
        input_tokens = getattr(response.usage, 'prompt_tokens', 0)
        output_tokens = getattr(response.usage, 'completion_tokens', 0)
        
        return CompletionResponse(
            text=text,
            model=model,
            provider="perplexity",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            stop_reason=response.choices[0].finish_reason or "stop",
        )

    def stream_complete(self, messages: List[Message], model: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs):
        """Stream completion"""
        formatted_messages = self.format_messages(messages)
        
        stream = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens or 1024,
            stream=True,
            **kwargs
        )
        
        for event in stream:
            if event.choices[0].delta.content:
                yield event.choices[0].delta.content

    def count_tokens(self, text: str, model: str) -> int:
        """Approximate token count"""
        return max(1, int(len(text) * 0.30))

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost"""
        models = {m.id: m for m in self.get_available_models()}
        if model in models:
            m = models[model]
            return (input_tokens / 1000 * m.cost_per_1k_input + 
                    output_tokens / 1000 * m.cost_per_1k_output)
        return 0.0
