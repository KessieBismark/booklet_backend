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
class BookAuthorsType:
    book_id: str
    author_id: str
    author_role: str
    books: Optional["BooksType"] = None
    authors: Optional["AuthorsType"] = None

@strawberry.input
class BookAuthorsCreateInput:
    book_id: str
    author_id: str
    author_role: str

@strawberry.input
class BookAuthorsUpdateInput:
    book_id: Optional[str] = None
    author_id: Optional[str] = None
    author_role: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
BookAuthorsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
BookAuthorsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``BookAuthorsFilterGroup`` continue to compile.
BookAuthorsFilterGroup         = FilterGroup
BookAuthorsOffsetPaginationInput = OffsetPaginationInput
BookAuthorsAggregation          = Aggregation
BookAuthorsAggregationResult    = AggregationResult
BookAuthorsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference BookAuthorsType) ──────────

@strawberry.type
class BookAuthorsListResponse:
    items: List[BookAuthorsType]
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
class BookAuthorsEdge:
    node: BookAuthorsType
    cursor: str

@strawberry.type
class BookAuthorsConnection:
    edges: List[BookAuthorsEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.authors import AuthorsType  # noqa: E402
from graphql_folder.types.books import BooksType  # noqa: E402