from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    sku = Column(String(50), unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Define the relationship with Category
    category = relationship("Category", back_populates="products")
    
    # Define the relationship with Inventory
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    
    # Define the relationship with SaleItem
    sale_items = relationship("SaleItem", back_populates="product")