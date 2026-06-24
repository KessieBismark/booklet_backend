
# enums.py
import strawberry
from enum import Enum

@strawberry.enum
class LogicalOperator(Enum):
    AND = "AND"
    OR = "OR"
    
@strawberry.enum
class OrderByOperator(Enum):
    ID_ASC = 'id:asc'
    ID_DESC = 'id:desc'
    CREATED_AT_ASC = 'created_at:asc'
    CREATED_AT_DESC = 'created_at:desc'

