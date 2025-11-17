import logging
from typing import List, Dict, Any, AsyncIterator, Optional
import asyncio
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Large Language Models."""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None

        # Initialize clients based on available API keys
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")

        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic client initialized")

    def build_rag_prompt(
        self,
        question: str,
        context_docs: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Build a RAG prompt with context documents.

        Args:
            question: User's question
            context_docs: Retrieved context documents
            conversation_history: Previous messages in conversation

        Returns:
            Formatted prompt string
        """
        # Format context documents
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            source = metadata.get('filename', 'Unknown')

            context_parts.append(
                f"[Document {i}] (Source: {source})\n{content}\n"
            )

        context = "\n".join(context_parts)

        # Build prompt
        prompt_parts = [
            "You are a helpful AI assistant that answers questions based on the provided context documents.",
            "",
            "Context Documents:",
            context,
            "",
        ]

        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Previous Conversation:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"{role.capitalize()}: {content}")
            prompt_parts.append("")

        prompt_parts.extend([
            f"User Question: {question}",
            "",
            "Instructions:",
            "- Answer the question based primarily on the provided context documents.",
            "- If the context doesn't contain enough information, acknowledge this limitation.",
            "- Cite specific documents when making claims (e.g., 'According to Document 1...').",
            "- Be concise but comprehensive in your answer.",
            "",
            "Answer:"
        ])

        return "\n".join(prompt_parts)

    async def generate_answer_openai(
        self,
        prompt: str,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate answer using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY.")

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                stream=stream,
                temperature=0.7,
                max_tokens=2000
            )

            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating answer with OpenAI: {str(e)}")
            raise

    async def generate_answer_anthropic(
        self,
        prompt: str,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate answer using Anthropic Claude."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Please set ANTHROPIC_API_KEY.")

        try:
            if stream:
                async with self.anthropic_client.messages.stream(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
            else:
                response = await self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                yield response.content[0].text

        except Exception as e:
            logger.error(f"Error generating answer with Anthropic: {str(e)}")
            raise

    async def generate_answer(
        self,
        question: str,
        context_docs: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        provider: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate answer using RAG.

        Args:
            question: User's question
            context_docs: Retrieved context documents
            conversation_history: Previous conversation messages
            stream: Whether to stream the response
            provider: LLM provider ('openai' or 'anthropic'). Uses default if not specified.

        Yields:
            Generated answer text (streaming or single response)
        """
        # Build RAG prompt
        prompt = self.build_rag_prompt(question, context_docs, conversation_history)

        # Determine provider
        if provider is None:
            provider = settings.DEFAULT_LLM_PROVIDER

        # Generate answer
        if provider == 'openai':
            async for chunk in self.generate_answer_openai(prompt, stream):
                yield chunk
        elif provider == 'anthropic':
            async for chunk in self.generate_answer_anthropic(prompt, stream):
                yield chunk
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")


# Global instance
llm_service = LLMService()
