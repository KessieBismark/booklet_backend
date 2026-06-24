from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Collections(Base):
    __tablename__ = "collections"
    __table_args__ = (UniqueConstraint('user_id', 'name'),)

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    color = Column(Text)
    icon = Column(Text)
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("Users", back_populates="collections")
    collection_books = relationship("CollectionBooks", back_populates="collections")
# ============================================================================
# Collections Configuration
# ============================================================================

# Fields that can be queried/filtered by users
COLLECTIONS_QUERYABLE_FIELDS = {
    'color',
    'created_at',
    'description',
    'icon',
    'id',
    'name',
    'sort_order',
    'updated_at',
}

# Fields that can be sorted by users
COLLECTIONS_ORDERABLE_FIELDS = {
    'created_at',
    'id',
    'sort_order',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
COLLECTIONS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
COLLECTIONS_LOADABLE_RELATIONSHIPS = {
    'users',
}

# Input validation - map field names to Python types
COLLECTIONS_INPUT_VALIDATION = {
    'color': 'str',
    'created_at': 'datetime',
    'description': 'str',
    'icon': 'str',
    'name': 'str',
    'sort_order': 'int',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
COLLECTIONS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
COLLECTIONS_UNIQUE_FIELDS = {
}
