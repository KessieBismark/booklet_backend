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
class GenresType:
    id: str
    name: str
    slug: str

@strawberry.input
class GenresCreateInput:
    name: str
    slug: str

@strawberry.input
class GenresUpdateInput:
    name: Optional[str] = None
    slug: Optional[str] = None

# ── Alias → shared common type (no model-specific fields) ──
GenresFilter = Filter

# ── Alias → shared common type (no model-specific fields) ──
GenresOrderBy = OrderBy


# ── Aliases to shared common types (zero model-specific fields) ──────────
# These names are kept so that all generated query / mutation files that
# already import e.g. ``GenresFilterGroup`` continue to compile.
GenresFilterGroup         = FilterGroup
GenresOffsetPaginationInput = OffsetPaginationInput
GenresAggregation          = Aggregation
GenresAggregationResult    = AggregationResult
GenresAggregationResponse  = AggregationResponse

# ── Model-specific types (these DO reference GenresType) ──────────

@strawberry.type
class GenresListResponse:
    items: List[GenresType]
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
class GenresEdge:
    node: GenresType
    cursor: str

@strawberry.type
class GenresConnection:
    edges: List[GenresEdge]
    page_info: PageInfo
    total_count: int
