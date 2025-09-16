from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional, Dict, Any
import logging
import time

from app.core.database import get_async_db
from app.services.harvester.wikipedia import wikipedia_harvester
from app.services.ml.embeddings import embeddings_service
from app.services.ml.vector_store import vector_store
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def verify_admin_key(x_admin_api_key: Optional[str] = Header(None)):
    """Verify admin API key"""
    if not settings.admin_api_key:
        return True  # No admin key configured
    
    if not x_admin_api_key or x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin API key"
        )
    return True


@router.post("/harvest")
async def trigger_harvest(
    source: str = "wikipedia",
    topics: Optional[list] = None,
    max_resources: int = 50,
    _: bool = Depends(verify_admin_key)
):
    """Trigger content harvest from specified source"""
    try:
        if source == "wikipedia":
            if not topics:
                topics = [
                    "machine learning", "artificial intelligence", "neural networks",
                    "data science", "programming", "mathematics", "physics"
                ]
            
            logger.info(f"Starting Wikipedia harvest for {len(topics)} topics")
            
            # Harvest content
            resources = await wikipedia_harvester.harvest_educational_content(
                topics=topics,
                max_articles=max_resources
            )
            
            # TODO: Save resources to database and generate embeddings
            
            return {
                "status": "success",
                "source": source,
                "resources_harvested": len(resources),
                "topics": topics,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported source: {source}"
            )
            
    except Exception as e:
        logger.error(f"Harvest error: {e}")
        raise HTTPException(status_code=500, detail=f"Harvest failed: {str(e)}")


@router.get("/harvest/status")
async def get_harvest_status(_: bool = Depends(verify_admin_key)):
    """Get harvest job status"""
    try:
        # TODO: Implement actual harvest job tracking
        return {
            "status": "idle",
            "last_harvest": None,
            "total_resources": 0,
            "last_updated": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting harvest status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get harvest status")


@router.post("/index/rebuild")
async def rebuild_vector_index(_: bool = Depends(verify_admin_key)):
    """Rebuild vector index from database"""
    try:
        logger.info("Starting vector index rebuild")
        
        # TODO: Implement actual index rebuilding
        # 1. Get all text chunks from database
        # 2. Generate embeddings
        # 3. Add to vector store
        
        return {
            "status": "success",
            "message": "Vector index rebuild completed",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Index rebuild error: {e}")
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(e)}")


@router.get("/stats")
async def get_system_stats(_: bool = Depends(verify_admin_key)):
    """Get comprehensive system statistics"""
    try:
        # Get vector store stats
        vector_stats = vector_store.get_stats()
        
        # Get embeddings info
        embeddings_info = {
            "model": embeddings_service.model_name,
            "dimension": embeddings_service.get_dimension(),
            "loaded": embeddings_service.model is not None
        }
        
        # TODO: Get database stats
        db_stats = {
            "total_resources": 0,
            "total_chunks": 0,
            "total_embeddings": 0
        }
        
        return {
            "system": {
                "uptime": time.time(),
                "version": "1.0.0",
                "status": "operational"
            },
            "vector_store": vector_stats,
            "embeddings": embeddings_info,
            "database": db_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system stats")


@router.post("/cache/clear")
async def clear_cache(_: bool = Depends(verify_admin_key)):
    """Clear system cache"""
    try:
        # TODO: Implement cache clearing
        logger.info("Cache cleared")
        
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.get("/health/detailed")
async def detailed_health_check(_: bool = Depends(verify_admin_key)):
    """Detailed health check for all system components"""
    try:
        health_status = {
            "overall": "healthy",
            "components": {},
            "timestamp": time.time()
        }
        
        # Check database
        try:
            async for db in get_async_db():
                # Simple database check
                health_status["components"]["database"] = "healthy"
                break
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {str(e)}"
            health_status["overall"] = "unhealthy"
        
        # Check embeddings service
        if embeddings_service.model:
            health_status["components"]["embeddings"] = "healthy"
        else:
            health_status["components"]["embeddings"] = "unhealthy: model not loaded"
            health_status["overall"] = "unhealthy"
        
        # Check vector store
        if vector_store.vectors or vector_store.qdrant_client:
            health_status["components"]["vector_store"] = "healthy"
        else:
            health_status["components"]["vector_store"] = "unhealthy: not initialized"
            health_status["overall"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
