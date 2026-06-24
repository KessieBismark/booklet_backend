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
class ReadingSessionsType:
    id: str
    user_id: str
    book_id: str
    device_id: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    words_read: Optional[int]
    start_percent: Optional[str]
    end_percent: Optional[str]
    created_at: datetime
    users: Optional["UsersType"] = None
    books: Optional["BooksType"] = None
    devices: Optional["DevicesType"] = None

@strawberry.input
class ReadingSessionsCreateInput:
    book_id: str
    device_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    words_read: Optional[int] = None
    start_percent: Optional[str] = None
    end_percent: Optional[str] = None

@strawberry.input
class ReadingSessionsUpdateInput:
    book_id: Optional[str] = None
    device_id: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    words_read: Optional[int] = None
    start_percent: Optional[str] = None
    end_percent: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
ReadingSessionsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
ReadingSessionsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``ReadingSessionsFilterGroup`` continue to compile.
ReadingSessionsFilterGroup         = FilterGroup
ReadingSessionsOffsetPaginationInput = OffsetPaginationInput
ReadingSessionsAggregation          = Aggregation
ReadingSessionsAggregationResult    = AggregationResult
ReadingSessionsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference ReadingSessionsType) ──────────

@strawberry.type
class ReadingSessionsListResponse:
    items: List[ReadingSessionsType]
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
class ReadingSessionsEdge:
    node: ReadingSessionsType
    cursor: str

@strawberry.type
class ReadingSessionsConnection:
    edges: List[ReadingSessionsEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.devices import DevicesType  # noqa: E402
from graphql_folder.types.users import UsersType  # noqa: E402