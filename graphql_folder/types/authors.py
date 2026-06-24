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
class AuthorsType:
    id: str
    name: str
    bio: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.input
class AuthorsCreateInput:
    name: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None

@strawberry.input
class AuthorsUpdateInput:
    name: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
AuthorsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
AuthorsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``AuthorsFilterGroup`` continue to compile.
AuthorsFilterGroup         = FilterGroup
AuthorsOffsetPaginationInput = OffsetPaginationInput
AuthorsAggregation          = Aggregation
AuthorsAggregationResult    = AggregationResult
AuthorsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference AuthorsType) ──────────

@strawberry.type
class AuthorsListResponse:
    items: List[AuthorsType]
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
class AuthorsEdge:
    node: AuthorsType
    cursor: str

@strawberry.type
class AuthorsConnection:
    edges: List[AuthorsEdge]
    page_info: PageInfo
    total_count: int
