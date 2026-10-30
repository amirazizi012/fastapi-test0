"""PostgreSQL storage layer for the books project."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def get_connection() -> psycopg.Connection:
    """Open a connection using the DATABASE_URL environment variable."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env first.")
    return psycopg.connect(url)


def init_schema(conn: psycopg.Connection) -> None:
    """Create tables if they do not exist yet."""
    with conn.cursor() as cur:
        cur.execute(SCHEMA_FILE.read_text(encoding="utf-8"))


def _get_or_create(cur, table: str, name: str) -> int:
    cur.execute(
        f"""INSERT INTO {table} (name) VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id""",
        (name,),
    )
    return cur.fetchone()[0]


def save_books(conn: psycopg.Connection, books: list[dict]) -> int:
    """Insert books (with authors and publisher). Returns how many were new."""
    inserted = 0
    with conn.cursor() as cur:
        for book in books:
            publisher_id = (
                _get_or_create(cur, "publishers", book["publisher"])
                if book.get("publisher") else None
            )
            cur.execute(
                """INSERT INTO books
                       (ol_key, title, first_publish_year, isbn, pages, publisher_id)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ON CONFLICT (ol_key) DO NOTHING
                   RETURNING id""",
                (
                    book["ol_key"], book["title"], book["first_publish_year"],
                    book.get("isbn") or None, book.get("pages") or None, publisher_id,
                ),
            )
            row = cur.fetchone()
            if row is None:      # already stored
                continue
            inserted += 1
            for name in book.get("author_list", []):
                author_id = _get_or_create(cur, "authors", name)
                cur.execute(
                    "INSERT INTO book_authors VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (row[0], author_id),
                )
    conn.commit()
    return inserted
