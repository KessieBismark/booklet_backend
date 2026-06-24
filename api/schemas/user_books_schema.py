
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class UserBooksBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    book_id: str
    status: str
    is_favorite: bool
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserBooksCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    book_id: str
    status: str
    is_favorite: bool
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    added_at: datetime

class UserBooksUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    book_id: Optional[str] = None
    status: Optional[str] = None
    is_favorite: Optional[bool] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    added_at: Optional[datetime] = None

class UserBooksResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    book_id: str
    status: str
    is_favorite: bool
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    added_at: datetime
    updated_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserBooksListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[UserBooksResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class UserBooksFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class UserBooksOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'
    STATUS_ASC = 'status:asc'
    STATUS_DESC = 'status:desc'
    IS_FAVORITE_ASC = 'is_favorite:asc'
    IS_FAVORITE_DESC = 'is_favorite:desc'
    RATING_ASC = 'rating:asc'
    RATING_DESC = 'rating:desc'
    REVIEW_ASC = 'review:asc'
    REVIEW_DESC = 'review:desc'
    STARTED_AT_ASC = 'started_at:asc'
    STARTED_AT_DESC = 'started_at:desc'
    FINISHED_AT_ASC = 'finished_at:asc'
    FINISHED_AT_DESC = 'finished_at:desc'
    ADDED_AT_ASC = 'added_at:asc'
    ADDED_AT_DESC = 'added_at:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class UserBooksQueryParams(BaseModel):
    """Query parameters for UserBooks"""
    filters: Optional[List[UserBooksFilter]] = None
    order_by: Optional[UserBooksOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)