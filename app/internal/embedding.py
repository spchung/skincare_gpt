from openai import OpenAI
import dotenv
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings

model = SentenceTransformer("sentence-transformers/all-MPNet-base-v2")
def create_embedding_768(text: str) -> np.array:
    try: 
        emb = model.encode(text, normalize_embeddings=True)
        return np.array(emb).astype(np.float16)
    except Exception as e: 
        raise e
    
class SkincareGPT768Embedding(Embeddings):
    def embed_query(self, text: str) -> list[float]:
        return create_embedding_768(text).tolist()
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [create_embedding_768(t).tolist() for t in texts]
