from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class ReadingGoals(Base):
    __tablename__ = "reading_goals"

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    period = Column(Text, nullable=False)
    metric = Column(Text, nullable=False)
    target_value = Column(Integer, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    users = relationship("Users", back_populates="reading_goals")
# ============================================================================
# ReadingGoals Configuration
# ============================================================================

# Fields that can be queried/filtered by users
READING_GOALS_QUERYABLE_FIELDS = {
    'created_at',
    'id',
    'metric',
    'period',
    'period_end',
    'period_start',
    'target_value',
    'updated_at',
}

# Fields that can be sorted by users
READING_GOALS_ORDERABLE_FIELDS = {
    'created_at',
    'id',
    'period_end',
    'period_start',
    'target_value',
    'updated_at',
    'user_id',
}

# Fields to exclude from API responses (sensitive/internal)
READING_GOALS_EXCLUDED_FIELDS = {
    'user_id',
}

# Foreign key relationships for eager loading
READING_GOALS_LOADABLE_RELATIONSHIPS = {
    'users',
}

# Input validation - map field names to Python types
READING_GOALS_INPUT_VALIDATION = {
    'created_at': 'datetime',
    'metric': 'str',
    'period': 'str',
    'period_end': 'date',
    'period_start': 'date',
    'target_value': 'int',
    'updated_at': 'datetime',
    'user_id': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
READING_GOALS_AUTO_VALIDATE_FIELDS = {
    'user_id',
}

# Fields with unique constraints
READING_GOALS_UNIQUE_FIELDS = {
}
