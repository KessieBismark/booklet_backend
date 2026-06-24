
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class ReadingProgressBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    char_offset: int
    progress_percent: str
    last_device_id: Optional[str] = None
    last_read_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReadingProgressCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    char_offset: int
    progress_percent: str
    last_device_id: Optional[str] = None
    last_read_at: datetime

class ReadingProgressUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    char_offset: Optional[int] = None
    progress_percent: Optional[str] = None
    last_device_id: Optional[str] = None
    last_read_at: Optional[datetime] = None

class ReadingProgressResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    char_offset: int
    progress_percent: str
    last_device_id: Optional[str] = None
    last_read_at: datetime
    updated_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReadingProgressListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[ReadingProgressResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class ReadingProgressFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class ReadingProgressOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'
    CHAPTER_ID_ASC = 'chapter_id:asc'
    CHAPTER_ID_DESC = 'chapter_id:desc'
    CHAR_OFFSET_ASC = 'char_offset:asc'
    CHAR_OFFSET_DESC = 'char_offset:desc'
    PROGRESS_PERCENT_ASC = 'progress_percent:asc'
    PROGRESS_PERCENT_DESC = 'progress_percent:desc'
    LAST_DEVICE_ID_ASC = 'last_device_id:asc'
    LAST_DEVICE_ID_DESC = 'last_device_id:desc'
    LAST_READ_AT_ASC = 'last_read_at:asc'
    LAST_READ_AT_DESC = 'last_read_at:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class ReadingProgressQueryParams(BaseModel):
    """Query parameters for ReadingProgress"""
    filters: Optional[List[ReadingProgressFilter]] = None
    order_by: Optional[ReadingProgressOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)