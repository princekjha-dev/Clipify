"""
Cohere provider implementation
Support for Cohere command models
"""

import os
from typing import List, Dict, Any, Optional
from ai.base_provider import BaseProvider, ProviderConfig, Message, CompletionResponse, ModelInfo, ModelType


class CohereProvider(BaseProvider):
    """Cohere Provider - RAG & Search focused"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        try:
            import cohere
            self.client = cohere.ClientV2(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install: pip install cohere")

    def health_check(self) -> bool:
        """Verify API connection"""
        try:
            response = self.client.chat(
                model="command-r-plus",
                messages=[{"role": "user", "content": "test"}]
            )
            return bool(response)
        except Exception as e:
            print(f"Cohere health check failed: {e}")
            return False

    def get_available_models(self) -> List[ModelInfo]:
        """Get available Cohere models"""
        return [
            ModelInfo(
                id="command-r-plus",
                name="Command R+",
                provider="cohere",
                model_type=ModelType.CHAT,
                context_window=128000,
                max_tokens=4000,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                description="Flagship model for RAG and search"
            ),
            ModelInfo(
                id="command-r",
                name="Command R",
                provider="cohere",
                model_type=ModelType.CHAT,
                context_window=128000,
                max_tokens=4000,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                description="Production model"
            ),
            ModelInfo(
                id="command-light",
                name="Command Light",
                provider="cohere",
                model_type=ModelType.CHAT,
                context_window=4096,
                max_tokens=2048,
                cost_per_1k_input=0.0001,
                cost_per_1k_output=0.0003,
                description="Fast lightweight model"
            ),
        ]

    def complete(
        self,
        messages: List[Message],
        model: str = "command-r-plus",
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
            stop_sequences=stop_sequences,
            **kwargs
        )
        
        text = response.message.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        return CompletionResponse(
            text=text,
            model=model,
            provider="cohere",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            stop_reason=response.stop_reason or "stop",
            raw_response={}
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
            if hasattr(event, 'text'):
                yield event.text

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
