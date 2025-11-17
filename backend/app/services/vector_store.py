import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage vector embeddings and similarity search using ChromaDB."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"VectorStore initialized with model: {settings.EMBEDDING_MODEL}")

    def get_collection_name(self, knowledge_base_id: int) -> str:
        """Generate collection name for a knowledge base."""
        return f"kb_{knowledge_base_id}"

    def create_collection(self, knowledge_base_id: int) -> None:
        """Create a new collection for a knowledge base."""
        try:
            collection_name = self.get_collection_name(knowledge_base_id)
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={"knowledge_base_id": knowledge_base_id}
            )
            logger.info(f"Collection created: {collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise

    def delete_collection(self, knowledge_base_id: int) -> None:
        """Delete a collection."""
        try:
            collection_name = self.get_collection_name(knowledge_base_id)
            self.client.delete_collection(name=collection_name)
            logger.info(f"Collection deleted: {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise

    def add_documents(
        self,
        knowledge_base_id: int,
        document_id: int,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        Add document chunks to the vector store.

        Args:
            knowledge_base_id: ID of the knowledge base
            document_id: ID of the document
            chunks: List of text chunks with metadata

        Returns:
            Number of chunks added
        """
        try:
            collection_name = self.get_collection_name(knowledge_base_id)
            collection = self.client.get_collection(name=collection_name)

            if not chunks:
                return 0

            # Prepare data
            texts = [chunk['content'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts).tolist()

            ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    **chunk['metadata'],
                    'document_id': document_id,
                    'knowledge_base_id': knowledge_base_id,
                }
                for chunk in chunks
            ]

            # Add to collection
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            return len(chunks)

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def delete_document(self, knowledge_base_id: int, document_id: int) -> None:
        """Delete all chunks for a specific document."""
        try:
            collection_name = self.get_collection_name(knowledge_base_id)
            collection = self.client.get_collection(name=collection_name)

            # Query for all chunks of this document
            results = collection.get(
                where={"document_id": document_id}
            )

            if results and results['ids']:
                collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def search(
        self,
        knowledge_base_id: int,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            knowledge_base_id: ID of the knowledge base
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of search results with content, metadata, and scores
        """
        try:
            collection_name = self.get_collection_name(knowledge_base_id)
            collection = self.client.get_collection(name=collection_name)

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()

            # Search
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                where=filter_metadata
            )

            # Format results
            search_results = []
            if results and results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    search_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'id': results['ids'][0][i]
                    })

            return search_results

        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise

    def get_collection_stats(self, knowledge_base_id: int) -> Dict[str, Any]:
        """Get statistics about a collection."""
        try:
            collection_name = self.get_collection_name(knowledge_base_id)
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()

            return {
                'collection_name': collection_name,
                'total_chunks': count,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {'collection_name': collection_name, 'total_chunks': 0}


# Global instance
vector_store = VectorStore()
