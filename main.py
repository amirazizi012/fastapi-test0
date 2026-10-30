from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_conn, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # runs once when the server starts
    yield


app = FastAPI(title="Library API", lifespan=lifespan)


class BookIn(BaseModel):
    title: str
    author: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None


def get_or_404(conn, book_id: int):
    book = conn.execute(
        "SELECT id, title, author FROM books WHERE id = %s", (book_id,)
    ).fetchone()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/books")
def list_books():
    with get_conn() as conn:
        return conn.execute("SELECT id, title, author FROM books ORDER BY id").fetchall()


@app.post("/books", status_code=201)
def create_book(book: BookIn):
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO books (title, author) VALUES (%s, %s) "
            "RETURNING id, title, author",
            (book.title, book.author),
        ).fetchone()


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with get_conn() as conn:
        return get_or_404(conn, book_id)


@app.patch("/books/{book_id}")
def update_book(book_id: int, changes: BookUpdate):
    with get_conn() as conn:
        book = get_or_404(conn, book_id)
        # only the fields the client sent (and not null)
        data = {k: v for k, v in changes.model_dump(exclude_unset=True).items() if v is not None}
        if not data:
            return book
        # the keys come from the BookUpdate model, never from user text
        columns = ", ".join(f"{key} = %s" for key in data)
        return conn.execute(
            f"UPDATE books SET {columns} WHERE id = %s RETURNING id, title, author",
            (*data.values(), book_id),
        ).fetchone()


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    with get_conn() as conn:
        get_or_404(conn, book_id)
        conn.execute("DELETE FROM books WHERE id = %s", (book_id,))
