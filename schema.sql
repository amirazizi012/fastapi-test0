-- Database schema for the Open Library books project.
-- Safe to run multiple times.

CREATE TABLE IF NOT EXISTS publishers (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS authors (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS books (
    id                  SERIAL PRIMARY KEY,
    ol_key              TEXT NOT NULL UNIQUE,
    title               TEXT NOT NULL,
    first_publish_year  INTEGER NOT NULL CHECK (first_publish_year > 2000),
    isbn                TEXT,
    pages               INTEGER,
    publisher_id        INTEGER REFERENCES publishers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id    INTEGER REFERENCES books(id)   ON DELETE CASCADE,
    author_id  INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

CREATE INDEX IF NOT EXISTS idx_books_year      ON books(first_publish_year);
CREATE INDEX IF NOT EXISTS idx_books_publisher ON books(publisher_id);
