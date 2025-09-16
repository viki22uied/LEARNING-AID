from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import uuid
from typing import Dict, Any

from app.config import settings
from app.core.database import init_db, close_db
from app.services.ml.embeddings import embeddings_service
from app.services.ml.vector_store import vector_store
from app.services.ml.stt import stt_service
from app.api import websocket, resources, admin
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Open Educational Resources Recommendation Backend...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Initialize ML services
        await embeddings_service.load_model()
        await vector_store.initialize(embeddings_service.get_dimension())
        await stt_service.load_model()
        logger.info("ML services initialized")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Open Educational Resources Recommendation Backend",
    description="A fully open-source, real-time educational resource recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
app.include_router(resources.router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Open Educational Resources Recommendation Backend",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": "connected",
            "embeddings": "loaded" if embeddings_service.model else "not_loaded",
            "vector_store": "initialized" if vector_store.vectors or vector_store.qdrant_client else "not_initialized",
            "stt": "loaded" if stt_service.model or stt_service.whisper_model else "not_loaded"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics for now
    return {
        "app_info": {
            "version": "1.0.0",
            "uptime": time.time()
        },
        "vector_store_stats": vector_store.get_stats(),
        "embeddings_info": {
            "model": embeddings_service.model_name,
            "dimension": embeddings_service.get_dimension()
        },
        "stt_info": stt_service.get_model_info()
    }


@app.get("/api/v1/status")
async def detailed_status():
    """Detailed system status"""
    return {
        "status": "operational",
        "timestamp": time.time(),
        "configuration": {
            "database_url": settings.database_url.split("@")[-1] if "@" in settings.database_url else "sqlite",
            "vector_db_type": settings.vector_db_type,
            "embeddings_model": settings.embeddings_model,
            "stt_model": settings.stt_model
        },
        "services": {
            "embeddings": {
                "loaded": embeddings_service.model is not None,
                "model": embeddings_service.model_name,
                "dimension": embeddings_service.get_dimension()
            },
            "vector_store": {
                "type": vector_store.vector_db_type,
                "initialized": vector_store.vectors or vector_store.qdrant_client is not None,
                "stats": vector_store.get_stats()
            },
            "stt": {
                "loaded": stt_service.model is not None or stt_service.whisper_model is not None,
                "model": stt_service.model_name,
                "use_faster_whisper": stt_service.use_faster_whisper
            }
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.log_level == "DEBUG" else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
