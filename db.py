import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SEED_BOOKS = [
    ("Clean Code", "Robert C. Martin"),
    ("The Pragmatic Programmer", "Andrew Hunt"),
    ("Introduction to Algorithms", "Thomas H. Cormen"),
    ("Design Patterns", "Erich Gamma"),
]


def get_conn():
    """Open a new connection. Rows come back as dicts."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    """Create the books table and add the starter books if it is empty."""
    schema = Path(__file__).with_name("schema.sql").read_text()
    with get_conn() as conn:
        conn.execute(schema)
        count = conn.execute("SELECT COUNT(*) AS n FROM books").fetchone()["n"]
        if count == 0:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO books (title, author) VALUES (%s, %s)", SEED_BOOKS
                )
