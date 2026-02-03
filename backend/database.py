from sqlmodel import create_engine, SQLModel, Session
from models import User, Subscription, ChatMessage, AuditLog
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./BetFaro.db")

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
