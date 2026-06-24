
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class QuotesBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    highlight_id: Optional[str] = None
    quote_text: str
    note: Optional[str] = None
    location_label: Optional[str] = None
    is_favorite: bool
    is_public: bool

    model_config = ConfigDict(from_attributes=True)

class QuotesCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    highlight_id: Optional[str] = None
    quote_text: str
    note: Optional[str] = None
    location_label: Optional[str] = None
    is_favorite: bool
    is_public: bool

class QuotesUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    highlight_id: Optional[str] = None
    quote_text: Optional[str] = None
    note: Optional[str] = None
    location_label: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_public: Optional[bool] = None

class QuotesResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str] = None
    highlight_id: Optional[str] = None
    quote_text: str
    note: Optional[str] = None
    location_label: Optional[str] = None
    is_favorite: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class QuotesListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[QuotesResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class QuotesFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class QuotesOrderBy(str, Enum):
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
    HIGHLIGHT_ID_ASC = 'highlight_id:asc'
    HIGHLIGHT_ID_DESC = 'highlight_id:desc'
    QUOTE_TEXT_ASC = 'quote_text:asc'
    QUOTE_TEXT_DESC = 'quote_text:desc'
    NOTE_ASC = 'note:asc'
    NOTE_DESC = 'note:desc'
    LOCATION_LABEL_ASC = 'location_label:asc'
    LOCATION_LABEL_DESC = 'location_label:desc'
    IS_FAVORITE_ASC = 'is_favorite:asc'
    IS_FAVORITE_DESC = 'is_favorite:desc'
    IS_PUBLIC_ASC = 'is_public:asc'
    IS_PUBLIC_DESC = 'is_public:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class QuotesQueryParams(BaseModel):
    """Query parameters for Quotes"""
    filters: Optional[List[QuotesFilter]] = None
    order_by: Optional[QuotesOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)