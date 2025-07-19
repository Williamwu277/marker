"""
Embedding utilities for text vectorization using SentenceTransformers.
Handles model loading, text embedding, and vector operations.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from config.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages text embeddings using SentenceTransformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: Name of the SentenceTransformers model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the SentenceTransformers model."""
        try:
            logger.info(f"Loading SentenceTransformers model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            np.ndarray: Array of embeddings with shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def get_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            np.ndarray: Single embedding vector
        """
        return self.get_embeddings([text])[0]
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity score between 0 and 1
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    def batch_similarity(self, query_embedding: np.ndarray, 
                        embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate similarity between a query embedding and a batch of embeddings.
        
        Args:
            query_embedding: Query embedding vector
            embeddings: Batch of embeddings to compare against
            
        Returns:
            np.ndarray: Array of similarity scores
        """
        try:
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                return np.zeros(len(embeddings))
            
            # Normalize all embeddings
            norms = np.linalg.norm(embeddings, axis=1)
            norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
            normalized_embeddings = embeddings / norms[:, np.newaxis]
            
            # Calculate similarities
            similarities = np.dot(normalized_embeddings, query_embedding) / query_norm
            return similarities
        except Exception as e:
            logger.error(f"Failed to calculate batch similarity: {e}")
            return np.zeros(len(embeddings))
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            int: Embedding dimension
        """
        if self.model is None:
            return Config.VECTOR_DIMENSION
        return self.model.get_sentence_embedding_dimension()


# Global embedding manager instance
embedding_manager = EmbeddingManager()


def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Convenience function to get embeddings for texts.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        np.ndarray: Array of embeddings
    """
    return embedding_manager.get_embeddings(texts)


def get_single_embedding(text: str) -> np.ndarray:
    """
    Convenience function to get embedding for a single text.
    
    Args:
        text: Text string to embed
        
    Returns:
        np.ndarray: Single embedding vector
    """
    return embedding_manager.get_single_embedding(text)


def calculate_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Convenience function to calculate cosine similarity.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        float: Cosine similarity score
    """
    return embedding_manager.cosine_similarity(embedding1, embedding2) 