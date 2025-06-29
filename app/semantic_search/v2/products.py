from qdrant_client import models
from app.internal.embedding_v2 import create_openai_embedding
from app.internal.qdrant import client
from app.models import QProductV2
from typing import List
from app.lang_graphs.chat.models import ProductSearchFilter

COLLECTION_NAME = "skincareGPT"

def product_search(query_text: str, limit: int = 5, additional_filters: dict = None) -> List[QProductV2]:
    filters = {"type": "product"}

    if additional_filters:
        filters.update(additional_filters)
        
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
        results.append(QProductV2(**point.payload))
    return results

def product_filtered_search(query_text: str, product_search_filters: List[ProductSearchFilter] | None = None, limit: int = 5) -> List[QProductV2]:
    filters = {"type": "product"}

    product_search_filters_conditions = [models.FieldCondition(key=k, match=models.MatchValue(value=v)) for k, v in filters.items()]
    
    for filter in product_search_filters:
        if filter.key == "price":
            filter.key = 'price_usd'

        if filter.condition == "above":
            product_search_filters_conditions.append(models.FieldCondition(key=filter.key,range=models.Range(gt=filter.value)))
        elif filter.condition == "below":
            product_search_filters_conditions.append(models.FieldCondition(key=filter.key,range=models.Range(lt=filter.value)))

    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=create_openai_embedding(query_text),  # Qdrant will handle the text embedding
        limit=limit,
        query_filter=models.Filter(
            must=product_search_filters_conditions
        )
    )
    
    points = search_result.points
    points.sort(key=lambda x: x.score, reverse=True)
    
    results = []
    for point in points:
        results.append(QProductV2(**point.payload))
    return results

