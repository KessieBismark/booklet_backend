
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class GenresBase(BaseModel):
    """Base schema for common fields"""
    id: str
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)

class GenresCreate(BaseModel):
    """Schema for create operations"""
    id: str
    name: str
    slug: str

class GenresUpdate(BaseModel):
    """Schema for update operations"""
    name: Optional[str] = None
    slug: Optional[str] = None

class GenresResponse(BaseModel):
    """Schema for API responses"""
    id: str
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)

class GenresListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[GenresResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class GenresFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class GenresOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    NAME_ASC = 'name:asc'
    NAME_DESC = 'name:desc'
    SLUG_ASC = 'slug:asc'
    SLUG_DESC = 'slug:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class GenresQueryParams(BaseModel):
    """Query parameters for Genres"""
    filters: Optional[List[GenresFilter]] = None
    order_by: Optional[GenresOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)