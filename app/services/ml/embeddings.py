from sentence_transformers import SentenceTransformer
from typing import List, Optional, Tuple
import numpy as np
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embeddings_model
        self.model = None
        self.dimension = 384  # Default for all-MiniLM-L6-v2

    async def load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading embeddings model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Set dimension based on model
            if "all-mpnet-base-v2" in self.model_name:
                self.dimension = 768
            else:
                self.dimension = 384
                
            logger.info(f"Embeddings model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not self.model:
            await self.load_model()
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            await self.load_model()
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def get_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.dimension


# Global instance
embeddings_service = EmbeddingsService()
