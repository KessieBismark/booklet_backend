from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class ReadingProgress(Base):
    __tablename__ = "reading_progress"
    __table_args__ = (UniqueConstraint('user_id', 'book_id'),)

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(String, ForeignKey("chapters.id", ondelete="SET NULL"))
    char_offset = Column(Integer, default=0, nullable=False)
    progress_percent = Column(String, default=0, nullable=False)
    last_device_id = Column(String, ForeignKey("devices.id", ondelete="SET NULL"))
    last_read_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="reading_progress")
    chapters = relationship("Chapters", back_populates="reading_progress")
    devices = relationship("Devices", back_populates="reading_progress")
    users = relationship("Users", back_populates="reading_progress")
# ============================================================================
# ReadingProgress Configuration
# ============================================================================

# Fields that can be queried/filtered by users
READING_PROGRESS_QUERYABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'char_offset',
    'id',
    'last_device_id',
    'last_read_at',
    'progress_percent',
    'updated_at',
}

# Fields that can be sorted by users
READING_PROGRESS_ORDERABLE_FIELDS = {
    'book_id',
    'chapter_id',
    'char_offset',
    'id',
    'last_device_id',
    'last_read_at',
    'progress_percent',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
READING_PROGRESS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
READING_PROGRESS_LOADABLE_RELATIONSHIPS = {
    'books',
    'chapters',
    'devices',
    'users',
}

# Input validation - map field names to Python types
READING_PROGRESS_INPUT_VALIDATION = {
    'book_id': 'str',
    'chapter_id': 'str',
    'char_offset': 'int',
    'last_device_id': 'str',
    'last_read_at': 'datetime',
    'progress_percent': 'str',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
READING_PROGRESS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
READING_PROGRESS_UNIQUE_FIELDS = {
}
