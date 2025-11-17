"""
RAG (Retrieval-Augmented Generation) engine
"""
from typing import List, Dict, Any, Iterator, Optional
from .vector_store import VectorStore
from .llm_client import LLMClient
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine"""

    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_client = LLMClient()

    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results as context"""
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results, 1):
            doc_text = result['document']
            metadata = result.get('metadata', {})
            filename = metadata.get('filename', 'Unknown')
            score = result.get('score', 0)

            context_parts.append(
                f"[文档 {i}] {filename} (相关度: {score:.2f})\n{doc_text}\n"
            )

        return "\n".join(context_parts)

    def _build_prompt(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build prompt with context for RAG"""
        system_message = """你是一个智能知识助手。你的任务是基于提供的文档内容回答用户问题。

请遵循以下原则：
1. 优先使用提供的文档内容来回答问题
2. 如果文档中没有相关信息，请明确说明
3. 回答要准确、清晰、有条理
4. 可以引用文档编号来支持你的回答
5. 如果需要，可以结合你的知识进行补充说明"""

        messages = [{"role": "system", "content": system_message}]

        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)

        # Add context and current query
        user_message = f"""参考文档：
{context}

用户问题：{query}

请基于上述文档内容回答问题。"""

        messages.append({"role": "user", "content": user_message})

        return messages

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents

        Args:
            query: User query
            top_k: Number of results to retrieve
            threshold: Similarity threshold

        Returns:
            List of search results
        """
        top_k = top_k or settings.RETRIEVAL_TOP_K
        threshold = threshold or settings.SIMILARITY_THRESHOLD

        results = self.vector_store.search(query, top_k=top_k)

        # Filter by threshold
        filtered_results = [
            r for r in results
            if r.get('score', 0) >= threshold
        ]

        return filtered_results

    def generate(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        model: Optional[str] = None,
        stream: bool = False,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Any:
        """
        Generate answer using LLM

        Args:
            query: User query
            context_docs: Retrieved context documents
            model: LLM model to use
            stream: Enable streaming
            chat_history: Previous chat messages

        Returns:
            Generated answer or iterator for streaming
        """
        # Format context
        context = self._format_context(context_docs)

        # Build messages
        messages = self._build_prompt(query, context, chat_history)

        # Generate response
        try:
            response = self.llm_client.chat(
                messages=messages,
                model=model,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise

    def chat(
        self,
        query: str,
        use_rag: bool = True,
        top_k: int = None,
        model: Optional[str] = None,
        stream: bool = False,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Any:
        """
        Chat with RAG support

        Args:
            query: User query
            use_rag: Whether to use RAG (retrieval)
            top_k: Number of documents to retrieve
            model: LLM model to use
            stream: Enable streaming
            chat_history: Previous chat messages

        Returns:
            Response text or iterator for streaming
        """
        context_docs = []

        if use_rag:
            # Retrieve relevant documents
            context_docs = self.retrieve(query, top_k=top_k)
            logger.info(f"Retrieved {len(context_docs)} documents for query: {query}")

        # Generate response
        return self.generate(
            query=query,
            context_docs=context_docs,
            model=model,
            stream=stream,
            chat_history=chat_history
        )

    def chat_stream(
        self,
        query: str,
        use_rag: bool = True,
        top_k: int = None,
        model: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Chat with streaming response and metadata

        Yields:
            Dict with 'type' and 'data' fields
        """
        context_docs = []

        if use_rag:
            # Retrieve relevant documents
            context_docs = self.retrieve(query, top_k=top_k)

            # Yield retrieval results
            yield {
                "type": "retrieval",
                "data": {
                    "count": len(context_docs),
                    "documents": [
                        {
                            "filename": doc.get("metadata", {}).get("filename", "Unknown"),
                            "score": doc.get("score", 0),
                            "preview": doc.get("document", "")[:100]
                        }
                        for doc in context_docs
                    ]
                }
            }

        # Generate streaming response
        response_iterator = self.generate(
            query=query,
            context_docs=context_docs,
            model=model,
            stream=True,
            chat_history=chat_history
        )

        # Yield text chunks
        for text_chunk in response_iterator:
            yield {
                "type": "text",
                "data": {"text": text_chunk}
            }

        # Yield completion
        yield {
            "type": "done",
            "data": {}
        }
