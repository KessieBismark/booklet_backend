
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class BookGenresBase(BaseModel):
    """Base schema for common fields"""
    book_id: str
    genre_id: str

    model_config = ConfigDict(from_attributes=True)

class BookGenresCreate(BaseModel):
    """Schema for create operations"""
    book_id: str
    book_id: str
    genre_id: str

class BookGenresUpdate(BaseModel):
    """Schema for update operations"""
    book_id: Optional[str] = None
    genre_id: Optional[str] = None

class BookGenresResponse(BaseModel):
    """Schema for API responses"""
    genre_id: str
    book_id: str

    model_config = ConfigDict(from_attributes=True)

class BookGenresListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[BookGenresResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class BookGenresFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class BookGenresOrderBy(str, Enum):
    """Enum for ordering options"""
    GENRE_ID_ASC = 'genre_id:asc'
    GENRE_ID_DESC = 'genre_id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class BookGenresQueryParams(BaseModel):
    """Query parameters for BookGenres"""
    filters: Optional[List[BookGenresFilter]] = None
    order_by: Optional[BookGenresOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)