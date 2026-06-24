
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class BooksBase(BaseModel):
    """Base schema for common fields"""
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    published_on: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    est_reading_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class BooksCreate(BaseModel):
    """Schema for create operations"""
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    published_on: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    est_reading_minutes: Optional[int] = None

class BooksUpdate(BaseModel):
    """Schema for update operations"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    published_on: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    est_reading_minutes: Optional[int] = None

class BooksResponse(BaseModel):
    """Schema for API responses"""
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    published_on: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    est_reading_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class BooksListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[BooksResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class BooksFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class BooksOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    TITLE_ASC = 'title:asc'
    TITLE_DESC = 'title:desc'
    SUBTITLE_ASC = 'subtitle:asc'
    SUBTITLE_DESC = 'subtitle:desc'
    DESCRIPTION_ASC = 'description:asc'
    DESCRIPTION_DESC = 'description:desc'
    ISBN_ASC = 'isbn:asc'
    ISBN_DESC = 'isbn:desc'
    LANGUAGE_ASC = 'language:asc'
    LANGUAGE_DESC = 'language:desc'
    PUBLISHER_ASC = 'publisher:asc'
    PUBLISHER_DESC = 'publisher:desc'
    PUBLISHED_ON_ASC = 'published_on:asc'
    PUBLISHED_ON_DESC = 'published_on:desc'
    COVER_IMAGE_URL_ASC = 'cover_image_url:asc'
    COVER_IMAGE_URL_DESC = 'cover_image_url:desc'
    WORD_COUNT_ASC = 'word_count:asc'
    WORD_COUNT_DESC = 'word_count:desc'
    CHAPTER_COUNT_ASC = 'chapter_count:asc'
    CHAPTER_COUNT_DESC = 'chapter_count:desc'
    EST_READING_MINUTES_ASC = 'est_reading_minutes:asc'
    EST_READING_MINUTES_DESC = 'est_reading_minutes:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class BooksQueryParams(BaseModel):
    """Query parameters for Books"""
    filters: Optional[List[BooksFilter]] = None
    order_by: Optional[BooksOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)