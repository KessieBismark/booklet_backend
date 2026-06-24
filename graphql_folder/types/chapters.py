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
class ChaptersType:
    id: str
    book_id: str
    order_index: int
    title: Optional[str]
    content: str
    content_format: Optional[str]
    word_count: Optional[int]
    char_count: Optional[int]
    created_at: datetime
    updated_at: datetime
    books: Optional["BooksType"] = None

@strawberry.input
class ChaptersCreateInput:
    book_id: str
    order_index: int
    title: Optional[str] = None
    content: str
    content_format: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None

@strawberry.input
class ChaptersUpdateInput:
    book_id: Optional[str] = None
    order_index: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    content_format: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None

# ── Alias → shared common type (no model-specific fields) ──
ChaptersFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
ChaptersOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``ChaptersFilterGroup`` continue to compile.
ChaptersFilterGroup         = FilterGroup
ChaptersOffsetPaginationInput = OffsetPaginationInput
ChaptersAggregation          = Aggregation
ChaptersAggregationResult    = AggregationResult
ChaptersAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference ChaptersType) ──────────

@strawberry.type
class ChaptersListResponse:
    items: List[ChaptersType]
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
class ChaptersEdge:
    node: ChaptersType
    cursor: str

@strawberry.type
class ChaptersConnection:
    edges: List[ChaptersEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402