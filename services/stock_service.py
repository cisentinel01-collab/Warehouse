from sqlalchemy.orm import Session
from models.inventory import Item, StockLot, StockQuant, Bin
from models.accounting import Account, Journal
from services.accounting_service import AccountingService
from app_logging.app_logger import app_logger
from datetime import datetime
from sqlalchemy.orm import Session

class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.accounting = AccountingService(db)

    def record_movement(self, movement_data: dict, items_list: list) -> bool:
        """
        Record movement, update quants, and create accounting entries.
        items_list: list of {'item_id', 'qty', 'price', 'bin_id', 'lot_number', 'expiry'}
        """
        try:
            # 1. Logic for Quants and Stock update
            total_value = 0.0
            for it in items_list:
                item = self.db.query(Item).filter(Item.id == it['item_id']).first()
                if not item: continue

                qty = it['qty']
                price = it['price']
                total_value += (qty * price)

                if movement_data['type'] == 'IN':
                    # Handle Lot
                    lot = self.db.query(StockLot).filter(
                        StockLot.item_id == item.id,
                        StockLot.lot_number == it.get('lot_number', 'DEFAULT')
                    ).first()
                    if not lot:
                        lot = StockLot(item_id=item.id, lot_number=it.get('lot_number', 'DEFAULT'), expiry_date=it.get('expiry'))
                        self.db.add(lot)
                        self.db.flush()

                    lot.quantity += qty
                    item.current_stock += qty

                    # Update Quant
                    quant = self.db.query(StockQuant).filter(
                        StockQuant.item_id == item.id, StockQuant.bin_id == it['bin_id'], StockQuant.lot_id == lot.id
                    ).first()
                    if not quant:
                        quant = StockQuant(item_id=item.id, bin_id=it['bin_id'], lot_id=lot.id, quantity=0)
                        self.db.add(quant)
                    quant.quantity += qty

                else: # OUT
                    item.current_stock -= qty
                    # Simple Quant deduction (In real ERP, we'd loop through quants FIFO/FEFO)
                    quant = self.db.query(StockQuant).filter(
                        StockQuant.item_id == item.id, StockQuant.bin_id == it['bin_id']
                    ).first()
                    if quant:
                        quant.quantity -= qty

            # 2. Automated Accounting Entry
            # Find default accounts (In production, these come from category/settings)
            inv_acc = self.db.query(Account).filter(Account.code == '1001').first() # Inventory
            cogs_acc = self.db.query(Account).filter(Account.code == '5001').first() # COGS / Purchase

            if inv_acc and cogs_acc:
                journal = self.db.query(Journal).filter(Journal.code == 'STK').first()
                if not journal:
                    journal = Journal(name="Stock Journal", code="STK", type="General")
                    self.db.add(journal)
                    self.db.flush()

                if movement_data['type'] == 'IN':
                    acc_items = [
                        {'account_id': inv_acc.id, 'name': f"Stock In: {movement_data['ref']}", 'debit': total_value, 'credit': 0.0},
                        {'account_id': cogs_acc.id, 'name': f"Stock In: {movement_data['ref']}", 'debit': 0.0, 'credit': total_value}
                    ]
                else:
                    acc_items = [
                        {'account_id': cogs_acc.id, 'name': f"Stock Out: {movement_data['ref']}", 'debit': total_value, 'credit': 0.0},
                        {'account_id': inv_acc.id, 'name': f"Stock Out: {movement_data['ref']}", 'debit': 0.0, 'credit': total_value}
                    ]

                self.accounting.create_entry(journal.id, datetime.now(), movement_data['ref'], acc_items)

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            app_logger.error(f"Movement failed: {e}")
            raise e
