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
class QuotesType:
    id: str
    user_id: str
    book_id: str
    chapter_id: Optional[str]
    highlight_id: Optional[str]
    quote_text: str
    note: Optional[str]
    location_label: Optional[str]
    is_favorite: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None
    books: Optional["BooksType"] = None
    chapters: Optional["ChaptersType"] = None
    highlights: Optional["HighlightsType"] = None

@strawberry.input
class QuotesCreateInput:
    book_id: str
    chapter_id: Optional[str] = None
    highlight_id: Optional[str] = None
    quote_text: str
    note: Optional[str] = None
    location_label: Optional[str] = None
    is_favorite: bool
    is_public: bool

@strawberry.input
class QuotesUpdateInput:
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    highlight_id: Optional[str] = None
    quote_text: Optional[str] = None
    note: Optional[str] = None
    location_label: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_public: Optional[bool] = None

# ── Alias → shared common type (no model-specific fields) ──
QuotesFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
QuotesOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``QuotesFilterGroup`` continue to compile.
QuotesFilterGroup         = FilterGroup
QuotesOffsetPaginationInput = OffsetPaginationInput
QuotesAggregation          = Aggregation
QuotesAggregationResult    = AggregationResult
QuotesAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference QuotesType) ──────────

@strawberry.type
class QuotesListResponse:
    items: List[QuotesType]
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
class QuotesEdge:
    node: QuotesType
    cursor: str

@strawberry.type
class QuotesConnection:
    edges: List[QuotesEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.chapters import ChaptersType  # noqa: E402
from graphql_folder.types.highlights import HighlightsType  # noqa: E402
from graphql_folder.types.users import UsersType  # noqa: E402