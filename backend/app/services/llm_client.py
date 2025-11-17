"""
LLM client for Zhipu AI and Anthropic Claude
"""
from typing import Optional, Iterator, Dict, Any
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client with support for multiple providers"""

    def __init__(self):
        self.zhipu_client = None
        self.anthropic_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize LLM API clients"""
        # Initialize Zhipu AI
        if settings.ZHIPU_API_KEY:
            try:
                from zhipuai import ZhipuAI
                self.zhipu_client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
                logger.info("Zhipu AI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Zhipu AI client: {e}")

        # Initialize Anthropic
        if settings.ANTHROPIC_API_KEY:
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")

    def chat(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Any:
        """
        Send chat request to LLM

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (auto-detect provider)
            stream: Enable streaming
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Response text or iterator for streaming
        """
        model = model or settings.ZHIPU_MODEL
        temperature = temperature or settings.LLM_TEMPERATURE
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS

        # Determine provider based on model name
        if model.startswith("glm"):
            return self._chat_zhipu(messages, model, stream, temperature, max_tokens)
        elif model.startswith("claude"):
            return self._chat_anthropic(messages, model, stream, temperature, max_tokens)
        else:
            # Default to Zhipu AI
            return self._chat_zhipu(messages, model, stream, temperature, max_tokens)

    def _chat_zhipu(
        self,
        messages: list[Dict[str, str]],
        model: str,
        stream: bool,
        temperature: float,
        max_tokens: int
    ) -> Any:
        """Chat with Zhipu AI GLM models"""
        if not self.zhipu_client:
            raise ValueError("Zhipu AI client not initialized. Please set ZHIPU_API_KEY.")

        try:
            response = self.zhipu_client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=settings.LLM_TOP_P
            )

            if stream:
                return self._stream_zhipu_response(response)
            else:
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Zhipu AI API error: {e}")
            raise

    def _stream_zhipu_response(self, response) -> Iterator[str]:
        """Stream Zhipu AI response"""
        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content

    def _chat_anthropic(
        self,
        messages: list[Dict[str, str]],
        model: str,
        stream: bool,
        temperature: float,
        max_tokens: int
    ) -> Any:
        """Chat with Anthropic Claude models"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Please set ANTHROPIC_API_KEY.")

        try:
            # Convert messages format (Anthropic expects specific format)
            system_message = None
            anthropic_messages = []

            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    anthropic_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })

            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": anthropic_messages
            }

            if system_message:
                kwargs["system"] = system_message

            if stream:
                response = self.anthropic_client.messages.stream(**kwargs)
                return self._stream_anthropic_response(response)
            else:
                response = self.anthropic_client.messages.create(**kwargs)
                return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _stream_anthropic_response(self, response) -> Iterator[str]:
        """Stream Anthropic response"""
        with response as stream:
            for text in stream.text_stream:
                yield text

    def get_available_models(self) -> Dict[str, list[str]]:
        """Get list of available models"""
        models = {
            "zhipu": [],
            "anthropic": []
        }

        if self.zhipu_client:
            models["zhipu"] = [
                settings.ZHIPU_MODEL,
                settings.ZHIPU_MODEL_PLUS
            ]

        if self.anthropic_client:
            models["anthropic"] = [
                settings.ANTHROPIC_MODEL
            ]

        return models
