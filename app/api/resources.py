from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from typing import List, Optional, Dict, Any
import time
import uuid
from sqlalchemy import func
import logging

from app.core.database import get_async_db
from app.core.models import Resource, TextChunk
from app.models.resources import ResourceCreate, ResourceUpdate, ResourceResponse
from app.models.search import SearchRequest, SearchResponse
from app.services.search import SearchService

logger = logging.getLogger(__name__)

router = APIRouter()
search_service = SearchService()


@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    skip: int = Query(0, ge=0, description="Number of resources to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of resources to return"),
    type: Optional[str] = Query(None, description="Filter by resource type"),
    license_type: Optional[str] = Query(None, description="Filter by license type"),
    source_platform: Optional[str] = Query(None, description="Filter by source platform"),
    language: Optional[str] = Query(None, description="Filter by language"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    db: AsyncSession = Depends(get_async_db)
):
    """List resources with pagination and filters"""
    try:
        # Build query
        query = select(Resource)
        
        # Apply filters
        filters = []
        if type:
            filters.append(Resource.type == type)
        if license_type:
            filters.append(Resource.license_type == license_type)
        if source_platform:
            filters.append(Resource.source_platform == source_platform)
        if language:
            filters.append(Resource.language == language)
        if difficulty_level:
            filters.append(Resource.difficulty_level == difficulty_level)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Add pagination and ordering
        query = query.order_by(desc(Resource.created_at)).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        resources = result.scalars().all()
        
        # Format response
        formatted_resources = []
        for resource in resources:
            formatted_resource = ResourceResponse(
                id=str(resource.id),
                title=resource.title,
                type=resource.type,
                url=resource.url,
                snippet=resource.description[:200] + "..." if resource.description and len(resource.description) > 200 else resource.description,
                license={
                    "type": resource.license_type,
                    "url": resource.license_url,
                    "attribution": resource.source_platform
                },
                source=resource.source_platform,
                relevance_score=None,
                quality_score=resource.quality_score or 0.5,
                tags=resource.tags or [],
                created_at=resource.created_at,
                updated_at=resource.updated_at
            )
            formatted_resources.append(formatted_resource)
        
        return formatted_resources
        
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific resource by ID"""
    try:
        query = select(Resource).where(Resource.id == resource_id)
        result = await db.execute(query)
        resource = result.scalar_one_or_none()
        
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return ResourceResponse(
            id=str(resource.id),
            title=resource.title,
            type=resource.type,
            url=resource.url,
            snippet=resource.description,
            license={
                "type": resource.license_type,
                "url": resource.license_url,
                "attribution": resource.source_platform
            },
            source=resource.source_platform,
            relevance_score=None,
            quality_score=resource.quality_score or 0.5,
            tags=resource.tags or [],
            created_at=resource.created_at,
            updated_at=resource.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/search", response_model=SearchResponse)
async def search_resources(
    search_request: SearchRequest
):
    """Search resources (alternative to WebSocket)"""
    try:
        return await search_service.search(search_request)
    except Exception as e:
        logger.error(f"Error searching resources: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/licenses/types")
async def list_license_types(db: AsyncSession = Depends(get_async_db)):
    """List available license types"""
    try:
        query = select(Resource.license_type).distinct()
        result = await db.execute(query)
        license_types = [row[0] for row in result.fetchall() if row[0]]
        
        return {
            "license_types": sorted(license_types),
            "count": len(license_types)
        }
    except Exception as e:
        logger.error(f"Error listing license types: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sources/platforms")
async def list_source_platforms(db: AsyncSession = Depends(get_async_db)):
    """List available source platforms"""
    try:
        query = select(Resource.source_platform).distinct()
        result = await db.execute(query)
        platforms = [row[0] for row in result.fetchall() if row[0]]
        
        return {
            "source_platforms": sorted(platforms),
            "count": len(platforms)
        }
    except Exception as e:
        logger.error(f"Error listing source platforms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/overview")
async def get_resource_stats(db: AsyncSession = Depends(get_async_db)):
    """Get resource statistics"""
    try:
        # Total resources
        total_query = select(func.count(Resource.id))
        total_result = await db.execute(total_query)
        total_resources = total_result.scalar()
        
        # Resources by type
        type_query = select(Resource.type, func.count(Resource.id)).group_by(Resource.type)
        type_result = await db.execute(type_query)
        resources_by_type = {row[0]: row[1] for row in type_result.fetchall()}
        
        # Resources by license
        license_query = select(Resource.license_type, func.count(Resource.id)).group_by(Resource.license_type)
        license_result = await db.execute(license_query)
        resources_by_license = {row[0]: row[1] for row in license_result.fetchall()}
        
        # Resources by source platform
        platform_query = select(Resource.source_platform, func.count(Resource.id)).group_by(Resource.source_platform)
        platform_result = await db.execute(platform_query)
        resources_by_platform = {row[0]: row[1] for row in platform_result.fetchall()}
        
        # Average quality score
        quality_query = select(func.avg(Resource.quality_score))
        quality_result = await db.execute(quality_query)
        avg_quality = quality_result.scalar() or 0.0
        
        return {
            "total_resources": total_resources,
            "resources_by_type": resources_by_type,
            "resources_by_license": resources_by_license,
            "resources_by_platform": resources_by_platform,
            "average_quality_score": round(avg_quality, 3),
            "last_updated": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error getting resource stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
