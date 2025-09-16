from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False)
    url = Column(Text, nullable=False)
    local_path = Column(Text, nullable=True)
    downloadable = Column(Boolean, default=False)
    
    # License information
    license_type = Column(String(100), nullable=False)
    license_url = Column(Text, nullable=True)
    
    # Source information
    source_platform = Column(String(100), nullable=True)
    authors = Column(JSONB, nullable=True)  # List of authors
    publication_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=func.now())
    
    # Content information
    description = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)  # List of tags
    subject_areas = Column(JSONB, nullable=True)  # List of subject areas
    difficulty_level = Column(String(20), nullable=True)
    language = Column(String(10), default="en")
    
    # Metadata
    file_size = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # For videos
    page_count = Column(Integer, nullable=True)  # For documents
    view_count = Column(Integer, nullable=True)
    quality_score = Column(Float, default=0.5)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_indexed = Column(DateTime, nullable=True)
    
    # Relationships
    text_chunks = relationship("TextChunk", back_populates="resource", cascade="all, delete-orphan")


class TextChunk(Base):
    __tablename__ = "text_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding_id = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    
    # Relationships
    resource = relationship("Resource", back_populates="text_chunks")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_id = Column(Integer, ForeignKey("text_chunks.id"), nullable=False)
    vector = Column(JSON, nullable=False)  # Store as JSON array for now, can be optimized with pgvector later


class HarvestJob(Base):
    __tablename__ = "harvest_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_platform = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    resources_found = Column(Integer, default=0)
    resources_processed = Column(Integer, default=0)
    errors = Column(JSONB, nullable=True)  # Store error details as JSON
    created_at = Column(DateTime, default=func.now())
