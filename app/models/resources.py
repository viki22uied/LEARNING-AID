from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ResourceType(str, Enum):
    DOCUMENT = "document"
    VIDEO = "video"
    ARTICLE = "article"
    COURSE = "course"
    INTERACTIVE = "interactive"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LicenseInfo(BaseModel):
    type: str = Field(..., description="License type (e.g., 'CC-BY-4.0', 'Public Domain')")
    url: Optional[HttpUrl] = Field(None, description="License deed URL")
    attribution_required: bool = Field(default=True)
    commercial_use_allowed: bool = Field(default=True)
    derivative_works_allowed: bool = Field(default=True)


class SourceInfo(BaseModel):
    platform: str = Field(..., description="Source platform (e.g., 'OpenStax', 'Wikipedia')")
    authors: List[str] = Field(default_factory=list)
    publication_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class ContentInfo(BaseModel):
    description: str = Field(..., max_length=500)
    tags: List[str] = Field(default_factory=list)
    subject_areas: List[str] = Field(default_factory=list)
    difficulty_level: Optional[DifficultyLevel] = None
    language: str = Field(default="en", description="ISO 639-1 code")


class IndexingInfo(BaseModel):
    text_chunks: List[str] = Field(default_factory=list)
    embedding_ids: List[int] = Field(default_factory=list)
    last_indexed: Optional[datetime] = None
    chunk_count: int = Field(default=0)


class MetadataInfo(BaseModel):
    file_size: Optional[int] = Field(None, description="File size in bytes")
    duration: Optional[int] = Field(None, description="Duration in seconds (for videos)")
    page_count: Optional[int] = Field(None, description="Page count (for documents)")
    view_count: Optional[int] = Field(None, description="View count")
    quality_score: float = Field(default=0.5, ge=0.0, le=1.0)


class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., max_length=500)
    type: ResourceType
    url: HttpUrl
    local_path: Optional[str] = None
    downloadable: bool = Field(default=False)
    license: LicenseInfo
    source: SourceInfo
    content: ContentInfo
    indexing: IndexingInfo = Field(default_factory=IndexingInfo)
    metadata: MetadataInfo = Field(default_factory=MetadataInfo)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResourceCreate(BaseModel):
    title: str = Field(..., max_length=500)
    type: ResourceType
    url: HttpUrl
    local_path: Optional[str] = None
    downloadable: bool = Field(default=False)
    license: LicenseInfo
    source: SourceInfo
    content: ContentInfo
    metadata: Optional[MetadataInfo] = None


class ResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    type: Optional[ResourceType] = None
    url: Optional[HttpUrl] = None
    local_path: Optional[str] = None
    downloadable: Optional[bool] = None
    license: Optional[LicenseInfo] = None
    source: Optional[SourceInfo] = None
    content: Optional[ContentInfo] = None
    metadata: Optional[MetadataInfo] = None


class ResourceResponse(BaseModel):
    id: str
    title: str
    type: ResourceType
    url: str
    snippet: Optional[str] = None
    license: LicenseInfo
    source: str
    relevance_score: Optional[float] = None
    quality_score: float
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
