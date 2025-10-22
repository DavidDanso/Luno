"""
Vector Store Module
Manages ChromaDB operations for document storage and retrieval
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K_RESULTS


class VectorStoreManager:
    """Manages vector database operations using ChromaDB"""
    
    def __init__(self):
        """Initialize the vector store with embeddings and ChromaDB client"""
        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Create ChromaDB directory if it doesn't exist
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize or get collection
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize or load existing vector store"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=COLLECTION_NAME)
            
            # Create LangChain Chroma instance from existing collection
            self.vector_store = Chroma(
                client=self.client,
                collection_name=COLLECTION_NAME,
                embedding_function=self.embeddings
            )
        except Exception:
            # Collection doesn't exist, will be created when first document is added
            self.vector_store = None
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add documents to the vector store
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not documents:
                return False
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    client=self.client,
                    collection_name=COLLECTION_NAME,
                    persist_directory=CHROMA_DB_PATH
                )
            else:
                # Add documents to existing vector store
                self.vector_store.add_documents(documents)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = TOP_K_RESULTS,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search on the vector store
        
        Args:
            query: Search query string
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of most relevant Document objects
        """
        if self.vector_store is None:
            return []
        
        try:
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k
                )
            return results
            
        except Exception as e:
            raise Exception(f"Error performing similarity search: {str(e)}")
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = TOP_K_RESULTS
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of (Document, score) tuples
        """
        if self.vector_store is None:
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            return results
            
        except Exception as e:
            raise Exception(f"Error performing similarity search with scores: {str(e)}")
    
    def get_all_documents(self) -> List[str]:
        """
        Get list of all unique document sources in the vector store
        
        Returns:
            List of document source names
        """
        if self.vector_store is None:
            return []
        
        try:
            # Get the collection
            collection = self.client.get_collection(name=COLLECTION_NAME)
            
            # Get all documents
            results = collection.get()
            
            # Extract unique sources from metadata
            sources = set()
            if results and 'metadatas' in results:
                for metadata in results['metadatas']:
                    if metadata and 'source' in metadata:
                        sources.add(metadata['source'])
            
            return sorted(list(sources))
            
        except Exception as e:
            raise Exception(f"Error retrieving documents: {str(e)}")
    
    def delete_document(self, source_name: str) -> bool:
        """
        Delete all chunks of a specific document from the vector store
        
        Args:
            source_name: Name of the document source to delete
            
        Returns:
            True if successful, False otherwise
        """
        if self.vector_store is None:
            return False
        
        try:
            # Get the collection
            collection = self.client.get_collection(name=COLLECTION_NAME)
            
            # Get all IDs for documents with this source
            results = collection.get(
                where={"source": source_name}
            )
            
            if results and 'ids' in results and results['ids']:
                # Delete all chunks with this source
                collection.delete(ids=results['ids'])
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    def clear_all_documents(self) -> bool:
        """
        Clear all documents from the vector store
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection
            self.client.delete_collection(name=COLLECTION_NAME)
            
            # Reinitialize vector store
            self.vector_store = None
            
            return True
            
        except Exception as e:
            raise Exception(f"Error clearing documents: {str(e)}")
    
    def get_document_count(self) -> int:
        """
        Get total number of document chunks in the vector store
        
        Returns:
            Number of chunks
        """
        if self.vector_store is None:
            return 0
        
        try:
            collection = self.client.get_collection(name=COLLECTION_NAME)
            return collection.count()
            
        except Exception:
            return 0
    
    def get_vector_store(self) -> Optional[Chroma]:
        """
        Get the underlying vector store object for use in QA chains
        
        Returns:
            Chroma vector store instance or None
        """
        return self.vector_store
