from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import schemas, models
from app.services import product_service

router = APIRouter()

@router.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db=db, product=product)

@router.get("/products/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return product_service.get_products(db=db, skip=skip, limit=limit, category_id=category_id)

@router.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_service.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = product_service.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_service.update_product(db=db, product_id=product_id, product=product)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_service.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product_service.delete_product(db=db, product_id=product_id)
    return {"detail": "Product deleted"}

# Category endpoints
@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return product_service.create_category(db=db, category=category)

@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_service.get_categories(db=db, skip=skip, limit=limit)