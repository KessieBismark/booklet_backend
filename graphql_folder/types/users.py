from __future__ import annotations
from typing import List, Optional, Any
from datetime import datetime, date, time
from decimal import Decimal
import strawberry
from utils.enums import LogicalOperator, OrderByOperator
from graphql_folder.common_types import (
    Filter, FilterGroup, OrderBy, OffsetPaginationInput,
    Aggregation, AggregationResult, AggregationResponse,
    ErrorType, PageInfo,
)

@strawberry.type
class UsersType:
    id: str
    email: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    locale: Optional[str]
    theme: Optional[str]
    font_scale: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_active_at: Optional[datetime]

@strawberry.input
class UsersFieldInput:
    fields: str  # e.g. 'email', 'password'
    value: str  # the actual value
    is_checker: bool = False
    is_password: bool = False

@strawberry.input
class UsersCreateInput:
    fields: List[UsersFieldInput]

@strawberry.input
class ChangeUsersFieldInput:
    fields: str  # e.g. 'email', 'password'
    value: str  # the actual value
    is_password: bool = False
    is_old: bool = False
    is_new: bool = False

@strawberry.input
class UsersUpdateInput:
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    theme: Optional[str] = None
    font_scale: Optional[str] = None
    last_active_at: Optional[datetime] = None
    password_hash: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
UsersFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
UsersOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``UsersFilterGroup`` continue to compile.
UsersFilterGroup         = FilterGroup
UsersOffsetPaginationInput = OffsetPaginationInput
UsersAggregation          = Aggregation
UsersAggregationResult    = AggregationResult
UsersAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference UsersType) ──────────

@strawberry.type
class UsersListResponse:
    items: List[UsersType]
    total_count: int
    count: int
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_next: Optional[bool] = None
    has_previous: Optional[bool] = None
    # Opaque cursor for keyset pagination: pass it back as `after` to fetch the next page
    # (None when there are no more rows). Available on every list response (OPS007 T3).
    next_cursor: Optional[str] = None

@strawberry.type
class UsersEdge:
    node: UsersType
    cursor: str

@strawberry.type
class UsersConnection:
    edges: List[UsersEdge]
    page_info: PageInfo
    total_count: int
