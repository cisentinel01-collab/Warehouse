from services.stock_service import StockService
from sqlalchemy.orm import Session

class StockController:
    def __init__(self, db: Session):
        self.service = StockService(db)

    def generate_invoice_no(self, type):
        import datetime
        return f"{type}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    def receive_stock(self, data, items):
        return self.service.record_movement(data, items), []

    def issue_stock(self, data, items):
        return self.service.record_movement(data, items), []

    def get_movement_history(self, **kwargs):
        from repositories.movement_repo import MovementRepository
        return MovementRepository(self.service.db).get_history(**kwargs)

    def generate_movement_pdf(self, m_id):
        return ""
