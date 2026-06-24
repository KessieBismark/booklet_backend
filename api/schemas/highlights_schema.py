
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class HighlightsBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    book_id: str
    chapter_id: str
    start_offset: int
    end_offset: int
    selected_text: str
    color: str
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class HighlightsCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    book_id: str
    chapter_id: str
    start_offset: int
    end_offset: int
    selected_text: str
    color: str
    note: Optional[str] = None

class HighlightsUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    selected_text: Optional[str] = None
    color: Optional[str] = None
    note: Optional[str] = None

class HighlightsResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    book_id: str
    chapter_id: str
    start_offset: int
    end_offset: int
    selected_text: str
    color: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class HighlightsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[HighlightsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class HighlightsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class HighlightsOrderBy(str, Enum):
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
    START_OFFSET_ASC = 'start_offset:asc'
    START_OFFSET_DESC = 'start_offset:desc'
    END_OFFSET_ASC = 'end_offset:asc'
    END_OFFSET_DESC = 'end_offset:desc'
    SELECTED_TEXT_ASC = 'selected_text:asc'
    SELECTED_TEXT_DESC = 'selected_text:desc'
    COLOR_ASC = 'color:asc'
    COLOR_DESC = 'color:desc'
    NOTE_ASC = 'note:asc'
    NOTE_DESC = 'note:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class HighlightsQueryParams(BaseModel):
    """Query parameters for Highlights"""
    filters: Optional[List[HighlightsFilter]] = None
    order_by: Optional[HighlightsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)