"""
ChromaDB Vector Database and HuggingFace Embeddings Integration.
Week 2 Implementation: Persistent ChromaDB client, sentence-transformers/all-MiniLM-L6-v2,
batch upload, and top-4 similarity search.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import settings, DB_DIR

# Initialize embedding model singleton
_embedding_model = None

def get_embedding_model():
    """
    Returns HuggingFaceEmbeddings using 'sentence-transformers/all-MiniLM-L6-v2'.
    Cached as a singleton for fast query response.
    """
    global _embedding_model
    if _embedding_model is None:
        print(f"[*] Initializing embedding model: {settings.EMBEDDING_MODEL_NAME}...")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("[+] Embedding model ready.")
    return _embedding_model


class VectorStoreManager:
    """Manages persistent ChromaDB vector store for legislative documents."""
    
    def __init__(self, persist_dir: Optional[str] = None, collection_name: Optional[str] = None):
        self.persist_dir = persist_dir or str(DB_DIR)
        self.collection_name = collection_name or settings.COLLECTION_NAME
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Persistent ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        self.embeddings = get_embedding_model()
        
        # LangChain Chroma wrapper
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )
        
    def batch_upload_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Batch uploads chunks into ChromaDB with deterministic IDs and rich metadata.
        Returns the number of chunks added/updated.
        """
        if not chunks:
            return 0
            
        documents = []
        ids = []
        
        for c in chunks:
            doc = Document(
                page_content=c["content"],
                metadata={
                    "chunk_id": c.get("chunk_id", ""),
                    "source": c.get("source", "unknown"),
                    "page_number": int(c.get("page_number", 1)),
                    "section": c.get("section", "General"),
                    "char_count": int(c.get("char_count", len(c["content"]))),
                    "word_count": int(c.get("word_count", len(c["content"].split())))
                }
            )
            documents.append(doc)
            ids.append(c["chunk_id"])
            
        # Add to Chroma vector store
        self.vector_store.add_documents(documents=documents, ids=ids)
        print(f"[+] Successfully uploaded {len(documents)} chunks to ChromaDB collection '{self.collection_name}'")
        return len(documents)

    def similarity_search(
        self,
        query: str,
        top_k: int = settings.SIMILARITY_TOP_K,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches ChromaDB for the top-k most relevant chunks.
        Returns structured list with content, metadata, page numbers, and similarity scores.
        """
        # Similarity search with relevance score
        results_with_scores = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=top_k,
            filter=filter_dict
        )
        
        formatted_results = []
        for doc, score in results_with_scores:
            formatted_results.append({
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "source": doc.metadata.get("source", ""),
                "page_number": doc.metadata.get("page_number", 1),
                "section": doc.metadata.get("section", ""),
                "relevance_score": round(float(score), 4) if score is not None else 1.0,
                "content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return formatted_results

    def get_as_retriever(self, top_k: int = settings.SIMILARITY_TOP_K, filter_dict: Optional[Dict] = None):
        """Returns a LangChain retriever for RAG pipelines."""
        search_kwargs = {"k": top_k}
        if filter_dict:
            search_kwargs["filter"] = filter_dict
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """Returns vector store stats: count of documents, collections."""
        collection = self.chroma_client.get_collection(self.collection_name)
        count = collection.count()
        return {
            "collection_name": self.collection_name,
            "persist_directory": self.persist_dir,
            "total_chunks_indexed": count,
            "embedding_model": settings.EMBEDDING_MODEL_NAME
        }

    def clear(self):
        """Clears the collection."""
        try:
            self.chroma_client.delete_collection(self.collection_name)
            # Recreate vector store
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )
            print(f"[+] Collection '{self.collection_name}' reset.")
        except Exception as e:
            print(f"[!] Warning clearing collection: {e}")
