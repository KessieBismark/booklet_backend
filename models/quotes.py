from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Quotes(Base):
    __tablename__ = "quotes"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.id", ondelete="SET NULL"))
    highlight_id = Column(String, ForeignKey("highlights.id", ondelete="SET NULL"))
    quote_text = Column(Text, nullable=False)
    note = Column(Text)
    location_label = Column(Text)
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="quotes")
    chapters = relationship("Chapters", back_populates="quotes")
    highlights = relationship("Highlights", back_populates="quotes")
    users = relationship("Users", back_populates="quotes")
# ============================================================================
# Quotes Configuration
# ============================================================================

# Fields that can be queried/filtered by users
QUOTES_QUERYABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'created_at',
    'highlight_id',
    'id',
    'is_favorite',
    'is_public',
    'location_label',
    'note',
    'quote_text',
    'updated_at',
}

# Fields that can be sorted by users
QUOTES_ORDERABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'created_at',
    'highlight_id',
    'id',
    'is_favorite',
    'is_public',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
QUOTES_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
QUOTES_LOADABLE_RELATIONSHIPS = {
    'books',
    'chapters',
    'highlights',
    'users',
}

# Input validation - map field names to Python types
QUOTES_INPUT_VALIDATION = {
    'book_id': 'str',
    'chapter_id': 'str',
    'created_at': 'datetime',
    'highlight_id': 'str',
    'is_favorite': 'bool',
    'is_public': 'bool',
    'location_label': 'str',
    'note': 'str',
    'quote_text': 'str',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
QUOTES_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
QUOTES_UNIQUE_FIELDS = {
}
