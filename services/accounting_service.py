from sqlalchemy.orm import Session
from models.accounting import JournalEntry, JournalItem, Account
from datetime import datetime
from app_logging.app_logger import app_logger

from models.accounting import Account, Journal, JournalEntry, JournalItem

class AccountingService:
    def __init__(self, db: Session):
        self.db = db

    def get_accounts(self):
        return self.db.query(Account).all()

    def create_entry(self, journal_id: int, date: datetime, ref: str, items: list) -> JournalEntry:
        """
        items: list of dicts {'account_id': id, 'name': label, 'debit': val, 'credit': val}
        """
        try:
            # Verify Balance (Debit == Credit)
            total_debit = sum(i['debit'] for i in items)
            total_credit = sum(i['credit'] for i in items)

            if round(total_debit, 2) != round(total_credit, 2):
                raise ValueError(f"Entry is not balanced. Debit: {total_debit}, Credit: {total_credit}")

            name = f"MISC/{datetime.now().strftime('%Y/%m')}/{ref}" # Simplified naming logic
            entry = JournalEntry(name=name, date=date, journal_id=journal_id, ref=ref, state='posted')
            self.db.add(entry)
            self.db.flush()

            for item_data in items:
                ji = JournalItem(
                    entry_id=entry.id,
                    account_id=item_data['account_id'],
                    name=item_data['name'],
                    debit=item_data['debit'],
                    credit=item_data['credit'],
                    balance=item_data['debit'] - item_data['credit'],
                    date=date
                )
                self.db.add(ji)

            # Removed commit to allow parent transaction (e.g. StockService) to control atomic scope
            self.db.flush()
            app_logger.info(f"Journal Entry created: {entry.name}")
            return entry
        except Exception as e:
            self.db.rollback()
            app_logger.error(f"Failed to create journal entry: {e}")
            raise e

    def get_trial_balance(self):
        # Implementation of Trial Balance using aggregate queries
        from sqlalchemy import func
        return self.db.query(
            Account.code,
            Account.name,
            func.sum(JournalItem.debit).label('total_debit'),
            func.sum(JournalItem.credit).label('total_credit')
        ).join(JournalItem, Account.id == JournalItem.account_id).group_by(Account.id).all()

    def get_profit_loss(self):
        """
        Calculate P&L based on Income and Expense account types.
        """
        from sqlalchemy import func
        results = self.db.query(
            Account.type,
            func.sum(JournalItem.debit - JournalItem.credit).label('balance')
        ).join(JournalItem, Account.id == JournalItem.account_id)\
         .filter(Account.type.in_(['Income', 'Expense']))\
         .group_by(Account.type).all()

        income = 0.0
        expense = 0.0
        for r in results:
            if r.type == 'Income': income = abs(r.balance)
            if r.type == 'Expense': expense = r.balance

        return {
            'income': income,
            'expense': expense,
            'net_profit': income - expense
        }
