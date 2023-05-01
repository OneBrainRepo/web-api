import os
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session,SQLModel,create_engine

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING","sqlite:///./sql_app-v1.db")
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    DB_CONNECTION_STRING, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

## Functions for helper
def create_all() -> None:
    """
    Create if doesnt exists
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Create a DB session
    """
    with Session(engine) as session:
        yield session