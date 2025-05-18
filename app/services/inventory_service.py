from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app import models, schemas
from fastapi import HTTPException
from typing import Optional

def get_inventory(db: Session, skip: int = 0, limit: int = 100, low_stock_only: bool = False):
    query = db.query(models.Inventory)
    
    if low_stock_only:
        query = query.filter(models.Inventory.quantity <= models.Inventory.low_stock_threshold)
    
    return query.offset(skip).limit(limit).all()

def get_inventory_by_product(db: Session, product_id: int):
    return db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()

def create_inventory(db: Session, inventory: schemas.InventoryCreate):
    db_inventory = get_inventory_by_product(db, product_id=inventory.product_id)
    if db_inventory:
        raise HTTPException(status_code=400, detail="Inventory for this product already exists")
    
    product = db.query(models.Product).filter(models.Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_inventory = models.Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def update_inventory(db: Session, product_id: int, inventory: schemas.InventoryUpdate, change_reason: Optional[str] = None):
    db_inventory = get_inventory_by_product(db, product_id=product_id)
    
    if inventory.quantity is not None and inventory.quantity != db_inventory.quantity:
        history = models.InventoryHistory(
            inventory_id=db_inventory.id,
            previous_quantity=db_inventory.quantity,
            new_quantity=inventory.quantity,
            change_reason=change_reason
        )
        db.add(history)
        
        if inventory.quantity > db_inventory.quantity:
            db_inventory.last_restock_date = datetime.now()
    
    update_data = inventory.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inventory, key, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def get_low_stock_alerts(db: Session):
    return db.query(models.Inventory).filter(
        models.Inventory.quantity <= models.Inventory.low_stock_threshold
    ).all()