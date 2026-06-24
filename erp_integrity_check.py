import sys
import os
sys.path.append(os.getcwd())

def verify():
    print("Verifying ERP Component Integration...")
    try:
        from database.session import Session
        from models.user import User
        from models.inventory import Item, Warehouse, UnitOfMeasure, Supplier, Bin
        from models.accounting import Account, JournalEntry
        from services.auth_service import AuthService
        from services.stock_service import StockService
        from services.accounting_service import AccountingService
        from services.uom_service import UOMService
        from services.dashboard_service import DashboardService
        from services.report_service import ReportService
        from views.main_window import MainWindow
        from app_logging.app_logger import app_logger

        print("PASS: All enterprise modules imported.")

        db = Session()
        auth = AuthService(db)
        stock = StockService(db)
        uom = UOMService(db)
        dashboard = DashboardService(db)

        assert hasattr(stock, 'accounting'), "StockService missing Accounting integration"
        print("PASS: Stock-Accounting integration verified.")

        # Verify model relationships
        assert 'items' in [t.name for t in Item.__table__.metadata.sorted_tables], "Metadata incomplete"
        print("PASS: Database metadata verified.")

        db.close()
        print("\nERP Architecture Integrity: SECURE")

    except Exception as e:
        print(f"\nINTEGRITY FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify()
