from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Bookmarks(Base):
    __tablename__ = "bookmarks"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    char_offset = Column(Integer, default=0, nullable=False)
    label = Column(Text)
    preview_text = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="bookmarks")
    chapters = relationship("Chapters", back_populates="bookmarks")
    users = relationship("Users", back_populates="bookmarks")
# ============================================================================
# Bookmarks Configuration
# ============================================================================

# Fields that can be queried/filtered by users
BOOKMARKS_QUERYABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'char_offset',
    'created_at',
    'id',
    'label',
    'preview_text',
    'updated_at',
}

# Fields that can be sorted by users
BOOKMARKS_ORDERABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'char_offset',
    'created_at',
    'id',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
BOOKMARKS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
BOOKMARKS_LOADABLE_RELATIONSHIPS = {
    'books',
    'chapters',
    'users',
}

# Input validation - map field names to Python types
BOOKMARKS_INPUT_VALIDATION = {
    'book_id': 'str',
    'chapter_id': 'str',
    'char_offset': 'int',
    'created_at': 'datetime',
    'label': 'str',
    'preview_text': 'str',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
BOOKMARKS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
BOOKMARKS_UNIQUE_FIELDS = {
}
