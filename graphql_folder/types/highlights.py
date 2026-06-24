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
class HighlightsType:
    id: str
    user_id: str
    book_id: str
    chapter_id: str
    start_offset: int
    end_offset: int
    selected_text: str
    color: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None
    books: Optional["BooksType"] = None
    chapters: Optional["ChaptersType"] = None

@strawberry.input
class HighlightsCreateInput:
    book_id: str
    chapter_id: str
    start_offset: int
    end_offset: int
    selected_text: str
    color: str
    note: Optional[str] = None

@strawberry.input
class HighlightsUpdateInput:
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    selected_text: Optional[str] = None
    color: Optional[str] = None
    note: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
HighlightsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
HighlightsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``HighlightsFilterGroup`` continue to compile.
HighlightsFilterGroup         = FilterGroup
HighlightsOffsetPaginationInput = OffsetPaginationInput
HighlightsAggregation          = Aggregation
HighlightsAggregationResult    = AggregationResult
HighlightsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference HighlightsType) ──────────

@strawberry.type
class HighlightsListResponse:
    items: List[HighlightsType]
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
class HighlightsEdge:
    node: HighlightsType
    cursor: str

@strawberry.type
class HighlightsConnection:
    edges: List[HighlightsEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.chapters import ChaptersType  # noqa: E402
from graphql_folder.types.users import UsersType  # noqa: E402