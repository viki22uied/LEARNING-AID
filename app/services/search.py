import logging
import time
from typing import List, Dict, Any, Optional
from app.models.search import SearchRequest, SearchResponse
from app.services.ml.embeddings import embeddings_service
from app.services.ml.vector_store import vector_store
from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from app.core.models import Resource, TextChunk

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        self.embeddings_service = embeddings_service
        self.vector_store = vector_store
    
    async def search(self, search_request: SearchRequest) -> SearchResponse:
        """Perform semantic search for educational resources"""
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = await self.embeddings_service.generate_embedding(search_request.query)
            
            # Search vector store
            vector_results = await self.vector_store.search(query_embedding, k=50)
            
            # Fetch resource details from database
            resources = await self._fetch_resources([result[0] for result in vector_results])
            
            # Apply filters and scoring
            filtered_results = await self._apply_filters_and_scoring(
                resources, search_request.filters, search_request.preferences
            )
            
            # Format results
            formatted_results = []
            for resource, score in filtered_results:
                formatted_result = await self._format_search_result(resource, score)
                formatted_results.append(formatted_result)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            return SearchResponse(
                query_id=str(time.time()),
                query=search_request.query,
                results=formatted_results,
                total_results=len(formatted_results),
                processing_time_ms=processing_time,
                search_type="semantic"
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    async def _fetch_resources(self, chunk_ids: List[int]) -> List[Resource]:
        """Fetch resource details from database"""
        try:
            async for db in get_async_db():
                # Get text chunks with their resources
                query = select(TextChunk, Resource).join(
                    Resource, TextChunk.resource_id == Resource.id
                ).where(TextChunk.id.in_(chunk_ids))
                
                result = await db.execute(query)
                rows = result.fetchall()
                
                # Group by resource and return unique resources
                resources = {}
                for chunk, resource in rows:
                    if resource.id not in resources:
                        resources[resource.id] = resource
                
                return list(resources.values())
                
        except Exception as e:
            logger.error(f"Error fetching resources: {e}")
            return []
    
    async def _apply_filters_and_scoring(
        self, 
        resources: List[Resource], 
        filters: Optional[Any], 
        preferences: Optional[Any]
    ) -> List[tuple]:
        """Apply filters and calculate final scores"""
        filtered_results = []
        
        for resource in resources:
            # Check if resource passes filters
            if await self._passes_filters(resource, filters):
                # Calculate final score
                score = await self._calculate_final_score(resource, preferences)
                filtered_results.append((resource, score))
        
        # Sort by score (descending)
        filtered_results.sort(key=lambda x: x[1], reverse=True)
        
        return filtered_results
    
    async def _passes_filters(self, resource: Resource, filters: Optional[Any]) -> bool:
        """Check if resource passes all filters"""
        if not filters:
            return True
        
        # License type filter
        if filters.license_types and resource.license_type not in filters.license_types:
            return False
        
        # Resource type filter
        if filters.resource_types and resource.type not in filters.resource_types:
            return False
        
        # Difficulty level filter
        if filters.difficulty_levels and resource.difficulty_level not in filters.difficulty_levels:
            return False
        
        # Language filter
        if filters.languages and resource.language not in filters.languages:
            return False
        
        # Source platform filter
        if filters.source_platforms and resource.source_platform not in filters.source_platforms:
            return False
        
        return True
    
    async def _calculate_final_score(self, resource: Resource, preferences: Optional[Any]) -> float:
        """Calculate final relevance score for a resource"""
        base_score = resource.quality_score or 0.5
        
        # Apply preference adjustments
        if preferences:
            # Prioritize recent content
            if preferences.prioritize_recent and resource.updated_at:
                # Simple recency boost (could be more sophisticated)
                days_old = (time.time() - resource.updated_at.timestamp()) / (24 * 3600)
                if days_old < 30:  # Less than 30 days old
                    base_score += 0.1
                elif days_old < 365:  # Less than 1 year old
                    base_score += 0.05
            
            # Quality score threshold
            if preferences.min_quality_score and base_score < preferences.min_quality_score:
                return 0.0
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    async def _format_search_result(self, resource: Resource, score: float) -> Dict[str, Any]:
        """Format resource for search response"""
        return {
            "id": str(resource.id),
            "title": resource.title,
            "type": resource.type,
            "url": resource.url,
            "snippet": resource.description[:200] + "..." if resource.description and len(resource.description) > 200 else resource.description,
            "license": {
                "type": resource.license_type,
                "url": resource.license_url,
                "attribution": resource.source_platform
            },
            "source": resource.source_platform,
            "relevance_score": score,
            "quality_score": resource.quality_score or 0.5,
            "tags": resource.tags or [],
            "subject_areas": resource.subject_areas or [],
            "difficulty_level": resource.difficulty_level,
            "language": resource.language,
            "created_at": resource.created_at.isoformat() if resource.created_at else None,
            "updated_at": resource.updated_at.isoformat() if resource.updated_at else None
        }
    
    async def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search by keywords (fallback method)"""
        try:
            async for db in get_async_db():
                # Build keyword search query
                keyword_conditions = []
                for keyword in keywords:
                    keyword_conditions.append(
                        or_(
                            Resource.title.ilike(f"%{keyword}%"),
                            Resource.description.ilike(f"%{keyword}%")
                        )
                    )
                
                query = select(Resource).where(
                    and_(*keyword_conditions)
                ).order_by(desc(Resource.quality_score)).limit(limit)
                
                result = await db.execute(query)
                resources = result.scalars().all()
                
                # Format results
                formatted_results = []
                for resource in resources:
                    formatted_result = await self._format_search_result(resource, 0.5)
                    formatted_results.append(formatted_result)
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
            return []


# Global instance
search_service = SearchService()
