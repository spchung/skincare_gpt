from openai import OpenAI
import dotenv
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("sentence-transformers/all-MPNet-base-v2")
def create_embedding_768(text: str) -> np.array:
    try: 
        emb = model.encode(text, normalize_embeddings=True)
        return np.array(emb).astype(np.float16)
    except Exception as e: 
        raise e