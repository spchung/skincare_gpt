from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class QProductV2(BaseModel):
    type: str 
    product_id: str = Field(..., description="Unique identifier for the product")
    product_name: str = Field(..., description="Name of the product")
    brand_name: str = Field(..., description="Brand name of the product")
    price_usd: float = Field(..., gt=0, description="Product price in USD")
    rating: float = Field(..., ge=0, le=5, description="Average product rating from 0 to 5")
    reviews: int = Field(..., ge=0, description="Total number of reviews for the product")
    size: str = Field(..., description="Product size specification")
    ingredients: List[str] = Field(default_factory=list, description="List of product ingredients")
    highlights: List[str] = Field(default_factory=list, description="List of product highlights or key features")
    primary_category: str = Field(..., description="Primary product category")
    secondary_category: Optional[str] = Field(None, description="Secondary product category")
    tertiary_category: Optional[str] = Field(None, description="Tertiary product category")
    loves_count: int = Field(..., ge=0, description="Number of users who marked this product as loved")

class QProduct(BaseModel):
    product_id: str
    price_usd: float | None
    size: str | None
    primary_category: str
    secondary_category: str | None
    tertiary_category: str | None
    rating: float | None
    reviews: int | None
    brand_name: str
    entity_type: str
    vector_column: str

class QReviewV2(BaseModel):
    type: str 
    review_id: str = Field(..., description="Unique identifier for the review")
    product_id: str = Field(..., description="Unique identifier for the product")
    author_id: str = Field(..., description="Unique identifier for the review author")
    is_recommended: bool = Field(..., description="Whether the author recommends the product")
    rating: int = Field(..., ge=1, le=5, description="Product rating from 1 to 5")
    review_title: str = Field(..., description="Title of the review")
    review_text: str = Field(..., description="Main content of the review")
    helpfulness: int = Field(..., ge=0, description="Helpfulness score of the review")
    total_feedback_count: int = Field(..., ge=0, description="Total number of feedback responses")
    total_neg_feedback_count: int = Field(..., ge=0, description="Number of negative feedback responses")
    total_pos_feedback_count: int = Field(..., ge=0, description="Number of positive feedback responses")
    submission_time: date = Field(..., description="Date when the review was submitted")
    skin_tone: Optional[str] = Field(None, description="Author's skin tone")
    eye_color: Optional[str] = Field(None, description="Author's eye color")
    skin_type: Optional[str] = Field(None, description="Author's skin type")
    hair_color: Optional[str] = Field(None, description="Author's hair color")
    product_name: str = Field(..., description="Name of the product being reviewed")
    brand_name: str = Field(..., description="Brand name of the product")
    price_usd: float = Field(..., gt=0, description="Product price in USD")

class QReview(BaseModel):
    entity_type: str
    vector_column: str
    product_id: str
    price_usd: float | None
    review_id: str
    rating: float | None
    is_recommended: bool | None
    review_title: str | None
    skin_tone: str | None
    eye_color: str | None
    skin_type: str | None
    hair_color: str | None
    product_name: str | None
    brand_name: str | None
