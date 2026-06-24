
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class AuthorsBase(BaseModel):
    """Base schema for common fields"""
    id: str
    name: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuthorsCreate(BaseModel):
    """Schema for create operations"""
    id: str
    name: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None

class AuthorsUpdate(BaseModel):
    """Schema for update operations"""
    name: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None

class AuthorsResponse(BaseModel):
    """Schema for API responses"""
    id: str
    name: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AuthorsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[AuthorsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class AuthorsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class AuthorsOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    NAME_ASC = 'name:asc'
    NAME_DESC = 'name:desc'
    BIO_ASC = 'bio:asc'
    BIO_DESC = 'bio:desc'
    PHOTO_URL_ASC = 'photo_url:asc'
    PHOTO_URL_DESC = 'photo_url:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class AuthorsQueryParams(BaseModel):
    """Query parameters for Authors"""
    filters: Optional[List[AuthorsFilter]] = None
    order_by: Optional[AuthorsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)