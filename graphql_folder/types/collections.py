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
class CollectionsType:
    id: str
    user_id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    sort_order: Optional[int]
    created_at: datetime
    updated_at: datetime
    users: Optional["UsersType"] = None

@strawberry.input
class CollectionsCreateInput:
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None

@strawberry.input
class CollectionsUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None

# ── Alias → shared common type (no model-specific fields) ──
CollectionsFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
CollectionsOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``CollectionsFilterGroup`` continue to compile.
CollectionsFilterGroup         = FilterGroup
CollectionsOffsetPaginationInput = OffsetPaginationInput
CollectionsAggregation          = Aggregation
CollectionsAggregationResult    = AggregationResult
CollectionsAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference CollectionsType) ──────────

@strawberry.type
class CollectionsListResponse:
    items: List[CollectionsType]
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
class CollectionsEdge:
    node: CollectionsType
    cursor: str

@strawberry.type
class CollectionsConnection:
    edges: List[CollectionsEdge]
    page_info: PageInfo
    total_count: int


# Resolve related types (imported last so mutual references don't deadlock).
from graphql_folder.types.users import UsersType  # noqa: E402