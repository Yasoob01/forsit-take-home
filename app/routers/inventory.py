from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import schemas
from app.services import inventory_service

router = APIRouter()

@router.post("/inventory/", response_model=schemas.Inventory)
def create_inventory(inventory: schemas.InventoryCreate, db: Session = Depends(get_db)):
    return inventory_service.create_inventory(db=db, inventory=inventory)

@router.get("/inventory/", response_model=List[schemas.Inventory])
def read_inventory(
    skip: int = 0, 
    limit: int = 100,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    return inventory_service.get_inventory(
        db=db, 
        skip=skip, 
        limit=limit,
        low_stock_only=low_stock_only
    )

@router.get("/inventory/{product_id}", response_model=schemas.InventoryWithHistory)
def read_inventory_by_product(product_id: int, db: Session = Depends(get_db)):
    db_inventory = inventory_service.get_inventory_by_product(db=db, product_id=product_id)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    return db_inventory

@router.put("/inventory/{product_id}", response_model=schemas.Inventory)
def update_inventory(
    product_id: int, 
    inventory: schemas.InventoryUpdate, 
    change_reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    db_inventory = inventory_service.get_inventory_by_product(db=db, product_id=product_id)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    return inventory_service.update_inventory(
        db=db, 
        product_id=product_id, 
        inventory=inventory,
        change_reason=change_reason
    )

@router.get("/inventory/low-stock/alerts", response_model=List[schemas.Inventory])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    return inventory_service.get_low_stock_alerts(db=db)