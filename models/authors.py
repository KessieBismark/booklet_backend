from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Authors(Base):
    __tablename__ = "authors"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    bio = Column(Text)
    photo_url = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    book_authors = relationship("BookAuthors", back_populates="authors")
# ============================================================================
# Authors Configuration
# ============================================================================

# Fields that can be queried/filtered by users
AUTHORS_QUERYABLE_FIELDS = {
    'bio',
    'created_at',
    'id',
    'name',
    'photo_url',
    'updated_at',
}

# Fields that can be sorted by users
AUTHORS_ORDERABLE_FIELDS = {
    'created_at',
    'id',
    'updated_at',
}

# Fields to exclude from API responses (sensitive/internal)
AUTHORS_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
AUTHORS_LOADABLE_RELATIONSHIPS = {
}

# Input validation - map field names to Python types
AUTHORS_INPUT_VALIDATION = {
    'bio': 'str',
    'created_at': 'datetime',
    'name': 'str',
    'photo_url': 'str',
    'updated_at': 'datetime',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
AUTHORS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
AUTHORS_UNIQUE_FIELDS = {
}
