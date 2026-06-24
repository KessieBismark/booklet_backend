
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class CollectionsBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class CollectionsCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None

class CollectionsUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None

class CollectionsResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CollectionsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[CollectionsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class CollectionsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class CollectionsOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    NAME_ASC = 'name:asc'
    NAME_DESC = 'name:desc'
    DESCRIPTION_ASC = 'description:asc'
    DESCRIPTION_DESC = 'description:desc'
    COLOR_ASC = 'color:asc'
    COLOR_DESC = 'color:desc'
    ICON_ASC = 'icon:asc'
    ICON_DESC = 'icon:desc'
    SORT_ORDER_ASC = 'sort_order:asc'
    SORT_ORDER_DESC = 'sort_order:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class CollectionsQueryParams(BaseModel):
    """Query parameters for Collections"""
    filters: Optional[List[CollectionsFilter]] = None
    order_by: Optional[CollectionsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)