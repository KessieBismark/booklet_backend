
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class DevicesBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    name: Optional[str] = None
    platform: Optional[str] = None
    last_synced_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DevicesCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    name: Optional[str] = None
    platform: Optional[str] = None
    last_synced_at: Optional[datetime] = None

class DevicesUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    name: Optional[str] = None
    platform: Optional[str] = None
    last_synced_at: Optional[datetime] = None

class DevicesResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    name: Optional[str] = None
    platform: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DevicesListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[DevicesResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class DevicesFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class DevicesOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    NAME_ASC = 'name:asc'
    NAME_DESC = 'name:desc'
    PLATFORM_ASC = 'platform:asc'
    PLATFORM_DESC = 'platform:desc'
    LAST_SYNCED_AT_ASC = 'last_synced_at:asc'
    LAST_SYNCED_AT_DESC = 'last_synced_at:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class DevicesQueryParams(BaseModel):
    """Query parameters for Devices"""
    filters: Optional[List[DevicesFilter]] = None
    order_by: Optional[DevicesOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)