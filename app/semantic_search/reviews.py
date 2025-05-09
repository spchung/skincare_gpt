from qdrant_client import models
from app.internal.embedding import create_embedding_768
from app.internal.qdrant import client

COLLECTION_NAME = "SkincareGPT_768"

def review_search(query_text: str, sentiment=None, limit: int = 5):
    try:
        filters = {"vector_column": "review_text"}
        if sentiment == "positive" or sentiment == "negative":
            filters['is_recommended'] = sentiment == "positive"
        
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
            results.append(point.payload)
        return results

    except Exception as e:
        print(f"Error searching Qdrant: {str(e)}")
        return []