from qdrant_client import models
from app.internal.embedding import create_embedding_768
from app.internal.qdrant import client
from app.models import QProduct
from typing import List
COLLECTION_NAME = "SkincareGPT_768"

def product_search(query_text: str, limit: int = 5, additional_filters: dict = None) -> List[QProduct]:
    try:
        filters = {"vector_column": "product_name"}

        if additional_filters:
            filters.update(additional_filters)

        # Perform the search
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=create_embedding_768(query_text),  # Qdrant will handle the text embedding
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
            results.append(QProduct(**point.payload))
        return results

    except Exception as e:
        print(f"Error searching Qdrant: {str(e)}")
        return []