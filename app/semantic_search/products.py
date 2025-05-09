from qdrant_client import models
from app.internal.embedding import create_embedding_768
from app.internal.qdrant import client

COLLECTION_NAME = "SkincareGPT_768"

