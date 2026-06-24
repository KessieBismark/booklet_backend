



import logging
from typing import Optional

from graphql import GraphQLError
from strawberry import Info
from utils.auth_utils import decode_token

# Security-audit log (SEC001): authorization denials and admin overrides are recorded here. Point a
# handler at the "security.audit" logger (or ship it to your SIEM) to retain an audit trail.
_audit_logger = logging.getLogger("security.audit")


def audit_event(event: str, **fields) -> None:
    """Emit a structured security-audit event (e.g. authorization_denied, admin_override)."""
    detail = " ".join(f"{k}={v}" for k, v in fields.items() if v is not None)
    _audit_logger.info("security_audit event=%s %s", event, detail)


async def get_user_id(info: Info) -> str:
    """
    Extract and validate user ID from JWT token in Authorization header (async version).
    
    Raises:
        GraphQLError: If user is not authenticated or token is invalid
    """
    # Get request from context
    context = info.context
    if not context:
        raise GraphQLError(
            "Request context not available",
            extensions={"code": "SERVER_ERROR"}
        )
    
    # Try to get user from middleware first (if exists)
    user = context.get('user')
    if user and hasattr(user, 'id'):
        return str(user.id)
    
    # If no middleware, extract and verify token from headers
    request = context.get('request')
    if not request:
        raise GraphQLError(
            "Request context not available",
            extensions={"code": "SERVER_ERROR"}
        )
    
    # Get Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise GraphQLError(
            "Authentication required to access this resource",
            extensions={"code": "AUTHENTICATION_REQUIRED"}
        )
    
    # Check Bearer format
    if not auth_header.startswith("Bearer "):
        raise GraphQLError(
            "Invalid authorization format. Use 'Bearer <token>'",
            extensions={"code": "AUTHENTICATION_ERROR"}
        )
    
    # Extract token
    token = auth_header.split(" ")[1]
    if not token:
        raise GraphQLError(
            "Empty token provided",
            extensions={"code": "AUTHENTICATION_ERROR"}
        )
    
    # Decode and verify token using your existing async function
    payload = await decode_token(token)
    
    if not payload:
        raise GraphQLError(
            "Invalid or expired token",
            extensions={"code": "AUTHENTICATION_ERROR"}
        )
    
    # Extract user_id from payload
    user_id = payload.get("user_id")
    if not user_id:
        raise GraphQLError(
            "Invalid token payload - missing user_id",
            extensions={"code": "AUTHENTICATION_ERROR"}
        )
    
    return user_id


# Owner-column conventions used for row-level authorization scoping (SEC001).
_OWNER_COLUMN_CANDIDATES = ("auth_id", "user_id", "owner_id", "created_by", "author_id", "account_id")


def owner_column(model):
    """
    Return the model's ownership column attribute for row-level scoping, or None when the
    model has no recognized owner column.

    Generalizes ownership beyond 'auth_id' so update/delete/list operations are scoped to the
    record owner for any model that carries a conventional owner column. NOTE: a model with NO
    recognized owner column returns None and is therefore NOT owner-scoped here -- such models
    require an explicit RBAC/permission policy (the IDOR fix for owner-less models -- e.g. a
    child/relationship entity with no owner column -- is part of the SEC001 RBAC design, not this
    scoping helper).
    """
    for _name in _OWNER_COLUMN_CANDIDATES:
        if hasattr(model, _name):
            return getattr(model, _name)
    return None


# ===========================================================================
# RBAC authorization context + checks (SEC001)
# ===========================================================================

async def _get_token_payload(info: Info) -> dict:
    """Extract and decode the JWT from the Authorization header; return its payload.

    Raises GraphQLError when the token is missing, malformed, or invalid.
    """
    context = info.context
    if not context:
        raise GraphQLError("Request context not available", extensions={"code": "SERVER_ERROR"})
    request = context.get("request")
    if not request:
        raise GraphQLError("Request context not available", extensions={"code": "SERVER_ERROR"})
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise GraphQLError("Authentication required to access this resource",
                           extensions={"code": "AUTHENTICATION_REQUIRED"})
    if not auth_header.startswith("Bearer "):
        raise GraphQLError("Invalid authorization format. Use 'Bearer <token>'",
                           extensions={"code": "AUTHENTICATION_ERROR"})
    token = auth_header.split(" ")[1]
    if not token:
        raise GraphQLError("Empty token provided", extensions={"code": "AUTHENTICATION_ERROR"})
    payload = await decode_token(token)
    if not payload:
        raise GraphQLError("Invalid or expired token", extensions={"code": "AUTHENTICATION_ERROR"})
    return payload


async def get_auth_context(info: Info) -> dict:
    """Build the authorization context from the request's JWT.

    Returns {"user_id", "roles", "perms", "is_superuser"} -- the inputs to RBAC checks.
    'perms' is the flattened "resource.action" set carried in the token (resolved at login).
    """
    payload = await _get_token_payload(info)
    user_id = payload.get("user_id")
    if not user_id:
        raise GraphQLError("Invalid token payload - missing user_id",
                           extensions={"code": "AUTHENTICATION_ERROR"})
    return {
        "user_id": user_id,
        "roles": list(payload.get("roles", []) or []),
        "perms": set(payload.get("perms", []) or []),
        "is_superuser": bool(payload.get("is_superuser", False)),
    }


def is_admin(context: dict) -> bool:
    """True when the context is a superuser or holds the 'admin' role (break-glass override)."""
    return bool(context.get("is_superuser")) or ("admin" in (context.get("roles") or ()))


def rbac_configured(context: dict) -> bool:
    """True when the token carries any RBAC signal (perms, roles, or superuser).

    Enforce-when-configured: a token with NO RBAC signal means the app has not wired RBAC yet,
    so permission checks pass (backward compatible, works out-of-the-box). Once login populates
    perms/roles/is_superuser, checks are enforced. Tokens are signed, so claims can't be forged.
    """
    return bool(context.get("perms")) or bool(context.get("roles")) or bool(context.get("is_superuser"))


# Action synonyms: the canonical server-side verbs (read/create/update/delete) and
# the common UI/permission-matrix vocabulary that maps onto them. A token minted
# from a frontend permission set ('posts.view', 'posts.edit', ...) thus satisfies
# the resolver checks ('post.read', 'post.update', ...) without re-seeding.
_ACTION_SYNONYMS = {
    "read": "read", "view": "read", "list": "read", "get": "read", "show": "read",
    "create": "create", "add": "create", "new": "create",
    "update": "update", "edit": "update", "modify": "update", "change": "update",
    "delete": "delete", "remove": "delete", "destroy": "delete",
}


def _canon_action(action: str) -> str:
    """Map an action verb to its canonical form ('view' -> 'read')."""
    a = str(action).lower()
    return _ACTION_SYNONYMS.get(a, a)


def _canon_resource(resource: str) -> str:
    """Fold a simple trailing-plural so 'posts' and 'post' compare equal.

    Resolver resource names follow the table name and are inconsistently
    singular/plural ('post' vs 'comments'); a frontend matrix tends to pluralize
    ('posts', 'comments'). Stripping one trailing 's' on both sides reconciles
    them without a hardcoded entity map.
    """
    r = str(resource).lower()
    return r[:-1] if (len(r) > 1 and r.endswith("s")) else r


def _canon_perm(code: str) -> str:
    """Canonicalize a 'resource.action' permission code for comparison."""
    code = str(code)
    if "." not in code:
        return code.lower()
    resource, _, action = code.rpartition(".")
    return f"{_canon_resource(resource)}.{_canon_action(action)}"


def _perm_satisfied(context: dict, resource: str, action: str) -> bool:
    """True when the token's perms grant `resource.action` (synonym/plural aware)."""
    required = _canon_perm(f"{resource}.{action}")
    return required in {_canon_perm(p) for p in (context.get("perms") or ())}


def has_permission(context: dict, resource: str, action: str) -> bool:
    """Non-raising permission check.

    - RBAC unconfigured (no signal in token) -> allow (backward compatible).
    - Admin/superuser -> allow (override).
    - Otherwise -> membership of "resource.action" in the flattened 'perms' set
      (default-deny), normalizing action synonyms and singular/plural resources.
    """
    if not rbac_configured(context):
        return True
    if is_admin(context):
        return True
    return _perm_satisfied(context, resource, action)


def require_permission(context: dict, resource: str, action: str) -> None:
    """Enforce a permission; raise FORBIDDEN when missing.

    Admin/superuser bypasses (audited as 'admin_override'); denials are audited as
    'authorization_denied'. RBAC-unconfigured tokens pass silently (backward compatible).
    """
    if not rbac_configured(context):
        return
    if is_admin(context):
        audit_event(
            "admin_override",
            user_id=context.get("user_id"),
            resource=resource,
            action=action,
        )
        return
    if _perm_satisfied(context, resource, action):
        return
    audit_event(
        "authorization_denied",
        user_id=context.get("user_id"),
        resource=resource,
        action=action,
    )
    raise GraphQLError(
        "Permission denied",
        extensions={"code": "FORBIDDEN", "required": f"{resource}.{action}"},
    )


async def require_permission_for(info: Info, resource: str, action: str) -> dict:
    """Resolver-side guard: build the auth context from the request and enforce a permission.

    One-line entry point for generated resolvers:
        await require_permission_for(info, "<resource>", "<action>")
    Enforce-when-configured: passes for tokens without RBAC claims; enforces once login populates
    roles/perms (see has_permission). Returns the auth context for any further use.
    """
    context = await get_auth_context(info)
    require_permission(context, resource, action)
    return context


# ===========================================================================
# Login token-claim population (SEC001 phase 1) -- entity-agnostic, best-effort
# ===========================================================================
#
# Conventional attribute names used to introspect the authenticated user for its RBAC claims.
# These are DUCK-TYPED names only -- never a hardcoded entity/model name -- so the same code works
# for ANY schema. If your user model exposes none of them, claims stay empty and the app runs
# RBAC-unconfigured (enforce-when-configured: every permission check passes until real role
# resolution is wired here). Adjust the tuples / build_token_claims() body for your schema.
_SUPERUSER_ATTRS = ("is_superuser", "is_admin", "superuser")
_ROLE_COLLECTION_ATTRS = ("roles", "user_roles", "role_list")
_ROLE_SCALAR_ATTRS = ("role", "role_name")
_ROLE_NAME_ATTRS = ("name", "code", "slug", "title", "role_name")
_PERMISSION_COLLECTION_ATTRS = ("permissions", "perms", "role_permissions")
_PERMISSION_CODE_ATTRS = ("code", "name", "slug")          # already a "resource.action" string
_PERMISSION_RESOURCE_ATTRS = ("resource", "resource_name", "entity", "model")
_PERMISSION_ACTION_ATTRS = ("action", "operation", "verb")


def _first_attr(obj, names):
    """Return the first present, non-None attribute value among `names`, else None."""
    for _name in names:
        value = getattr(obj, _name, None)
        if value is not None:
            return value
    return None


def _as_iterable(value):
    """Coerce a relationship/scalar into a list (a string is treated as a single item)."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def _role_name(role) -> Optional[str]:
    """Resolve a role object/string to its name."""
    if isinstance(role, str):
        return role
    value = _first_attr(role, _ROLE_NAME_ATTRS)
    return str(value) if value is not None else None


def _permission_code(perm) -> Optional[str]:
    """Normalize a permission object/string into a flattened "resource.action" code."""
    if isinstance(perm, str):
        return perm
    code = _first_attr(perm, _PERMISSION_CODE_ATTRS)
    if code is not None:
        return str(code)
    resource = _first_attr(perm, _PERMISSION_RESOURCE_ATTRS)
    action = _first_attr(perm, _PERMISSION_ACTION_ATTRS)
    if resource is not None and action is not None:
        return f"{resource}.{action}"
    return None


def build_token_claims(user) -> dict:
    """Best-effort RBAC claims for the access token: {"roles", "perms", "is_superuser"}.

    Entity-agnostic: introspects `user` via the conventional attribute names above (never a
    hardcoded entity name) and flattens roles -> permissions into a "resource.action" set that
    resolvers check cheaply (see has_permission). Fully guarded -- ANY failure (e.g. accessing an
    unloaded async relationship) yields empty claims so login never breaks and the app simply runs
    RBAC-unconfigured. For async apps, eager-load the user's roles/permissions before login if you
    want populated claims, or replace this body with your own resolution.
    """
    try:
        is_superuser = any(bool(getattr(user, _attr, None)) for _attr in _SUPERUSER_ATTRS)

        role_objs = _first_attr(user, _ROLE_COLLECTION_ATTRS)
        if role_objs is None:
            role_objs = _first_attr(user, _ROLE_SCALAR_ATTRS)

        roles = []
        perms = set()
        for role in _as_iterable(role_objs):
            name = _role_name(role)
            if name:
                roles.append(name)
                # Some schemas store flattened "resource.action" permission codes
                # DIRECTLY in the roles[] collection (e.g. a Postgres ARRAY(Text)
                # column populated from a UI permission matrix) instead of role
                # objects carrying a .permissions relationship. A bare dotted
                # string is therefore a permission, not a role label — enforce it
                # as one so the check below ('perms' membership) honors it.
                if isinstance(role, str) and "." in name:
                    perms.add(name)
            for perm in _as_iterable(_first_attr(role, _PERMISSION_COLLECTION_ATTRS)):
                code = _permission_code(perm)
                if code:
                    perms.add(code)

        # Permissions attached directly to the user (in addition to role-derived ones).
        for perm in _as_iterable(_first_attr(user, _PERMISSION_COLLECTION_ATTRS)):
            code = _permission_code(perm)
            if code:
                perms.add(code)

        # JSON-serializable (lists, not a set) so the JWT can carry them.
        return {"roles": roles, "perms": sorted(perms), "is_superuser": is_superuser}
    except Exception:
        # Never let claim introspection break login -- fall back to RBAC-unconfigured.
        return {"roles": [], "perms": [], "is_superuser": False}


