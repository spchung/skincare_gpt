from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.internal.postgres import get_db
from app.models.sephora import SephoraProduct, ProductBase

router = APIRouter()

@router.get("/products/", response_model=List[ProductBase])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    brand_name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SephoraProduct)
    
    if brand_name:
        query = query.filter(SephoraProduct.brand_name.ilike(f"%{brand_name}%"))
    if category:
        query = query.filter(
            (SephoraProduct.primary_category.ilike(f"%{category}%")) |
            (SephoraProduct.secondary_category.ilike(f"%{category}%")) |
            (SephoraProduct.teritary_category.ilike(f"%{category}%"))
        )
    if min_price is not None:
        query = query.filter(SephoraProduct.price_usd >= min_price)
    if max_price is not None:
        query = query.filter(SephoraProduct.price_usd <= max_price)
    
    products = query.offset(skip).limit(limit).all()
    return [product.to_pydantic() for product in products]

@router.get("/products/{product_id}", response_model=ProductBase)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(SephoraProduct).filter(SephoraProduct.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_pydantic()

@router.get("/products/brand/{brand_name}", response_model=List[ProductBase])
async def get_products_by_brand(brand_name: str, db: Session = Depends(get_db)):
    products = db.query(SephoraProduct).filter(
        SephoraProduct.brand_name.ilike(f"%{brand_name}%")
    ).all()
    return [product.to_pydantic() for product in products] 