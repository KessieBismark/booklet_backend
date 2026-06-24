"""
Keyset (cursor) pagination -- entity-agnostic, opt-in alongside offset/limit (OPS007 T3).

Offset/limit pagination re-scans the skipped rows (slow for deep pages) and can skip or duplicate
rows when the table changes between page loads. Keyset pagination instead remembers the LAST row of
a page (its primary key) in an opaque cursor and fetches the next page with a WHERE comparison, so
each page costs O(limit) regardless of depth and is stable under concurrent inserts.

This module pages by the model's PRIMARY KEY (ascending), supporting single and composite keys via a
portable lexicographic comparison (works across SQL dialects). It is entity-agnostic -- it inspects
whatever primary key the given model defines. Sorting by an arbitrary column with keyset is an
extension point (encode that column's value alongside the key); the PK path is the safe default.

Cursor format: base64url(JSON list of primary-key values). Opaque to clients.
"""

import base64
import json
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import and_, or_

from query.ordering import primary_key_columns


def _jsonable(value):
    """Make a primary-key value JSON-serializable for the cursor."""
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def encode_cursor(pk_values) -> str:
    """Encode a row's primary-key value(s) into an opaque, URL-safe cursor string."""
    raw = json.dumps([_jsonable(v) for v in pk_values], separators=(",", ":"), default=str)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def decode_cursor(cursor: str) -> list:
    """Decode a cursor string back into its list of primary-key values."""
    raw = base64.urlsafe_b64decode(cursor.encode("ascii"))
    values = json.loads(raw)
    return values if isinstance(values, list) else [values]


def cursor_for(row, model) -> str:
    """Build the cursor that points AT ``row`` (used as the ``after`` cursor for the next page)."""
    return encode_cursor([getattr(row, column.name) for column in primary_key_columns(model)])


def _keyset_predicate(pk_columns, values):
    """Portable ``(pk...) > (values...)`` as a lexicographic OR expansion (dialect-agnostic).

    (c0 > v0) OR (c0 = v0 AND c1 > v1) OR (c0 = v0 AND c1 = v1 AND c2 > v2) ...
    """
    clauses = []
    for index in range(len(pk_columns)):
        equals = [pk_columns[col] == values[col] for col in range(index)]
        equals.append(pk_columns[index] > values[index])
        clauses.append(and_(*equals))
    return or_(*clauses)


def apply_keyset(stmt, model, after=None, limit=50):
    """Apply primary-key keyset pagination to a ``select()``.

    Orders by the full primary key ascending and (when ``after`` is given) restricts to rows beyond
    the cursor. Returns the modified statement limited to ``limit`` rows. Build the next cursor from
    the last returned row with :func:`cursor_for`; treat ``len(rows) == limit`` as "there may be
    more".
    """
    pk_columns = primary_key_columns(model)
    for column in pk_columns:
        stmt = stmt.order_by(column.asc())
    if after:
        stmt = stmt.where(_keyset_predicate(pk_columns, decode_cursor(after)))
    return stmt.limit(limit)
