import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.inventory import Base, Item, Supplier, Warehouse, Bin, Account, Journal
from services.stock_service import StockService

@pytest.fixture
def db_session():
    # Use real SQLite to test relationships better if needed, but in-memory is fine
    engine = create_engine("sqlite:///:memory:")
    # We need accounting models too
    from models.accounting import Base as AccBase
    Base.metadata.create_all(engine)
    AccBase.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Setup mandatory accounting records
    session.add(Account(code='1001', name='Inventory', type='Asset'))
    session.add(Account(code='5001', name='COGS', type='Expense'))
    session.commit()

    yield session
    session.close()

def test_stock_in_integration(db_session):
    service = StockService(db_session)

    # Create Item
    item = Item(code="I1", name="Item 1", current_stock=0)
    db_session.add(item)

    # Create Bin
    bin = Bin(code="B1", zone_id=1) # Simplified
    db_session.add(bin)
    db_session.commit()

    movement_data = {
        "reference_no": "IN-001",
        "type": "IN",
        "ref": "IN-001"
    }
    items_list = [{
        'item_id': item.id,
        'qty': 100,
        'price': 10.0,
        'bin_id': bin.id,
        'lot_number': 'BATCH-01'
    }]

    success = service.record_movement(movement_data, items_list)
    assert success is True
    assert item.current_stock == 100

    # Check Accounting
    from models.accounting import JournalItem
    items = db_session.query(JournalItem).all()
    assert len(items) == 2
    # Inventory Debit 1000
    assert any(it.debit == 1000 for it in items)
