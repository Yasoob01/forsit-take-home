from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SaleItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    subtotal: float = Field(..., gt=0)

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemInDB(SaleItemBase):
    id: int
    sale_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SaleBase(BaseModel):
    order_id: str
    order_date: datetime
    customer_id: Optional[str] = None
    total_amount: float = Field(..., gt=0)
    platform: Optional[str] = None
    status: str = "completed"

class SaleCreate(SaleBase):
    items: List[SaleItemCreate]

class SaleInDB(SaleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Sale(SaleInDB):
    items: List[SaleItemInDB] = []

# For analytics
class PeriodInfo(BaseModel):
    start_date: datetime
    end_date: datetime

class SummaryInfo(BaseModel):
    total_orders: int
    total_revenue: float

class PlatformSales(BaseModel):
    platform: str
    order_count: int
    revenue: float

class TopProduct(BaseModel):
    id: int
    name: str
    total_quantity: int
    total_revenue: float

class SalesAnalytics(BaseModel):
    period: PeriodInfo
    summary: SummaryInfo
    platforms: List[PlatformSales]
    top_products: List[TopProduct]
    total_sales: float
    total_orders: int
    average_order_value: float

    class Config:
        orm_mode = True
        from_attributes = True

class RevenueByPeriod(BaseModel):
    period: str
    revenue: float
    order_count: int