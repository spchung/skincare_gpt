from qdrant_client import models
from app.internal.embedding import create_embedding_768
from app.internal.qdrant import client

COLLECTION_NAME = "SkincareGPT_768"

def generic_search(query_text: str, limit: int = 5):
    try:
        
        # Perform the search
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=create_embedding_768(query_text),  # Qdrant will handle the text embedding
            limit=limit,
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