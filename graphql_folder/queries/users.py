
import logging
import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import func, select, and_, or_, cast, String
from sqlalchemy.exc import SQLAlchemyError
from strawberry.exceptions import GraphQLError
import strawberry
from strawberry import Info

from config.dbconfig import get_db
from utils.authorize_token import get_user_id, owner_column, require_permission_for
from utils.rate_limiter import rate_limit
from utils.resolver_errors import handle_resolver_errors
from utils.filters import build_filter_conditions
from utils.root_loader import apply_eager_loading_paths
from utils.enums import LogicalOperator
from utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from query.ordering import apply_stable_ordering
from query.pagination import pagination_meta
from query.search import build_search_filter
from query.keyset import apply_keyset, cursor_for

from models.users import Users
from models.users import (
    USERS_QUERYABLE_FIELDS,
    USERS_ORDERABLE_FIELDS,
    USERS_LOADABLE_RELATIONSHIPS,
)
from ..types.users import (
    UsersType,
    UsersFilter,
    UsersFilterGroup,
    UsersOrderBy,
    UsersListResponse,
    UsersOffsetPaginationInput,
)

from ..types.users import (
    UsersAggregation,
    UsersAggregationResponse,
    UsersAggregationResult,
)


logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================

def validate_queryable_fields(fields: List[str], queryable_config: set) -> None:
    """
    Validate that requested fields are queryable.
    
    Args:
        fields: List of field names to query
        queryable_config: Set of allowed queryable fields
    
    Raises:
        GraphQLError: If any field is not queryable
    """
    invalid_fields = set(fields) - queryable_config
    if invalid_fields:
        raise GraphQLError(
            f"Cannot query fields: {invalid_fields}. "
            f"Allowed fields: {sorted(queryable_config)}",
            extensions={"code": "VALIDATION_ERROR"}
        )


def validate_orderable_fields(field: str, orderable_config: set) -> None:
    """
    Validate that a field can be sorted by.
    
    Args:
        field: Field name to sort by
        orderable_config: Set of allowed orderable fields
    
    Raises:
        GraphQLError: If field cannot be ordered
    """
    if field not in orderable_config:
        raise GraphQLError(
            f"Cannot order by '{field}'. "
            f"Allowed fields: {sorted(orderable_config)}",
            extensions={"code": "VALIDATION_ERROR"}
        )


def validate_relationships(
    relationships: Optional[List[str]],
    loadable_config: set
) -> None:
    """
    Validate that requested relationships can be loaded.
    
    Args:
        relationships: List of relationship names
        loadable_config: Set of allowed loadable relationships
    
    Raises:
        GraphQLError: If any relationship is invalid
    """
    if not relationships:
        return
    
    invalid_rels = set(relationships) - loadable_config
    if invalid_rels:
        raise GraphQLError(
            f"Invalid relationships: {invalid_rels}. "
            f"Available: {sorted(loadable_config)}",
            extensions={"code": "VALIDATION_ERROR"}
        )


def _get_relationship_paths_from_query(
    info: Info,
    model: type,
    loadable_rels: set,
    root_field: str = "items",
    max_depth: int = 3
) -> List[str]:
    """
    Walk the GraphQL selection set and return dot-notation eager load paths
    for any selected field that maps to a SQLAlchemy relationship.

    Only paths whose root name is in loadable_rels are included.

    Example:
        Query:   commentsList > items > post > auth > id
        Returns: ["post", "post.auth"]
    """
    from sqlalchemy import inspect as sa_inspect
    from sqlalchemy.exc import InvalidRequestError

    paths: List[str] = []

    def _get_rels(m) -> set:
        try:
            return {rel.key for rel in sa_inspect(m).relationships}
        except InvalidRequestError:
            return set()

    def _get_related_model(m, rel_name: str):
        try:
            return sa_inspect(m).relationships[rel_name].mapper.class_
        except (InvalidRequestError, KeyError):
            return None

    def _walk(selections, current_model, prefix: str, depth: int):
        if depth > max_depth:
            return
        rels = _get_rels(current_model)
        for field in selections:
            if not hasattr(field, 'name'):
                continue
            field_name = field.name
            if field_name not in rels:
                continue
            path = f"{prefix}.{field_name}" if prefix else field_name
            # Only include if root of path is in the allowed set
            root = path.split(".")[0]
            if root not in loadable_rels:
                continue
            paths.append(path)
            related_model = _get_related_model(current_model, field_name)
            if related_model and getattr(field, 'selections', None):
                _walk(field.selections, related_model, path, depth + 1)

    try:
        for top_field in info.selected_fields:
            items_field = next(
                (f for f in top_field.selections if f.name == root_field), None
            )
            if items_field and items_field.selections:
                _walk(items_field.selections, model, "", 0)
                break
    except Exception:
        pass

    return paths


# Keep old name as alias for backward compatibility
def _get_requested_relationships(info: Info, loadable_rels: set) -> List[str]:
    return []  # Replaced by _get_relationship_paths_from_query



# ============================================================================
# Users Queries
# ============================================================================

@strawberry.type
class UsersQuery:
    """GraphQL queries for Users"""

    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def users_by_id(
        self,
        id: str,
        info: Info,
        relationships: Optional[List[str]] = None
    ) -> Optional[UsersType]:
        """
        Get Users by ID.
        
        Args:
            id: Record ID
            relationships: Optional relationships to eager load
        
        Returns:
            Users record or None
        
        Raises:
            GraphQLError: If not authorized or record not found
        """
        try:
            # ====== Authorization ======
            user_id = await get_user_id(info)
            await require_permission_for(info, "users", "read")
            logger.debug(f"User {user_id} querying Users: {id}")
            
            # ====== Auto-detect relationships from the GraphQL query ======
            # Walks the selection set to build dot-notation paths like
            # ["relation", "relation.nested"] so nested rels are always eager-loaded
            # before the session closes — no DetachedInstanceError.
            if not relationships:
                relationships = _get_relationship_paths_from_query(
                    info, Users, USERS_LOADABLE_RELATIONSHIPS
                )
            else:
                # Caller supplied manually — validate top-level names only
                validate_relationships(
                    [p.split('.')[0] for p in relationships],
                    USERS_LOADABLE_RELATIONSHIPS
                )

            async with get_db() as db:
                # ====== Build query ======
                stmt = select(Users).where(Users.id == id)
                
                # Add user filter if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                # ====== Apply eager loading (chained, from query paths) ======
                if relationships:
                    stmt = apply_eager_loading_paths(
                        stmt,
                        Users,
                        paths=relationships
                    )
                
                # ====== Execute query ======
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()
                
                if not record:
                    logger.warning(f"Users not found: {id}")
                    raise GraphQLError(
                        "Users not found or access denied",
                        extensions={"code": "NOT_FOUND"}
                    )
                
                return record

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def users_by_field(
        self,
        field_name: str,
        field_value: str,
        info: Info,
        relationships: Optional[List[str]] = None
    ) -> Optional[UsersType]:
        """
        Get Users by queryable field value.
        
        Args:
            field_name: Field to query by (must be in QUERYABLE_FIELDS)
            field_value: Value to match
            relationships: Optional relationships to eager load
        
        Returns:
            Users record or None
        
        Raises:
            GraphQLError: If field not queryable or record not found
        """
        try:
            # ====== Authorization ======
            user_id = await get_user_id(info)
            await require_permission_for(info, "users", "read")
            
            # ====== Validate queryable field ======
            validate_queryable_fields([field_name], USERS_QUERYABLE_FIELDS)
            
            # ====== Validate field exists ======
            if not hasattr(Users, field_name):
                raise GraphQLError(
                    f"Field '{field_name}' does not exist",
                    extensions={"code": "VALIDATION_ERROR", "field": field_name}
                )
            
            # ====== Auto-detect relationships from the GraphQL query ======
            if not relationships:
                relationships = _get_relationship_paths_from_query(
                    info, Users, USERS_LOADABLE_RELATIONSHIPS
                )
            else:
                validate_relationships(
                    [p.split('.')[0] for p in relationships],
                    USERS_LOADABLE_RELATIONSHIPS
                )

            async with get_db() as db:
                # ====== Build query ======
                column = getattr(Users, field_name)
                stmt = select(Users).where(column == field_value)
                
                # Add user filter if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                # ====== Apply eager loading (chained, from query paths) ======
                if relationships:
                    stmt = apply_eager_loading_paths(
                        stmt,
                        Users,
                        paths=relationships
                    )
                
                # ====== Execute query ======
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()
                
                return record

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def users_list(
        self,
        info: Info,
        pagination: Optional[UsersOffsetPaginationInput] = None,
        filter_group: Optional[UsersFilterGroup] = None,
        order_by: Optional[UsersOrderBy] = None,
        search: Optional[str] = None,
        after: Optional[str] = None,
        relationships: Optional[List[str]] = None
    ) -> UsersListResponse:
        """
        List Users with searching, filtering, sorting, and pagination.

        Args:
            pagination: Offset/limit pagination
            filter_group: Optional filters with AND/OR logic
            order_by: Optional ordering
            search: Optional case-insensitive search across the model's text columns
            after: Optional keyset cursor (from a previous response's `next_cursor`); when set,
                pages by primary key for stable, deep-page-efficient results (the requested sort is
                not applied in cursor mode)
            relationships: Optional relationships to eager load
        
        Returns:
            Paginated list of Users
        
        Raises:
            GraphQLError: If validation fails or database error
        """
        try:
            # ====== Authorization ======
            user_id = await get_user_id(info)
            await require_permission_for(info, "users", "read")
            logger.debug(f"User {user_id} listing Users")
            
            # ====== Validate and sanitize pagination ======
            offset = pagination.offset if pagination else 0
            limit = pagination.limit if pagination else DEFAULT_PAGE_SIZE
            
            if offset < 0:
                raise GraphQLError(
                    "Offset must be non-negative",
                    extensions={"code": "VALIDATION_ERROR"}
                )
            
            if limit <= 0:
                raise GraphQLError(
                    "Limit must be positive",
                    extensions={"code": "VALIDATION_ERROR"}
                )
            
            if limit > MAX_PAGE_SIZE:
                limit = MAX_PAGE_SIZE  # Cap to maximum
            
            # ====== Auto-detect relationships from the GraphQL query ======
            if not relationships:
                relationships = _get_relationship_paths_from_query(
                    info, Users, USERS_LOADABLE_RELATIONSHIPS
                )
            else:
                validate_relationships(
                    [p.split('.')[0] for p in relationships],
                    USERS_LOADABLE_RELATIONSHIPS
                )

            async with get_db() as db:
                # ====== Build base query ======
                stmt = select(Users)
                count_stmt = select(func.count()).select_from(Users)
                
                # Add user filter if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                    count_stmt = count_stmt.where(_owner == user_id)
                
                # ====== Apply eager loading (chained, from query paths) ======
                if relationships:
                    stmt = apply_eager_loading_paths(
                        stmt,
                        Users,
                        paths=relationships
                    )
                
                # ====== Apply filters ======
                if filter_group and filter_group.filters:
                    # Validate queryable fields in filters
                    for f in filter_group.filters:
                        validate_queryable_fields([f.field], USERS_QUERYABLE_FIELDS)
                    
                    filter_conditions = build_filter_conditions(
                        Users,
                        filters=filter_group.filters,
                        logic=filter_group.logic
                    )
                    
                    if filter_conditions is not None:
                        stmt = stmt.where(filter_conditions)
                        count_stmt = count_stmt.where(filter_conditions)

                # ====== Apply server-side search (parity with REST) ======
                # Case-insensitive match across the model's text columns; applied to BOTH the data
                # and count query so total_count reflects the search.
                _search_filter = build_search_filter(Users, search)
                if _search_filter is not None:
                    stmt = stmt.where(_search_filter)
                    count_stmt = count_stmt.where(_search_filter)

                # ====== Get total count ======
                count_result = await db.execute(count_stmt)
                total_count = count_result.scalar() or 0
                
                # Adjust offset if out of range
                if offset >= total_count and total_count > 0:
                    offset = 0
                
                # ====== Apply ordering (stable: requested sort + primary-key tiebreak) ======
                # The primary-key tiebreak (added by apply_stable_ordering) makes offset/limit
                # pagination deterministic even when the sort column is non-unique or absent.
                _order_column = None
                _order_descending = False
                if order_by:
                    try:
                        order_field, order_direction = order_by.value.split(':')
                    except (ValueError, AttributeError):
                        raise GraphQLError(
                            "Invalid order_by format. Use 'field:direction'",
                            extensions={"code": "VALIDATION_ERROR"}
                        )

                    # Validate orderable field
                    validate_orderable_fields(order_field, USERS_ORDERABLE_FIELDS)

                    if order_direction not in ('asc', 'desc'):
                        raise GraphQLError(
                            f"Invalid sort direction: {order_direction}",
                            extensions={"code": "VALIDATION_ERROR"}
                        )

                    if hasattr(Users, order_field):
                        _order_column = getattr(Users, order_field)
                        _order_descending = order_direction == 'desc'
                # ====== Apply ordering + pagination ======
                # Keyset (cursor) pagination when `after` is provided: pages strictly by primary key
                # (stable + O(limit) for deep pages; the requested sort is not applied in cursor
                # mode). Otherwise classic offset/limit with the stable ordering (sort + PK tiebreak).
                if after:
                    stmt = apply_keyset(stmt, Users, after=after, limit=limit)
                else:
                    stmt = apply_stable_ordering(stmt, Users, _order_column, _order_descending)
                    stmt = stmt.offset(offset).limit(limit)

                # ====== Execute query ======
                result = await db.execute(stmt)
                items = result.scalars().all()

                # A full page implies there may be more rows; expose a cursor for the next page.
                _next_cursor = cursor_for(items[-1], Users) if items and len(items) == limit else None
                _meta = pagination_meta(total_count, offset, limit)
                return UsersListResponse(
                    items=items,
                    total_count=total_count,
                    count=len(items),
                    page=_meta["page"],
                    page_size=_meta["page_size"],
                    has_next=(_next_cursor is not None) if after else _meta["has_next"],
                    has_previous=_meta["has_previous"],
                    next_cursor=_next_cursor
                )

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def users_count(
        self,
        info: Info,
        filter_group: Optional[UsersFilterGroup] = None
    ) -> int:
        """
        Count Users records matching filters.
        
        Args:
            filter_group: Optional filters
        
        Returns:
            Count of matching records
        
        Raises:
            GraphQLError: If validation fails
        """
        try:
            # ====== Authorization ======
            user_id = await get_user_id(info)
            await require_permission_for(info, "users", "read")

            async with get_db() as db:
                # ====== Build query ======
                stmt = select(func.count(Users.id))
                
                # Add user filter if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                # ====== Apply filters ======
                if filter_group and filter_group.filters:
                    # Validate queryable fields
                    for f in filter_group.filters:
                        validate_queryable_fields([f.field], USERS_QUERYABLE_FIELDS)
                    
                    filter_conditions = build_filter_conditions(
                        Users,
                        filters=filter_group.filters,
                        logic=filter_group.logic
                    )
                    
                    if filter_conditions is not None:
                        stmt = stmt.where(filter_conditions)
                
                # ====== Execute query ======
                result = await db.execute(stmt)
                return result.scalar() or 0

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def users_exists(
        self,
        info: Info,
        filter_group: UsersFilterGroup
    ) -> bool:
        """
        Check if Users records matching filters exist.
        
        Args:
            filter_group: Filters to check
        
        Returns:
            True if matching records exist
        
        Raises:
            GraphQLError: If validation fails
        """
        try:
            # ====== Authorization ======
            user_id = await get_user_id(info)
            await require_permission_for(info, "users", "read")

            async with get_db() as db:
                # ====== Build query ======
                stmt = select(Users).limit(1)
                
                # Add user filter if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                # ====== Apply filters ======
                if filter_group.filters:
                    # Validate queryable fields
                    for f in filter_group.filters:
                        validate_queryable_fields([f.field], USERS_QUERYABLE_FIELDS)
                    
                    filter_conditions = build_filter_conditions(
                        Users,
                        filters=filter_group.filters,
                        logic=filter_group.logic
                    )
                    
                    if filter_conditions is not None:
                        stmt = stmt.where(filter_conditions)
                
                # ====== Execute query ======
                result = await db.execute(stmt)
                return result.scalar_one_or_none() is not None

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def users_aggregation(
        self,
        info: Info,
        filter_group: Optional[UsersFilterGroup] = None,
        aggregations: Optional[List[UsersAggregation]] = None,
        group_by: Optional[List[str]] = None
    ) -> UsersAggregationResponse:
        """
        Get aggregated Users data with optional grouping.
        
        Args:
            filter_group: Optional filters
            aggregations: Operations (sum, avg, min, max, count)
            group_by: Fields to group by
        
        Returns:
            Aggregation results
        
        Raises:
            GraphQLError: If validation fails
        """
        try:
            # ====== Authorization ======
            user_id = await get_user_id(info)
            await require_permission_for(info, "users", "read")
            
            # ====== Validate inputs ======
            if group_by:
                validate_queryable_fields(group_by, USERS_QUERYABLE_FIELDS)

            async with get_db() as db:
                # Build aggregation columns
                select_columns = []
                group_by_columns = []
                
                # Add group by columns
                if group_by:
                    for field in group_by:
                        if hasattr(Users, field):
                            column = getattr(Users, field)
                            select_columns.append(column.label(field))
                            group_by_columns.append(column)
                
                # Add aggregation columns
                if aggregations:
                    for agg in aggregations:
                        if hasattr(Users, agg.field):
                            column = getattr(Users, agg.field)
                            
                            if agg.operation == "sum":
                                agg_col = func.sum(column).label(f"{agg.field}_sum")
                            elif agg.operation == "avg":
                                agg_col = func.avg(column).label(f"{agg.field}_avg")
                            elif agg.operation == "max":
                                agg_col = func.max(column).label(f"{agg.field}_max")
                            elif agg.operation == "min":
                                agg_col = func.min(column).label(f"{agg.field}_min")
                            elif agg.operation == "count":
                                agg_col = func.count(column).label(f"{agg.field}_count")
                            elif agg.operation == "count_distinct":
                                agg_col = func.count(func.distinct(column)).label(f"{agg.field}_count_distinct")
                            else:
                                continue
                            
                            select_columns.append(agg_col)
                else:
                    # Default: count all
                    count_col = func.count(Users.id).label("total_count")
                    select_columns.append(count_col)
                
                # Build query
                if select_columns:
                    stmt = select(*select_columns)
                else:
                    stmt = select(func.count(Users.id).label("total_count"))
                
                # Add user filter if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                # ====== Apply filters ======
                if filter_group and filter_group.filters:
                    for f in filter_group.filters:
                        validate_queryable_fields([f.field], USERS_QUERYABLE_FIELDS)
                    
                    filter_conditions = build_filter_conditions(
                        Users,
                        filters=filter_group.filters,
                        logic=filter_group.logic
                    )
                    
                    if filter_conditions is not None:
                        stmt = stmt.where(filter_conditions)
                
                # Apply grouping
                if group_by_columns:
                    stmt = stmt.group_by(*group_by_columns)
                
                # ====== Execute query ======
                result = await db.execute(stmt)
                rows = result.all()
                
                # Process results into AggregationResult objects
                results = []
                for row in rows:
                    agg_result = UsersAggregationResult()
                    
                    # Map group by values
                    if group_by:
                        for i, field in enumerate(group_by):
                            if i < len(row):
                                setattr(agg_result, field, row[i])
                    
                    # Map aggregation values
                    col_idx = len(group_by or [])
                    if aggregations:
                        for agg in aggregations:
                            if col_idx < len(row):
                                agg_attr = f"{agg.field}_{agg.operation}"
                                setattr(agg_result, agg_attr, row[col_idx])
                                col_idx += 1
                    else:
                        if col_idx < len(row):
                            setattr(agg_result, "total_count", row[col_idx])
                    
                    results.append(agg_result)
                
                return UsersAggregationResponse(
                    results=results,
                    count=len(results),
                    grouped=bool(group_by)
                )

        except GraphQLError:
            raise

