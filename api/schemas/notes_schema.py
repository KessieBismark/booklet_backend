
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class NotesBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    char_offset: Optional[int] = None
    content: str

    model_config = ConfigDict(from_attributes=True)

class NotesCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    char_offset: Optional[int] = None
    content: str

class NotesUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    char_offset: Optional[int] = None
    content: Optional[str] = None

class NotesResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    char_offset: Optional[int] = None
    content: str
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class NotesListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[NotesResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class NotesFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class NotesOrderBy(str, Enum):
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
    CONTENT_ASC = 'content:asc'
    CONTENT_DESC = 'content:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class NotesQueryParams(BaseModel):
    """Query parameters for Notes"""
    filters: Optional[List[NotesFilter]] = None
    order_by: Optional[NotesOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)