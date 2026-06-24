from sqlalchemy.orm import Session
from repositories.supplier_repo import SupplierRepository
from models.inventory import Supplier
from app_logging.app_logger import app_logger

class SupplierService:
    def __init__(self, db: Session):
        self.repo = SupplierRepository(db)
        self.db = db

    def get_all(self):
        return self.repo.get_all()

    def create(self, data: dict):
        new_s = Supplier(**data)
        return self.repo.create(new_s)

    def search(self, term: str):
        return self.repo.search(term)
