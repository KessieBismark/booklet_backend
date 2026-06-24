from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class ReadingSessions(Base):
    __tablename__ = "reading_sessions"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(String, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String, ForeignKey("devices.id", ondelete="SET NULL"))
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(TIMESTAMP(timezone=True))
    duration_seconds = Column(Integer)
    words_read = Column(Integer)
    start_percent = Column(String)
    end_percent = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    books = relationship("Books", back_populates="reading_sessions")
    devices = relationship("Devices", back_populates="reading_sessions")
    users = relationship("Users", back_populates="reading_sessions")
# ============================================================================
# ReadingSessions Configuration
# ============================================================================

# Fields that can be queried/filtered by users
READING_SESSIONS_QUERYABLE_FIELDS = {
    'book_id',
    'created_at',
    'device_id',
    'duration_seconds',
    'end_percent',
    'ended_at',
    'id',
    'start_percent',
    'started_at',
    'words_read',
}

# Fields that can be sorted by users
READING_SESSIONS_ORDERABLE_FIELDS = {
    'book_id',
    'created_at',
    'device_id',
    'duration_seconds',
    'end_percent',
    'ended_at',
    'id',
    'start_percent',
    'started_at',
    'user_id',
    'words_read',
}

# Fields to exclude from API responses (sensitive/internal)
READING_SESSIONS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
READING_SESSIONS_LOADABLE_RELATIONSHIPS = {
    'books',
    'devices',
    'users',
}

# Input validation - map field names to Python types
READING_SESSIONS_INPUT_VALIDATION = {
    'book_id': 'str',
    'created_at': 'datetime',
    'device_id': 'str',
    'duration_seconds': 'int',
    'end_percent': 'str',
    'ended_at': 'datetime',
    'start_percent': 'str',
    'started_at': 'datetime',
    'user_id': 'str',
    'words_read': 'int',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
READING_SESSIONS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
READING_SESSIONS_UNIQUE_FIELDS = {
}
