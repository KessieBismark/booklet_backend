


from datetime import datetime
import logging
from typing import Any, List, Optional, Type
from graphql import GraphQLError
from sqlalchemy import String, and_, cast, func, or_
from utils.enums import LogicalOperator


logger = logging.getLogger(__name__)

def build_filter_conditions(
    model_class,
    filters: Optional[List],
    logic: Optional[LogicalOperator] = LogicalOperator.AND,
):
    """Build filter conditions with proper type handling."""
    conditions = []

    if not filters:
        return None

    for f in filters:
        # Validate field exists and is queryable
        if not hasattr(model_class, f.field):
            raise GraphQLError(
                f"Field '{f.field}' does not exist on {model_class.__name__}",
                extensions={"code": "VALIDATION_ERROR"}
            )
        
        column = getattr(model_class, f.field)
        
        # Type casting with proper error handling
        try:
            col_type = column.type.python_type
            casted_value = _cast_value(f.value, col_type, f.operator)
        except ValueError as e:
            raise GraphQLError(
                f"Invalid value for field '{f.field}': {str(e)}",
                extensions={"code": "VALIDATION_ERROR", "field": f.field}
            )
        except Exception as e:
            logging.error(f"Type casting error: {e}", exc_info=True)
            raise GraphQLError(
                f"Cannot process filter for field '{f.field}'",
                extensions={"code": "VALIDATION_ERROR"}
            )
        
        # Build condition
        try:
            condition = _build_operator_condition(column, f.operator, casted_value)
            if condition is not None:
                conditions.append(condition)
        except Exception as e:
            raise GraphQLError(
                f"Invalid operator '{f.operator}' for field '{f.field}': {str(e)}",
                extensions={"code": "VALIDATION_ERROR"}
            )
    
    # Combine conditions
    if not conditions:
        return None

    return or_(*conditions) if logic == LogicalOperator.OR else and_(*conditions)


def _cast_value(value: Any, target_type: Type, operator: str) -> Any:
    """
    Cast value to target type with validation.
    
    Raises:
        ValueError: If casting fails or value is invalid for operator
    """
    if value is None:
        if operator != "is_null":
            raise ValueError("Value cannot be None for this operator")
        return None
    
    if target_type is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "1", "yes"]
        raise ValueError(f"Cannot convert {type(value).__name__} to bool")
    
    elif target_type is datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Invalid datetime format: {value}")
        raise ValueError(f"Cannot convert {type(value).__name__} to datetime")
    
    elif target_type in (int, float):
        # Parse comma-separated list for the "in" operator.
        if operator == "in" and isinstance(value, str):
            parts = [p.strip() for p in value.split(',')]
            try:
                return [target_type(p) for p in parts]
            except Exception:
                return parts  # fallback: keep as list of strings
        try:
            return target_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert {value} to {target_type.__name__}")
    
    elif target_type is str:
        # Parse comma-separated list for the "in" operator.
        if operator == "in" and isinstance(value, str):
            return [p.strip() for p in value.split(',')]
        return str(value)
    
    else:
        # Parse comma-separated list for the "in" operator.
        if operator == "in" and isinstance(value, str):
            parts = [p.strip() for p in value.split(',')]
            try:
                return [target_type(p) for p in parts]
            except Exception:
                return parts
        # Try direct conversion
        try:
            return target_type(value)
        except Exception as e:
            raise ValueError(f"Cannot convert to {target_type.__name__}: {str(e)}")


def _build_operator_condition(column, operator: str, value: Any):
    """Build SQLAlchemy condition for given operator."""
    if operator == "eq":
        return column == value
    elif operator == "ne":
        return column != value
    elif operator == "lt":
        return column < value
    elif operator == "lte":
        return column <= value
    elif operator == "gt":
        return column > value
    elif operator == "gte":
        return column >= value
    elif operator == "in":
        if not isinstance(value, list):
            raise ValueError("'in' operator requires a list")
        return column.in_(value)
    elif operator == "contains":
        return func.lower(cast(column, String)).ilike(f"%{str(value).lower()}%")
    elif operator == "is_null":
        return column.is_(None) if value else column.is_not(None)
    else:
        raise ValueError(f"Unsupported operator: {operator}")
        
