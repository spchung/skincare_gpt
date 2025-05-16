from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from app.internal.embedding import SkincareGPT768Embedding
from langchain_qdrant import QdrantVectorStore, RetrievalMode

# Load environment variables
load_dotenv()

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333")
)

embedding_fn = SkincareGPT768Embedding()

qdrant_store = QdrantVectorStore(
    client=client,
    collection_name="SkincareGPT_768",
    embedding=embedding_fn,
    retrieval_mode=RetrievalMode.DENSE,
)