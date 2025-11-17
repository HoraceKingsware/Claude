"""
Vector store service using ChromaDB and sentence-transformers
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..core.config import settings


class VectorStore:
    """Vector database operations using ChromaDB"""

    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_document(
        self,
        document_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add document to vector store

        Args:
            document_id: Document ID
            content: Document content
            metadata: Additional metadata

        Returns:
            Number of chunks created
        """
        # Split text into chunks
        chunks = self.text_splitter.split_text(content)

        if not chunks:
            return 0

        # Generate chunk IDs
        chunk_ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Generate embeddings
        embeddings = self._generate_embeddings(chunks)

        # Prepare metadata
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "document_id": document_id,
                "chunk_index": i,
                "chunk_text": chunk[:200],  # Store preview
                **(metadata or {})
            }
            metadatas.append(chunk_metadata)

        # Add to collection
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search similar documents

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filter

        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )

        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'score': 1 - results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)

        return formatted_results

    def delete_document(self, document_id: int):
        """Delete all chunks of a document"""
        self.collection.delete(
            where={"document_id": document_id}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }

    def clear(self):
        """Clear all documents from collection"""
        self.client.delete_collection(name="documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
