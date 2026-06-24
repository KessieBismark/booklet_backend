from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Notes(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.id", ondelete="SET NULL"))
    char_offset = Column(Integer)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="notes")
    chapters = relationship("Chapters", back_populates="notes")
    users = relationship("Users", back_populates="notes")
# ============================================================================
# Notes Configuration
# ============================================================================

# Fields that can be queried/filtered by users
NOTES_QUERYABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'char_offset',
    'content',
    'created_at',
    'id',
    'updated_at',
}

# Fields that can be sorted by users
NOTES_ORDERABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'char_offset',
    'created_at',
    'id',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
NOTES_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
NOTES_LOADABLE_RELATIONSHIPS = {
    'books',
    'chapters',
    'users',
}

# Input validation - map field names to Python types
NOTES_INPUT_VALIDATION = {
    'book_id': 'str',
    'chapter_id': 'str',
    'char_offset': 'int',
    'content': 'str',
    'created_at': 'datetime',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
NOTES_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
NOTES_UNIQUE_FIELDS = {
}
