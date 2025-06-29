from qdrant_client import models
from app.internal.embedding_v2 import create_openai_embedding
from app.internal.qdrant import client
from app.models import QReviewV2
from typing import List

COLLECTION_NAME = "skincareGPT"

def review_search(query_text: str, sentiment = None, limit: int = 5) -> List[QReviewV2]:
    
    filters = {"vector_column": "review_text"}
    if sentiment == "positive" or sentiment == "negative":
        filters['is_recommended'] = sentiment == "positive"
    
    # Perform the search
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=create_openai_embedding(query_text),  # Qdrant will handle the text embedding
        limit=limit,
        query_filter=models.Filter(
            must=[models.FieldCondition(
                key=k, match=models.MatchValue(value=v)) for k, v in filters.items()]
        )
    )
    points = search_result.points
    points.sort(key=lambda x: x.score, reverse=True)
    
    results = []
    for point in points:
        results.append(QReviewV2(**point.payload))
    return results