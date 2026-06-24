from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Genres(Base):
    __tablename__ = "genres"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(Text, unique=True, nullable=False)
    slug = Column(Text, unique=True, nullable=False)

    book_genres = relationship("BookGenres", back_populates="genres")
# ============================================================================
# Genres Configuration
# ============================================================================

# Fields that can be queried/filtered by users
GENRES_QUERYABLE_FIELDS = {
    'id',
    'name',
    'slug',
}

# Fields that can be sorted by users
GENRES_ORDERABLE_FIELDS = {
    'id',
}

# Fields to exclude from API responses (sensitive/internal)
GENRES_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
GENRES_LOADABLE_RELATIONSHIPS = {
}

# Input validation - map field names to Python types
GENRES_INPUT_VALIDATION = {
    'name': 'str',
    'slug': 'str',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
GENRES_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
GENRES_UNIQUE_FIELDS = {
    'name',
    'slug',
}
