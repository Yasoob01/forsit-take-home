from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app import schemas
from app.services import sales_service

router = APIRouter()

@router.post("/sales/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    return sales_service.create_sale(db=db, sale=sale)

@router.get("/sales/", response_model=List[schemas.Sale])
def read_sales(
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return sales_service.get_sales(
        db=db, 
        skip=skip, 
        limit=limit, 
        start_date=start_date,
        end_date=end_date,
        platform=platform
    )

@router.get("/sales/{sale_id}", response_model=schemas.Sale)
def read_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = sales_service.get_sale(db=db, sale_id=sale_id)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return db_sale

# Analytics endpoints
@router.get("/sales/analytics/summary", response_model=schemas.SalesAnalytics)
def get_sales_analytics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    platform: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return sales_service.get_sales_summary(
        db=db,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/sales/analytics/revenue", response_model=List[schemas.RevenueByPeriod])
def get_revenue_by_period(
    period_type: str = Query(..., description="Period type: daily, weekly, monthly, yearly"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    platform: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return sales_service.get_revenue_by_period(
        db=db,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        platform=platform,
        category_id=category_id
    )

@router.get("/sales/analytics/compare", response_model=dict)
def compare_revenue(
    period_type: str = Query(..., description="Period type: daily, weekly, monthly, yearly"),
    current_start: date = Query(..., description="Start date of current period"),
    current_end: date = Query(..., description="End date of current period"),
    previous_start: date = Query(..., description="Start date of previous period"),
    previous_end: date = Query(..., description="End date of previous period"),
    platform: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return sales_service.compare_revenue(
        db=db,
        period_type=period_type,
        current_start=current_start,
        current_end=current_end,
        previous_start=previous_start,
        previous_end=previous_end,
        platform=platform,
        category_id=category_id
    )