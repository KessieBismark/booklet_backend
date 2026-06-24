
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class BookAuthorsBase(BaseModel):
    """Base schema for common fields"""
    book_id: str
    author_id: str
    author_role: str

    model_config = ConfigDict(from_attributes=True)

class BookAuthorsCreate(BaseModel):
    """Schema for create operations"""
    book_id: str
    book_id: str
    author_id: str
    author_role: str

class BookAuthorsUpdate(BaseModel):
    """Schema for update operations"""
    book_id: Optional[str] = None
    author_id: Optional[str] = None
    author_role: Optional[str] = None

class BookAuthorsResponse(BaseModel):
    """Schema for API responses"""
    author_role: str
    book_id: str
    author_id: str

    model_config = ConfigDict(from_attributes=True)

class BookAuthorsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[BookAuthorsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class BookAuthorsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class BookAuthorsOrderBy(str, Enum):
    """Enum for ordering options"""
    AUTHOR_ROLE_ASC = 'author_role:asc'
    AUTHOR_ROLE_DESC = 'author_role:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'
    AUTHOR_ID_ASC = 'author_id:asc'
    AUTHOR_ID_DESC = 'author_id:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class BookAuthorsQueryParams(BaseModel):
    """Query parameters for BookAuthors"""
    filters: Optional[List[BookAuthorsFilter]] = None
    order_by: Optional[BookAuthorsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)