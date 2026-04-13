"""
Fireworks AI provider implementation
Fastest open-source inference
"""

import os
from typing import List, Dict, Any, Optional
from ai.base_provider import BaseProvider, ProviderConfig, Message, CompletionResponse, ModelInfo, ModelType


class FireworksProvider(BaseProvider):
    """Fireworks AI Provider - Fast inference"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            from fireworks.client import Fireworks
            self.client = Fireworks(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install: pip install fireworks-ai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat.completions.create(
                model="accounts/fireworks/models/llama-v2-7b-chat",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return bool(response)
        except Exception as e:
            print(f"Fireworks health check failed: {e}")
            return False

    def get_available_models(self) -> List[ModelInfo]:
        """Get available Fireworks models"""
        return [
            ModelInfo(
                id="accounts/fireworks/models/llama-v2-70b-chat",
                name="Llama 2 70B Chat",
                provider="fireworks",
                model_type=ModelType.CHAT,
                context_window=4096,
                max_tokens=4096,
                cost_per_1k_input=0.0009,
                cost_per_1k_output=0.0009,
            ),
            ModelInfo(
                id="accounts/fireworks/models/llama-v2-13b-chat",
                name="Llama 2 13B Chat",
                provider="fireworks",
                model_type=ModelType.CHAT,
                context_window=4096,
                max_tokens=4096,
                cost_per_1k_input=0.0002,
                cost_per_1k_output=0.0002,
            ),
            ModelInfo(
                id="accounts/fireworks/models/llama-v2-7b-chat",
                name="Llama 2 7B Chat",
                provider="fireworks",
                model_type=ModelType.CHAT,
                context_window=4096,
                max_tokens=4096,
                cost_per_1k_input=0.00008,
                cost_per_1k_output=0.00008,
            ),
        ]

    def complete(
        self,
        messages: List[Message],
        model: str = "accounts/fireworks/models/llama-v2-70b-chat",
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
            provider="fireworks",
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
        return max(1, int(len(text) * 0.28))

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost"""
        models = {m.id: m for m in self.get_available_models()}
        if model in models:
            m = models[model]
            return (input_tokens / 1000 * m.cost_per_1k_input + 
                    output_tokens / 1000 * m.cost_per_1k_output)
        return 0.0
