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
class CollectionBooksType:
    collection_id: str
    book_id: str
    added_at: datetime
    collections: Optional["CollectionsType"] = None
    books: Optional["BooksType"] = None

@strawberry.input
class CollectionBooksCreateInput:
    collection_id: str
    book_id: str
    added_at: datetime

@strawberry.input
class CollectionBooksUpdateInput:
    collection_id: Optional[str] = None
    book_id: Optional[str] = None
    added_at: Optional[datetime] = None

# ── Alias → shared common type (no model-specific fields) ──
CollectionBooksFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
CollectionBooksOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``CollectionBooksFilterGroup`` continue to compile.
CollectionBooksFilterGroup         = FilterGroup
CollectionBooksOffsetPaginationInput = OffsetPaginationInput
CollectionBooksAggregation          = Aggregation
CollectionBooksAggregationResult    = AggregationResult
CollectionBooksAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference CollectionBooksType) ──────────

@strawberry.type
class CollectionBooksListResponse:
    items: List[CollectionBooksType]
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
class CollectionBooksEdge:
    node: CollectionBooksType
    cursor: str

@strawberry.type
class CollectionBooksConnection:
    edges: List[CollectionBooksEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.books import BooksType  # noqa: E402
from graphql_folder.types.collections import CollectionsType  # noqa: E402