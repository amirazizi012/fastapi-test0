# Library API

A library API built with **FastAPI** and **PostgreSQL**. Books are stored in a `books` table, so the data stays after the server restarts.

## Endpoints

| Method | Endpoint      | Description               |
|--------|---------------|---------------------------|
| GET    | `/books`      | Get the list of all books |
| POST   | `/books`      | Add a new book            |
| GET    | `/books/{id}` | Get a specific book       |
| PATCH  | `/books/{id}` | Update a specific book    |
| DELETE | `/books/{id}` | Delete a specific book    |

A book has two fields: `title` and `author`.

## Installation

Requires Python 3.10+ and PostgreSQL.

```
pip install -r requirements.txt
```

## Database

Create a user and a database (in `psql`):

```sql
CREATE USER app_user WITH PASSWORD 'your_password';
CREATE DATABASE library OWNER app_user;
```

Copy `.env.example` to `.env` and set the connection string:

```
DATABASE_URL=postgresql://app_user:your_password@localhost:5432/library
```

The `books` table (see `schema.sql`) is created automatically when the server starts. If it is empty, four starter books are added.

## Run

```
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000/docs` to test the API.

## Example

```
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Refactoring", "author": "Martin Fowler"}'
```

## How the connection works

`db.py` reads `DATABASE_URL` from `.env` and opens a connection with `psycopg`. Each endpoint opens a connection with `with get_conn() as conn:`, runs its SQL, and the `with` block commits and closes it. Values are always passed as `%s` parameters, never pasted into the SQL string, so user input cannot inject SQL.
