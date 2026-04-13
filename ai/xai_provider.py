"""
xAI provider implementation
Grok models with web access
"""

import os
from typing import List, Dict, Any, Optional
from ai.base_provider import BaseProvider, ProviderConfig, Message, CompletionResponse, ModelInfo, ModelType


class XAIProvider(BaseProvider):
    """xAI Provider - Grok models"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1/chat/completions"
            )
        except ImportError:
            raise ImportError("Install: pip install openai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model="grok-2",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return bool(response)
        except Exception as e:
            print(f"xAI health check failed: {e}")
            return False

    def get_available_models(self) -> List[ModelInfo]:
        """Get available xAI models"""
        return [
            ModelInfo(
                id="grok-2",
                name="Grok 2",
                provider="xai",
                model_type=ModelType.CHAT,
                context_window=128000,
                max_tokens=131072,
                cost_per_1k_input=0.002,
                cost_per_1k_output=0.01,
                description="Latest Grok model with extended context"
            ),
            ModelInfo(
                id="grok-2-mini",
                name="Grok 2 Mini",
                provider="xai",
                model_type=ModelType.CHAT,
                context_window=128000,
                max_tokens=131072,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                description="Smaller, faster Grok model"
            ),
            ModelInfo(
                id="grok-1",
                name="Grok 1",
                provider="xai",
                model_type=ModelType.CHAT,
                context_window=128000,
                max_tokens=131072,
                cost_per_1k_input=0.001,
                cost_per_1k_output=0.005,
                description="Previous generation Grok"
            ),
        ]

    def complete(
        self,
        messages: List[Message],
        model: str = "grok-2",
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
            stop=stop_sequences,
            **kwargs
        )
        
        text = response.choices[0].message.content
        input_tokens = getattr(response.usage, 'prompt_tokens', 0)
        output_tokens = getattr(response.usage, 'completion_tokens', 0)
        
        return CompletionResponse(
            text=text,
            model=model,
            provider="xai",
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
