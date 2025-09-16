import faiss
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
from app.services.ml.embeddings import embeddings_service

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available, using numpy-based similarity")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("Qdrant not available")


class VectorStore:
    def __init__(self, vector_db_type: Optional[str] = None):
        self.vector_db_type = vector_db_type or settings.vector_db_type
        self.dimension = 384  # Default dimension
        self.index = None
        self.qdrant_client = None
        self.vectors = []
        self.metadata = []
        
    async def initialize(self, dimension: int = 384):
        """Initialize the vector store"""
        self.dimension = dimension
        
        if self.vector_db_type == "qdrant" and QDRANT_AVAILABLE:
            await self._init_qdrant()
        elif self.vector_db_type == "faiss" and FAISS_AVAILABLE:
            await self._init_faiss()
        else:
            await self._init_simple()
            
        logger.info(f"Vector store initialized with type: {self.vector_db_type}")
    
    async def _init_qdrant(self):
        """Initialize Qdrant vector database"""
        try:
            self.qdrant_client = QdrantClient(settings.qdrant_url)
            
            # Create collection if it doesn't exist
            collections = self.qdrant_client.get_collections()
            collection_name = "open_edu_vectors"
            
            if collection_name not in [c.name for c in collections.collections]:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
                )
                logger.info("Created Qdrant collection: open_edu_vectors")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            await self._init_simple()
    
    async def _init_faiss(self):
        """Initialize FAISS index"""
        try:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            logger.info("FAISS index initialized")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
            await self._init_simple()
    
    async def _init_simple(self):
        """Initialize simple numpy-based storage"""
        self.vectors = []
        self.metadata = []
        logger.info("Using simple vector storage")
    
    async def add_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        """Add vectors to the store"""
        if not vectors:
            return
            
        if self.vector_db_type == "qdrant" and self.qdrant_client:
            await self._add_to_qdrant(vectors, metadata)
        elif self.vector_db_type == "faiss" and self.index:
            await self._add_to_faiss(vectors, metadata)
        else:
            await self._add_to_simple(vectors, metadata)
    
    async def _add_to_qdrant(self, vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        """Add vectors to Qdrant"""
        try:
            points = []
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                point = PointStruct(
                    id=len(self.vectors) + i,
                    vector=vector,
                    payload=meta
                )
                points.append(point)
            
            self.qdrant_client.upsert(
                collection_name="open_edu_vectors",
                points=points
            )
            logger.info(f"Added {len(vectors)} vectors to Qdrant")
        except Exception as e:
            logger.error(f"Error adding to Qdrant: {e}")
    
    async def _add_to_faiss(self, vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        """Add vectors to FAISS"""
        try:
            vectors_array = np.array(vectors, dtype=np.float32)
            self.index.add(vectors_array)
            self.metadata.extend(metadata)
            logger.info(f"Added {len(vectors)} vectors to FAISS")
        except Exception as e:
            logger.error(f"Error adding to FAISS: {e}")
    
    async def _add_to_simple(self, vectors: List[List[float]], metadata: List[Dict[str, Any]]):
        """Add vectors to simple storage"""
        self.vectors.extend(vectors)
        self.metadata.extend(metadata)
        logger.info(f"Added {len(vectors)} vectors to simple storage")
    
    async def search(self, query_vector: List[float], k: int = 10) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Search for similar vectors"""
        if self.vector_db_type == "qdrant" and self.qdrant_client:
            return await self._search_qdrant(query_vector, k)
        elif self.vector_db_type == "faiss" and self.index:
            return await self._search_faiss(query_vector, k)
        else:
            return await self._search_simple(query_vector, k)
    
    async def _search_qdrant(self, query_vector: List[float], k: int) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Search in Qdrant"""
        try:
            results = self.qdrant_client.search(
                collection_name="open_edu_vectors",
                query_vector=query_vector,
                limit=k
            )
            
            return [(r.id, r.score, r.payload) for r in results]
        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            return []
    
    async def _search_faiss(self, query_vector: List[float], k: int) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Search in FAISS"""
        try:
            query_array = np.array([query_vector], dtype=np.float32)
            scores, indices = self.index.search(query_array, k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.metadata):
                    results.append((int(idx), float(score), self.metadata[idx]))
            
            return results
        except Exception as e:
            logger.error(f"Error searching FAISS: {e}")
            return []
    
    async def _search_simple(self, query_vector: List[float], k: int) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Search in simple storage"""
        if not self.vectors:
            return []
        
        try:
            query_array = np.array(query_vector)
            similarities = []
            
            for i, vector in enumerate(self.vectors):
                vector_array = np.array(vector)
                similarity = np.dot(query_array, vector_array) / (
                    np.linalg.norm(query_array) * np.linalg.norm(vector_array)
                )
                similarities.append((i, similarity))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = []
            
            for i, (idx, score) in enumerate(similarities[:k]):
                if idx < len(self.metadata):
                    results.append((idx, score, self.metadata[idx]))
            
            return results
        except Exception as e:
            logger.error(f"Error in simple search: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        stats = {
            "type": self.vector_db_type,
            "dimension": self.dimension,
            "total_vectors": len(self.vectors) if self.vectors else 0
        }
        
        if self.vector_db_type == "qdrant" and self.qdrant_client:
            try:
                collection_info = self.qdrant_client.get_collection("open_edu_vectors")
                stats["qdrant_vectors"] = collection_info.vectors_count
            except:
                pass
        
        return stats


# Global instance
vector_store = VectorStore()
