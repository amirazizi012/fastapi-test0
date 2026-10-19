from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Library API")


class BookIn(BaseModel):
    title: str
    author: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None



books = {
    1: {"title": "Clean Code", "author": "Robert C. Martin"},
    2: {"title": "The Pragmatic Programmer", "author": "Andrew Hunt"},
    3: {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen"},
    4: {"title": "Design Patterns", "author": "Erich Gamma"},
}
next_id = 5


def get_or_404(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]


@app.get("/books")
def list_books():
    return [{"id": i, **b} for i, b in books.items()]


@app.post("/books", status_code=201)
def create_book(book: BookIn):
    global next_id
    books[next_id] = book.model_dump()
    next_id += 1
    return {"id": next_id - 1, **books[next_id - 1]}


@app.get("/books/{book_id}")
def get_book(book_id: int):
    return {"id": book_id, **get_or_404(book_id)}


@app.patch("/books/{book_id}")
def update_book(book_id: int, changes: BookUpdate):
    book = get_or_404(book_id)
    book.update(changes.model_dump(exclude_unset=True))
    return {"id": book_id, **book}


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    get_or_404(book_id)
    del books[book_id]
