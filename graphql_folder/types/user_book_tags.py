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
class UserBookTagsType:
    user_book_id: str
    tag_id: str
    user_books: Optional["UserBooksType"] = None
    tags: Optional["TagsType"] = None

@strawberry.input
class UserBookTagsCreateInput:
    user_book_id: str
    tag_id: str

@strawberry.input
class UserBookTagsUpdateInput:
    user_book_id: Optional[str] = None
    tag_id: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
UserBookTagsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
UserBookTagsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``UserBookTagsFilterGroup`` continue to compile.
UserBookTagsFilterGroup         = FilterGroup
UserBookTagsOffsetPaginationInput = OffsetPaginationInput
UserBookTagsAggregation          = Aggregation
UserBookTagsAggregationResult    = AggregationResult
UserBookTagsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference UserBookTagsType) ──────────

@strawberry.type
class UserBookTagsListResponse:
    items: List[UserBookTagsType]
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
class UserBookTagsEdge:
    node: UserBookTagsType
    cursor: str

@strawberry.type
class UserBookTagsConnection:
    edges: List[UserBookTagsEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.tags import TagsType  # noqa: E402
from graphql_folder.types.user_books import UserBooksType  # noqa: E402