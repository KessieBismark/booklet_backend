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
class ReadingGoalsType:
    id: str
    user_id: str
    period: str
    metric: str
    target_value: int
    period_start: date
    period_end: date
    created_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None

@strawberry.input
class ReadingGoalsCreateInput:
    period: str
    metric: str
    target_value: int
    period_start: date
    period_end: date

@strawberry.input
class ReadingGoalsUpdateInput:
    period: Optional[str] = None
    metric: Optional[str] = None
    target_value: Optional[int] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None

# ── Alias → shared common type (no model-specific fields) ──
ReadingGoalsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
ReadingGoalsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``ReadingGoalsFilterGroup`` continue to compile.
ReadingGoalsFilterGroup         = FilterGroup
ReadingGoalsOffsetPaginationInput = OffsetPaginationInput
ReadingGoalsAggregation          = Aggregation
ReadingGoalsAggregationResult    = AggregationResult
ReadingGoalsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference ReadingGoalsType) ──────────

@strawberry.type
class ReadingGoalsListResponse:
    items: List[ReadingGoalsType]
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
class ReadingGoalsEdge:
    node: ReadingGoalsType
    cursor: str

@strawberry.type
class ReadingGoalsConnection:
    edges: List[ReadingGoalsEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.users import UsersType  # noqa: E402