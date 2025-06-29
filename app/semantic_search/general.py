from qdrant_client import models
from app.internal.embedding import create_embedding_768
from app.internal.embedding_v2 import create_openai_embedding
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


COLLECTION_NAME_V2 = "skincareGPT"
def generic_search_v2(query_text: str, limit: int = 5):
    try:
        # Perform the search
        search_result = client.query_points(
            collection_name=COLLECTION_NAME_V2,
            query=create_openai_embedding(query_text),  # Qdrant will handle the text embedding
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