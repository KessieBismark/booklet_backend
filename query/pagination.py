"""
Offset/limit pagination metadata (OPS007) -- entity-agnostic, pure arithmetic.

``pagination_meta(total, offset, limit)`` returns every page-metadata field the GraphQL and REST
list responses need, computed once in one place so the two stay consistent. Callers pick the fields
their response shape uses (GraphQL: page/page_size/has_next/has_previous; REST: page/total_pages/
has_more). Knows nothing about specific entities.
"""


def pagination_meta(total: int, offset: int, limit: int) -> dict:
    """Compute pagination metadata for an offset/limit page over ``total`` rows.

    Args:
        total: total number of rows in the (filtered) result set.
        offset: number of rows skipped before this page (``skip``).
        limit: page size.

    Returns a dict with: total, offset, limit, page, page_size, total_pages, has_next,
    has_previous, has_more. ``has_more`` is an alias of ``has_next`` (REST naming).
    """
    if limit > 0:
        page = (offset // limit) + 1
        total_pages = (total + limit - 1) // limit
    else:
        page = 1
        total_pages = 1
    has_next = (offset + limit) < total
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_previous": offset > 0,
        "has_more": has_next,
    }
