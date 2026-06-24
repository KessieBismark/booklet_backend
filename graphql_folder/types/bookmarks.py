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
class BookmarksType:
    id: str
    user_id: str
    book_id: str
    chapter_id: str
    char_offset: int
    label: Optional[str]
    preview_text: Optional[str]
    created_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None
    books: Optional["BooksType"] = None
    chapters: Optional["ChaptersType"] = None

@strawberry.input
class BookmarksCreateInput:
    book_id: str
    chapter_id: str
    char_offset: int
    label: Optional[str] = None
    preview_text: Optional[str] = None

@strawberry.input
class BookmarksUpdateInput:
    book_id: Optional[str] = None
    chapter_id: Optional[str] = None
    char_offset: Optional[int] = None
    label: Optional[str] = None
    preview_text: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
BookmarksFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
BookmarksOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``BookmarksFilterGroup`` continue to compile.
BookmarksFilterGroup         = FilterGroup
BookmarksOffsetPaginationInput = OffsetPaginationInput
BookmarksAggregation          = Aggregation
BookmarksAggregationResult    = AggregationResult
BookmarksAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference BookmarksType) ──────────

@strawberry.type
class BookmarksListResponse:
    items: List[BookmarksType]
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
class BookmarksEdge:
    node: BookmarksType
    cursor: str

@strawberry.type
class BookmarksConnection:
    edges: List[BookmarksEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.chapters import ChaptersType  # noqa: E402
from graphql_folder.types.users import UsersType  # noqa: E402