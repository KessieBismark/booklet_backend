
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class ChaptersBase(BaseModel):
    """Base schema for common fields"""
    id: str
    book_id: str
    order_index: int
    title: Optional[str] = None
    content: str
    content_format: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ChaptersCreate(BaseModel):
    """Schema for create operations"""
    id: str
    book_id: str
    order_index: int
    title: Optional[str] = None
    content: str
    content_format: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None

class ChaptersUpdate(BaseModel):
    """Schema for update operations"""
    book_id: Optional[str] = None
    order_index: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    content_format: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None

class ChaptersResponse(BaseModel):
    """Schema for API responses"""
    id: str
    book_id: str
    order_index: int
    title: Optional[str] = None
    content: str
    content_format: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ChaptersListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[ChaptersResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class ChaptersFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class ChaptersOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'
    ORDER_INDEX_ASC = 'order_index:asc'
    ORDER_INDEX_DESC = 'order_index:desc'
    TITLE_ASC = 'title:asc'
    TITLE_DESC = 'title:desc'
    CONTENT_ASC = 'content:asc'
    CONTENT_DESC = 'content:desc'
    CONTENT_FORMAT_ASC = 'content_format:asc'
    CONTENT_FORMAT_DESC = 'content_format:desc'
    WORD_COUNT_ASC = 'word_count:asc'
    WORD_COUNT_DESC = 'word_count:desc'
    CHAR_COUNT_ASC = 'char_count:asc'
    CHAR_COUNT_DESC = 'char_count:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class ChaptersQueryParams(BaseModel):
    """Query parameters for Chapters"""
    filters: Optional[List[ChaptersFilter]] = None
    order_by: Optional[ChaptersOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)