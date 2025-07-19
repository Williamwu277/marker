"""
FAISS index utility for vector storage and retrieval.
Handles index creation, storage, and similarity search operations.
"""

import logging
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
from config.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class FAISSIndex:
    """Manages FAISS vector index for similarity search."""
    
    def __init__(self, dimension: int = None, index_path: str = None):
        """
        Initialize the FAISS index.
        
        Args:
            dimension: Dimension of the vectors
            index_path: Path to save/load the index
        """
        self.dimension = dimension or Config.VECTOR_DIMENSION
        self.index_path = index_path or Config.FAISS_INDEX_PATH
        self.index = None
        self.metadata = []
        self._initialize_index()
    
    def _initialize_index(self) -> None:
        """Initialize or load the FAISS index."""
        try:
            if os.path.exists(self.index_path):
                self._load_index()
                logger.info(f"Loaded existing FAISS index from {self.index_path}")
            else:
                self._create_new_index()
                logger.info(f"Created new FAISS index with dimension {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        try:
            # Create a flat index for exact search
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
            logger.info("Created new FAISS index")
        except Exception as e:
            logger.error(f"Failed to create new index: {e}")
            raise
    
    def _load_index(self) -> None:
        """Load existing index and metadata."""
        try:
            # Load the index
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            metadata_path = f"{self.index_path}_metadata.pkl"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                self.metadata = []
                
            logger.info(f"Loaded index with {self.index.ntotal} vectors and {len(self.metadata)} metadata entries")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise
    
    def _save_index(self) -> None:
        """Save the index and metadata."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save the index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            metadata_path = f"{self.index_path}_metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
                
            logger.info(f"Saved index with {self.index.ntotal} vectors to {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def add_vectors(self, vectors: np.ndarray, metadata_list: List[Dict[str, Any]]) -> None:
        """
        Add vectors and their metadata to the index.
        
        Args:
            vectors: Array of vectors to add
            metadata_list: List of metadata dictionaries for each vector
        """
        if len(vectors) != len(metadata_list):
            raise ValueError("Number of vectors must match number of metadata entries")
        
        if len(vectors) == 0:
            return
        
        try:
            # Add vectors to index
            self.index.add(vectors)
            
            # Add metadata
            self.metadata.extend(metadata_list)
            
            logger.info(f"Added {len(vectors)} vectors to index")
        except Exception as e:
            logger.error(f"Failed to add vectors to index: {e}")
            raise
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Search for similar vectors in the index.
        
        Args:
            query_vector: Query vector to search for
            k: Number of results to return
            
        Returns:
            Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]: 
                (distances, indices, metadata_list)
        """
        if self.index.ntotal == 0:
            return np.array([]), np.array([]), []
        
        try:
            # Reshape query vector if needed
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Search the index
            distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Get metadata for returned indices
            metadata_results = []
            for idx in indices[0]:
                if idx < len(self.metadata):
                    metadata_results.append(self.metadata[idx])
                else:
                    metadata_results.append({})
            
            logger.debug(f"Found {len(indices[0])} similar vectors")
            return distances[0], indices[0], metadata_results
            
        except Exception as e:
            logger.error(f"Failed to search index: {e}")
            return np.array([]), np.array([]), []
    
    def search_by_text(self, text: str, k: int = 5, embedding_func=None) -> List[Dict[str, Any]]:
        """
        Search for similar content by text (converts to embedding first).
        
        Args:
            text: Text to search for
            k: Number of results to return
            embedding_func: Function to convert text to embedding
            
        Returns:
            List[Dict[str, Any]]: List of similar content with metadata
        """
        if embedding_func is None:
            logger.error("Embedding function is required for text search")
            return []
        
        try:
            # Convert text to embedding
            query_embedding = embedding_func(text)
            
            # Search the index
            distances, indices, metadata_list = self.search(query_embedding, k)
            
            # Combine results
            results = []
            for i, (distance, metadata) in enumerate(zip(distances, metadata_list)):
                if metadata:
                    result = metadata.copy()
                    result['similarity_score'] = float(distance)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by text: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dict[str, Any]: Index statistics
        """
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'metadata_entries': len(self.metadata),
            'index_path': self.index_path,
            'is_trained': self.index.is_trained if self.index else False
        }
    
    def clear(self) -> None:
        """Clear all vectors and metadata from the index."""
        try:
            self._create_new_index()
            logger.info("Cleared FAISS index")
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            raise
    
    def save(self) -> None:
        """Save the current index and metadata."""
        self._save_index()
    
    def get_metadata_by_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific vector ID.
        
        Args:
            vector_id: ID of the vector
            
        Returns:
            Optional[Dict[str, Any]]: Metadata for the vector, or None if not found
        """
        if 0 <= vector_id < len(self.metadata):
            return self.metadata[vector_id]
        return None
    
    def filter_by_metadata(self, filter_func) -> List[int]:
        """
        Get vector IDs that match a filter function.
        
        Args:
            filter_func: Function that takes metadata and returns bool
            
        Returns:
            List[int]: List of vector IDs that match the filter
        """
        matching_ids = []
        for i, metadata in enumerate(self.metadata):
            if filter_func(metadata):
                matching_ids.append(i)
        return matching_ids


# Global FAISS index instance
faiss_index = FAISSIndex()


def add_to_index(vectors: np.ndarray, metadata_list: List[Dict[str, Any]]) -> None:
    """
    Convenience function to add vectors to the index.
    
    Args:
        vectors: Array of vectors to add
        metadata_list: List of metadata dictionaries
    """
    faiss_index.add_vectors(vectors, metadata_list)


def search_index(query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
    """
    Convenience function to search the index.
    
    Args:
        query_vector: Query vector
        k: Number of results
        
    Returns:
        Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]: Search results
    """
    return faiss_index.search(query_vector, k)


def search_by_text(text: str, k: int = 5, embedding_func=None) -> List[Dict[str, Any]]:
    """
    Convenience function to search by text.
    
    Args:
        text: Text to search for
        k: Number of results
        embedding_func: Function to convert text to embedding
        
    Returns:
        List[Dict[str, Any]]: Search results
    """
    return faiss_index.search_by_text(text, k, embedding_func) 