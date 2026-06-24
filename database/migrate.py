from database.session import engine, Base
# Ensure all models are imported for metadata
from models.user import User
from models.inventory import Warehouse, Zone, Bin, Item, StockLot, StockQuant, UnitOfMeasure
from models.accounting import Account, Journal, JournalEntry, JournalItem
from models.audit import AuditLog

def migrate():
    print("Initializing Enterprise Database schema...")
    Base.metadata.create_all(bind=engine)
    print("Migration complete. System ready.")

if __name__ == "__main__":
    migrate()
