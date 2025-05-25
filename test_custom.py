from pprint import pprint
from app.internal.qdrant import client
from qdrant_client import models
from app.internal.embedding import create_embedding_768
from app.internal.postgres import get_db
from app.models.sephora import SephoraReviewSQLModel, SephoraProductSQLModel
from app.lang_graphs.chat_v1.handlers.vector_search_rewrite_worker import QueryRewriteInputSchema, vector_search_rewrite_agent

COLLECTION_NAME = "SkincareGPT_768"

text = ''

def search_reviews(query_text: str, limit: int = 5):
    filters = {"vector_column": "product_name"}

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

    return points


db = next(get_db())
while True:
    input_text = input("Search: ")
    if input_text.lower() == 'exit':
        break

    res = vector_search_rewrite_agent.run(
        QueryRewriteInputSchema(query=input_text)
    )

    rewritten_query = res.rewritten_query
    print(f"\nRewritten Query: {rewritten_query}\n")

    res = search_reviews(rewritten_query, limit=1)
    
    # review_id = res[0].payload['review_id']
    # text = db.query(SephoraReviewSQLModel).filter(SephoraReviewSQLModel.review_id == review_id).first().review_text

    product_id = res[0].payload['product_id']
    text = db.query(SephoraProductSQLModel).filter(SephoraProductSQLModel.product_id == product_id).first().product_name

    print(f"\nRes : {text}\n")

db.close()
