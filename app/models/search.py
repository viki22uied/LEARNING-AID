from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .resources import ResourceType, DifficultyLevel


class SearchFilters(BaseModel):
    license_types: Optional[List[str]] = Field(None, description="Filter by license types")
    resource_types: Optional[List[ResourceType]] = Field(None, description="Filter by resource types")
    difficulty_levels: Optional[List[DifficultyLevel]] = Field(None, description="Filter by difficulty levels")
    languages: Optional[List[str]] = Field(None, description="Filter by languages (ISO 639-1 codes)")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    source_platforms: Optional[List[str]] = Field(None, description="Filter by source platforms")


class SearchPreferences(BaseModel):
    prioritize_recent: bool = Field(default=True, description="Prioritize recently updated resources")
    include_snippets: bool = Field(default=True, description="Include text snippets in results")
    min_quality_score: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum quality score")
    semantic_search: bool = Field(default=True, description="Use semantic search instead of keyword search")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    filters: Optional[SearchFilters] = Field(default_factory=SearchFilters)
    preferences: Optional[SearchPreferences] = Field(default_factory=SearchPreferences)


class SearchResponse(BaseModel):
    query_id: str
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    processing_time_ms: int
    filters_applied: Optional[SearchFilters] = None
    search_type: str = Field(default="semantic", description="Type of search performed")


class AutoRecommendation(BaseModel):
    trigger_concept: str
    resources: List[Dict[str, Any]]
    confidence: float = Field(ge=0.0, le=1.0)


class LiveTranscript(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    is_final: bool = Field(default=False)


class LiveUpdateResponse(BaseModel):
    transcript: LiveTranscript
    auto_recommendations: Optional[List[AutoRecommendation]] = None
    processing_time_ms: int
