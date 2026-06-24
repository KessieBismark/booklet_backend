# booklet — API Reference

Auto-generated for this project (Both, Asynchronous). Every section below is tailored to the actual models and endpoints that were generated.

## Contents

- [Conventions](#conventions)
- [Authentication](#authentication)
- [Filtering, search, sorting & pagination](#filtering-search-sorting--pagination)
- [Models](#models)
  - [`users`](#users)
  - [`devices`](#devices)
  - [`books`](#books)
  - [`book_authors`](#book_authors)
  - [`authors`](#authors)
  - [`book_genres`](#book_genres)
  - [`genres`](#genres)
  - [`chapters`](#chapters)
  - [`user_books`](#user_books)
  - [`collections`](#collections)
  - [`collection_books`](#collection_books)
  - [`tags`](#tags)
  - [`user_book_tags`](#user_book_tags)
  - [`reading_progress`](#reading_progress)
  - [`reading_sessions`](#reading_sessions)
  - [`highlights`](#highlights)
  - [`bookmarks`](#bookmarks)
  - [`quotes`](#quotes)
  - [`notes`](#notes)
  - [`reading_goals`](#reading_goals)

## Conventions

- **REST base path:** `/api` — each model is mounted at `/api/<model>/`.
- **GraphQL endpoint:** `/graphql` (GraphiQL playground in the browser).
- **Interactive docs:** Swagger at `/docs`, ReDoc at `/redoc`, this portal at `/portal`.
- **Content type:** `application/json`.

## Authentication

All data endpoints require a **JWT bearer token**:

```http
Authorization: Bearer <your-token>
```

For GraphQL, send the same header; unauthenticated requests get a guest context.

## Filtering, search, sorting & pagination

Every model's **list** endpoint/query supports the same controls. The exact fields you can filter and sort by are listed per model below (they exclude sensitive and complex columns automatically).

### Filter operators

| Operator | Meaning |
| --- | --- |
| `eq` | equals |
| `ne` | not equal |
| `lt` | less than |
| `lte` | less than or equal |
| `gt` | greater than |
| `gte` | greater than or equal |
| `contains` | case-insensitive substring match |
| `in` | value in a list |
| `is_null` | is / is not NULL |

### REST list parameters

| Query param | Type | Description |
| --- | --- | --- |
| `skip` | int | Offset — number of rows to skip (default `0`). |
| `limit` | int | Page size, `1`–`100` (default `50`). |
| `order_by` | string | `field:asc` or `field:desc` (e.g. `created_at:desc`). |
| `search` | string | Case-insensitive match across the model's text columns. |
| `after` | string | Keyset cursor from a previous response's `next_cursor` (stable, efficient deep pagination by primary key). |

Responses include `items`, `total`, `page`, `total_pages`, `has_more` and `next_cursor` (pass it back as `after` for the next page).

### REST analytics endpoints

Each model also exposes (at parity with GraphQL):

| Endpoint | Description |
| --- | --- |
| `GET /api/<model>/count` | Count rows; optional `search` or `field`+`value`. Returns `{count}`. |
| `GET /api/<model>/exists` | Whether any row matches. Returns `{exists}`. |
| `GET /api/<model>/by-field` | First row where `field`==`value` (404 if none). |
| `GET /api/<model>/aggregate` | `op`=count/sum/avg/min/max on `field`, optional `group_by`. |

```bash
# total views per status
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/post/aggregate?op=sum&field=views&group_by=status"
```

### GraphQL

Each model exposes `<model>_list`, `<model>_by_id`, `<model>_by_field`, `<model>_count`, `<model>_exists` and `<model>_aggregation` queries, plus `create_<model>`, `update_<model>` and `delete_<model>` mutations. `<model>_list` accepts `filter_group` (AND/OR groups of `{field, operator, value}`), `order_by`, `pagination`, `search` and `after`.

## Models

<a id="users"></a>
### `users` _(auth model)_

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `email` | TEXT | NOT NULL |  |
| `password_hash` | TEXT | NOT NULL |  |
| `display_name` | TEXT |  |  |
| `avatar_url` | TEXT |  |  |
| `locale` | TEXT |  |  |
| `theme` | TEXT |  |  |
| `font_scale` | NUMERIC(3, |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `last_active_at` | TIMESTAMP WITH TIME ZONE |  |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/users/register` | Register a new users (sign up); returns the created record |
| `POST` | `/api/users/login` | Authenticate; returns an access token (+ refresh token) |
| `POST` | `/api/users/change-password` | Change the authenticated user's password |
| `GET` | `/api/users/` | List users (search, sort, paginate) |
| `GET` | `/api/users/count` | Count users (optional search / field==value) |
| `GET` | `/api/users/exists` | Whether any users matches |
| `GET` | `/api/users/by-field` | Fetch the first users where field == value |
| `GET` | `/api/users/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/users/{id}` | Retrieve one users by id |
| `PUT` | `/api/users/{id}` | Replace a users record |
| `PATCH` | `/api/users/{id}` | Partially update a users record |
| `DELETE` | `/api/users/{id}` | Delete a users record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `users_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `users_by_id` | Fetch a single record by id |
| `users_by_field` | Fetch the first record where field == value |
| `users_count` | Count records (optionally filtered) |
| `users_exists` | Whether any record matches |
| `users_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_users` | Create a users |
| `update_users` | Update a users by id |
| `delete_users` | Delete a users by id |
| `login` | Authenticate; returns access + refresh tokens |
| `change_password` | Change password (old + new) |
| `refresh_access_token` | Exchange a refresh token for a fresh access token |

**Filter by:** `id`, `email`, `display_name`, `avatar_url`, `locale`, `theme`, `font_scale`, `created_at`, `updated_at`, `last_active_at`

**Sort by:** `id`, `font_scale`, `created_at`, `updated_at`, `last_active_at`

**Search covers:** `email`, `password_hash`, `display_name`, `avatar_url`, `locale`, `theme`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/users/?order_by=created_at:desc&limit=20"
```

**Example — login (REST):**

```bash
curl -X POST http://localhost:8000/api/users/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "user@example.com", "password": "secret"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  users_list(
    filter_group: { filters: [{ field: "email", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id email password_hash display_name }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  login(input: [{ fields: "email", value: "user@example.com" },
               { fields: "password", value: "secret", is_password: true }]) {
    access_token
    refresh_token
  }
}
```


<a id="devices"></a>
### `devices`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `name` | TEXT |  |  |
| `platform` | TEXT |  |  |
| `push_token` | TEXT |  |  |
| `last_synced_at` | TIMESTAMP WITH TIME ZONE |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/devices/` | Create a devices record |
| `GET` | `/api/devices/` | List devices (search, sort, paginate) |
| `GET` | `/api/devices/count` | Count devices (optional search / field==value) |
| `GET` | `/api/devices/exists` | Whether any devices matches |
| `GET` | `/api/devices/by-field` | Fetch the first devices where field == value |
| `GET` | `/api/devices/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/devices/{id}` | Retrieve one devices by id |
| `PUT` | `/api/devices/{id}` | Replace a devices record |
| `PATCH` | `/api/devices/{id}` | Partially update a devices record |
| `DELETE` | `/api/devices/{id}` | Delete a devices record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `devices_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `devices_by_id` | Fetch a single record by id |
| `devices_by_field` | Fetch the first record where field == value |
| `devices_count` | Count records (optionally filtered) |
| `devices_exists` | Whether any record matches |
| `devices_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_devices` | Create a devices |
| `update_devices` | Update a devices by id |
| `delete_devices` | Delete a devices by id |

**Filter by:** `id`, `name`, `platform`, `last_synced_at`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `last_synced_at`, `created_at`, `updated_at`

**Search covers:** `name`, `platform`, `push_token`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/devices/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "example", "platform": "example", "push_token": "example", "last_synced_at": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  devices_list(
    filter_group: { filters: [{ field: "name", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id name platform }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_devices(input: { name: "example", platform: "example", push_token: "example", last_synced_at: "example" }) {
    id
  }
}
```


<a id="books"></a>
### `books`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `title` | TEXT | NOT NULL |  |
| `subtitle` | TEXT |  |  |
| `description` | TEXT |  |  |
| `isbn` | TEXT |  |  |
| `language` | TEXT |  |  |
| `publisher` | TEXT |  |  |
| `published_on` | DATE |  |  |
| `cover_image_url` | TEXT |  |  |
| `word_count` | INTEGER |  |  |
| `chapter_count` | INTEGER |  |  |
| `est_reading_minutes` | INTEGER |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/books/` | Create a books record |
| `GET` | `/api/books/` | List books (search, sort, paginate) |
| `GET` | `/api/books/count` | Count books (optional search / field==value) |
| `GET` | `/api/books/exists` | Whether any books matches |
| `GET` | `/api/books/by-field` | Fetch the first books where field == value |
| `GET` | `/api/books/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/books/{id}` | Retrieve one books by id |
| `PUT` | `/api/books/{id}` | Replace a books record |
| `PATCH` | `/api/books/{id}` | Partially update a books record |
| `DELETE` | `/api/books/{id}` | Delete a books record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `books_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `books_by_id` | Fetch a single record by id |
| `books_by_field` | Fetch the first record where field == value |
| `books_count` | Count records (optionally filtered) |
| `books_exists` | Whether any record matches |
| `books_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_books` | Create a books |
| `update_books` | Update a books by id |
| `delete_books` | Delete a books by id |

**Filter by:** `id`, `title`, `subtitle`, `description`, `isbn`, `language`, `publisher`, `published_on`, `cover_image_url`, `word_count`, `chapter_count`, `est_reading_minutes`, `created_at`, `updated_at`

**Sort by:** `id`, `published_on`, `word_count`, `chapter_count`, `est_reading_minutes`, `created_at`, `updated_at`

**Search covers:** `title`, `subtitle`, `description`, `isbn`, `language`, `publisher`, `cover_image_url`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/books/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "example", "subtitle": "example", "description": "example", "isbn": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  books_list(
    filter_group: { filters: [{ field: "title", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id title subtitle description }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_books(input: { title: "example", subtitle: "example", description: "example", isbn: "example" }) {
    id
  }
}
```


<a id="book_authors"></a>
### `book_authors`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `book_id` | UUID | NOT NULL | PK |
| `author_id` | UUID | NOT NULL | PK |
| `author_role` | TEXT | NOT NULL | PK |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/book_authors/` | Create a book_authors record |
| `GET` | `/api/book_authors/` | List book_authors (search, sort, paginate) |
| `GET` | `/api/book_authors/count` | Count book_authors (optional search / field==value) |
| `GET` | `/api/book_authors/exists` | Whether any book_authors matches |
| `GET` | `/api/book_authors/by-field` | Fetch the first book_authors where field == value |
| `GET` | `/api/book_authors/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/book_authors/{id}` | Retrieve one book_authors by id |
| `PUT` | `/api/book_authors/{id}` | Replace a book_authors record |
| `PATCH` | `/api/book_authors/{id}` | Partially update a book_authors record |
| `DELETE` | `/api/book_authors/{id}` | Delete a book_authors record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `book_authors_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `book_authors_by_id` | Fetch a single record by id |
| `book_authors_by_field` | Fetch the first record where field == value |
| `book_authors_count` | Count records (optionally filtered) |
| `book_authors_exists` | Whether any record matches |
| `book_authors_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_book_authors` | Create a book_authors |
| `update_book_authors` | Update a book_authors by id |
| `delete_book_authors` | Delete a book_authors by id |

**Filter by:** `book_id`, `author_id`, `author_role`

**Sort by:** `book_id`, `author_id`

**Search covers:** `author_role`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/book_authors/?order_by=book_id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/book_authors/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{}'
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_book_authors(input: {  }) {
    book_id
  }
}
```


<a id="authors"></a>
### `authors`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `name` | TEXT | NOT NULL |  |
| `bio` | TEXT |  |  |
| `photo_url` | TEXT |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/authors/` | Create a authors record |
| `GET` | `/api/authors/` | List authors (search, sort, paginate) |
| `GET` | `/api/authors/count` | Count authors (optional search / field==value) |
| `GET` | `/api/authors/exists` | Whether any authors matches |
| `GET` | `/api/authors/by-field` | Fetch the first authors where field == value |
| `GET` | `/api/authors/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/authors/{id}` | Retrieve one authors by id |
| `PUT` | `/api/authors/{id}` | Replace a authors record |
| `PATCH` | `/api/authors/{id}` | Partially update a authors record |
| `DELETE` | `/api/authors/{id}` | Delete a authors record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `authors_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `authors_by_id` | Fetch a single record by id |
| `authors_by_field` | Fetch the first record where field == value |
| `authors_count` | Count records (optionally filtered) |
| `authors_exists` | Whether any record matches |
| `authors_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_authors` | Create a authors |
| `update_authors` | Update a authors by id |
| `delete_authors` | Delete a authors by id |

**Filter by:** `id`, `name`, `bio`, `photo_url`, `created_at`, `updated_at`

**Sort by:** `id`, `created_at`, `updated_at`

**Search covers:** `name`, `bio`, `photo_url`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/authors/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/authors/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "example", "bio": "example", "photo_url": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  authors_list(
    filter_group: { filters: [{ field: "name", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id name bio photo_url }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_authors(input: { name: "example", bio: "example", photo_url: "example" }) {
    id
  }
}
```


<a id="book_genres"></a>
### `book_genres`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `book_id` | UUID | NOT NULL | PK |
| `genre_id` | UUID | NOT NULL | PK |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/book_genres/` | Create a book_genres record |
| `GET` | `/api/book_genres/` | List book_genres (search, sort, paginate) |
| `GET` | `/api/book_genres/count` | Count book_genres (optional search / field==value) |
| `GET` | `/api/book_genres/exists` | Whether any book_genres matches |
| `GET` | `/api/book_genres/by-field` | Fetch the first book_genres where field == value |
| `GET` | `/api/book_genres/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/book_genres/{id}` | Retrieve one book_genres by id |
| `PUT` | `/api/book_genres/{id}` | Replace a book_genres record |
| `PATCH` | `/api/book_genres/{id}` | Partially update a book_genres record |
| `DELETE` | `/api/book_genres/{id}` | Delete a book_genres record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `book_genres_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `book_genres_by_id` | Fetch a single record by id |
| `book_genres_by_field` | Fetch the first record where field == value |
| `book_genres_count` | Count records (optionally filtered) |
| `book_genres_exists` | Whether any record matches |
| `book_genres_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_book_genres` | Create a book_genres |
| `update_book_genres` | Update a book_genres by id |
| `delete_book_genres` | Delete a book_genres by id |

**Filter by:** `book_id`, `genre_id`

**Sort by:** `book_id`, `genre_id`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/book_genres/?order_by=book_id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/book_genres/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{}'
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_book_genres(input: {  }) {
    book_id
  }
}
```


<a id="genres"></a>
### `genres`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `name` | TEXT | NOT NULL |  |
| `slug` | TEXT | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/genres/` | Create a genres record |
| `GET` | `/api/genres/` | List genres (search, sort, paginate) |
| `GET` | `/api/genres/count` | Count genres (optional search / field==value) |
| `GET` | `/api/genres/exists` | Whether any genres matches |
| `GET` | `/api/genres/by-field` | Fetch the first genres where field == value |
| `GET` | `/api/genres/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/genres/{id}` | Retrieve one genres by id |
| `PUT` | `/api/genres/{id}` | Replace a genres record |
| `PATCH` | `/api/genres/{id}` | Partially update a genres record |
| `DELETE` | `/api/genres/{id}` | Delete a genres record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `genres_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `genres_by_id` | Fetch a single record by id |
| `genres_by_field` | Fetch the first record where field == value |
| `genres_count` | Count records (optionally filtered) |
| `genres_exists` | Whether any record matches |
| `genres_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_genres` | Create a genres |
| `update_genres` | Update a genres by id |
| `delete_genres` | Delete a genres by id |

**Filter by:** `id`, `name`, `slug`

**Sort by:** `id`

**Search covers:** `name`, `slug`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/genres/?order_by=id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/genres/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "example", "slug": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  genres_list(
    filter_group: { filters: [{ field: "name", operator: "eq", value: "example" }] }
    order_by: { field: "id", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id name slug }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_genres(input: { name: "example", slug: "example" }) {
    id
  }
}
```


<a id="chapters"></a>
### `chapters`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `book_id` | UUID | NOT NULL | FK → books |
| `order_index` | INTEGER | NOT NULL |  |
| `title` | TEXT |  |  |
| `content` | TEXT | NOT NULL |  |
| `content_format` | TEXT |  |  |
| `word_count` | INTEGER |  |  |
| `char_count` | INTEGER |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/chapters/` | Create a chapters record |
| `GET` | `/api/chapters/` | List chapters (search, sort, paginate) |
| `GET` | `/api/chapters/count` | Count chapters (optional search / field==value) |
| `GET` | `/api/chapters/exists` | Whether any chapters matches |
| `GET` | `/api/chapters/by-field` | Fetch the first chapters where field == value |
| `GET` | `/api/chapters/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/chapters/{id}` | Retrieve one chapters by id |
| `PUT` | `/api/chapters/{id}` | Replace a chapters record |
| `PATCH` | `/api/chapters/{id}` | Partially update a chapters record |
| `DELETE` | `/api/chapters/{id}` | Delete a chapters record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `chapters_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `chapters_by_id` | Fetch a single record by id |
| `chapters_by_field` | Fetch the first record where field == value |
| `chapters_count` | Count records (optionally filtered) |
| `chapters_exists` | Whether any record matches |
| `chapters_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_chapters` | Create a chapters |
| `update_chapters` | Update a chapters by id |
| `delete_chapters` | Delete a chapters by id |

**Filter by:** `id`, `book_id`, `order_index`, `title`, `content`, `content_format`, `word_count`, `char_count`, `created_at`, `updated_at`

**Sort by:** `id`, `book_id`, `order_index`, `word_count`, `char_count`, `created_at`, `updated_at`

**Search covers:** `title`, `content`, `content_format`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/chapters/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/chapters/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "order_index": 10, "title": "example", "content": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  chapters_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id book_id order_index title }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_chapters(input: { book_id: "example", order_index: 10, title: "example", content: "example" }) {
    id
  }
}
```


<a id="user_books"></a>
### `user_books`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `status` | TEXT | NOT NULL |  |
| `is_favorite` | BOOLEAN | NOT NULL |  |
| `rating` | SMALLINT |  |  |
| `review` | TEXT |  |  |
| `started_at` | TIMESTAMP WITH TIME ZONE |  |  |
| `finished_at` | TIMESTAMP WITH TIME ZONE |  |  |
| `added_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/user_books/` | Create a user_books record |
| `GET` | `/api/user_books/` | List user_books (search, sort, paginate) |
| `GET` | `/api/user_books/count` | Count user_books (optional search / field==value) |
| `GET` | `/api/user_books/exists` | Whether any user_books matches |
| `GET` | `/api/user_books/by-field` | Fetch the first user_books where field == value |
| `GET` | `/api/user_books/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/user_books/{id}` | Retrieve one user_books by id |
| `PUT` | `/api/user_books/{id}` | Replace a user_books record |
| `PATCH` | `/api/user_books/{id}` | Partially update a user_books record |
| `DELETE` | `/api/user_books/{id}` | Delete a user_books record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `user_books_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `user_books_by_id` | Fetch a single record by id |
| `user_books_by_field` | Fetch the first record where field == value |
| `user_books_count` | Count records (optionally filtered) |
| `user_books_exists` | Whether any record matches |
| `user_books_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_user_books` | Create a user_books |
| `update_user_books` | Update a user_books by id |
| `delete_user_books` | Delete a user_books by id |

**Filter by:** `id`, `book_id`, `status`, `is_favorite`, `rating`, `review`, `started_at`, `finished_at`, `added_at`, `updated_at`

**Sort by:** `id`, `user_id`, `book_id`, `is_favorite`, `rating`, `started_at`, `finished_at`, `added_at`, `updated_at`

**Search covers:** `status`, `review`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/user_books/?order_by=id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/user_books/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "status": "example", "is_favorite": true, "rating": 10}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  user_books_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "id", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id status }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_user_books(input: { book_id: "example", status: "example", is_favorite: true, rating: 10 }) {
    id
  }
}
```


<a id="collections"></a>
### `collections`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `name` | TEXT | NOT NULL |  |
| `description` | TEXT |  |  |
| `color` | TEXT |  |  |
| `icon` | TEXT |  |  |
| `sort_order` | INTEGER |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/collections/` | Create a collections record |
| `GET` | `/api/collections/` | List collections (search, sort, paginate) |
| `GET` | `/api/collections/count` | Count collections (optional search / field==value) |
| `GET` | `/api/collections/exists` | Whether any collections matches |
| `GET` | `/api/collections/by-field` | Fetch the first collections where field == value |
| `GET` | `/api/collections/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/collections/{id}` | Retrieve one collections by id |
| `PUT` | `/api/collections/{id}` | Replace a collections record |
| `PATCH` | `/api/collections/{id}` | Partially update a collections record |
| `DELETE` | `/api/collections/{id}` | Delete a collections record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `collections_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `collections_by_id` | Fetch a single record by id |
| `collections_by_field` | Fetch the first record where field == value |
| `collections_count` | Count records (optionally filtered) |
| `collections_exists` | Whether any record matches |
| `collections_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_collections` | Create a collections |
| `update_collections` | Update a collections by id |
| `delete_collections` | Delete a collections by id |

**Filter by:** `id`, `name`, `description`, `color`, `icon`, `sort_order`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `sort_order`, `created_at`, `updated_at`

**Search covers:** `name`, `description`, `color`, `icon`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/collections/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/collections/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "example", "description": "example", "color": "example", "icon": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  collections_list(
    filter_group: { filters: [{ field: "name", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id name description }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_collections(input: { name: "example", description: "example", color: "example", icon: "example" }) {
    id
  }
}
```


<a id="collection_books"></a>
### `collection_books`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `collection_id` | UUID | NOT NULL | PK |
| `book_id` | UUID | NOT NULL | PK |
| `added_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/collection_books/` | Create a collection_books record |
| `GET` | `/api/collection_books/` | List collection_books (search, sort, paginate) |
| `GET` | `/api/collection_books/count` | Count collection_books (optional search / field==value) |
| `GET` | `/api/collection_books/exists` | Whether any collection_books matches |
| `GET` | `/api/collection_books/by-field` | Fetch the first collection_books where field == value |
| `GET` | `/api/collection_books/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/collection_books/{id}` | Retrieve one collection_books by id |
| `PUT` | `/api/collection_books/{id}` | Replace a collection_books record |
| `PATCH` | `/api/collection_books/{id}` | Partially update a collection_books record |
| `DELETE` | `/api/collection_books/{id}` | Delete a collection_books record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `collection_books_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `collection_books_by_id` | Fetch a single record by id |
| `collection_books_by_field` | Fetch the first record where field == value |
| `collection_books_count` | Count records (optionally filtered) |
| `collection_books_exists` | Whether any record matches |
| `collection_books_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_collection_books` | Create a collection_books |
| `update_collection_books` | Update a collection_books by id |
| `delete_collection_books` | Delete a collection_books by id |

**Filter by:** `collection_id`, `book_id`, `added_at`

**Sort by:** `collection_id`, `book_id`, `added_at`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/collection_books/?order_by=collection_id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/collection_books/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"added_at": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  collection_books_list(
    filter_group: { filters: [{ field: "added_at", operator: "eq", value: "example" }] }
    order_by: { field: "collection_id", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { collection_id book_id added_at }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_collection_books(input: { added_at: "example" }) {
    collection_id
  }
}
```


<a id="tags"></a>
### `tags`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `name` | TEXT | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/tags/` | Create a tags record |
| `GET` | `/api/tags/` | List tags (search, sort, paginate) |
| `GET` | `/api/tags/count` | Count tags (optional search / field==value) |
| `GET` | `/api/tags/exists` | Whether any tags matches |
| `GET` | `/api/tags/by-field` | Fetch the first tags where field == value |
| `GET` | `/api/tags/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/tags/{id}` | Retrieve one tags by id |
| `PUT` | `/api/tags/{id}` | Replace a tags record |
| `PATCH` | `/api/tags/{id}` | Partially update a tags record |
| `DELETE` | `/api/tags/{id}` | Delete a tags record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `tags_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `tags_by_id` | Fetch a single record by id |
| `tags_by_field` | Fetch the first record where field == value |
| `tags_count` | Count records (optionally filtered) |
| `tags_exists` | Whether any record matches |
| `tags_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_tags` | Create a tags |
| `update_tags` | Update a tags by id |
| `delete_tags` | Delete a tags by id |

**Filter by:** `id`, `name`

**Sort by:** `id`, `user_id`

**Search covers:** `name`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/tags/?order_by=id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/tags/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  tags_list(
    filter_group: { filters: [{ field: "name", operator: "eq", value: "example" }] }
    order_by: { field: "id", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id name }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_tags(input: { name: "example" }) {
    id
  }
}
```


<a id="user_book_tags"></a>
### `user_book_tags`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `user_book_id` | UUID | NOT NULL | PK |
| `tag_id` | UUID | NOT NULL | PK |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/user_book_tags/` | Create a user_book_tags record |
| `GET` | `/api/user_book_tags/` | List user_book_tags (search, sort, paginate) |
| `GET` | `/api/user_book_tags/count` | Count user_book_tags (optional search / field==value) |
| `GET` | `/api/user_book_tags/exists` | Whether any user_book_tags matches |
| `GET` | `/api/user_book_tags/by-field` | Fetch the first user_book_tags where field == value |
| `GET` | `/api/user_book_tags/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/user_book_tags/{id}` | Retrieve one user_book_tags by id |
| `PUT` | `/api/user_book_tags/{id}` | Replace a user_book_tags record |
| `PATCH` | `/api/user_book_tags/{id}` | Partially update a user_book_tags record |
| `DELETE` | `/api/user_book_tags/{id}` | Delete a user_book_tags record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `user_book_tags_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `user_book_tags_by_id` | Fetch a single record by id |
| `user_book_tags_by_field` | Fetch the first record where field == value |
| `user_book_tags_count` | Count records (optionally filtered) |
| `user_book_tags_exists` | Whether any record matches |
| `user_book_tags_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_user_book_tags` | Create a user_book_tags |
| `update_user_book_tags` | Update a user_book_tags by id |
| `delete_user_book_tags` | Delete a user_book_tags by id |

**Filter by:** `user_book_id`, `tag_id`

**Sort by:** `user_book_id`, `tag_id`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/user_book_tags/?order_by=user_book_id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/user_book_tags/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{}'
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_user_book_tags(input: {  }) {
    user_book_id
  }
}
```


<a id="reading_progress"></a>
### `reading_progress`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `chapter_id` | UUID |  | FK → chapters |
| `char_offset` | INTEGER | NOT NULL |  |
| `progress_percent` | NUMERIC(5, | NOT NULL |  |
| `last_device_id` | UUID |  | FK → devices |
| `last_read_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/reading_progress/` | Create a reading_progress record |
| `GET` | `/api/reading_progress/` | List reading_progress (search, sort, paginate) |
| `GET` | `/api/reading_progress/count` | Count reading_progress (optional search / field==value) |
| `GET` | `/api/reading_progress/exists` | Whether any reading_progress matches |
| `GET` | `/api/reading_progress/by-field` | Fetch the first reading_progress where field == value |
| `GET` | `/api/reading_progress/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/reading_progress/{id}` | Retrieve one reading_progress by id |
| `PUT` | `/api/reading_progress/{id}` | Replace a reading_progress record |
| `PATCH` | `/api/reading_progress/{id}` | Partially update a reading_progress record |
| `DELETE` | `/api/reading_progress/{id}` | Delete a reading_progress record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `reading_progress_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `reading_progress_by_id` | Fetch a single record by id |
| `reading_progress_by_field` | Fetch the first record where field == value |
| `reading_progress_count` | Count records (optionally filtered) |
| `reading_progress_exists` | Whether any record matches |
| `reading_progress_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_reading_progress` | Create a reading_progress |
| `update_reading_progress` | Update a reading_progress by id |
| `delete_reading_progress` | Delete a reading_progress by id |

**Filter by:** `id`, `book_id`, `chapter_id`, `char_offset`, `progress_percent`, `last_device_id`, `last_read_at`, `updated_at`

**Sort by:** `id`, `user_id`, `book_id`, `chapter_id`, `char_offset`, `progress_percent`, `last_device_id`, `last_read_at`, `updated_at`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/reading_progress/?order_by=id:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/reading_progress/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "chapter_id": "example", "char_offset": 10, "progress_percent": 10}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  reading_progress_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "id", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id chapter_id }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_reading_progress(input: { book_id: "example", chapter_id: "example", char_offset: 10, progress_percent: 10 }) {
    id
  }
}
```


<a id="reading_sessions"></a>
### `reading_sessions`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `device_id` | UUID |  | FK → devices |
| `started_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `ended_at` | TIMESTAMP WITH TIME ZONE |  |  |
| `duration_seconds` | INTEGER |  |  |
| `words_read` | INTEGER |  |  |
| `start_percent` | NUMERIC(5, |  |  |
| `end_percent` | NUMERIC(5, |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/reading_sessions/` | Create a reading_sessions record |
| `GET` | `/api/reading_sessions/` | List reading_sessions (search, sort, paginate) |
| `GET` | `/api/reading_sessions/count` | Count reading_sessions (optional search / field==value) |
| `GET` | `/api/reading_sessions/exists` | Whether any reading_sessions matches |
| `GET` | `/api/reading_sessions/by-field` | Fetch the first reading_sessions where field == value |
| `GET` | `/api/reading_sessions/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/reading_sessions/{id}` | Retrieve one reading_sessions by id |
| `PUT` | `/api/reading_sessions/{id}` | Replace a reading_sessions record |
| `PATCH` | `/api/reading_sessions/{id}` | Partially update a reading_sessions record |
| `DELETE` | `/api/reading_sessions/{id}` | Delete a reading_sessions record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `reading_sessions_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `reading_sessions_by_id` | Fetch a single record by id |
| `reading_sessions_by_field` | Fetch the first record where field == value |
| `reading_sessions_count` | Count records (optionally filtered) |
| `reading_sessions_exists` | Whether any record matches |
| `reading_sessions_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_reading_sessions` | Create a reading_sessions |
| `update_reading_sessions` | Update a reading_sessions by id |
| `delete_reading_sessions` | Delete a reading_sessions by id |

**Filter by:** `id`, `book_id`, `device_id`, `started_at`, `ended_at`, `duration_seconds`, `words_read`, `start_percent`, `end_percent`, `created_at`

**Sort by:** `id`, `user_id`, `book_id`, `device_id`, `started_at`, `ended_at`, `duration_seconds`, `words_read`, `start_percent`, `end_percent`, `created_at`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/reading_sessions/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/reading_sessions/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "device_id": "example", "started_at": "example", "ended_at": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  reading_sessions_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id device_id }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_reading_sessions(input: { book_id: "example", device_id: "example", started_at: "example", ended_at: "example" }) {
    id
  }
}
```


<a id="highlights"></a>
### `highlights`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `chapter_id` | UUID | NOT NULL | FK → chapters |
| `start_offset` | INTEGER | NOT NULL |  |
| `end_offset` | INTEGER | NOT NULL |  |
| `selected_text` | TEXT | NOT NULL |  |
| `color` | TEXT | NOT NULL |  |
| `note` | TEXT |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/highlights/` | Create a highlights record |
| `GET` | `/api/highlights/` | List highlights (search, sort, paginate) |
| `GET` | `/api/highlights/count` | Count highlights (optional search / field==value) |
| `GET` | `/api/highlights/exists` | Whether any highlights matches |
| `GET` | `/api/highlights/by-field` | Fetch the first highlights where field == value |
| `GET` | `/api/highlights/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/highlights/{id}` | Retrieve one highlights by id |
| `PUT` | `/api/highlights/{id}` | Replace a highlights record |
| `PATCH` | `/api/highlights/{id}` | Partially update a highlights record |
| `DELETE` | `/api/highlights/{id}` | Delete a highlights record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `highlights_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `highlights_by_id` | Fetch a single record by id |
| `highlights_by_field` | Fetch the first record where field == value |
| `highlights_count` | Count records (optionally filtered) |
| `highlights_exists` | Whether any record matches |
| `highlights_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_highlights` | Create a highlights |
| `update_highlights` | Update a highlights by id |
| `delete_highlights` | Delete a highlights by id |

**Filter by:** `id`, `book_id`, `chapter_id`, `start_offset`, `end_offset`, `selected_text`, `color`, `note`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `book_id`, `chapter_id`, `start_offset`, `end_offset`, `created_at`, `updated_at`

**Search covers:** `selected_text`, `color`, `note`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/highlights/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/highlights/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "chapter_id": "example", "start_offset": 10, "end_offset": 10}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  highlights_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id chapter_id }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_highlights(input: { book_id: "example", chapter_id: "example", start_offset: 10, end_offset: 10 }) {
    id
  }
}
```


<a id="bookmarks"></a>
### `bookmarks`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `chapter_id` | UUID | NOT NULL | FK → chapters |
| `char_offset` | INTEGER | NOT NULL |  |
| `label` | TEXT |  |  |
| `preview_text` | TEXT |  |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/bookmarks/` | Create a bookmarks record |
| `GET` | `/api/bookmarks/` | List bookmarks (search, sort, paginate) |
| `GET` | `/api/bookmarks/count` | Count bookmarks (optional search / field==value) |
| `GET` | `/api/bookmarks/exists` | Whether any bookmarks matches |
| `GET` | `/api/bookmarks/by-field` | Fetch the first bookmarks where field == value |
| `GET` | `/api/bookmarks/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/bookmarks/{id}` | Retrieve one bookmarks by id |
| `PUT` | `/api/bookmarks/{id}` | Replace a bookmarks record |
| `PATCH` | `/api/bookmarks/{id}` | Partially update a bookmarks record |
| `DELETE` | `/api/bookmarks/{id}` | Delete a bookmarks record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `bookmarks_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `bookmarks_by_id` | Fetch a single record by id |
| `bookmarks_by_field` | Fetch the first record where field == value |
| `bookmarks_count` | Count records (optionally filtered) |
| `bookmarks_exists` | Whether any record matches |
| `bookmarks_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_bookmarks` | Create a bookmarks |
| `update_bookmarks` | Update a bookmarks by id |
| `delete_bookmarks` | Delete a bookmarks by id |

**Filter by:** `id`, `book_id`, `chapter_id`, `char_offset`, `label`, `preview_text`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `book_id`, `chapter_id`, `char_offset`, `created_at`, `updated_at`

**Search covers:** `label`, `preview_text`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/bookmarks/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/bookmarks/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "chapter_id": "example", "char_offset": 10, "label": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  bookmarks_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id chapter_id }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_bookmarks(input: { book_id: "example", chapter_id: "example", char_offset: 10, label: "example" }) {
    id
  }
}
```


<a id="quotes"></a>
### `quotes`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `chapter_id` | UUID |  | FK → chapters |
| `highlight_id` | UUID |  | FK → highlights |
| `quote_text` | TEXT | NOT NULL |  |
| `note` | TEXT |  |  |
| `location_label` | TEXT |  |  |
| `is_favorite` | BOOLEAN | NOT NULL |  |
| `is_public` | BOOLEAN | NOT NULL |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/quotes/` | Create a quotes record |
| `GET` | `/api/quotes/` | List quotes (search, sort, paginate) |
| `GET` | `/api/quotes/count` | Count quotes (optional search / field==value) |
| `GET` | `/api/quotes/exists` | Whether any quotes matches |
| `GET` | `/api/quotes/by-field` | Fetch the first quotes where field == value |
| `GET` | `/api/quotes/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/quotes/{id}` | Retrieve one quotes by id |
| `PUT` | `/api/quotes/{id}` | Replace a quotes record |
| `PATCH` | `/api/quotes/{id}` | Partially update a quotes record |
| `DELETE` | `/api/quotes/{id}` | Delete a quotes record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `quotes_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `quotes_by_id` | Fetch a single record by id |
| `quotes_by_field` | Fetch the first record where field == value |
| `quotes_count` | Count records (optionally filtered) |
| `quotes_exists` | Whether any record matches |
| `quotes_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_quotes` | Create a quotes |
| `update_quotes` | Update a quotes by id |
| `delete_quotes` | Delete a quotes by id |

**Filter by:** `id`, `book_id`, `chapter_id`, `highlight_id`, `quote_text`, `note`, `location_label`, `is_favorite`, `is_public`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `book_id`, `chapter_id`, `highlight_id`, `is_favorite`, `is_public`, `created_at`, `updated_at`

**Search covers:** `quote_text`, `note`, `location_label`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/quotes/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/quotes/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "chapter_id": "example", "highlight_id": "example", "quote_text": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  quotes_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id chapter_id }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_quotes(input: { book_id: "example", chapter_id: "example", highlight_id: "example", quote_text: "example" }) {
    id
  }
}
```


<a id="notes"></a>
### `notes`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `book_id` | UUID | NOT NULL | FK → books |
| `chapter_id` | UUID |  | FK → chapters |
| `char_offset` | INTEGER |  |  |
| `content` | TEXT | NOT NULL |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/notes/` | Create a notes record |
| `GET` | `/api/notes/` | List notes (search, sort, paginate) |
| `GET` | `/api/notes/count` | Count notes (optional search / field==value) |
| `GET` | `/api/notes/exists` | Whether any notes matches |
| `GET` | `/api/notes/by-field` | Fetch the first notes where field == value |
| `GET` | `/api/notes/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/notes/{id}` | Retrieve one notes by id |
| `PUT` | `/api/notes/{id}` | Replace a notes record |
| `PATCH` | `/api/notes/{id}` | Partially update a notes record |
| `DELETE` | `/api/notes/{id}` | Delete a notes record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `notes_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `notes_by_id` | Fetch a single record by id |
| `notes_by_field` | Fetch the first record where field == value |
| `notes_count` | Count records (optionally filtered) |
| `notes_exists` | Whether any record matches |
| `notes_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_notes` | Create a notes |
| `update_notes` | Update a notes by id |
| `delete_notes` | Delete a notes by id |

**Filter by:** `id`, `book_id`, `chapter_id`, `char_offset`, `content`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `book_id`, `chapter_id`, `char_offset`, `created_at`, `updated_at`

**Search covers:** `content`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/notes/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/notes/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"book_id": "example", "chapter_id": "example", "char_offset": 10, "content": "example"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  notes_list(
    filter_group: { filters: [{ field: "book_id", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id book_id chapter_id }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_notes(input: { book_id: "example", chapter_id: "example", char_offset: 10, content: "example" }) {
    id
  }
}
```


<a id="reading_goals"></a>
### `reading_goals`

**Fields**

| Column | Type | Null | Key |
| --- | --- | --- | --- |
| `id` | UUID | NOT NULL | PK |
| `user_id` | UUID | NOT NULL | FK → users |
| `period` | TEXT | NOT NULL |  |
| `metric` | TEXT | NOT NULL |  |
| `target_value` | INTEGER | NOT NULL |  |
| `period_start` | DATE | NOT NULL |  |
| `period_end` | DATE | NOT NULL |  |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL |  |

**REST endpoints**

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/reading_goals/` | Create a reading_goals record |
| `GET` | `/api/reading_goals/` | List reading_goals (search, sort, paginate) |
| `GET` | `/api/reading_goals/count` | Count reading_goals (optional search / field==value) |
| `GET` | `/api/reading_goals/exists` | Whether any reading_goals matches |
| `GET` | `/api/reading_goals/by-field` | Fetch the first reading_goals where field == value |
| `GET` | `/api/reading_goals/aggregate` | count / sum / avg / min / max (optional group_by) |
| `GET` | `/api/reading_goals/{id}` | Retrieve one reading_goals by id |
| `PUT` | `/api/reading_goals/{id}` | Replace a reading_goals record |
| `PATCH` | `/api/reading_goals/{id}` | Partially update a reading_goals record |
| `DELETE` | `/api/reading_goals/{id}` | Delete a reading_goals record |

**GraphQL queries**

| Query | Description |
| --- | --- |
| `reading_goals_list` | List with filter_group (AND/OR), order_by, pagination, search, after |
| `reading_goals_by_id` | Fetch a single record by id |
| `reading_goals_by_field` | Fetch the first record where field == value |
| `reading_goals_count` | Count records (optionally filtered) |
| `reading_goals_exists` | Whether any record matches |
| `reading_goals_aggregation` | Aggregate: count / sum / avg / min / max (optional group_by) |

**GraphQL mutations**

| Mutation | Description |
| --- | --- |
| `create_reading_goals` | Create a reading_goals |
| `update_reading_goals` | Update a reading_goals by id |
| `delete_reading_goals` | Delete a reading_goals by id |

**Filter by:** `id`, `period`, `metric`, `target_value`, `period_start`, `period_end`, `created_at`, `updated_at`

**Sort by:** `id`, `user_id`, `target_value`, `period_start`, `period_end`, `created_at`, `updated_at`

**Search covers:** `period`, `metric`

**Example — list (REST):**

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/reading_goals/?order_by=created_at:desc&limit=20"
```

**Example — create (REST):**

```bash
curl -X POST http://localhost:8000/api/reading_goals/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"period": "example", "metric": "example", "target_value": 10, "period_start": "2024-01-01"}'
```

**Example — filtered list (GraphQL):**

```graphql
query {
  reading_goals_list(
    filter_group: { filters: [{ field: "period", operator: "eq", value: "example" }] }
    order_by: { field: "created_at", direction: DESC }
    pagination: { limit: 20, offset: 0 }
  ) {
    items { id user_id period metric }
    total
  }
}
```

**Example — mutation (GraphQL):**

```graphql
mutation {
  create_reading_goals(input: { period: "example", metric: "example", target_value: 10, period_start: "2024-01-01" }) {
    id
  }
}
```


---

_Generated by backend_coder._
