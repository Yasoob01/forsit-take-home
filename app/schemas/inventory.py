from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(10, ge=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)

class InventoryHistoryBase(BaseModel):
    previous_quantity: int
    new_quantity: int
    change_reason: Optional[str] = None

class InventoryHistoryCreate(InventoryHistoryBase):
    inventory_id: int

class InventoryHistoryInDB(InventoryHistoryBase):
    id: int
    inventory_id: int
    changed_at: datetime

    class Config:
        orm_mode = True

class InventoryInDB(InventoryBase):
    id: int
    last_restock_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Inventory(InventoryInDB):
    pass

class InventoryWithHistory(Inventory):
    history: List[InventoryHistoryInDB] = []