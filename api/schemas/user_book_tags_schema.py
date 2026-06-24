
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class UserBookTagsBase(BaseModel):
    """Base schema for common fields"""
    user_book_id: str
    tag_id: str

    model_config = ConfigDict(from_attributes=True)

class UserBookTagsCreate(BaseModel):
    """Schema for create operations"""
    user_book_id: str
    user_book_id: str
    tag_id: str

class UserBookTagsUpdate(BaseModel):
    """Schema for update operations"""
    user_book_id: Optional[str] = None
    tag_id: Optional[str] = None

class UserBookTagsResponse(BaseModel):
    """Schema for API responses"""
    tag_id: str
    user_book_id: str

    model_config = ConfigDict(from_attributes=True)

class UserBookTagsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[UserBookTagsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class UserBookTagsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class UserBookTagsOrderBy(str, Enum):
    """Enum for ordering options"""
    TAG_ID_ASC = 'tag_id:asc'
    TAG_ID_DESC = 'tag_id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_BOOK_ID_ASC = 'user_book_id:asc'
    USER_BOOK_ID_DESC = 'user_book_id:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class UserBookTagsQueryParams(BaseModel):
    """Query parameters for UserBookTags"""
    filters: Optional[List[UserBookTagsFilter]] = None
    order_by: Optional[UserBookTagsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)