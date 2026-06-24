"""
Server-side search across a model's text columns (OPS007) -- entity-agnostic.

``build_search_filter(model, term)`` returns a SQLAlchemy OR predicate that case-insensitively
(ILIKE) matches ``term`` against every String/Text column of ``model``, or ``None`` when there is
nothing to search. Apply it to BOTH the data query and the count query so totals reflect the search.
This module knows nothing about specific entities -- it inspects whatever columns the model defines.
"""

from sqlalchemy import String, Text, or_


def searchable_columns(model):
    """Return the model's String/Text columns (the ones worth an ILIKE search)."""
    return [
        column
        for column in model.__table__.columns
        if isinstance(column.type, (String, Text))
    ]


def build_search_filter(model, term):
    """Return an OR(ILIKE) predicate over the model's text columns, or None if not applicable.

    Returns None when ``term`` is empty/None or the model has no text columns, so callers can do:

        predicate = build_search_filter(Model, term)
        if predicate is not None:
            stmt = stmt.where(predicate)
            count_stmt = count_stmt.where(predicate)
    """
    if not term:
        return None
    columns = searchable_columns(model)
    if not columns:
        return None
    pattern = f"%{term}%"
    return or_(*[column.ilike(pattern) for column in columns])
