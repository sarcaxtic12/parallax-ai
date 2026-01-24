import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    topic = Column(String)
    url = Column(String)
    bias_rating = Column(String)
    summary = Column(Text)
    content = Column(Text)

def get_db_engine():
    """
    Creates and returns a SQLAlchemy engine.
    Falls back to localhost for local development if DATABASE_URL is not set.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback for local run
        db_url = "postgresql://parallax_user:parallax_pass@localhost:5432/parallax_core"
    
    # Fix for Render/Heroku postgres:// schema if necessary for SQLAlchemy 1.4+
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return create_engine(db_url)

def init_db():
    """
    Initializes the database by creating all tables defined in Base.
    """
    engine = get_db_engine()
    Base.metadata.create_all(engine)
