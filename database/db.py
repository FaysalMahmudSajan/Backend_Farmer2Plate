from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

Base = declarative_base()

engine = create_engine(settings.DB_CONNECTION)

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()