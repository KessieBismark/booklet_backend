
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class TagsBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class TagsCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    name: str

class TagsUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    name: Optional[str] = None

class TagsResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class TagsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[TagsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class TagsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class TagsOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    NAME_ASC = 'name:asc'
    NAME_DESC = 'name:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class TagsQueryParams(BaseModel):
    """Query parameters for Tags"""
    filters: Optional[List[TagsFilter]] = None
    order_by: Optional[TagsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)