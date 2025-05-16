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