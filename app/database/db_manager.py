import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

from psycopg2 import pool

# Load environment variables from .env file
load_dotenv()

class DBManager:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.config = {
                'dbname': os.getenv('DB_NAME', 'wms_erp'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASS', 'postgres'),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432')
            }
            try:
                cls._pool = pool.SimpleConnectionPool(1, 10, **cls._instance.config)
            except Exception as e:
                print(f"Pool creation error: {e}")
        return cls._instance

    def get_connection(self):
        if not self._pool:
            raise ConnectionError("Database connection pool is not initialized. Please check your DB settings.")
        return self._pool.getconn()

    def release_connection(self, conn):
        if self._pool and conn:
            self._pool.putconn(conn)

    def execute_query(self, query, params=(), commit=False):
        try:
            conn = self.get_connection()
        except ConnectionError as ce:
            print(f"DB Error: {ce}")
            return []
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                    # If it's an INSERT with RETURNING, fetch the ID
                    if "RETURNING" in query.upper():
                        try:
                            res = cursor.fetchone()
                            return res['id'] if res and 'id' in res else None
                        except:
                            return None
                    return None

                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            if commit:
                conn.rollback()
            raise e
        finally:
            self.release_connection(conn)
