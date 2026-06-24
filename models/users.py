from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    display_name = Column(Text)
    avatar_url = Column(Text)
    locale = Column(Text, default='en')
    theme = Column(Text, default='system')
    font_scale = Column(String, default=1)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_active_at = Column(TIMESTAMP(timezone=True))

    devices = relationship("Devices", back_populates="users")
    user_books = relationship("UserBooks", back_populates="users")
    collections = relationship("Collections", back_populates="users")
    tags = relationship("Tags", back_populates="users")
    reading_progress = relationship("ReadingProgress", back_populates="users")
    reading_sessions = relationship("ReadingSessions", back_populates="users")
    highlights = relationship("Highlights", back_populates="users")
    bookmarks = relationship("Bookmarks", back_populates="users")
    quotes = relationship("Quotes", back_populates="users")
    notes = relationship("Notes", back_populates="users")
    reading_goals = relationship("ReadingGoals", back_populates="users")
# ============================================================================
# Users Configuration
# ============================================================================

# Fields that can be queried/filtered by users
USERS_QUERYABLE_FIELDS = {
    'avatar_url',
    'created_at',
    'display_name',
    'email',
    'font_scale',
    'id',
    'last_active_at',
    'locale',
    'theme',
    'updated_at',
}

# Fields that can be sorted by users
USERS_ORDERABLE_FIELDS = {
    'created_at',
    'font_scale',
    'id',
    'last_active_at',
    'updated_at',
}

# Fields to exclude from API responses (sensitive/internal)
USERS_EXCLUDED_FIELDS = {
    'password_hash',
}

# Foreign key relationships for eager loading
USERS_LOADABLE_RELATIONSHIPS = {
}

# Input validation - map field names to Python types
USERS_INPUT_VALIDATION = {
    'avatar_url': 'str',
    'created_at': 'datetime',
    'display_name': 'str',
    'email': 'str',
    'font_scale': 'str',
    'last_active_at': 'datetime',
    'locale': 'str',
    'password_hash': 'str',
    'theme': 'str',
    'updated_at': 'datetime',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
USERS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
USERS_UNIQUE_FIELDS = {
    'email',
}
