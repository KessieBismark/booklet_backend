"""
REST API routes for Genres (Async)
Generated FastAPI endpoints with full CRUD operations and JWT authentication

Primary Key: id (String)
Auto-generated: No - Requires manual input
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, cast, String
from typing import List, Optional
import logging
from datetime import datetime
from config.dbconfig import get_db_dependency
from models.genres import Genres
from api.schemas.genres_schema import (
    GenresCreate,
    GenresUpdate,
    GenresResponse,
    GenresListResponse,
    GenresFilter,
    GenresOrderBy,
    PaginationParams
)
from utils.auth_utils import create_access_token, decode_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


# JWT Authentication dependency
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user from JWT token
    Similar to GraphQL context authentication
    """
    token = credentials.credentials
    try:
        payload = await decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token. Please login again",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception as e:
        logging.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please login again",
            headers={"WWW-Authenticate": "Bearer"},
        )


from utils.authorize_token import has_permission, build_token_claims


def require_permission_rest(resource: str, action: str):
    """FastAPI dependency factory: enforce-when-configured RBAC for a REST endpoint.

    Reuses has_permission from the shared authz module so the policy lives in one place and
    stays entity-agnostic: passes for tokens without RBAC claims (backward compatible), and
    enforces resource.action once login populates roles/permissions. Returns current_user."""
    def _checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not has_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {resource}.{action}",
            )
        return current_user
    return _checker


# Filter builder helper
def build_filter_conditions(model_class, filters: Optional[List[GenresFilter]]):
    """Build SQLAlchemy filter conditions from filter list"""
    if not filters:
        return None
    
    conditions = []
    for f in filters:
        if not hasattr(model_class, f.field):
            continue
        
        column = getattr(model_class, f.field)
        
        try:
            col_type = column.type.python_type
            if col_type is bool:
                value = str(f.value).lower() in ["true", "1", "yes"]
            elif col_type is datetime:
                value = datetime.fromisoformat(f.value)
            else:
                value = col_type(f.value)
        except (ValueError, TypeError):
            value = f.value
        
        if f.operator == "eq":
            conditions.append(column == value)
        elif f.operator == "ne":
            conditions.append(column != value)
        elif f.operator == "lt":
            conditions.append(column < value)
        elif f.operator == "lte":
            conditions.append(column <= value)
        elif f.operator == "gt":
            conditions.append(column > value)
        elif f.operator == "gte":
            conditions.append(column >= value)
        elif f.operator == "contains":
            conditions.append(func.lower(cast(column, String)).ilike(f"%{str(f.value).lower()}%"))
        elif f.operator == "in" and isinstance(value, list):
            conditions.append(column.in_(value))
        elif f.operator == "is_null":
            conditions.append(column.is_(None) if f.value else column.is_not(None))
    
    return and_(*conditions) if conditions else None


router = APIRouter(
    prefix="/genres",
    tags=["genres"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=GenresResponse, status_code=status.HTTP_201_CREATED)
async def create_genres(
    data: GenresCreate = Body(..., description="Data to create genres"),
    current_user: dict = Depends(require_permission_rest("genres", "create")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Create new genres
    Requires JWT authentication
    
    Primary key is required (id)
    """
    try:
        item_data = data.model_dump(exclude_unset=True)
        
        # Validate manual primary key
        if 'id' not in item_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primary key 'id' is required"
            )
        
        # Check uniqueness
        check_stmt = select(Genres).where(Genres.id == item_data['id'])
        check_result = await db.execute(check_stmt)
        existing = check_result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Genres with id {item_data['id']} already exists"
            )

        new_item = Genres(**item_data)
        
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        
        logging.info(f"New genres created with id {new_item.id}")
        return new_item
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Error creating genres: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating genres: {str(e)}"
        )


@router.get("/", response_model=GenresListResponse)
async def list_genres(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    order_by: Optional[str] = Query(None, description="Field:direction (e.g., created_at:desc)"),
    search: Optional[str] = Query(None, description="Case-insensitive search across text columns"),
    after: Optional[str] = Query(None, description="Keyset cursor from a previous response's next_cursor; pages by primary key"),
    current_user: dict = Depends(require_permission_rest("genres", "read")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    List all genres with server-side search, sorting and pagination
    Requires JWT authentication

    Order by format: field:asc or field:desc
    Example: /api/genres/?search=foo&order_by=created_at:desc&skip=0&limit=50
    """
    try:
        stmt = select(Genres)
        count_stmt = select(func.count()).select_from(Genres)

        # Server-side search across the model's text columns (entity-agnostic).
        # Applied to BOTH the query and the count so `total` reflects the search.
        from query.search import build_search_filter
        _search_filter = build_search_filter(Genres, search)
        if _search_filter is not None:
            stmt = stmt.where(_search_filter)
            count_stmt = count_stmt.where(_search_filter)

        # Get total count (reflects search)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Ordering + pagination: keyset (cursor) when `after` is given (stable + O(limit) for deep
        # pages; pages strictly by primary key), otherwise offset/limit with stable ordering.
        from query.ordering import apply_stable_ordering
        from query.keyset import apply_keyset, cursor_for
        if after:
            stmt = apply_keyset(stmt, Genres, after=after, limit=limit)
        else:
            _order_column = None
            _order_descending = False
            if order_by:
                try:
                    field, direction = order_by.split(':')
                    if hasattr(Genres, field):
                        _order_column = getattr(Genres, field)
                        _order_descending = direction.lower() == 'desc'
                except ValueError:
                    logging.warning(f"Invalid order_by format: {order_by}")
            stmt = apply_stable_ordering(stmt, Genres, _order_column, _order_descending)
            stmt = stmt.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(stmt)
        items = result.scalars().all()

        # Pagination metadata + keyset cursor for the next page (full page => maybe more).
        from query.pagination import pagination_meta
        _meta = pagination_meta(total, skip, limit)
        _next_cursor = cursor_for(items[-1], Genres) if items and len(items) == limit else None

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (_next_cursor is not None) if after else _meta["has_more"],
            "page": _meta["page"],
            "total_pages": _meta["total_pages"],
            "next_cursor": _next_cursor
        }
        
    except Exception as e:
        logging.error(f"Error listing genres: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving items"
        )


@router.get("/count", summary="Count genres")
async def count_genres(
    field: Optional[str] = Query(None, description="Optional exact-match column"),
    value: Optional[str] = Query(None, description="Value for `field` exact match"),
    search: Optional[str] = Query(None, description="Case-insensitive search across text columns"),
    current_user: dict = Depends(require_permission_rest("genres", "read")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """Count genres records (optionally filtered by `search` or `field`==`value`)."""
    try:
        stmt = select(func.count()).select_from(Genres)
        if field and value is not None and hasattr(Genres, field):
            stmt = stmt.where(getattr(Genres, field) == value)
        from query.search import build_search_filter
        _f = build_search_filter(Genres, search)
        if _f is not None:
            stmt = stmt.where(_f)
        result = await db.execute(stmt)
        return {"count": result.scalar() or 0}
    except Exception as e:
        logging.error(f"Error counting genres: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/exists", summary="Whether any genres matches")
async def exists_genres(
    field: Optional[str] = Query(None, description="Column to match"),
    value: Optional[str] = Query(None, description="Value to match"),
    search: Optional[str] = Query(None, description="Case-insensitive search across text columns"),
    current_user: dict = Depends(require_permission_rest("genres", "read")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """Return {"exists": bool} — whether any genres matches the filter."""
    try:
        stmt = select(Genres).limit(1)
        if field and value is not None and hasattr(Genres, field):
            stmt = stmt.where(getattr(Genres, field) == value)
        from query.search import build_search_filter
        _f = build_search_filter(Genres, search)
        if _f is not None:
            stmt = stmt.where(_f)
        result = await db.execute(stmt)
        return {"exists": result.scalar_one_or_none() is not None}
    except Exception as e:
        logging.error(f"Error checking existence of genres: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/by-field", response_model=GenresResponse, summary="Get one genres by field==value")
async def get_genres_by_field(
    field: str = Query(..., description="Column to match"),
    value: str = Query(..., description="Value to match"),
    current_user: dict = Depends(require_permission_rest("genres", "read")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """Return the first genres where `field` == `value` (404 if none)."""
    if not hasattr(Genres, field):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown field: {field}")
    try:
        stmt = select(Genres).where(getattr(Genres, field) == value).limit(1)
        result = await db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return obj
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching genres by field: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/aggregate", summary="Aggregate genres")
async def aggregate_genres(
    op: str = Query("count", description="count | sum | avg | min | max"),
    field: Optional[str] = Query(None, description="Column to aggregate (required for sum/avg/min/max)"),
    group_by: Optional[str] = Query(None, description="Optional column to group by"),
    search: Optional[str] = Query(None, description="Optional case-insensitive search filter"),
    current_user: dict = Depends(require_permission_rest("genres", "read")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """Aggregate genres: count/sum/avg/min/max, optionally grouped by a column.

    Examples:
      /api/genres/aggregate?op=count
      /api/genres/aggregate?op=sum&field=amount&group_by=status
    """
    _ops = {"count": func.count, "sum": func.sum, "avg": func.avg, "min": func.min, "max": func.max}
    if op not in _ops:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported op: {op}")
    if op != "count" and not (field and hasattr(Genres, field)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"`field` is required for op={op}")
    try:
        if field and hasattr(Genres, field):
            agg_col = _ops[op](getattr(Genres, field)).label("value")
        else:
            agg_col = func.count().label("value")
        from query.search import build_search_filter
        _f = build_search_filter(Genres, search)
        if group_by and hasattr(Genres, group_by):
            gcol = getattr(Genres, group_by)
            stmt = select(gcol.label("group"), agg_col).group_by(gcol)
            if _f is not None:
                stmt = stmt.where(_f)
            result = await db.execute(stmt)
            return {"op": op, "field": field, "group_by": group_by,
                     "groups": [{"group": r[0], "value": r[1]} for r in result.all()]}
        stmt = select(agg_col).select_from(Genres)
        if _f is not None:
            stmt = stmt.where(_f)
        result = await db.execute(stmt)
        row = result.first()
        return {"op": op, "field": field, "value": (row[0] if row else None)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error aggregating genres: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred")


@router.get("/{id}", response_model=GenresResponse)
async def get_genres(
    id: str = Path(..., description="Genres primary key"),
    current_user: dict = Depends(require_permission_rest("genres", "read")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Retrieve genres by primary key
    Requires JWT authentication
    """
    try:
        stmt = select(Genres).where(Genres.id == id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genres with id {id} not found"
            )
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving genres: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the item"
        )


@router.put("/{id}", response_model=GenresResponse)
async def update_genres(
    id: str = Path(..., description="Genres primary key"),
    data: GenresUpdate = Body(..., description="Updated data"),
    current_user: dict = Depends(require_permission_rest("genres", "update")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Full update of genres
    Requires JWT authentication
    """
    try:
        stmt = select(Genres).where(Genres.id == id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genres with id {id} not found"
            )
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        
        await db.commit()
        await db.refresh(record)
        
        logging.info(f"genres with id {id} updated")
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Error updating genres: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating genres: {str(e)}"
        )


@router.patch("/{id}", response_model=GenresResponse)
async def partial_update_genres(
    id: str = Path(..., description="Genres primary key"),
    data: GenresUpdate = Body(..., description="Partial update data"),
    current_user: dict = Depends(require_permission_rest("genres", "update")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Partial update of genres - only provided fields are updated
    Requires JWT authentication
    """
    try:
        stmt = select(Genres).where(Genres.id == id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genres with id {id} not found"
            )
        
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        
        await db.commit()
        await db.refresh(record)
        
        logging.info(f"genres with id {id} partially updated")
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Error updating genres: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating genres: {str(e)}"
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genres(
    id: str = Path(..., description="Genres primary key"),
    hard: bool = Query(False, description="Permanent delete if True, soft delete if False"),
    current_user: dict = Depends(require_permission_rest("genres", "delete")),
    db: AsyncSession = Depends(get_db_dependency)
):
    """
    Delete genres - supports soft and hard delete
    Requires JWT authentication
    
    Parameters:
    - hard=False (default): Soft delete (marks as_deleted=True)
    - hard=True: Permanent delete from database
    """
    try:
        stmt = select(Genres).where(Genres.id == id)
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genres with id {id} not found"
            )
        
        if hard:
            await db.delete(record)
            logging.info(f"genres with id {id} hard deleted")
        else:
            if hasattr(record, 'is_deleted'):
                record.is_deleted = True
                await db.commit()
                logging.info(f"genres with id {id} soft deleted")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Soft delete not supported for this model"
                )
        
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logging.error(f"Error deleting genres: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting genres: {str(e)}"
        )
