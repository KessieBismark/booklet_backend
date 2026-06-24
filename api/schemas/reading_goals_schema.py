
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

class ReadingGoalsBase(BaseModel):
    """Base schema for common fields"""
    id: str
    user_id: str
    period: str
    metric: str
    target_value: int
    period_start: datetime
    period_end: datetime

    model_config = ConfigDict(from_attributes=True)

class ReadingGoalsCreate(BaseModel):
    """Schema for create operations"""
    id: str
    user_id: str
    period: str
    metric: str
    target_value: int
    period_start: datetime
    period_end: datetime

class ReadingGoalsUpdate(BaseModel):
    """Schema for update operations"""
    user_id: Optional[str] = None
    period: Optional[str] = None
    metric: Optional[str] = None
    target_value: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

class ReadingGoalsResponse(BaseModel):
    """Schema for API responses"""
    id: str
    user_id: str
    period: str
    metric: str
    target_value: int
    period_start: datetime
    period_end: datetime
    created_at: datetime
    updated_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReadingGoalsListResponse(BaseModel):
    """Schema for paginated list responses"""
    items: List[ReadingGoalsResponse]
    total: int
    skip: int = 0
    limit: int = 50
    has_more: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    next_cursor: Optional[str] = None

class ReadingGoalsFilter(BaseModel):
    """Schema for filtering operations"""
    field: str
    operator: str = Field(..., description="eq, ne, lt, lte, gt, gte, contains, in, is_null")
    value: Any

class ReadingGoalsOrderBy(str, Enum):
    """Enum for ordering options"""
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'
    USER_ID_ASC = 'user_id:asc'
    USER_ID_DESC = 'user_id:desc'
    PERIOD_ASC = 'period:asc'
    PERIOD_DESC = 'period:desc'
    METRIC_ASC = 'metric:asc'
    METRIC_DESC = 'metric:desc'
    TARGET_VALUE_ASC = 'target_value:asc'
    TARGET_VALUE_DESC = 'target_value:desc'
    PERIOD_START_ASC = 'period_start:asc'
    PERIOD_START_DESC = 'period_start:desc'
    PERIOD_END_ASC = 'period_end:asc'
    PERIOD_END_DESC = 'period_end:desc'

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

class ReadingGoalsQueryParams(BaseModel):
    """Query parameters for ReadingGoals"""
    filters: Optional[List[ReadingGoalsFilter]] = None
    order_by: Optional[ReadingGoalsOrderBy] = None
    pagination: PaginationParams = Field(default_factory=PaginationParams)