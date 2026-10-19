# Library API

A simple library management API built with **FastAPI**.
There is no database: books are stored in a Python dictionary (hash map) inside `main.py`, so data resets when the server restarts.

## Endpoints

| Method | Endpoint      | Description                 |
|--------|---------------|-----------------------------|
| GET    | `/books`      | Get the list of all books   |
| POST   | `/books`      | Add a new book              |
| GET    | `/books/{id}` | Get a specific book         |
| PATCH  | `/books/{id}` | Update a specific book      |
| DELETE | `/books/{id}` | Delete a specific book      |

A book has two fields: `title` and `author`.

## Installation

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Run

```bash
uvicorn main:app --reload
```

(with uv: `uv run uvicorn main:app --reload`)

Then open `http://127.0.0.1:8000/docs` to test the API.

## Example

```bash
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Refactoring", "author": "Martin Fowler"}'
```

## Why these choices

- **FastAPI**: builds the endpoints, validates input, and generates the `/docs` page automatically.
- **Uvicorn**: the server that runs the FastAPI app.
- **Dictionary (hash map)**: books are stored by id, so finding, updating or deleting a book is a single lookup and does not get slower as books are added.
- **Separate models (BookCreate, BookUpdate, Book):** create requires title and author, update makes every field optional so PATCH can change just one, and - - Book (with id) defines the response shape shown in the docs.
- PATCH only changes sent fields: exclude_unset=True ignores everything the client did not send; fields sent as null are ignored too.
- get_or_404 and ensure_isbn_is_unique helpers: each check is written once and reused by several endpoints instead of being repeated.
- HTTP status codes: 201 created, 204 deleted (no body), 404 not found, 409 duplicate ISBN, 422 invalid input. These follow standard REST conventions.
- Single application file: the project is small, so keeping everything in main.py makes it easy to read and review.