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
class UserBooksType:
    id: str
    user_id: str
    book_id: str
    status: str
    is_favorite: bool
    rating: Optional[int]
    review: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    added_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None
    books: Optional["BooksType"] = None

@strawberry.input
class UserBooksCreateInput:
    book_id: str
    status: str
    is_favorite: bool
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    added_at: datetime

@strawberry.input
class UserBooksUpdateInput:
    book_id: Optional[str] = None
    status: Optional[str] = None
    is_favorite: Optional[bool] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    added_at: Optional[datetime] = None

# ── Alias → shared common type (no model-specific fields) ──
UserBooksFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
UserBooksOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``UserBooksFilterGroup`` continue to compile.
UserBooksFilterGroup         = FilterGroup
UserBooksOffsetPaginationInput = OffsetPaginationInput
UserBooksAggregation          = Aggregation
UserBooksAggregationResult    = AggregationResult
UserBooksAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference UserBooksType) ──────────

@strawberry.type
class UserBooksListResponse:
    items: List[UserBooksType]
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
class UserBooksEdge:
    node: UserBooksType
    cursor: str

@strawberry.type
class UserBooksConnection:
    edges: List[UserBooksEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.users import UsersType  # noqa: E402