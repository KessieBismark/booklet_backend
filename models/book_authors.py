from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class BookAuthors(Base):
    __tablename__ = "book_authors"

    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    author_id = Column(String, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    author_role = Column(Text, primary_key=True, default='author', nullable=False)

    authors = relationship("Authors", back_populates="book_authors")
    books = relationship("Books", back_populates="book_authors")
# ============================================================================
# BookAuthors Configuration
# ============================================================================

# Fields that can be queried/filtered by users
BOOK_AUTHORS_QUERYABLE_FIELDS = {
    'author_id',
    'author_role',
    'book_id',
}

# Fields that can be sorted by users
BOOK_AUTHORS_ORDERABLE_FIELDS = {
    'author_id',
    'book_id',
}

# Fields to exclude from API responses (sensitive/internal)
BOOK_AUTHORS_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
BOOK_AUTHORS_LOADABLE_RELATIONSHIPS = {
    'authors',
    'books',
}

# Input validation - map field names to Python types
BOOK_AUTHORS_INPUT_VALIDATION = {
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
BOOK_AUTHORS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
BOOK_AUTHORS_UNIQUE_FIELDS = {
}
