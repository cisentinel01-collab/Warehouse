from database.session import engine, Base
import os
from sqlalchemy import text
from app_logging.app_logger import app_logger

# Ensure all models are imported for metadata
from models.user import User
from models.inventory import Warehouse, Zone, Bin, Item, StockLot, StockQuant, UnitOfMeasure, Supplier, Location, Movement, Settings
from models.accounting import Account, Journal, JournalEntry, JournalItem
from models.audit import AuditLog

def migrate():
    app_logger.info("Initializing Enterprise Database schema...")

    # 1. Create tables from models
    Base.metadata.create_all(bind=engine)

    # 2. Run manual schema additions (like devices)
    schema_path = os.path.join(os.path.dirname(__file__), "schema_devices.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            sql = f.read()
            with engine.connect() as conn:
                with conn.begin():
                    for statement in sql.split(";"):
                        if statement.strip():
                            conn.execute(text(statement))

    app_logger.info("Migration complete. System ready.")

if __name__ == "__main__":
    migrate()
