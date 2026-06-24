
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class CollectionBooksBase(BaseModel):
    """Base schema for common fields"""
    collection_id: str
    book_id: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CollectionBooksCreate(BaseModel):
    """Schema for create operations"""
    collection_id: str
    collection_id: str
    book_id: str
    added_at: datetime

class CollectionBooksUpdate(BaseModel):
    """Schema for update operations"""
    collection_id: Optional[str] = None
    book_id: Optional[str] = None
    added_at: Optional[datetime] = None

class CollectionBooksResponse(BaseModel):
    """Schema for API responses"""
    book_id: str
    collection_id: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CollectionBooksListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[CollectionBooksResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class CollectionBooksFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class CollectionBooksOrderBy(str, Enum):
    """Enum for ordering options"""
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    COLLECTION_ID_ASC = 'collection_id:asc'
    COLLECTION_ID_DESC = 'collection_id:desc'
    ADDED_AT_ASC = 'added_at:asc'
    ADDED_AT_DESC = 'added_at:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class CollectionBooksQueryParams(BaseModel):
    """Query parameters for CollectionBooks"""
    filters: Optional[List[CollectionBooksFilter]] = None
    order_by: Optional[CollectionBooksOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)