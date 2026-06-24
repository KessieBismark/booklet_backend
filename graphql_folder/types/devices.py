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
class DevicesType:
    id: str
    user_id: str
    name: Optional[str]
    platform: Optional[str]
    last_synced_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None

@strawberry.input
class DevicesCreateInput:
    name: Optional[str] = None
    platform: Optional[str] = None
    push_token: str

@strawberry.input
class DevicesUpdateInput:
    name: Optional[str] = None
    platform: Optional[str] = None
    push_token: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
DevicesFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
DevicesOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``DevicesFilterGroup`` continue to compile.
DevicesFilterGroup         = FilterGroup
DevicesOffsetPaginationInput = OffsetPaginationInput
DevicesAggregation          = Aggregation
DevicesAggregationResult    = AggregationResult
DevicesAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference DevicesType) ──────────

@strawberry.type
class DevicesListResponse:
    items: List[DevicesType]
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
class DevicesEdge:
    node: DevicesType
    cursor: str

@strawberry.type
class DevicesConnection:
    edges: List[DevicesEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.users import UsersType  # noqa: E402