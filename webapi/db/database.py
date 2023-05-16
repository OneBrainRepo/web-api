import os
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session,SQLModel,create_engine

POSTGRES_USER = os.getenv("POSTGRES_USER","postgres")
POSTGRES_PASSWD = os.getenv("POSTGRES_PASSWD","postgres")

DB_CONNECTION_STRING = os.getenv(f"DB_CONNECTION_STRING","localhost:5432/db")
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app-v1.db"
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWD}@{DB_CONNECTION_STRING}"


engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """
    Create if doesnt exists
    """
    SQLModel.metadata.create_all(engine)

class CustomSession:
    def __init__(self, engine):
        self.session = Session(engine)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

def get_session():
    """
    Create a DB session
    """
    return CustomSession(engine)