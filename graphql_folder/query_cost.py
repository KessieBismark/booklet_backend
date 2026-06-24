"""
GraphQL query cost (complexity) limiting (OPS008) -- entity-agnostic.

Defends against expensive queries, a DoS surface that depth-limiting alone does not cover: a wide or
heavily-aliased query can be shallow yet enormous. The cost of an operation is the number of selected
fields, where each list field multiplies its subtree by the list's page size (the `limit`/`first`/
`last`/`page_size` argument, or DEFAULT_LIST_MULTIPLIER when unspecified) -- so a paginated list of N
expands its children N-fold. Added to the schema as a graphql-core validation rule (alongside
QueryDepthLimiter), so over-budget operations are rejected before execution.

Tune the budget with the QUERY_COST_LIMIT environment variable (default 1000).
"""

import os

from graphql import GraphQLError
from graphql.language import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    InlineFragmentNode,
    IntValueNode,
    OperationDefinitionNode,
)
from graphql.validation import ValidationRule

# When a list field has no explicit page-size argument, assume this many rows for costing.
DEFAULT_LIST_MULTIPLIER = 10
# Arguments that bound a list's size.
PAGINATION_ARGS = ("limit", "first", "last", "page_size")


def get_max_query_cost() -> int:
    """Maximum allowed operation cost (from QUERY_COST_LIMIT, default 1000)."""
    try:
        return max(1, int(os.getenv("QUERY_COST_LIMIT", "1000")))
    except (TypeError, ValueError):
        return 1000


def _pagination_multiplier(field: FieldNode) -> int:
    """The list multiplier for a field.

    Returns the field's explicit page-size argument value (e.g. ``limit: 50`` -> 50); 1 when the
    field has no pagination argument (ordinary nesting is not penalized -- the server caps unbounded
    lists at its own default page size); or DEFAULT_LIST_MULTIPLIER when a page size is given but not
    a literal int (e.g. a variable, whose value is unknown at validation time).
    """
    has_pagination_arg = False
    for argument in field.arguments or ():
        if argument.name.value in PAGINATION_ARGS:
            has_pagination_arg = True
            if isinstance(argument.value, IntValueNode):
                try:
                    value = int(argument.value.value)
                except (TypeError, ValueError):
                    continue
                if value > 0:
                    return value
    return DEFAULT_LIST_MULTIPLIER if has_pagination_arg else 1


def _selection_cost(selection_set, fragments, multiplier, seen_fragments):
    """Recursively sum the cost of a selection set, multiplying list subtrees by their page size."""
    if selection_set is None:
        return 0
    cost = 0
    for selection in selection_set.selections:
        if isinstance(selection, FieldNode):
            cost += multiplier
            if selection.selection_set is not None:
                child_multiplier = multiplier * _pagination_multiplier(selection)
                cost += _selection_cost(
                    selection.selection_set, fragments, child_multiplier, seen_fragments
                )
        elif isinstance(selection, InlineFragmentNode):
            cost += _selection_cost(selection.selection_set, fragments, multiplier, seen_fragments)
        elif isinstance(selection, FragmentSpreadNode):
            name = selection.name.value
            if name in seen_fragments:
                continue  # guard against fragment cycles
            fragment = fragments.get(name)
            if fragment is not None:
                cost += _selection_cost(
                    fragment.selection_set, fragments, multiplier, seen_fragments | {name}
                )
    return cost


def estimate_query_cost(document) -> int:
    """Estimate the total cost of a GraphQL document (an AST or a query string)."""
    if isinstance(document, str):
        from graphql import parse

        document = parse(document)
    fragments = {
        definition.name.value: definition
        for definition in document.definitions
        if isinstance(definition, FragmentDefinitionNode)
    }
    total = 0
    for definition in document.definitions:
        if isinstance(definition, OperationDefinitionNode):
            total += _selection_cost(definition.selection_set, fragments, 1, frozenset())
    return total


class QueryCostLimiter(ValidationRule):
    """Reject operations whose estimated cost exceeds QUERY_COST_LIMIT (graphql-core rule)."""

    def __init__(self, context):
        super().__init__(context)
        self.max_cost = get_max_query_cost()
        self._fragments = {
            definition.name.value: definition
            for definition in context.document.definitions
            if isinstance(definition, FragmentDefinitionNode)
        }

    def enter_operation_definition(self, node, *_args):
        cost = _selection_cost(node.selection_set, self._fragments, 1, frozenset())
        if cost > self.max_cost:
            self.report_error(
                GraphQLError(
                    f"Query is too complex: cost {cost} exceeds the maximum allowed "
                    f"({self.max_cost}). Request fewer fields or smaller page sizes.",
                    node,
                )
            )
