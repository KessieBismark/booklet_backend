from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Highlights(Base):
    __tablename__ = "highlights"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    start_offset = Column(Integer, nullable=False)
    end_offset = Column(Integer, nullable=False)
    selected_text = Column(Text, nullable=False)
    color = Column(Text, default='yellow', nullable=False)
    note = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="highlights")
    chapters = relationship("Chapters", back_populates="highlights")
    users = relationship("Users", back_populates="highlights")
    quotes = relationship("Quotes", back_populates="highlights")
# ============================================================================
# Highlights Configuration
# ============================================================================

# Fields that can be queried/filtered by users
HIGHLIGHTS_QUERYABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'color',
    'created_at',
    'end_offset',
    'id',
    'note',
    'selected_text',
    'start_offset',
    'updated_at',
}

# Fields that can be sorted by users
HIGHLIGHTS_ORDERABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'created_at',
    'end_offset',
    'id',
    'start_offset',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
HIGHLIGHTS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
HIGHLIGHTS_LOADABLE_RELATIONSHIPS = {
    'books',
    'chapters',
    'users',
}

# Input validation - map field names to Python types
HIGHLIGHTS_INPUT_VALIDATION = {
    'book_id': 'str',
    'chapter_id': 'str',
    'color': 'str',
    'created_at': 'datetime',
    'end_offset': 'int',
    'note': 'str',
    'selected_text': 'str',
    'start_offset': 'int',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
HIGHLIGHTS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
HIGHLIGHTS_UNIQUE_FIELDS = {
}
