from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.internal.postgres import get_db
from app.models.sephora import SephoraReview, ReviewBase
from app.semantic_search.reviews import review_search

router = APIRouter()

# TODO: Implement sentiment classification
def classify_sentiment(query_text: str) -> str:
    # Implement sentiment classification logic here
    # This is a placeholder implementation
    return "positive"  # Replace with actual sentiment classification

@router.get("/semantic/reviews/")
async def get_reviews(
    query_text: str,
    limit: int = 5
):
    try:

        ## need sentiment classification
        sentiment = classify_sentiment(query_text)
        results = review_search(query_text, sentiment, limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    