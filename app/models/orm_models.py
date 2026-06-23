from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False) # admin, warehouse_manager, follow_up, read_only
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    description = Column(Text)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), index=True)
    unit = Column(String(20))
    location_id = Column(Integer, ForeignKey("locations.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    min_stock = Column(Integer, default=0)
    current_stock = Column(Integer, default=0)
    barcode = Column(String(100), unique=True, index=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    location = relationship("Location")
    supplier = relationship("Supplier")

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    batch_number = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, default=0)
    production_date = Column(Date)
    expiry_date = Column(Date, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item")

class Movement(Base):
    __tablename__ = "movements"
    id = Column(Integer, primary_key=True)
    type = Column(String(10), nullable=False, index=True) # IN, OUT
    reference_no = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    received_by = Column(String(100))
    issuing_entity = Column(String(100))
    receiver_name = Column(String(100))
    final_total = Column(Float, default=0.0)

class MovementItem(Base):
    __tablename__ = "movement_items"
    id = Column(Integer, primary_key=True)
    movement_id = Column(Integer, ForeignKey("movements.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, default=0.0)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_value = Column(Text)
    new_value = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
