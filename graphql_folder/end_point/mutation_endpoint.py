
import strawberry
from graphql_folder.mutations.users import UsersMutation
from graphql_folder.mutations.devices import DevicesMutation
from graphql_folder.mutations.books import BooksMutation
from graphql_folder.mutations.book_authors import BookAuthorsMutation
from graphql_folder.mutations.authors import AuthorsMutation
from graphql_folder.mutations.book_genres import BookGenresMutation
from graphql_folder.mutations.genres import GenresMutation
from graphql_folder.mutations.chapters import ChaptersMutation
from graphql_folder.mutations.user_books import UserBooksMutation
from graphql_folder.mutations.collections import CollectionsMutation
from graphql_folder.mutations.collection_books import CollectionBooksMutation
from graphql_folder.mutations.tags import TagsMutation
from graphql_folder.mutations.user_book_tags import UserBookTagsMutation
from graphql_folder.mutations.reading_progress import ReadingProgressMutation
from graphql_folder.mutations.reading_sessions import ReadingSessionsMutation
from graphql_folder.mutations.highlights import HighlightsMutation
from graphql_folder.mutations.bookmarks import BookmarksMutation
from graphql_folder.mutations.quotes import QuotesMutation
from graphql_folder.mutations.notes import NotesMutation
from graphql_folder.mutations.reading_goals import ReadingGoalsMutation


@strawberry.type
class GeneralMutation(
    UsersMutation,
    DevicesMutation,
    BooksMutation,
    BookAuthorsMutation,
    AuthorsMutation,
    BookGenresMutation,
    GenresMutation,
    ChaptersMutation,
    UserBooksMutation,
    CollectionsMutation,
    CollectionBooksMutation,
    TagsMutation,
    UserBookTagsMutation,
    ReadingProgressMutation,
    ReadingSessionsMutation,
    HighlightsMutation,
    BookmarksMutation,
    QuotesMutation,
    NotesMutation,
    ReadingGoalsMutation
    ):
    pass
    
    
    
    