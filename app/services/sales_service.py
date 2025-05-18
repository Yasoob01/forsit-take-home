from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app import models, schemas
from fastapi import HTTPException
from typing import List, Optional, Dict, Any

def get_sales(db: Session, skip: int = 0, limit: int = 100, 
              start_date: Optional[datetime] = None, 
              end_date: Optional[datetime] = None,
              platform: Optional[str] = None,
              status: Optional[str] = None):
    """
    Get sales with optional filtering by date range, platform, and status
    """
    query = db.query(models.Sale)
    
    if start_date:
        query = query.filter(models.Sale.order_date >= start_date)
    
    if end_date:
        query = query.filter(models.Sale.order_date <= end_date)
    
    if platform:
        query = query.filter(models.Sale.platform == platform)
    
    if status:
        query = query.filter(models.Sale.status == status)
    
    return query.order_by(models.Sale.order_date.desc()).offset(skip).limit(limit).all()

def get_sale_by_id(db: Session, sale_id: int):
    """
    Get a specific sale by ID
    """
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()

def get_sale_by_order_id(db: Session, order_id: str):
    """
    Get a specific sale by order ID
    """
    return db.query(models.Sale).filter(models.Sale.order_id == order_id).first()

def create_sale(db: Session, sale: schemas.SaleCreate):
    """
    Create a new sale with items
    """
    # Create the sale
    db_sale = models.Sale(
        order_id=sale.order_id,
        order_date=sale.order_date or datetime.now(),
        customer_id=sale.customer_id,
        total_amount=sale.total_amount,
        platform=sale.platform,
        status=sale.status or "completed"
    )
    db.add(db_sale)
    db.flush()
    
    # Create sale items
    for item in sale.items:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal
        )
        db.add(db_item)
        
        # Update inventory
        inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item.product_id).first()
        if inventory:
            inventory.quantity = max(0, inventory.quantity - item.quantity)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sales_summary(db: Session, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None):
    """
    Get sales summary statistics
    """
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # Total sales and revenue
    sales_query = db.query(
        func.count(models.Sale.id).label("total_orders"),
        func.sum(models.Sale.total_amount).label("total_revenue")
    ).filter(
        models.Sale.order_date.between(start_date, end_date)
    ).first()
    
    total_orders = sales_query.total_orders or 0
    total_revenue = float(sales_query.total_revenue or 0)
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Sales by platform
    platform_query = db.query(
        models.Sale.platform,
        func.count(models.Sale.id).label("order_count"),
        func.sum(models.Sale.total_amount).label("revenue")
    ).filter(
        models.Sale.order_date.between(start_date, end_date)
    ).group_by(models.Sale.platform).all()
    
    # Top selling products
    top_products_query = db.query(
        models.Product.id,
        models.Product.name,
        func.sum(models.SaleItem.quantity).label("total_quantity"),
        func.sum(models.SaleItem.subtotal).label("total_revenue")
    ).join(
        models.SaleItem, models.Product.id == models.SaleItem.product_id
    ).join(
        models.Sale, models.SaleItem.sale_id == models.Sale.id
    ).filter(
        models.Sale.order_date.between(start_date, end_date)
    ).group_by(
        models.Product.id, models.Product.name
    ).order_by(
        func.sum(models.SaleItem.quantity).desc()
    ).limit(5).all()
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue
        },
        "platforms": [
            {
                "platform": p.platform,
                "order_count": p.order_count,
                "revenue": float(p.revenue or 0)
            } for p in platform_query
        ],
        "top_products": [
            {
                "id": p.id,
                "name": p.name,
                "total_quantity": p.total_quantity,
                "total_revenue": float(p.total_revenue or 0)
            } for p in top_products_query
        ],
        # Add these fields to match what your schema expects
        "total_sales": total_revenue,
        "total_orders": total_orders,
        "average_order_value": average_order_value
    }

def get_revenue_by_period(db: Session, 
                         period_type: str = "daily",
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         platform: Optional[str] = None,
                         category_id: Optional[int] = None):
    """
    Get revenue data grouped by period (daily, weekly, monthly, yearly)
    """
    if not start_date:
        if period_type == "daily":
            start_date = datetime.now() - timedelta(days=30)
        elif period_type == "weekly":
            start_date = datetime.now() - timedelta(days=90)
        elif period_type == "monthly":
            start_date = datetime.now() - timedelta(days=365)
        else:  # yearly
            start_date = datetime.now() - timedelta(days=365*3)
    
    if not end_date:
        end_date = datetime.now()
    
    # Define the date part to extract based on period type
    if period_type == "daily":
        date_part = func.date(models.Sale.order_date)
    elif period_type == "weekly":
        date_part = func.date_trunc('week', models.Sale.order_date)
    elif period_type == "monthly":
        date_part = func.date_trunc('month', models.Sale.order_date)
    else:  # yearly
        date_part = extract('year', models.Sale.order_date)
    
    # Build the query
    query = db.query(
        date_part.label("period"),
        func.sum(models.Sale.total_amount).label("revenue"),
        func.count(models.Sale.id).label("order_count")
    ).filter(
        models.Sale.order_date.between(start_date, end_date)
    )
    
    # Add filters for platform and category if provided
    if platform:
        query = query.filter(models.Sale.platform == platform)
    
    if category_id:
        query = query.join(
            models.SaleItem, models.Sale.id == models.SaleItem.sale_id
        ).join(
            models.Product, models.SaleItem.product_id == models.Product.id
        ).filter(
            models.Product.category_id == category_id
        )
    
    query = query.group_by(date_part).order_by(date_part)
    result = query.all()
    
    # Return just the data list instead of a dictionary
    return [
        {
            "period": str(item.period),
            "revenue": float(item.revenue or 0),
            "order_count": item.order_count
        } for item in result
    ]

def compare_revenue(db: Session,
                   period_type: str = "monthly",
                   current_start: datetime = None,
                   current_end: datetime = None,
                   previous_start: datetime = None,
                   previous_end: datetime = None,
                   platform: Optional[str] = None,
                   category_id: Optional[int] = None):
    """
    Compare revenue between two periods
    """

    if not current_end:
        current_end = datetime.now()
    
    if not current_start:
        if period_type == "daily":
            current_start = current_end - timedelta(days=1)
        elif period_type == "weekly":
            current_start = current_end - timedelta(days=7)
        elif period_type == "monthly":
            current_start = current_end - timedelta(days=30)
        else:
            current_start = current_end - timedelta(days=365)
    
    if not previous_end:
        previous_end = current_start
    
    if not previous_start:
        if period_type == "daily":
            previous_start = previous_end - timedelta(days=1)
        elif period_type == "weekly":
            previous_start = previous_end - timedelta(days=7)
        elif period_type == "monthly":
            previous_start = previous_end - timedelta(days=30)
        else:
            previous_start = previous_end - timedelta(days=365)

    current_query = db.query(
        func.sum(models.Sale.total_amount).label("revenue")
    ).filter(
        models.Sale.order_date.between(current_start, current_end)
    )

    previous_query = db.query(
        func.sum(models.Sale.total_amount).label("revenue")
    ).filter(
        models.Sale.order_date.between(previous_start, previous_end)
    )
    
    if platform:
        current_query = current_query.filter(models.Sale.platform == platform)
        previous_query = previous_query.filter(models.Sale.platform == platform)
    
    if category_id:
        current_query = current_query.join(
            models.SaleItem, models.Sale.id == models.SaleItem.sale_id
        ).join(
            models.Product, models.SaleItem.product_id == models.Product.id
        ).filter(
            models.Product.category_id == category_id
        )
        
        previous_query = previous_query.join(
            models.SaleItem, models.Sale.id == models.SaleItem.sale_id
        ).join(
            models.Product, models.SaleItem.product_id == models.Product.id
        ).filter(
            models.Product.category_id == category_id
        )
    
    current_revenue = current_query.scalar() or 0
    previous_revenue = previous_query.scalar() or 0

    change = current_revenue - previous_revenue
    percent_change = (change / previous_revenue * 100) if previous_revenue > 0 else 0
    
    return {
        "period_type": period_type,
        "current_period": {
            "start_date": current_start,
            "end_date": current_end,
            "revenue": float(current_revenue)
        },
        "previous_period": {
            "start_date": previous_start,
            "end_date": previous_end,
            "revenue": float(previous_revenue)
        },
        "comparison": {
            "change": float(change),
            "percent_change": float(percent_change)
        }
    }