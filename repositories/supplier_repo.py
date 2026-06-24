from repositories.base_repository import BaseRepository
from models.inventory import Supplier
from sqlalchemy.orm import Session

class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: Session):
        super().__init__(Supplier, db)

    def search(self, term: str) -> list[Supplier]:
        return self.db.query(Supplier).filter(
            Supplier.name.ilike(f"%{term}%"),
            Supplier.is_deleted == False
        ).all()
