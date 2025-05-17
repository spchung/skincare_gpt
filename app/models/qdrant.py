from pydantic import BaseModel, Field

class QProduct(BaseModel):
    product_id: str
    price_usd: float
    size: str
    primary_category: str
    secondary_category: str
    tertiary_category: str
    rating: float
    reviews: int
    brand_name: str
    entity_type: str
    vector_column: str

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
