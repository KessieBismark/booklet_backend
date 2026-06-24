from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class BookGenres(Base):
    __tablename__ = "book_genres"

    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    genre_id = Column(String, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    books = relationship("Books", back_populates="book_genres")
    genres = relationship("Genres", back_populates="book_genres")
# ============================================================================
# BookGenres Configuration
# ============================================================================

# Fields that can be queried/filtered by users
BOOK_GENRES_QUERYABLE_FIELDS = {
    'book_id',
    'genre_id',
}

# Fields that can be sorted by users
BOOK_GENRES_ORDERABLE_FIELDS = {
    'book_id',
    'genre_id',
}

# Fields to exclude from API responses (sensitive/internal)
BOOK_GENRES_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
BOOK_GENRES_LOADABLE_RELATIONSHIPS = {
    'books',
    'genres',
}

# Input validation - map field names to Python types
BOOK_GENRES_INPUT_VALIDATION = {
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
BOOK_GENRES_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
BOOK_GENRES_UNIQUE_FIELDS = {
}
