"""common_types.py

Single source of truth for all generic GraphQL types.
No model-specific fields live here — every type is reusable across
every model/table in the project.

Flutter usage example
---------------------
// One universal query helper works for ALL models:
Future<QueryResult> queryModel({
  required String modelEndpoint,
  FilterGroup? filterGroup,
  OrderBy? orderBy,
  OffsetPaginationInput? pagination,
}) { ... }
"""
from __future__ import annotations
from typing import List, Optional
from decimal import Decimal
import strawberry
from utils.enums import LogicalOperator, OrderByOperator


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

@strawberry.input
class Filter:
    """A single field filter condition."""
    field: str
    operator: str   # eq | ne | lt | lte | gt | gte | contains | in | is_null
    value: str


@strawberry.input
class FilterGroup:
    """A group of Filter conditions combined with AND / OR logic."""
    logic: Optional[LogicalOperator] = LogicalOperator.AND
    filters: Optional[List[Filter]] = None


# ---------------------------------------------------------------------------
# Ordering & Pagination
# ---------------------------------------------------------------------------

@strawberry.input
class OrderBy:
    """Order-by direction for any model."""
    order: Optional[OrderByOperator] = OrderByOperator.CREATED_AT_DESC


@strawberry.input
class OffsetPaginationInput:
    """Offset / limit pagination — identical for every model."""
    offset: int = 0
    limit: int = 50


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

@strawberry.input
class Aggregation:
    """Specifies one aggregation operation on one field."""
    field: str
    operation: str  # "sum" | "avg" | "max" | "min" | "count" | "count_distinct"


@strawberry.type
class AggregationResult:
    """Result row for a single aggregation / group-by bucket."""
    field_value: Optional[str] = None   # populated when group_by is used
    sum: Optional[float] = None
    average: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    count: int = 0


@strawberry.type
class AggregationResponse:
    """Container for all aggregation result rows."""
    results: List[AggregationResult]
    count: int
    grouped: bool


# ---------------------------------------------------------------------------
# Shared utility types
# ---------------------------------------------------------------------------

@strawberry.type
class ErrorType:
    """Structured error returned from mutations / queries."""
    code: str
    message: str
    details: Optional[dict] = None


@strawberry.type
class PageInfo:
    """Relay-style page info for cursor-based pagination."""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None
