from pydantic import BaseModel, Field

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
