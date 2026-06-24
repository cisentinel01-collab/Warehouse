from database.session import Session, engine
from sqlalchemy import text
from app_logging.app_logger import app_logger

class DBManager:
    """Unified Database Manager using SQLAlchemy for connection pooling and ORM integration."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
        return cls._instance

    def execute_query(self, query, params=(), commit=False):
        """Compatibility method for legacy raw SQL queries using SQLAlchemy engine."""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query), params)
                if commit:
                    conn.commit()
                    # Logic for RETURNING
                    if "RETURNING" in query.upper():
                        return result.scalar()
                    return None

                # Fetch results as list of dicts for backward compatibility
                if result.returns_rows:
                    return [dict(row._mapping) for row in result]
                return []
        except Exception as e:
            app_logger.error(f"DBManager Error: {e}")
            raise e

    def get_session(self):
        return Session()
