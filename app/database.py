from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .utils import get_settings, logger

Base = declarative_base()
_engine = None
_SessionLocal = None

def init_db():
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=_engine)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        logger.info("Database initialized")

def get_session():
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()