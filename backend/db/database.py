from sqlmodel import Session, create_engine, SQLModel
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    """Returns the session that will be used to access the database"""
    with Session(engine) as session:
        yield session

def create_db_and_tables(populating:bool):
    """
    Creates the database and populates if populating is True
    :param: whether you are populating the db or not
    """
    #uncomment if you want to reset the db (WARNING: WILL LOSE ALL DATA)
    #SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    if populating:
        from backend.ingestion.update_service import update_db
        update_db()
