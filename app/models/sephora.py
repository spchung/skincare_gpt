from sqlalchemy import Column, String, Integer, Float, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# SQLAlchemy Base
class Base(DeclarativeBase):
    pass

# Pydantic Models
class ProductBase(BaseModel):
    product_id: str
    product_name: str
    brand_id: int
    brand_name: str
    loves_count: Optional[int] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    size: Optional[str] = None
    ingredients: Optional[List[Any]] = None
    price_usd: float
    highlights: Optional[List[Any]] = None
    primary_category: str
    secondary_category: Optional[str] = None
    teritary_category: Optional[str] = None

class ReviewBase(BaseModel):
    review_id: str
    author_id: str
    rating: int
    is_recommended: bool
    helpfulness: Optional[float] = None
    total_feedback_count: int
    total_neg_feedback_count: int
    total_pos_feedback_count: int
    submission_time: str
    review_text: str
    review_title: str
    skin_tone: Optional[str] = None
    eye_color: Optional[str] = None
    skin_type: Optional[str] = None
    hair_color: Optional[str] = None
    product_id: str
    product_name: str
    brand_name: str
    price_usd: float

# SQLAlchemy Models
class SephoraProduct(Base):
    __tablename__ = "sephora_product"

    product_id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    brand_id = Column(Integer, nullable=False)
    brand_name = Column(String, nullable=False)
    loves_count = Column(Integer)
    rating = Column(Float)
    reviews = Column(Integer)
    size = Column(String)
    ingredients = Column(JSON)
    price_usd = Column(Float, nullable=False)
    highlights = Column(JSON)
    primary_category = Column(String, nullable=False)
    secondary_category = Column(String)
    teritary_category = Column(String)

    def to_pydantic(self) -> ProductBase:
        return ProductBase(
            product_id=self.product_id,
            product_name=self.product_name,
            brand_id=self.brand_id,
            brand_name=self.brand_name,
            loves_count=self.loves_count,
            rating=self.rating,
            reviews=self.reviews,
            size=self.size,
            ingredients=self.ingredients or [],  # Convert None to empty list
            price_usd=self.price_usd,
            highlights=self.highlights or [],  # Convert None to empty list
            primary_category=self.primary_category,
            secondary_category=self.secondary_category,
            teritary_category=self.teritary_category
        )

class SephoraReview(Base):
    __tablename__ = "sephora_review"

    review_id = Column(String, primary_key=True)
    author_id = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    is_recommended = Column(Boolean, nullable=False)
    helpfulness = Column(Float)
    total_feedback_count = Column(Integer, nullable=False)
    total_neg_feedback_count = Column(Integer, nullable=False)
    total_pos_feedback_count = Column(Integer, nullable=False)
    submission_time = Column(String, nullable=False)
    review_text = Column(String, nullable=False)
    review_title = Column(String, nullable=False)
    skin_tone = Column(String)
    eye_color = Column(String)
    skin_type = Column(String)
    hair_color = Column(String)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    brand_name = Column(String, nullable=False)
    price_usd = Column(Float, nullable=False)

    def to_pydantic(self) -> ReviewBase:
        return ReviewBase(
            review_id=self.review_id,
            author_id=self.author_id,
            rating=self.rating,
            is_recommended=self.is_recommended,
            helpfulness=self.helpfulness,
            total_feedback_count=self.total_feedback_count,
            total_neg_feedback_count=self.total_neg_feedback_count,
            total_pos_feedback_count=self.total_pos_feedback_count,
            submission_time=self.submission_time,
            review_text=self.review_text,
            review_title=self.review_title,
            skin_tone=self.skin_tone,
            eye_color=self.eye_color,
            skin_type=self.skin_type,
            hair_color=self.hair_color,
            product_id=self.product_id,
            product_name=self.product_name,
            brand_name=self.brand_name,
            price_usd=self.price_usd
        ) 