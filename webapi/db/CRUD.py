from typing import Any, List, Optional, Type
from sqlmodel import Field, SQLModel, select
from webapi.db.database import get_session
from sqlalchemy import asc, desc

"""
Automatically handles database operations therefore no need to create session for each usages under service files

Example CRUD USAGE

from sqlmodel import Field, SQLModel
from database import create_tables
from CRUD import create, read, update, delete

class Book(SQLModel, table=True):
    id: int = Field(primary_key=True, autoincrement=True)
    title: str = Field(nullable=False)
    author: str = Field(nullable=False)

# Create tables
create_tables()

# Create a new book
new_book = Book(title="The Catcher in the Rye", author="J.D. Salinger")
create(Book, new_book)

# Query the database
books = read(Book, filter_by={"title": "The Catcher in the Rye"})
for book in books:
    print(book.title, book.author)

# Update a book
updated_book = update(Book, 1, {"title": "The Catcher in the Rye (Updated)"})
if updated_book:
    print("Updated book:", updated_book.title, updated_book.author)

# Order by specific entry
ordered_books_asc = read_order(Book, "title", descending=False)
print("Books ordered by title (ascending):")
for book in ordered_books_asc:
    print(book.title, book.author)

# Delete a book
if delete(Book, 1):
    print("Book deleted")

"""

def create(table: Type[SQLModel], item: SQLModel) -> SQLModel:
    with get_session() as db:
        db.add(item)
        db.commit()
        db.refresh(item)
    return item

def read(table: Type[SQLModel], filter_by: Optional[dict] = None) -> List[SQLModel]:
    with get_session() as db:
        query = db.query(table)

        if filter_by:
            for key, value in filter_by.items():
                query = query.filter(getattr(table, key) == value)

        return query.all()

def find_first(table: Type[SQLModel], filter_by: Optional[dict] = None) -> Optional[SQLModel]:
    with get_session() as db:
        query = db.query(table)

        if filter_by:
            for key, value in filter_by.items():
                query = query.filter(getattr(table, key) == value)

        return query.first()

def read_order(table: Type[SQLModel], order_by: str, descending: bool = False, filter_by: Optional[dict] = None) -> List[SQLModel]:
    with get_session() as db:
        query = db.query(table)

        if filter_by:
            for key, value in filter_by.items():
                query = query.filter(getattr(table, key) == value)

        order_column = getattr(table, order_by)
        query = query.order_by(desc(order_column)) if descending else query.order_by(asc(order_column))

        return query.all()

def update(table: Type[SQLModel], id: Any, item: dict) -> Optional[SQLModel]:
    with get_session() as db:
        entry = db.query(table).filter(table.id == id).one_or_none()

        if entry:
            for key, value in item.items():
                setattr(entry, key, value)

            db.commit()
            return entry

    return None

def delete(table: Type[SQLModel], id: Any) -> bool:
    with get_session() as db:
        entry = db.query(table).filter(table.id == id).one_or_none()

        if entry:
            db.delete(entry)
            db.commit()
            return True

    return False
