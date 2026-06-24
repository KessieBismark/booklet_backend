
"""
Database eager loading utility for SQLAlchemy.

Provides optimized eager loading strategies to prevent N+1 query problems
while avoiding exponential query explosion from deep recursion.

WARNING: Keep max_depth <= 2. Each depth level multiplies queries exponentially.
"""

from typing import List, Set, Type, Optional, Dict
from sqlalchemy.orm import selectinload, RelationshipProperty
from sqlalchemy.sql import Select
from sqlalchemy import inspect
from sqlalchemy.exc import InvalidRequestError
import sys
import logging

logger = logging.getLogger("eager_loading")

# Safe defaults
DEFAULT_EAGER_LOAD_DEPTH = 2
MAX_EAGER_LOAD_DEPTH = 3


def get_all_relationships(model: Type) -> List[str]:
    """
    Discover all relationships of a SQLAlchemy model.
    
    Args:
        model: SQLAlchemy mapped class
    
    Returns:
        List of relationship attribute names
    
    Raises:
        TypeError: If model is not a valid SQLAlchemy mapped class
    """
    try:
        mapper = inspect(model)
    except InvalidRequestError as e:
        raise TypeError(
            f"{{model.__name__}} is not a valid SQLAlchemy mapped class. "
            f"Error: {{e}}"
        )
    
    return [rel.key for rel in mapper.relationships]

def build_recursive_loader(
    model: Type,
    depth: int = DEFAULT_EAGER_LOAD_DEPTH,
    visited_models: Optional[Set[Type]] = None,
    _recursion_depth: int = 0
) -> List:
    """Recursively build chained selectinload options."""
    if visited_models is None:
        visited_models = set()
    
    if depth <= 0 or model in visited_models:
        return []
    
    if depth > MAX_EAGER_LOAD_DEPTH:
        raise ValueError(
            f"Depth {{depth}} exceeds maximum safe depth ({{MAX_EAGER_LOAD_DEPTH}})."
        )
    
    if _recursion_depth > sys.getrecursionlimit() - 100:
        raise RecursionError(
            f"Recursive eager loading exceeded Python recursion limit"
        )
    
    visited_models.add(model)
    loader_options = []
    
    try:
        mapper = inspect(model)
    except InvalidRequestError:
        return []
    
    for rel in mapper.relationships:
        related_model = rel.mapper.class_
        
        if related_model in visited_models:
            continue
        
        rel_attr = getattr(model, rel.key)
        
        # Get nested loaders for this relationship
        nested_visited = visited_models.copy()  # Create copy for this branch
        nested_loaders = build_recursive_loader(
            related_model,
            depth - 1,
            nested_visited,
            _recursion_depth + 1
        )
        
        # Chain the loaders properly
        if nested_loaders:
            loader = selectinload(rel_attr).options(*nested_loaders)
        else:
            loader = selectinload(rel_attr)
        
        loader_options.append(loader)
    
    return loader_options


def apply_eager_loading(
    stmt: Select,
    model: Type,
    relationships: Optional[List[str]] = None,
    load_nested: bool = True,
    max_depth: int = DEFAULT_EAGER_LOAD_DEPTH,
    debug: bool = False
) -> Select:
    """
    Apply eager loading for relationships on a SQLAlchemy select statement.
    
    Uses selectinload() by default:
    - Generates separate SELECT for each relationship
    - Avoids Cartesian product issues with JOINs
    - More memory efficient for large result sets
    - Typically 2-3 queries instead of 1 massive JOIN
    
    Args:
        stmt: SQLAlchemy select() statement to modify
        model: SQLAlchemy model class being queried
        relationships: List of specific relationship names to load.
                      If None and load_nested=False, loads all relationships.
        load_nested: If True, recursively load nested relationships up to max_depth.
                    If False, only load top-level relationships.
        max_depth: Maximum recursion depth for nested loading (keep <= 2).
                  WARNING: Each level multiplies queries exponentially!
        debug: If True, print debug information about loaded relationships
    
    Returns:
        Modified select statement with eager loading options applied
    
    Raises:
        ValueError: If max_depth exceeds safe limits or invalid relationships
        TypeError: If model is not a SQLAlchemy mapped class
    
    Example - Load all nested relationships:
        stmt = select(User)
        stmt = apply_eager_loading(stmt, User, load_nested=True, max_depth=2)
        users = session.execute(stmt).scalars()
    
    Example - Load specific relationships only:
        stmt = select(User)
        stmt = apply_eager_loading(
            stmt, 
            User,
            relationships=['related_one', 'related_two'],
            load_nested=False
        )
        users = session.execute(stmt).scalars()
    """
    if max_depth > MAX_EAGER_LOAD_DEPTH:
        raise ValueError(
            f"max_depth={{max_depth}} exceeds maximum ({{MAX_EAGER_LOAD_DEPTH}}). "
            f"Recursive eager loading grows exponentially. Recommended: {{DEFAULT_EAGER_LOAD_DEPTH}}"
        )
    
    # Recursive eager loading
    if load_nested:
        loader_options = build_recursive_loader(model, depth=max_depth)
        result = stmt.options(*loader_options)
        
        if debug:
            logger.debug(f"[DEBUG] Applied {len(loader_options)} recursive loaders "
                  f"to {model.__name__} (depth={max_depth})")
        
        return result
    
    # Non-recursive: load specific relationships
    if relationships is None:
        relationships = get_all_relationships(model)
    
    # Validate requested relationships
    try:
        mapper = inspect(model)
    except InvalidRequestError:
        raise TypeError(f"{model} is not a valid SQLAlchemy mapped class")
    
    available_rels = {rel.key for rel in mapper.relationships}
    invalid_rels = set(relationships) - available_rels
    
    if invalid_rels:
        raise ValueError(
            f"Invalid relationships for {model.__name__}: {invalid_rels}. "
            f"Available: {sorted(available_rels)}"
        )
    
    loader_options = []
    for rel_name in relationships:
        # Double-check it's actually a relationship (not a column)
        if not isinstance(mapper.attrs[rel_name], RelationshipProperty):
            raise TypeError(
                f"{rel_name} on {model.__name__} is not a relationship. "
                f"Only relationships can be eagerly loaded."
            )
        
        rel_attr = getattr(model, rel_name)
        loader_options.append(selectinload(rel_attr))
    
    if debug:
        logger.debug(f"[DEBUG] Applied {len(loader_options)} eager loaders "
              f"to {model.__name__}: {relationships}")
    
    return stmt.options(*loader_options)


def apply_eager_loading_paths(
    stmt: Select,
    model: Type,
    paths: List[str],
    debug: bool = False
) -> Select:
    """
    Apply chained selectinload options from dot-notation paths.
    
    Args:
        stmt: SQLAlchemy select statement
        model: Base model class
        paths: List of dot-notation paths like ['relation', 'relation.nested']
        debug: Enable debug logging
    
    Returns:
        Modified select statement with eager loading options
    """
    from sqlalchemy.orm import Load
    from sqlalchemy import inspect as sa_inspect
    
    # Build a tree of paths
    paths_tree = {}
    for path in paths:
        parts = path.split('.')
        current = paths_tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    def build_loaders(model_cls, subtree):
        """ Recursively build selectinload chains from path tree. """

        loaders = []
        try:
            mapper = sa_inspect(model_cls)
        except Exception:
            return loaders
        
        for rel_name, deeper in subtree.items():
            if rel_name not in mapper.relationships:
                continue
            
            rel_attr = getattr(model_cls, rel_name)
            related_model = mapper.relationships[rel_name].mapper.class_
            
            if deeper:
                # Build nested loaders
                nested = build_loaders(related_model, deeper)
                if nested:
                    loaders.append(selectinload(rel_attr).options(*nested))
                else:
                    loaders.append(selectinload(rel_attr))
            else:
                loaders.append(selectinload(rel_attr))
        
        return loaders
    
    options_list = build_loaders(model, paths_tree)
    
    if debug and options_list:
        logger.debug(f"[DEBUG] Applying eager loading paths: {paths}")
        logger.debug(f"[DEBUG] Generated {len(options_list)} loader options")
    
    return stmt.options(*options_list) if options_list else stmt
    
def apply_eager_loading_with_filters(
    stmt: Select,
    model: Type,
    relationship_filters: Optional[Dict[str, any]] = None,
    max_depth: int = DEFAULT_EAGER_LOAD_DEPTH,
    debug: bool = False
) -> Select:
    """
    Apply eager loading with filtering on specific relationships.
    
    Allows loading only a subset of related records, e.g., only recent related rows.
    
    Args:
        stmt: SQLAlchemy select() statement
        model: SQLAlchemy model class
        relationship_filters: Dict mapping relationship name to filter condition
        max_depth: Maximum depth for nested loading
        debug: Print debug info
    
    Example:
        stmt = select(User)
        stmt = apply_eager_loading_with_filters(
            stmt,
            User,
            relationship_filters={
                'related_one': RelatedOne.is_active == True,
                'related_two': RelatedTwo.status == 'active'
            }
        )
    
    Note:
        This uses contains_eager() instead of selectinload() for filtered
        relationships, which requires a join() to be present in the query.
    """
    from sqlalchemy.orm import contains_eager
    
    if relationship_filters is None:
        # Fall back to standard eager loading
        return apply_eager_loading(
            stmt, model, load_nested=True, max_depth=max_depth, debug=debug
        )
    
    mapper = inspect(model)
    loader_options = []
    
    for rel_name, filter_cond in relationship_filters.items():
        if rel_name not in {rel.key for rel in mapper.relationships}:
            raise ValueError(
                f"Invalid relationship: {rel_name} on {model.__name__}"
            )
        
        rel_attr = getattr(model, rel_name)
        # contains_eager requires a join in the statement
        loader = contains_eager(rel_attr).where(filter_cond)
        loader_options.append(loader)
    
    if debug:
        logger.debug(f"[DEBUG] Applied {len(loader_options)} filtered loaders "
              f"to {model.__name__}")
    
    return stmt.options(*loader_options)


def get_relationship_paths_from_query(
    info,
    model: Type,
    root_field: str = "items",
    max_depth: int = MAX_EAGER_LOAD_DEPTH
) -> List[str]:
    """
    Walk the GraphQL selection set and return dot-notation eager load paths
    for any selected field that maps to a SQLAlchemy relationship.

    Example:
        Query:   parentList > items > relation > nested > id
        Returns: ["relation", "relation.nested"]
    """
    paths: List[str] = []

    def _get_rels(m: Type) -> set:
        try:
            return {rel.key for rel in inspect(m).relationships}
        except InvalidRequestError:
            return set()

    def _get_related_model(m: Type, rel_name: str):
        try:
            return inspect(m).relationships[rel_name].mapper.class_
        except (InvalidRequestError, KeyError):
            return None

    def _walk(selections, current_model: Type, prefix: str, depth: int):
        if depth > max_depth:
            return
        rels = _get_rels(current_model)
        for field in selections:
            if not hasattr(field, 'name'):
                continue
            field_name = field.name
            if field_name not in rels:
                continue
            path = f"{prefix}.{field_name}" if prefix else field_name
            paths.append(path)
            related_model = _get_related_model(current_model, field_name)
            if related_model and getattr(field, 'selections', None):
                _walk(field.selections, related_model, path, depth + 1)

    try:
        for top_field in info.selected_fields:
            items_field = next(
                (f for f in top_field.selections if f.name == root_field), None
            )
            if items_field and items_field.selections:
                _walk(items_field.selections, model, "", 0)
                break
    except Exception:
        pass

    return paths



        