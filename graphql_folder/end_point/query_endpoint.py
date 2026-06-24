
import strawberry
from graphql_folder.queries.users import UsersQuery
from graphql_folder.queries.devices import DevicesQuery
from graphql_folder.queries.books import BooksQuery
from graphql_folder.queries.book_authors import BookAuthorsQuery
from graphql_folder.queries.authors import AuthorsQuery
from graphql_folder.queries.book_genres import BookGenresQuery
from graphql_folder.queries.genres import GenresQuery
from graphql_folder.queries.chapters import ChaptersQuery
from graphql_folder.queries.user_books import UserBooksQuery
from graphql_folder.queries.collections import CollectionsQuery
from graphql_folder.queries.collection_books import CollectionBooksQuery
from graphql_folder.queries.tags import TagsQuery
from graphql_folder.queries.user_book_tags import UserBookTagsQuery
from graphql_folder.queries.reading_progress import ReadingProgressQuery
from graphql_folder.queries.reading_sessions import ReadingSessionsQuery
from graphql_folder.queries.highlights import HighlightsQuery
from graphql_folder.queries.bookmarks import BookmarksQuery
from graphql_folder.queries.quotes import QuotesQuery
from graphql_folder.queries.notes import NotesQuery
from graphql_folder.queries.reading_goals import ReadingGoalsQuery


@strawberry.type
class GeneralQuery(
    UsersQuery,
    DevicesQuery,
    BooksQuery,
    BookAuthorsQuery,
    AuthorsQuery,
    BookGenresQuery,
    GenresQuery,
    ChaptersQuery,
    UserBooksQuery,
    CollectionsQuery,
    CollectionBooksQuery,
    TagsQuery,
    UserBookTagsQuery,
    ReadingProgressQuery,
    ReadingSessionsQuery,
    HighlightsQuery,
    BookmarksQuery,
    QuotesQuery,
    NotesQuery,
    ReadingGoalsQuery
    ):
    pass
    
    
    