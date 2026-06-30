from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database.session import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False) # Asset, Liability, Equity, Income, Expense
    parent_id = Column(Integer, ForeignKey("accounts.id"))
    is_reconcile = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    parent = relationship("Account", remote_side=[id])

class Journal(Base):
    __tablename__ = "journals"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    type = Column(String(20)) # Sale, Purchase, Cash, Bank, General

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True) # Reference Number
    date = Column(Date, default=datetime.utcnow, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    ref = Column(String(100)) # External Reference
    state = Column(String(20), default="draft") # draft, posted, cancelled

    items = relationship("JournalItem", back_populates="entry")

class JournalItem(Base):
    __tablename__ = "journal_items"
    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(100)) # Label
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    date = Column(Date, index=True)

    entry = relationship("JournalEntry", back_populates="items")
    account = relationship("Account")
