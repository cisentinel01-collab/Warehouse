from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# scoped_session ensures that each thread has its own unique session
Session = scoped_session(SessionFactory)
Base = declarative_base()

def get_db():
    """Provides a transactional scope around a series of operations."""
    db = Session()
    try:
        yield db
    finally:
        # scoped_session.remove() is better than .close() for scoped sessions
        Session.remove()
