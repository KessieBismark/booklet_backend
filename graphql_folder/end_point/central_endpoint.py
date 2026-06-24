
import os
import strawberry
from strawberry.extensions import QueryDepthLimiter, AddValidationRules
from graphql_folder.query_cost import QueryCostLimiter
from .mutation_endpoint import GeneralMutation
from .query_endpoint import GeneralQuery


# GraphQL hardening (OPS008):
#  - QueryDepthLimiter rejects deeply-nested queries (query-depth DoS). Tune max_depth.
#  - QueryCostLimiter rejects wide/expensive queries by estimated cost (tune via QUERY_COST_LIMIT);
#    depth caps nesting, cost caps total work, so a shallow-but-huge query is also rejected.
#  - Schema introspection is disabled in production so the full schema is not exposed to attackers
#    (introspection stays on in non-production for tooling/explorers).
_schema_extensions = [
    QueryDepthLimiter(max_depth=10),
    AddValidationRules([QueryCostLimiter]),
]
if os.getenv("ENVIRONMENT", "development").lower() == "production":
    from graphql import NoSchemaIntrospectionCustomRule
    _schema_extensions.append(AddValidationRules([NoSchemaIntrospectionCustomRule]))

mainEndpoint = strawberry.Schema(
    mutation=GeneralMutation,
    query=GeneralQuery,
    extensions=_schema_extensions,
)


    