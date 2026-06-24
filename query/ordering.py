"""
Stable ordering for offset/limit pagination (OPS007 T3) -- entity-agnostic.

Offset pagination is only correct over a DETERMINISTIC row order. Sorting on a non-unique column
(or not sorting at all) lets the database return rows in an arbitrary, page-inconsistent order,
which silently skips or duplicates rows across pages. ``apply_stable_ordering`` always appends the
model's primary key as a final tiebreak, so paging is stable for any schema (including composite
keys). This module knows nothing about specific entities -- it inspects whatever model it is given.
"""

from sqlalchemy import inspect as sqlalchemy_inspect


def primary_key_columns(model):
    """Return the model's primary-key Column objects (supports composite keys; entity-agnostic).

    Falls back to a conventional ``id`` column if the mapper cannot be inspected, and to an empty
    list if there is no usable key (in which case no tiebreak is added).
    """
    try:
        pk = list(sqlalchemy_inspect(model).primary_key)
        if pk:
            return pk
    except Exception:
        pass
    return [model.id] if hasattr(model, "id") else []


def apply_stable_ordering(stmt, model, column=None, descending=False):
    """Order by the requested column (if any) then the primary key as a deterministic tiebreak.

    Args:
        stmt: a SQLAlchemy ``select()`` to order.
        model: the ORM model being queried (used to resolve its primary key).
        column: an ORM column/attribute to sort by, or ``None`` for default (primary-key) order.
        descending: sort direction for ``column``; the primary-key tiebreak is always ascending.

    Ordering by a primary-key column twice is harmless (the duplicate key never changes the result),
    so no de-duplication is needed when ``column`` is itself the primary key.
    """
    if column is not None:
        stmt = stmt.order_by(column.desc() if descending else column.asc())
    for pk_column in primary_key_columns(model):
        stmt = stmt.order_by(pk_column.asc())
    return stmt
