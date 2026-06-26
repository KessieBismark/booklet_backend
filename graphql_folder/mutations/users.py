
import logging
import uuid
import random
from typing import Optional, List
from datetime import datetime, timezone
from dataclasses import asdict
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from strawberry.exceptions import GraphQLError
import strawberry
from strawberry import Info

from config.dbconfig import get_db
from utils.authorize_token import get_user_id, owner_column, require_permission_for, build_token_claims
from utils.rate_limiter import rate_limit
from utils.resolver_errors import handle_resolver_errors
from utils.filters import build_filter_conditions
from utils.security import verify_password, hash_password
from utils.auth_utils import create_access_token, create_refresh_token, verify_refresh_token
from utils.root_loader import apply_eager_loading

from models.users import Users
from models.users import (
    USERS_EXCLUDED_FIELDS,
    USERS_AUTO_VALIDATE_FIELDS,
    USERS_UNIQUE_FIELDS,
    USERS_INPUT_VALIDATION,
    USERS_LOADABLE_RELATIONSHIPS,
)
from ..types.users import (
    UsersType,
    UsersCreateInput,
    UsersUpdateInput,
)

from ..types.users import (
    UsersFieldInput,
    ChangeUsersFieldInput,
)


logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================

def validate_input_fields(input_data: dict, input_validation_config: dict) -> None:
    """
    Validate input data types against configuration.
    
    Args:
        input_data: Dictionary of input field names to values
        input_validation_config: Configuration mapping field names to types
    
    Raises:
        GraphQLError: If validation fails
    """
    for field_name, value in input_data.items():
        if field_name not in input_validation_config:
            continue
        
        expected_type = input_validation_config[field_name]
        type_map = {
            'int': int,
            'str': str,
            'float': float,
            'Decimal': Decimal,
            'bool': bool,
            'datetime': datetime,
        }
        
        expected = type_map.get(expected_type)
        if value is not None and expected and not isinstance(value, expected):
            raise GraphQLError(
                f"Field '{field_name}' must be {expected_type}, got {type(value).__name__}",
                extensions={"code": "VALIDATION_ERROR", "field": field_name}
            )


async def check_unique_constraints(
    db,
    table_class,
    unique_fields: set,
    input_data: dict,
    user_id: Optional[int] = None,
    exclude_id: Optional[str] = None
) -> None:
    """
    Check unique constraints for input data.
    
    Args:
        db: Database session
        table_class: SQLAlchemy model class
        unique_fields: Set of field names with unique constraints
        input_data: Data to validate
        user_id: Current user ID (for user-scoped uniqueness)
        exclude_id: ID to exclude from check (for updates)
    
    Raises:
        GraphQLError: If unique constraint would be violated
    """
    for field_name in unique_fields:
        value = input_data.get(field_name)
        if value is None:
            continue
        
        # Build query for uniqueness check
        stmt = select(table_class).where(
            getattr(table_class, field_name) == value
        )
        
        # For user-scoped uniqueness, add auth check
        _owner = owner_column(table_class)
        if user_id and _owner is not None:
            stmt = stmt.where(_owner == user_id)
        
        # Exclude current record in updates
        if exclude_id:
            stmt = stmt.where(table_class.id != exclude_id)
        
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise GraphQLError(
                f"A record with {field_name}='{value}' already exists",
                extensions={"code": "DUPLICATE_ENTRY", "field": field_name}
            )


async def get_protected_context(info: Info, info_name: str = "mutation") -> dict:
    """
    Get and validate user context with authorization.
    
    Args:
        info: Strawberry Info object
        info_name: Name of operation for logging
    
    Returns:
        Dictionary with user_id and other context
    
    Raises:
        GraphQLError: If user is not authenticated
    """
    try:
        user_id = await get_user_id(info)
        logger.debug(f"User {user_id} authorized for {info_name}")
        return {"user_id": user_id}
    except GraphQLError:
        raise
    except Exception as e:
        logger.error(f"Authorization error in {info_name}: {e}")
        raise GraphQLError(
            "Authorization failed",
            extensions={"code": "AUTHENTICATION_REQUIRED"}
        )



# ============================================================================
# Auth Token Types
# ============================================================================

@strawberry.type
class AuthTokens:
    access_token: str
    refresh_token: str


# ============================================================================
# Users Mutations
# ============================================================================

@strawberry.type
class UsersMutation:
    """GraphQL mutations for Users model"""

    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def create_users(
        self,
        info: Info,
        input: List[UsersFieldInput]
    ) -> UsersType:
        """
        Create new auth user account.
        
        Args:
            input: List of field inputs (email, password, etc.)
        
        Returns:
            Created user account
        
        Raises:
            GraphQLError: If validation fails or email already exists
        """
        try:
            # ====== Extract and validate inputs ======
            password_field = next((f for f in input if f.is_password), None)
            checker_fields = [f for f in input if f.is_checker]

            if not password_field:
                raise GraphQLError(
                    "Password field is required",
                    extensions={"code": "VALIDATION_ERROR"}
                )
            
            if not checker_fields:
                raise GraphQLError(
                    "At least one checker field (e.g., email) is required",
                    extensions={"code": "VALIDATION_ERROR"}
                )

            # ====== Check for duplicates (user-scoped) ======
            async with get_db() as db:
                for checker in checker_fields:
                    if not hasattr(Users, checker.fields):
                        raise GraphQLError(
                            f"Invalid field: {checker.fields}",
                            extensions={"code": "VALIDATION_ERROR", "field": checker.fields}
                        )
                    
                    column = getattr(Users, checker.fields)
                    stmt = select(Users).where(column == checker.value)
                    result = await db.execute(stmt)
                    existing = result.scalar_one_or_none()
                    
                    if existing:
                        raise GraphQLError(
                            f"{checker.fields.capitalize()} {checker.value} already exists",
                            extensions={"code": "DUPLICATE_ENTRY", "field": checker.fields}
                        )

                # ====== Build user data ======
                user_data = {}
                for field_input in input:
                    if not hasattr(Users, field_input.fields):
                        raise GraphQLError(
                            f"Invalid field: {field_input.fields}",
                            extensions={"code": "VALIDATION_ERROR", "field": field_input.fields}
                        )
                    
                    if field_input.is_password:
                        # Hash password before storing
                        user_data[field_input.fields] = await hash_password(field_input.value)
                    else:
                        user_data[field_input.fields] = field_input.value
                
                # Add timestamps
                user_data['created_at'] = datetime.now(timezone.utc)
                user_data['updated_at'] = datetime.now(timezone.utc)
                
                # Inject primary key if not auto-generated by the database.
                # id_value is set by static_mutation_code():
                #   str  PK  ->  str(uuid.uuid4())
                #   int  PK  ->  random.randint(100000, 999999)
                user_data['id'] = str(uuid.uuid4())

                # ====== Create and save ======
                user = Users(**user_data)
                db.add(user)
                await db.commit()
                await db.refresh(user)
                
                logger.info(f"User account created: {user.id}")
                return user

        except GraphQLError:
            raise

    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def login(
        self,
        info: Info,
        fields: List[UsersFieldInput]
    ) -> AuthTokens:
        """
        Authenticate user and return JWT access + refresh token pair.
        
        Args:
            fields: Email/username and password
        
        Returns:
            AuthTokens containing access_token and refresh_token
        
        Raises:
            GraphQLError: If credentials invalid or user not found
        """
        try:
            # ====== Extract and validate inputs ======
            password_field = next((f for f in fields if f.is_password), None)
            checker_fields = [f for f in fields if f.is_checker]

            if not password_field:
                raise GraphQLError(
                    "Password field is required",
                    extensions={"code": "VALIDATION_ERROR"}
                )
            
            if not checker_fields:
                raise GraphQLError(
                    "At least one identifier field required",
                    extensions={"code": "VALIDATION_ERROR"}
                )

            # ====== SEC002: brute-force lockout (keyed by the supplied identifier values) ======
            # Shares the auth.throttle store with the REST login, so the lockout is unified.
            from auth.throttle import is_locked, record_failed_login, reset_login_attempts
            _throttle_key = "|".join(f"{c.fields}={c.value}" for c in checker_fields)
            _locked, _retry = is_locked(_throttle_key)
            if _locked:
                raise GraphQLError(
                    f"Too many failed login attempts. Try again in {int(_retry)} seconds.",
                    extensions={"code": "LOGIN_RATE_LIMITED"}
                )

            # ====== Find user ======
            async with get_db() as db:
                stmt = select(Users)
                for checker in checker_fields:
                    if not hasattr(Users, checker.fields):
                        raise GraphQLError(
                            f"Invalid field: {checker.fields}",
                            extensions={"code": "VALIDATION_ERROR", "field": checker.fields}
                        )
                    
                    column = getattr(Users, checker.fields)
                    stmt = stmt.where(column == checker.value)

                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.warning(f"Login attempt with non-existent user")
                    record_failed_login(_throttle_key)
                    raise GraphQLError(
                        "Invalid credentials",
                        extensions={"code": "AUTHENTICATION_REQUIRED"}
                    )

                # ====== Verify password ======
                password_field_name = password_field.fields
                if not hasattr(user, password_field_name):
                    raise GraphQLError(
                        "Invalid password field",
                        extensions={"code": "VALIDATION_ERROR"}
                    )

                hashed_password = getattr(user, password_field_name)
                is_valid = await verify_password(password_field.value, hashed_password)
                
                if not is_valid:
                    logger.warning(f"Failed login attempt for user {user.id}")
                    record_failed_login(_throttle_key)
                    raise GraphQLError(
                        "Invalid credentials",
                        extensions={"code": "AUTHENTICATION_REQUIRED"}
                    )

                # ====== Successful login — clear the failure counter ======
                reset_login_attempts(_throttle_key)

                # ====== Generate token ======
                # Carry the user's RBAC claims (roles/perms/is_superuser) so server-side
                # permission checks enforce (entity-agnostic, best-effort; empty when the schema
                # has no RBAC -> app runs RBAC-unconfigured). See utils.authorize_token.
                token_payload = {"user_id": user.id}
                token_payload.update(build_token_claims(user))
                for checker in checker_fields:
                    token_payload[checker.fields] = checker.value

                logger.info(f"User {user.id} logged in successfully")
                return AuthTokens(
                    access_token=await create_access_token(token_payload),
                    refresh_token=await create_refresh_token(token_payload),
                )

        except GraphQLError:
            raise

    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def change_password(
        self,
        info: Info,
        fields: List[ChangeUsersFieldInput]
    ) -> bool:
        """
        Change user password (requires old password).
        
        Args:
            fields: Old password, new password, and identifier
        
        Returns:
            True if successful
        
        Raises:
            GraphQLError: If old password incorrect or user not found
        """
        try:
            context = await get_protected_context(info, "change_password")
            user_id = context["user_id"]

            # ====== Extract and validate inputs ======
            old_pwd = next((f for f in fields if f.is_old), None)
            new_pwd = next((f for f in fields if f.is_new), None)
            identifier = next((f for f in fields if not f.is_old and not f.is_new), None)

            if not all([old_pwd, new_pwd, identifier]):
                raise GraphQLError(
                    "Old password, new password, and identifier required",
                    extensions={"code": "VALIDATION_ERROR"}
                )

            # ====== Find user ======
            async with get_db() as db:
                if not hasattr(Users, identifier.fields):
                    raise GraphQLError(
                        f"Invalid field: {identifier.fields}",
                        extensions={"code": "VALIDATION_ERROR", "field": identifier.fields}
                    )

                column = getattr(Users, identifier.fields)
                stmt = select(Users).where(column == identifier.value)
                
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    raise GraphQLError(
                        "User not found",
                        extensions={"code": "NOT_FOUND"}
                    )

                # ====== Verify old password ======
                password_attr = next((f.fields for f in fields if f.is_password), None)
                if not password_attr or not hasattr(user, password_attr):
                    raise GraphQLError(
                        "Invalid password field",
                        extensions={"code": "VALIDATION_ERROR"}
                    )

                is_valid = await verify_password(old_pwd.value, getattr(user, password_attr))
                
                if not is_valid:
                    logger.warning(f"Failed password change attempt for user {user.id}")
                    raise GraphQLError(
                        "Old password is incorrect",
                        extensions={"code": "AUTHENTICATION_REQUIRED"}
                    )

                # ====== Update password ======
                new_hashed = await hash_password(new_pwd.value)
                setattr(user, password_attr, new_hashed)
                user.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                
                logger.info(f"User {user.id} changed password")
                return True

        except GraphQLError:
            raise

    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def refresh_access_token(
        self,
        info: Info,
        refresh_token: str
    ) -> AuthTokens:
        """
        Exchange a valid refresh token for a fresh access + refresh token pair.
        The user stays logged in silently as long as the refresh token has not expired.
        If the refresh token is expired or invalid, SESSION_EXPIRED is raised
        so the frontend can redirect the user to login.

        Args:
            refresh_token: The long-lived refresh token from a previous login

        Returns:
            AuthTokens with a new access_token and a rotated refresh_token

        Raises:
            GraphQLError: SESSION_EXPIRED if refresh token is invalid or expired
        """
        try:
            payload = await verify_refresh_token(refresh_token)
            # Strip JWT reserved claims so we don't re-sign stale exp/iat/type
            token_payload = {k: v for k, v in payload.items()
                             if k not in ("exp", "iat", "type")}
            logger.info(f"Token refreshed for user {token_payload.get('user_id')}")
            return AuthTokens(
                access_token=await create_access_token(token_payload),
                refresh_token=await create_refresh_token(token_payload),
            )
        except GraphQLError:
            raise
        except Exception as e:
            raise GraphQLError(f"Unexpected error during token refresh: {str(e)}")


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def update_users(
        self,
        info: Info,
        id: str,
        input: UsersUpdateInput,
        relationships: Optional[List[str]] = None
    ) -> UsersType:
        """
        Update Users record.
        
        Args:
            id: Record ID to update
            input: Update input with fields to change
            relationships: Optional relationships to eager load
        
        Returns:
            Updated Users
        
        Raises:
            GraphQLError: If not authorized or record not found
        """
        try:
            context = await get_protected_context(info, "update_users")
            await require_permission_for(info, "users", "update")
            user_id = context["user_id"]

            # ====== Fetch record ======
            async with get_db() as db:
                stmt = select(Users).where(Users.id == id)
                
                # Add auth check if model has auth_id
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()

                if not record:
                    raise GraphQLError(
                        "Users not found or access denied",
                        extensions={"code": "NOT_FOUND"}
                    )

                # ====== Validate relationships ======
                if relationships:
                    invalid = set(relationships) - USERS_LOADABLE_RELATIONSHIPS
                    if invalid:
                        raise GraphQLError(
                            f"Invalid relationships: {invalid}",
                            extensions={"code": "VALIDATION_ERROR"}
                        )

                # ====== Prepare update data ======
                update_dict = {k: v for k, v in asdict(input).items() if v is not None}
                validate_input_fields(update_dict, USERS_INPUT_VALIDATION)

                # Check unique constraints (excluding current record)
                await check_unique_constraints(db, Users, USERS_UNIQUE_FIELDS, update_dict, user_id, exclude_id=id)

                # Apply updates
                update_dict['updated_at'] = datetime.now(timezone.utc)
                for field, value in update_dict.items():
                    setattr(record, field, value)

                await db.commit()

                # Load relationships if requested
                if relationships:
                    stmt = select(Users).where(Users.id == id)
                    stmt = apply_eager_loading(stmt, Users, relationships, load_nested=False)
                    result = await db.execute(stmt)
                    record = result.scalar_one()

                logger.info(f"User {user_id} updated Users: {id}")
                return record

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def delete_users(
        self,
        info: Info,
        id: str,
        hard: bool = False
    ) -> bool:
        """
        Delete Users record (soft or hard delete).
        
        Args:
            id: Record ID to delete
            hard: If True, permanently delete; if False, soft delete
        
        Returns:
            True if successful
        
        Raises:
            GraphQLError: If not authorized or record not found
        """
        try:
            context = await get_protected_context(info, "delete_users")
            await require_permission_for(info, "users", "delete")
            user_id = context["user_id"]

            async with get_db() as db:
                stmt = select(Users).where(Users.id == id)
                
                _owner = owner_column(Users)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()

                if not record:
                    raise GraphQLError(
                        "Users not found or access denied",
                        extensions={"code": "NOT_FOUND"}
                    )

                # Check if already deleted
                if hasattr(record, 'is_deleted') and record.is_deleted:
                    raise GraphQLError(
                        "Users is already deleted",
                        extensions={"code": "BAD_REQUEST"}
                    )

                if hard:
                    # Hard delete - permanent removal
                    await db.delete(record)
                    delete_type = "hard"
                else:
                    # Soft delete - mark as deleted
                    if not hasattr(record, 'is_deleted'):
                        raise GraphQLError(
                            "Soft delete not supported for this model",
                            extensions={"code": "BAD_REQUEST"}
                        )
                    
                    record.is_deleted = True
                    if hasattr(record, 'deleted_at'):
                        record.deleted_at = datetime.now(timezone.utc)
                    delete_type = "soft"

                await db.commit()
                
                logger.info(f"User {user_id} {delete_type}-deleted Users: {id}")
                return True

        except GraphQLError:
            raise

