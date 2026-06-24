from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class UserBooks(Base):
    __tablename__ = "user_books"
    __table_args__ = (UniqueConstraint('user_id', 'book_id'),)

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    status = Column(Text, default='want_to_read', nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    rating = Column(SmallInteger)
    review = Column(Text)
    started_at = Column(TIMESTAMP(timezone=True))
    finished_at = Column(TIMESTAMP(timezone=True))
    added_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="user_books")
    users = relationship("Users", back_populates="user_books")
    user_book_tags = relationship("UserBookTags", back_populates="user_books")
# ============================================================================
# UserBooks Configuration
# ============================================================================

# Fields that can be queried/filtered by users
USER_BOOKS_QUERYABLE_FIELDS = {
    'added_at',
    'book_id',
    'finished_at',
    'id',
    'is_favorite',
    'rating',
    'review',
    'started_at',
    'status',
    'updated_at',
}

# Fields that can be sorted by users
USER_BOOKS_ORDERABLE_FIELDS = {
    'added_at',
    'book_id',
    'finished_at',
    'id',
    'is_favorite',
    'rating',
    'started_at',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
USER_BOOKS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
USER_BOOKS_LOADABLE_RELATIONSHIPS = {
    'books',
    'users',
}

# Input validation - map field names to Python types
USER_BOOKS_INPUT_VALIDATION = {
    'added_at': 'datetime',
    'book_id': 'str',
    'finished_at': 'datetime',
    'is_favorite': 'bool',
    'rating': 'int',
    'review': 'str',
    'started_at': 'datetime',
    'status': 'str',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
USER_BOOKS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
USER_BOOKS_UNIQUE_FIELDS = {
}
