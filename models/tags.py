from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Tags(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint('user_id', 'name'),)

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)

    users = relationship("Users", back_populates="tags")
    user_book_tags = relationship("UserBookTags", back_populates="tags")
# ============================================================================
# Tags Configuration
# ============================================================================

# Fields that can be queried/filtered by users
TAGS_QUERYABLE_FIELDS = {
    'id',
    'name',
}

# Fields that can be sorted by users
TAGS_ORDERABLE_FIELDS = {
    'id',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
TAGS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
TAGS_LOADABLE_RELATIONSHIPS = {
    'users',
}

# Input validation - map field names to Python types
TAGS_INPUT_VALIDATION = {
    'name': 'str',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
TAGS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
TAGS_UNIQUE_FIELDS = {
}
