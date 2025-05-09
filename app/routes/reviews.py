from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.internal.postgres import get_db
from app.models.sephora import SephoraReview

router = APIRouter()

@router.get("/reviews/", response_model=List[dict])
async def get_reviews(
    skip: int = 0,
    limit: int = 10,
    product_id: Optional[str] = None,
    min_rating: Optional[int] = None,
    is_recommended: Optional[bool] = None,
    skin_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SephoraReview)
    
    if product_id:
        query = query.filter(SephoraReview.product_id == product_id)
    if min_rating is not None:
        query = query.filter(SephoraReview.rating >= min_rating)
    if is_recommended is not None:
        query = query.filter(SephoraReview.is_recommended == is_recommended)
    if skin_type:
        query = query.filter(SephoraReview.skin_type.ilike(f"%{skin_type}%"))
    
    reviews = query.offset(skip).limit(limit).all()
    return [review.__dict__ for review in reviews]

@router.get("/reviews/{review_id}", response_model=dict)
async def get_review(review_id: str, db: Session = Depends(get_db)):
    review = db.query(SephoraReview).filter(SephoraReview.review_id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.__dict__

@router.get("/reviews/product/{product_id}", response_model=List[dict])
async def get_product_reviews(
    product_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    reviews = db.query(SephoraReview).filter(
        SephoraReview.product_id == product_id
    ).offset(skip).limit(limit).all()
    return [review.__dict__ for review in reviews] 