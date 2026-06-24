
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

from models.genres import Genres
from models.genres import (
    GENRES_EXCLUDED_FIELDS,
    GENRES_AUTO_VALIDATE_FIELDS,
    GENRES_UNIQUE_FIELDS,
    GENRES_INPUT_VALIDATION,
    GENRES_LOADABLE_RELATIONSHIPS,
)
from ..types.genres import (
    GenresType,
    GenresCreateInput,
    GenresUpdateInput,
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
        if expected and not isinstance(value, expected):
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


def get_protected_context(info: Info, info_name: str = "mutation") -> dict:
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
        user_id = get_user_id(info)
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
# Genres Mutations
# ============================================================================

@strawberry.type
class GenresMutation:
    """GraphQL mutations for Genres model"""

    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def create_genres(
        self,
        info: Info,
        input: GenresCreateInput,
        relationships: Optional[List[str]] = None
    ) -> GenresType:
        """
        Create new Genres record.
        
        Args:
            input: Create input with required fields
            relationships: Optional relationships to eager load
        
        Returns:
            Created Genres
        
        Raises:
            GraphQLError: If validation fails or unique constraint violated
        """
        try:
            context = get_protected_context(info, "create_genres")
            await require_permission_for(info, "genres", "create")
            user_id = context["user_id"]

            # ====== Validate input ======
            input_dict = asdict(input)
            validate_input_fields(input_dict, GENRES_INPUT_VALIDATION)

            # ====== Auto-validate auth fields ======
            for auth_field in GENRES_AUTO_VALIDATE_FIELDS:
                if auth_field in input_dict:
                    if input_dict[auth_field] != user_id:
                        raise GraphQLError(
                            f"Cannot create {auth_field} for another user",
                            extensions={"code": "FORBIDDEN", "field": auth_field}
                        )
                else:
                    # Auto-set auth field to current user
                    input_dict[auth_field] = user_id

            # ====== Validate relationships ======
            if relationships:
                invalid = set(relationships) - GENRES_LOADABLE_RELATIONSHIPS
                if invalid:
                    raise GraphQLError(
                        f"Invalid relationships: {invalid}",
                        extensions={"code": "VALIDATION_ERROR"}
                    )

            # ====== Create record ======
            async with get_db() as db:
                # Check unique constraints
                await check_unique_constraints(db, Genres, GENRES_UNIQUE_FIELDS, input_dict, user_id)

                # Prepare data
                create_data = {k: v for k, v in input_dict.items() if v is not None}
                create_data['created_at'] = datetime.now(timezone.utc)
                create_data['updated_at'] = datetime.now(timezone.utc)
                
                # Inject primary key if not auto-generated by the database.
                # id_value is set by static_mutation_code():
                #   str  PK  ->  str(uuid.uuid4())
                #   int  PK  ->  random.randint(100000, 999999)
                create_data['id'] = str(uuid.uuid4())

                # Create and save
                record = Genres(**create_data)
                db.add(record)
                await db.commit()
                await db.refresh(record)

                # Load relationships if requested
                if relationships:
                    stmt = select(Genres).where(Genres.id == record.id)
                    stmt = apply_eager_loading(stmt, Genres, relationships, load_nested=False)
                    result = await db.execute(stmt)
                    record = result.scalar_one()

                logger.info(f"User {user_id} created Genres: {record.id}")
                return record

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def update_genres(
        self,
        info: Info,
        id: str,
        input: GenresUpdateInput,
        relationships: Optional[List[str]] = None
    ) -> GenresType:
        """
        Update Genres record.
        
        Args:
            id: Record ID to update
            input: Update input with fields to change
            relationships: Optional relationships to eager load
        
        Returns:
            Updated Genres
        
        Raises:
            GraphQLError: If not authorized or record not found
        """
        try:
            context = get_protected_context(info, "update_genres")
            await require_permission_for(info, "genres", "update")
            user_id = context["user_id"]

            # ====== Fetch record ======
            async with get_db() as db:
                stmt = select(Genres).where(Genres.id == id)
                
                # Add auth check if model has auth_id
                _owner = owner_column(Genres)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()

                if not record:
                    raise GraphQLError(
                        "Genres not found or access denied",
                        extensions={"code": "NOT_FOUND"}
                    )

                # ====== Validate relationships ======
                if relationships:
                    invalid = set(relationships) - GENRES_LOADABLE_RELATIONSHIPS
                    if invalid:
                        raise GraphQLError(
                            f"Invalid relationships: {invalid}",
                            extensions={"code": "VALIDATION_ERROR"}
                        )

                # ====== Prepare update data ======
                update_dict = {k: v for k, v in asdict(input).items() if v is not None}
                validate_input_fields(update_dict, GENRES_INPUT_VALIDATION)

                # Check unique constraints (excluding current record)
                await check_unique_constraints(db, Genres, GENRES_UNIQUE_FIELDS, update_dict, user_id, exclude_id=id)

                # Apply updates
                update_dict['updated_at'] = datetime.now(timezone.utc)
                for field, value in update_dict.items():
                    setattr(record, field, value)

                await db.commit()

                # Load relationships if requested
                if relationships:
                    stmt = select(Genres).where(Genres.id == id)
                    stmt = apply_eager_loading(stmt, Genres, relationships, load_nested=False)
                    result = await db.execute(stmt)
                    record = result.scalar_one()

                logger.info(f"User {user_id} updated Genres: {id}")
                return record

        except GraphQLError:
            raise


    @strawberry.field
    @rate_limit
    @handle_resolver_errors
    async def delete_genres(
        self,
        info: Info,
        id: str,
        hard: bool = False
    ) -> bool:
        """
        Delete Genres record (soft or hard delete).
        
        Args:
            id: Record ID to delete
            hard: If True, permanently delete; if False, soft delete
        
        Returns:
            True if successful
        
        Raises:
            GraphQLError: If not authorized or record not found
        """
        try:
            context = get_protected_context(info, "delete_genres")
            await require_permission_for(info, "genres", "delete")
            user_id = context["user_id"]

            async with get_db() as db:
                stmt = select(Genres).where(Genres.id == id)
                
                _owner = owner_column(Genres)
                if _owner is not None:
                    stmt = stmt.where(_owner == user_id)
                
                result = await db.execute(stmt)
                record = result.scalar_one_or_none()

                if not record:
                    raise GraphQLError(
                        "Genres not found or access denied",
                        extensions={"code": "NOT_FOUND"}
                    )

                # Check if already deleted
                if hasattr(record, 'is_deleted') and record.is_deleted:
                    raise GraphQLError(
                        "Genres is already deleted",
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
                
                logger.info(f"User {user_id} {delete_type}-deleted Genres: {id}")
                return True

        except GraphQLError:
            raise

