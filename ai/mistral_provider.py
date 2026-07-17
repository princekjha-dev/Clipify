"""
Mistral AI provider implementation
Support for Mistral models via official API
"""

import os
from typing import List, Dict, Any, Optional
from ai.base_provider import BaseProvider, ProviderConfig, Message, CompletionResponse, ModelInfo, ModelType


class MistralProvider(BaseProvider):
    """Mistral AI Provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            from mistralai.client import MistralClient
            self.client = MistralClient(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install: pip install mistralai")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": "test"}]
            )
            return bool(response)
        except Exception as e:
            print(f"Mistral health check failed: {e}")
            return False

    def get_available_models(self) -> List[ModelInfo]:
        """Get available Mistral models"""
        return [
            ModelInfo(
                id="mistral-small-latest",
                name="Mistral Small",
                provider="mistral",
                model_type=ModelType.CHAT,
                context_window=8000,
                max_tokens=8000,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00042,
                description="Fast and efficient model"
            ),
            ModelInfo(
                id="mistral-medium-latest",
                name="Mistral Medium",
                provider="mistral",
                model_type=ModelType.CHAT,
                context_window=32000,
                max_tokens=8000,
                cost_per_1k_input=0.00027,
                cost_per_1k_output=0.00081,
                description="Balanced model"
            ),
            ModelInfo(
                id="mistral-large-latest",
                name="Mistral Large",
                provider="mistral",
                model_type=ModelType.CHAT,
                context_window=32000,
                max_tokens=8000,
                cost_per_1k_input=0.0008,
                cost_per_1k_output=0.0024,
                description="Powerful reasoning model"
            ),
        ]

    def complete(
        self,
        messages: List[Message],
        model: str = "mistral-small-latest",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> CompletionResponse:
        """Generate completion"""
        formatted_messages = self.format_messages(messages)
        
        response = self.client.chat(
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
            provider="mistral",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            stop_reason=response.choices[0].finish_reason or "stop",
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else {}
        )

    def stream_complete(self, messages: List[Message], model: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs):
        """Stream completion"""
        formatted_messages = self.format_messages(messages)
        
        stream = self.client.chat_stream(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens or 1024,
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
