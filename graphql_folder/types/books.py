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
class BooksType:
    id: str
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    isbn: Optional[str]
    language: Optional[str]
    publisher: Optional[str]
    published_on: Optional[date]
    cover_image_url: Optional[str]
    word_count: Optional[int]
    chapter_count: Optional[int]
    est_reading_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime

@strawberry.input
class BooksCreateInput:
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    published_on: Optional[date] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    est_reading_minutes: Optional[int] = None

@strawberry.input
class BooksUpdateInput:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    published_on: Optional[date] = None
    cover_image_url: Optional[str] = None
    word_count: Optional[int] = None
    chapter_count: Optional[int] = None
    est_reading_minutes: Optional[int] = None

# ── Alias → shared common type (no model-specific fields) ──
BooksFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
BooksOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``BooksFilterGroup`` continue to compile.
BooksFilterGroup         = FilterGroup
BooksOffsetPaginationInput = OffsetPaginationInput
BooksAggregation          = Aggregation
BooksAggregationResult    = AggregationResult
BooksAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference BooksType) ──────────

@strawberry.type
class BooksListResponse:
    items: List[BooksType]
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
class BooksEdge:
    node: BooksType
    cursor: str

@strawberry.type
class BooksConnection:
    edges: List[BooksEdge]
    page_info: PageInfo
    total_count: int
