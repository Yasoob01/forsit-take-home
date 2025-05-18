from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    last_restock_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Define the relationship with Product
    product = relationship("Product", back_populates="inventory")
    
    # Define the relationship with InventoryHistory
    history = relationship("InventoryHistory", back_populates="inventory")

class InventoryHistory(Base):
    __tablename__ = "inventory_history"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"))
    previous_quantity = Column(Integer)
    new_quantity = Column(Integer)
    change_date = Column(DateTime, default=datetime.now)
    change_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    inventory = relationship("Inventory", back_populates="history")