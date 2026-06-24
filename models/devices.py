from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Devices(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text)
    platform = Column(Text)
    push_token = Column(Text)
    last_synced_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("Users", back_populates="devices")
    reading_progress = relationship("ReadingProgress", back_populates="devices")
    reading_sessions = relationship("ReadingSessions", back_populates="devices")
# ============================================================================
# Devices Configuration
# ============================================================================

# Fields that can be queried/filtered by users
DEVICES_QUERYABLE_FIELDS = {
    'created_at',
    'id',
    'last_synced_at',
    'name',
    'platform',
    'updated_at',
}

# Fields that can be sorted by users
DEVICES_ORDERABLE_FIELDS = {
    'created_at',
    'id',
    'last_synced_at',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
DEVICES_EXCLUDED_FIELDS = {
    'push_token',
    'user_id',
}

# Foreign key relationships for eager loading
DEVICES_LOADABLE_RELATIONSHIPS = {
    'users',
}

# Input validation - map field names to Python types
DEVICES_INPUT_VALIDATION = {
    'created_at': 'datetime',
    'last_synced_at': 'datetime',
    'name': 'str',
    'platform': 'str',
    'push_token': 'str',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
DEVICES_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
DEVICES_UNIQUE_FIELDS = {
}
