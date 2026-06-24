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
class BookGenresType:
    book_id: str
    genre_id: str
    books: Optional["BooksType"] = None
    genres: Optional["GenresType"] = None

@strawberry.input
class BookGenresCreateInput:
    book_id: str
    genre_id: str

@strawberry.input
class BookGenresUpdateInput:
    book_id: Optional[str] = None
    genre_id: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
BookGenresFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
BookGenresOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``BookGenresFilterGroup`` continue to compile.
BookGenresFilterGroup         = FilterGroup
BookGenresOffsetPaginationInput = OffsetPaginationInput
BookGenresAggregation          = Aggregation
BookGenresAggregationResult    = AggregationResult
BookGenresAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference BookGenresType) ──────────

@strawberry.type
class BookGenresListResponse:
    items: List[BookGenresType]
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
class BookGenresEdge:
    node: BookGenresType
    cursor: str

@strawberry.type
class BookGenresConnection:
    edges: List[BookGenresEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.genres import GenresType  # noqa: E402