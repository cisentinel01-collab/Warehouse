from database.session import Session, engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
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
        # Convert %s to :param_idx for SQLAlchemy text()
        import re
        sql_converted = query
        param_dict = {}

        # Simple %s to :p1, :p2 conversion
        count = 1
        while '%s' in sql_converted:
            placeholder = f"p{count}"
            sql_converted = sql_converted.replace('%s', f":{placeholder}", 1)
            if (count-1) < len(params):
                param_dict[placeholder] = params[count-1]
            count += 1

        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql_converted), param_dict)
                if commit:
                    conn.commit()
                    if "RETURNING" in query.upper():
                        return result.scalar()
                    return None

                if result.returns_rows:
                    return [dict(row._mapping) for row in result]
                return []
        except SQLAlchemyError as e:
            app_logger.error(f"DBManager Query Error: {e} | SQL: {sql_converted}")
            raise e

    def get_session(self):
        return Session()
