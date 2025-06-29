# app/internal/embedding_v2.py
from openai import OpenAI
import os
from typing import Optional
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_openai_embedding(text: str, model: str = "text-embedding-3-small") -> np.array:
    """
    Create embeddings using OpenAI's embedding models
    text-embedding-3-small: 1536 dimensions, faster, cheaper
    text-embedding-3-large: 3072 dimensions, better quality, more expensive
    """
    try:
        response = openai_client.embeddings.create(
            input=text,
            model=model
        )
        embedding = np.array(response.data[0].embedding, dtype=np.float32)
        return embedding
    except Exception as e:
        raise Exception(f"OpenAI embedding failed: {str(e)}")

def create_review_embedding(
    review_text: str,
    review_title: str,
    product_name: str,
    skin_tone: Optional[str] = None,
    eye_color: Optional[str] = None,
    skin_type: Optional[str] = None,
    hair_color: Optional[str] = None,
    is_recommended: bool = None,
    rating: int = None,
    model: str = "text-embedding-3-small"
) -> np.array:
    """
    Create enhanced review embedding by combining multiple fields
    """
    
    # Build the composite text for embedding
    embedding_parts = []
    
    # Core review content (highest weight)
    embedding_parts.append(f"Review: {review_text}")
    embedding_parts.append(f"Title: {review_title}")
    embedding_parts.append(f"Product: {product_name}")
    
    # User characteristics (for personalized matching)
    user_profile = []
    if skin_tone:
        user_profile.append(f"skin tone {skin_tone}")
    if skin_type:
        user_profile.append(f"skin type {skin_type}")
    if eye_color:
        user_profile.append(f"eye color {eye_color}")
    if hair_color:
        user_profile.append(f"hair color {hair_color}")
    
    if user_profile:
        embedding_parts.append(f"Reviewer profile: {', '.join(user_profile)}")
    
    # Sentiment and rating context
    if is_recommended is not None:
        recommendation_text = "recommended" if is_recommended else "not recommended"
        embedding_parts.append(f"Overall: {recommendation_text}")
    
    if rating is not None:
        rating_context = {
            1: "very negative",
            2: "negative", 
            3: "neutral",
            4: "positive",
            5: "very positive"
        }
        embedding_parts.append(f"Rating: {rating}/5 stars ({rating_context.get(rating, 'neutral')})")
    
    # Combine all parts
    composite_text = " | ".join(embedding_parts)
    
    return create_openai_embedding(composite_text, model)

def create_product_embedding(
    product_name: str,
    brand_name: str,
    primary_category: str,
    secondary_category: Optional[str] = None,
    tertiary_category: Optional[str] = None,
    price_usd: Optional[float] = None,
    highlights: Optional[list] = None,
    ingredients: Optional[list] = None,
    model: str = "text-embedding-3-small"
) -> np.array:
    """
    Create enhanced product embedding
    """
    
    embedding_parts = []
    
    # Core product info
    embedding_parts.append(f"Product: {product_name}")
    embedding_parts.append(f"Brand: {brand_name}")
    
    # Categories
    categories = [primary_category]
    if secondary_category:
        categories.append(secondary_category)
    if tertiary_category:
        categories.append(tertiary_category)
    embedding_parts.append(f"Categories: {' > '.join(categories)}")
    
    # Price context
    if price_usd:
        price_tier = "budget" if price_usd < 25 else "mid-range" if price_usd < 75 else "luxury"
        embedding_parts.append(f"Price: ${price_usd} ({price_tier})")
    
    # Key features and benefits
    if highlights:
        embedding_parts.append(f"Benefits: {', '.join(highlights)}")
    
    # Key ingredients (limit to avoid overwhelming the embedding)
    if ingredients and len(ingredients) > 0:
        # Take first 5 ingredients to avoid token limits
        key_ingredients = ingredients[:5] if len(ingredients) > 5 else ingredients
        embedding_parts.append(f"Key ingredients: {', '.join(key_ingredients)}")
    
    composite_text = " | ".join(embedding_parts)
    
    return create_openai_embedding(composite_text, model)

# Updated embedding class for Langchain compatibility
class SkincareGPTOpenAIEmbedding:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
    
    def embed_query(self, text: str) -> list[float]:
        return create_openai_embedding(text, self.model).tolist()
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [create_openai_embedding(t, self.model).tolist() for t in texts]