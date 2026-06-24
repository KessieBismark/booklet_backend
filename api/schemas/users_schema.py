
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class UsersBase(BaseModel):
    """Base schema for common fields"""
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    theme: Optional[str] = None
    font_scale: Optional[str] = None
    last_active_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UsersCreate(BaseModel):
    """Schema for create operations"""
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    theme: Optional[str] = None
    font_scale: Optional[str] = None
    last_active_at: Optional[datetime] = None

class UsersUpdate(BaseModel):
    """Schema for update operations"""
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    theme: Optional[str] = None
    font_scale: Optional[str] = None
    last_active_at: Optional[datetime] = None

class UsersResponse(BaseModel):
    """Schema for API responses"""
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    theme: Optional[str] = None
    font_scale: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UsersListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[UsersResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class UsersFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class UsersOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    EMAIL_ASC = 'email:asc'
    EMAIL_DESC = 'email:desc'
    DISPLAY_NAME_ASC = 'display_name:asc'
    DISPLAY_NAME_DESC = 'display_name:desc'
    AVATAR_URL_ASC = 'avatar_url:asc'
    AVATAR_URL_DESC = 'avatar_url:desc'
    LOCALE_ASC = 'locale:asc'
    LOCALE_DESC = 'locale:desc'
    THEME_ASC = 'theme:asc'
    THEME_DESC = 'theme:desc'
    FONT_SCALE_ASC = 'font_scale:asc'
    FONT_SCALE_DESC = 'font_scale:desc'
    LAST_ACTIVE_AT_ASC = 'last_active_at:asc'
    LAST_ACTIVE_AT_DESC = 'last_active_at:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class UsersQueryParams(BaseModel):
    """Query parameters for Users"""
    filters: Optional[List[UsersFilter]] = None
    order_by: Optional[UsersOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)