from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class CollectionBooks(Base):
    __tablename__ = "collection_books"

    collection_id = Column(String, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    added_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="collection_books")
    collections = relationship("Collections", back_populates="collection_books")
# ============================================================================
# CollectionBooks Configuration
# ============================================================================

# Fields that can be queried/filtered by users
COLLECTION_BOOKS_QUERYABLE_FIELDS = {
    'added_at',
    'book_id',
    'collection_id',
}

# Fields that can be sorted by users
COLLECTION_BOOKS_ORDERABLE_FIELDS = {
    'added_at',
    'book_id',
    'collection_id',
}

# Fields to exclude from API responses (sensitive/internal)
COLLECTION_BOOKS_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
COLLECTION_BOOKS_LOADABLE_RELATIONSHIPS = {
    'books',
    'collections',
}

# Input validation - map field names to Python types
COLLECTION_BOOKS_INPUT_VALIDATION = {
    'added_at': 'datetime',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
COLLECTION_BOOKS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
COLLECTION_BOOKS_UNIQUE_FIELDS = {
}
