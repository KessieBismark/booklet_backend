
from functools import wraps
import logging
import uuid
from sqlalchemy.exc import SQLAlchemyError

from graphql import GraphQLError

logger = logging.getLogger(__name__)

def handle_resolver_errors(func):
    """
    Decorator for consistent error handling in resolvers.
    
    Logs errors with request ID and returns sanitized error messages.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request_id = str(uuid.uuid4())
        try:
            return await func(*args, **kwargs)
        except GraphQLError:
            raise
        except SQLAlchemyError as e:
            logger.error(
                f"[{request_id}] Database error in {func.__name__}: {e}",
                exc_info=True
            )
            raise GraphQLError(
                f"Database error occurred (request: {request_id})",
                extensions={
                    "code": "DATABASE_ERROR",
                    "requestId": request_id
                }
            )
        except ValueError as e:
            logger.warning(f"[{request_id}] Validation error: {e}")
            raise GraphQLError(
                str(e),
                extensions={
                    "code": "VALIDATION_ERROR",
                    "requestId": request_id
                }
            )
        except Exception as e:
            logger.error(
                f"[{request_id}] Unexpected error in {func.__name__}: {e}",
                exc_info=True
            )
            raise GraphQLError(
                f"An unexpected error occurred (request: {request_id})",
                extensions={
                    "code": "INTERNAL_SERVER_ERROR",
                    "requestId": request_id
                }
            )
    return wrapper



