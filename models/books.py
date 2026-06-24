from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, TIMESTAMP, ForeignKey, func, text, BigInteger, SmallInteger, Date, Time, ARRAY, Numeric, Float
from sqlalchemy.orm import relationship
from config.dbconfig import Base

class Books(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, nullable=False)
    title = Column(Text, nullable=False)
    subtitle = Column(Text)
    description = Column(Text)
    isbn = Column(Text, unique=True)
    language = Column(Text, default='en')
    publisher = Column(Text)
    published_on = Column(Date)
    cover_image_url = Column(Text)
    word_count = Column(Integer, default=0)
    chapter_count = Column(Integer, default=0)
    est_reading_minutes = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    book_authors = relationship("BookAuthors", back_populates="books")
    book_genres = relationship("BookGenres", back_populates="books")
    chapters = relationship("Chapters", back_populates="books")
    user_books = relationship("UserBooks", back_populates="books")
    collection_books = relationship("CollectionBooks", back_populates="books")
    reading_progress = relationship("ReadingProgress", back_populates="books")
    reading_sessions = relationship("ReadingSessions", back_populates="books")
    highlights = relationship("Highlights", back_populates="books")
    bookmarks = relationship("Bookmarks", back_populates="books")
    quotes = relationship("Quotes", back_populates="books")
    notes = relationship("Notes", back_populates="books")
# ============================================================================
# Books Configuration
# ============================================================================

# Fields that can be queried/filtered by users
BOOKS_QUERYABLE_FIELDS = {
    'chapter_count',
    'cover_image_url',
    'created_at',
    'description',
    'est_reading_minutes',
    'id',
    'isbn',
    'language',
    'published_on',
    'publisher',
    'subtitle',
    'title',
    'updated_at',
    'word_count',
}

# Fields that can be sorted by users
BOOKS_ORDERABLE_FIELDS = {
    'chapter_count',
    'created_at',
    'est_reading_minutes',
    'id',
    'published_on',
    'updated_at',
    'word_count',
}

# Fields to exclude from API responses (sensitive/internal)
BOOKS_EXCLUDED_FIELDS = {
}

# Foreign key relationships for eager loading
BOOKS_LOADABLE_RELATIONSHIPS = {
}

# Input validation - map field names to Python types
BOOKS_INPUT_VALIDATION = {
    'chapter_count': 'int',
    'cover_image_url': 'str',
    'created_at': 'datetime',
    'description': 'str',
    'est_reading_minutes': 'int',
    'isbn': 'str',
    'language': 'str',
    'published_on': 'date',
    'publisher': 'str',
    'subtitle': 'str',
    'title': 'str',
    'updated_at': 'datetime',
    'word_count': 'int',
}

# Fields that must match current user for authorization
# These are automatically checked before mutations
BOOKS_AUTO_VALIDATE_FIELDS = {
}

# Fields with unique constraints
BOOKS_UNIQUE_FIELDS = {
    'isbn',
}
