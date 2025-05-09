from fastapi import FastAPI
from app.routes import products, reviews

app = FastAPI()

# Include the routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"]) 