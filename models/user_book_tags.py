from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class UserBookTags(Base):
    __tablename__ = "user_book_tags"

    user_book_id = Column(String, ForeignKey("user_books.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tag_id = Column(String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    tags = relationship("Tags", back_populates="user_book_tags")
    user_books = relationship("UserBooks", back_populates="user_book_tags")
# ============================================================================
# UserBookTags Configuration
# ============================================================================

# Fields that can be queried/filtered by users
USER_BOOK_TAGS_QUERYABLE_FIELDS = {
    'tag_id',
    'user_book_id',
}

# Fields that can be sorted by users
USER_BOOK_TAGS_ORDERABLE_FIELDS = {
    'tag_id',
    'user_book_id',
}

# Fields to exclude from API responses (sensitive/internal)
USER_BOOK_TAGS_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
USER_BOOK_TAGS_LOADABLE_RELATIONSHIPS = {
    'tags',
    'user_books',
}

# Input validation - map field names to Python types
USER_BOOK_TAGS_INPUT_VALIDATION = {
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
USER_BOOK_TAGS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
USER_BOOK_TAGS_UNIQUE_FIELDS = {
}
