from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Импортируем все модели для корректной работы Alembic
from app.models import (
    user,
    role,
    category,
    product,
    product_photo,
    carpet,
    product_type,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
