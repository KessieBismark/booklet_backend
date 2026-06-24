from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Chapters(Base):
    __tablename__ = "chapters"
    __table_args__ = (UniqueConstraint('book_id', 'order_index'),)

    id = Column(String, primary_key=True, nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False)
    title = Column(Text)
    content = Column(Text, nullable=False)
    content_format = Column(Text, default='markdown')
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="chapters")
    reading_progress = relationship("ReadingProgress", back_populates="chapters")
    highlights = relationship("Highlights", back_populates="chapters")
    bookmarks = relationship("Bookmarks", back_populates="chapters")
    quotes = relationship("Quotes", back_populates="chapters")
    notes = relationship("Notes", back_populates="chapters")
# ============================================================================
# Chapters Configuration
# ============================================================================

# Fields that can be queried/filtered by users
CHAPTERS_QUERYABLE_FIELDS = {
    'book_id',
    'char_count',
    'content',
    'content_format',
    'created_at',
    'id',
    'order_index',
    'title',
    'updated_at',
    'word_count',
}

# Fields that can be sorted by users
CHAPTERS_ORDERABLE_FIELDS = {
    'book_id',
    'char_count',
    'created_at',
    'id',
    'order_index',
    'updated_at',
    'word_count',
}

# Fields to exclude from API responses (sensitive/internal)
CHAPTERS_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
CHAPTERS_LOADABLE_RELATIONSHIPS = {
    'books',
}

# Input validation - map field names to Python types
CHAPTERS_INPUT_VALIDATION = {
    'book_id': 'str',
    'char_count': 'int',
    'content': 'str',
    'content_format': 'str',
    'created_at': 'datetime',
    'order_index': 'int',
    'title': 'str',
    'updated_at': 'datetime',
    'word_count': 'int',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
CHAPTERS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
CHAPTERS_UNIQUE_FIELDS = {
}
