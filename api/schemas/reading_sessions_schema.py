
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class ReadingSessionsBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    book_id: str
    device_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    words_read: Optional[int] = None
    start_percent: Optional[str] = None
    end_percent: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReadingSessionsCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    book_id: str
    device_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    words_read: Optional[int] = None
    start_percent: Optional[str] = None
    end_percent: Optional[str] = None

class ReadingSessionsUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    book_id: Optional[str] = None
    device_id: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    words_read: Optional[int] = None
    start_percent: Optional[str] = None
    end_percent: Optional[str] = None

class ReadingSessionsResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    book_id: str
    device_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    words_read: Optional[int] = None
    start_percent: Optional[str] = None
    end_percent: Optional[str] = None
    created_at: datetime
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReadingSessionsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[ReadingSessionsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class ReadingSessionsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class ReadingSessionsOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    BOOK_ID_ASC = 'book_id:asc'
    BOOK_ID_DESC = 'book_id:desc'
    DEVICE_ID_ASC = 'device_id:asc'
    DEVICE_ID_DESC = 'device_id:desc'
    STARTED_AT_ASC = 'started_at:asc'
    STARTED_AT_DESC = 'started_at:desc'
    ENDED_AT_ASC = 'ended_at:asc'
    ENDED_AT_DESC = 'ended_at:desc'
    DURATION_SECONDS_ASC = 'duration_seconds:asc'
    DURATION_SECONDS_DESC = 'duration_seconds:desc'
    WORDS_READ_ASC = 'words_read:asc'
    WORDS_READ_DESC = 'words_read:desc'
    START_PERCENT_ASC = 'start_percent:asc'
    START_PERCENT_DESC = 'start_percent:desc'
    END_PERCENT_ASC = 'end_percent:asc'
    END_PERCENT_DESC = 'end_percent:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class ReadingSessionsQueryParams(BaseModel):
    """Query parameters for ReadingSessions"""
    filters: Optional[List[ReadingSessionsFilter]] = None
    order_by: Optional[ReadingSessionsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)