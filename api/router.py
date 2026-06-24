"""Aggregated API router — includes every table's routes (generated)."""
from fastapi import APIRouter

api_router = APIRouter()

from api.routes import users_routes
api_router.include_router(users_routes.router)
from api.routes import devices_routes
api_router.include_router(devices_routes.router)
from api.routes import books_routes
api_router.include_router(books_routes.router)
from api.routes import book_authors_routes
api_router.include_router(book_authors_routes.router)
from api.routes import authors_routes
api_router.include_router(authors_routes.router)
from api.routes import book_genres_routes
api_router.include_router(book_genres_routes.router)
from api.routes import genres_routes
api_router.include_router(genres_routes.router)
from api.routes import chapters_routes
api_router.include_router(chapters_routes.router)
from api.routes import user_books_routes
api_router.include_router(user_books_routes.router)
from api.routes import collections_routes
api_router.include_router(collections_routes.router)
from api.routes import collection_books_routes
api_router.include_router(collection_books_routes.router)
from api.routes import tags_routes
api_router.include_router(tags_routes.router)
from api.routes import user_book_tags_routes
api_router.include_router(user_book_tags_routes.router)
from api.routes import reading_progress_routes
api_router.include_router(reading_progress_routes.router)
from api.routes import reading_sessions_routes
api_router.include_router(reading_sessions_routes.router)
from api.routes import highlights_routes
api_router.include_router(highlights_routes.router)
from api.routes import bookmarks_routes
api_router.include_router(bookmarks_routes.router)
from api.routes import quotes_routes
api_router.include_router(quotes_routes.router)
from api.routes import notes_routes
api_router.include_router(notes_routes.router)
from api.routes import reading_goals_routes
api_router.include_router(reading_goals_routes.router)
