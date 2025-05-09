from fastapi import FastAPI
from app.routes import products, reviews, chat, semantic

app = FastAPI()

# Include the routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"]) 
app.include_router(semantic.router, prefix="/api/v1", tags=["semantic"])